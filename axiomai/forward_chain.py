"""
Forward Chaining Engine — Data-driven inference.
"""

from __future__ import annotations

import re
from typing import Optional
from axiomai.facts import FactStore, Fact
from axiomai.rules import RuleStore, Rule
from axiomai.proof_trace import ProofTrace, ProofStep


class ForwardChainResult:
    def __init__(
        self,
        new_facts: list[str],
        proof_trace: ProofTrace,
        all_derived_facts: list[str],
    ):
        self.new_facts = new_facts
        self.proof_trace = proof_trace
        self.all_derived_facts = all_derived_facts


class ForwardChainEngine:
    """
    Data-driven forward chaining inference engine.

    Algorithm:
    1. Load all facts into working memory
    2. For each rule (by priority), try to unify antecedents with facts
    3. On successful unification, add consequent to working memory
    4. Repeat until fixpoint (no new facts)
    5. Return all derived facts + full proof trace
    """

    def __init__(self, fact_store: FactStore, rule_store: RuleStore):
        self.fact_store = fact_store
        self.rule_store = rule_store
        self.step_counter = 0

    def run(self) -> ForwardChainResult:
        """Execute forward chaining until fixpoint."""
        working_memory: dict[str, bool] = {f.predicate: True for f in self.fact_store.list_all()}
        proof_trace = ProofTrace()
        new_facts_found: list[str] = []
        all_derived: list[str] = list(working_memory.keys())

        # Record initial facts
        for f in self.fact_store.list_all():
            self.step_counter += 1
            proof_trace.add_step(ProofStep(
                step=self.step_counter,
                type="fact",
                content=f.predicate,
                justification="Given",
                derived_from=[],
            ))

        changed = True
        iterations = 0
        max_iterations = 1000  # Guard against infinite loops

        while changed and iterations < max_iterations:
            changed = False
            iterations += 1

            for rule in self.rule_store.list_all():
                results = self._try_apply_rule(rule, working_memory)
                for consequent, bindings in results:
                    if consequent not in working_memory:
                        working_memory[consequent] = True
                        all_derived.append(consequent)
                        new_facts_found.append(consequent)
                        changed = True
                        self.step_counter += 1
                        proof_trace.add_step(ProofStep(
                            step=self.step_counter,
                            type="conclude",
                            content=consequent,
                            justification=f"Rule: {rule}",
                            derived_from=[consequent],
                        ))

        return ForwardChainResult(
            new_facts=new_facts_found,
            proof_trace=proof_trace,
            all_derived_facts=all_derived,
        )

    def _try_apply_rule(self, rule: Rule, working_memory: dict[str, bool]) -> list[tuple[str, dict]]:
        """
        Try to apply a rule. Returns list of (consequent_predicate, bindings).
        Handles multi-antecedent rules with variable unification.
        """
        results = []

        # Find facts that match each antecedent
        for antecedent in rule.antecedents:
            matched = self._match_antecedent(antecedent, working_memory)
            if not matched:
                return []  # One antecedent failed

        # All antecedents matched — apply the rule
        # Build consequent with any bound variables
        consequent = self._apply_rule_consequent(rule.consequent, rule.antecedents, working_memory)
        if consequent:
            results.append((consequent, {}))

        return results

    def _match_antecedent(self, antecedent: str, working_memory: dict[str, bool]) -> bool:
        """Check if an antecedent matches any fact in working memory (with unification)."""
        # Try direct match first
        if antecedent in working_memory:
            return True

        # Try variable unification — find facts with same relation
        match = re.match(r"^(\w+)\((.*)\)$", antecedent)
        if not match:
            return False

        rel = match.group(1)
        terms = [t.strip() for t in match.group(2).split(",")]

        # Check all facts in working memory
        for fact_pred in working_memory:
            f_match = re.match(r"^(\w+)\((.*)\)$", fact_pred)
            if not f_match or f_match.group(1) != rel:
                continue
            f_terms = [t.strip() for t in f_match.group(2).split(",")]
            if len(f_terms) != len(terms):
                continue
            # Check if terms unify (constants match or one is variable)
            if self._terms_unify(terms, f_terms):
                return True

        return False

    def _terms_unify(self, pattern_terms: list[str], fact_terms: list[str]) -> bool:
        """Check if pattern terms unify with fact terms."""
        for p, f in zip(pattern_terms, fact_terms):
            if self._is_variable(p):
                continue  # Variable unifies with anything
            if p != f:
                return False
        return True

    def _is_variable(self, term: str) -> bool:
        return bool(term and term[0].islower() and term not in ("true", "false"))

    def _apply_rule_consequent(
        self,
        consequent: str,
        antecedents: list[str],
        working_memory: dict[str, bool],
    ) -> Optional[str]:
        """
        Apply the rule consequent using the bindings from matched antecedents.
        Returns the concrete consequent predicate.
        """
        match = re.match(r"^(\w+)\((.*)\)$", consequent)
        if not match:
            return None

        rel = match.group(1)
        terms_str = match.group(2)
        terms = [t.strip() for t in terms_str.split(",")]

        # Try to resolve each term from working memory
        resolved_terms = []
        for term in terms:
            if self._is_variable(term):
                # Find what this variable is bound to
                bound = self._resolve_variable(term, antecedents, working_memory)
                if bound:
                    resolved_terms.append(bound)
                else:
                    resolved_terms.append(term)  # Keep unbound variable
            else:
                resolved_terms.append(term)

        return f"{rel}({', '.join(resolved_terms)})"

    def _resolve_variable(
        self,
        var: str,
        antecedents: list[str],
        working_memory: dict[str, bool],
    ) -> Optional[str]:
        """Resolve a variable to its bound value from matched antecedents."""
        for ant in antecedents:
            if var not in ant:
                continue
            match = re.match(r"^(\w+)\((.*)\)$", ant)
            if not match:
                continue
            terms = [t.strip() for t in match.group(2).split(",")]
            for fact_pred in working_memory:
                f_match = re.match(r"^(\w+)\((.*)\)$", fact_pred)
                if not f_match or f_match.group(1) != match.group(1):
                    continue
                f_terms = [t.strip() for t in f_match.group(2).split(",")]
                for p, f in zip(terms, f_terms):
                    if p == var and not self._is_variable(f):
                        return f
        return None
