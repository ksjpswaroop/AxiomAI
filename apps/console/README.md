# AxiomAI Console (M17)

**UI stack:** Streamlit (MVP) — chosen for P5 speed-to-demo.

Streamlit provides rapid multi-page console development without a separate frontend build step. A React/Next.js console remains an option for P6+ production UI.

## Run locally

Terminal 1 — API:

```bash
pip install -e ".[dev,console]"
axiomai-server
```

Terminal 2 — Console:

```bash
AXIOMAI_API_URL=http://localhost:8000 streamlit run apps/console/app.py
```

Open http://localhost:8501

## Pages

| Page | Feature |
|------|---------|
| Knowledge Base | Add facts/rules, run queries, view proofs |
| Case Studies | Launch CS-07, CS-02, CS-03 demos |
| Governance | Simulate agent refund actions |
| Audit Trail | Browse governance decisions |

## Docker

See `docs/DEPLOYMENT.md` — `docker compose up` runs API + UI together.
