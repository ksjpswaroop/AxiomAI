"""
Constraint Solving — Z3-backed CSP solver.
"""

from __future__ import annotations

from z3 import Solver, Int, If, sat, unsat
import json


class ConstraintSolver:
    """
    Z3-backed constraint satisfaction solver.
    
    Usage:
        solver = ConstraintSolver()
        solver.var("x", 1, 10)
        solver.var("y", 1, 10)
        solver.add_constraint("x + y <= 12")
        result = solver.solve()
    """

    def __init__(self):
        self._vars: dict[str, Int] = {}
        self._solver = Solver()
        self._domains: dict[str, tuple[int, int]] = {}

    def var(self, name: str, min_val: int, max_val: int):
        """Declare an integer variable with domain [min, max]."""
        self._vars[name] = Int(name)
        self._domains[name] = (min_val, max_val)
        self._solver.add(self._vars[name] >= min_val, self._vars[name] <= max_val)

    def add_constraint(self, constraint: str):
        """
        Add a constraint expression.
        E.g. "x + y <= 12", "x != y", "x * 2 == y"
        """
        # Map variable names to Z3 Int objects
        local_vars = {k: v for k, v in self._vars.items()}
        # Evaluate constraint string in Z3 context
        try:
            # Use Z3's Python API directly for safety
            self._solver.add(eval(constraint, {"x": self._vars.get("x"), "y": self._vars.get("y"), 
                                                "z": self._vars.get("z"), 
                                                "If": If, "Int": Int}))
        except Exception as e:
            raise ValueError(f"Invalid constraint: {constraint} — {e}")

    def solve(self) -> dict | None:
        """Solve the CSP. Returns assignment dict or None if unsatisfiable."""
        if self._solver.check() == sat:
            model = self._solver.model()
            return {d.name(): model[d].as_long() for d in model.decls()}
        return None

    def solve_all(self, max_models: int = 10) -> list[dict]:
        """Return up to max_models solutions."""
        results = []
        while len(results) < max_models:
            if self._solver.check() == sat:
                model = self._solver.model()
                assignment = {d.name(): model[d].as_long() for d in model.decls()}
                results.append(assignment)
                # Block this model to find the next
                block = [d() != model[d] for d in model.decls()]
                self._solver.add(block)
            else:
                break
        return results

    def is_satisfiable(self) -> bool:
        return self._solver.check() == sat

    def is_unsatisfiable(self) -> bool:
        return self._solver.check() == unsat


def solve_sudoku(grid: list[list[int]]) -> dict | None:
    """
    Solve a 9x9 Sudoku puzzle.
    grid[i][j] = 0 means empty cell.
    Returns 9x9 solution or None.
    """
    solver = ConstraintSolver()

    # Create 81 variables
    for i in range(9):
        for j in range(9):
            solver.var(f"c{i}{j}", 1, 9)

    # Row constraints
    for i in range(9):
        for a in range(9):
            for b in range(a + 1, 9):
                solver.add_constraint(f"c{i}{a} != c{i}{b}")

    # Column constraints
    for j in range(9):
        for a in range(9):
            for b in range(a + 1, 9):
                solver.add_constraint(f"c{a}{j} != c{b}{j}")

    # 3x3 block constraints
    for bi in range(3):
        for bj in range(3):
            cells = [(bi * 3 + i, bj * 3 + j) for i in range(3) for j in range(3)]
            for a in range(9):
                for b in range(a + 1, 9):
                    solver.add_constraint(f"c{cells[a][0]}{cells[a][1]} != c{cells[b][0]}{cells[b][1]}")

    # Pre-filled cells
    for i in range(9):
        for j in range(9):
            if grid[i][j] != 0:
                solver.add_constraint(f"c{i}{j} == {grid[i][j]}")

    result = solver.solve()
    if result is None:
        return None

    # Convert back to 9x9 grid
    solution = [[0] * 9 for _ in range(9)]
    for i in range(9):
        for j in range(9):
            solution[i][j] = result[f"c{i}{j}"]
    return solution
