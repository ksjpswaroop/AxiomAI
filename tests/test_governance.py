"""P3a: Agent governance framework tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from axiomai.governance import (
    AuditLog,
    Decision,
    EscalationRouter,
    GovernanceEngine,
    PolicyPack,
)

POLICY_YAML = """\
name: refund-policy
version: "1.0"
action_type: refund
rules:
  - IF WithinRefundWindow(x) AND UnderLimit(x) AND ProductReturned(x) AND NotFinalSale(x) THEN RefundAllowed(x)
  - IF AmountMidRange(x) THEN EscalateRefund(x)
  - IF AlreadyRefunded(x) THEN RefundDenied(x)
  - IF OutsideRefundWindow(x) THEN PolicyViolation_Window(x)
  - IF NotProductReturned(x) THEN PolicyViolation_Return(x)
allow_query: "RefundAllowed({entity})"
deny_queries:
  - "RefundDenied({entity})"
  - "PolicyViolation_Window({entity})"
  - "PolicyViolation_Return({entity})"
escalate_queries:
  - "EscalateRefund({entity})"
  - "ManagerApprovalRequired({entity})"
"""

VIOLATION_CONTEXT = [
    "OutsideRefundWindow(order1)",
    "UnderLimit(order1)",
    "NotProductReturned(order1)",
    "NotAlreadyRefunded(order1)",
    "NotFinalSale(order1)",
]

ALLOW_CONTEXT = [
    "WithinRefundWindow(order2)",
    "UnderLimit(order2)",
    "ProductReturned(order2)",
    "NotAlreadyRefunded(order2)",
    "NotFinalSale(order2)",
]

ESCALATE_CONTEXT = [
    "WithinRefundWindow(order3)",
    "AmountMidRange(order3)",
    "ProductReturned(order3)",
    "NotAlreadyRefunded(order3)",
    "NotFinalSale(order3)",
]


@pytest.fixture
def policy_file(tmp_path: Path) -> Path:
    path = tmp_path / "refund-policy.yaml"
    path.write_text(POLICY_YAML)
    return path


def test_policy_pack_load_yaml(policy_file: Path):
    pack = PolicyPack.load(policy_file)
    assert pack.name == "refund-policy"
    assert pack.version == "1.0"
    assert len(pack.rules) == 5
    assert "RefundAllowed({entity})" in pack.allow_query


def test_policy_pack_load_json(tmp_path: Path):
    payload = {
        "name": "refund-policy",
        "version": "1.0",
        "action_type": "refund",
        "rules": [
            "IF WithinRefundWindow(x) AND UnderLimit(x) AND ProductReturned(x) "
            "AND NotFinalSale(x) THEN RefundAllowed(x)",
            "IF AlreadyRefunded(x) THEN RefundDenied(x)",
        ],
        "allow_query": "RefundAllowed({entity})",
        "deny_queries": ["RefundDenied({entity})"],
        "escalate_queries": [],
    }
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(payload))
    pack = PolicyPack.load(path)
    assert pack.name == "refund-policy"
    assert len(pack.rules) == 2


def test_governance_denies_policy_violation(policy_file: Path):
    engine = GovernanceEngine(PolicyPack.load(policy_file))
    decision = engine.validate(
        action={"type": "refund", "entity": "order1", "amount": 350},
        context=VIOLATION_CONTEXT,
    )
    assert decision.outcome == "DENY"
    assert decision.proof is not None
    assert len(decision.violated_rules) >= 1
    assert "window" in decision.explanation.lower() or "return" in decision.explanation.lower()


def test_governance_allows_compliant_refund(policy_file: Path):
    engine = GovernanceEngine(PolicyPack.load(policy_file))
    decision = engine.validate(
        action={"type": "refund", "entity": "order2", "amount": 200},
        context=ALLOW_CONTEXT,
    )
    assert decision.outcome == "ALLOW"
    assert decision.proof is not None


def test_governance_escalates_mid_range_amount(policy_file: Path):
    engine = GovernanceEngine(PolicyPack.load(policy_file))
    decision = engine.validate(
        action={"type": "refund", "entity": "order3", "amount": 750},
        context=ESCALATE_CONTEXT,
    )
    assert decision.outcome == "ESCALATE"


def test_audit_log_append_only(policy_file: Path):
    engine = GovernanceEngine(PolicyPack.load(policy_file))
    audit = AuditLog()
    decision = engine.validate(
        action={"type": "refund", "entity": "order1", "amount": 350},
        context=VIOLATION_CONTEXT,
    )
    entry = audit.record(decision, action={"type": "refund", "entity": "order1"})
    assert entry["outcome"] == "DENY"
    assert "timestamp" in entry
    assert "proof" in entry
    assert len(audit.entries) == 1
    audit.record(decision, action={"type": "refund", "entity": "order1"})
    assert len(audit.entries) == 2


def test_escalation_router_routes_by_outcome():
    router = EscalationRouter(
        routes={
            "DENY": "agent-feedback",
            "ESCALATE": "manager-queue",
        }
    )
    deny = Decision(outcome="DENY", explanation="blocked", violated_rules=["r1"])
    esc = Decision(outcome="ESCALATE", explanation="needs approval", violated_rules=[])
    assert router.route(deny) == "agent-feedback"
    assert router.route(esc) == "manager-queue"
    allow = Decision(outcome="ALLOW", explanation="ok", violated_rules=[])
    assert router.route(allow) is None


def test_governance_demo_blocks_violating_action(policy_file: Path):
    """P3 exit criteria: middleware blocks policy-violating agent action with proof."""
    engine = GovernanceEngine(PolicyPack.load(policy_file))
    audit = AuditLog()
    router = EscalationRouter(routes={"DENY": "agent-feedback", "ESCALATE": "manager-queue"})

    action = {"type": "refund", "entity": "order1", "amount": 350, "agent": "support-bot"}
    decision = engine.validate(action=action, context=VIOLATION_CONTEXT)
    audit.record(decision, action=action)
    queue = router.route(decision)

    assert decision.outcome == "DENY"
    assert decision.proof is not None
    assert queue == "agent-feedback"
    assert audit.entries[-1]["outcome"] == "DENY"
