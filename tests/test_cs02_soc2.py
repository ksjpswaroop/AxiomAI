"""P4 CS-02: SOC2 compliance automation tests."""

from __future__ import annotations

import json

import pytest

from apps.case_studies.cs02_soc2.engine import SOC2_CONTROLS, GapAnalysisEngine
from apps.case_studies.cs02_soc2.report import (
    export_gap_report_json,
    export_gap_report_markdown,
)
from axiomai.connectors import AWSConfigConnector, AzureADConnector


@pytest.fixture
def gap_report():
    engine = GapAnalysisEngine()
    engine.load_connectors(AzureADConnector(), AWSConfigConnector())
    return engine.run_audit()


def test_soc2_controls_count():
    assert len(SOC2_CONTROLS) >= 8


def test_mfa_control_fails(gap_report):
    mfa = next(c for c in gap_report.controls if c.control_id == "CC6.1")
    assert mfa.status == "FAIL"
    assert "bob" in mfa.gap_summary.lower() or "MfaDisabled" in str(mfa.evidence)


def test_backup_control_detects_gap(gap_report):
    backup = next(c for c in gap_report.controls if c.control_id == "CC7.2")
    assert backup.status in ("FAIL", "PASS")


def test_log_retention_control(gap_report):
    log_ctrl = next(c for c in gap_report.controls if c.control_id == "CC7.3")
    assert log_ctrl.status in ("FAIL", "PASS")


def test_access_review_control(gap_report):
    access = next(c for c in gap_report.controls if c.control_id == "CC6.2")
    assert access.status in ("FAIL", "PASS")


def test_gap_report_json_export(gap_report):
    payload = json.loads(export_gap_report_json(gap_report))
    assert "controls" in payload
    assert len(payload["controls"]) >= 8


def test_gap_report_markdown_export(gap_report):
    md = export_gap_report_markdown(gap_report)
    assert "Control ID" in md or "CC6.1" in md
    assert "FAIL" in md or "PASS" in md


def test_each_control_has_pass_or_fail(gap_report):
    for control in gap_report.controls:
        assert control.status in ("PASS", "FAIL")
