"""Narrator explanation tests."""

from __future__ import annotations

from axiomai.reasoner.explain.narrator import Narrator
from axiomai.reasoner.explain.proof import ProofStep, ProofTree, StepType


def _proved_tree() -> ProofTree:
    tree = ProofTree(query="Mortal(Socrates)")
    tree.result = "PROVED"
    tree.add_step(ProofStep(step=1, type=StepType.FACT, content="Human(Socrates)", justification="Given"))
    tree.add_step(ProofStep(step=2, type=StepType.RULE, content="Mortal(Socrates)", justification="IF Human(x) THEN Mortal(x)"))
    tree.add_step(ProofStep(step=3, type=StepType.CONCLUDE, content="Mortal(Socrates)", justification="Derived"))
    return tree


def test_narrator_one_line():
    assert Narrator.one_line(_proved_tree()) == "Yes"


def test_narrator_short_proved():
    text = Narrator.short(_proved_tree())
    assert "Yes" in text or "✅" in text


def test_narrator_medium_includes_rules():
    text = Narrator.medium(_proved_tree())
    assert "Human" in text
    assert "Rules used" in text


def test_narrator_disproved():
    tree = ProofTree(query="Mortal(Socrates)")
    tree.result = "DISPROVED"
    tree.add_step(ProofStep(step=1, type=StepType.FAIL, content="Mortal(Socrates)", justification="No proof"))
    assert "No" in Narrator.short(tree)
