# AxiomAI — Implementation Tracker

**Version:** 1.2  
**Date:** 2026-06-17  
**Last Updated:** 2026-06-18 (Production Readiness audit tracked)  
**Companion doc:** [PROJECT-MODULES.md](./PROJECT-MODULES.md)

Use this document as the single source of truth for build progress. Update checkboxes as work completes.

---

## How to Use This Tracker

1. Work **top to bottom within each phase** unless a dependency note says otherwise.
2. Do not start **Phase 4 (case studies)** until **Phase 0–2** are complete.
3. Do not expose the API publicly until **Phase PR-1** is complete.
4. Mark items: `[ ]` not started · `[~]` in progress · `[x]` done · `[—]` cancelled/deferred
4. Each task has an **ID** (e.g. `P0-03`) for issue/PR linking.
5. **Definition of Done (DoD)** for every task:
   - Code merged to `master`
   - Tests pass (when applicable)
   - Documented in README or module doc
   - No regressions in `examples/socrates.py`

---

## Status Summary

| Phase | Name | Progress | Blocker |
|-------|------|----------|---------|
| P0 | Foundation Fixes | 8/8 ✅ | None |
| P1 | Core Engine Completion | 14/14 ✅ | None |
| P2 | Platform Layer | 16/16 ✅ | None |
| P3 | Application Framework | 10/10 ✅ | None |
| P4 | Tier 1 Case Studies | 3/3 ✅ | None |
| P5 | Working Application | 12/12 ✅ | None |
| P6 | Tier 2–5 Case Studies | 15/15 ✅ | None |
| PR | Production Readiness | 0/42 | Security (no API auth) |

**Overall:** P0–P6 complete. **281 tests passing**, ~79% coverage on `axiomai/`. 18 investor-ready case studies with scenarios. v0.3.0 (Alpha).

