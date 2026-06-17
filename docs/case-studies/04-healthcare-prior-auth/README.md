# Case Study 4: Healthcare Prior Authorization

**Industry:** Healthcare / Health Insurance
**Vertical:** Medical Decision Support (NOT diagnosis)
**Revenue Potential:** $15B US prior auth market

---

## Problem

**Insurance medical reviewers manually determine prior authorization approvals.**

Process:
```
Reviewer reads request
Checks symptoms
Checks test results
Checks guidelines
Checks history
Makes decision
```

**Time per review:** 20–45 minutes
**Cost per review:** $25–$75
**Inconsistency:** High — different reviewers reach different conclusions
**Appeal rate:** 15–20%

---

## Solution: Deterministic Reasoning Engine

**Guidelines encoded as rules:**
```
Rule: MRI approval requires ALL of:
  IF physical_therapy_completed
  AND pain_duration_weeks > 6
  AND xray_completed
  AND symptom_severity >= 6

Rule: MRI approval requires specialist referral
  IF secondOpinion_required = true

Rule: Emergency exception — auto-approve
  IF emergency_flag = true
```

---

## Engine Output — Denied

```
MRI Request: DENIED

Reason:
  1. ✓ Physical therapy: completed
  2. ✓ Pain duration: 8 weeks
  3. ✓ X-ray: completed
  4. ✗ Symptom severity: 5/10 — required >= 6

Missing criteria:
  Symptom severity documentation

Action:
  Request additional documentation from provider.
```

## Engine Output — Approved

```
MRI Request: APPROVED

Criteria satisfied:
  1. ✓ Physical therapy: completed
  2. ✓ Pain duration: 10 weeks
  3. ✓ X-ray: completed
  4. ✓ Symptom severity: 7/10

Evidence on file:
  PT notes, imaging report, specialist referral
```

---

## Business Value

| Metric | Before | After |
|--------|--------|-------|
| Review time | 20–45 min | 20 sec |
| Consistency | Variable | Deterministic |
| Appeal rate | 15–20% | <5% |
| Annual review cost | $2M | $200K |
| Provider satisfaction | Low | High |

**Per health plan (1M members): $1.5M/year savings**

---

## Key Positioning

**NOT:** "AI diagnoses patients"
**IS:** "AI checks if guideline criteria are met"

This keeps it strictly as a decision-support tool, avoiding FDA/clinical validation requirements.

---

## Compliance Mapping

| Standard | Requirement | AxiomAI Checks |
|----------|-------------|----------------|
| CMS Prior Auth Rules | Medical necessity | Guideline criteria |
| URAC | Consistent review | Deterministic rules |
| State MLR | Administrative efficiency | Automated review |
| HIPAA | Minimum necessary | Appropriate use review |
