# Case Study 18: Agentic Trading Guardrail

**Industry:** Financial Services / Trading
**Vertical:** Algorithmic Trading Governance
**Revenue Potential:** $50B algo trading market

---

## Problem

**AI trading agents may overtrade, exceed position limits, or violate risk parameters.**

Current process:
```
Algo trading system
    ↓
AI identifies opportunity
    ↓
Executes trades
    ↓
Position limit exceeded
    ↓
Risk officer discovers at end of day
    ↓
Regulatory inquiry
    ↓
Fine
```

**Regulatory fines:** $100K–$10M per violation
**Financial losses:** Positions can move against the firm in minutes
**No explainability:** "Why did the algo do that?" → Black box

---

## Solution: Deterministic Risk Guardrail

**Trading rules encoded:**
```
Rule: Daily loss limit
  IF daily_pnl < -2% of portfolio
  THEN block_all_new_trades
  AND alert_risk_manager

Rule: Position size limit
  IF proposed_position_size > 10% of portfolio
  THEN reject_order
  AND log_rejection

Rule: Concentration limit
  IF sector_concentration > 25%
  AND proposed_trade_adds_to_sector = true
  THEN require_explicit_approval

Rule: Volatility trigger
  IF market_volatility > 2x_normal
  THEN reduce_position_sizes_by_50%
  AND increase_margin_requirements

Rule: Counterparty limit
  IF counterparty_exposure > 5% of book
  THEN block_new_trades_with_counterparty

Rule: Restricted securities
  IF symbol IN blackout_list
  THEN block_all_orders
```

---

## Engine Output

```
Order Rejected: BUY AAPL 50,000 shares

Trader: Algo-001 (ML-based momentum strategy)
Order: Buy AAPL @ $185 — $9.25M position
Portfolio: $150M

Rejection reason: POSITION SIZE VIOLATION

Policy: Single position <= 10% of portfolio
Proposed position: 6.17% of portfolio

After execution:
  AAPL position: 6.17% (within limit) — PASS
  BUT: Sector (Tech) concentration: 24% → 29%
  Sector limit: 25%

Decision: BLOCKED

Reason:
  Adding $9.25M AAPL position would exceed
  Technology sector concentration limit (25%)
  Proposed: 29%

Alternative:
  Reduce to 20,000 shares = $3.7M
  Resulting sector: 26% — Marginal, monitor

Risk Manager alerted:
  Algo-001 rejected 3 similar orders today
  Pattern: Momentum strategy chasing Tech rally
  Recommend: Review strategy allocation

Audit trail:
  Timestamp: 2026-06-17 09:42:11
  Rule triggered: sector_concentration_limit
  Decision: Blocked
```

---

## Business Value

| Metric | Before | After |
|--------|--------|-------|
| Position limit violations | Occasional | Zero |
| Daily loss exceedances | 2–3/month | Zero |
| Regulatory findings | High | Minimal |
| Risk manager overhead | Full-time monitoring | Exception handling only |
| Trading confidence | Low | High |

**Per trading desk: $500K–$5M/year in prevented violations + fines**

---

## Extendable Trading Rules

```
Risk Controls:
  ✓ Position size limits
  ✓ Sector concentration
  ✓ Daily/weekly/monthly P&L limits
  ✓ Volatility-triggered position reduction
  ✓ Counterparty credit limits
  ✓ Margin/leverage limits
  ✓ Blackout period rules
  ✓ News/event trading restrictions
  ✓ Cross-border position rules
```

---

## Deployment Pattern

```
Trading Algorithm
    │
    ├── Order generation
    │
    ▼
AxiomAI Trading Guardrail
    │
    ├── Position check
    ├── P&L check
    ├── Concentration check
    ├── Volatility adjustment
    │
    ▼
ALLOW — if all checks pass
MODIFY — if modification suggested
BLOCK — if any rule violated
    │
    ▼
Execution Broker + Audit Log + Risk Dashboard
```

---

## Compliance Mapping

| Standard | Requirement | AxiomAI Checks |
|----------|-------------|----------------|
| SEC Rule 15c3-5 | Market access rules | Pre-trade risk checks |
| MiFID II | Best execution | Order size/risk limits |
| EMIR | Derivative reporting | Counterparty limits |
| Dodd-Frank | Swaps regulation | Position limits |
| Internal risk policies | Firm-specific rules | Custom rule enforcement |
