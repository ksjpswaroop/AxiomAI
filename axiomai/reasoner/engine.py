"""
Reasoner — Main reasoning engine facade.
Combines all components into a single entry point.
"""

from __future__ import annotations

import time
import hashlib
from .core.models import Fact, Rule, Predicate
from .core.unification import UnificationEngine
from .core.parser import Parser
from .kb.store import KnowledgeBase, ContradictionReport
from .engines.forward import ForwardChainEngine, ForwardChainResult
from .engines.backward import BackwardChainEngine, BackwardChainResult
from .engines.resolution import ResolutionEngine, ResolutionResult
from .engines.constraints import ConstraintSolver, solve_sudoku
from .engines.planner import PlanningEngine, Plan, STRIPSAction
from .engines.causal import CausalEngine
from .explain.proof import ProofTree
from .explain.narrator import Narrator
from .integrations.llm_extractor import LLMExtractor


class QueryResult:
    """Unified query result across all reasoning modes."""

    def __init__(
        self,
        query: str,
        result: str,
        proof: ProofTree,
        bindings: dict,
        duration_ms: float,
        reasoning_mode: str,
        narrator: Narrator,
    ):
        self.query = query
        self.result = result
        self.proof = proof
        self.bindings = bindings
        self.duration_ms = duration_ms
        self.reasoning_mode = reasoning_mode
        self._narrator = narrator

    def explain(self, style: str = "short") -> str:
        """Get explanation in different styles: one_line, short, medium, detailed."""
        if style == "one_line":
            return Narrator.one_line(self.proof)
        elif style == "short":
            return Narrator.short(self.proof)
        elif style == "medium":
            return Narrator.medium(self.proof)
        elif style == "detailed":
            return Narrator.detailed(self.proof)
        return Narrator.short(self.proof)

    @property
    def status(self) -> str:
        """Logical confidence: PROVED / DISPROVED / UNKNOWN / INCONSISTENT."""
        return self.result


