"""CS-10 Banking loan eligibility."""

from __future__ import annotations

from apps.case_studies._base.simple_engine import CaseStudyResult, SimpleRuleEngine

RULES = [
    "IF CreditScorePrime(a) AND DtiPrime(a) AND VerifiedIncome(a) AND EmploymentStable(a) THEN LoanTier_Prime(a)",
    "IF CreditScoreSubprime(a) AND DtiSubprime(a) THEN LoanTier_Subprime(a)",
    "IF DtiTooHigh(a) THEN LoanDeclined(a)",
    "IF CreditScoreTooLow(a) THEN LoanDeclined(a)",
    "IF FraudFlag(a) THEN LoanDeclined(a)",
    "IF SelfEmployedVolatile(a) THEN ManualReviewRequired(a)",
]

DEFAULT_FACTS = [
    "CreditScorePrime(applicant1)",
    "DtiPrime(applicant1)",
    "VerifiedIncome(applicant1)",
    "EmploymentStable(applicant1)",
]


def run(entity: str = "applicant1") -> CaseStudyResult:
    facts = [f.replace("applicant1", entity) for f in DEFAULT_FACTS]
    return SimpleRuleEngine().analyze(
        RULES,
        facts,
        entity=entity,
        deny_queries=["LoanDeclined({entity})"],
        allow_queries=["LoanTier_Prime({entity})", "LoanTier_Subprime({entity})"],
        escalate_queries=["ManualReviewRequired({entity})"],
    )
