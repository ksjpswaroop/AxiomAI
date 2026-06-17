# Case Study 3: AI Customer Support Governance

**Industry:** E-commerce, SaaS, Fintech, Healthcare
**Vertical:** Agent Governance / Refund Control
**Revenue Potential:** Prevents 100% of unauthorized refunds

---

## Problem

**LLM support agents refund customers without proper policy checks.**

Occurrences:
- Refunds issued outside policy window
- Amounts exceeding policy limits
- Products not eligible for return
- Duplicate refunds

**Cost:** Revenue leakage, customer disputes, audit failures

---

## Solution: Deterministic Reasoning Layer

**Policy encoded as rules:**
```
Rule: Refund allowed
  IF purchase_date < 30 days
  AND amount < $500
  AND product_returned = true
  AND not_final_sale

Rule: Manager approval required
  IF amount >= $500 AND < $2000

Rule: Block refund
  IF already_refunded = true
```

**LLM suggests:** "Refund customer $350"

**Reasoner checks:**
```
purchase_date: 43 days ago    ← VIOLATION
amount: $350                  ← OK
product_returned: false       ← VIOLATION
already_refunded: false       ← OK
```

---

## Engine Output

```
Refund: DENIED

Reason:
  1. Purchase was 43 days ago — exceeds 30-day window.
  2. Product not yet returned.

Rule violated:
  Refund Window Policy §4.2

Request returned to:
  L1 agent with explanation
```

---

## Business Value

| Metric | Before | After |
|--------|--------|-------|
| Policy violations | Frequent | Near zero |
| Auditability | None | Complete |
| Compliance risk | High | Low |
| Refund abuse cost | 2–5% revenue | $0 |
| Customer disputes | High | Reduced |

**For a $10M/year e-commerce business: $200K–$500K saved**

---

## Extendable to Other Agent Actions

```
Governed Actions:
  ✓ Refunds
  ✓ Account bans
  ✓ Credit adjustments
  ✓ Discount approvals
  ✓ Contract modifications
  ✓ Data deletions (GDPR)
```

---

## Deployment Pattern

```
Customer Message
    │
    ▼
LLM Support Agent (generates response)
    │
    ├── Suggest refund
    │   ▼
    │   AxiomAI Policy Check
    │   ├── ALLOW → Execute refund
    │   ├── DENY → Modify response
    │   └── ESCALATE → Manager queue
    │
    └── Suggest ban / credit / etc.
        ▼
    AxiomAI Policy Check
```

---

## Compliance Mapping

| Standard | Requirement | AxiomAI Checks |
|----------|-------------|----------------|
| SOC2 CC6 | Logical access | Refund authority limits |
| PCI DSS | Transaction controls | Amount thresholds |
| GDPR Art. 17 | Right to erasure | Data deletion approval |
| SOX | Financial controls | Credit adjustments |
