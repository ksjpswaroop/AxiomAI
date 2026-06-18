"""
KB Store — In-memory knowledge base store.
SQLite and graph-backed stores extend this.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union

from ..core.models import Entity, Fact, Predicate, RelationDef, Rule
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
        self._justifications: dict[str, list[str]] = {}
        self._derived_from: dict[str, list[str]] = {}
        self._dependents: dict[str, list[str]] = {}
        self._ordering = OrderingEngine()
        self._stats = {"adds": 0, "queries": 0, "retractions": 0}

    def _fact_key(self, predicate: Union[str, Predicate], fact: Optional[Fact] = None) -> str:
        if isinstance(predicate, str):
            return predicate
        base = str(predicate)
        if fact and fact.metadata.get("negated"):
            return f"¬{base}"
        return base

    # ── Facts ────────────────────────────────────────────────────────────────

    def add_fact(self, fact: Fact) -> Fact:
        """Add a fact. Idempotent — same predicate replaces existing."""
        self._stats["adds"] += 1
        key = self._fact_key(fact.predicate, fact)
        self._facts[key] = fact
        return fact

    def add_derived_fact(
        self,
        fact: Fact,
        rule_ids: list[str],
        source_fact_keys: list[str],
    ) -> Fact:
        """Add a derived fact with provenance for truth maintenance."""
        key = self._fact_key(fact.predicate, fact)
        self._facts[key] = fact
        self._justifications[fact.id] = rule_ids
        self._derived_from[fact.id] = source_fact_keys
        for src_key in source_fact_keys:
            self._dependents.setdefault(src_key, []).append(key)
        self._stats["adds"] += 1
        return fact

    def retract_fact(self, predicate_str: str) -> bool:
        """Remove a fact and cascade to dependents."""
        if predicate_str not in self._facts:
            return False
        self._stats["retractions"] += 1
        to_remove = self._collect_dependents(predicate_str)
        to_remove.add(predicate_str)
        for key in to_remove:
            fact = self._facts.pop(key, None)
            if fact:
                self._justifications.pop(fact.id, None)
                self._derived_from.pop(fact.id, None)
            self._dependents.pop(key, None)
        return True

    def _collect_dependents(self, fact_key: str) -> set[str]:
        """Collect all facts transitively derived from fact_key."""
        collected: set[str] = set()
        stack = list(self._dependents.get(fact_key, []))
        while stack:
            key = stack.pop()
            if key in collected:
                continue
            collected.add(key)
            stack.extend(self._dependents.get(key, []))
        return collected

    def query_fact(self, predicate_str: str, at: Optional[datetime] = None) -> bool:
        """Check if an active fact exists."""
        self._stats["queries"] += 1
        fact = self._facts.get(predicate_str)
        if fact is None:
            return False
        return fact.is_valid_at(at)

    def get_fact(self, predicate_str: str) -> Optional[Fact]:
        fact = self._facts.get(predicate_str)
        if fact and fact.is_valid_at():
            return fact
        return None

    def list_facts(self) -> list[Fact]:
        """Return all facts sorted deterministically."""
        return self._ordering.sort_facts(list(self._facts.values()))

    def list_active_facts(self, at: Optional[datetime] = None) -> list[Fact]:
        """Return facts valid at the given time (default: now)."""
        return self._ordering.sort_facts(
            [f for f in self._facts.values() if f.is_valid_at(at)]
        )

    def list_facts_by_relation(self, relation: str) -> list[Fact]:
        return [
            f for f in self.list_active_facts()
            if f.predicate.relation == relation
        ]

    # ── Rules ───────────────────────────────────────────────────────────────

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
        """Scan active facts for P(x) and ¬P(x) pairs."""
        reports = []
        seen: set[str] = set()
        for fact in self.list_active_facts():
            key = str(fact.predicate)
            if key in seen:
                continue
            neg_str = f"¬{key}"
            if neg_str in self._facts and self._facts[neg_str].is_valid_at():
                reports.append(ContradictionReport(
                    fact1=fact,
                    fact2=self._facts[neg_str],
                    explanation=f"Direct contradiction: {fact.predicate} and ¬{fact.predicate}",
                ))
                seen.add(key)
                seen.add(neg_str)
        return reports

    def is_consistent(self) -> bool:
        return len(self.detect_contradictions()) == 0

    def snapshot(self) -> str:
        """Immutable hash ID for current KB state."""
        parts = sorted(self._facts.keys()) + [str(r) for r in self.list_rules()]
        content = "|".join(parts)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def record_inference_run(
        self,
        query: str,
        mode: str,
        result: str,
        duration_ms: float,
        run_hash: str,
    ) -> str:
        """No-op for in-memory KB. Overridden by PersistentKnowledgeBase."""
        return ""

    def record_proof(
        self,
        query: str,
        result: str,
        proof_json: str,
        run_hash: Optional[str] = None,
    ) -> str:
        """No-op for in-memory KB. Overridden by PersistentKnowledgeBase."""
        return ""

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
        self._dependents.clear()
