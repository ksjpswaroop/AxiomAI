# CS-07 Cybersecurity Root Cause Analysis

Runnable Tier 1 case study — ransomware attack chain reconstruction with deterministic reasoning.

## Run

```bash
python apps/case-studies/07-cybersecurity/demo.py
```

## What it does

1. Loads ransomware incident scenario (15+ security facts)
2. Ingests mock SIEM connector alerts
3. Runs forward-chaining attack rules (10+ MITRE-aligned rules)
4. Reconstructs attack chain and root cause
5. Prints MTTR before/after metrics

## Package

Importable logic lives in `apps/case_studies/cs07_cybersecurity/`.

Spec: `docs/case-studies/07-cybersecurity-root-cause/README.md`
