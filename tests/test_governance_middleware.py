"""Governance middleware, registry, and multi-policy tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from axiomai.governance import (
    AgentGovernanceMiddleware,
    PolicyRegistry,
)
from axiomai.reasoner.api.audit_store import AuditStore
from axiomai.reasoner.api.main import app


PROCUREMENT_CONTEXT = [
    "PurchaseAmount(req1, 45000)",
    "OverThreshold1000(45000)",
    "OverThreshold10000(45000)",
    "NewVendor(req1, NewCloudProvider)",
    "ContractTermMonths(req1, 24)",
    "Over12Months(24)",
    "GpuResource(req1)",
]


def test_policy_registry_lists_builtin():
    registry = PolicyRegistry.default()
    policies = registry.list_policies()
    ids = {p["id"] for p in policies}
    assert "refund-policy" in ids
    assert "procurement-policy" in ids
    assert "data-access-policy" in ids
    assert "cloud-cost-policy" in ids


def test_procurement_policy_blocks_purchase():
    middleware = AgentGovernanceMiddleware()
    result = middleware.intercept(
        action={"type": "purchase", "entity": "req1", "amount": 45000},
        context=PROCUREMENT_CONTEXT,
        policy_id="procurement-policy",
    )
    assert result["decision"]["outcome"] in ("DENY", "ESCALATE")
    assert result["escalation_queue"] is not None or result["decision"]["outcome"] == "DENY"


def test_middleware_blocks_callback_on_deny():
    middleware = AgentGovernanceMiddleware()
    called = {"value": False}

    def callback():
        called["value"] = True
        return "executed"

    result = middleware.intercept(
        action={"type": "purchase", "entity": "req1"},
        context=["RequiresSecurityReview(req1)", "PurchaseBlocked(req1)"],
        policy_id="procurement-policy",
        callback=callback,
    )
    assert result["decision"]["outcome"] == "DENY"
    assert called["value"] is False


def test_middleware_runs_callback_on_allow():
    middleware = AgentGovernanceMiddleware()
    result = middleware.intercept(
        action={"type": "refund", "entity": "order2", "amount": 200},
        context=[
            "WithinRefundWindow(order2)",
            "UnderLimit(order2)",
            "ProductReturned(order2)",
            "NotAlreadyRefunded(order2)",
            "NotFinalSale(order2)",
        ],
        policy_id="refund-policy",
        callback=lambda: "refund-processed",
    )
    assert result["decision"]["outcome"] == "ALLOW"
    assert result["result"] == "refund-processed"


def test_middleware_nl_context_extraction():
    middleware = AgentGovernanceMiddleware()
    result = middleware.validate_action(
        action={"type": "refund", "entity": "order2", "amount": 200},
        context=[
            "WithinRefundWindow(order2)",
            "UnderLimit(order2)",
            "ProductReturned(order2)",
            "NotAlreadyRefunded(order2)",
            "NotFinalSale(order2)",
        ],
        policy_id="refund-policy",
        nl_context="order2 is within refund window",
    )
    assert result.outcome in ("ALLOW", "DENY", "ESCALATE")


def test_audit_store_persists(tmp_path: Path):
    path = tmp_path / "audit.json"
    store = AuditStore(persist_path=str(path))
    from axiomai.governance import Decision

    store.record(
        Decision(outcome="DENY", explanation="blocked", violated_rules=["r1"]),
        action={"type": "refund"},
        policy_id="refund-policy",
    )
    assert path.exists()

    store2 = AuditStore(persist_path=str(path))
    entries = store2.query(policy_id="refund-policy")
    assert len(entries) == 1
    assert entries[0]["outcome"] == "DENY"


def test_api_list_policies():
    client = TestClient(app)
    r = client.get("/policies")
    assert r.status_code == 200
    assert len(r.json()["policies"]) >= 4


def test_api_governance_with_policy_id():
    client = TestClient(app)
    r = client.post(
        "/governance/validate",
        json={
            "action": {"type": "purchase", "entity": "req1", "amount": 45000},
            "context": PROCUREMENT_CONTEXT,
            "policy_id": "procurement-policy",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["policy_id"] == "procurement-policy"
    assert "escalation_queue" in data


def test_api_extract_endpoint():
    client = TestClient(app)
    client.post("/reset")
    r = client.post("/extract", json={"text": "Socrates is a human. All humans are mortal.", "load": True})
    assert r.status_code == 200
    data = r.json()
    assert len(data["facts"]) >= 1
    assert data["loaded"] is True
