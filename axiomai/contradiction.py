"""
Contradiction Detection — Truth maintenance system.
"""

from __future__ import annotations

import re
from axiomai.facts import FactStore


class ContradictionDetector:
    """
    Detects logical contradictions in the knowledge base.
    
    A contradiction occurs when both P(x) and ¬P(x) are present,
    or when a fact and its negation can both be derived.
    """

    def __init__(self, fact_store: FactStore):
        self.fact_store = fact_store

    def check(self) -> list[dict]:
        """
        Scan the fact store for contradictions.
        Returns list of contradiction reports.
        """
        contradictions = []

        for fact in self.fact_store.list_all():
            negation = self._negate(fact.predicate)
            if self.fact_store.query(negation):
                contradictions.append({
                    "type": "direct",
                    "fact": fact.predicate,
                    "negation": negation,
                    "message": f"Contradiction: {fact.predicate} and {negation} both asserted",
                })

        return contradictions

    def _negate(self, predicate: str) -> str:
        """
        Negate a predicate.
        Human(Socrates) → ¬Human(Socrates)
        """
        if predicate.startswith("¬"):
            return predicate[1:]
        # Simple negation prefix
        return f"¬{predicate}"

    def is_consistent(self) -> bool:
        """Return True if no contradictions detected."""
        return len(self.check()) == 0
