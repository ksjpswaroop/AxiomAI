"""Full persistence tests — proof/run queries, contradictions, API."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from axiomai import Reasoner


@pytest.fixture
def persist_url(tmp_path: Path) -> str:
    return f"sqlite:///{tmp_path}/full.db"


def test_list_proofs_after_query(persist_url: str):
    r = Reasoner(persist= persist_url)
    r.load_socrates()
    r.ask("Mortal(Socrates)")

    proofs = r.list_proofs()
    assert len(proofs) >= 1
    assert proofs[0]["query"] == "Mortal(Socrates)"
    assert proofs[0]["result"] == "PROVED"
    assert "proof_json" in proofs[0]

    fetched = r.get_proof(proofs[0]["id"])
    assert fetched is not None
    assert fetched["id"] == proofs[0]["id"]


def test_list_inference_runs(persist_url: str):
    r = Reasoner(persist=persist_url)
    r.add_fact("Human(Socrates)")
    r.add_rule("IF Human(x) THEN Mortal(x)")
    r.ask("Mortal(Socrates)", mode="backward")

    runs = r.list_inference_runs()
    assert len(runs) >= 1
    assert runs[0]["mode"] == "backward_chaining"
    assert runs[0]["duration_ms"] >= 0
    assert runs[0]["run_hash"]

    run = r.get_inference_run(runs[0]["id"])
    assert run is not None
    assert run["query"] == "Mortal(Socrates)"


def test_filter_proofs_by_query(persist_url: str):
    r = Reasoner(persist=persist_url)
    r.load_socrates()
    r.ask("Mortal(Socrates)")
    r.ask("Mortal(Plato)")

    socrates_proofs = r.list_proofs(query="Mortal(Socrates)")
    assert len(socrates_proofs) >= 1
    assert all(p["query"] == "Mortal(Socrates)" for p in socrates_proofs)


def test_contradiction_persistence(persist_url: str):
    r = Reasoner(persist=persist_url)
    r.add_fact("Human(Socrates)")
    r.add_fact("¬Human(Socrates)")

    reports = r.check_consistency()
    assert len(reports) == 1

    history = r.list_persisted_contradictions()
    assert len(history) >= 1
    assert history[0]["fact1"] == "Human(Socrates)" or history[0]["fact2"] == "Human(Socrates)"


def test_in_memory_returns_empty_lists():
    r = Reasoner()
    r.add_fact("Human(Socrates)")
    assert r.list_proofs() == []
    assert r.list_inference_runs() == []
    assert r.get_proof("nope") is None
    assert r.list_persisted_contradictions() == []


def test_persistence_api_endpoints(persist_url: str):
    from fastapi.testclient import TestClient

    import axiomai.reasoner.api.main as api_main
    from axiomai.reasoner.api.main import app

    r = Reasoner(persist=persist_url)
    r.load_socrates()
    r.ask("Mortal(Socrates)")

    saved = api_main.reasoner
    api_main.reasoner = r
    try:
        client = TestClient(app)
        proofs_resp = client.get("/proofs")
        assert proofs_resp.status_code == 200
        data = proofs_resp.json()
        assert data["count"] >= 1

        proof_id = data["proofs"][0]["id"]
        single = client.get(f"/proofs/{proof_id}")
        assert single.status_code == 200
        json.loads(single.json()["proof_json"])

        runs_resp = client.get("/inference-runs")
        assert runs_resp.status_code == 200
        assert runs_resp.json()["count"] >= 1

        r2 = Reasoner(persist=persist_url)
        r2.add_fact("Human(Socrates)")
        r2.add_fact("¬Human(Socrates)")
        api_main.reasoner = r2
        client.get("/contradictions")
        history = client.get("/contradictions/history")
        assert history.status_code == 200
        assert history.json()["count"] >= 1
    finally:
        api_main.reasoner = saved
