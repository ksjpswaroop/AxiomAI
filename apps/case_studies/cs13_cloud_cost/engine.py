"""CS-13 Cloud cost governance."""

from __future__ import annotations

from apps.case_studies._base.simple_engine import CaseStudyResult, SimpleRuleEngine

RULES = [
    "IF GpuInstance(x) AND MonthlyCost(x, c) AND OverCost5000(c) THEN RequiresFinanceApproval(x)",
    "IF HighMemInstance(x) AND MonthlyCost(x, c) AND OverCost2000(c) THEN RequiresTeamLeadApproval(x)",
    "IF NewRegion(x) THEN RequiresSecurityReview(x)",
    "IF StorageTb(x, t) AND OverStorage10Tb(t) THEN RequiresStorageApproval(x)",
    "IF MonthlyEgressCost(x, c) AND OverEgress1000(c) THEN AlertFinance(x)",
    "IF RequiresFinanceApproval(x) AND LongCommitment(x) THEN ResourceBlocked(x)",
    "IF RequiresSecurityReview(x) THEN ResourceBlocked(x)",
]

DEFAULT_FACTS = [
    "GpuInstance(req_gpu)",
    "MonthlyCost(req_gpu, 45000)",
    "OverCost5000(45000)",
    "LongCommitment(req_gpu)",
    "NewRegion(req_gpu)",
]


def run(entity: str = "req_gpu") -> CaseStudyResult:
    facts = [f.replace("req_gpu", entity) for f in DEFAULT_FACTS]
    result = SimpleRuleEngine().analyze(
        RULES,
        facts,
        entity=entity,
        deny_queries=["ResourceBlocked({entity})"],
        escalate_queries=["RequiresFinanceApproval({entity})", "AlertFinance({entity})"],
    )
    if result.outcome in ("DENY", "ESCALATE"):
        result.outcome = "BLOCKED"
        result.explanation = "GPU cluster blocked — exceeds $5K/month and requires finance review."
    return result
