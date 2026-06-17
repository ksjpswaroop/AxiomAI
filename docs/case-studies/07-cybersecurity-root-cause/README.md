# Case Study 7: Cybersecurity Root Cause Analysis

**Industry:** Cybersecurity / SOC / MSSP
**Vertical:** Security Operations & Incident Response
**Revenue Potential:** Primary vertical — fastest to close

---

## Problem

**Security incidents require senior analysts to manually correlate alerts across multiple tools.**

Current process:
```
SIEM Alert (possible intrusion)
    ↓
L1 analyst investigates (30 min)
    ↓
Escalate to L2 (if suspicious)
    ↓
L2 correlation (1–2 hours)
    ↓
Escalate to L3 / Incident Responder
    ↓
Final root cause (4–6 hours)
```

**Cost per major incident:** $10,000–$100,000
**Senior analyst hourly rate:** $150–$300/hr
**Alert fatigue:** Analysts receive 1,000+ alerts/day

---

## Solution: Deterministic Reasoning Engine

**Facts ingested from security stack:**
```
User001 clicked email attachment     = TRUE
PowerShell launched by User001      = TRUE
Encoded PowerShell command detected  = TRUE
Outbound traffic spike from Host42  = TRUE
Lateral movement detected           = TRUE
Admin account used on non-admin host = TRUE
```

**Attack chain rules:**
```
Rule: Phishing → Execution chain
  IF email_click
  AND powershell_launched
  AND encoded_command
  THEN probable_initial_access

Rule: Execution → Persistence
  IF powershell_execution
  AND scheduled_task_created
  THEN probable_persistence

Rule: C2 indicators
  IF encoded_command
  AND c2_traffic
  AND beacon_pattern_detected
  THEN probable_c2_communication

Rule: Lateral movement
  IF admin_credential_use
  AND unusual_host_access
  THEN probable_lateral_movement

Rule: Ransomware
  IF phishing
  AND powershell_execution
  AND c2_traffic
  AND file_encryption_started
  THEN confirmed_ransomware
```

---

## Engine Output

```
INCIDENT: Possible ransomware — Host42

Attack Chain (reconstructed):
  1. [INITIAL ACCESS] Phishing email clicked
     Evidence: User001 opened attachment
     Time: 2026-06-17 09:14:22

  2. [EXECUTION] PowerShell launched
     Evidence: encoded command detected
     Time: 2026-06-17 09:14:35

  3. [C2] Command and control
     Evidence: beacon to 45.33.x.x every 30s
     Time: 2026-06-17 09:15:00

  4. [LATERAL] Admin credentials used
     Evidence: Admin001 on Workstation18
     Time: 2026-06-17 09:16:00

  5. [IMPACT] File encryption started
     Evidence: 3,421 files modified
     Time: 2026-06-17 09:17:00

ROOT CAUSE: Phishing → Ransomware

Confidence: CONFIRMED (all chain steps verified)

Containment recommendation:
  1. Isolate Host42 immediately
  2. Revoke Admin001 credentials
  3. Block 45.33.x.x at perimeter
  4. Scan all endpoints for Emotet indicators
```

---

## Business Value

| Metric | Before | After |
|--------|--------|-------|
| Investigation time | 4–8 hours | 10–15 minutes |
| Junior analyst effectiveness | Low | High |
| Incident containment | Slow | Fast |
| MTTR | 6 hours | 45 minutes |
| L3 escalation | 100% | 20% |

**Per SOC (24/7 monitoring): $800K–$2M/year in analyst time savings**

**Additional value:** Faster containment = smaller breach = $100K–$10M in breach costs avoided

---

## Extendable Detection Patterns

```
RULE SETS:

Ransomware Detection:
  Email click → PowerShell → C2 → Encryption

Insider Threat:
  Unusual data access → Large download → Exfiltration

Supply Chain:
  Third-party VPN → Privileged escalation → DC compromise

Credential Attack:
  Brute force → Privilege escalation → Persistence
```

---

## Deployment Pattern

```
Security Stack
    │
    ├── SIEM (Splunk, Elastic, Sentinel)
    ├── EDR (CrowdStrike, SentinelOne)
    ├── Email (Proofpoint, Mimecast)
    ├── Identity (Azure AD, Okta)
    ├── Firewall / NetFlow
    └── Certificate logs
    │
    ▼
AxiomAI Security Engine
    │
    ├── Parse events → Facts
    ├── Match rules → Attack chains
    ├── Calculate confidence
    │
    ▼
Alert + Root Cause + Containment
    │
    ▼
SOC Dashboard / SOAR Integration
```

---

## Compliance Mapping

| Standard | Requirement | AxiomAI Checks |
|----------|-------------|----------------|
| NIST 800-61 | Incident handling | Root cause analysis |
| SOC2 CC7 | Security incidents | Attack chain detection |
| ISO 27001 A.16 | Incident management | Evidence correlation |
| PCI DSS | Breach response | Attack reconstruction |
| HIPAA | Security incidents | PHI exposure detection |
