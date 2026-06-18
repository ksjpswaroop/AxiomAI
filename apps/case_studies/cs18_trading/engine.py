"""CS-18 Agentic trading guardrail."""

from __future__ import annotations

from apps.case_studies._base.simple_engine import CaseStudyResult, SimpleRuleEngine

RULES = [
    "IF DailyPnl(port, p) AND BelowNeg2Pct(p) THEN HaltTrading(port)",
    "IF PositionSize(port, s) AND Over10PctPortfolio(s) THEN RejectOrder(port)",
    "IF SectorExposure(port, sec, e) AND Over25Pct(e) AND AddingPosition(port) THEN ApprovalRequired(port)",
    "IF Volatility(port, v) AND Over2xNormal(v) THEN ReducePositionSize(port)",
    "IF HaltTrading(port) THEN TradeBlocked(port)",
    "IF RejectOrder(port) THEN TradeBlocked(port)",
]

DEFAULT_FACTS = [
    "PositionSize(port1, 12)",
    "Over10PctPortfolio(12)",
    "SectorExposure(port1, tech, 30)",
    "Over25Pct(30)",
    "AddingPosition(port1)",
]


def run(entity: str = "port1") -> CaseStudyResult:
    facts = [f.replace("port1", entity) for f in DEFAULT_FACTS]
    result = SimpleRuleEngine().analyze(
        RULES,
        facts,
        entity=entity,
        deny_queries=["TradeBlocked({entity})", "HaltTrading({entity})"],
        escalate_queries=["ApprovalRequired({entity})", "ReducePositionSize({entity})"],
    )
    if result.outcome in ("DENY", "ESCALATE"):
        result.outcome = "BLOCKED"
    return result
