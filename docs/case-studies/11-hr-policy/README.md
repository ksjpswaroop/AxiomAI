# Case Study 11: HR Policy & Employee Benefits

**Industry:** All enterprises
**Vertical:** HR Service Delivery
**Revenue Potential:** $15B HR tech market

---

## Problem

**HR teams repeatedly answer eligibility questions manually.**

Common questions:
- Is this employee eligible for parental leave?
- Can this contractor receive this benefit?
- Can this employee transfer internally?
- Does this termination trigger severance?
- Can this employee work remotely from this state?

**Time spent:** 5–20 min per question
**HR tickets:** 30–50% of total volume
**Consistency:** Poor — different HR reps give different answers

---

## Solution: Deterministic Reasoning Engine

**Policy rules encoded:**
```
Rule: Parental leave eligibility
  IF employee_type = full_time
  AND tenure_months >= 12
  AND location IN [US, CA, UK, DE]
  AND not_on_PIP = true
  THEN parental_leave_eligible

Rule: Contractor benefits exclusion
  IF employee_type = contractor
  THEN benefit_eligibility = false

Rule: Remote work eligibility
  IF location = approved_state = true
  AND role_eligible_for_remote = true
  AND data_classification <= role_clearance
  THEN remote_work_allowed

Rule: Severance eligibility
  IF termination_type = layoff
  AND tenure_years >= 1
  AND role_tier >= L3
  THEN severance_eligible
```

---

## Engine Output

```
Request: Parental leave for Sarah M.

Employee ID: EMP-4821
Type: Full-time
Tenure: 14 months
Location: Texas
Current status: Not on PIP

Decision: ELIGIBLE

Leave entitlement:
  • Weeks: 12 paid
  • Start date: Upon request + 30-day notice
  • Manager approval: Required

Actions:
  1. Submit leave request in Workday
  2. Manager approval within 5 business days
  3. HR acknowledgment sent

---
Request: Remote work from Colorado

Employee: John K.
Role: Software Engineer L4
Data access: Confidential
Colorado approved states: Yes

Decision: ELIGIBLE

Note:
  Colorado equal pay law requirements confirmed.
  IT equipment request will be generated.
```

---

## Business Value

| Metric | Before | After |
|--------|--------|-------|
| HR ticket volume | High | 30–50% reduction |
| Time per eligibility question | 10–20 min | 30 sec |
| Consistency | Variable | 100% |
| Employee satisfaction | Medium | High |
| Policy violations | Occasional | Near zero |

**Per 1,000-employee company: $150K/year in HR time savings**

---

## Extendable HR Rules

```
Policy Types:
  ✓ Leave management (PTO, sick, parental)
  ✓ Benefits eligibility
  ✓ Remote work policies
  ✓ Internal transfers
  ✓ Promotions (tenure/performance requirements)
  ✓ Termination/severance
  ✓ Equipment requests
  ✓ Access provisioning
  ✓ Offboarding checklists
```

---

## Deployment Pattern

```
Employee / Manager Request
    │
    ├── HRIS integration (Workday, BambooHR)
    ├── Payroll data
    ├── Location database
    │
    ▼
AxiomAI HR Policy Engine
    │
    ├── Employee fact lookup
    ├── Policy rule evaluation
    │
    ▼
Decision: Approved / Denied / Escalate
    │
    ▼
HR Service Ticket System
```

---

## Compliance Mapping

| Standard | Requirement | AxiomAI Checks |
|----------|-------------|----------------|
| FMLA | Leave eligibility | tenure, type, hours |
| State labor laws | Location-specific rules | state-by-state rules |
| ADA | Accommodations | role suitability |
| EEO | Non-discrimination | consistent criteria |
| SOX | Financial controls | executive approval |
