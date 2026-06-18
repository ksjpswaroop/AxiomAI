"""CS-01 MSP network operations — VPN root cause analysis."""

from __future__ import annotations

from apps.case_studies._base.simple_engine import CaseStudyResult, SimpleRuleEngine

RULES = [
    "IF AuthFailureIncreased(x) AND CertificateExpired(x) THEN RootCause_Certificate(x)",
    "IF VpnServiceRunning(x) AND RootCause_Certificate(x) THEN VpnOutageExplained(x)",
    "IF DnsFailure(x) AND NotCertificateIssue(x) THEN RootCause_Dns(x)",
]

DEFAULT_FACTS = [
    "AuthFailureIncreased(vpn1)",
    "CertificateExpired(vpn1)",
    "VpnServiceRunning(vpn1)",
]


def run(entity: str = "vpn1") -> CaseStudyResult:
    facts = [f.replace("vpn1", entity) for f in DEFAULT_FACTS]
    result = SimpleRuleEngine().analyze(
        RULES,
        facts,
        entity=entity,
        goal_queries=["RootCause_Certificate({entity})", "VpnOutageExplained({entity})"],
    )
    if result.outcome == "PROVED":
        result.outcome = "ROOT_CAUSE_FOUND"
        result.explanation = "VPN certificate expired — root cause of authentication failures."
    return result