**Deployment verdict:** ✅ Demo / private pilot · ❌ Public internet / multi-tenant production (see [Phase PR](#phase-pr--production-readiness))

**Active branch:** `cursor/investor-demo-ui-ef4a`

**Investor demo:** `docker compose up` → http://localhost:8501 — Case Study Gallery (18), Brainstorming, Feature Guides, KB, Governance, Audit

**Recommended next:** Phase PR-1 (auth + dangerous endpoint gating) → private pilot customers

---

## Phase P0 — Foundation Fixes

> **Goal:** Make the project installable, importable, and runnable end-to-end.  
> **Priority:** CRITICAL — nothing else works reliably until this is done.

| ID | Task | Module | Status | Acceptance Criteria |
|----|------|--------|--------|---------------------|
| P0-01 | Fix `unification.py` imports (`axiomai.src` → `axiomai.reasoner`) | M3 | [x] | `from axiomai.reasoner.core.unification import UnificationEngine` works |
| P0-02 | Fix `engine.py` relative imports (`..core` → `.core`) | M9 | [x] | `from axiomai import Reasoner` works without ImportError |
| P0-03 | Fix `cli.py` relative imports (`..engine` → `.engine`) | M11 | [x] | `python -m axiomai.reasoner.cli socrates` runs |
| P0-04 | Add `main()` function to `cli.py` for entry point | M11 | [x] | `axiomai socrates` works after `pip install -e .` |
| P0-05 | Fix stale paths in `docs/README.md` and `docs/API.md` | Docs | [x] | All docs reference `axiomai.reasoner.*` |
| P0-06 | Add root `README.md` symlink or copy pointing to `docs/README.md` | Docs | [x] | GitHub renders project README |
| P0-07 | Add `LICENSE` file (MIT) | Legal | [x] | Matches `pyproject.toml` declaration |
| P0-08 | Verify `pip install -e .` + smoke test | All | [x] | Socrates demo proves `Mortal(Socrates)` |

**P0 Exit Criteria:** `axiomai socrates` and `python examples/socrates.py` both succeed. ✅ Met.

### P0 Additional Fixes (discovered during smoke test)

| ID | Task | Module | Status | Notes |
|----|------|--------|--------|-------|
| P0-09 | Backward chaining checks KB facts in recursive `_prove_goal` | M6a | [x] | Socrates was returning UNKNOWN |
| P0-10 | Normalize KB fact keys via `str(predicate)` | M5 | [x] | Fixes multi-arg lookup mismatch |
| P0-11 | Set proof tree `result`/`conclusion` on successful proofs | M7 | [x] | CLI proof footer showed UNKNOWN |

---

## Phase P1 — Core Engine Completion

> **Goal:** Complete all six inference modes, wire integrations, harden determinism.

### P1a — Resolution Engine

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| P1-01 | Implement CNF conversion for facts and rules | [x] | `Human(Socrates)` + `IF Human(x) THEN Mortal(x)` → clauses |
| P1-02 | Implement proper `_resolve_pair` (not just direct negation) | [x] | Resolves complementary literals with unification |
| P1-03 | Integrate Z3 for unsatisfiability check | [x] | `ask("Mortal(Socrates)", mode="resolution")` → PROVED |
| P1-04 | Add resolution proof steps to proof tree | [x] | Proof shows resolution steps, not empty tree |
| P1-04b | Full resolution: SOS, subsumption, factorization | [x] | Multi-hop proofs without Z3 fallback |

### P1b — Parser & Models

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| P1-05 | Add disjunction support in rule antecedents (`A OR B`) | [x] | Parser accepts `IF A OR B THEN C` |
| P1-06 | Add namespace prefixes (`domain:Predicate(x)`) | [x] | Facts isolated per namespace |
| P1-07 | Add temporal validity on facts (`valid_from`, `valid_until`) | [x] | Expired facts excluded from inference |

### P1c — Knowledge Base

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| P1-08 | Rule-based contradiction detection | [x] | Detects derived contradictions, not just direct |
| P1-09 | Truth maintenance: retraction cascades | [x] | Retracting a fact invalidates derived facts |
| P1-10 | KB versioning (snapshot ID per state) | [x] | `kb.snapshot()` returns immutable ID |

### P1d — Integrations & Facade

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| P1-11 | Wire `LLMExtractor` into `Reasoner.extract(text)` | [x] | `r.extract("Socrates is human")` adds fact |
| P1-11b | LLM client protocol + `POST /extract` + CLI `extract` | [x] | `LLMClient`, `MockLLMClient`, env-based factory |
| P1-12 | Implement smart `ask(mode="auto")` selection | [x] | Picks forward/backward/resolution by query shape |
| P1-13 | Run hash: SHA-256 of (query + KB fingerprint + result) | [x] | Same run always produces same hash |
| P1-14 | Remove or wire unused deps (`kanren`, `unification`) | [x] | No dead dependencies in pyproject.toml |

**P1 Exit Criteria:** All 6 engines pass integration tests; determinism test confirms identical outputs.

---

## Phase P2 — Platform Layer

> **Goal:** Production-ready interfaces — persistence, tests, CI, packaging.

### P2a — Test Suite (M13)

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| P2-01 | Create `tests/conftest.py` with shared `Reasoner` fixture | [x] | pytest discovers tests |
| P2-02 | `test_unification.py` — basic + occurs check cases | [x] | ≥10 cases |
| P2-03 | `test_backward.py` — Socrates, multi-rule, negation | [x] | ≥8 cases |
| P2-04 | `test_forward.py` — fixpoint, derived facts | [x] | ≥6 cases |
| P2-05 | `test_constraints.py` — Sudoku, simple CSP | [x] | Sudoku solves correctly |
| P2-06 | `test_planner.py` — blocks world or similar | [x] | Plan found for known problem |
| P2-07 | `test_causal.py` — root cause, paths | [x] | Correct root causes returned |
| P2-08 | `test_determinism.py` — 100 runs, same fingerprint + result | [x] | Zero variance |
| P2-09 | `test_api.py` — FastAPI TestClient for all endpoints | [x] | All endpoints return 200 |
| P2-10 | Property tests with hypothesis for unification | [x] | No crashes on random terms |
| P2-10b | Coverage tooling + ≥75% on `axiomai/` core | [x] | `pytest --cov=axiomai --cov-fail-under=75` in CI |
| P2-10c | `test_models.py`, `test_llm_extractor.py`, `test_narrator.py` | [x] | Core module unit tests |

### P2b — Persistence (M12)

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| P2-11 | SQLAlchemy models for facts, rules, proofs, runs | [x] | Schema matches PRD §10 |
| P2-12 | SQLite backend with async (`aiosqlite`) | [x] | KB survives process restart |
| P2-13 | `Reasoner` option: `Reasoner(persist="sqlite://...")` | [x] | Transparent persistence |
| P2-13b | Proof/run query API + contradiction audit persistence | [x] | `list_proofs`, `GET /proofs`, `GET /inference-runs` |

### P2c — Packaging & CI

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| P2-14 | GitHub Actions: lint (ruff) + test (pytest) | [x] | CI green on PR |
| P2-14b | Docker build + health check in CI | [x] | `docker build` job in workflow |
| P2-15 | `mypy` type checking on core modules | [x] | No errors on engine facade |
| P2-16 | Version bump to 0.3.0 after P2 complete | [x] | Published to PyPI (optional) |

**P2 Exit Criteria:** `pytest` passes with ≥80% coverage on core; CI enforced.

---

## Phase P3 — Application Framework

> **Goal:** Reusable layer for agent governance, connectors, and audit — shared by all case studies.

### P3a — Agent Governance (M15)

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| P3-01 | Create `axiomai/governance/` package | [x] | Importable submodule |
| P3-02 | `PolicyPack` — load rules from YAML/JSON | [x] | `PolicyPack.load("refund-policy.yaml")` |
| P3-03 | `GovernanceEngine.validate(action, context)` → Decision | [x] | Returns ALLOW/DENY/ESCALATE + proof |
| P3-04 | `AuditLog` — append-only decision log with proof JSON | [x] | Every decision logged with timestamp |
| P3-05 | `EscalationRouter` — route DENY/ESCALATE to human queue | [x] | Configurable routing rules |
| P3-05b | `AgentGovernanceMiddleware` + `PolicyRegistry` + multi-policy packs | [x] | refund, procurement, data-access, cloud-cost |
| P3-05c | Persistent audit log (`AXIOMAI_AUDIT_PERSIST`) + `/policies` API | [x] | Audit survives restart |

### P3b — Connector SDK (M16)

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| P3-06 | `Connector` protocol + base class | [x] | Documented interface |
| P3-07 | `FileConnector` — ingest facts from CSV/JSON | [x] | Used by all demos |
| P3-08 | `WebhookConnector` — receive facts via HTTP POST | [x] | Used by API integrations |
| P3-09 | Mock connectors for Azure AD, AWS, SIEM (synthetic data) | [x] | Enable offline demos |
| P3-09b | Connector REST API (`/connectors/webhook/facts`, `/connectors/file/ingest`) | [x] | Webhook + file ingest endpoints |

### P3c — Shared Case Study Utilities

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| P3-10 | `apps/case-studies/_base/` — shared demo runner, report formatter | [x] | All CS packages use same runner |

**P3 Exit Criteria:** Governance middleware demo blocks a policy-violating agent action with proof. ✅ Met.

---

## Phase P4 — Tier 1 Case Studies (Pilot Verticals)

> **Goal:** Three runnable vertical demos aligned with GTM Phase 1.  
> **Specs:** `docs/case-studies/{07,02,03}-*/README.md`

### CS-07 — Cybersecurity Root Cause Analysis

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| CS07-01 | Create `apps/case-studies/07-cybersecurity/` package | [x] | Directory structure per PROJECT-MODULES §7 |
| CS07-02 | Encode MITRE-aligned attack chain rules (10+ rules) | [x] | Phishing → execution → C2 → lateral → ransomware |
| CS07-03 | Sample incident scenario JSON (ransomware) | [x] | 15+ facts from spec |
| CS07-04 | `demo.py` — ingest facts, run causal + forward, print root cause | [x] | Identifies initial access vector |
| CS07-05 | `demo.py` — generate MTTR report (before/after metrics) | [x] | Matches spec output format |
| CS07-06 | Mock SIEM connector feeding alert facts | [x] | Uses M16 connector SDK |
| CS07-07 | Unit tests for attack chain inference | [x] | ≥5 scenarios |
| CS07-08 | README with run instructions | [x] | `python apps/case-studies/07-cybersecurity/demo.py` |

### CS-02 — SOC2 Compliance Automation

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| CS02-01 | Create `apps/case-studies/02-soc2-compliance/` package | [x] | Directory structure |
| CS02-02 | Encode SOC2 control rules (MFA, backup, log retention, access review) | [x] | ≥8 controls from spec |
| CS02-03 | Mock Azure AD + AWS evidence connectors | [x] | Synthetic admin/MFA/backup data |
| CS02-04 | Gap analysis engine — FAIL/PASS per control | [x] | Produces control gap report |
| CS02-05 | `demo.py` — full audit cycle simulation | [x] | Output matches spec format |
| CS02-06 | Export gap report as JSON + markdown | [x] | Auditor-ready format |
| CS02-07 | Unit tests per control | [x] | Each control has pass/fail test |

### CS-03 — AI Customer Support Governance

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| CS03-01 | Create `apps/case-studies/03-ai-support-governance/` package | [x] | Directory structure |
| CS03-02 | Refund policy rules (window, amount, return status) | [x] | Rules from spec |
| CS03-03 | `GovernanceEngine` integration for refund decisions | [x] | Uses M15 middleware |
| CS03-04 | 5 test scenarios (allow, deny, escalate) | [x] | All return correct decision + proof |
| CS03-05 | `demo.py` — simulate LLM refund request → governance check | [x] | Shows DENIED with violated rules |
| CS03-06 | Audit log output for each decision | [x] | Immutable log entries |

**P4 Exit Criteria:** All three demos runnable from CLI; each produces spec-matching output. ✅ Met.

---

## Phase P5 — Working Application

> **Goal:** Unified demo application combining Tier 1 case studies into a pilot product shell.

### P5a — Backend API Extensions

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| P5-01 | `/case-studies` endpoint — list available demos | [x] | Returns CS-02, CS-03, CS-07 metadata |
| P5-02 | `/case-studies/{id}/run` — execute demo scenario | [x] | Returns decision + proof + metrics |
| P5-03 | `/governance/validate` — agent action validation endpoint | [x] | Uses M15 GovernanceEngine |
| P5-04 | `/audit` — query audit log | [x] | Filterable by time, decision, case study |
| P5-05 | OpenAPI docs updated | [x] | Swagger UI shows new endpoints |

### P5b — Web Console (M17)

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| P5-06 | Choose UI stack (recommend: Streamlit for MVP speed) | [x] | Decision documented |
| P5-07 | KB editor page — add facts/rules, run query | [x] | Interactive proof viewer |
| P5-08 | Case study launcher — pick CS-02/03/07, run demo | [x] | Shows results + metrics |
| P5-09 | Governance simulator — input agent action, see ALLOW/DENY | [x] | Proof trace displayed |
| P5-10 | Docker Compose: API + UI + SQLite | [x] | `docker compose up` runs full stack |

### P5c — Documentation & Onboarding

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| P5-11 | `docs/QUICKSTART.md` — 5-minute getting started | [x] | New developer can run in 5 min |
| P5-12 | `docs/DEPLOYMENT.md` — production deployment guide | [x] | Docker + env vars documented |

**P5 Exit Criteria:** `docker compose up` launches working app; all 3 Tier 1 case studies accessible from UI. ✅ Met.

---

## Phase P6 — Remaining Case Studies (Tier 2–5)

> **Goal:** Implement remaining 15 verticals using the shared framework from P3–P5.  
> **Pattern:** Each follows the same template as P4 (package + rules + connectors + demo + tests).

### Tier 2 — High Value (build after P5)

| ID | Case Study | Slug | Key Tasks | Status |
|----|-----------|------|-----------|--------|
| CS01 | MSP Network Operations | `01-msp-network` | Topology rules, alert correlation, MTTR demo | [x] |
| CS06 | Procurement Agent Governance | `06-procurement-agent` | Spend limits, vendor rules, governance middleware | [x] |
| CS12 | Data Governance / Access Control | `12-data-governance` | HIPAA/SOC2 access rules, PII detection facts | [x] |
| CS13 | Cloud Cost Governance | `13-cloud-cost` | Budget constraints, resource policy rules | [x] |

### Tier 3 — Vertical Products

| ID | Case Study | Slug | Key Tasks | Status |
|----|-----------|------|-----------|--------|
| CS04 | Healthcare Prior Auth | `04-healthcare-prior-auth` | Clinical criteria rules, guideline facts | [x] |
| CS08 | Contract / SLA Analysis | `08-contract-analysis` | Obligation rules, deadline tracking | [x] |
| CS09 | Insurance Claims | `09-insurance-claims` | Coverage rules, claim validation | [x] |
| CS10 | Banking Loan Eligibility | `10-banking-loan` | Underwriting rules, regulatory constraints | [x] |

### Tier 4 — Niche / High Margin

| ID | Case Study | Slug | Key Tasks | Status |
|----|-----------|------|-----------|--------|
| CS11 | HR Policy Engine | `11-hr-policy` | Benefits eligibility rules | [x] |
| CS14 | Manufacturing QC | `14-manufacturing-qc` | Defect classification rules | [x] |
| CS15 | Education Degree Audit | `15-education-degree` | Transcript validation rules | [x] |
| CS16 | Immigration Assistant | `16-immigration` | Checklist rules, document requirements | [x] |
| CS17 | Sales Qualification | `17-sales-qualification` | ICP matching rules | [x] |

### Tier 5 — Future / Complex

| ID | Case Study | Slug | Key Tasks | Status |
|----|-----------|------|-----------|--------|
| CS05 | AI Code Review Guardrail | `05-ai-code-review` | Security pattern rules, architecture constraints | [x] |
| CS18 | Agentic Trading Guardrail | `18-agentic-trading` | Position limits, regulatory rules | [x] |

**P6 Exit Criteria:** All 15 remaining verticals implemented with demo + tests + API registration. ✅ Met (18/18 total).

### Per-Case-Study Task Template

For each case study `{NN}`, complete these 6 tasks:

```
CS{NN}-01  Create package at apps/case-studies/{NN}-{slug}/
CS{NN}-02  Encode domain rules from docs/case-studies/{NN}-{slug}/README.md
CS{NN}-03  Create sample scenario data (facts JSON)
CS{NN}-04  Build demo.py using _base runner
CS{NN}-05  Add unit tests (≥3 scenarios)
CS{NN}-06  Register in /case-studies API + web console launcher
```

---

## Milestone Map

```
M0: P0 complete ✅ ──────────► Project runs (axiomai socrates works)
         │
M1: P1 + P2 complete ✅ ────► Engine production-ready (tests + CI)
         │
M2: P3 complete ────────────► Governance framework demo works  ✅
         │
M3: P4 complete ────────────► 3 Tier 1 vertical demos runnable  ✅
         │
M4: P5 complete ────────────► Working application (Docker + UI)  ✅
         │
M5: P6 Tier 2 ──────────────► 4 additional verticals  ✅
         │
M6: P6 Tier 3–5 ────────────► All 18 case studies implemented  ✅
         │
M7: PR complete ────────────► Production-ready for managed SaaS
```

---

## Phase PR — Production Readiness

> **Goal:** Harden the platform for internet-facing, multi-tenant, or regulated production deployments.  
> **Audit date:** 2026-06-18 · **Verdict:** Strong demo/pilot; not production-ready without PR phase.  
> **Work top to bottom** — PR-1 blockers must ship before PR-2+.

### Deployment Tiers (what works today)

| Tier | Use case | Ready? | Minimum requirements |
|------|----------|--------|----------------------|
| **Demo** | Investor meetings, local laptop | ✅ Yes | `docker compose up` on localhost |
| **Private pilot** | 1–3 design partners on VPN | ⚠️ Mostly | VPN + PR-1 complete |
| **Embedded** | Reasoner inside customer's app | ✅ Core yes | Customer owns auth/network; use as library |
| **Managed SaaS** | Public multi-tenant product | ❌ No | PR-1 through PR-3 |
| **Regulated** | HIPAA/SOC2-hosted service | ❌ No | PR-1 through PR-4 + pen test |

### What's Already Production-Grade

| Area | Evidence |
|------|----------|
| Core reasoning engine | 6 inference modes, proof traces, contradiction detection; `tests/test_determinism.py` |
| Test & CI gate | 281 tests, ≥75% coverage on `axiomai/`; `.github/workflows/ci.yml` |
| Containerized demo | `Dockerfile`, `docker-compose.yml`, API healthcheck |
| SQLite persistence | `AXIOMAI_PERSIST`, proofs/runs/contradictions query API |
| Governance framework | 4 policy packs, middleware, audit log (`AXIOMAI_AUDIT_PERSIST` supported) |
| Secrets hygiene | `.env` gitignored; LLM keys from env only |
| Investor application | 18 case studies, Streamlit console, brainstorming, guides |

---

### PR-1 — Block Exposure (Critical Blockers)

> **Priority:** CRITICAL — do not expose API publicly until PR-1 is complete.

| ID | Task | Module | Status | Acceptance Criteria |
|----|------|--------|--------|---------------------|
| PR-01 | API authentication (API key or OAuth2 bearer) on all routes | `axiomai/reasoner/api/` | [ ] | Unauthenticated requests return 401; tests cover auth |
| PR-02 | Role-based access: read-only vs admin scopes | API middleware | [ ] | Mutating routes require admin scope |
| PR-03 | Gate `POST /reset` behind `AXIOMAI_DEV_MODE=true` or remove in prod | `main.py` | [ ] | `/reset` returns 404/403 when dev mode off |
| PR-04 | Gate `DELETE /audit` behind dev mode or admin-only | `routes_app.py` | [ ] | Audit log cannot be cleared in production |
| PR-05 | Remove or restrict `POST /connectors/file/ingest` arbitrary path read | `routes_connectors.py` | [ ] | Allowlist directory only; path traversal blocked; security tests |
| PR-06 | Replace `eval()` in constraint solver with safe expression parser | `engines/constraints.py` | [ ] | `POST /constraints/solve` rejects unsafe input; no RCE |
| PR-07 | Document private-network-only deployment until PR-01 ships | `docs/DEPLOYMENT.md` | [ ] | Warning banner + VPN requirement stated |
| PR-08 | Add `.env.example` with all supported env vars | repo root | [ ] | `AXIOMAI_PERSIST`, `AXIOMAI_AUDIT_PERSIST`, `OPENAI_API_KEY`, `AXIOMAI_DEV_MODE`, auth vars |

**PR-1 Exit Criteria:** API requires auth; dangerous endpoints gated; file ingest restricted; constraints safe. ✅ Required before any public exposure.

---

### PR-2 — Security Core (High Priority)

| ID | Task | Module | Status | Acceptance Criteria |
|----|------|--------|--------|---------------------|
| PR-09 | TLS termination sample config (nginx or Caddy) | `deploy/` or `docs/DEPLOYMENT.md` | [ ] | Copy-paste config terminates HTTPS → API/UI |
| PR-10 | CORS allowlist middleware | `main.py` | [ ] | Configurable origins; default deny |
| PR-11 | Rate limiting on expensive endpoints | API middleware | [ ] | `/query`, `/forward`, `/extract` throttled |
| PR-12 | Streamlit console behind auth (OAuth proxy or built-in) | `apps/console/` | [ ] | Unauthenticated users cannot reach UI |
| PR-13 | Lock console API URL to configured host (prevent SSRF) | `apps/console/app.py` | [ ] | Sidebar cannot point httpx at arbitrary hosts |
| PR-14 | Protect `/docs` and `/openapi.json` in production | `main.py` | [ ] | Disabled or auth-gated when `AXIOMAI_DEV_MODE` off |
| PR-15 | Webhook HMAC signature validation | `routes_connectors.py` | [ ] | `POST /connectors/webhook/facts` rejects unsigned payloads |
| PR-16 | Pin dependencies (lock file) | `pyproject.toml` + lock | [ ] | Reproducible installs; CI uses lock file |
| PR-17 | Docker non-root user | `Dockerfile` | [ ] | Container runs as unprivileged UID |
| PR-18 | LLM call guards: timeout, retry limit, token budget | `llm_client.py` | [ ] | Hung/expensive LLM calls fail fast |
| PR-19 | PII / prompt-injection filtering on `POST /extract` | `llm_extractor.py` | [ ] | Documented limits; oversized input rejected |
| PR-20 | Security scanning in CI (Bandit + Trivy or equivalent) | `.github/workflows/` | [ ] | CI fails on critical CVEs / high-severity findings |

**PR-2 Exit Criteria:** HTTPS deployable; abuse-resistant API; hardened LLM and connector surfaces.

---

### PR-3 — Operations & Observability (High Priority)

| ID | Task | Module | Status | Acceptance Criteria |
|----|------|--------|--------|---------------------|
| PR-21 | Structured logging (JSON) with request correlation IDs | `axiomai/` | [ ] | Every API request logged with `request_id` |
| PR-22 | Prometheus `/metrics` endpoint | API | [ ] | Request count, latency, error rate exposed |
| PR-23 | Deep health check (`/health` verifies DB + disk) | `main.py` | [ ] | Unhealthy when SQLite unreachable or disk full |
| PR-24 | Set `AXIOMAI_AUDIT_PERSIST` in `docker-compose.yml` | `docker-compose.yml` | [ ] | Governance audit survives container restart |
| PR-25 | SQLite backup script + restore procedure | `scripts/` + docs | [ ] | Documented one-command backup of `/data` volume |
| PR-26 | Alembic (or equivalent) schema migrations | `axiomai/reasoner/kb/` | [ ] | Schema changes versioned; upgrade path documented |
| PR-27 | PostgreSQL backend (or document SQLite single-node limit) | `kb/persistence.py` | [ ] | Multi-instance API supported OR limitation explicit in docs |
| PR-28 | Audit store file locking / atomic writes | `audit_store.py` | [ ] | Concurrent writes do not corrupt audit JSON |
| PR-29 | Graceful shutdown / lifespan hooks | `main.py` | [ ] | In-flight requests complete; DB connections closed |
| PR-30 | Compose: `restart` policy + resource limits | `docker-compose.yml` | [ ] | Services auto-restart; memory/CPU capped |
| PR-31 | Production runbook (incident, rollback, backup) | `docs/runbooks/` | [ ] | On-call can restore from backup in <30 min |
| PR-32 | Update `DEPLOYMENT.md` — all env vars, all endpoints | `docs/DEPLOYMENT.md` | [ ] | Matches live API (brainstorm, scenarios, connectors) |

**PR-3 Exit Criteria:** Observable, backupable, operable single-node deployment with persistent audit.

---

### PR-4 — Scale, Tenancy & Release (Medium Priority)

| ID | Task | Module | Status | Acceptance Criteria |
|----|------|--------|--------|---------------------|
| PR-33 | Per-tenant KB namespace / isolation | `Reasoner`, API | [ ] | Tenants cannot read or mutate each other's facts |
| PR-34 | API versioning (`/v1/` prefix) | API routes | [ ] | Breaking changes ship under new version |
| PR-35 | Custom policy pack registration via API | `governance/` | [ ] | Customers load YAML without code deploy |
| PR-36 | Real connector credentials (Azure AD, AWS, SIEM) | `axiomai/connectors/` | [ ] | At least one non-mock connector with secret management |
| PR-37 | CD pipeline — image publish + tagged releases | `.github/workflows/` | [ ] | `v*` tag triggers image push to registry |
| PR-38 | Gunicorn / multi-worker deployment guide | `docs/DEPLOYMENT.md` | [ ] | Document worker count for CPU-bound inference |
| PR-39 | Load tests (locust or k6) in CI or nightly | `tests/load/` | [ ] | Baseline latency/throughput documented |
| PR-40 | Security test suite (auth bypass, path abuse, injection) | `tests/security/` | [ ] | CI runs security tests on every PR |
| PR-41 | Include `apps/` in coverage or dedicated integration tests | `pyproject.toml`, tests | [ ] | Case study runners and console paths tested |
| PR-42 | Bump classifier to Beta; PyPI publish workflow | `pyproject.toml`, CI | [ ] | `pip install axiomai` from PyPI with pinned release |

**PR-4 Exit Criteria:** Multi-tenant ready; release automation; load and security baselines established.

---

### PR Readiness Grades (current)

| Layer | Grade | Notes |
|-------|-------|-------|
| Reasoning engine | **A** | Tested, deterministic, feature-complete |
| Governance framework | **B+** | Works; audit persistence and custom policies need ops work |
| Case studies / console | **A-** | Investor-ready; Streamlit is MVP by design |
| API security | **F** | No auth; dangerous endpoints exposed |
| DevOps / SRE | **D** | CI yes; CD, observability, backups no |
| Operator documentation | **C** | Good dev docs; weak production runbooks |

---

## Dependency Matrix

| Task | Depends On |
|------|------------|
| P1-* | P0-* |
| P2-* | P0-* |
| P3-* | P1-*, P2-* |
| CS07/02/03-* | P3-* |
| P5-* | P4-* |
| CS01,06,12,13-* | P5-* |
| CS04,08,09,10-* | Tier 2 complete |
| CS11,14,15,16,17-* | Tier 3 complete |
| CS05,18-* | Tier 4 complete |
| PR-1-* | P5-* (working app exists) |
| PR-2-* | PR-1-* |
| PR-3-* | PR-1-* |
| PR-4-* | PR-2-*, PR-3-* |

---

## Risk Register

| Risk | Impact | Status | Mitigation |
|------|--------|--------|------------|
| Import path bugs block all development | High | ✅ Resolved | P0 complete (PR #4) |
| Invalid PyPI deps block install | High | ✅ Resolved | Removed `unification>=0.4.2`, `kanren` |
| **No API authentication** | **Critical** | **Open** | PR-01, PR-02; block public exposure until done |
| **Dangerous endpoints exposed (`/reset`, file ingest, `eval`)** | **Critical** | **Open** | PR-03–PR-06 |
| **Single global KB — no tenant isolation** | **High** | **Open** | PR-33; document single-tenant limit until then |
| Resolution engine too complex for MVP | Medium | Open | Ship with backward chaining; resolution as beta |
| Case studies scope creep | High | ✅ Mitigated | 18/18 complete with JSON scenario template |
| Connector integrations need real credentials | Medium | Open | Mock connectors first; PR-36 for production |
| No frontend expertise | Medium | ✅ Mitigated | Streamlit MVP shipped; React deferred to PR-4+ |
| Determinism regressions | High | ✅ Mitigated | `test_determinism.py` in CI (P2-08) |
| Audit log not persisted in default compose | Medium | Open | PR-24 |
| PostgreSQL documented but not implemented | Medium | Open | PR-27 |
| Unpinned dependencies | Medium | Open | PR-16 |
| No production runbooks | Medium | Open | PR-31 |

---

## Progress Log

| Date | Phase | Update |
|------|-------|--------|
| 2026-06-18 | PR | Production Readiness audit — 42 tracked tasks (PR-01–PR-42), deployment tiers, readiness grades |
| 2026-06-18 | Investor | 18 case studies with JSON scenarios, investor console, brainstorming, guides |
| 2026-06-18 | Platform | Full verification — all 9 former "Not Implemented" items complete |
| 2026-06-18 | P6 | All 15 remaining case studies — 18/18 verticals, 281 tests |
| 2026-06-17 | P5 | Working app — API extensions, Streamlit console, Docker Compose |
| 2026-06-17 | P0 | Foundation fixes complete: deps, imports, CLI, backward chaining, KB keys |
| 2026-06-17 | — | PR #3 merged to master: module docs + tracker (docs only) |
| 2026-06-17 | — | Tracker v1.0 created. Engine ~85% alpha. 18 case study specs exist. |

---

## Quick Reference: What Exists Today

### Implemented (verified after P0)

- `pip install -e ".[dev]"` succeeds
- `from axiomai import Reasoner` — no import errors
- `axiomai socrates` → PROVED: `Mortal(Socrates)`
- Predicate/Fact/Rule models and parser
- Backward and forward chaining with proof trees
- Z3 constraint solver + Sudoku
- STRIPS planner
- Causal graph engine
- In-memory KB with contradiction detection + normalized fact keys
- FastAPI REST server (all endpoints)
- Typer CLI with `main()` entry point
- Explanation narrator (4 styles)
- `examples/socrates.py` (5 demos)
- Root `README.md`, `LICENSE`, corrected doc paths
- Full resolution engine (SOS, subsumption, factorization, Z3 fallback)
- Persistent storage (SQLite facts/rules/proofs/runs/contradictions + query API)
- Test suite with coverage enforcement (≥75% on core, **281 tests**, ~79% coverage)
- LLM integration on Reasoner facade (`LLMClient`, `/extract`, CLI)
- Agent governance framework (`AgentGovernanceMiddleware`, multi-policy, persistent audit)
- Connector SDK + REST API (`/connectors/webhook/facts`, `/connectors/file/ingest`)
- Web UI — Streamlit console (KB, 18 case studies, governance, audit) + Docker Compose
- All 18 case study applications (registry + API + tests)
- CI/CD pipeline (ruff + pytest + coverage + mypy + Docker build)

### Partially Implemented (production gaps)

- **API security** — no authentication; `/reset`, `DELETE /audit`, file ingest, and `eval()` constraints exposed (see PR-01–PR-06)
- **Operations** — no structured logging, metrics, backups, or runbooks (see PR-21–PR-31)
- **Multi-tenancy** — single global `Reasoner` per process (see PR-33)
- **PostgreSQL** — documented in PROJECT-MODULES but not implemented (see PR-27)
- **CD / releases** — CI only; no image publish or PyPI workflow (see PR-37, PR-42)
- **Real connectors** — Azure/AWS/SIEM are mocks (see PR-36)
- **Operator docs** — `DEPLOYMENT.md` stale vs live API; no `.env.example` (see PR-08, PR-32)

### Not Implemented (production readiness — Phase PR)

All 42 tasks in [Phase PR](#phase-pr--production-readiness) (PR-01 through PR-42). Feature development (P0–P6) is complete; production hardening is not.

---

## Related Documents

| Document | Purpose |
|----------|---------|
| [PROJECT-MODULES.md](./PROJECT-MODULES.md) | Module architecture reference |
| [PRD.md](../PRD.md) | Product requirements |
| [MASTER-BUSINESS-STRATEGY.md](./business/MASTER-BUSINESS-STRATEGY.md) | GTM and case study priority |
| [docs/case-studies/](./case-studies/) | Per-vertical specifications |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | Docker deployment (demo); production hardening in Phase PR |
| [guides/FEATURES.md](./guides/FEATURES.md) | Platform feature guide for pilots |
| [API.md](./API.md) | REST API reference |
