"""
CNF — Convert facts and rules to conjunctive normal form clauses.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..kb.store import KnowledgeBase
from .models import Fact, Predicate, Rule
from .unification import UnificationEngine


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
        return hash(tuple(sorted(str(lit) for lit in self.literals)))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Clause):
            return False
        return {str(lit) for lit in self.literals} == {str(lit) for lit in other.literals}

    def is_empty(self) -> bool:
        return len(self.literals) == 0

    def contains_literal(self, other: Literal) -> bool:
        return any(str(lit) == str(other) for lit in self.literals)


def fact_to_clause(fact: Fact) -> Clause:
    """A ground fact is a unit clause (supports negated facts)."""
    pred_str = str(fact.predicate)
    if fact.metadata.get("negated"):
        return Clause([Literal.from_string(f"¬{pred_str}")])
    return Clause([Literal.from_string(pred_str)])


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
    return "|".join(sorted(str(lit) for lit in clause.literals))


def dedupe_literals(literals: list[Literal]) -> list[Literal]:
    """Remove duplicate literals preserving deterministic order."""
    seen: dict[str, Literal] = {}
    for lit in literals:
        seen[str(lit)] = lit
    return [seen[k] for k in sorted(seen.keys())]


def is_tautology(clause: Clause, unification: UnificationEngine) -> bool:
    """True when clause contains complementary unifiable literals."""
    for i, lit1 in enumerate(clause.literals):
        for lit2 in clause.literals[i + 1 :]:
            if lit1.negated == lit2.negated:
                continue
            result = unification.unify(lit1.predicate, lit2.predicate)
            if result.success:
                return True
    return False


def simplify_clause(clause: Clause, unification: UnificationEngine) -> Clause | None:
    """Deduplicate literals and drop tautological clauses."""
    literals = dedupe_literals(clause.literals)
    simplified = Clause(literals)
    if simplified.is_empty():
        return simplified
    if is_tautology(simplified, unification):
        return None
    return simplified


def clause_subsumes(
    sub: Clause,
    sup: Clause,
    unification: UnificationEngine,
) -> bool:
    """
    True if `sub` subsumes `sup` (every literal in sub matches one in sup).

    Ground case: literal set inclusion. First-order: each literal in sub
    has a complementary-sign match in sup under some substitution.
    """
    if sub.is_empty():
        return not sup.is_empty()
    if len(sub.literals) > len(sup.literals):
        return False

    def match_all(subst: dict[str, str], idx: int) -> bool:
        if idx >= len(sub.literals):
            return True
        lit = sub.literals[idx].substitute(subst)
        for candidate in sup.literals:
            if lit.negated != candidate.negated:
                continue
            result = unification.unify(lit.predicate, candidate.predicate)
            if not result.success:
                continue
            merged = {**subst, **result.substitution.to_dict()}
            if match_all(merged, idx + 1):
                return True
        return False

    return match_all({}, 0)


def factor_clause(clause: Clause, unification: UnificationEngine) -> list[Clause]:
    """Factor a clause on unifiable same-polarity literals."""
    if len(clause.literals) < 2:
        return []
    factors: list[Clause] = []
    seen: set[str] = set()
    for i, lit1 in enumerate(clause.literals):
        for j in range(i + 1, len(clause.literals)):
            lit2 = clause.literals[j]
            if lit1.negated != lit2.negated:
                continue
            result = unification.unify(lit1.predicate, lit2.predicate)
            if not result.success:
                continue
            subst = result.substitution.to_dict()
            remaining = [
                clause.literals[k].substitute(subst)
                for k in range(len(clause.literals))
                if k not in (i, j)
            ]
            merged_lit = lit1.substitute(subst)
            factored = simplify_clause(
                Clause(dedupe_literals([merged_lit, *remaining])),
                unification,
            )
            if factored and not factored.is_empty():
                key = clause_key(factored)
                if key not in seen:
                    seen.add(key)
                    factors.append(factored)
    return factors
