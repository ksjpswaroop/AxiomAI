"""P1-11–P1-13: Reasoner facade tests."""

from __future__ import annotations

from axiomai import Reasoner


def test_extract_adds_facts_and_rules(reasoner):
    result = reasoner.extract("Socrates is a human. All humans are mortal.")
    assert len(result["facts"]) >= 1
    assert len(result["rules"]) >= 1
    assert len(reasoner.list_facts()) >= 1
    assert len(reasoner.list_rules()) >= 1


def test_auto_mode_proves_socrates(socrates_kb):
    result = socrates_kb.ask("Mortal(Socrates)", mode="auto")
    assert result.result == "PROVED"
    assert result.reasoning_mode in ("backward_chaining", "resolution")


def test_auto_mode_uses_forward_for_fact_only_kb(reasoner):
    reasoner.add_fact("Human(Socrates)")
    reasoner.add_fact("Human(Plato)")
    reasoner.add_rule("IF Human(x) THEN Mortal(x)")
    result = reasoner.ask("Mortal(Socrates)", mode="auto")
    assert result.result == "PROVED"


def test_run_hash_is_deterministic(socrates_kb):
    r1 = socrates_kb.ask("Mortal(Socrates)")
    h1 = socrates_kb.last_run_hash()
    r2 = socrates_kb.ask("Mortal(Socrates)")
    h2 = socrates_kb.last_run_hash()
    assert r1.result == r2.result
    assert h1 == h2
    assert len(h1) == 16


def test_or_rule_backward_chaining(reasoner):
    reasoner.add_fact("Rational(Socrates)")
    reasoner.add_rule("IF Human(x) OR Rational(x) THEN Person(x)")
    result = reasoner.ask("Person(Socrates)")
    assert result.result == "PROVED"
