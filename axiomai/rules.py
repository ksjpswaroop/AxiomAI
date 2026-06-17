"""
Rule Store — IF-THEN rule storage and querying.
"""

from __future__ import annotations

import uuid
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Rule:
    """A single IF-THEN rule."""
    id: str
    antecedents: list[str]  # e.g. ["Human(x)", "Rational(x)"]
    consequent: str          # e.g. "Mortal(x)"
    priority: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_string(cls, rule_str: str, priority: int = 1) -> Rule:
        """
        Parse 'IF Human(x) THEN Mortal(x)'
        or 'Human(x) -> Mortal(x)'
        """
        rule_str = rule_str.strip()

        # Try "IF ... THEN ..."
        if_match = re.match(r"IF\s+(.+?)\s+THEN\s+(.+)$", rule_str, re.IGNORECASE)
        if if_match:
            antecedents_str = if_match.group(1)
            consequent = if_match.group(2).strip()
        else:
            # Try "A -> B"
            arrow_match = re.match(r"^(.+?)\s*->\s*(.+)$", rule_str)
            if not arrow_match:
                raise ValueError(f"Invalid rule syntax: {rule_str}")
            antecedents_str = arrow_match.group(1).strip()
            consequent = arrow_match.group(2).strip()

        # Split antecedents by " AND "
        antecedents = [a.strip() for a in re.split(r"\s+AND\s+", antecedents_str)]

        return cls(
            id=str(uuid.uuid4()),
            antecedents=antecedents,
            consequent=consequent,
            priority=priority,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "antecedents": self.antecedents,
            "consequent": self.consequent,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        ants = " AND ".join(self.antecedents)
        return f"IF {ants} THEN {self.consequent}"


class RuleStore:
    """In-memory rule store."""

    def __init__(self):
        self._rules: dict[str, Rule] = {}

    def add(self, rule_str: str, priority: int = 1) -> Rule:
        """Add a rule from string. Returns the Rule object."""
        rule = Rule.from_string(rule_str, priority)
        self._rules[rule.id] = rule
        return rule

    def add_rule(self, antecedents: list[str], consequent: str, priority: int = 1) -> Rule:
        """Add a rule from antecedents + consequent."""
        rule = Rule(
            id=str(uuid.uuid4()),
            antecedents=antecedents,
            consequent=consequent,
            priority=priority,
        )
        self._rules[rule.id] = rule
        return rule

    def retract(self, rule_id: str) -> bool:
        """Remove a rule by ID."""
        return self._rules.pop(rule_id, None) is not None

    def get(self, rule_id: str) -> Optional[Rule]:
        return self._rules.get(rule_id)

    def list_all(self) -> list[Rule]:
        """Return all rules sorted by priority (highest first)."""
        return sorted(self._rules.values(), key=lambda r: -r.priority)

    def get_rules_for_consequent(self, consequent_pattern: str) -> list[Rule]:
        """
        Find rules whose consequent matches (unifies with) the pattern.
        Uses simple string matching for MVP; extend with unification later.
        """
        results = []
        for rule in self._rules.values():
            if self._consequent_matches(rule.consequent, consequent_pattern):
                results.append(rule)
        return results

    def _consequent_matches(self, rule_consequent: str, query: str) -> bool:
        """Check if rule consequent could unify with query (simple variable check)."""
        # Extract relation names
        r_match = re.match(r"^(\w+)\(", rule_consequent)
        q_match = re.match(r"^(\w+)\(", query)
        if not r_match or not q_match:
            return False
        return r_match.group(1) == q_match.group(1)

    def clear(self):
        self._rules.clear()

    def __len__(self) -> int:
        return len(self._rules)
