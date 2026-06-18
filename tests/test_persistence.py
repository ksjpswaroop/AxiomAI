"""P2-11–P2-13: Persistence tests."""

from __future__ import annotations

from pathlib import Path

from axiomai import Reasoner


def test_persist_facts_and_rules(tmp_path: Path):
    db_url = f"sqlite:///{tmp_path}/axiomai.db"
    r1 = Reasoner(persist=db_url)
    r1.add_fact("Human(Socrates)")
    r1.add_rule("IF Human(x) THEN Mortal(x)")

    r2 = Reasoner(persist=db_url)
    assert r2.kb.query_fact("Human(Socrates)")
    assert len(r2.list_rules()) == 1


def test_persist_survives_query(tmp_path: Path):
    db_url = f"sqlite:///{tmp_path}/test.db"
    r1 = Reasoner(persist=db_url)
    r1.load_socrates()
    r1.ask("Mortal(Socrates)")

    r2 = Reasoner(persist=db_url)
    result = r2.ask("Mortal(Socrates)")
    assert result.result == "PROVED"


def test_in_memory_default_no_persist(tmp_path: Path):
    r = Reasoner()
    r.add_fact("Human(Socrates)")
    assert r.kb.query_fact("Human(Socrates)")
