# CS-03 AI Customer Support Governance

Runnable Tier 1 case study — deterministic refund policy enforcement for LLM support agents.

## Run

```bash
python apps/case-studies/03-ai-support-governance/demo.py
```

## What it does

1. Simulates an LLM agent suggesting a $350 refund
2. Runs `GovernanceEngine` against refund policy (window, amount, return status)
3. Returns DENY with violated rules and proof
4. Runs 5 scenarios (allow, deny, escalate) and writes audit log JSON

## Package

Importable logic lives in `apps/case_studies/cs03_support_governance/`.

Spec: `docs/case-studies/03-ai-support-governance/README.md`
