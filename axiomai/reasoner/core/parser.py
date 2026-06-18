"""
Parser — Parse predicate strings into structured objects.
"""

from __future__ import annotations

import re

from ..core.models import Entity, Fact, Predicate, Rule


class ParserError(ValueError):
    """Raised when parsing fails."""
    pass


class Parser:
    """
    Parse predicate strings into structured logic objects.

    Supported syntax:
      - Human(Socrates)
      - IF Human(x) AND Rational(x) THEN Person(x)
      - Human(x) -> Mortal(x)
      - Fact: Human(Socrates)
      - Entity: Socrates [Person]
    """

    def __init__(self):
        self._entity_cache: dict[str, Entity] = {}

    def parse_predicate(self, s: str) -> Predicate:
        """Parse a predicate string."""
        s = s.strip()
        try:
            return Predicate.parse(s)
        except Exception as e:
            raise ParserError(f"Invalid predicate '{s}': {e}")

    def parse_fact(self, s: str, source: str = "user") -> Fact:
        """Parse a fact string."""
        s = s.strip()
        if s.startswith("Fact:"):
            s = s[5:].strip()
        try:
            pred = Predicate.parse(s)
            return Fact.create(pred, source=source, confidence_source="asserted")
        except Exception as e:
            raise ParserError(f"Invalid fact '{s}': {e}")

    def parse_rule(self, s: str, priority: int = 1) -> Rule:
        """Parse a rule string."""
        try:
            return Rule.parse(s, priority=priority)
        except Exception as e:
            raise ParserError(f"Invalid rule '{s}': {e}")

    def parse_entity(self, s: str) -> Entity:
        """Parse 'EntityName [Type]' or just 'EntityName'."""
        s = s.strip()
        match = re.match(r"^(\w+)(?:\s*\[(\w+)\])?$", s)
        if not match:
            raise ParserError(f"Invalid entity syntax: {s}")
        name, type_ = match.groups()
        if name in self._entity_cache:
            return self._entity_cache[name]
        entity = Entity(name=name, type=type_)
        self._entity_cache[name] = entity
        return entity

    def parse_query(self, s: str) -> tuple[Predicate, dict]:
        """
        Parse a query with optional bindings.
        E.g. 'Mortal(Socrates)' -> predicate + {}
        E.g. 'Mortal(x) where x=Socrates' -> predicate + {x: Socrates}
        """
        s = s.strip()
        bindings = {}

        if " where " in s:
            query_part, binding_part = s.split(" where ", 1)
            s = query_part.strip()
            for binding in binding_part.split(","):
                binding = binding.strip()
                if "=" in binding:
                    var, val = binding.split("=", 1)
                    bindings[var.strip()] = val.strip()

        pred = self.parse_predicate(s)
        return pred, bindings

    def is_variable(self, s: str) -> bool:
        """Check if a string represents a variable."""
        s = s.strip()
        if not s:
            return False
        return (
            s[0].islower()
            and s not in ("true", "false", "null", "none")
        )

    def is_constant(self, s: str) -> bool:
        """Check if a string represents a constant."""
        return not self.is_variable(s)
