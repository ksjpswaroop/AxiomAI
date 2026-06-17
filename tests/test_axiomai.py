"""
Test suite for AxiomAI.
"""

import pytest
from axiomai import AxiomEngine, FactStore, RuleStore
from axiomai.proof_trace import ProofTrace, ProofStep
from axiomai.constraints import solve_sudoku


class TestFactStore:
    def test_add_fact(self):
        store = FactStore()
        fact = store.add("Human(Socrates)")
        assert fact.predicate == "Human(Socrates)"
        assert fact.relation == "Human"
        assert fact.terms == ["Socrates"]

    def test_query_fact(self):
        store = FactStore()
        store.add("Human(Socrates)")
        assert store.query("Human(Socrates)") is True
        assert store.query("Mortal(Socrates)") is False

    def test_retract_fact(self):
        store = FactStore()
        store.add("Human(Socrates)")
        assert store.retract("Human(Socrates)") is True
        assert store.query("Human(Socrates)") is False

    def test_parse_predicate(self):
        from axiomai.facts import Fact
        f = Fact.from_predicate("Loves(John, Mary)")
        assert f.relation == "Loves"
        assert f.terms == ["John", "Mary"]


class TestRuleStore:
    def test_add_rule_if_then(self):
        store = RuleStore()
        rule = store.add("IF Human(x) THEN Mortal(x)")
        assert rule.antecedents == ["Human(x)"]
        assert rule.consequent == "Mortal(x)"

    def test_add_rule_arrow(self):
        store = RuleStore()
        rule = store.add("Human(x) -> Mortal(x)")
        assert rule.antecedents == ["Human(x)"]
        assert rule.consequent == "Mortal(x)"

    def test_add_rule_multi_antecedent(self):
        store = RuleStore()
        rule = store.add("IF Human(x) AND Rational(x) THEN Person(x)")
        assert len(rule.antecedents) == 2
        assert rule.antecedents == ["Human(x)", "Rational(x)"]


class TestAxiomEngine:
    def test_socrates_basic(self):
        engine = AxiomEngine()
        engine.add_fact("Human(Socrates)")
        engine.add_rule("IF Human(x) THEN Mortal(x)")

        result = engine.backward_chain("Mortal(Socrates)")
        assert result.result == "TRUE"

    def test_socrates_forward(self):
        engine = AxiomEngine()
        engine.add_fact("Human(Socrates)")
        engine.add_fact("Human(Plato)")
        engine.add_rule("IF Human(x) THEN Mortal(x)")

        result = engine.forward_chain()
        assert "Mortal(Socrates)" in result.all_derived_facts
        assert "Mortal(Plato)" in result.all_derived_facts

    def test_unknown_goal(self):
        engine = AxiomEngine()
        engine.add_fact("Human(Socrates)")
        engine.add_rule("IF Human(x) THEN Mortal(x)")

        result = engine.backward_chain("Wise(Socrates)")
        assert result.result == "FALSE"

    def test_load_socrates(self):
        engine = AxiomEngine()
        engine.load_socrates()
        assert len(engine.list_facts()) == 2
        assert len(engine.list_rules()) == 1

        result = engine.backward_chain("Mortal(Socrates)")
        assert result.result == "TRUE"

    def test_reset(self):
        engine = AxiomEngine()
        engine.add_fact("Human(Socrates)")
        engine.reset()
        assert len(engine.list_facts()) == 0


class TestProofTrace:
    def test_proof_trace_to_text(self):
        trace = ProofTrace()
        trace.add_step(ProofStep(
            step=1,
            type="fact",
            content="Human(Socrates)",
            justification="Given",
            derived_from=[],
        ))
        trace.add_step(ProofStep(
            step=2,
            type="conclude",
            content="Mortal(Socrates)",
            justification="Rule: IF Human(x) THEN Mortal(x)",
            derived_from=["Human(Socrates)"],
        ))

        text = trace.to_text()
        assert "Human(Socrates)" in text
        assert "Mortal(Socrates)" in text
        assert "PROOF TRACE" in text


class TestConstraintSolver:
    def test_simple_csp(self):
        from axiomai.constraints import ConstraintSolver
        solver = ConstraintSolver()
        solver.var("x", 1, 10)
        solver.var("y", 1, 10)
        solver.add_constraint("x + y <= 15")
        solver.add_constraint("x != y")
        result = solver.solve()
        assert result is not None
        assert result["x"] + result["y"] <= 15
        assert result["x"] != result["y"]

    def test_sudoku(self):
        puzzle = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9],
        ]
        solution = solve_sudoku(puzzle)
        assert solution is not None
        # Verify all rows sum correctly (1-9 = 45)
        for row in solution:
            assert sum(row) == 45
