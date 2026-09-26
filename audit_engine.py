"""
audit_engine.py — Runs Slither static analysis on Solidity contracts
and returns structured findings for report generation.
"""
import json
import subprocess
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class Finding:
    contract_file: str
    check: str            # Slither detector name, e.g. "reentrancy-eth"
    impact: str            # High / Medium / Low / Informational
    confidence: str         # High / Medium / Low
    description: str        # Slither's raw description
    line_numbers: list = field(default_factory=list)


IMPACT_ORDER = {"High": 0, "Medium": 1, "Low": 2, "Informational": 3, "Optimization": 4}


def run_slither(contract_path: Path) -> list[Finding]:
    """Run Slither on a single .sol file and parse its JSON output."""
    result = subprocess.run(
        ["slither", str(contract_path), "--json", "-"],
        capture_output=True,
        text=True,
    )

    # Slither exits non-zero when it finds issues — that's expected, not a failure.
    if not result.stdout.strip():
        print(f"  ! No JSON output for {contract_path.name} — check stderr below:")
        print(result.stderr[:500])
        return []

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"  ! Could not parse Slither output for {contract_path.name}")
        return []

    findings = []
    for detector in data.get("results", {}).get("detectors", []):
        line_numbers = []
        for elem in detector.get("elements", []):
            src_mapping = elem.get("source_mapping", {})
            if src_mapping.get("lines"):
                line_numbers.extend(src_mapping["lines"])

        findings.append(Finding(
            contract_file=contract_path.name,
            check=detector.get("check", "unknown"),
            impact=detector.get("impact", "Informational"),
            confidence=detector.get("confidence", "Low"),
            description=detector.get("description", "").strip(),
            line_numbers=sorted(set(line_numbers)),
        ))

    return findings


def audit_directory(contracts_dir: Path) -> list[Finding]:
    """Run Slither on every .sol file in a directory. Returns all findings, sorted by severity."""
    all_findings = []
    sol_files = sorted(contracts_dir.glob("*.sol"))

    if not sol_files:
        print(f"No .sol files found in {contracts_dir}")
        return []

    for sol_file in sol_files:
        print(f"Analysing {sol_file.name}...")
        findings = run_slither(sol_file)
        print(f"  -> {len(findings)} finding(s)")
        all_findings.extend(findings)

    all_findings.sort(key=lambda f: IMPACT_ORDER.get(f.impact, 99))
    return all_findings


if __name__ == "__main__":
    contracts_dir = Path(__file__).parent / "contracts"
    findings = audit_directory(contracts_dir)

    print(f"\n{'='*60}")
    print(f"Total findings: {len(findings)}")
    for f in findings:
        print(f"[{f.impact:>13}] {f.contract_file} — {f.check}")
