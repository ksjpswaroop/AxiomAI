"""P2-02: Unification engine tests."""

from __future__ import annotations

import pytest

from axiomai.reasoner.core.models import Predicate
from axiomai.reasoner.core.unification import UnificationEngine


@pytest.fixture
def uni() -> UnificationEngine:
    return UnificationEngine()


def test_unify_identical_constants(uni):
    p1 = Predicate.parse("Human(Socrates)")
    p2 = Predicate.parse("Human(Socrates)")
    result = uni.unify(p1, p2)
    assert result.success


def test_unify_variable_with_constant(uni):
    p1 = Predicate.parse("Human(x)")
    p2 = Predicate.parse("Human(Socrates)")
    result = uni.unify(p1, p2)
    assert result.success
    assert result.substitution.get("x") == "Socrates"


def test_unify_two_variables(uni):
    p1 = Predicate.parse("Loves(x, y)")
    p2 = Predicate.parse("Loves(Socrates, Plato)")
    result = uni.unify(p1, p2)
    assert result.success
    assert result.substitution.get("x") == "Socrates"
    assert result.substitution.get("y") == "Plato"


def test_unify_relation_mismatch_fails(uni):
    p1 = Predicate.parse("Human(Socrates)")
    p2 = Predicate.parse("Mortal(Socrates)")
    result = uni.unify(p1, p2)
    assert not result.success


def test_unify_arity_mismatch_fails(uni):
    p1 = Predicate.parse("Parent(John)")
    p2 = Predicate.parse("Parent(John, Mary)")
    result = uni.unify(p1, p2)
    assert not result.success


def test_unify_constant_conflict_fails(uni):
    p1 = Predicate.parse("Human(Socrates)")
    p2 = Predicate.parse("Human(Plato)")
    result = uni.unify(p1, p2)
    assert not result.success


def test_unify_same_variable_names(uni):
    p1 = Predicate.parse("Human(x)")
    p2 = Predicate.parse("Human(x)")
    result = uni.unify(p1, p2)
    assert result.success


def test_match_one_way(uni):
    pattern = Predicate.parse("Human(x)")
    target = Predicate.parse("Human(Socrates)")
    subst = uni.match(pattern, target)
    assert subst is not None
    assert subst.get("x") == "Socrates"


def test_match_fails_wrong_constant(uni):
    pattern = Predicate.parse("Human(Socrates)")
    target = Predicate.parse("Human(Plato)")
    subst = uni.match(pattern, target)
    assert subst is None


def test_unify_multi_arg(uni):
    p1 = Predicate.parse("Parent(John, x)")
    p2 = Predicate.parse("Parent(John, Mary)")
    result = uni.unify(p1, p2)
    assert result.success
    assert result.substitution.get("x") == "Mary"


def test_stats_increment(uni):
    uni.unify(Predicate.parse("Human(x)"), Predicate.parse("Human(Socrates)"))
    stats = uni.stats()
    assert stats["unifications"] >= 1
