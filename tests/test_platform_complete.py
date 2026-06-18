"""Platform completeness verification — all items formerly 'Not Implemented'."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from apps.case_studies.registry import CASE_STUDY_CATALOG, run_case_study
from axiomai import AgentGovernanceMiddleware, PolicyRegistry, Reasoner
from axiomai.reasoner.api.main import app
from axiomai.reasoner.engines.resolution import ResolutionEngine
from axiomai.reasoner.integrations.llm_client import MockLLMClient
from axiomai.reasoner.kb.persistence import PersistentKnowledgeBase


# ── 1. Resolution (full) ─────────────────────────────────────────────────────


def test_resolution_full_engine_has_sos_and_resolve_all():
    assert hasattr(ResolutionEngine, "_resolve_all")
    assert hasattr(ResolutionEngine, "_add_clause")


def test_resolution_proves_socrates_without_z3(monkeypatch):
    r = Reasoner()
    r.load_socrates()

    def no_z3(_self, _query):
        return False

    monkeypatch.setattr(ResolutionEngine, "_z3_prove", no_z3)
    result = r.ask("Mortal(Socrates)", mode="resolution")
    assert result.result == "PROVED"


# ── 2. Persistent storage ────────────────────────────────────────────────────


def test_persistent_storage_full(tmp_path: Path):
    url = f"sqlite:///{tmp_path}/verify.db"
    r1 = Reasoner(persist=url)
    r1.load_socrates()
    r1.ask("Mortal(Socrates)")

    assert isinstance(r1.kb, PersistentKnowledgeBase)
    assert len(r1.list_proofs()) >= 1
    assert len(r1.list_inference_runs()) >= 1

    r2 = Reasoner(persist=url)
    assert r2.kb.query_fact("Human(Socrates)")
    assert len(r2.list_proofs()) >= 1


# ── 3. Test suite ────────────────────────────────────────────────────────────


def test_test_suite_modules_exist():
    tests_dir = Path(__file__).resolve().parent
    required = [
        "test_models.py",
        "test_llm_extractor.py",
        "test_resolution_full.py",
        "test_persistence_full.py",
        "test_governance_middleware.py",
        "test_connectors.py",
        "test_p6_case_studies.py",
    ]
    for name in required:
        assert (tests_dir / name).exists(), f"Missing test module: {name}"


# ── 4. LLM integration on Reasoner facade ────────────────────────────────────


def test_llm_facade_extract_and_api():
    mock = MockLLMClient(
        responses={
            "human": {
                "facts": [{"predicate": "Human(Socrates)", "source": "llm"}],
                "rules": [],
            }
        }
    )
    r = Reasoner(llm_client=mock)
    result = r.extract("Socrates is human")
    assert len(result["facts"]) == 1
    assert "stats" in result

    client = TestClient(app)
    client.post("/reset")
    resp = client.post("/extract", json={"text": "Socrates is a human.", "load": True})
    assert resp.status_code == 200
    assert len(resp.json()["facts"]) >= 1


# ── 5. Agent governance framework ────────────────────────────────────────────


def test_governance_framework_complete():
    registry = PolicyRegistry.default()
    assert len(registry.list_policies()) >= 4

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
    )
    assert result["decision"]["outcome"] == "ALLOW"
    assert "escalation_queue" in result

    client = TestClient(app)
    policies = client.get("/policies")
    assert policies.status_code == 200
    assert len(policies.json()["policies"]) >= 4


# ── 6. Connectors ────────────────────────────────────────────────────────────


def test_connectors_sdk_and_api():
    from axiomai.connectors import (
        AWSConfigConnector,
        AzureADConnector,
        FileConnector,
        SIEMConnector,
        WebhookConnector,
    )

    assert len(WebhookConnector().fetch_evidence()) == 0
    assert len(AzureADConnector().fetch_evidence()) > 0
    assert len(SIEMConnector().fetch_evidence()) > 0
    assert len(AWSConfigConnector().fetch_evidence()) > 0

    client = TestClient(app)
    ingest = client.post(
        "/connectors/webhook/facts",
        json={"facts": ["Human(Socrates)", "Mortal(Socrates)"]},
    )
    assert ingest.status_code == 200
    assert ingest.json()["received"] == 2

    listed = client.get("/connectors/webhook/facts")
    assert listed.status_code == 200
    assert listed.json()["count"] == 2


def test_file_connector_via_api(tmp_path: Path):
    path = tmp_path / "facts.json"
    path.write_text('{"facts": ["Human(Plato)", "Rational(Plato)"]}')
    client = TestClient(app)
    resp = client.post("/connectors/file/ingest", json={"path": str(path)})
    assert resp.status_code == 200
    assert resp.json()["count"] == 2


# ── 7. Web UI ────────────────────────────────────────────────────────────────


def test_web_ui_console_exists():
    root = Path(__file__).resolve().parents[1]
    console = root / "apps" / "console"
    assert (console / "app.py").exists()
    for page in (
        "1_Case_Study_Gallery.py",
        "2_Brainstorming.py",
        "3_Feature_Guides.py",
        "4_Knowledge_Base.py",
        "5_Governance.py",
        "6_Audit_Trail.py",
    ):
        assert (console / "pages" / page).exists()


def test_docker_compose_stack_defined():
    compose = Path(__file__).resolve().parents[1] / "docker-compose.yml"
    text = compose.read_text(encoding="utf-8")
    assert "api:" in text
    assert "ui:" in text
    assert "streamlit" in text


# ── 8. All 18 case study applications ────────────────────────────────────────


@pytest.mark.parametrize("case_id", [c["id"] for c in CASE_STUDY_CATALOG])
def test_all_18_case_studies_registered(case_id: str):
    assert len(CASE_STUDY_CATALOG) == 18
    result = run_case_study(case_id)
    assert result.get("case_study_id") == case_id or case_id.replace("-", "") in str(result)


# ── 9. CI/CD pipeline ────────────────────────────────────────────────────────


def test_cicd_workflow_exists():
    workflow = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml"
    assert workflow.exists()
    text = workflow.read_text(encoding="utf-8")
    assert "pytest" in text
    assert "ruff" in text
    assert "cov" in text


def test_dockerfile_exists():
    dockerfile = Path(__file__).resolve().parents[1] / "Dockerfile"
    assert dockerfile.exists()
    assert "axiomai-server" in dockerfile.read_text(encoding="utf-8") or "pip install" in dockerfile.read_text(encoding="utf-8")
