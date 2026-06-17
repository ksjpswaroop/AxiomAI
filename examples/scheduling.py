"""
Scheduling Example — CSP with Z3.
"""

from axiomai.constraints import ConstraintSolver, solve_sudoku


def scheduling_example():
    """Simple job scheduling with resource constraints."""
    print("=== Job Scheduling CSP ===")
    
    solver = ConstraintSolver()
    
    # Three jobs: A, B, C
    # Each has a start time between 0 and 10
    solver.var("start_A", 0, 10)
    solver.var("start_B", 0, 10)
    solver.var("start_C", 0, 10)
    
    # Durations
    dur_A, dur_B, dur_C = 3, 2, 4
    
    # Job A and B cannot overlap (share a resource)
    # Constraint: start_A + dur_A <= start_B OR start_B + dur_B <= start_A
    # Simplified: |start_A - start_B| >= max(dur_A, dur_B)
    solver.add_constraint(f"(start_A + {dur_A} <= start_B) or (start_B + {dur_B} <= start_A)")
    
    # Job C must start after A finishes
    solver.add_constraint(f"start_C >= start_A + {dur_A}")
    
    # Find all solutions
    solutions = solver.solve_all(max_models=3)
    print(f"Found {len(solutions)} solutions:")
    for i, sol in enumerate(solutions, 1):
        print(f"  Solution {i}: {sol}")


def sudoku_example():
    """Solve a Sudoku puzzle."""
    print("\n=== Sudoku Solver ===")
    
    # Easy Sudoku (0 = empty)
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
    
    print("Puzzle:")
    for row in puzzle:
        print("  " + " ".join(str(c) if c != 0 else "." for c in row))
    
    solution = solve_sudoku(puzzle)
    
    if solution:
        print("\nSolution:")
        for row in solution:
            print("  " + " ".join(str(c) for c in row))
    else:
        print("\nNo solution found!")


if __name__ == "__main__":
    scheduling_example()
    sudoku_example()
