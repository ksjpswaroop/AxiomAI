# AxiomAI Deployment Guide

## Docker Compose (recommended for demos)

```bash
docker compose up --build
```

| Service | URL | Description |
|---------|-----|---------------|
| `api` | http://localhost:8000 | FastAPI reasoning + governance API |
| `ui` | http://localhost:8501 | Streamlit console |

Swagger docs: http://localhost:8000/docs

### Volumes

SQLite persistence is stored in the `axiomai-data` Docker volume (`/data/axiomai.db` inside the API container).

## Environment variables

| Variable | Service | Default | Description |
|----------|---------|---------|-------------|
| `AXIOMAI_API_URL` | UI | `http://localhost:8000` | FastAPI base URL for the console |
| `AXIOMAI_PERSIST` | API | (none) | SQLite URL, e.g. `sqlite:////data/axiomai.db` |

## Manual deployment

### API server

```bash
pip install -e ".[console]"
export AXIOMAI_PERSIST=sqlite:///./axiomai.db   # optional
axiomai-server
```

Or with uvicorn directly:

```bash
uvicorn axiomai.reasoner.api.main:app --host 0.0.0.0 --port 8000
```

### Streamlit console

```bash
export AXIOMAI_API_URL=http://your-api-host:8000
streamlit run apps/console/app.py --server.port=8501 --server.address=0.0.0.0
```

## API endpoints (P5)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/case-studies` | List Tier 1 demos |
| POST | `/case-studies/{id}/run` | Run CS-07, CS-02, or CS-03 |
| POST | `/governance/validate` | Agent action policy check |
| GET | `/audit` | Query audit log (`?outcome=DENY`) |

## Production considerations

- Put API behind HTTPS (nginx, Caddy, or cloud load balancer)
- Restrict CORS if exposing the API publicly
- Use managed PostgreSQL instead of SQLite for multi-instance API deployments
- Run Streamlit behind auth (OAuth proxy, VPN, or private network)
- Pin image tags and enable CI (`pytest`, `ruff`) on every deploy

## Health checks

```bash
curl http://localhost:8000/health
```

## UI stack

**Streamlit** was chosen for the P5 MVP console (see `apps/console/README.md`). Migrate to React/Next.js when pilot customers need custom branding or complex workflows.
