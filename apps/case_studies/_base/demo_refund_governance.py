#!/usr/bin/env python3
"""P3 exit demo — refund governance blocks policy-violating agent action."""

from __future__ import annotations

from pathlib import Path

from apps.case_studies._base import DemoRunner, format_decision_report
from axiomai.governance import AuditLog, EscalationRouter, GovernanceEngine, PolicyPack

POLICY = Path(__file__).resolve().parents[3] / "axiomai" / "governance" / "policies" / "refund-policy.yaml"

VIOLATION_CONTEXT = [
    "OutsideRefundWindow(order1)",
    "UnderLimit(order1)",
    "NotProductReturned(order1)",
    "NotAlreadyRefunded(order1)",
    "NotFinalSale(order1)",
]


def main() -> None:
    runner = DemoRunner("AI Support Governance — Refund Policy")
    engine_holder: dict[str, GovernanceEngine] = {}
    decision_holder: dict[str, object] = {}

    def load_policy() -> None:
        engine_holder["engine"] = GovernanceEngine(PolicyPack.load(POLICY))

    def validate_refund() -> None:
        action = {"type": "refund", "entity": "order1", "amount": 350, "agent": "support-bot"}
        decision = engine_holder["engine"].validate(action=action, context=VIOLATION_CONTEXT)
        decision_holder["decision"] = decision
        decision_holder["action"] = action

    def audit_and_route() -> None:
        audit = AuditLog()
        router = EscalationRouter(routes={"DENY": "agent-feedback", "ESCALATE": "manager-queue"})
        decision = decision_holder["decision"]
        action = decision_holder["action"]
        audit.record(decision, action=action)
        queue = router.route(decision)
        report = format_decision_report("Refund Governance", action, decision)
        print(report)
        print(f"Routed to: {queue}")
        print(f"Audit entries: {len(audit.entries)}")

    runner.add_step("Load refund policy", load_policy)
    runner.add_step("Validate agent refund request", validate_refund)
    runner.add_step("Audit decision and route", audit_and_route)
    runner.run()


if __name__ == "__main__":
    main()
