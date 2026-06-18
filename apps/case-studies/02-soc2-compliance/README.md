# CS-02 SOC2 Compliance Automation

Runnable Tier 1 case study — automated SOC2 control gap analysis from enterprise evidence.

## Run

```bash
python apps/case-studies/02-soc2-compliance/demo.py
```

## What it does

1. Ingests evidence from mock Azure AD and AWS Config connectors
2. Evaluates 8 SOC2 controls (MFA, backup, log retention, access review, etc.)
3. Produces PASS/FAIL per control with evidence
4. Exports auditor-ready gap report (JSON + Markdown) to `output/`

## Package

Importable logic lives in `apps/case_studies/cs02_soc2/`.

Spec: `docs/case-studies/02-soc2-compliance/README.md`
