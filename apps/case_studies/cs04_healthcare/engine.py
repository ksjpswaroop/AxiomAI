"""CS-04 Healthcare prior authorization."""

from __future__ import annotations

from apps.case_studies._base.simple_engine import CaseStudyResult, SimpleRuleEngine

RULES = [
    "IF PhysicalTherapyDone(p) AND PainOver6Weeks(p) AND XrayCompleted(p) AND SeverityHigh(p) THEN PriorAuthApproved(p)",
    "IF EmergencyFlag(p) THEN PriorAuthApproved(p)",
    "IF SpecialistRequired(p) AND NotSecondOpinion(p) THEN PriorAuthDenied(p)",
    "IF NotPhysicalTherapyDone(p) THEN PriorAuthDenied(p)",
]

DEFAULT_FACTS = [
    "PhysicalTherapyDone(patient1)",
    "PainOver6Weeks(patient1)",
    "XrayCompleted(patient1)",
    "SeverityHigh(patient1)",
]


def run(entity: str = "patient1") -> CaseStudyResult:
    facts = [f.replace("patient1", entity) for f in DEFAULT_FACTS]
    return SimpleRuleEngine().analyze(
        RULES,
        facts,
        entity=entity,
        deny_queries=["PriorAuthDenied({entity})"],
        allow_queries=["PriorAuthApproved({entity})"],
    )
