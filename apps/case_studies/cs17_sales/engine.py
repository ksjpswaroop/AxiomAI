"""CS-17 Sales qualification and lead routing."""

from __future__ import annotations

from apps.case_studies._base.simple_engine import CaseStudyResult, SimpleRuleEngine

RULES = [
    "IF CompanySize(l, s) AND Over100Seats(s) AND SecurityTeam(l) AND ComplianceNeed(l) AND BudgetConfirmed(l) THEN Route_SeniorAe(l)",
    "IF CompanySize(l, s) AND Under10Seats(s) AND RevenueUnder1M(l) THEN Route_Nurture(l)",
    "IF CompanySize(l, s) AND Over1000Seats(s) AND ComplianceNeed(l) AND ItDecisionMaker(l) THEN Route_Enterprise(l)",
    "IF OnDncList(l) THEN Route_Dnc(l)",
]

DEFAULT_FACTS = [
    "CompanySize(lead1, 250)",
    "Over100Seats(250)",
    "SecurityTeam(lead1)",
    "ComplianceNeed(lead1)",
    "BudgetConfirmed(lead1)",
]


def run(entity: str = "lead1") -> CaseStudyResult:
    facts = [f.replace("lead1", entity) for f in DEFAULT_FACTS]
    result = SimpleRuleEngine().analyze(
        RULES,
        facts,
        entity=entity,
        goal_queries=[
            "Route_SeniorAe({entity})",
            "Route_Enterprise({entity})",
            "Route_Nurture({entity})",
            "Route_Dnc({entity})",
        ],
    )
    if result.outcome == "PROVED":
        result.outcome = "ROUTED"
    return result
