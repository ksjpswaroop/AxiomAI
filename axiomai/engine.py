"""
AxiomAI Engine — Main inference engine facade.
"""

from __future__ import annotations

from axiomai.facts import FactStore, Fact
from axiomai.rules import RuleStore, Rule
from axiomai.unification import UnificationEngine
from axiomai.forward_chain import ForwardChainEngine, ForwardChainResult
from axiomai.backward_chain import BackwardChainEngine, BackwardChainResult
from axiomai.proof_trace import ProofTrace


class AxiomEngine:
    """
    Main entry point for AxiomAI.
    
    Usage:
        engine = AxiomEngine()
        engine.add_fact("Human(Socrates)")
        engine.add_rule("IF Human(x) THEN Mortal(x)")
        result = engine.query("Mortal(Socrates)")
        print(result.proof_trace.to_text())
    """

    def __init__(self):
        self.facts = FactStore()
        self.rules = RuleStore()
        self.unification = UnificationEngine()

    # ── Facts ──────────────────────────────────────────────────────────────────

    def add_fact(self, predicate: str) -> Fact:
        """Add a fact to the knowledge base."""
        return self.facts.add(predicate)

    def add_facts(self, *predicates: str) -> list[Fact]:
        """Add multiple facts at once."""
        return [self.add_fact(p) for p in predicates]

    def retract_fact(self, predicate: str) -> bool:
        """Remove a fact from the knowledge base."""
        return self.facts.retract(predicate)

    def list_facts(self) -> list[Fact]:
        """List all facts."""
        return self.facts.list_all()

    # ── Rules ─────────────────────────────────────────────────────────────────

    def add_rule(self, rule_str: str, priority: int = 1) -> Rule:
        """Add a rule from string: 'IF Human(x) THEN Mortal(x)' or 'Human(x) -> Mortal(x)'"""
        return self.rules.add(rule_str, priority)

    def add_rule_direct(self, antecedents: list[str], consequent: str, priority: int = 1) -> Rule:
        """Add a rule directly: antecedents=['Human(x)'], consequent='Mortal(x)'"""
        return self.rules.add_rule(antecedents, consequent, priority)

    def retract_rule(self, rule_id: str) -> bool:
        """Remove a rule by ID."""
        return self.rules.retract(rule_id)

    def list_rules(self) -> list[Rule]:
        """List all rules."""
        return self.rules.list_all()

    # ── Inference ─────────────────────────────────────────────────────────────

    def forward_chain(self) -> ForwardChainResult:
        """Run forward chaining from current facts. Returns new facts + trace."""
        engine = ForwardChainEngine(self.facts, self.rules)
        return engine.run()

    def backward_chain(self, goal: str) -> BackwardChainResult:
        """Run backward chaining to prove a goal. Returns TRUE/FALSE/UNKNOWN + trace."""
        engine = BackwardChainEngine(self.facts, self.rules)
        return engine.prove(goal)

    def query(self, goal: str) -> BackwardChainResult:
        """
        Query the knowledge base. Alias for backward_chain.
        Automatically determines the best reasoning strategy.
        """
        return self.backward_chain(goal)

    def derive_all(self) -> ForwardChainResult:
        """Derive all possible conclusions from current facts + rules."""
        return self.forward_chain()

    # ── Utilities ─────────────────────────────────────────────────────────────

    def reset(self):
        """Clear all facts and rules."""
        self.facts.clear()
        self.rules.clear()

    def load_socrates(self):
        """Load the classic Socrates example."""
        self.reset()
        self.add_fact("Human(Socrates)")
        self.add_fact("Human(Plato)")
        self.add_rule("IF Human(x) THEN Mortal(x)")

    def __repr__(self) -> str:
        return f"AxiomEngine(facts={len(self.facts)}, rules={len(self.rules)})"
