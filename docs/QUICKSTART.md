# AxiomAI Quickstart

Get the reasoning engine, API, and console running in about 5 minutes.

## Prerequisites

- Python 3.11+
- pip

## 1. Install

```bash
git clone https://github.com/ksjpswaroop/AxiomAI.git
cd AxiomAI
pip install -e ".[dev,console]"
```

## 2. Smoke test (CLI)

```bash
axiomai socrates
```

Expected: `PROVED: Mortal(Socrates)`

## 3. Run case study demos

Tier 1 (pilot):
```bash
python apps/case-studies/07-cybersecurity/demo.py
python apps/case-studies/02-soc2-compliance/demo.py
python apps/case-studies/03-ai-support-governance/demo.py
```

All 18 verticals are available via API (`GET /case-studies`) or the Streamlit console.

## 4. Start the API

```bash
axiomai-server
```

Open http://localhost:8000/docs for Swagger UI.

Try:

```bash
curl http://localhost:8000/case-studies
curl -X POST http://localhost:8000/case-studies/cs-07/run
```

## 5. Start the console (optional)

In a second terminal:

```bash
AXIOMAI_API_URL=http://localhost:8000 streamlit run apps/console/app.py
```

Open http://localhost:8501

## 6. Run tests

```bash
pytest tests/ -q
```

## Docker (all-in-one)

```bash
docker compose up --build
```

- API: http://localhost:8000
- Console: http://localhost:8501

See [DEPLOYMENT.md](./DEPLOYMENT.md) for production notes.

## Next steps

- [PROJECT-MODULES.md](./PROJECT-MODULES.md) — architecture
- [IMPLEMENTATION-TRACKER.md](./IMPLEMENTATION-TRACKER.md) — build progress
- Case study specs: `docs/case-studies/`
