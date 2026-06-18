# AxiomAI — Implementation Tracker

**Version:** 1.1  
**Date:** 2026-06-17  
**Last Updated:** 2026-06-17 (P0 complete, PR #4 open)  
**Companion doc:** [PROJECT-MODULES.md](./PROJECT-MODULES.md)

Use this document as the single source of truth for build progress. Update checkboxes as work completes.

---

## How to Use This Tracker

1. Work **top to bottom within each phase** unless a dependency note says otherwise.
2. Do not start **Phase 4 (case studies)** until **Phase 0–2** are complete.
3. Mark items: `[ ]` not started · `[~]` in progress · `[x]` done · `[—]` cancelled/deferred
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
| P3 | Application Framework | 0/10 | Depends on P2 |
| P4 | Tier 1 Case Studies | 0/3 verticals | Depends on P3 |
| P5 | Working Application | 0/8 | Depends on P4 |
| P6 | Tier 2–5 Case Studies | 0/15 verticals | Depends on P5 |

**Overall:** P0–P2 complete. 85 tests passing. CI configured. v0.3.0. Next: P3 application framework.

**Active branch:** `cursor/p2-platform-layer-ef4a`

**Recommended next:** P3 — agent governance framework and connector SDK

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

### P2b — Persistence (M12)

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| P2-11 | SQLAlchemy models for facts, rules, proofs, runs | [x] | Schema matches PRD §10 |
| P2-12 | SQLite backend with async (`aiosqlite`) | [x] | KB survives process restart |
| P2-13 | `Reasoner` option: `Reasoner(persist="sqlite://...")` | [x] | Transparent persistence |

### P2c — Packaging & CI

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| P2-14 | GitHub Actions: lint (ruff) + test (pytest) | [x] | CI green on PR |
| P2-15 | `mypy` type checking on core modules | [x] | No errors on engine facade |
| P2-16 | Version bump to 0.3.0 after P2 complete | [x] | Published to PyPI (optional) |

**P2 Exit Criteria:** `pytest` passes with ≥80% coverage on core; CI enforced.

---

## Phase P3 — Application Framework

> **Goal:** Reusable layer for agent governance, connectors, and audit — shared by all case studies.

### P3a — Agent Governance (M15)

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| P3-01 | Create `axiomai/governance/` package | [ ] | Importable submodule |
| P3-02 | `PolicyPack` — load rules from YAML/JSON | [ ] | `PolicyPack.load("refund-policy.yaml")` |
| P3-03 | `GovernanceEngine.validate(action, context)` → Decision | [ ] | Returns ALLOW/DENY/ESCALATE + proof |
| P3-04 | `AuditLog` — append-only decision log with proof JSON | [ ] | Every decision logged with timestamp |
| P3-05 | `EscalationRouter` — route DENY/ESCALATE to human queue | [ ] | Configurable routing rules |

### P3b — Connector SDK (M16)

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| P3-06 | `Connector` protocol + base class | [ ] | Documented interface |
| P3-07 | `FileConnector` — ingest facts from CSV/JSON | [ ] | Used by all demos |
| P3-08 | `WebhookConnector` — receive facts via HTTP POST | [ ] | Used by API integrations |
| P3-09 | Mock connectors for Azure AD, AWS, SIEM (synthetic data) | [ ] | Enable offline demos |

### P3c — Shared Case Study Utilities

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| P3-10 | `apps/case-studies/_base/` — shared demo runner, report formatter | [ ] | All CS packages use same runner |

**P3 Exit Criteria:** Governance middleware demo blocks a policy-violating agent action with proof.

---

## Phase P4 — Tier 1 Case Studies (Pilot Verticals)

> **Goal:** Three runnable vertical demos aligned with GTM Phase 1.  
> **Specs:** `docs/case-studies/{07,02,03}-*/README.md`

### CS-07 — Cybersecurity Root Cause Analysis

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| CS07-01 | Create `apps/case-studies/07-cybersecurity/` package | [ ] | Directory structure per PROJECT-MODULES §7 |
| CS07-02 | Encode MITRE-aligned attack chain rules (10+ rules) | [ ] | Phishing → execution → C2 → lateral → ransomware |
| CS07-03 | Sample incident scenario JSON (ransomware) | [ ] | 15+ facts from spec |
| CS07-04 | `demo.py` — ingest facts, run causal + forward, print root cause | [ ] | Identifies initial access vector |
| CS07-05 | `demo.py` — generate MTTR report (before/after metrics) | [ ] | Matches spec output format |
| CS07-06 | Mock SIEM connector feeding alert facts | [ ] | Uses M16 connector SDK |
| CS07-07 | Unit tests for attack chain inference | [ ] | ≥5 scenarios |
| CS07-08 | README with run instructions | [ ] | `python apps/case-studies/07-cybersecurity/demo.py` |

### CS-02 — SOC2 Compliance Automation

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| CS02-01 | Create `apps/case-studies/02-soc2-compliance/` package | [ ] | Directory structure |
| CS02-02 | Encode SOC2 control rules (MFA, backup, log retention, access review) | [ ] | ≥8 controls from spec |
| CS02-03 | Mock Azure AD + AWS evidence connectors | [ ] | Synthetic admin/MFA/backup data |
| CS02-04 | Gap analysis engine — FAIL/PASS per control | [ ] | Produces control gap report |
| CS02-05 | `demo.py` — full audit cycle simulation | [ ] | Output matches spec format |
| CS02-06 | Export gap report as JSON + markdown | [ ] | Auditor-ready format |
| CS02-07 | Unit tests per control | [ ] | Each control has pass/fail test |

### CS-03 — AI Customer Support Governance

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| CS03-01 | Create `apps/case-studies/03-ai-support-governance/` package | [ ] | Directory structure |
| CS03-02 | Refund policy rules (window, amount, return status) | [ ] | Rules from spec |
| CS03-03 | `GovernanceEngine` integration for refund decisions | [ ] | Uses M15 middleware |
| CS03-04 | 5 test scenarios (allow, deny, escalate) | [ ] | All return correct decision + proof |
| CS03-05 | `demo.py` — simulate LLM refund request → governance check | [ ] | Shows DENIED with violated rules |
| CS03-06 | Audit log output for each decision | [ ] | Immutable log entries |

**P4 Exit Criteria:** All three demos runnable from CLI; each produces spec-matching output.

---

## Phase P5 — Working Application

> **Goal:** Unified demo application combining Tier 1 case studies into a pilot product shell.

### P5a — Backend API Extensions

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| P5-01 | `/case-studies` endpoint — list available demos | [ ] | Returns CS-02, CS-03, CS-07 metadata |
| P5-02 | `/case-studies/{id}/run` — execute demo scenario | [ ] | Returns decision + proof + metrics |
| P5-03 | `/governance/validate` — agent action validation endpoint | [ ] | Uses M15 GovernanceEngine |
| P5-04 | `/audit` — query audit log | [ ] | Filterable by time, decision, case study |
| P5-05 | OpenAPI docs updated | [ ] | Swagger UI shows new endpoints |

### P5b — Web Console (M17)

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| P5-06 | Choose UI stack (recommend: Streamlit for MVP speed) | [ ] | Decision documented |
| P5-07 | KB editor page — add facts/rules, run query | [ ] | Interactive proof viewer |
| P5-08 | Case study launcher — pick CS-02/03/07, run demo | [ ] | Shows results + metrics |
| P5-09 | Governance simulator — input agent action, see ALLOW/DENY | [ ] | Proof trace displayed |
| P5-10 | Docker Compose: API + UI + SQLite | [ ] | `docker compose up` runs full stack |

### P5c — Documentation & Onboarding

| ID | Task | Status | Acceptance Criteria |
|----|------|--------|---------------------|
| P5-11 | `docs/QUICKSTART.md` — 5-minute getting started | [ ] | New developer can run in 5 min |
| P5-12 | `docs/DEPLOYMENT.md` — production deployment guide | [ ] | Docker + env vars documented |

**P5 Exit Criteria:** `docker compose up` launches working app; all 3 Tier 1 case studies accessible from UI.

---

## Phase P6 — Remaining Case Studies (Tier 2–5)

> **Goal:** Implement remaining 15 verticals using the shared framework from P3–P5.  
> **Pattern:** Each follows the same template as P4 (package + rules + connectors + demo + tests).

### Tier 2 — High Value (build after P5)

| ID | Case Study | Slug | Key Tasks | Status |
|----|-----------|------|-----------|--------|
| CS01 | MSP Network Operations | `01-msp-network` | Topology rules, alert correlation, MTTR demo | [ ] |
| CS06 | Procurement Agent Governance | `06-procurement-agent` | Spend limits, vendor rules, governance middleware | [ ] |
| CS12 | Data Governance / Access Control | `12-data-governance` | HIPAA/SOC2 access rules, PII detection facts | [ ] |
| CS13 | Cloud Cost Governance | `13-cloud-cost` | Budget constraints, resource policy rules | [ ] |

### Tier 3 — Vertical Products

| ID | Case Study | Slug | Key Tasks | Status |
|----|-----------|------|-----------|--------|
| CS04 | Healthcare Prior Auth | `04-healthcare-prior-auth` | Clinical criteria rules, guideline facts | [ ] |
| CS08 | Contract / SLA Analysis | `08-contract-analysis` | Obligation rules, deadline tracking | [ ] |
| CS09 | Insurance Claims | `09-insurance-claims` | Coverage rules, claim validation | [ ] |
| CS10 | Banking Loan Eligibility | `10-banking-loan` | Underwriting rules, regulatory constraints | [ ] |

### Tier 4 — Niche / High Margin

| ID | Case Study | Slug | Key Tasks | Status |
|----|-----------|------|-----------|--------|
| CS11 | HR Policy Engine | `11-hr-policy` | Benefits eligibility rules | [ ] |
| CS14 | Manufacturing QC | `14-manufacturing-qc` | Defect classification rules | [ ] |
| CS15 | Education Degree Audit | `15-education-degree` | Transcript validation rules | [ ] |
| CS16 | Immigration Assistant | `16-immigration` | Checklist rules, document requirements | [ ] |
| CS17 | Sales Qualification | `17-sales-qualification` | ICP matching rules | [ ] |

### Tier 5 — Future / Complex

| ID | Case Study | Slug | Key Tasks | Status |
|----|-----------|------|-----------|--------|
| CS05 | AI Code Review Guardrail | `05-ai-code-review` | Security pattern rules, architecture constraints | [ ] |
| CS18 | Agentic Trading Guardrail | `18-agentic-trading` | Position limits, regulatory rules | [ ] |

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
M2: P3 complete ────────────► Governance framework demo works  ← CURRENT TARGET
         │
M3: P4 complete ────────────► 3 Tier 1 vertical demos runnable
         │
M4: P5 complete ────────────► Working application (Docker + UI)
         │
M5: P6 Tier 2 ──────────────► 4 additional verticals
         │
M6: P6 Tier 3–5 ────────────► All 18 case studies implemented
```

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

---

## Risk Register

| Risk | Impact | Status | Mitigation |
|------|--------|--------|------------|
| Import path bugs block all development | High | ✅ Resolved | P0 complete (PR #4) |
| Invalid PyPI deps block install | High | ✅ Resolved | Removed `unification>=0.4.2`, `kanren` |
| Resolution engine too complex for MVP | Medium | Open | Ship with backward chaining; resolution as beta |
| Case studies scope creep | High | Open | Strict 6-task template per vertical |
| Connector integrations need real credentials | Medium | Open | Mock connectors with synthetic data first |
| No frontend expertise | Medium | Open | Streamlit MVP before React |
| Determinism regressions | High | Open | `test_determinism.py` in CI (P2-08) |

---

## Progress Log

| Date | Phase | Update |
|------|-------|--------|
| 2026-06-17 | P2 | Platform layer: 85 tests, SQLite persistence, CI, v0.3.0 |
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

### Partially Implemented

- Resolution engine (stub `_resolve_pair`, no full CNF)
- LLM extractor module (not wired to `Reasoner` facade)
- KB namespace / versioning / temporal validity

### Not Implemented

- Resolution (full)
- Persistent storage
- Test suite
- LLM integration on Reasoner facade
- Agent governance framework
- Connectors
- Web UI
- All 18 case study applications
- CI/CD pipeline

---

## Related Documents

| Document | Purpose |
|----------|---------|
| [PROJECT-MODULES.md](./PROJECT-MODULES.md) | Module architecture reference |
| [PRD.md](../PRD.md) | Product requirements |
| [MASTER-BUSINESS-STRATEGY.md](./business/MASTER-BUSINESS-STRATEGY.md) | GTM and case study priority |
| [docs/case-studies/](./case-studies/) | Per-vertical specifications |
| [API.md](./API.md) | REST API reference |
