# Smart Contract Security Audit Tool

Automated static analysis tool for Solidity smart contracts. Runs
[Slither](https://github.com/crytic/slither) (industry-standard static
analyzer used by real audit firms) against a set of contracts, then uses
Claude to translate each raw technical finding into a plain-English risk
explanation and remediation recommendation — packaged into a client-ready
PDF audit report.

## What's included

- `contracts/` — 4 sample contracts, each with one intentionally injected
  vulnerability (reentrancy, missing access control, unchecked arithmetic,
  `tx.origin` authentication)
- `audit_engine.py` — runs Slither and parses its findings into a
  structured format
- `report_generator.py` — sends each finding to Claude for a plain-English
  explanation, then builds the final PDF report
- `requirements.txt`

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Install a Solidity compiler version

Slither needs `solc` (the Solidity compiler) available. `solc-select`
handles this for you:

```bash
solc-select install 0.8.19
solc-select use 0.8.19
```

### 3. Set your Anthropic API key

```bash
# macOS / Linux
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# Windows PowerShell
$env:ANTHROPIC_API_KEY='sk-ant-your-key-here'
```

### 4. Run the audit

```bash
python report_generator.py
```

This will:
1. Run Slither against every `.sol` file in `contracts/`
2. Send each finding to Claude for a plain-English explanation
3. Generate `audit_report.pdf` with a severity summary and detailed findings

## Adding your own contracts

Drop any `.sol` file into `contracts/` and re-run `report_generator.py` —
no code changes needed.

## Why this project

Static analysis is exactly how real audit teams do a first-pass security
review before manual review. This tool demonstrates the same workflow at
a small scale: identify a risk with a recognised tool, explain its
business impact, and document a remediation path — the core loop of an
IT/security audit engagement.
