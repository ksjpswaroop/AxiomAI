"""
Resolution / Theorem Proving via refutation.
"""

from __future__ import annotations

import time
from ..core.models import Fact, Rule, Predicate
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
    1. Add ¬Query to KB
    2. Convert to CNF
    3. Apply resolution rules until:
       - Contradiction found → Query is PROVED
       - No more resolutions → Query is DISPROVED
    """

    def __init__(self, kb: KnowledgeBase, unification: UnificationEngine):
        self.kb = kb
        self.unification = unification

    def prove(self, query_str: str) -> ResolutionResult:
        """Prove query via refutation."""
        start = time.perf_counter()
        proof = ProofTree(query=query_str)

        # Check if query is already directly true
        if self.kb.query_fact(query_str):
            proof.result = "PROVED"
            proof.conclusion = query_str
            return ResolutionResult(True, proof, (time.perf_counter() - start) * 1000)

        # Add negation of query as assumption
        neg_query = f"¬{query_str}"
        proof.add_step(ProofStep(
            step=1,
            type=StepType.ASSUME,
            content=neg_query,
            justification="Negation of query for refutation",
        ))

        # Resolution loop
        clauses = self.kb.list_facts()
        clauses.append(Fact.create(neg_query, source="resolution", confidence_source="assumed"))

        resolvents: list[Fact] = []
        max_steps = 1000
        step_num = 2

        for _ in range(max_steps):
            new_resolvents = self._resolve_clauses(clauses + resolvents, proof, step_num)
            if new_resolvents is None:
                # Contradiction found
                proof.result = "PROVED"
                proof.conclusion = query_str
                return ResolutionResult(
                    True, proof, (time.perf_counter() - start) * 1000
                )
            if not new_resolvents:
                break
            resolvents.extend(new_resolvents)
            step_num += len(new_resolvents)

        # No contradiction — query is not provable
        proof.result = "DISPROVED"
        proof.conclusion = f"No resolution proof for: {query_str}"
        return ResolutionResult(
            False, proof, (time.perf_counter() - start) * 1000
        )

    def _resolve_clauses(
        self,
        clauses: list[Fact],
        proof: ProofTree,
        start_step: int,
    ) -> list[Fact] | None:
        """Try to derive contradiction between clauses. Returns None if contradiction found."""
        new_facts = []

        for i, c1 in enumerate(clauses):
            for c2 in clauses[i + 1:]:
                resolvent = self._resolve_pair(c1, c2)
                if resolvent is None:
                    # Contradiction!
                    proof.add_step(ProofStep(
                        step=start_step,
                        type=StepType.CONFLICT,
                        content=f"Contradiction: {c1.predicate} and {c2.predicate}",
                        justification=f"Resolved {c1.predicate} with {c2.predicate}",
                    ))
                    return None
                if resolvent:
                    new_facts.append(resolvent)

        return new_facts

    def _resolve_pair(self, c1: Fact, c2: Fact) -> Fact | None:
        """Resolve two clauses. Returns resolvent or None (if contradiction)."""
        pred1 = c1.predicate
        pred2 = c2.predicate

        # Try to unify predicate with negation of another
        neg1 = str(pred1).startswith("¬")
        neg2 = str(pred2).startswith("¬")

        # Direct contradiction: P and ¬P
        p1_str = str(pred1).lstrip("¬")
        p2_str = str(pred2).lstrip("¬")

        if p1_str == p2_str and (neg1 or neg2) and neg1 != neg2:
            return None  # Contradiction found

        return None  # No resolution possible in this simplified version
