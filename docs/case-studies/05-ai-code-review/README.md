# Case Study 5: AI Code Review Guardrail

**Industry:** Software Development / DevOps
**Vertical:** Autonomous Software Engineering (TEL / Bingo.dev)
**Revenue Potential:** Prevents security defects before production

---

## Problem

**LLM coding assistants generate code that violates security policies and architecture rules.**

Common LLM code issues:
- Hardcoded secrets (API keys, passwords)
- SQL injection vulnerabilities
- Missing authentication on endpoints
- Direct database access from UI layer
- Unapproved dependencies
- License violations

**Current state:**
- Manual code review
- SAST tools (high false positive rate)
- LLM reviews LLM code (circular)

---

## Solution: Deterministic Reasoning Layer

**Security and architecture rules encoded:**
```
Rule: No hardcoded secrets
  IF "password" IN code
  OR "api_key" IN code
  OR "secret" IN code
  THEN flag_violation

Rule: All API endpoints require authentication
  IF route_definition
  AND NOT authentication_required
  THEN block_deploy

Rule: No direct DB access from UI
  IF frontend_code
  AND SQL_query
  THEN flag_violation

Rule: Dependencies must be approved
  IF new_dependency
  AND NOT in_approved_list
  THEN require_security_review
```

---

## Engine Output

```
Code PR: feature/add-auth

Violations detected:

1. [CRITICAL] Hardcoded secret
   File: src/config.py:23
   Line: password="admin123"

2. [HIGH] Missing auth on endpoint
   File: src/api/users.py:5
   Endpoint: /api/users (no @require_auth)

3. [MEDIUM] Direct SQL in frontend
   File: src/pages/orders.js:42
   Query: raw SQL without ORM

Deploy: BLOCKED

Actions required:
  1. Move secret to environment variable
  2. Add @require_auth decorator
  3. Move SQL to backend API
```

---

## Business Value

| Metric | Before | After |
|--------|--------|-------|
| Security defects in code | High | Low |
| Manual review effort | 2 hr/PR | 5 min |
| Secret leaks to prod | 2–5/year | 0 |
| Compliance posture | Uncertain | Verifiable |
| Dev velocity impact | None | Minimal |

**For 100-dev team: $500K–$1M/year in prevented incidents**

---

## Extendable Rules

```
Architecture Rules:
  ✓ No circular dependencies
  ✓ No circular imports
  ✓ Required test coverage
  ✓ No deprecated library usage

Business Rules:
  ✓ No PII in logs
  ✓ Data residency requirements
  ✓ Rate limiting on all endpoints
  ✓ Required security headers

License Compliance:
  ✓ No GPL in proprietary products
  ✓ No unapproved open source
```

---

## Deployment Pattern

```
Developer → PR → LLM Code Review
    │
    ├── Generate code
    │
    ▼
AxiomAI Code Guardrail
    │
    ├── Parse code AST
    ├── Extract facts (imports, secrets, routes)
    ├── Match against rules
    │
    ▼
Block / Warn / Approve
    │
    ▼
CI/CD Pipeline
```

---

## Compliance Mapping

| Standard | Requirement | AxiomAI Checks |
|----------|-------------|----------------|
| SOC2 CC7 | Security vulnerabilities | SAST equivalent |
| ISO 27001 A.14 | Secure development | Architecture rules |
| PCI DSS | Secure coding | No secrets, auth required |
| HIPAA | Technical safeguards | No PII in code |
| NIST 800-53 | System & communications | Dependency review |
