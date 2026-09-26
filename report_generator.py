"""
report_generator.py — Turns raw Slither findings into a readable,
audit-style PDF report using Claude for plain-language explanations
and remediation guidance.
"""
import os
from datetime import date
from pathlib import Path

import anthropic
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)

from audit_engine import Finding, audit_directory

IMPACT_COLORS = {
    "High": colors.HexColor("#C0392B"),
    "Medium": colors.HexColor("#E67E22"),
    "Low": colors.HexColor("#F1C40F"),
    "Informational": colors.HexColor("#7F8C8D"),
    "Optimization": colors.HexColor("#2980B9"),
}


def get_ai_commentary(client: anthropic.Anthropic, finding: Finding) -> str:
    """Ask Claude to turn a raw Slither finding into a short, audit-style
    explanation and remediation recommendation."""
    prompt = f"""You are a smart contract security auditor writing a finding for a client report.

Slither detector: {finding.check}
Impact: {finding.impact}
Confidence: {finding.confidence}
Contract: {finding.contract_file}
Raw technical description:
{finding.description}

Write exactly two short paragraphs in plain English, no headers, no markdown:
1. What the risk is and why it matters in plain business/security terms (2-3 sentences).
2. A concrete, actionable remediation recommendation (2-3 sentences).

Keep it concise and professional, as it would appear in a client-facing audit report."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def build_pdf_report(findings: list[Finding], commentary: dict[str, str], output_path: Path):
    doc = SimpleDocTemplate(
        str(output_path), pagesize=A4,
        topMargin=2*cm, bottomMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("TitleCustom", parent=styles["Title"], fontSize=20, spaceAfter=6)
    subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"], fontSize=11, textColor=colors.grey)
    h2_style = ParagraphStyle("H2Custom", parent=styles["Heading2"], fontSize=13, spaceBefore=14, spaceAfter=6)
    body_style = ParagraphStyle("BodyCustom", parent=styles["Normal"], fontSize=10, leading=14)
    meta_style = ParagraphStyle("Meta", parent=styles["Normal"], fontSize=9, textColor=colors.grey, spaceAfter=8)

    story = []

    # --- Cover / summary ---
    story.append(Paragraph("Smart Contract Security Audit Report", title_style))
    story.append(Paragraph(f"Generated {date.today().isoformat()} — Automated static analysis (Slither) with AI-assisted commentary", subtitle_style))
    story.append(Spacer(1, 1*cm))

    counts = {}
    for f in findings:
        counts[f.impact] = counts.get(f.impact, 0) + 1

    summary_data = [["Severity", "Count"]] + [[k, str(v)] for k, v in counts.items()]
    summary_table = Table(summary_data, colWidths=[6*cm, 3*cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)
    story.append(PageBreak())

    # --- Findings ---
    story.append(Paragraph("Detailed Findings", styles["Title"]))
    story.append(Spacer(1, 0.5*cm))

    for i, f in enumerate(findings, 1):
        color = IMPACT_COLORS.get(f.impact, colors.grey)
        header = f'<font color="{color.hexval()}"><b>[{f.impact}]</b></font> {f.check} — {f.contract_file}'
        story.append(Paragraph(header, h2_style))

        lines_str = ", ".join(str(l) for l in f.line_numbers) if f.line_numbers else "n/a"
        story.append(Paragraph(f"Detector confidence: {f.confidence} · Line(s): {lines_str}", meta_style))

        ai_text = commentary.get(f"{f.contract_file}:{f.check}:{i}", "")
        for para in ai_text.split("\n\n"):
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
                story.append(Spacer(1, 0.3*cm))

    doc.build(story)


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit(
            "Set your ANTHROPIC_API_KEY environment variable first, e.g.:\n"
            "  export ANTHROPIC_API_KEY=sk-ant-...   (macOS/Linux)\n"
            "  $env:ANTHROPIC_API_KEY='sk-ant-...'    (Windows PowerShell)"
        )

    client = anthropic.Anthropic(api_key=api_key)

    contracts_dir = Path(__file__).parent / "contracts"
    findings = audit_directory(contracts_dir)

    if not findings:
        print("No findings to report — check that Slither ran correctly.")
        return

    print(f"\nGenerating AI commentary for {len(findings)} finding(s)...")
    commentary = {}
    for i, f in enumerate(findings, 1):
        key = f"{f.contract_file}:{f.check}:{i}"
        print(f"  [{i}/{len(findings)}] {f.check} ({f.contract_file})")
        commentary[key] = get_ai_commentary(client, f)

    output_path = Path(__file__).parent / "audit_report.pdf"
    build_pdf_report(findings, commentary, output_path)
    print(f"\nReport generated: {output_path}")


if __name__ == "__main__":
    main()
