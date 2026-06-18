"""P2-03: Backward chaining tests."""

from __future__ import annotations


def test_socrates_backward(socrates_kb):
    result = socrates_kb.ask("Mortal(Socrates)", mode="backward")
    assert result.result == "PROVED"


def test_socrates_plato(socrates_kb):
    result = socrates_kb.ask("Mortal(Plato)", mode="backward")
    assert result.result == "PROVED"


def test_unknown_without_rule(reasoner):
    reasoner.add_fact("Human(Socrates)")
    result = reasoner.ask("Mortal(Socrates)", mode="backward")
    assert result.result == "UNKNOWN"


def test_direct_fact_proved(reasoner):
    reasoner.add_fact("Mortal(Socrates)")
    result = reasoner.ask("Mortal(Socrates)", mode="backward")
    assert result.result == "PROVED"


def test_multi_rule_chain(reasoner):
    reasoner.add_fact("Human(Socrates)")
    reasoner.add_rule("IF Human(x) THEN Mortal(x)")
    reasoner.add_rule("IF Mortal(x) THEN Dead(x)")
    result = reasoner.ask("Dead(Socrates)", mode="backward")
    assert result.result == "PROVED"


def test_and_rule_requires_all_antecedents(reasoner):
    reasoner.add_fact("Human(Socrates)")
    reasoner.add_rule("IF Human(x) AND Rational(x) THEN Person(x)")
    result = reasoner.ask("Person(Socrates)", mode="backward")
    assert result.result == "UNKNOWN"


def test_and_rule_with_both_facts(reasoner):
    reasoner.add_fact("Human(Socrates)")
    reasoner.add_fact("Rational(Socrates)")
    reasoner.add_rule("IF Human(x) AND Rational(x) THEN Person(x)")
    result = reasoner.ask("Person(Socrates)", mode="backward")
    assert result.result == "PROVED"


def test_or_rule_single_antecedent(reasoner):
    reasoner.add_fact("Rational(Socrates)")
    reasoner.add_rule("IF Human(x) OR Rational(x) THEN Person(x)")
    result = reasoner.ask("Person(Socrates)", mode="backward")
    assert result.result == "PROVED"


def test_proof_has_steps(socrates_kb):
    result = socrates_kb.ask("Mortal(Socrates)", mode="backward")
    assert len(result.proof.steps) >= 1
