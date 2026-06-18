"""CS-15 Education degree audit."""

from __future__ import annotations

from apps.case_studies._base.simple_engine import CaseStudyResult, SimpleRuleEngine

RULES = [
    "IF PrerequisiteCompleted(s, calc1) AND EnrolledIn(s, calc2) THEN EnrollmentAllowed(s, calc2)",
    "IF NotPrerequisiteCompleted(s, calc1) AND EnrolledIn(s, calc2) THEN EnrollmentDenied(s, calc2)",
    "IF TotalCredits(s, c) AND AtLeast120(c) AND MajorCredits(s, m) AND AtLeast40Major(m) AND GpaMet(s) THEN GraduationEligible(s)",
]

DEFAULT_FACTS = [
    "PrerequisiteCompleted(student1, calc1)",
    "EnrolledIn(student1, calc2)",
    "TotalCredits(student1, 124)",
    "AtLeast120(124)",
    "MajorCredits(student1, 42)",
    "AtLeast40Major(42)",
    "GpaMet(student1)",
]


def run(entity: str = "student1") -> CaseStudyResult:
    facts = [f.replace("student1", entity) for f in DEFAULT_FACTS]
    return SimpleRuleEngine().analyze(
        RULES,
        facts,
        entity=entity,
        deny_queries=["EnrollmentDenied({entity}, calc2)"],
        allow_queries=["EnrollmentAllowed({entity}, calc2)", "GraduationEligible({entity})"],
    )
