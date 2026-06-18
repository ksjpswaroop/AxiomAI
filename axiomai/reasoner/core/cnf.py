"""
CNF — Convert facts and rules to conjunctive normal form clauses.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import Fact, Rule, Predicate
from ..kb.store import KnowledgeBase


@dataclass(frozen=True)
class Literal:
    """A single literal: predicate with optional negation."""

    predicate: Predicate
    negated: bool = False

    def __str__(self) -> str:
        p = str(self.predicate)
        return f"¬{p}" if self.negated else p

    def complement(self) -> Literal:
        return Literal(self.predicate, not self.negated)

    @classmethod
    def from_string(cls, s: str) -> Literal:
        s = s.strip()
        negated = False
        if s.startswith("¬") or s.upper().startswith("NOT "):
            negated = True
            s = s.lstrip("¬").strip()
            if s.upper().startswith("NOT "):
                s = s[4:].strip()
        return cls(Predicate.parse(s), negated=negated)

    def substitute(self, bindings: dict[str, str]) -> Literal:
        return Literal(self.predicate.substitute(bindings), self.negated)


@dataclass
class Clause:
    """A disjunction of literals (CNF clause)."""

    literals: list[Literal] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash(tuple(sorted(str(l) for l in self.literals)))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Clause):
            return False
        return {str(l) for l in self.literals} == {str(l) for l in other.literals}

    def is_empty(self) -> bool:
        return len(self.literals) == 0

    def contains_literal(self, other: Literal) -> bool:
        return any(str(l) == str(other) for l in self.literals)


def fact_to_clause(fact: Fact) -> Clause:
    """A ground fact is a unit clause."""
    lit = Literal.from_string(str(fact.predicate))
    return Clause([lit])


def rule_to_clauses(rule: Rule) -> list[Clause]:
    """
    Convert a rule to CNF clause(s).

    IF A AND B THEN C  →  ¬A ∨ ¬B ∨ C
    IF A OR B THEN C   →  (¬A ∨ C) AND (¬B ∨ C)
    """
    if not rule.consequent:
        return []

    consequent_lit = Literal(rule.consequent, negated=False)

    if rule.antecedent_operator == "or":
        return [
            Clause([Literal(ant, negated=True), consequent_lit])
            for ant in rule.antecedents
        ]

    antecedent_lits = [Literal(ant, negated=True) for ant in rule.antecedents]
    return [Clause(antecedent_lits + [consequent_lit])]


def kb_to_clauses(kb: KnowledgeBase) -> list[Clause]:
    """Convert all active facts and enabled rules to CNF clauses."""
    clauses: list[Clause] = []
    for fact in kb.list_active_facts():
        clauses.append(fact_to_clause(fact))
    for rule in kb.get_enabled_rules():
        clauses.extend(rule_to_clauses(rule))
    return clauses


def clause_key(clause: Clause) -> str:
    """Deterministic key for clause deduplication."""
    return "|".join(sorted(str(l) for l in clause.literals))
