"""CS-08 Contract and SLA analysis."""

from __future__ import annotations

from apps.case_studies._base.simple_engine import CaseStudyResult, SimpleRuleEngine

RULES = [
    "IF UptimePercent(c, u) AND BelowSla999(u) AND EnterpriseTier(c) THEN SlaBreach_Penalty(c)",
    "IF EndDateWithinDays(c, d) AND Within90Days(d) AND AutoRenewal(c) THEN RenewalNoticeRequired(c)",
    "IF ActualUsage(c, a) AND MinimumCommitment(c, m) AND BelowCommitment(a, m) THEN TrueUpInvoice(c)",
]

DEFAULT_FACTS = [
    "UptimePercent(contract1, 99.2)",
    "BelowSla999(99.2)",
    "EnterpriseTier(contract1)",
    "EndDateWithinDays(contract1, 60)",
    "Within90Days(60)",
    "AutoRenewal(contract1)",
]


def run(entity: str = "contract1") -> CaseStudyResult:
    facts = [f.replace("contract1", entity) for f in DEFAULT_FACTS]
    result = SimpleRuleEngine().analyze(
        RULES,
        facts,
        entity=entity,
        goal_queries=[
            "SlaBreach_Penalty({entity})",
            "RenewalNoticeRequired({entity})",
            "TrueUpInvoice({entity})",
        ],
    )
    if result.outcome == "PROVED":
        result.outcome = "OBLIGATION_TRIGGERED"
    return result
