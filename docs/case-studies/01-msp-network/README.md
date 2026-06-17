# Case Study 1: MSP / Network Operations

**Industry:** Managed Services (MSP)
**Vertical:** Network Operations & Troubleshooting
**Revenue Potential:** $720K/year per 100-seat MSP

---

## Problem

A client reports: VPN users cannot connect.

**Current process:**
```
Level 1 → Escalate → Level 2 → Level 3 → Root Cause
```

**Typical resolution:** 2–6 hours
**Senior engineer cost:** $100–$200/hr

---

## Solution: Deterministic Reasoning Engine

**Knowledge base contains:**
- VPN rules and policies
- Firewall configurations
- Certificate status and expiration
- Identity provider configs
- Past incident history
- Network topology

**Extracted facts:**
```
VPN service running = true
Auth failures increased = true
Certificate expired = June 16
```

**Rules:**
```
IF auth_failure
AND certificate_expired
THEN root_cause = certificate
```

---

## Engine Output

```
Root Cause: VPN certificate expired.

Evidence:
  • Certificate expiration date: June 16
  • Authentication failures: started June 17
  • VPN service: running normally

Confidence: LOGICALLY PROVEN
```

---

## Business Value

| Metric | Before | After |
|--------|--------|-------|
| MTTR | 4 hours | 15 minutes |
| Escalations | High | Low |
| L3 engineer usage | 100% | 30% |
| Customer satisfaction | Medium | High |

**Annual Impact (100 incidents/month):**
- 400 engineer hours saved/month
- At $150/hr: **$720,000/year**

---

## Differentiation from Pure LLM

A pure LLM approach: "Try restarting the VPN service." → costs hours
AxiomAI reasoning: exact root cause in 15 minutes → costs near zero

---

## Compliance Mapping

| Standard | Control | AxiomAI Checks |
|----------|---------|----------------|
| SOC2 CC7.2 | Monitoring | Certificate expiration alerts |
| ISO 27001 A.10 | Non-repudiation | Audit trail of failures |
| NIST SP 800-53 | Incident response | Automated root cause |

---

## Deployment Pattern

```
AxiomAI Reasoning Engine
    │
    ├── Ticket System (Autotask, ConnectWise)
    ├── Monitoring (Datadog, PRTG)
    ├── Identity Provider (Okta, Azure AD)
    └── Certificate Monitor (Duo, Venafi)
    │
    ▼
L1 Analyst receives → "Certificate expired" → Fix in 15 min
```
