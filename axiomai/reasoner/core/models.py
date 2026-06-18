"""
Core Data Models — Predicate, Fact, Rule, Entity, Term.
All structured logic objects for the reasoning engine.
"""

from __future__ import annotations

import uuid
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Union


class TermType(Enum):
    CONSTANT = "constant"   # Socrates, 42, "hello"
    VARIABLE = "variable"    # x, y, person
    FUNCTION = "function"    # Father(x) — returns a term

    def __repr__(self) -> str:
        return self.value


@dataclass
class Term:
    """A single term in a predicate — constant, variable, or function call."""
    name: str
    type: TermType = TermType.CONSTANT

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Term({self.name}, {self.type.value})"

    def is_variable(self) -> bool:
        return self.type == TermType.VARIABLE

    def is_constant(self) -> bool:
        return self.type == TermType.CONSTANT


class Predicate:
    """A predicate expression: Relation(term1, term2, ...) or namespace:Relation(...)"""

    def __init__(
        self,
        relation: str,
        terms: list[Union[str, Term]],
        namespace: str = "default",
    ):
        self.namespace = namespace
        self.relation = relation
        self.terms: list[Term] = [
            t if isinstance(t, Term) else self._parse_term(str(t))
            for t in terms
        ]
        self._str_cache: Optional[str] = None

    @staticmethod
    def _parse_term(t: str) -> Term:
        """Parse a term string into a Term object."""
        t = t.strip()
        if not t:
            return Term(t, TermType.CONSTANT)
        if t[0].islower() and t not in ("true", "false", "null", "none"):
            return Term(t, TermType.VARIABLE)
        return Term(t, TermType.CONSTANT)

    @classmethod
    def parse(cls, s: str) -> Predicate:
        """Parse 'Relation(x, y)' or 'namespace:Relation(x, y)'."""
        s = s.strip()
        namespace = "default"
        if ":" in s.split("(")[0]:
            ns_part, remainder = s.split(":", 1)
            namespace = ns_part
            s = remainder
        match = re.match(r"^(\w+)\((.*)\)$", s)
        if not match:
            raise ValueError(f"Invalid predicate syntax: {s}")
        rel = match.group(1)
        terms_str = match.group(2).strip()
        if not terms_str:
            terms: list[str] = []
        else:
            terms = cls._split_terms(terms_str)
        return cls(rel, terms, namespace=namespace)

    @staticmethod
    def _split_terms(s: str) -> list[str]:
        """Split by comma, respecting nested parentheses."""
        result, depth = [], 0
        current = []
        for ch in s:
            if ch == '(':
                depth += 1
                current.append(ch)
            elif ch == ')':
                depth -= 1
                current.append(ch)
            elif ch == ',' and depth == 0:
                result.append(''.join(current).strip())
                current = []
            else:
                current.append(ch)
        if current:
            result.append(''.join(current).strip())
        return result

    def __str__(self) -> str:
        if self._str_cache is None:
            prefix = f"{self.namespace}:" if self.namespace != "default" else ""
            self._str_cache = (
                f"{prefix}{self.relation}({', '.join(str(t) for t in self.terms)})"
            )
        return self._str_cache

    def __repr__(self) -> str:
        return f"Predicate({self.relation}, {[str(t) for t in self.terms]})"

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Predicate):
            return False
        return str(self) == str(other)

    def get_variables(self) -> list[Term]:
        return [t for t in self.terms if t.is_variable()]

    def get_constants(self) -> list[Term]:
        return [t for t in self.terms if t.is_constant()]

    def substitute(self, substitution: dict[str, str]) -> Predicate:
        """Apply variable substitutions to a copy of this predicate."""
        new_terms = []
        for t in self.terms:
            if t.is_variable() and t.name in substitution:
                new_terms.append(Term(substitution[t.name], TermType.CONSTANT))
            else:
                new_terms.append(t)
        return Predicate(self.relation, new_terms, namespace=self.namespace)