class Reasoner:
    """
    Main AxiomAI Reasoner engine.

    Usage:
        r = Reasoner()
        r.add_fact("Human(Socrates)")
        r.add_rule("IF Human(x) THEN Mortal(x)")
        result = r.ask("Mortal(Socrates)")
        print(result.explain())
    """

    def __init__(self, namespace: str = "default"):
        self.kb = KnowledgeBase(namespace=namespace)
        self.unification = UnificationEngine()
        self.parser = Parser()
        self.forward_engine = ForwardChainEngine(self.kb, self.unification)
        self.backward_engine = BackwardChainEngine(self.kb, self.unification)
        self.resolution_engine = ResolutionEngine(self.kb, self.unification)
        self.causal_engine = CausalEngine()
        self.planning_engine = PlanningEngine()
        self._narrator = Narrator()
        self._run_hash: str = ""
        self._run_count: int = 0

    # ── Facts ────────────────────────────────────────────────────────────────

    def add_fact(self, predicate: str, source: str = "user", **kwargs) -> Fact:
        """Add a fact to the knowledge base."""
        fact = self.parser.parse_fact(predicate, source=source)
        for k, v in kwargs.items():
            setattr(fact, k, v)
        return self.kb.add_fact(fact)

    def add_facts(self, *predicates: str, source: str = "user") -> list[Fact]:
        """Add multiple facts."""
        return [self.add_fact(p, source=source) for p in predicates]

    def retract_fact(self, predicate: str) -> bool:
        """Remove a fact."""
        return self.kb.retract_fact(predicate)

    def list_facts(self) -> list[Fact]:
        return self.kb.list_facts()

    # ── Rules ───────────────────────────────────────────────────────────────

    def add_rule(self, rule_str: str, priority: int = 1, **kwargs) -> Rule:
        """Add a rule from string."""
        rule = self.parser.parse_rule(rule_str, priority=priority)
        for k, v in kwargs.items():
            setattr(rule, k, v)
        return self.kb.add_rule(rule)

    def add_rule_direct(
        self, antecedents: list[str], consequent: str, priority: int = 1, **kwargs
    ) -> Rule:
        """Add a rule directly from antecedents + consequent."""
        rule = Rule(antecedents=[Predicate.parse(a) for a in antecedents],
                    consequent=Predicate.parse(consequent), priority=priority)
        for k, v in kwargs.items():
            setattr(rule, k, v)
        return self.kb.add_rule(rule)

    def retract_rule(self, rule_id: str) -> bool:
        return self.kb.retract_rule(rule_id)

    def list_rules(self) -> list[Rule]:
        return self.kb.list_rules()

    # ── Causal ───────────────────────────────────────────────────────────────

    def add_causal(self, cause: str, effect: str):
        """Add a causal relationship: cause → effect."""
        self.causal_engine.add_causal_fact(cause, effect)

    # ── Planning ────────────────────────────────────────────────────────────

    def add_action(
        self, name: str, preconditions: list[str],
        add_effects: list[str], del_effects: list[str] = None, cost: int = 1
    ) -> STRIPSAction:
        """Add a planning action (STRIPS-style)."""
        action = STRIPSAction(
            name=name,
            preconditions=preconditions,
            add_effects=add_effects,
            del_effects=del_effects or [],
            cost=cost,
        )
        self.planning_engine.add_action(action)
        return action

    # ── Reasoning ───────────────────────────────────────────────────────────

    def ask(self, query: str, mode: str = "auto") -> QueryResult:
        """
        Ask a query. Mode: 'auto', 'backward', 'forward', 'resolution'.
        Returns QueryResult with explanation.
        """
        self._run_count += 1
        start = time.perf_counter()

        # Auto-select mode
        if mode == "auto":
            # Forward chain if no rules match, backward if they might
            mode = "backward"

        if mode == "backward":
            result = self.backward_engine.prove(query)
            return QueryResult(
                query=query,
                result=result.result,
                proof=result.proof,
                bindings=result.bindings,
                duration_ms=(time.perf_counter() - start) * 1000,
                reasoning_mode="backward_chaining",
                narrator=self._narrator,
            )
        elif mode == "forward":
            result = self.forward_engine.run()
            # Check if query is in derived facts
            found = any(str(f.predicate) == query for f in result.all_derived)
            return QueryResult(
                query=query,
                result="PROVED" if found else "DISPROVED",
                proof=result.proof,
                bindings={},
                duration_ms=(time.perf_counter() - start) * 1000,
                reasoning_mode="forward_chaining",
                narrator=self._narrator,
            )
        elif mode == "resolution":
            result = self.resolution_engine.prove(query)
            return QueryResult(
                query=query,
                result="PROVED" if result.provable else "DISPROVED",
                proof=result.proof,
                bindings={},
                duration_ms=(time.perf_counter() - start) * 1000,
                reasoning_mode="resolution",
                narrator=self._narrator,
            )
        else:
            return self.ask(query, mode="backward")

    def derive_all(self) -> ForwardChainResult:
        """Run forward chaining to derive everything possible."""
        return self.forward_engine.run()

    # ── Contradictions ─────────────────────────────────────────────────────

    def check_consistency(self) -> list[ContradictionReport]:
        """Check for contradictions in the knowledge base."""
        return self.kb.detect_contradictions()

    def is_consistent(self) -> bool:
        return self.kb.is_consistent()

    # ── Constraints ────────────────────────────────────────────────────────

    def solve_csp(self, constraints: ConstraintSolver) -> dict | None:
        return constraints.solve()

    # ── Planning ───────────────────────────────────────────────────────────

    def plan(
        self, initial_state: set[str], goal: set[str], max_depth: int = 20
    ) -> Plan:
        return self.planning_engine.plan(initial_state, goal, max_depth)

    # ── Utilities ─────────────────────────────────────────────────────────

    def reset(self):
        """Clear all knowledge."""
        self.kb.clear()
        self._run_hash = ""
        self._run_count = 0

    def load_socrates(self):
        """Load the classic Socrates example."""
        self.reset()
        self.add_fact("Human(Socrates)")
        self.add_fact("Human(Plato)")
        self.add_rule("IF Human(x) THEN Mortal(x)")

    def fingerprint(self) -> str:
        """
        Deterministic hash of current KB state.
        Same KB always produces same fingerprint.
        """
        parts = []
        for f in sorted(self.kb.list_facts(), key=lambda f: str(f.predicate)):
            parts.append(str(f.predicate))
        for r in sorted(self.kb.list_rules(), key=lambda r: str(r)):
            parts.append(str(r))
        content = "|".join(parts)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def __repr__(self) -> str:
        return (
            f"Reasoner(facts={len(self.kb)}, rules={len(self.kb._rules)}, "
            f"fingerprint={self.fingerprint()})"
        )
