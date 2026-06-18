"""P2-09: FastAPI endpoint tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from axiomai.reasoner.api.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_kb():
    client.post("/reset")
    yield
    client.post("/reset")


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_add_and_list_facts():
    r = client.post("/facts", json={"predicate": "Human(Socrates)"})
    assert r.status_code == 200
    r = client.get("/facts")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_add_and_list_rules():
    r = client.post("/rules", json={"rule_str": "IF Human(x) THEN Mortal(x)"})
    assert r.status_code == 200
    r = client.get("/rules")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_query_socrates():
    client.post("/load/socrates")
    r = client.post("/query", json={"query": "Mortal(Socrates)"})
    assert r.status_code == 200
    assert r.json()["result"] == "PROVED"


def test_forward_chain():
    client.post("/facts", json={"predicate": "Human(Socrates)"})
    client.post("/rules", json={"rule_str": "IF Human(x) THEN Mortal(x)"})
    r = client.post("/forward")
    assert r.status_code == 200
    assert "Mortal(Socrates)" in r.json()["new_facts"]


def test_resolution():
    client.post("/load/socrates")
    r = client.post("/resolution", json={"query": "Mortal(Socrates)"})
    assert r.status_code == 200
    assert r.json()["provable"] is True


def test_contradictions():
    r = client.get("/contradictions")
    assert r.status_code == 200
    assert r.json()["consistent"] is True


def test_sudoku():
    r = client.post("/sudoku")
    assert r.status_code == 200
    assert r.json()["solution"] is not None


def test_planning():
    client.post("/planning/action", json={
        "name": "move",
        "preconditions": ["at(A)"],
        "add_effects": ["at(B)"],
        "del_effects": ["at(A)"],
    })
    r = client.post("/planning/plan", json={
        "initial_state": ["at(A)"],
        "goal": ["at(B)"],
    })
    assert r.status_code == 200
    assert r.json()["found"] is True


def test_causal():
    client.post("/causal", json={"cause": "A", "effect": "B"})
    r = client.get("/causal/root-causes/B")
    assert r.status_code == 200


def test_stats():
    r = client.get("/stats")
    assert r.status_code == 200
    assert "fingerprint" in r.json()


def test_reset():
    client.post("/facts", json={"predicate": "Human(Socrates)"})
    r = client.post("/reset")
    assert r.status_code == 200
    r = client.get("/facts")
    assert len(r.json()) == 0
