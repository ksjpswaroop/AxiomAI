"""CS-06 Procurement agent governance."""

from __future__ import annotations

from apps.case_studies._base.simple_engine import CaseStudyResult, SimpleRuleEngine

RULES = [
    "IF PurchaseAmount(x, a) AND OverThreshold1000(a) THEN RequiresManagerApproval(x)",
    "IF PurchaseAmount(x, a) AND OverThreshold10000(a) THEN RequiresFinanceApproval(x)",
    "IF NewVendor(x, v) THEN RequiresSecurityReview(x)",
    "IF ContractTermMonths(x, m) AND Over12Months(m) THEN RequiresLegalReview(x)",
    "IF GpuResource(x) THEN RequiresCostAnalysis(x)",
    "IF RequiresSecurityReview(x) THEN PurchaseBlocked(x)",
    "IF RequiresFinanceApproval(x) AND RequiresLegalReview(x) THEN PurchaseBlocked(x)",
]

DEFAULT_FACTS = [
    "PurchaseAmount(req1, 45000)",
    "OverThreshold1000(45000)",
    "OverThreshold10000(45000)",
    "NewVendor(req1, NewCloudProvider)",
    "ContractTermMonths(req1, 24)",
    "Over12Months(24)",
    "GpuResource(req1)",
]


def run(entity: str = "req1") -> CaseStudyResult:
    facts = [f.replace("req1", entity) for f in DEFAULT_FACTS]
    result = SimpleRuleEngine().analyze(
        RULES,
        facts,
        entity=entity,
        deny_queries=["PurchaseBlocked({entity})"],
        escalate_queries=[
            "RequiresFinanceApproval({entity})",
            "RequiresLegalReview({entity})",
            "RequiresSecurityReview({entity})",
        ],
    )
    if result.outcome in ("DENY", "ESCALATE"):
        result.outcome = "BLOCKED"
        result.explanation = "Purchase blocked — vendor, finance, and legal review required."
    return result
