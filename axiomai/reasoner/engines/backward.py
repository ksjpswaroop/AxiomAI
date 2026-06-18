"""
Backward Chaining Engine — Goal-driven inference (Prolog-style).
"""

from __future__ import annotations

import time
from typing import Optional
from ..core.models import Fact, Rule, Predicate
from ..core.substitution import Substitution
from ..core.unification import UnificationEngine
from ..explain.proof import ProofTree, ProofStep, StepType
from ..kb.store import KnowledgeBase


class BackwardChainResult:
    def __init__(
        self,
        goal: str,
        result: str,
        proof: ProofTree,
        bindings: dict,
        duration_ms: float,
    ):
        self.goal = goal
        self.result = result      # PROVED, DISPROVED, UNKNOWN, INCONSISTENT
        self.proof = proof
        self.bindings = bindings
        self.duration_ms = duration_ms


class BackwardChainEngine:
    """
    Goal-driven backward chaining inference engine.

    Algorithm (Prolog-style):
    1. Receive goal predicate G
    2. Find rules with consequent matching G
    3. For each rule, recursively prove all antecedents
    4. If all antecedents provable → G is PROVED
    5. If no rule fires → G is DISPROVED
    6. Track proof tree at each step
    """

    def __init__(self, kb: KnowledgeBase, unification: UnificationEngine):
        self.kb = kb
        self.unification = unification
        self.step_counter = 0
        self._memo: dict[str, str] = {}  # goal_str -> result

    def prove(self, goal_str: str) -> BackwardChainResult:
        """Prove a goal predicate. Returns PROVED/DISPROVED/UNKNOWN + proof."""
        start = time.perf_counter()

        self.step_counter = 0
        proof = ProofTree(query=goal_str)
        goal_pred = Predicate.parse(goal_str)

        # Check memoization
        if goal_str in self._memo:
            result = self._memo[goal_str]
            duration_ms = (time.perf_counter() - start) * 1000
            proof.result = result
            proof.conclusion = f"From cache: {result}"
            return BackwardChainResult(goal_str, result, proof, {}, duration_ms)

        # Direct fact check
        if self.kb.query_fact(goal_str):
            self.step_counter += 1
            proof.add_step(ProofStep(
                step=self.step_counter,
                type=StepType.FACT,
                content=goal_str,
                justification="Given",
            ))
            proof.result = "PROVED"
            proof.conclusion = goal_str
            duration_ms = (time.perf_counter() - start) * 1000
            return BackwardChainResult(goal_str, "PROVED", proof, {}, duration_ms)

        # Try rules
        result, proof, bindings = self._prove_goal(goal_pred, proof)

        duration_ms = (time.perf_counter() - start) * 1000
        proof.duration_ms = duration_ms
        if result:
            proof.result = result
            proof.conclusion = goal_str if result == "PROVED" else result
            self._memo[goal_str] = result

        return BackwardChainResult(
            goal=goal_str,
            result=result or "UNKNOWN",
            proof=proof,
            bindings=bindings,
            duration_ms=duration_ms,
        )

    def _prove_goal(
        self,
        goal: Predicate,
        proof: ProofTree,
        depth: int = 0,
    ) -> tuple[Optional[str], ProofTree, dict]:
        """Recursive goal prover. Returns (result, proof, bindings)."""
        goal_str = str(goal)

        if depth > 100:
            return "UNKNOWN", proof, {}

        # Check if goal is a known fact
        if self.kb.query_fact(goal_str):
            self.step_counter += 1
            proof.add_step(ProofStep(
                step=self.step_counter,
                type=StepType.FACT,
                content=goal_str,
                justification="Given",
            ))
            return "PROVED", proof, {}

        # Find applicable rules
        rules = self.kb.get_rules_for_consequent(goal)
        if not rules:
            self.step_counter += 1
            proof.add_step(ProofStep(
                step=self.step_counter,
                type=StepType.FAIL,
                content=goal_str,
                justification="No matching rule found",
            ))
            return None, proof, {}

        for rule in rules:
            proved, proof_out, subst = self._try_rule(rule, goal, proof, depth)
            if proved:
                return "PROVED", proof_out, subst.to_dict()

        # All rules failed
        return None, proof, {}

    def _try_rule(
        self,
        rule: Rule,
        goal: Predicate,
        proof: ProofTree,
        depth: int,
    ) -> tuple[bool, ProofTree, Substitution]:
        """Try to prove goal using a specific rule."""
        self.step_counter += 1
        rule_step = ProofStep(
            step=self.step_counter,
            type=StepType.RULE,
            content=str(rule),
            justification=f"Attempting rule for: {goal}",
            rule_id=rule.id,
        )
        proof.add_step(rule_step)

        # Unify goal with rule consequent
        subst = self.unification.match(rule.consequent, goal)
        if subst is None:
            return False, proof, Substitution.identity()

        # Prove antecedents recursively
        if rule.antecedent_operator == "or":
            any_proved = False
            for ant in rule.antecedents:
                ant_inst = ant.substitute(subst.to_dict())
                result, proof, _ = self._prove_goal(ant_inst, proof, depth + 1)
                if result == "PROVED":
                    any_proved = True
                    break
            if not any_proved:
                return False, proof, Substitution.identity()
        else:
            for ant in rule.antecedents:
                ant_inst = ant.substitute(subst.to_dict())
                result, proof, _ = self._prove_goal(ant_inst, proof, depth + 1)
                if result != "PROVED":
                    return False, proof, Substitution.identity()

        # All antecedents proved
        self.step_counter += 1
        proof.add_step(ProofStep(
            step=self.step_counter,
            type=StepType.CONCLUDE,
            content=str(goal),
            justification=f"Rule fired: {rule}",
            rule_id=rule.id,
            bindings=subst.to_dict(),
        ))

        return True, proof, subst
