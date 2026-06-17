# Case Study 10: Banking Loan Eligibility

**Industry:** Banking / Credit Unions / FinTech
**Vertical:** Loan Underwriting Automation
**Revenue Potential:** $12B lending automation market

---

## Problem

**Loan officers manually verify credit rules, income checks, debt ratios, and risk thresholds.**

Current process:
```
Application received
    ↓
LO reads policy manual (hundreds of pages)
    ↓
Checks: debt-to-income ratio
Checks: credit score threshold
Checks: income verification
Checks: employment history
Checks: collateral value
Checks: risk tier
    ↓
Manual decision or escalation
```

**Time per application:** 3–7 days
**Cost per application:** $200–$1,000 in LO time
**Regulatory risk:** Manual interpretation = compliance exposure

---

## Solution: Deterministic Reasoning Engine

**Policy rules encoded:**
```
Rule: Prime eligibility
  IF credit_score >= 720
  AND debt_to_income <= 36%
  AND income_verified = true
  AND employment >= 2 years
  THEN eligible_tier = prime

Rule: Subprime eligibility
  IF credit_score >= 620
  AND debt_to_income <= 43%
  AND income_verified = true
  THEN eligible_tier = subprime

Rule: Decline
  IF debt_to_income > 50%
  OR credit_score < 580
  OR fraud_flag = true
  THEN declined

Rule: Manual review required
  IF self_employed = true
  AND income_volatility > 30%
  THEN manual_review_required
```

---

## Engine Output

```
Application: #APP-2026-4421
Type: Personal Loan — $35,000
Applicant: John D.

Decision: NOT ELIGIBLE YET

Credit score: 685
Debt-to-income: 49%
Income verified: Yes
Employment: 3.2 years

Failures:
  • DTI 49% — exceeds 43% subprime maximum

Current status:
  Please pay down debt to reach DTI <= 43%

Pre-approval possible when:
  • DTI <= 43% (current: 49%)
  • Required debt reduction: ~$340/month

Alternative:
  Reduce requested amount to $25,000
  Results in DTI of 39% — APPROVED
```

---

## Business Value

| Metric | Before | After |
|--------|--------|-------|
| Underwriting time | 3–7 days | Same-day |
| Consistency | Variable | Deterministic |
| Regulatory issues | Frequent | Reduced |
| Denial appeals | High | Low |
| LO capacity | 15 apps/week | 50 apps/week |

**Per mid-size bank: $1.5M/year in LO productivity**

---

## Extendable Financial Products

```
Product Types:
  ✓ Personal loans
  ✓ Auto loans
  ✓ Mortgages
  ✓ Credit cards
  ✓ Business loans
  ✓ HELOCs
  ✓ Credit line increases
```

---

## Deployment Pattern

```
Loan Application (digital portal)
    │
    ├── Credit bureau pull
    ├── Bank statement analysis
    ├── Employment verification
    │
    ▼
AxiomAI Underwriting Engine
    │
    ├── Policy rule evaluation
    ├── Risk tier determination
    ├── Compliance check
    │
    ▼
Decision: Approve / Decline / Manual Review
    │
    ▼
Applicant + LO Dashboard
```

---

## Compliance Mapping

| Standard | Requirement | AxiomAI Checks |
|----------|-------------|----------------|
| ECOA | Consistent treatment | Rule-based decisions |
| FCRA | Credit reporting accuracy | Data verification |
| TILA | Disclosure requirements | Required notices |
| QM Rule | Ability to repay | DTI/rate checks |
| State usury laws | Rate limits | State-specific rules |
