# AxiomAI Investor Console

Desktop demo UI for investors and pilots. Minimal design, all features, all 18 case studies.

## Run locally

```bash
docker compose up
```

- **Console:** http://localhost:8501
- **API:** http://localhost:8000/docs

Or without Docker:

```bash
pip install -e ".[console]"
axiomai-server &   # API on :8000
streamlit run apps/console/app.py --server.port 8501
```

## Pages

| Page | Purpose |
|------|---------|
| Home | Platform overview + 5-minute investor path |
| Case Study Gallery | All 18 verticals with scenario picker |
| Brainstorming | Describe your problem → scope check + no-code path |
| Feature Guides | How to use every platform capability |
| Knowledge Base | Facts, rules, queries, LLM extract |
| Governance | Policy pack simulator (4 policies) |
| Audit Trail | Governance decision log |

## Investor demo script (5 min)

1. **Home** — show platform metrics
2. **Case Study Gallery → CS-07** — ransomware RCA, attack chain, MTTR
3. **Case Study Gallery → CS-03** — try `allow_compliant` and `deny_outside_window` scenarios
4. **Case Study Gallery → CS-02** — SOC2 gap analysis
5. **Governance** — procurement policy blocked purchase
6. **Brainstorming** — paste prospect use case, show scope match
7. **Knowledge Base** — live query with proof tree

## Data

All case study data is **synthetic**, modeled on open standards (MITRE ATT&CK, SOC2, NIST, OWASP, USCIS, etc.). See `apps/case_studies/data/` and per-guide `docs/guides/case-studies/`.
