"""Case study registry and demo execution for the working application API."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apps.case_studies.cs02_soc2.engine import GapAnalysisEngine
from apps.case_studies.cs02_soc2.report import export_gap_report_json
from apps.case_studies.cs03_support_governance.engine import SupportGovernanceDemo
from apps.case_studies.cs07_cybersecurity.engine import IncidentAnalyzer, load_scenario
from apps.case_studies.cs07_cybersecurity.report import (
    format_incident_report,
    format_mttr_report,
)
from axiomai.connectors import AWSConfigConnector, AzureADConnector, SIEMConnector

ROOT = Path(__file__).resolve().parents[3]
POLICY_PATH = ROOT / "axiomai" / "governance" / "policies" / "refund-policy.yaml"
CS07_SCENARIO = ROOT / "apps" / "case_studies" / "cs07_cybersecurity" / "scenarios" / "ransomware_incident.json"

CASE_STUDY_CATALOG: list[dict[str, str]] = [
    {
        "id": "cs-07",
        "name": "Cybersecurity Root Cause Analysis",
        "description": "Ransomware attack chain reconstruction with MTTR metrics",
        "tier": "1",
        "module": "CS-07",
    },
    {
        "id": "cs-02",
        "name": "SOC2 Compliance Automation",
        "description": "Automated control gap analysis from enterprise evidence",
        "tier": "1",
        "module": "CS-02",
    },
    {
        "id": "cs-03",
        "name": "AI Customer Support Governance",
        "description": "Deterministic refund policy enforcement for LLM agents",
        "tier": "1",
        "module": "CS-03",
    },
]


def list_case_studies() -> list[dict[str, str]]:
    return list(CASE_STUDY_CATALOG)


def run_case_study(case_study_id: str) -> dict[str, Any]:
    runners = {
        "cs-07": _run_cs07,
        "cs-02": _run_cs02,
        "cs-03": _run_cs03,
    }
    if case_study_id not in runners:
        raise KeyError(case_study_id)
    return runners[case_study_id]()


def _run_cs07() -> dict[str, Any]:
    scenario = load_scenario(CS07_SCENARIO)
    siem_facts = [str(f.predicate) for f in SIEMConnector().fetch_evidence()]
    scenario["facts"].extend(
        {"predicate": p, "timestamp": "", "evidence": f"SIEM: {p}"} for p in siem_facts
    )
    result = IncidentAnalyzer().analyze(scenario)
    return {
        "case_study_id": "cs-07",
        "incident_id": result.incident_id,
        "incident_host": result.incident_host,
        "confirmed": result.confirmed,
        "root_cause": result.root_cause,
        "confidence": result.confidence,
        "attack_chain": result.attack_chain,
        "containment": result.containment,
        "mttr": {
            "before_minutes": result.mttr_before_minutes,
            "after_minutes": result.mttr_after_minutes,
        },
        "report": format_incident_report(result),
        "mttr_report": format_mttr_report(result),
    }


def _run_cs02() -> dict[str, Any]:
    engine = GapAnalysisEngine()
    engine.load_connectors(AzureADConnector(), AWSConfigConnector())
    report = engine.run_audit()
    return {
        "case_study_id": "cs-02",
        "audit_id": report.audit_id,
        "pass_count": report.pass_count,
        "fail_count": report.fail_count,
        "controls": [
            {
                "control_id": c.control_id,
                "name": c.name,
                "status": c.status,
                "gap_summary": c.gap_summary,
                "evidence": c.evidence,
            }
            for c in report.controls
        ],
        "gap_report_json": export_gap_report_json(report),
    }


def _run_cs03() -> dict[str, Any]:
    demo = SupportGovernanceDemo(POLICY_PATH)
    result = demo.simulate_llm_refund_request(
        customer="order1",
        amount=350,
        days_since_purchase=43,
        product_returned=False,
    )
    return {
        "case_study_id": "cs-03",
        "scenario": result.scenario_id,
        "description": result.description,
        "action": result.action,
        "decision": result.decision.to_dict(),
        "audit_entry": result.audit_entry,
    }
