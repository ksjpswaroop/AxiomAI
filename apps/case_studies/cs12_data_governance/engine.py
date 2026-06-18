"""CS-12 Data governance and access control."""

from __future__ import annotations

from apps.case_studies._base.simple_engine import CaseStudyResult, SimpleRuleEngine

RULES = [
    "IF DataClassification(x, PHI) AND ApprovedHealthcareRole(u) AND HipaaTraining(u) THEN GrantAccess(u, x)",
    "IF DataClassification(x, PCI) AND FinanceDepartment(u) AND BackgroundCheck(u) THEN GrantAccess(u, x)",
    "IF DataClassification(x, PII) AND ApprovedCustomerRole(u) AND ManagerApproval(u) THEN GrantAccess(u, x)",
    "IF DataAnalystRole(u) AND FullSalesforceAccess(x) THEN AccessDenied_Role(u, x)",
    "IF DataClassification(x, PCI) AND NotFinanceDepartment(u) THEN AccessDenied_PCI(u, x)",
    "IF TerminatedEmployee(u) THEN RevokeAllAccess(u)",
]

DEFAULT_FACTS = [
    "DataClassification(ar9942, PII)",
    "DataClassification(ar9942, PCI)",
    "DataAnalystRole(alex)",
    "FullSalesforceAccess(ar9942)",
    "NotFinanceDepartment(alex)",
    "NotManagerApproval(alex)",
]


def run(entity: str = "alex") -> CaseStudyResult:
    facts = list(DEFAULT_FACTS)
    result = SimpleRuleEngine().analyze(
        RULES,
        facts,
        entity=entity,
        deny_queries=[
            "AccessDenied_Role({entity}, ar9942)",
            "AccessDenied_PCI({entity}, ar9942)",
            "RevokeAllAccess({entity})",
        ],
        allow_queries=["GrantAccess({entity}, ar9942)"],
    )
    if result.outcome == "DENY":
        result.explanation = "Access denied — role not approved for PII/PCI Salesforce data."
    return result
