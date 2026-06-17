"""
Z3 Adapter — Connect Z3 solver to the reasoning engine.
"""

from __future__ import annotations

from z3 import (
    Solver, Int, Bool, Real, String, FreshInt,
    sat, unsat, unknown,
    Or, And, Not, Implies, Xor,
    ForAll, Exists,
)
from ..engines.constraints import ConstraintSolver


class Z3Adapter:
    """
    Bridge between AxiomAI predicates and Z3 symbolic reasoning.
    Useful for: quantified formulas, arithmetic, formal verification.
    """

    def __init__(self):
        self._solver = Solver()
        self._vars: dict[str, object] = {}

    def declare_int(self, name: str, min_val=None, max_val=None):
        """Declare an integer variable."""
        v = Int(name)
        self._vars[name] = v
        if min_val is not None:
            self._solver.add(v >= min_val)
        if max_val is not None:
            self._solver.add(v <= max_val)
        return v

    def declare_bool(self, name: str):
        """Declare a Boolean variable."""
        v = Bool(name)
        self._vars[name] = v
        return v

    def assert_prop(self, prop):
        """Add a Z3 property to the solver."""
        self._solver.add(prop)

    def assert_or(self, *props):
        self._solver.add(Or(*props))

    def assert_and(self, *props):
        self._solver.add(And(*props))

    def prove(self, proposition) -> bool:
        """Attempt to prove a proposition (check if it must be true)."""
        old = self._solver
        self._solver = Solver()
        self._solver.set(unsat_core=True)
        # Copy vars
        for name, var in self._vars.items():
            if isinstance(var, Int):
                Int(name)
            elif isinstance(var, Bool):
                Bool(name)
        self._solver.add(Not(proposition))
        result = self._solver.check()
        self._solver = old
        return result == unsat

    def check_sat(self) -> bool:
        return self._solver.check() == sat

    def model(self) -> dict:
        """Get current model assignments."""
        if self._solver.check() != sat:
            return {}
        m = self._solver.model()
        return {d.name(): m[d] for d in m.decls()}

    def get_vars(self) -> dict:
        return self._vars

    def to_z3(self) -> Solver:
        return self._solver
