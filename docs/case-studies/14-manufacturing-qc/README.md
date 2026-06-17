# Case Study 14: Manufacturing Quality Control

**Industry:** Manufacturing / Industrial
**Vertical:** Quality Management & Root Cause
**Revenue Potential:** $10B industrial AI market

---

## Problem

**Defect diagnosis depends on senior plant engineers with decades of experience.**

Current process:
```
Defect detected on production line
    ↓
Line supervisor calls senior engineer
    ↓
Senior engineer travels to plant (or remote)
    ↓
Analyzes: temp logs, vibration data, material specs
    ↓
Guesses root cause based on experience
    ↓
Replaces components
    ↓
Sometimes fixes problem
    ↓
Sometimes doesn't — repeat
```

**Cost of downtime:** $10K–$100K/hour
**Senior engineer scarcity:** Critical skills gap
**Root cause accuracy:** ~60% on first attempt

---

## Solution: Deterministic Reasoning Engine

**Manufacturing rules encoded:**
```
Rule: Vibration = Misalignment
  IF vibration_abnormal = true
  AND alignment_deviation > 0.1mm
  AND maintenance_overdue = true
  THEN likely_root_cause = shaft_misalignment

Rule: Temperature = Bearing failure
  IF temperature_high = true
  AND bearing_wear > threshold
  THEN likely_root_cause = bearing_failure

Rule: Surface defect = Material issue
  IF surface_defect_rate > 2%
  AND incoming_material_lot != current_lot
  AND defect_pattern = consistent
  THEN likely_root_cause = material_batch

Rule: Scrap spike
  IF scrap_rate > 5%
  AND machine_calibration_overdue = true
  THEN recommend_recalibration
```

---

## Engine Output

```
Quality Alert: Assembly Line 3
Time: 2026-06-17 06:42:15

Symptoms:
  • Defect rate: 8.7% (baseline: 1.2%)
  • Vibration: abnormal (+340% deviation)
  • Temperature: +15°F above baseline
  • Calibration: overdue (scheduled 6/15)

Likely Root Cause:
  SHAFT MISALIGNMENT — 94% confidence

Evidence:
  1. Vibration abnormal: detected 06:30
  2. Alignment deviation: 0.23mm (threshold: 0.1mm)
  3. Last alignment check: 3 months ago
  4. Bearing wear: 68% (normal: <40%)

Recommended Actions:
  1. STOP LINE — imminent failure risk
  2. Check shaft alignment
  3. Inspect bearings
  4. Recalibrate after repair

Estimated downtime if caught now: 2 hours
Estimated downtime if missed: 18 hours + emergency repair
```

---

## Business Value

| Metric | Before | After |
|--------|--------|-------|
| Root cause accuracy | ~60% | 90%+ |
| MTTR | 18 hours | 2 hours |
| Unplanned downtime | 40 hrs/month | 5 hrs/month |
| Scrap rate | 3–5% | <1% |
| Senior engineer travel | Frequent | Reduced |

**Per plant: $500K–$3M/year in prevented downtime + scrap**

---

## Extendable QC Rules

```
Defect Patterns:
  ✓ Dimensional drift
  ✓ Surface finish issues
  ✓ Material properties
  ✓ Weld quality
  ✓ Coating adhesion
  ✓ Assembly errors
```

---

## Deployment Pattern

```
Sensors (IoT)
    │
    ├── Temperature sensors
    ├── Vibration sensors
    ├── Vision systems
    ├── PLC data
    │
    ▼
SCADA / MES / Historian
    │
    ▼
AxiomAI QC Engine
    │
    ├── Fact extraction
    ├── Rule matching
    ├── Root cause analysis
    │
    ▼
Plant Dashboard + Maintenance Queue
```

---

## Compliance Mapping

| Standard | Requirement | AxiomAI Checks |
|----------|-------------|----------------|
| ISO 9001 | Quality management | Root cause tracking |
| IATF 16949 | Automotive quality | Process control rules |
| FDA 21 CFR | Medical devices | Inspection rules |
| cGMP | Manufacturing quality | Calibration checks |
