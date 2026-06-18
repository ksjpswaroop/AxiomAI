"""P1-01: CNF conversion tests."""

from __future__ import annotations

from axiomai.reasoner.core.cnf import Literal, fact_to_clause, rule_to_clauses, kb_to_clauses
from axiomai.reasoner.core.models import Fact, Rule
from axiomai.reasoner.kb.store import KnowledgeBase


def test_fact_to_unit_clause():
    fact = Fact.create("Human(Socrates)")
    clause = fact_to_clause(fact)
    assert len(clause.literals) == 1
    lit = next(iter(clause.literals))
    assert str(lit.predicate) == "Human(Socrates)"
    assert lit.negated is False


def test_rule_to_single_clause():
    rule = Rule.parse("IF Human(x) THEN Mortal(x)")
    clauses = rule_to_clauses(rule)
    assert len(clauses) == 1
    lits = {str(l) for l in clauses[0].literals}
    assert "Human(x)" in lits or "¬Human(x)" in lits
    assert "Mortal(x)" in lits or "¬Mortal(x)" in lits


def test_or_rule_produces_multiple_clauses():
    rule = Rule.parse("IF Human(x) OR Rational(x) THEN Person(x)")
    clauses = rule_to_clauses(rule)
    assert len(clauses) == 2


def test_kb_to_clauses_includes_facts_and_rules():
    kb = KnowledgeBase()
    kb.add_fact(Fact.create("Human(Socrates)"))
    kb.add_rule(Rule.parse("IF Human(x) THEN Mortal(x)"))
    clauses = kb_to_clauses(kb)
    assert len(clauses) >= 2


def test_literal_complement():
    lit = Literal.from_string("Human(Socrates)")
    assert str(lit.complement()) == "¬Human(Socrates)"
