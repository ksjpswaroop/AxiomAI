"""P5a: Working application API extension tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from axiomai.reasoner.api.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_state():
    client.post("/reset")
    client.delete("/audit")
    yield
    client.post("/reset")
    client.delete("/audit")


def test_list_case_studies():
    r = client.get("/case-studies")
    assert r.status_code == 200
    data = r.json()
    ids = {item["id"] for item in data}
    assert "cs-07" in ids
    assert "cs-02" in ids
    assert "cs-03" in ids
    assert len(data) == 18


def test_run_case_study_cs07():
    r = client.post("/case-studies/cs-07/run")
    assert r.status_code == 200
    body = r.json()
    assert body["case_study_id"] == "cs-07"
    assert body["confirmed"] is True
    assert "root_cause" in body
    assert "mttr" in body


def test_run_case_study_cs02():
    r = client.post("/case-studies/cs-02/run")
    assert r.status_code == 200
    body = r.json()
    assert body["case_study_id"] == "cs-02"
    assert body["fail_count"] >= 1
    assert len(body["controls"]) >= 8


def test_run_case_study_cs03():
    r = client.post("/case-studies/cs-03/run")
    assert r.status_code == 200
    body = r.json()
    assert body["case_study_id"] == "cs-03"
    assert body["outcome"] == "DENY"
    assert body["decision"]["proof"] is not None


def test_run_case_study_cs01():
    r = client.post("/case-studies/cs-01/run")
    assert r.status_code == 200
    body = r.json()
    assert body["case_study_id"] == "cs-01"
    assert body["outcome"] in ("ROOT_CAUSE_FOUND", "PROVED")


def test_run_unknown_case_study():
    r = client.post("/case-studies/cs-99/run")
    assert r.status_code == 404


def test_governance_validate_deny():
    r = client.post(
        "/governance/validate",
        json={
            "action": {"type": "refund", "entity": "order1", "amount": 350},
            "context": [
                "OutsideRefundWindow(order1)",
                "UnderLimit(order1)",
                "NotProductReturned(order1)",
                "NotAlreadyRefunded(order1)",
                "NotFinalSale(order1)",
            ],
            "case_study": "cs-03",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["outcome"] == "DENY"
    assert body["proof"] is not None


def test_governance_validate_allow():
    r = client.post(
        "/governance/validate",
        json={
            "action": {"type": "refund", "entity": "order2", "amount": 200},
            "context": [
                "WithinRefundWindow(order2)",
                "UnderLimit(order2)",
                "ProductReturned(order2)",
                "NotAlreadyRefunded(order2)",
                "NotFinalSale(order2)",
            ],
        },
    )
    assert r.status_code == 200
    assert r.json()["outcome"] == "ALLOW"


def test_audit_log_after_governance():
    client.post(
        "/governance/validate",
        json={
            "action": {"type": "refund", "entity": "order1", "amount": 350},
            "context": ["OutsideRefundWindow(order1)", "NotProductReturned(order1)"],
            "case_study": "cs-03",
        },
    )
    r = client.get("/audit")
    assert r.status_code == 200
    entries = r.json()["entries"]
    assert len(entries) >= 1
    assert entries[0]["outcome"] == "DENY"


def test_audit_filter_by_outcome():
    client.post(
        "/governance/validate",
        json={
            "action": {"type": "refund", "entity": "order2", "amount": 200},
            "context": [
                "WithinRefundWindow(order2)",
                "UnderLimit(order2)",
                "ProductReturned(order2)",
                "NotAlreadyRefunded(order2)",
                "NotFinalSale(order2)",
            ],
        },
    )
    client.post(
        "/governance/validate",
        json={
            "action": {"type": "refund", "entity": "order1", "amount": 350},
            "context": ["OutsideRefundWindow(order1)"],
        },
    )
    r = client.get("/audit", params={"outcome": "DENY"})
    assert r.status_code == 200
    assert all(e["outcome"] == "DENY" for e in r.json()["entries"])


def test_openapi_includes_p5_routes():
    r = client.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json()["paths"]
    assert "/case-studies" in paths
    assert "/governance/validate" in paths
    assert "/audit" in paths
    assert "/brainstorm" in paths


def test_list_case_study_scenarios():
    r = client.get("/case-studies/cs-07/scenarios")
    assert r.status_code == 200
    body = r.json()
    assert body["case_study_id"] == "cs-07"
    assert len(body["scenarios"]) >= 1
    assert any(s["id"] == "default" for s in body["scenarios"])


def test_run_case_study_with_scenario():
    r = client.post("/case-studies/cs-03/run", json={"scenario": "default"})
    assert r.status_code == 200
    assert r.json()["case_study_id"] == "cs-03"


@pytest.mark.parametrize("case_id", [f"cs-{i:02d}" for i in range(1, 19)])
def test_run_all_case_studies(case_id):
    r = client.post(f"/case-studies/{case_id}/run", json={"scenario": "default"})
    assert r.status_code == 200
    body = r.json()
    assert body["case_study_id"] == case_id


def test_brainstorm_in_scope():
    r = client.post(
        "/brainstorm",
        json={
            "description": (
                "Our support AI keeps issuing refunds outside the return window. "
                "We need governance with proof and audit trail."
            )
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["in_scope"] is True
    assert "cs-03" in body["matched_case_studies"]
    assert len(body["how_to_test"]) >= 1
    assert len(body["how_to_production"]) >= 1


def test_brainstorm_out_of_scope():
    r = client.post(
        "/brainstorm",
        json={
            "description": (
                "We need a video editing timeline with color grading, "
                "motion graphics templates, and social media export presets."
            )
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["in_scope"] is False
    assert body["out_of_scope_reason"]
