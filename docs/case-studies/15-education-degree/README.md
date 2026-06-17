# Case Study 15: Education Degree Audit

**Industry:** Higher Education
**Vertical:** Academic Advising & Student Success
**Revenue Potential:** $5B EdTech market

---

## Problem

**Students and academic advisors manually check degree requirements.**

Current process:
```
Student meets with advisor (30 min)
    ↓
Advisor pulls degree requirements (PDF — 40 pages)
    ↓
Advisor checks: completed courses vs. requirements
    ↓
Checks: prerequisites
Checks: minimum grades
Checks: transfer credits
Checks: residency requirements
    ↓
Advisor makes recommendation
    ↓
Student: "So I'm on track to graduate?"
    ↓
Advisor: "I think so?"
```

**Time per audit:** 30–60 minutes
**Inconsistency:** Different advisors give different advice
**Student frustration:** High — don't know graduation timeline

---

## Solution: Deterministic Reasoning Engine

**Degree requirements encoded:**
```
Rule: Lab science requirement
  IF degree = BS
  AND department = Engineering
  THEN requires_lab_science = 2 courses

Rule: Upper division minimum
  IF degree = BA
  AND major = Economics
  THEN upper_division_credits >= 33

Rule: Prerequisites
  IF course = Calculus_II
  AND student NOT completed Calculus_I
  THEN cannot_enroll

Rule: Graduation eligibility
  IF total_credits >= 120
  AND major_credits >= 40
  AND gen_ed_complete = true
  AND upper_division >= 30
  AND gpa >= 2.0
  THEN eligible_to_graduated
```

---

## Engine Output

```
Degree Audit: Sarah M.
Major: BS Computer Science
Year: Junior
Credits completed: 92 / 120 required

Status: NOT READY TO GRADUATE

Missing Requirements:

GEN ED:
  ✓ English Composition (6 credits)
  ✓ Math through Calculus III
  ✓ Lab science (1 of 2 required)
  ✗ Lab science — incomplete
  ✓ Social science (6 credits)
  ✓ Fine arts (3 credits)

MAJOR:
  ✓ CS Core (all complete)
  ✓ Upper division CS (18 of 18)
  ✓ Technical electives (12 of 12)
  ✗ Capstone project (not enrolled)

ELECTIVES:
  ✓ General electives (21 of 21)

ON TRACK?
  Semester credits needed: 28
  Semesters remaining: 4
  Feasible: YES — if enrolled in lab science + capstone

Graduation timeline: May 2028 (2 years)
```

---

## Business Value

| Metric | Before | After |
|--------|--------|-------|
| Audit time | 30–60 min | 30 sec |
| Advisor capacity | 20 students/day | 100 students/day |
| Consistent advice | No | Yes |
| Student satisfaction | Medium | High |
| Summer melt (enrolled → didn't return) | 12% | <5% |

**Per university: $500K–$1M/year in advisor productivity + retention**

---

## Extendable Academic Rules

```
Academic Rules:
  ✓ Degree requirements (all majors)
  ✓ Prerequisite chains
  ✓ Course sequencing
  ✓ Placement test rules
  ✓ Financial aid eligibility
  ✓ Scholarship requirements
  ✓ Transfer credit evaluation
  ✓ Academic standing (probation, suspension)
```

---

## Deployment Pattern

```
Student Portal / SIS (Banner, PeopleSoft)
    │
    ├── Transcript
    ├── Degree requirements
    ├── Course catalog
    │
    ▼
AxiomAI Academic Engine
    │
    ├── Requirement matching
    ├── Gap analysis
    ├── Timeline projection
    │
    ▼
Student Dashboard + Advisor Dashboard
```

---

## Compliance Mapping

| Standard | Requirement | AxiomAI Checks |
|----------|-------------|----------------|
| Title IV | Financial aid rules | Eligibility verification |
| NCAA | Progress toward degree | Athlete eligibility |
| State residency | Tuition classification | Residency rules |
| ADA | Accommodations | Course accessibility |
