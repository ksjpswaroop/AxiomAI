"""P2-05: Constraint solver tests."""

from __future__ import annotations

from axiomai.reasoner.engines.constraints import ConstraintSolver, solve_sudoku


def test_simple_csp():
    solver = ConstraintSolver()
    solver.var("x", 1, 5)
    solver.var("y", 1, 5)
    solver.add("x + y == 5")
    solver.add("x > y")
    result = solver.solve()
    assert result is not None
    assert result["x"] + result["y"] == 5


def test_csp_unsatisfiable():
    solver = ConstraintSolver()
    solver.var("x", 1, 3)
    solver.add("x > 5")
    assert solver.solve() is None


def test_sudoku_solves_default_puzzle():
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]
    solution = solve_sudoku(puzzle)
    assert solution is not None
    assert all(solution[r][c] != 0 for r in range(9) for c in range(9))


def test_sudoku_rows_valid():
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]
    solution = solve_sudoku(puzzle)
    for row in solution:
        vals = [v for v in row if v != 0]
        assert len(vals) == len(set(vals))
