"""CS-11 HR policy and benefits eligibility."""

from __future__ import annotations

from apps.case_studies._base.simple_engine import CaseStudyResult, SimpleRuleEngine

RULES = [
    "IF FullTimeEmployee(e) AND TenureEligible(e) AND ApprovedLocation(e) AND NotOnPip(e) THEN ParentalLeaveEligible(e)",
    "IF Contractor(e) THEN BenefitsIneligible(e)",
    "IF RemoteRole(e) AND ApprovedState(e) AND RoleFit(e) AND ClearanceOk(e) THEN RemoteWorkApproved(e)",
    "IF Layoff(e) AND TenureEligible(e) AND RoleLevelAtLeastL3(e) THEN SeveranceEligible(e)",
]

DEFAULT_FACTS = [
    "FullTimeEmployee(emp1)",
    "TenureEligible(emp1)",
    "ApprovedLocation(emp1)",
    "NotOnPip(emp1)",
]


def run(entity: str = "emp1") -> CaseStudyResult:
    facts = [f.replace("emp1", entity) for f in DEFAULT_FACTS]
    return SimpleRuleEngine().analyze(
        RULES,
        facts,
        entity=entity,
        deny_queries=["BenefitsIneligible({entity})"],
        allow_queries=[
            "ParentalLeaveEligible({entity})",
            "RemoteWorkApproved({entity})",
            "SeveranceEligible({entity})",
        ],
    )
