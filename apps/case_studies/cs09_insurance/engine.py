"""CS-09 Insurance claims validation."""

from __future__ import annotations

from apps.case_studies._base.simple_engine import CaseStudyResult, SimpleRuleEngine

RULES = [
    "IF IncidentType(c, water_damage) AND BuildingInsured(c) THEN CoverageApplies(c)",
    "IF RoofAgeYears(c, y) AND Over20Years(y) AND NeglectReported(c) THEN ClaimDenied_Exclusion(c)",
    "IF PoliceReportSubmitted(c) AND EstimateSubmitted(c) THEN DocsComplete(c)",
    "IF CoverageApplies(c) AND DocsComplete(c) THEN ClaimApproved(c)",
    "IF NotPoliceReportSubmitted(c) THEN ClaimPending_Docs(c)",
]

DEFAULT_FACTS = [
    "IncidentType(claim1, water_damage)",
    "BuildingInsured(claim1)",
    "PoliceReportSubmitted(claim1)",
    "EstimateSubmitted(claim1)",
]


def run(entity: str = "claim1") -> CaseStudyResult:
    facts = [f.replace("claim1", entity) for f in DEFAULT_FACTS]
    return SimpleRuleEngine().analyze(
        RULES,
        facts,
        entity=entity,
        deny_queries=["ClaimDenied_Exclusion({entity})"],
        allow_queries=["ClaimApproved({entity})"],
        escalate_queries=["ClaimPending_Docs({entity})"],
    )
