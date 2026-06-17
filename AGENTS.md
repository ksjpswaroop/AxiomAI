# AGENTS.md

## Cursor Cloud specific instructions

AxiomAI is a single Python product: a deterministic reasoning engine exposed as
an importable library, a Typer CLI (`axiomai`), and a FastAPI REST API. There is
no frontend/GUI. Python 3.12 is used (`requires-python >=3.11`).

### Environment
- Dependencies are installed into a virtualenv at `.venv` (created by the
  startup update script). Always run tools via that venv, e.g.
  `.venv/bin/python`, `.venv/bin/pytest`, `.venv/bin/ruff`, `.venv/bin/uvicorn`,
  `.venv/bin/axiomai`. There is no auto-activation; either prefix with
  `.venv/bin/` or run `source .venv/bin/activate` first.
- The package is installed editable (`pip install -e ".[dev]"`), so source edits
  are picked up without reinstalling.

### Run / test / lint / build
- Library demo: `.venv/bin/python examples/socrates.py`
- CLI: `.venv/bin/axiomai --help` (e.g. `axiomai socrates`, `axiomai solve-sudoku`).
- API server (dev): `.venv/bin/uvicorn axiomai.reasoner.api.main:app --reload --port 8000`.
  Then hit endpoints like `POST /facts`, `POST /rules`, `POST /forward`,
  `POST /query`, `POST /sudoku`, `GET /stats`, `GET /health`.
- Tests: `.venv/bin/pytest`. NOTE: the `tests/` directory currently contains no
  test cases, so pytest collects 0 tests and exits with code 5 — this is
  expected, not a failure.
- Lint: `.venv/bin/ruff check .`. NOTE: there are pre-existing lint findings
  (mostly unused imports, `F401`); a clean exit is not currently expected.

### Non-obvious gotchas
- The actual package layout is `axiomai/reasoner/...` (NOT `axiomai/src/reasoner/`
  as some docs show). Use module path `axiomai.reasoner.api.main:app` for uvicorn.
- Reasoning behavior note: backward chaining (`ask`, CLI `socrates`/`prove`,
  `POST /query`) can return `UNKNOWN` for facts that forward chaining
  (`derive_all` / `POST /forward`) correctly derives. Forward chaining is the
  reliable path to demonstrate proofs end-to-end. This is application logic, not
  an environment issue.