@dataclass
class Fact:
    """An atomic fact in the knowledge base."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    predicate: Predicate = field(default_factory=lambda: Predicate("", []))
    source: Optional[str] = None
    source_doc: Optional[str] = None
    confidence_source: str = "asserted"
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict = field(default_factory=dict)

    @classmethod
    def create(cls, predicate: Union[str, Predicate], **kwargs) -> Fact:
        negated = False
        if isinstance(predicate, str):
            s = predicate.strip()
            if s.startswith("¬") or s.upper().startswith("NOT "):
                negated = True
                s = s.lstrip("¬").strip()
                if s.upper().startswith("NOT "):
                    s = s[4:].strip()
                predicate = Predicate.parse(s)
            else:
                predicate = Predicate.parse(s)
        metadata = kwargs.pop("metadata", {})
        if negated:
            metadata = {**metadata, "negated": True}
        return cls(predicate=predicate, metadata=metadata, **kwargs)

    def is_valid_at(self, dt: Optional[datetime] = None) -> bool:
        if self.valid_from is None and self.valid_to is None:
            return True
        dt = dt or datetime.now(timezone.utc)
        if self.valid_from and dt < self.valid_from:
            return False
        if self.valid_to and dt > self.valid_to:
            return False
        return True

    def __str__(self) -> str:
        return str(self.predicate)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "predicate": str(self.predicate),
            "relation": self.predicate.relation,
            "terms": [str(t) for t in self.predicate.terms],
            "source": self.source,
            "confidence_source": self.confidence_source,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_to": self.valid_to.isoformat() if self.valid_to else None,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class Rule:
    """An IF-THEN rule."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    antecedents: list[Predicate] = field(default_factory=list)
    consequent: Optional[Predicate] = None
    antecedent_operator: str = "and"  # "and" or "or"
    priority: int = 1
    author: Optional[str] = None
    domain: Optional[str] = None
    source: Optional[str] = None
    confidence_source: str = "asserted"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict = field(default_factory=dict)
    enabled: bool = True

    @classmethod
    def parse(cls, rule_str: str, priority: int = 1, **kwargs) -> Rule:
        """Parse 'IF Human(x) THEN Mortal(x)' or 'Human(x) -> Mortal(x)'."""
        rule_str = rule_str.strip()
        antecedent_operator = "and"

        if_match = re.match(r"IF\s+(.+?)\s+THEN\s+(.+)$", rule_str, re.IGNORECASE)
        if if_match:
            ant_part = if_match.group(1).strip()
            cons_str = if_match.group(2).strip()
            if re.search(r"\s+OR\s+", ant_part, re.IGNORECASE):
                antecedent_operator = "or"
                ant_strs = [a.strip() for a in re.split(r"\s+OR\s+", ant_part, flags=re.IGNORECASE)]
            else:
                ant_strs = [a.strip() for a in re.split(r"\s+AND\s+", ant_part, flags=re.IGNORECASE)]
        else:
            arrow_match = re.match(r"^(.+?)\s*->\s*(.+)$", rule_str)
            if not arrow_match:
                raise ValueError(f"Invalid rule syntax: {rule_str}")
            ant_part = arrow_match.group(1).strip()
            cons_str = arrow_match.group(2).strip()
            if re.search(r"\s+OR\s+", ant_part, re.IGNORECASE):
                antecedent_operator = "or"
                ant_strs = [a.strip() for a in re.split(r"\s+OR\s+", ant_part, flags=re.IGNORECASE)]
            else:
                ant_strs = [a.strip() for a in ant_part.split(" AND ")]

        antecedents = [Predicate.parse(a) for a in ant_strs]
        consequent = Predicate.parse(cons_str)

        return cls(
            antecedents=antecedents,
            consequent=consequent,
            antecedent_operator=antecedent_operator,
            priority=priority,
            **kwargs,
        )

    def __str__(self) -> str:
        ants = " AND ".join(str(a) for a in self.antecedents)
        return f"IF {ants} THEN {self.consequent}"

    def __repr__(self) -> str:
        return f"Rule({self.antecedents} → {self.consequent}, priority={self.priority})"

    def get_all_variables(self) -> set[str]:
        vars_ = set()
        for ant in self.antecedents:
            for t in ant.get_variables():
                vars_.add(t.name)
        if self.consequent:
            for t in self.consequent.get_variables():
                vars_.add(t.name)
        return vars_

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "antecedents": [str(a) for a in self.antecedents],
            "consequent": str(self.consequent) if self.consequent else None,
            "priority": self.priority,
            "author": self.author,
            "domain": self.domain,
            "source": self.source,
            "confidence_source": self.confidence_source,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class Entity:
    """A named entity in the knowledge base."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: Optional[str] = None
    namespace: str = "default"
    attributes: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __str__(self) -> str:
        return self.name


@dataclass
class RelationDef:
    """A relation definition in the ontology."""
    name: str = ""
    domain_types: list[str] = field(default_factory=list)
    range_types: list[str] = field(default_factory=list)
    is_symmetric: bool = False
    is_transitive: bool = False
    is_functional: bool = False
    inverse: Optional[str] = None
    namespace: str = "default"
