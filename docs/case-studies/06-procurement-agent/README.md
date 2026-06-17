# Case Study 6: Procurement Agent Governance

**Industry:** Enterprise (All industries)
**Vertical:** Autonomous Agent Governance
**Revenue Potential:** Prevents uncontrolled cloud spend

---

## Problem

**AI agents are being deployed to purchase cloud resources — without governance.**

Current autonomous agent problem:
```
AI Agent → Buys $50,000 GPU cluster
    ↓
Finance discovers charge
    ↓
No approval workflow
    ↓
No budget visibility
    ↓
Board question: "Who authorized this?"
```

---

## Solution: Deterministic Policy Engine

**Governance rules:**
```
Rule: Budget thresholds
  IF purchase_amount > $1000
  THEN require_manager_approval

Rule: Large purchases
  IF purchase_amount > $10000
  THEN require_finance_approval

Rule: New vendor
  IF vendor NOT IN approved_vendors
  THEN require_security_review

Rule: Long-term contracts
  IF contract_term > 12 months
  THEN require_legal_review

Rule: GPU/AI resources
  IF resource_type IN [GPU, TPU, AI_accelerator]
  THEN require_cost_analysis
```

---

## Engine Output

```
Purchase Request: BLOCKED

Request: GPU cluster — $45,000/month
Vendor: NewCloudProvider (not approved)
Contract: 24-month commitment

Blocked reasons:
  1. [CRITICAL] New vendor — requires security review
  2. [HIGH] Amount > $10K — requires finance approval
  3. [HIGH] 24-month term — requires legal review

Action required:
  Submit vendor for security assessment.
  Obtain finance sign-off.
  Legal contract review.

Request queued for:
  CFO approval
  CISO security review
  Legal review
```

---

## Business Value

| Metric | Before | After |
|--------|--------|-------|
| Rogue purchases | Possible | Prevented |
| Budget surprises | Frequent | None |
| Compliance posture | Weak | Strong |
| Auditability | Low | Full |
| CFO confidence | Low | High |

**For a mid-market company: $200K–$2M/year prevented in unauthorized spend**

---

## Extendable to All Agent Actions

```
Agent Actions Governed:
  ✓ Cloud resource provisioning
  ✓ Vendor onboarding
  ✓ Data sharing agreements
  ✓ Customer contract terms
  ✓ Employee offboarding
  ✓ Access provisioning
  ✓ External API calls
  ✓ Data exports
```

---

## Deployment Pattern

```
AI Agent Intent → AxiomAI Governance
    │
    ├── Policy Check
    │   ├── ALLOW → Execute
    │   ├── BLOCK → Require approval
    │   └── MODIFY → Suggest changes
    │
    ▼
Approval Workflow (if needed)
    │
    ▼
Execution + Audit Trail
    │
    ▼
Finance / Compliance Dashboard
```

---

## Compliance Mapping

| Standard | Requirement | AxiomAI Checks |
|----------|-------------|----------------|
| SOC2 CC9 | Change management | Approval workflows |
| SOX | Financial controls | Budget thresholds |
| ISO 27001 A.15 | Supplier relationships | Vendor approval |
| NIST 800-53 | Contingency planning | Vendor risk |
| PCI DSS | Vendor management | Third-party risk |
