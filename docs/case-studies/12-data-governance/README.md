# Case Study 12: Data Governance & Access Control

**Industry:** Healthcare, Finance, Government, Tech
**Vertical:** Data Security & Privacy Governance
**Revenue Potential:** $8B data governance market

---

## Problem

**Employees request access to sensitive data. Approvals are manual, inconsistent, and risky.**

Current process:
```
Access request submitted
    ↓
Manager approves (doesn't fully understand data)
    ↓
Security reviews (high volume — approves most)
    ↓
Access granted
    ↓
Audit: "Why does this person have PHI access?"
    ↓
"No idea"
```

**Risk:** Data breaches, HIPAA violations, GDPR fines, SOC2 failures
**Manual review:** 2–5 days per request
**Consistency:** Poor

---

## Solution: Deterministic Reasoning Engine

**Access control rules:**
```
Rule: PHI access requires
  IF data_classification = PHI
  AND user_role IN approved_healthcare_roles
  AND user_has_HIPAA_training = true
  AND purpose_of_access = treatment_payment_operations
  THEN grant_access

Rule: Financial data access
  IF data_classification = PCI
  AND user_department = finance_accounting
  AND user_has_background_check = true
  THEN grant_access

Rule: Customer PII access
  IF data_classification = PII
  AND user_role IN approved_customer_data_roles
  AND manager_approval = true
  THEN grant_access

Rule: Block access
  IF terminated_employee = true
  THEN immediately_revoke_all
```

---

## Engine Output

```
Access Request: #AR-2026-9942
User: Alex T. (Data Analyst)
Request: Salesforce customer database — full read

Data classification: PII + PCI

Decision: DENIED

Reason:
  1. User role (Data Analyst) not approved for full Salesforce access
  2. PCI data present — requires finance department role
  3. Manager approval: not obtained

Alternative:
  Role-based access to anonymized customer metrics
  available through approved reporting dashboard

Action:
  Request submitted for modified scope.

Audit trail:
  Requested: 2026-06-15
  Denied: 2026-06-15 (same day, automated)
  Alternative offered: 2026-06-15
```

---

## Business Value

| Metric | Before | After |
|--------|--------|-------|
| Access review time | 2–5 days | 5 minutes |
| Over-provisioning | 40% of accounts | <5% |
| Audit findings | High | Low |
| Data breach risk | High | Low |
| Compliance posture | Weak | Strong |

**Per enterprise: $500K–$2M/year in prevented incidents + audit costs**

---

## Extendable Access Rules

```
Data Types:
  ✓ PHI (HIPAA)
  ✓ PII (GDPR, CCPA)
  ✓ PCI (cardholder data)
  ✓ Financial records
  ✓ Intellectual property
  ✓ Customer data
  ✓ Employee records
  ✓ Government data
```

---

## Deployment Pattern

```
Access Request (ServiceNow, Jira, custom)
    │
    ├── User identity (Okta, Azure AD)
    ├── Role (HRIS, AD)
    ├── Data classification (Varonis, Spirion)
    │
    ▼
AxiomAI Access Governance Engine
    │
    ├── User eligibility check
    ├── Data classification check
    ├── Purpose verification
    │
    ▼
Approve / Deny / Modify / Escalate
    │
    ▼
Access Provisioning + Audit Log
```

---

## Compliance Mapping

| Standard | Requirement | AxiomAI Checks |
|----------|-------------|----------------|
| HIPAA §164.312 | Access control | Role-based PHI access |
| SOC2 CC6 | Logical access | Least privilege |
| GDPR Art. 6, 7 | Lawful basis | Purpose limitation |
| ISO 27001 A.9 | Access control | Role-based access |
| PCI DSS Req 7 | Restrict access | Need-to-know basis |
| NIST 800-53 | Access control | Attribute-based access |
