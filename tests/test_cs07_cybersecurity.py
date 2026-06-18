"""P4 CS-07: Cybersecurity root cause analysis tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps.case_studies.cs07_cybersecurity import rules as attack_rules
from apps.case_studies.cs07_cybersecurity.engine import IncidentAnalyzer, load_scenario
from apps.case_studies.cs07_cybersecurity.report import (
    format_incident_report,
    format_mttr_report,
)
from axiomai.connectors import SIEMConnector

SCENARIO = Path(__file__).resolve().parents[1] / "apps" / "case_studies" / "cs07_cybersecurity" / "scenarios" / "ransomware_incident.json"


@pytest.fixture
def scenario():
    return load_scenario(SCENARIO)


def test_attack_rules_count():
    assert len(attack_rules.ATTACK_CHAIN_RULES) >= 10


def test_scenario_has_enough_facts(scenario):
    assert len(scenario["facts"]) >= 15


def test_analyzer_confirms_ransomware(scenario):
    analyzer = IncidentAnalyzer()
    result = analyzer.analyze(scenario)
    assert result.confirmed is True
    assert "Host42" in result.incident_host
    assert any("INITIAL ACCESS" in step for step in result.attack_chain)


def test_analyzer_identifies_phishing_root_cause(scenario):
    analyzer = IncidentAnalyzer()
    result = analyzer.analyze(scenario)
    assert "Phishing" in result.root_cause or "InitialAccess" in result.root_cause


def test_siem_connector_feeds_facts():
    facts = SIEMConnector().fetch_evidence()
    analyzer = IncidentAnalyzer()
    result = analyzer.analyze_from_predicates([str(f.predicate) for f in facts])
    assert result is not None


def test_mttr_report_format(scenario):
    analyzer = IncidentAnalyzer()
    result = analyzer.analyze(scenario)
    report = format_mttr_report(result)
    assert "MTTR" in report
    assert "6 hours" in report or "360" in report
    assert "45" in report


def test_incident_report_format(scenario):
    analyzer = IncidentAnalyzer()
    result = analyzer.analyze(scenario)
    report = format_incident_report(result)
    assert "ROOT CAUSE" in report
    assert "Attack Chain" in report


def test_scenario_json_valid():
    data = json.loads(SCENARIO.read_text())
    assert data["incident_id"]
    assert data["host"] == "Host42"
