"""P3b: Connector SDK tests."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from axiomai.connectors import (
    AWSConfigConnector,
    AzureADConnector,
    Connector,
    FileConnector,
    SIEMConnector,
    WebhookConnector,
)
from axiomai.reasoner.core.models import Fact


def test_connector_protocol():
    assert hasattr(Connector, "fetch_evidence")
    assert hasattr(Connector, "health")


def test_file_connector_json(tmp_path: Path):
    data = {"facts": ["Human(Socrates)", "Mortal(Plato)"]}
    path = tmp_path / "facts.json"
    path.write_text(json.dumps(data))
    connector = FileConnector(path)
    assert connector.health() is True
    facts = connector.fetch_evidence()
    assert len(facts) == 2
    assert all(isinstance(f, Fact) for f in facts)
    assert str(facts[0].predicate) == "Human(Socrates)"


def test_file_connector_csv(tmp_path: Path):
    path = tmp_path / "facts.csv"
    path.write_text("predicate\nHuman(Socrates)\nMortal(Plato)\n")
    connector = FileConnector(path)
    facts = connector.fetch_evidence()
    assert len(facts) == 2
    assert str(facts[0].predicate) == "Human(Socrates)"


def test_webhook_connector_ingest_and_fetch():
    connector = WebhookConnector()
    connector.ingest({"facts": ["LoggedIn(alice)", "Admin(alice)"]})
    facts = connector.fetch_evidence()
    assert len(facts) == 2
    assert connector.health() is True


def test_webhook_connector_fastapi_route():
    connector = WebhookConnector()
    app = FastAPI()
    app.include_router(connector.as_router(), prefix="/connectors")
    client = TestClient(app)
    r = client.post(
        "/connectors/webhook/facts",
        json={"facts": ["Event(login_failed)", "Source(ip_10_0_0_5)"]},
    )
    assert r.status_code == 200
    facts = connector.fetch_evidence()
    assert len(facts) == 2


def test_mock_azure_ad_connector():
    connector = AzureADConnector()
    assert connector.health() is True
    facts = connector.fetch_evidence()
    assert len(facts) >= 3
    relations = {str(f.predicate).split("(")[0] for f in facts}
    assert "User" in relations or "MfaEnabled" in relations


def test_mock_aws_connector():
    connector = AWSConfigConnector()
    facts = connector.fetch_evidence()
    assert len(facts) >= 3
    assert connector.health() is True


def test_mock_siem_connector():
    connector = SIEMConnector()
    facts = connector.fetch_evidence()
    assert len(facts) >= 3
    assert connector.health() is True


def test_file_connector_loads_into_reasoner(tmp_path: Path):
    from axiomai import Reasoner

    path = tmp_path / "facts.json"
    path.write_text(json.dumps({"facts": ["Human(Socrates)"]}))
    r = Reasoner()
    for fact in FileConnector(path).fetch_evidence():
        r.add_fact(str(fact.predicate), source=fact.source)
    result = r.ask("Human(Socrates)")
    assert result.result == "PROVED"
