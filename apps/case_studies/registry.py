"""Central registry for all 18 AxiomAI case studies."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from apps.case_studies._base.simple_engine import CaseStudyResult
from apps.case_studies.cs01_msp_network.engine import run as run_cs01
from apps.case_studies.cs02_soc2.engine import GapAnalysisEngine
from apps.case_studies.cs02_soc2.report import export_gap_report_json
from apps.case_studies.cs03_support_governance.engine import SupportGovernanceDemo
from apps.case_studies.cs04_healthcare.engine import run as run_cs04
from apps.case_studies.cs05_code_review.engine import run as run_cs05
from apps.case_studies.cs06_procurement.engine import run as run_cs06
from apps.case_studies.cs07_cybersecurity.engine import IncidentAnalyzer, load_scenario
from apps.case_studies.cs07_cybersecurity.report import (
    format_incident_report,
    format_mttr_report,
)
from apps.case_studies.cs08_contract.engine import run as run_cs08
from apps.case_studies.cs09_insurance.engine import run as run_cs09
from apps.case_studies.cs10_banking.engine import run as run_cs10
from apps.case_studies.cs11_hr_policy.engine import run as run_cs11
from apps.case_studies.cs12_data_governance.engine import run as run_cs12
from apps.case_studies.cs13_cloud_cost.engine import run as run_cs13
from apps.case_studies.cs14_manufacturing.engine import run as run_cs14
from apps.case_studies.cs15_education.engine import run as run_cs15
from apps.case_studies.cs16_immigration.engine import run as run_cs16
from apps.case_studies.cs17_sales.engine import run as run_cs17
from apps.case_studies.cs18_trading.engine import run as run_cs18
from axiomai.connectors import AWSConfigConnector, AzureADConnector, SIEMConnector

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "axiomai" / "governance" / "policies" / "refund-policy.yaml"
CS07_SCENARIO = ROOT / "apps" / "case_studies" / "cs07_cybersecurity" / "scenarios" / "ransomware_incident.json"

CASE_STUDY_CATALOG: list[dict[str, str]] = [
    {"id": "cs-01", "name": "MSP Network Operations", "description": "VPN outage root cause — certificate expiration", "tier": "2", "module": "CS-01", "slug": "01-msp-network"},
    {"id": "cs-02", "name": "SOC2 Compliance Automation", "description": "Automated control gap analysis", "tier": "1", "module": "CS-02", "slug": "02-soc2-compliance"},
    {"id": "cs-03", "name": "AI Customer Support Governance", "description": "Refund policy enforcement for LLM agents", "tier": "1", "module": "CS-03", "slug": "03-ai-support-governance"},
    {"id": "cs-04", "name": "Healthcare Prior Authorization", "description": "Clinical criteria for prior auth approval", "tier": "3", "module": "CS-04", "slug": "04-healthcare-prior-auth"},
    {"id": "cs-05", "name": "AI Code Review Guardrail", "description": "Block insecure code patterns before deploy", "tier": "5", "module": "CS-05", "slug": "05-ai-code-review"},
    {"id": "cs-06", "name": "Procurement Agent Governance", "description": "Block unapproved agent purchases", "tier": "2", "module": "CS-06", "slug": "06-procurement-agent"},
    {"id": "cs-07", "name": "Cybersecurity Root Cause Analysis", "description": "Ransomware attack chain reconstruction", "tier": "1", "module": "CS-07", "slug": "07-cybersecurity"},
    {"id": "cs-08", "name": "Contract / SLA Analysis", "description": "SLA breach and obligation triggers", "tier": "3", "module": "CS-08", "slug": "08-contract-analysis"},
    {"id": "cs-09", "name": "Insurance Claims", "description": "Coverage and documentation validation", "tier": "3", "module": "CS-09", "slug": "09-insurance-claims"},
    {"id": "cs-10", "name": "Banking Loan Eligibility", "description": "Underwriting tier and decline rules", "tier": "3", "module": "CS-10", "slug": "10-banking-loan"},
    {"id": "cs-11", "name": "HR Policy Engine", "description": "Benefits and leave eligibility", "tier": "4", "module": "CS-11", "slug": "11-hr-policy"},
    {"id": "cs-12", "name": "Data Governance", "description": "PHI/PII/PCI access control", "tier": "2", "module": "CS-12", "slug": "12-data-governance"},
    {"id": "cs-13", "name": "Cloud Cost Governance", "description": "FinOps resource approval policies", "tier": "2", "module": "CS-13", "slug": "13-cloud-cost"},
    {"id": "cs-14", "name": "Manufacturing QC", "description": "Defect root cause diagnosis", "tier": "4", "module": "CS-14", "slug": "14-manufacturing-qc"},
    {"id": "cs-15", "name": "Education Degree Audit", "description": "Enrollment and graduation eligibility", "tier": "4", "module": "CS-15", "slug": "15-education-degree"},
    {"id": "cs-16", "name": "Immigration Assistant", "description": "H-1B filing eligibility checklist", "tier": "4", "module": "CS-16", "slug": "16-immigration"},
    {"id": "cs-17", "name": "Sales Qualification", "description": "ICP-based lead routing", "tier": "4", "module": "CS-17", "slug": "17-sales-qualification"},
    {"id": "cs-18", "name": "Agentic Trading Guardrail", "description": "Position limits and trading halts", "tier": "5", "module": "CS-18", "slug": "18-agentic-trading"},
]

_RUNNERS: dict[str, Callable[[], dict[str, Any]]] = {}


def _wrap(case_id: str, result: CaseStudyResult) -> dict[str, Any]:
    payload = result.to_dict()
    payload["case_study_id"] = case_id
    return payload


def _register_p6() -> None:
    mapping = {
        "cs-01": run_cs01,
        "cs-04": run_cs04,
        "cs-05": run_cs05,
        "cs-06": run_cs06,
        "cs-08": run_cs08,
        "cs-09": run_cs09,
        "cs-10": run_cs10,
        "cs-11": run_cs11,
        "cs-12": run_cs12,
        "cs-13": run_cs13,
        "cs-14": run_cs14,
        "cs-15": run_cs15,
        "cs-16": run_cs16,
        "cs-17": run_cs17,
        "cs-18": run_cs18,
    }
    for case_id, fn in mapping.items():
        _RUNNERS[case_id] = lambda cid=case_id, f=fn: _wrap(cid, f())


def _run_cs07() -> dict[str, Any]:
    scenario = load_scenario(CS07_SCENARIO)
    siem_facts = [str(f.predicate) for f in SIEMConnector().fetch_evidence()]
    scenario["facts"].extend(
        {"predicate": p, "timestamp": "", "evidence": f"SIEM: {p}"} for p in siem_facts
    )
    result = IncidentAnalyzer().analyze(scenario)
    return {
        "case_study_id": "cs-07",
        "outcome": "CONFIRMED" if result.confirmed else "PROBABLE",
        "confirmed": result.confirmed,
        "incident_id": result.incident_id,
        "root_cause": result.root_cause,
        "attack_chain": result.attack_chain,
        "mttr": {"before_minutes": result.mttr_before_minutes, "after_minutes": result.mttr_after_minutes},
        "report": format_incident_report(result),
        "mttr_report": format_mttr_report(result),
    }


def _run_cs02() -> dict[str, Any]:
    engine = GapAnalysisEngine()
    engine.load_connectors(AzureADConnector(), AWSConfigConnector())
    report = engine.run_audit()
    return {
        "case_study_id": "cs-02",
        "outcome": "AUDIT_COMPLETE",
        "pass_count": report.pass_count,
        "fail_count": report.fail_count,
        "controls": [
            {"control_id": c.control_id, "name": c.name, "status": c.status, "gap_summary": c.gap_summary}
            for c in report.controls
        ],
        "gap_report_json": export_gap_report_json(report),
    }


def _run_cs03() -> dict[str, Any]:
    demo = SupportGovernanceDemo(POLICY_PATH)
    result = demo.simulate_llm_refund_request(
        customer="order1", amount=350, days_since_purchase=43, product_returned=False
    )
    return {
        "case_study_id": "cs-03",
        "outcome": result.decision.outcome,
        "action": result.action,
        "decision": result.decision.to_dict(),
        "audit_entry": result.audit_entry,
    }


def _register_tier1() -> None:
    _RUNNERS["cs-07"] = _run_cs07
    _RUNNERS["cs-02"] = _run_cs02
    _RUNNERS["cs-03"] = _run_cs03


_register_tier1()
_register_p6()


def list_case_studies() -> list[dict[str, str]]:
    return list(CASE_STUDY_CATALOG)


def run_case_study(case_study_id: str) -> dict[str, Any]:
    runner = _RUNNERS.get(case_study_id)
    if runner is None:
        raise KeyError(case_study_id)
    return runner()
