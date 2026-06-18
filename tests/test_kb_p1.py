"""P1-07–P1-10: Knowledge base extension tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from axiomai import Reasoner
from axiomai.reasoner.core.models import Fact, Rule
from axiomai.reasoner.kb.store import KnowledgeBase


def test_expired_fact_excluded_from_query():
    kb = KnowledgeBase()
    past = datetime.now(timezone.utc) - timedelta(days=10)
    expired = Fact.create(
        "Human(Socrates)",
        valid_from=past - timedelta(days=1),
        valid_to=past,
    )
    kb.add_fact(expired)
    assert kb.query_fact("Human(Socrates)") is False
    assert len(kb.list_active_facts()) == 0


def test_active_fact_visible():
    kb = KnowledgeBase()
    kb.add_fact(Fact.create("Human(Socrates)"))
    assert kb.query_fact("Human(Socrates)") is True
    assert len(kb.list_active_facts()) == 1


def test_derived_contradiction_detected():
    kb = KnowledgeBase()
    kb.add_fact(Fact.create("Mortal(Socrates)"))
    kb.add_fact(Fact.create("¬Mortal(Socrates)"))
    reports = kb.detect_contradictions()
    assert len(reports) >= 1


def test_retraction_cascades_to_derived_facts():
    kb = KnowledgeBase()
    parent = kb.add_fact(Fact.create("Human(Socrates)"))
    derived = Fact.create("Mortal(Socrates)", source="rule:r1")
    kb.add_derived_fact(derived, rule_ids=["r1"], source_fact_keys=["Human(Socrates)"])
    assert kb.query_fact("Mortal(Socrates)")
    kb.retract_fact("Human(Socrates)")
    assert not kb.query_fact("Mortal(Socrates)")


def test_snapshot_returns_stable_id():
    kb = KnowledgeBase()
    kb.add_fact(Fact.create("Human(Socrates)"))
    kb.add_rule(Rule.parse("IF Human(x) THEN Mortal(x)"))
    snap1 = kb.snapshot()
    snap2 = kb.snapshot()
    assert snap1 == snap2
    assert len(snap1) == 16


def test_namespace_isolation():
    r1 = Reasoner(namespace="medical")
    r2 = Reasoner(namespace="legal")
    r1.add_fact("medical:Patient(John)")
    r2.add_fact("legal:Client(John)")
    assert r1.kb.query_fact("medical:Patient(John)")
    assert not r1.kb.query_fact("legal:Client(John)")
