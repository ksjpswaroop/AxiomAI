"""
KB Store — In-memory knowledge base store.
SQLite and graph-backed stores extend this.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from ..core.models import Fact, Rule, Predicate, Entity, RelationDef
from ..core.substitution import Substitution
from ..core.ordering import OrderingEngine


@dataclass
class ContradictionReport:
    """A detected contradiction."""
    fact1: Fact
    fact2: Fact
    explanation: str


class KnowledgeBase:
    """
    In-memory knowledge base store.
    Thread-safe for single-engine use.
    Production: subclass with SQLite/Postgres backend.
    """

    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
        self._facts: dict[str, Fact] = {}
        self._rules: dict[str, Rule] = {}
        self._entities: dict[str, Entity] = {}
        self._relations: dict[str, RelationDef] = {}
        self._justifications: dict[str, list[str]] = {}  # fact_id -> [rule_ids that derived it]
        self._derived_from: dict[str, list[str]] = {}  # fact_id -> [source fact_ids]
        self._ordering = OrderingEngine()
        self._stats = {"adds": 0, "queries": 0, "retractions": 0}

    # ── Facts ────────────────────────────────────────────────────────────────

    def add_fact(self, fact: Fact) -> Fact:
        """Add a fact. Idempotent — same predicate replaces existing."""
        self._stats["adds"] += 1
        self._facts[fact.predicate.relation + "(" + ",".join(
            str(t) for t in fact.predicate.terms
        ) + ")"] = fact
        return fact

    def retract_fact(self, predicate_str: str) -> bool:
        """Remove a fact by predicate string."""
        self._stats["retractions"] += 1
        return self._facts.pop(predicate_str, None) is not None

    def query_fact(self, predicate_str: str) -> bool:
        """Check if a fact exists."""
        self._stats["queries"] += 1
        return predicate_str in self._facts

    def get_fact(self, predicate_str: str) -> Optional[Fact]:
        return self._facts.get(predicate_str)

    def list_facts(self) -> list[Fact]:
        """Return all facts sorted deterministically."""
        return self._ordering.sort_facts(list(self._facts.values()))

    def list_facts_by_relation(self, relation: str) -> list[Fact]:
        return [
            f for f in self._facts.values()
            if f.predicate.relation == relation
        ]

    # ── Rules ────────────────────────────────────────────────────────────────

    def add_rule(self, rule: Rule) -> Rule:
        self._stats["adds"] += 1
        self._rules[rule.id] = rule
        return rule

    def retract_rule(self, rule_id: str) -> bool:
        self._stats["retractions"] += 1
        return self._rules.pop(rule_id, None) is not None

    def get_rule(self, rule_id: str) -> Optional[Rule]:
        return self._rules.get(rule_id)

    def list_rules(self) -> list[Rule]:
        """Return all rules sorted by priority."""
        return self._ordering.sort_rules(list(self._rules.values()))

    def get_enabled_rules(self) -> list[Rule]:
        return [r for r in self.list_rules() if r.enabled]

    def get_rules_for_consequent(self, consequent: Predicate) -> list[Rule]:
        """Find rules whose consequent unifies with the given predicate."""
        results = []
        for rule in self.get_enabled_rules():
            if rule.consequent and rule.consequent.relation == consequent.relation:
                results.append(rule)
        return results

    # ── Entities ────────────────────────────────────────────────────────────

    def add_entity(self, entity: Entity) -> Entity:
        self._entities[entity.name] = entity
        return entity

    def get_entity(self, name: str) -> Optional[Entity]:
        return self._entities.get(name)

    def list_entities(self) -> list[Entity]:
        return list(self._entities.values())

    # ── Relations ───────────────────────────────────────────────────────────

    def add_relation(self, rel: RelationDef) -> RelationDef:
        self._relations[rel.name] = rel
        return rel

    def get_relation(self, name: str) -> Optional[RelationDef]:
        return self._relations.get(name)

    # ── Justification / Provenance ──────────────────────────────────────────

    def justify(self, fact_id: str, rule_ids: list[str], source_fact_ids: list[str]):
        """Record why a derived fact was derived."""
        self._justifications[fact_id] = rule_ids
        self._derived_from[fact_id] = source_fact_ids

    def get_justification(self, fact_id: str) -> dict:
        return {
            "rules": self._justifications.get(fact_id, []),
            "source_facts": self._derived_from.get(fact_id, []),
        }

    # ── Contradiction Detection ─────────────────────────────────────────────

    def detect_contradictions(self) -> list[ContradictionReport]:
        """Scan for P(x) and ¬P(x) pairs."""
        reports = []
        for fact in self._facts.values():
            neg_str = f"¬{str(fact.predicate)}"
            if neg_str in self._facts:
                reports.append(ContradictionReport(
                    fact1=fact,
                    fact2=self._facts[neg_str],
                    explanation=f"Direct contradiction: {fact.predicate} and ¬{fact.predicate}",
                ))
        return reports

    def is_consistent(self) -> bool:
        return len(self.detect_contradictions()) == 0

    # ── Stats ───────────────────────────────────────────────────────────────

    def stats(self) -> dict:
        return {
            **self._stats,
            "fact_count": len(self._facts),
            "rule_count": len(self._rules),
            "entity_count": len(self._entities),
        }

    def __len__(self) -> int:
        return len(self._facts)

    def clear(self):
        self._facts.clear()
        self._rules.clear()
        self._entities.clear()
        self._justifications.clear()
        self._derived_from.clear()
