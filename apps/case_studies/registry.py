"""Central registry for all 18 AxiomAI case studies."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apps.case_studies._base.case_runner import run_case as run_rule_governance_case
from apps.case_studies._base.scenario_loader import list_definitions, load_definition
from apps.case_studies._base.simple_engine import CaseStudyResult
from apps.case_studies.cs02_soc2.engine import GapAnalysisEngine
from apps.case_studies.cs02_soc2.report import export_gap_report_json
from apps.case_studies.cs03_support_governance.engine import SupportGovernanceDemo
from apps.case_studies.cs07_cybersecurity.engine import IncidentAnalyzer, load_scenario
from apps.case_studies.cs07_cybersecurity.report import (
    format_incident_report,
    format_mttr_report,
)
from axiomai.connectors import AWSConfigConnector, AzureADConnector, SIEMConnector

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "axiomai" / "governance" / "policies" / "refund-policy.yaml"
CS07_SCENARIO = ROOT / "apps" / "case_studies" / "cs07_cybersecurity" / "scenarios" / "ransomware_incident.json"

_RUNNERS: dict[str, Any] = {}


def _enrich(payload: dict[str, Any], case_id: str, scenario_id: str) -> dict[str, Any]:
    try:
        definition = load_definition(case_id)
        payload.setdefault("name", definition.get("name"))
        payload.setdefault("story", definition.get("story"))
        payload.setdefault("problem", definition.get("problem"))
        payload["data_sources"] = definition.get("data_sources", [])
        payload["tier"] = definition.get("tier")
        payload["module"] = definition.get("module")
    except KeyError:
        pass
    payload["scenario_id"] = scenario_id
    return payload


def _run_cs07(scenario_id: str = "default") -> dict[str, Any]:
    scenario = load_scenario(CS07_SCENARIO)
    siem_facts = [str(f.predicate) for f in SIEMConnector().fetch_evidence()]
    scenario["facts"].extend(
        {"predicate": p, "timestamp": "", "evidence": f"SIEM: {p}"} for p in siem_facts
    )
    result = IncidentAnalyzer().analyze(scenario)
    payload = {
        "case_study_id": "cs-07",
        "outcome": "CONFIRMED" if result.confirmed else "PROBABLE",
        "confirmed": result.confirmed,
        "incident_id": result.incident_id,
        "root_cause": result.root_cause,
        "attack_chain": result.attack_chain,
        "mttr": {"before_minutes": result.mttr_before_minutes, "after_minutes": result.mttr_after_minutes},
        "report": format_incident_report(result),
        "mttr_report": format_mttr_report(result),
        "proofs": [{"attack_chain": result.attack_chain, "root_cause": result.root_cause}],
    }
    return _enrich(payload, "cs-07", scenario_id)


def _run_cs02(scenario_id: str = "default") -> dict[str, Any]:
    engine = GapAnalysisEngine()
    engine.load_connectors(AzureADConnector(), AWSConfigConnector())
    report = engine.run_audit()
    payload = {
        "case_study_id": "cs-02",
        "outcome": "AUDIT_COMPLETE",
        "pass_count": report.pass_count,
        "fail_count": report.fail_count,
        "controls": [
            {"control_id": c.control_id, "name": c.name, "status": c.status, "gap_summary": c.gap_summary}
            for c in report.controls
        ],
        "gap_report_json": export_gap_report_json(report),
        "proofs": [{"controls_evaluated": len(report.controls)}],
    }
    return _enrich(payload, "cs-02", scenario_id)


def _run_cs03(scenario_id: str = "deny_outside_window") -> dict[str, Any]:
    from apps.case_studies.cs03_support_governance.engine import SCENARIOS

    demo = SupportGovernanceDemo(POLICY_PATH)
    if scenario_id in SCENARIOS:
        result = demo.run_scenario(scenario_id)
    else:
        result = demo.simulate_llm_refund_request(
            customer="order1", amount=350, days_since_purchase=43, product_returned=False
        )

    payload = {
        "case_study_id": "cs-03",
        "outcome": result.decision.outcome,
        "action": result.action,
        "decision": result.decision.to_dict(),
        "audit_entry": result.audit_entry,
        "explanation": result.decision.explanation,
        "proofs": result.decision.proofs or ([result.decision.proof] if result.decision.proof else []),
        "scenario_description": result.description,
    }
    return _enrich(payload, "cs-03", scenario_id)


def _register() -> None:
    for item in list_definitions():
        case_id = item["id"]
        definition = load_definition(case_id)
        runner_type = definition.get("runner", "rules")

        if runner_type == "custom_cyber":
            _RUNNERS[case_id] = _run_cs07
        elif runner_type == "custom_soc2":
            _RUNNERS[case_id] = _run_cs02
        elif runner_type == "custom_governance":
            _RUNNERS[case_id] = _run_cs03
        else:
            def _make(cid: str):
                return lambda scenario_id="default": _enrich(
                    run_rule_governance_case(cid, scenario_id), cid, scenario_id
                )
            _RUNNERS[case_id] = _make(case_id)


_register()


def list_case_studies() -> list[dict[str, Any]]:
    return list_definitions()


def list_scenarios(case_study_id: str) -> list[dict[str, str]]:
    definition = load_definition(case_study_id)
    return [
        {"id": sid, "label": s.get("label", sid), "expected_outcome": s.get("expected_outcome", "")}
        for sid, s in definition.get("scenarios", {}).items()
    ]


def run_case_study(case_study_id: str, scenario_id: str = "default") -> dict[str, Any]:
    runner = _RUNNERS.get(case_study_id)
    if runner is None:
        raise KeyError(case_study_id)
    return runner(scenario_id)


CASE_STUDY_CATALOG = list_case_studies()
