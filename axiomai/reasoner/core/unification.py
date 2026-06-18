"""
Unification — First-order unification with occurs check.
"""

from __future__ import annotations

from typing import Optional

from .models import Predicate, Term, TermType
from .substitution import Substitution


class UnificationResult:
    def __init__(
        self,
        success: bool,
        substitution: Optional[Substitution] = None,
        error: Optional[str] = None,
    ):
        self.success = success
        self.substitution = substitution or Substitution.identity()
        self.error = error

    def __repr__(self) -> str:
        if self.success:
            return f"UnificationResult(success=True, subst={self.substitution})"
        return f"UnificationResult(success=False, error={self.error})"


class UnificationEngine:
    """
    First-order unification with occurs check.
    Deterministic: same inputs always produce same output.
    """

    def __init__(self):
        self._stats = {"unifications": 0, "failures": 0}

    def unify(
        self,
        p1: Predicate,
        p2: Predicate,
        subst: Optional[Substitution] = None,
    ) -> UnificationResult:
        """Unify two predicates under an optional existing substitution."""
        self._stats["unifications"] += 1
        subst = subst or Substitution.identity()

        if p1.relation != p2.relation:
            self._stats["failures"] += 1
            return UnificationResult(False, error=f"Relation mismatch: {p1.relation} ≠ {p2.relation}")

        if len(p1.terms) != len(p2.terms):
            self._stats["failures"] += 1
            return UnificationResult(False, error=f"Arity mismatch: {len(p1.terms)} vs {len(p2.terms)}")

        return self._unify_terms(p1.terms, p2.terms, subst)

    def _unify_terms(
        self,
        terms1: list[Term],
        terms2: list[Term],
        subst: Substitution,
    ) -> UnificationResult:
        if not terms1 and not terms2:
            return UnificationResult(True, subst)
        if not terms1 or not terms2:
            return UnificationResult(False, error="Term list length mismatch")

        t1 = terms1[0]
        t2 = terms2[0]
        result = self._unify_term(t1, t2, subst)
        if not result.success:
            return result
        return self._unify_terms(terms1[1:], terms2[1:], result.substitution)

    def _unify_term(
        self,
        t1: Term,
        t2: Term,
        subst: Substitution,
    ) -> UnificationResult:
        """Unify a single pair of terms."""
        t1 = self._apply_subst_to_term(t1, subst)
        t2 = self._apply_subst_to_term(t2, subst)

        if t1.name == t2.name and t1.type == t2.type:
            return UnificationResult(True, subst)

        if t1.is_constant() and t2.is_constant():
            if t1.name != t2.name:
                return UnificationResult(False, error=f"Constant conflict: {t1.name} ≠ {t2.name}")
            return UnificationResult(True, subst)

        if t1.is_variable():
            return self._unify_variable_with_term(t1, t2, subst)
        if t2.is_variable():
            return self._unify_variable_with_term(t2, t1, subst)

        return UnificationResult(False, error=f"Cannot unify {t1} with {t2}")

    def _unify_variable_with_term(
        self,
        var: Term,
        other: Term,
        subst: Substitution,
    ) -> UnificationResult:
        """Unify a variable with another term, with occurs check."""
        if self._occurs_check(var.name, other):
            return UnificationResult(False, error=f"Occurs check failed: {var.name} in {other}")

        if var.name in subst:
            existing = subst.get(var.name)
            existing_term = Term(existing, TermType.CONSTANT)
            return self._unify_term(existing_term, other, subst)

        new_subst = subst.add(var.name, other.name)
        return UnificationResult(True, new_subst)

    def _occurs_check(self, var_name: str, term: Term) -> bool:
        """Check if a variable occurs in a term (recursive)."""
        if term.is_variable() and term.name == var_name:
            return True
        return False

    def _apply_subst_to_term(self, term: Term, subst: Substitution) -> Term:
        """Apply substitution to a term."""
        if term.is_variable() and term.name in subst:
            return Term(subst.get(term.name), TermType.CONSTANT)
        return term

    def match(self, pattern: Predicate, target: Predicate) -> Optional[Substitution]:
        """Match a pattern against a target (one-way unification)."""
        result = self.unify(pattern, target)
        return result.substitution if result.success else None

    def is_more_general(self, p1: Predicate, p2: Predicate) -> bool:
        """Check if p1 is more general than p2."""
        vars1 = sum(1 for t in p1.terms if t.is_variable())
        vars2 = sum(1 for t in p2.terms if t.is_variable())
        return vars1 >= vars2

    def stats(self) -> dict:
        return dict(self._stats)
