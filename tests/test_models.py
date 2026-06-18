"""Core model tests."""

from __future__ import annotations

import pytest

from axiomai.reasoner.core.models import Fact, Predicate, Rule, Term, TermType


def test_predicate_parse_simple():
    p = Predicate.parse("Human(Socrates)")
    assert p.relation == "Human"
    assert str(p.terms[0]) == "Socrates"


def test_predicate_parse_variable():
    p = Predicate.parse("Parent(x, y)")
    assert p.terms[0].is_variable()
    assert p.terms[1].is_variable()


def test_predicate_namespace():
    p = Predicate.parse("medical:Diagnosis(patient1, flu)")
    assert p.namespace == "medical"
    assert p.relation == "Diagnosis"


def test_predicate_substitute():
    p = Predicate.parse("Human(x)")
    sub = p.substitute({"x": "Socrates"})
    assert str(sub) == "Human(Socrates)"


def test_fact_create_negated():
    fact = Fact.create("¬Human(Socrates)")
    assert fact.metadata.get("negated") is True
    assert str(fact.predicate) == "Human(Socrates)"


def test_fact_to_dict():
    fact = Fact.create("Human(Socrates)", source="test")
    d = fact.to_dict()
    assert "predicate" in d
    assert d["source"] == "test"


def test_rule_parse_and_str():
    rule = Rule.parse("IF Human(x) THEN Mortal(x)", priority=2)
    assert rule.consequent.relation == "Mortal"
    assert len(rule.antecedents) == 1
    assert rule.priority == 2
    assert "IF" in str(rule)


def test_rule_or_antecedent():
    rule = Rule.parse("IF Human(x) OR Rational(x) THEN Person(x)")
    assert rule.antecedent_operator == "or"
    assert len(rule.antecedents) == 2


def test_term_types():
    var = Term("x", TermType.VARIABLE)
    const = Term("Socrates", TermType.CONSTANT)
    assert var.is_variable()
    assert const.is_constant()


def test_predicate_invalid_raises():
    with pytest.raises(ValueError):
        Predicate.parse("not-valid")
