"""CS-16 Immigration filing assistant."""

from __future__ import annotations

from apps.case_studies._base.simple_engine import CaseStudyResult, SimpleRuleEngine

RULES = [
    "IF SpecialtyOccupation(p) AND DegreeRequired(p) AND PrevailingWageMet(p) AND BonaFideEmployer(p) THEN H1bEligible(p)",
    "IF H1bEligible(p) THEN FilingChecklistComplete(p)",
    "IF StatusViolation(p) THEN HighRiskAdjustment(p)",
    "IF FilingWindowOk(p) THEN ReadyToFile(p)",
    "IF HighRiskAdjustment(p) THEN FilingDenied(p)",
]

DEFAULT_FACTS = [
    "SpecialtyOccupation(petition1)",
    "DegreeRequired(petition1)",
    "PrevailingWageMet(petition1)",
    "BonaFideEmployer(petition1)",
    "FilingWindowOk(petition1)",
]


def run(entity: str = "petition1") -> CaseStudyResult:
    facts = [f.replace("petition1", entity) for f in DEFAULT_FACTS]
    return SimpleRuleEngine().analyze(
        RULES,
        facts,
        entity=entity,
        deny_queries=["FilingDenied({entity})"],
        allow_queries=["H1bEligible({entity})", "ReadyToFile({entity})"],
        escalate_queries=["HighRiskAdjustment({entity})"],
    )
