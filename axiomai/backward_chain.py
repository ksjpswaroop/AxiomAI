"""
Backward Chaining Engine — Goal-driven inference.
"""

from __future__ import annotations

import re
from typing import Optional
from axiomai.facts import FactStore
from axiomai.rules import RuleStore, Rule
from axiomai.proof_trace import ProofTrace, ProofStep


class BackwardChainResult:
    def __init__(
        self,
        goal: str,
        result: str,  # "TRUE", "FALSE", "UNKNOWN"
        proof_trace: ProofTrace,
        bindings: dict = None,
    ):
        self.goal = goal
        self.result = result
        self.proof_trace = proof_trace
        self.bindings = bindings or {}


class BackwardChainEngine:
    """
    Goal-driven backward chaining inference engine.

    Algorithm (Prolog-style):
    1. Receive goal predicate G
    2. Find rules with consequent matching G
    3. For each rule, recursively prove all antecedents
    4. If all antecedents provable → G is TRUE
    5. If no rule fires → G is FALSE
    6. Return result + proof tree
    """

    def __init__(self, fact_store: FactStore, rule_store: RuleStore):
        self.fact_store = fact_store
        self.rule_store = rule_store
        self.step_counter = 0

    def prove(self, goal: str) -> BackwardChainResult:
        """Prove a goal predicate. Returns TRUE/FALSE/UNKNOWN with proof trace."""
        proof_trace = ProofTrace()
        self.step_counter = 0

        # Check direct facts first
        if self.fact_store.query(goal):
            self.step_counter += 1
            proof_trace.add_step(ProofStep(
                step=self.step_counter,
                type="fact",
                content=goal,
                justification="Given",
                derived_from=[],
            ))
            return BackwardChainResult(goal=goal, result="TRUE", proof_trace=proof_trace)

        # Try rules
        result, trace = self._prove_goal(goal, proof_trace)

        return BackwardChainResult(
            goal=goal,
            result=result,
            proof_trace=trace,
        )

    def _prove_goal(self, goal: str, proof_trace: ProofTrace) -> tuple[str, ProofTrace]:
        """Recursive goal prover."""
        # Extract relation from goal
        match = re.match(r"^(\w+)\((.*)\)$", goal)
        if not match:
            return "UNKNOWN", proof_trace

        rel = match.group(1)
        goal_terms = [t.strip() for t in match.group(2).split(",")]

        # Find applicable rules
        rules = self.rule_store.get_rules_for_consequent(goal)
        if not rules:
            self.step_counter += 1
            proof_trace.add_step(ProofStep(
                step=self.step_counter,
                type="fail",
                content=goal,
                justification="No matching rule found",
                derived_from=[],
            ))
            return "FALSE", proof_trace

        for rule in rules:
            # Try to prove via this rule
            proved, trace = self._try_rule(rule, goal, goal_terms, proof_trace)
            if proved:
                return "TRUE", trace

        return "FALSE", proof_trace

    def _try_rule(
        self,
        rule: Rule,
        goal: str,
        goal_terms: list[str],
        proof_trace: ProofTrace,
    ) -> tuple[bool, ProofTrace]:
        """Try to prove goal using a specific rule."""
        # Build substitution by matching goal with rule consequent
        subst = self._build_substitution(rule.consequent, goal, goal_terms)
        if subst is None:
            return False, proof_trace

        # Recursively prove each antecedent
        all_proved = True
        for ant in rule.antecedents:
            # Apply substitution to antecedent
            ant_inst = self._apply_substitution(ant, subst)
            self.step_counter += 1
            proof_trace.add_step(ProofStep(
                step=self.step_counter,
                type="rule",
                content=f"{rule}",
                justification=f"Attempting antecedent: {ant_inst}",
                derived_from=[ant_inst],
            ))
            result, proof_trace = self._prove_goal(ant_inst, proof_trace)
            if result != "TRUE":
                all_proved = False
                break

        if all_proved:
            self.step_counter += 1
            proof_trace.add_step(ProofStep(
                step=self.step_counter,
                type="conclude",
                content=goal,
                justification=f"Proved via rule: {rule}",
                derived_from=rule.antecedents,
            ))
            return True, proof_trace

        return False, proof_trace

    def _build_substitution(self, consequent: str, goal: str, goal_terms: list[str]) -> Optional[dict]:
        """
        Build variable substitution by unifying consequent with goal.
        Returns dict of {var: value} or None if can't unify.
        """
        match = re.match(r"^(\w+)\((.*)\)$", consequent)
        if not match:
            return None
        cons_terms = [t.strip() for t in match.group(2).split(",")]

        if len(cons_terms) != len(goal_terms):
            return None

        subst: dict[str, str] = {}
        for c, g in zip(cons_terms, goal_terms):
            if self._is_variable(c):
                if c in subst and subst[c] != g:
                    return None  # Conflicting bindings
                subst[c] = g
            elif c != g:
                return None  # Constants must match

        return subst

    def _apply_substitution(self, predicate: str, subst: dict[str, str]) -> str:
        """Apply substitution to a predicate."""
        match = re.match(r"^(\w+)\((.*)\)$", predicate)
        if not match:
            return predicate
        rel = match.group(1)
        terms = [t.strip() for t in match.group(2).split(",")]
        resolved = [subst.get(t, t) for t in terms]
        return f"{rel}({', '.join(resolved)})"

    def _is_variable(self, term: str) -> bool:
        return bool(term and term[0].islower() and term not in ("true", "false"))
