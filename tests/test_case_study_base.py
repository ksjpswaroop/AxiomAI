"""P3c: Shared case study utilities tests."""

from __future__ import annotations

from apps.case_studies._base import (
    DemoRunner,
    format_decision_report,
    format_proof_summary,
)
from axiomai.governance import Decision


def test_format_decision_report_deny():
    decision = Decision(
        outcome="DENY",
        explanation="Purchase outside 30-day window.",
        violated_rules=["PolicyViolation_Window(order1)"],
    )
    report = format_decision_report(
        title="Refund Governance",
        action={"type": "refund", "entity": "order1", "amount": 350},
        decision=decision,
    )
    assert "DENY" in report
    assert "order1" in report
    assert "30-day" in report or "window" in report.lower()


def test_format_proof_summary():
    decision = Decision(
        outcome="DENY",
        explanation="Blocked",
        violated_rules=["PolicyViolation_Return(order1)"],
        proof={"query": "PolicyViolation_Return(order1)", "result": "PROVED", "steps": []},
    )
    summary = format_proof_summary(decision)
    assert "PROVED" in summary or "PolicyViolation" in summary


def test_demo_runner_executes_steps(capsys):
    steps_run: list[str] = []

    def step_one():
        steps_run.append("load")

    def step_two():
        steps_run.append("validate")

    runner = DemoRunner("Refund Demo")
    runner.add_step("Load policy", step_one)
    runner.add_step("Validate action", step_two)
    report = runner.run()
    assert steps_run == ["load", "validate"]
    assert "Refund Demo" in report
    captured = capsys.readouterr()
    assert "Load policy" in captured.out or "Refund Demo" in report
