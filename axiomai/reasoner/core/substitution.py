"""
Substitution — Variable bindings for unification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Substitution:
    """
    A mapping from variables to terms.
    {x: Socrates, y: Plato}
    """
    bindings: dict[str, str] = field(default_factory=dict)

    def add(self, var: str, term: str) -> Substitution:
        result = Substitution(dict(self.bindings))
        result.bindings[var] = term
        return result

    def get(self, var: str) -> Optional[str]:
        return self.bindings.get(var)

    def apply_term_str(self, term_str: str, var_map: dict) -> str:
        """Apply substitution to a term string."""
        if term_str in self.bindings:
            return self.bindings[term_str]
        return term_str

    def compose(self, other: Substitution) -> Substitution:
        """Compose two substitutions: self ∘ other."""
        result = {}
        for v, t in self.bindings.items():
            result[v] = other.get(t) or t
        for v, t in other.bindings.items():
            if v not in result:
                result[v] = t
        return Substitution(result)

    def __contains__(self, var: str) -> bool:
        return var in self.bindings

    def __len__(self) -> int:
        return len(self.bindings)

    def __repr__(self) -> str:
        if not self.bindings:
            return "{}"
        return "{" + ", ".join(f"{k}: {v}" for k, v in self.bindings.items()) + "}"

    def to_dict(self) -> dict:
        return dict(self.bindings)

    @classmethod
    def identity(cls) -> Substitution:
        return cls({})

    @classmethod
    def from_dict(cls, d: dict) -> Substitution:
        return cls(dict(d))
