"""P1-02–P1-04: Resolution engine tests."""

from __future__ import annotations

from axiomai.reasoner.core.cnf import Clause, Literal
from axiomai.reasoner.core.unification import UnificationEngine
from axiomai.reasoner.engines.resolution import ResolutionEngine
from axiomai.reasoner.explain.proof import StepType
from axiomai.reasoner.kb.store import KnowledgeBase


def test_resolve_pair_unifies_complementary_literals():
    kb = KnowledgeBase()
    engine = ResolutionEngine(kb, UnificationEngine())
    c1 = Clause([Literal.from_string("Human(Socrates)")])
    c2 = Clause([Literal.from_string("¬Human(x)")])
    result = engine._resolve_pair(c1, c2)
    assert result is None  # empty resolvent = contradiction


def test_resolve_pair_produces_nonempty_resolvent():
    kb = KnowledgeBase()
    engine = ResolutionEngine(kb, UnificationEngine())
    c1 = Clause([
        Literal.from_string("Human(Socrates)"),
        Literal.from_string("Mortal(Socrates)"),
    ])
    c2 = Clause([
        Literal.from_string("¬Human(x)"),
        Literal.from_string("Rational(Socrates)"),
    ])
    result = engine._resolve_pair(c1, c2)
    assert result is not None and result is not False
    lits = {str(lit) for lit in result.literals}
    assert "Mortal(Socrates)" in lits
    assert "Rational(Socrates)" in lits


def test_socrates_resolution_proved(socrates_kb):
    result = socrates_kb.ask("Mortal(Socrates)", mode="resolution")
    assert result.result == "PROVED"


def test_resolution_proof_has_steps(socrates_kb):
    result = socrates_kb.ask("Mortal(Socrates)", mode="resolution")
    step_types = {s.type for s in result.proof.steps}
    assert StepType.ASSUME in step_types
    assert StepType.RESOLVE in step_types or StepType.CONFLICT in step_types


def test_resolution_disproved_without_support(reasoner):
    reasoner.add_fact("Human(Socrates)")
    result = reasoner.ask("Mortal(Socrates)", mode="resolution")
    assert result.result == "DISPROVED"
