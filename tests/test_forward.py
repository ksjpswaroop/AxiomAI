"""P2-04: Forward chaining tests."""

from __future__ import annotations


def test_forward_derives_mortal(reasoner):
    reasoner.add_fact("Human(Socrates)")
    reasoner.add_rule("IF Human(x) THEN Mortal(x)")
    result = reasoner.derive_all()
    derived = {str(f.predicate) for f in result.all_derived}
    assert "Mortal(Socrates)" in derived


def test_forward_fixpoint_no_new_facts(reasoner):
    reasoner.add_fact("Human(Socrates)")
    result = reasoner.derive_all()
    assert len(result.new_facts) == 0


def test_forward_multiple_entities(reasoner):
    reasoner.add_fact("Human(Socrates)")
    reasoner.add_fact("Human(Plato)")
    reasoner.add_rule("IF Human(x) THEN Mortal(x)")
    result = reasoner.derive_all()
    derived = {str(f.predicate) for f in result.new_facts}
    assert "Mortal(Socrates)" in derived
    assert "Mortal(Plato)" in derived


def test_forward_chain_two_rules(reasoner):
    reasoner.add_fact("Human(Socrates)")
    reasoner.add_rule("IF Human(x) THEN Mortal(x)")
    reasoner.add_rule("IF Mortal(x) THEN Dead(x)")
    result = reasoner.derive_all()
    derived = {str(f.predicate) for f in result.all_derived}
    assert "Dead(Socrates)" in derived


def test_forward_ask_proves_query(reasoner):
    reasoner.add_fact("Human(Socrates)")
    reasoner.add_rule("IF Human(x) THEN Mortal(x)")
    result = reasoner.ask("Mortal(Socrates)", mode="forward")
    assert result.result == "PROVED"


def test_forward_ask_disproves_missing(reasoner):
    reasoner.add_fact("Human(Socrates)")
    result = reasoner.ask("Mortal(Socrates)", mode="forward")
    assert result.result == "DISPROVED"


def test_forward_proof_records_steps(reasoner):
    reasoner.add_fact("Human(Socrates)")
    reasoner.add_rule("IF Human(x) THEN Mortal(x)")
    result = reasoner.derive_all()
    assert len(result.proof.steps) >= 2
