"""CS-14 Manufacturing quality control."""

from __future__ import annotations

from apps.case_studies._base.simple_engine import CaseStudyResult, SimpleRuleEngine

RULES = [
    "IF VibrationHigh(l) AND AlignmentDeviation(l) AND MaintenanceOverdue(l) THEN RootCause_Misalignment(l)",
    "IF TemperatureHigh(l) AND BearingWear(l) THEN RootCause_BearingFailure(l)",
    "IF SurfaceDefectSpike(l) AND NewMaterialLot(l) THEN RootCause_BadBatch(l)",
    "IF ScrapRate(l, r) AND Over5Percent(r) THEN QcEscalation(l)",
]

DEFAULT_FACTS = [
    "VibrationHigh(line3)",
    "AlignmentDeviation(line3)",
    "MaintenanceOverdue(line3)",
    "ScrapRate(line3, 6)",
    "Over5Percent(6)",
]


def run(entity: str = "line3") -> CaseStudyResult:
    facts = [f.replace("line3", entity) for f in DEFAULT_FACTS]
    result = SimpleRuleEngine().analyze(
        RULES,
        facts,
        entity=entity,
        goal_queries=["RootCause_Misalignment({entity})", "QcEscalation({entity})"],
    )
    if result.outcome == "PROVED":
        result.outcome = "DIAGNOSIS_FOUND"
    return result
