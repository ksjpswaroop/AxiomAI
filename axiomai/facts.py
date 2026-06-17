"""
Fact Store — Predicate-based fact storage and querying.
"""

from __future__ import annotations

import uuid
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Fact:
    """A single predicate fact."""
    id: str
    predicate: str
    relation: str
    terms: list[str]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_predicate(cls, predicate: str) -> Fact:
        """Parse 'Relation(term1, term2, ...)' into a Fact."""
        match = re.match(r"^(\w+)\((.*)\)$", predicate.strip())
        if not match:
            raise ValueError(f"Invalid predicate syntax: {predicate}")
        relation = match.group(1)
        terms_raw = match.group(2)
        terms = [t.strip() for t in terms_raw.split(",")] if terms_raw.strip() else []
        return cls(
            id=str(uuid.uuid4()),
            predicate=predicate.strip(),
            relation=relation,
            terms=terms,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "predicate": self.predicate,
            "relation": self.relation,
            "terms": self.terms,
            "created_at": self.created_at.isoformat(),
        }


class FactStore:
    """
    In-memory fact store. Thread-safe for single-engine use.
    Replace with SQLite-backed store for persistence.
    """

    def __init__(self):
        self._facts: dict[str, Fact] = {}

    def add(self, predicate: str) -> Fact:
        """Add a fact. Raises if predicate is malformed."""
        fact = Fact.from_predicate(predicate)
        # Key by predicate string for fast lookup (no duplicates)
        self._facts[fact.predicate] = fact
        return fact

    def retract(self, predicate: str) -> bool:
        """Remove a fact by predicate string. Returns True if found."""
        return self._facts.pop(predicate, None) is not None

    def query(self, predicate: str) -> bool:
        """Check if a fact exists in the store."""
        return predicate in self._facts

    def get(self, predicate: str) -> Optional[Fact]:
        """Get a fact by predicate string."""
        return self._facts.get(predicate)

    def list_all(self) -> list[Fact]:
        """Return all facts."""
        return list(self._facts.values())

    def list_by_relation(self, relation: str) -> list[Fact]:
        """Return all facts with a given relation."""
        return [f for f in self._facts.values() if f.relation == relation]

    def clear(self):
        """Remove all facts."""
        self._facts.clear()

    def __len__(self) -> int:
        return len(self._facts)

    def __contains__(self, predicate: str) -> bool:
        return predicate in self._facts
