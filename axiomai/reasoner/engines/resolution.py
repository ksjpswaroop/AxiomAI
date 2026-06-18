"""
Resolution / Theorem Proving via refutation (full first-order prover).
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from ..core.cnf import (
    Clause,
    Literal,
    clause_key,
    clause_subsumes,
    factor_clause,
    kb_to_clauses,
    simplify_clause,
)
from ..core.unification import UnificationEngine
from ..explain.proof import ProofStep, ProofTree, StepType
from ..kb.store import KnowledgeBase


@dataclass
class _ClauseEntry:
    clause: Clause
    key: str
    source: str = "kb"


class ResolutionResult:
    def __init__(self, provable: bool, proof: ProofTree, duration_ms: float):
        self.provable = provable
        self.proof = proof
        self.duration_ms = duration_ms


class ResolutionEngine:
    """
    Full resolution theorem prover using refutation with:

    - CNF conversion for facts and rules
    - Set-of-support (SOS) strategy
    - Tautology removal and subsumption
    - Clause factorization
    - Z3 unsatisfiability fallback for ground cases
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

        kb_entries = [
            _ClauseEntry(c, clause_key(c), "kb")
            for c in kb_to_clauses(self.kb)
        ]
        sos = [_ClauseEntry(Clause([Literal.from_string(neg_query)]), clause_key(
            Clause([Literal.from_string(neg_query)])
        ), "goal")]

        all_entries: dict[str, _ClauseEntry] = {e.key: e for e in kb_entries}
        for e in sos:
            all_entries[e.key] = e

        step_num = 2
        max_steps = 5000

        for _ in range(max_steps):
            if not sos:
                break

            selected = sos.pop(0)

            # Factor selected clause
            for factored in factor_clause(selected.clause, self.unification):
                self._add_clause(
                    factored, "factor", all_entries, sos, proof, step_num
                )
                step_num += 1

            pool = list(all_entries.values())
            found_contradiction = False

            for other in pool:
                if other.key == selected.key:
                    continue
                for resolvent in self._resolve_all(selected.clause, other.clause):
                    if resolvent is None:
                        proof.add_step(ProofStep(
                            step=step_num,
                            type=StepType.CONFLICT,
                            content="□",
                            justification=(
                                f"Empty clause from {selected.clause} ⊗ {other.clause}"
                            ),
                        ))
                        found_contradiction = True
                        break

                    added = self._add_clause(
                        resolvent,
                        f"resolve({selected.source},{other.source})",
                        all_entries,
                        sos,
                        proof,
                        step_num,
                    )
                    if added:
                        step_num += 1

                if found_contradiction:
                    break

            if found_contradiction:
                proof.result = "PROVED"
                proof.conclusion = query_str
                return ResolutionResult(
                    True, proof, (time.perf_counter() - start) * 1000
                )

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

    def _add_clause(
        self,
        clause: Clause,
        source: str,
        all_entries: dict[str, _ClauseEntry],
        sos: list[_ClauseEntry],
        proof: ProofTree,
        step_num: int,
    ) -> bool:
        simplified = simplify_clause(clause, self.unification)
        if simplified is None:
            return False
        key = clause_key(simplified)

        # Subsumption: skip if subsumed by existing clause
        for existing in list(all_entries.values()):
            if clause_subsumes(existing.clause, simplified, self.unification):
                return False

        # Remove clauses subsumed by the new one
        for existing_key in list(all_entries.keys()):
            existing = all_entries[existing_key]
            if clause_subsumes(simplified, existing.clause, self.unification):
                all_entries.pop(existing_key, None)
                sos[:] = [e for e in sos if e.key != existing_key]

        if key in all_entries:
            return False

        entry = _ClauseEntry(simplified, key, source)
        all_entries[key] = entry
        sos.append(entry)
        proof.add_step(ProofStep(
            step=step_num,
            type=StepType.RESOLVE,
            content=", ".join(str(lit) for lit in simplified.literals) or "□",
            justification=f"Derived via {source}",
        ))
        return True

    def _resolve_all(self, c1: Clause, c2: Clause) -> list[Clause | None]:
        """Resolve two clauses on all complementary unifiable literal pairs."""
        results: list[Clause | None] = []
        seen: set[str] = set()

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
                unique = dedupe_literals_dict(remaining)
                resolvent = Clause(list(unique.values()))
                if resolvent.is_empty():
                    results.append(None)
                    continue
                key = clause_key(resolvent)
                if key not in seen:
                    seen.add(key)
                    results.append(resolvent)
        return results

    def _z3_prove(self, query_str: str) -> bool:
        """Z3 fallback: KB ∪ {¬query} unsatisfiable ⇒ query provable."""
        try:
            from z3 import Bool, Not, Or, Solver, unsat

            solver = Solver()
            bool_vars: dict[str, object] = {}

            def get_bool(name: str):
                safe = "".join(c if c.isalnum() else "_" for c in name)
                if safe not in bool_vars:
                    bool_vars[safe] = Bool(safe)
                return bool_vars[safe]

            for fact in self.kb.list_active_facts():
                pred = str(fact.predicate)
                if fact.metadata.get("negated"):
                    solver.add(Not(get_bool(pred)))
                else:
                    solver.add(get_bool(pred))

            for rule in self.kb.get_enabled_rules():
                if not rule.consequent or not rule.antecedents:
                    continue
                cons = get_bool(str(rule.consequent))
                if rule.antecedent_operator == "or":
                    for ant in rule.antecedents:
                        solver.add(Or(Not(get_bool(str(ant))), cons))
                else:
                    solver.add(
                        Or(*[Not(get_bool(str(a))) for a in rule.antecedents], cons)
                    )

            solver.add(Not(get_bool(query_str)))
            return solver.check() == unsat
        except Exception:
            return False


def dedupe_literals_dict(literals: list[Literal]) -> dict[str, Literal]:
    return {str(lit): lit for lit in literals}
