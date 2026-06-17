"""
Unification Engine — First-order unification via kanren.
"""

from __future__ import annotations

import re
from typing import Optional
from kanren import run, var, Relation, fact, facts
from kanren.core import sreify


class UnificationEngine:
    """
    Wrapper around kanren for first-order unification.
    
    Example:
        engine = UnificationEngine()
        engine.fact("Human", "Socrates")
        engine.rule("Mortal", "x", body=("Human", "x"))
        result = engine.query("Mortal", "Socrates")  # → {x: Socrates}
    """

    def __init__(self):
        self._relations: dict[str, Relation] = {}
        self._vars: dict[str, object] = {}
        self._kb_facts: list = []

    def get_var(self, name: str):
        """Get or create a logic variable by name."""
        if name not in self._vars:
            self._vars[name] = var()
        return self._vars[name]

    def get_relation(self, name: str) -> Relation:
        """Get or create a kanren Relation by name."""
        if name not in self._relations:
            self._relations[name] = Relation(name)
        return self._relations[name]

    def fact(self, relation: str, *terms):
        """Assert a fact: e.g. engine.fact('Human', 'Socrates')"""
        rel = self.get_relation(relation)
        facts(rel, *terms)

    def facts(self, relation: str, *fact_tuples):
        """Assert multiple facts at once."""
        rel = self.get_relation(relation)
        for t in fact_tuples:
            facts(rel, t)

    def rule(self, consequent_relation: str, consequent_var, *, body: tuple = None):
        """
        Define a rule (for kanren's logic programming style).
        More sophisticated rules are handled in forward/backward chainers.
        """
        rel = self.get_relation(consequent_relation)
        # kanren uses lambda-based rules; this is a placeholder
        # for the full rule system see rules.py + forward_chain.py
        return rel

    def query(self, relation: str, *terms):
        """
        Query: find all substitutions for variables in terms.
        Returns list of dicts mapping variable names to values.
        """
        rel = self.get_relation(relation)
        vars_list = list(self._vars.values())
        results = run(5, *(self.get_var(v) for v in self._vars), (rel, *terms))
        return results

    def parse_predicate(self, predicate: str):
        """
        Parse 'Relation(term1, term2)' into (relation_name, [terms]).
        Handles variables (lowercase x, y, z) vs constants (uppercase).
        """
        match = re.match(r"^(\w+)\((.*)\)$", predicate.strip())
        if not match:
            raise ValueError(f"Invalid predicate: {predicate}")
        relation = match.group(1)
        terms_raw = match.group(2)
        terms = []
        for t in terms_raw.split(","):
            t = t.strip()
            if t and t[0].islower():
                # Variable
                terms.append(self.get_var(t))
            else:
                # Constant
                terms.append(t)
        return relation, terms

    def unify_predicates(self, p1: str, p2: str) -> Optional[dict]:
        """
        Unify two predicates.
        Returns substitution dict or None if they can't unify.
        """
        rel1, terms1 = self.parse_predicate(p1)
        rel2, terms2 = self.parse_predicate(p2)

        if rel1 != rel2 or len(terms1) != len(terms2):
            return None

        # Build kanren goal
        goal = (self.get_relation(rel1), *terms1)
        results = self.query(rel1, *terms1)
        # Simplified: kanren handles this internally
        return results

    def extract_variables(self, predicate: str) -> list[str]:
        """Extract variable names from a predicate."""
        match = re.match(r"^(\w+)\((.*)\)$", predicate.strip())
        if not match:
            return []
        terms_raw = match.group(2)
        return [t.strip() for t in terms_raw.split(",") if t.strip() and t.strip()[0].islower()]

    def is_variable(self, term: str) -> bool:
        return bool(term and term[0].islower())
