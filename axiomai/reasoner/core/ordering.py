"""
Ordering — Deterministic rule/fact ordering for reproducible inference.
"""

from __future__ import annotations

from ..core.models import Rule, Fact, Predicate


class OrderingEngine:
    """
    Provides deterministic ordering of rules and facts.
    Key for making the engine reproducible: same inputs → same outputs.
    """

    @staticmethod
    def sort_rules(rules: list[Rule]) -> list[Rule]:
        """
        Sort rules deterministically:
        1. By priority (descending)
        2. By string representation (stable sort)
        """
        return sorted(rules, key=lambda r: (-r.priority, str(r)))

    @staticmethod
    def sort_facts(facts: list[Fact]) -> list[Fact]:
        """
        Sort facts deterministically:
        1. By creation time (ascending)
        2. By predicate string (stable sort)
        """
        return sorted(facts, key=lambda f: (f.created_at, str(f.predicate)))

    @staticmethod
    def sort_predicates(predicates: list[Predicate]) -> list[Predicate]:
        """Sort predicates by string representation."""
        return sorted(predicates, key=str)

    @staticmethod
    def tiebreak_rules(rules: list[Rule]) -> list[Rule]:
        """When multiple rules have same priority, use canonical ordering."""
        return sorted(rules, key=lambda r: (
            -r.priority,
            len(r.antecedents),
            str(r)
        ))
