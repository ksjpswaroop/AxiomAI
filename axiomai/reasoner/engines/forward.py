"""
Forward Chaining Engine — Data-driven inference.
"""

from __future__ import annotations

import time
from ..core.models import Fact, Rule, Predicate
from ..core.substitution import Substitution
from ..core.unification import UnificationEngine
from ..explain.proof import ProofTree, ProofStep, StepType
from ..kb.store import KnowledgeBase


class ForwardChainResult:
    def __init__(
        self,
        new_facts: list[Fact],
        proof: ProofTree,
        all_derived: list[Fact],
        duration_ms: float,
    ):
        self.new_facts = new_facts
        self.proof = proof
        self.all_derived = all_derived
        self.duration_ms = duration_ms


class ForwardChainEngine:
    """
    Data-driven forward chaining inference engine.

    Algorithm:
    1. Load all facts into working memory
    2. For each rule (by priority), try to unify antecedents
    3. On success, add consequent to working memory
    4. Repeat until fixpoint (no new facts)
    5. Return all derived facts + full proof trace
    """

    def __init__(self, kb: KnowledgeBase, unification: UnificationEngine):
        self.kb = kb
        self.unification = unification
        self.step_counter = 0

    def run(self, max_iterations: int = 1000) -> ForwardChainResult:
        """Execute forward chaining until fixpoint."""
        start = time.perf_counter()

        proof = ProofTree()
        working: dict[str, Fact] = {str(f.predicate): f for f in self.kb.list_facts()}
        new_facts_found: list[Fact] = []
        all_derived: list[Fact] = list(working.values())

        # Record initial facts
        for f in self.kb.list_facts():
            self.step_counter += 1
            step = ProofStep(
                step=self.step_counter,
                type=StepType.FACT,
                content=str(f.predicate),
                justification="Given",
            )
            proof.add_step(step)

        changed = True
        iterations = 0

        while changed and iterations < max_iterations:
            changed = False
            iterations += 1

            for rule in self.kb.get_enabled_rules():
                results = self._apply_rule(rule, working)
                for consequent, subst in results:
                    if str(consequent) not in working:
                        working[str(consequent)] = consequent
                        all_derived.append(consequent)
                        new_facts_found.append(consequent)
                        changed = True
                        self.step_counter += 1
                        proof.add_step(ProofStep(
                            step=self.step_counter,
                            type=StepType.CONCLUDE,
                            content=str(consequent),
                            justification=f"Rule fired: {rule}",
                            rule_id=rule.id,
                            bindings=subst.to_dict(),
                        ))

        duration_ms = (time.perf_counter() - start) * 1000
        proof.result = "PROVED" if new_facts_found else "NO_NEW_FACTS"
        proof.conclusion = f"Derived {len(new_facts_found)} new facts in {iterations} iterations"

        return ForwardChainResult(
            new_facts=new_facts_found,
            proof=proof,
            all_derived=all_derived,
            duration_ms=duration_ms,
        )

    def _apply_rule(
        self,
        rule: Rule,
        working: dict[str, Fact],
    ) -> list[tuple[Fact, Substitution]]:
        """Try to apply a rule. Returns list of (consequent_fact, substitution)."""
        if not rule.consequent:
            return []

        # Try to match all antecedents
        subst = Substitution.identity()
        matched_facts: list[Fact] = []

        for ant in rule.antecedents:
            matched = self._match_antecedent(ant, working, subst)
            if matched is None:
                return []
            fact, new_subst = matched
            matched_facts.append(fact)
            subst = subst.compose(new_subst)

        # Apply substitution to consequent
        consequent_pred = rule.consequent.substitute(subst.to_dict())
        consequent_fact = Fact.create(
            consequent_pred,
            source=f"rule:{rule.id}",
            confidence_source="derived",
        )

        return [(consequent_fact, subst)]

    def _match_antecedent(
        self,
        antecedent: Predicate,
        working: dict[str, Fact],
        current_subst: Substitution,
    ) -> tuple[Fact, Substitution] | None:
        """Find a fact in working memory that unifies with antecedent."""
        for fact_pred_str, fact in working.items():
            subst = self.unification.match(antecedent, fact.predicate)
            if subst is not None:
                composed = current_subst.compose(subst)
                return fact, subst
        return None
