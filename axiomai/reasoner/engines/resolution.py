"""
Resolution / Theorem Proving via refutation.
"""

from __future__ import annotations

import re
import time

from ..core.cnf import Clause, Literal, kb_to_clauses, clause_key
from ..core.unification import UnificationEngine
from ..explain.proof import ProofTree, ProofStep, StepType
from ..kb.store import KnowledgeBase


class ResolutionResult:
    def __init__(self, provable: bool, proof: ProofTree, duration_ms: float):
        self.provable = provable
        self.proof = proof
        self.duration_ms = duration_ms


class ResolutionEngine:
    """
    Resolution theorem prover using refutation.

    To prove KB ⊨ Query:
    1. Convert facts + rules to CNF clauses
    2. Add ¬Query as a unit clause
    3. Apply resolution until empty clause (contradiction) or exhaustion
    4. Fall back to Z3 unsatisfiability check for ground cases
    """

    def __init__(self, kb: KnowledgeBase, unification: UnificationEngine):
        self.kb = kb
        self.unification = unification

    def prove(self, query_str: str) -> ResolutionResult:
        """Prove query via refutation."""
        start = time.perf_counter()
        proof = ProofTree(query=query_str)

        if self.kb.query_fact(query_str):
            proof.result = "PROVED"
            proof.conclusion = query_str
            proof.add_step(ProofStep(
                step=1,
                type=StepType.FACT,
                content=query_str,
                justification="Given fact",
            ))
            return ResolutionResult(True, proof, (time.perf_counter() - start) * 1000)

        neg_query = f"¬{query_str}"
        proof.add_step(ProofStep(
            step=1,
            type=StepType.ASSUME,
            content=neg_query,
            justification="Negation of query for refutation",
        ))

        clauses: list[Clause] = kb_to_clauses(self.kb)
        clauses.append(Clause([Literal.from_string(neg_query)]))

        known: set[str] = {clause_key(c) for c in clauses}
        step_num = 2
        max_steps = 2000

        for _ in range(max_steps):
            new_clauses: list[Clause] = []
            found_contradiction = False

            for i, c1 in enumerate(clauses):
                for c2 in clauses[i + 1:]:
                    result = self._resolve_pair(c1, c2)
                    if result is None:
                        found_contradiction = True
                        proof.add_step(ProofStep(
                            step=step_num,
                            type=StepType.CONFLICT,
                            content=f"Empty clause from {c1} and {c2}",
                            justification="Contradiction derived",
                        ))
                        break
                    if result is not False:
                        key = clause_key(result)
                        if key not in known:
                            known.add(key)
                            new_clauses.append(result)
                            proof.add_step(ProofStep(
                                step=step_num,
                                type=StepType.RESOLVE,
                                content=", ".join(str(l) for l in result.literals),
                                justification=f"Resolved {c1} with {c2}",
                            ))
                            step_num += 1
                if found_contradiction:
                    break

            if found_contradiction:
                proof.result = "PROVED"
                proof.conclusion = query_str
                return ResolutionResult(
                    True, proof, (time.perf_counter() - start) * 1000
                )

            if not new_clauses:
                break
            clauses.extend(new_clauses)

        if self._z3_prove(query_str):
            proof.add_step(ProofStep(
                step=step_num,
                type=StepType.RESOLVE,
                content=query_str,
                justification="Z3 unsatisfiability check confirmed proof",
            ))
            proof.result = "PROVED"
            proof.conclusion = query_str
            return ResolutionResult(True, proof, (time.perf_counter() - start) * 1000)

        proof.result = "DISPROVED"
        proof.conclusion = f"No resolution proof for: {query_str}"
        return ResolutionResult(
            False, proof, (time.perf_counter() - start) * 1000
        )

    def _resolve_pair(
        self, c1: Clause, c2: Clause
    ) -> Clause | None | bool:
        """
        Resolve two clauses on complementary unifiable literals.

        Returns:
            Clause — new resolvent
            None — empty clause (contradiction)
            False — no resolution possible
        """
        for lit1 in c1.literals:
            for lit2 in c2.literals:
                if lit1.negated == lit2.negated:
                    continue
                result = self.unification.unify(lit1.predicate, lit2.predicate)
                if not result.success:
                    continue
                subst = result.substitution.to_dict()
                remaining: list[Literal] = []
                for lit in c1.literals:
                    if lit is not lit1:
                        remaining.append(lit.substitute(subst))
                for lit in c2.literals:
                    if lit is not lit2:
                        remaining.append(lit.substitute(subst))
                unique: dict[str, Literal] = {str(lit): lit for lit in remaining}
                resolvent = Clause(list(unique.values()))
                if resolvent.is_empty():
                    return None
                return resolvent
        return False

    def _z3_prove(self, query_str: str) -> bool:
        """Z3 fallback: KB ∪ {¬query} unsatisfiable ⇒ query provable."""
        try:
            from z3 import Solver, Bool, Not, Or, unsat

            solver = Solver()
            bool_vars: dict[str, object] = {}

            def get_bool(name: str):
                safe = re.sub(r"[^\w]", "_", name)
                if safe not in bool_vars:
                    bool_vars[safe] = Bool(safe)
                return bool_vars[safe]

            for fact in self.kb.list_active_facts():
                solver.add(get_bool(str(fact.predicate)))

            for rule in self.kb.get_enabled_rules():
                if not rule.consequent or not rule.antecedents:
                    continue
                cons = get_bool(str(rule.consequent))
                if rule.antecedent_operator == "or":
                    for ant in rule.antecedents:
                        solver.add(Not(get_bool(str(ant))) | cons)
                else:
                    solver.add(
                        Or(*[Not(get_bool(str(a))) for a in rule.antecedents], cons)
                    )

            solver.add(Not(get_bool(query_str)))
            return solver.check() == unsat
        except Exception:
            return False
