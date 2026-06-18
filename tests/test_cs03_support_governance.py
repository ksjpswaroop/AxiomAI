"""P4 CS-03: AI support governance case study tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps.case_studies.cs03_support_governance.engine import (
    SCENARIOS,
    SupportGovernanceDemo,
)
from apps.case_studies.cs03_support_governance.report import format_audit_trail

POLICY = Path(__file__).resolve().parents[1] / "axiomai" / "governance" / "policies" / "refund-policy.yaml"


@pytest.fixture
def demo():
    return SupportGovernanceDemo(POLICY)


def test_five_scenarios_defined():
    assert len(SCENARIOS) == 5


@pytest.mark.parametrize(
    "scenario_id,expected",
    [
        ("deny_outside_window", "DENY"),
        ("deny_not_returned", "DENY"),
        ("allow_compliant", "ALLOW"),
        ("escalate_mid_amount", "ESCALATE"),
        ("deny_already_refunded", "DENY"),
    ],
)
def test_scenario_outcomes(demo, scenario_id, expected):
    result = demo.run_scenario(scenario_id)
    assert result.decision.outcome == expected
    assert result.decision.proof is not None


def test_denied_scenario_lists_violations(demo):
    result = demo.run_scenario("deny_outside_window")
    assert result.decision.outcome == "DENY"
    assert len(result.decision.violated_rules) >= 1


def test_audit_log_immutable(demo):
    results = demo.run_all_scenarios()
    trail = format_audit_trail(results)
    assert len(trail) == 5
    assert all("timestamp" in entry for entry in trail)


def test_llm_refund_simulation_denied(demo):
    result = demo.simulate_llm_refund_request(
        customer="order1",
        amount=350,
        days_since_purchase=43,
        product_returned=False,
    )
    assert result.decision.outcome == "DENY"
    assert "window" in result.decision.explanation.lower() or "return" in result.decision.explanation.lower()
