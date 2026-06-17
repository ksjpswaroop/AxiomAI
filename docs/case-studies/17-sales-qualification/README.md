# Case Study 17: Sales Qualification Engine

**Industry:** B2B SaaS / Sales
**Vertical:** SDR / Sales Automation
**Revenue Potential:** $20B sales tech market

---

## Problem

**Sales teams inconsistently qualify leads. AEs waste time on unqualified prospects.**

Current process:
```
Lead comes in from marketing
    ↓
SDR calls: "Do you have budget?"
    ↓
Lead: "Sure"
    ↓
SDR: "Great, I'll book a demo"
    ↓
AE spends 2 hours on demo
    ↓
Lead: "We were just exploring"
    ↓
No deal — wasted time
```

**Demo-to-close rate for unqualified leads:** <5%
**AE hourly cost:** $75–$150
**Time wasted on bad leads:** 30–40% of AE capacity

---

## Solution: Deterministic Reasoning Engine

**Qualification rules encoded:**
```
Rule: High-priority lead
  IF company_size > 100 employees
  AND has_security_team = true
  AND compliance_requirement IN [SOC2, HIPAA, PCI]
  AND budget_identified = true
  THEN priority = high
  AND route_to = senior_AE

Rule: Do not call (DNC)
  IF company_size < 10
  AND annual_revenue < 1M
  THEN priority = low
  AND route_to = nurture_sequence

Rule: Enterprise qualification
  IF company_size > 1000
  AND compliance_requirement = true
  AND IT_decision_maker_identified = true
  THEN enterprise = true
  AND required_meetings = 3+

Rule: Competitor customer
  IF currently_using = competitor_product
  AND satisfaction = low
  AND switching_cost = low
  THEN high_intent = true
```

---

## Engine Output

```
Lead: TechCorp Inc.
Source: LinkedIn ad — SOC2 compliance
Contact: VP Engineering
Company size: 450 employees
Industry: Healthcare SaaS

Priority: HIGH

Qualification score: 87/100

Firmographics:
  ✓ Company size: 450 (threshold: 100+) — PASS
  ✓ Industry: Healthcare — compliance-driven buyer
  ✓ Growth: 40% YoY — budget likely available
  ✓ Stage: Series B — active expansion

Trigger signals:
  ✓ Compliance requirement: SOC2 Type II (internal deadline Q3)
  ✓ IT team: 12-person team (decision-maker: VP Eng)
  ✓ Competitor used: Jira (low satisfaction score 2.1/5)
  ✓ Intent signals: Downloaded security whitepaper

Recommendation:
  1. Route to: Sarah Chen (Enterprise AE)
  2. Script: Compliance pain angle
  3. Demo: Security + compliance features
  4. Timing: Q3 budget cycle — NOW
  5. Competitor angle: "Jira security gaps"

Confidence: 87% likely to convert
```

---

## Business Value

| Metric | Before | After |
|--------|--------|-------|
| Qualified lead accuracy | ~35% | 80%+ |
| AE time on unqualified leads | 30–40% | <10% |
| Demo-to-close rate | <5% | 15–20% |
| Sales cycle | 90 days | 60 days |
| AE capacity | 15 deals/quarter | 30 deals/quarter |

**Per 20-AE team: $1.5M/year in recovered capacity**

---

## Extendable Qualification Rules

```
Lead Scoring Dimensions:
  ✓ Firmographic (size, industry, growth)
  ✓ Technographic (tech stack)
  ✓ Intent signals (content engagement)
  ✓ Behavioral (webinar attendance, demo requests)
  ✓ Competitive (competitor usage)
  ✓ Budget (stated vs. inferred)
  ✓ Timeline (decision-making window)
```

---

## Deployment Pattern

```
Marketing Automation (Marketo, HubSpot)
    │
    ├── Website analytics
    ├── Content engagement
    ├── Form submissions
    │
    ▼
AxiomAI Sales Qualification Engine
    │
    ├── Lead scoring
    ├── Routing rules
    ├── Talk track recommendations
    │
    ▼
CRM Update (Salesforce, HubSpot)
    │
    ▼
SDR / AE Assignment + Alerts
```

---

## Compliance Mapping

| Standard | Requirement | AxiomAI Checks |
|----------|-------------|----------------|
| GDPR | Consent management | Opt-in verification |
| CAN-SPAM | Email compliance | Unsubscribe handling |
| SOC2 | Vendor management | Data handling rules |
| CCPA | Consumer rights | Prospect data handling |
