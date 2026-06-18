"""Full resolution engine tests — SOS, subsumption, multi-hop, negated facts."""

from __future__ import annotations

from axiomai import Reasoner
from axiomai.reasoner.core.cnf import (
    Clause,
    Literal,
    clause_subsumes,
    is_tautology,
    simplify_clause,
)
from axiomai.reasoner.core.unification import UnificationEngine
from axiomai.reasoner.engines.resolution import ResolutionEngine
from axiomai.reasoner.explain.proof import StepType


def test_cnf_simplify_drops_tautology():
    uni = UnificationEngine()
    clause = Clause([
        Literal.from_string("Human(x)"),
        Literal.from_string("¬Mortal(Socrates)"),
    ])
    assert is_tautology(clause, uni) is False
    taut = Clause([
        Literal.from_string("Human(Socrates)"),
        Literal.from_string("¬Human(Socrates)"),
    ])
    assert is_tautology(taut, uni) is True
    assert simplify_clause(taut, uni) is None


def test_clause_subsumption_ground():
    uni = UnificationEngine()
    sub = Clause([Literal.from_string("Human(Socrates)")])
    sup = Clause([
        Literal.from_string("Human(Socrates)"),
        Literal.from_string("Mortal(Socrates)"),
    ])
    assert clause_subsumes(sub, sup, uni) is True
    assert clause_subsumes(sup, sub, uni) is False


def test_resolution_multi_hop_chain():
    """A → B → C requires multiple resolution steps."""
    r = Reasoner()
    r.add_fact("A(x)")
    r.add_rule("IF A(x) THEN B(x)")
    r.add_rule("IF B(x) THEN C(x)")
    result = r.ask("C(Socrates)", mode="resolution")
    assert result.result == "PROVED"


def test_resolution_with_negated_fact():
    r = Reasoner()
    r.add_fact("¬Mortal(Socrates)")
    result = r.ask("Mortal(Socrates)", mode="resolution")
    assert result.result == "DISPROVED"


def test_resolution_sos_proves_without_z3(monkeypatch):
    """Socrates proof via pure resolution (Z3 disabled)."""
    r = Reasoner()
    r.load_socrates()

    def no_z3(_self, _query):
        return False

    monkeypatch.setattr(ResolutionEngine, "_z3_prove", no_z3)
    result = r.ask("Mortal(Socrates)", mode="resolution")
    assert result.result == "PROVED"
    step_types = {s.type for s in result.proof.steps}
    assert StepType.ASSUME in step_types
    assert StepType.RESOLVE in step_types or StepType.CONFLICT in step_types


def test_resolution_disjunction_rule():
    r = Reasoner()
    r.add_fact("Red(apple)")
    r.add_rule("IF Red(x) OR Green(x) THEN Edible(x)")
    result = r.ask("Edible(apple)", mode="resolution")
    assert result.result == "PROVED"


def test_resolution_subsumption_prunes_redundant():
    uni = UnificationEngine()
    sub = Clause([Literal.from_string("P(a)")])
    sup = Clause([
        Literal.from_string("P(a)"),
        Literal.from_string("Q(b)"),
    ])
    assert clause_subsumes(sub, sup, uni) is True
    assert clause_subsumes(sup, sub, uni) is False
