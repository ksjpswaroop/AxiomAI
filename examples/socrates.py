"""
AxiomAI Socrates Demo
Classic logic example: All humans are mortal, Socrates is human, therefore Socrates is mortal.
"""

from axiomai import Reasoner


def demo_basic():
    print("=" * 60)
    print("AxiomAI — Socrates Demo")
    print("=" * 60)

    r = Reasoner()

    # Load facts
    r.add_fact("Human(Socrates)")
    r.add_fact("Human(Plato)")
    r.add_fact("Rational(Socrates)")

    # Load rule: IF Human(x) THEN Mortal(x)
    r.add_rule("IF Human(x) THEN Mortal(x)")

    # Load rule: IF Human(x) AND Rational(x) THEN Person(x)
    r.add_rule("IF Human(x) AND Rational(x) THEN Person(x)")

    print("\nFacts:")
    for f in r.list_facts():
        print(f"  • {f.predicate}")

    print("\nRules:")
    for rule in r.list_rules():
        print(f"  • {rule}")

    print("\n" + "-" * 60)
    print("QUERY: Mortal(Socrates)?")
    print("-" * 60)
    result = r.ask("Mortal(Socrates)")
    print(f"Result: {result.result}")
    print(f"Mode: {result.reasoning_mode}")
    print(f"Duration: {result.duration_ms:.2f}ms")
    print()
    print("Explanation (short):")
    print(result.explain("short"))
    print()
    print("Proof Tree:")
    print(result.proof.to_text())

    print("\n" + "-" * 60)
    print("QUERY: Person(Socrates)?")
    print("-" * 60)
    result2 = r.ask("Person(Socrates)")
    print(f"Result: {result2.result}")
    print(result2.explain("medium"))

    print("\n" + "-" * 60)
    print("Forward Chaining — Derive ALL facts")
    print("-" * 60)
    fc = r.derive_all()
    print(f"New facts derived: {len(fc.new_facts)}")
    for f in fc.new_facts:
        print(f"  + {f.predicate}")
    print()
    print("Full trace:")
    print(fc.proof.to_text())

    print("\n" + "-" * 60)
    print("Contradiction Check")
    print("-" * 60)
    print(f"Consistent: {r.is_consistent()}")

    print("\n" + "-" * 60)
    print("KB Fingerprint (deterministic hash)")
    print("-" * 60)
    print(f"Fingerprint: {r.fingerprint()}")


def demo_medical():
    """Medical diagnosis example — more complex."""
    print("\n" + "=" * 60)
    print("Medical Diagnosis Demo")
    print("=" * 60)

    r = Reasoner()

    # Patient facts
    r.add_fact("Patient(John)")
    r.add_fact("Symptom(John, Fever)")
    r.add_fact("Symptom(John, Cough)")
    r.add_fact("Symptom(John, ChestPain)")

    # Rules
    r.add_rule("IF Symptom(x, Fever) AND Symptom(x, Cough) THEN Has(x, RespiratoryInfection)")
    r.add_rule("IF Has(x, RespiratoryInfection) AND Symptom(x, ChestPain) THEN Has(x, PneumoniaRisk)")
    r.add_rule("IF Has(x, PneumoniaRisk) THEN Recommend(x, ChestXRay)")
    r.add_rule("IF Has(x, RespiratoryInfection) THEN Recommend(x, Rest)")
    r.add_rule("IF Recommend(x, ChestXRay) THEN MustDo(x, ChestXRay)")

    print("\nPatient John — Facts:")
    for f in r.list_facts():
        print(f"  • {f.predicate}")

    print("\nQueries:")
    for query in ["Has(John, RespiratoryInfection)", "Has(John, PneumoniaRisk)", "Recommend(John, ChestXRay)"]:
        result = r.ask(query)
        print(f"  {query}? → {result.result}")
        print(f"    {result.explain('one_line')}")

    print("\nAll derived facts (forward chain):")
    fc = r.derive_all()
    for f in fc.new_facts:
        print(f"  + {f.predicate}")


def demo_planning():
    """STRIPS planning example."""
    print("\n" + "=" * 60)
    print("Planning Demo — Airport Run")
    print("=" * 60)

    r = Reasoner()

    r.add_action(
        "GetInCar",
        preconditions=["HasCar", "AtHome"],
        add_effects=["InCar"],
        del_effects=["AtHome"],
    )
    r.add_action(
        "DriveToAirport",
        preconditions=["InCar", "License"],
        add_effects=["AtAirport"],
        del_effects=["AtHome", "InCar"],
    )

    plan = r.plan(
        initial_state={"HasCar", "License", "AtHome"},
        goal={"AtAirport"},
    )

    print(f"Plan found: {plan.found}")
    if plan.found:
        print(f"Actions ({plan.cost} steps):")
        for action in plan.actions:
            print(f"  → {action}")
    else:
        print(f"Failed: {plan.failure_reason}")


def demo_sudoku():
    """Sudoku solver demo."""
    print("\n" + "=" * 60)
    print("Sudoku Solver Demo")
    print("=" * 60)

    from axiomai.reasoner.engines.constraints import solve_sudoku

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
    if solution:
        print("Puzzle:")
        for row in puzzle:
            print("  " + " ".join(str(c) if c != 0 else "." for c in row))
        print("\nSolution:")
        for row in solution:
            print("  " + " ".join(str(c) for c in row))
    else:
        print("No solution found")


def demo_llm_guard():
    """
    Demo: LLM generates claims → AxiomAI verifies them.
    This is the key product use case: LLM claim verifier.
    """
    print("\n" + "=" * 60)
    print("LLM Guard Demo — Claim Verification")
    print("=" * 60)

    r = Reasoner()

    # Ground truth from authoritative source
    r.add_fact("ProductCategory(WidgetA, Electronics)", source="catalog:v1.json")
    r.add_fact("RequiresCertification(WidgetA, FCC)", source="catalog:v1.json")
    r.add_fact("HasCertification(WidgetB, FCC)", source="certdb:2024.json")

    # LLM-extracted claim (simulated)
    print("\nLLM Claim: 'WidgetA has FCC certification'")
    result = r.ask("HasCertification(WidgetA, FCC)")
    print(f"  AxiomAI says: {result.result}")
    if result.result == "DISPROVED":
        print(f"  Proof: {result.explain('short')}")
        print("  → LLM claim is HALLUCINATED. Reject.")

    print("\nLLM Claim: 'WidgetB has FCC certification'")
    result2 = r.ask("HasCertification(WidgetB, FCC)")
    print(f"  AxiomAI says: {result2.result}")
    if result2.result == "PROVED":
        print("  → LLM claim is VERIFIED. Accept.")


if __name__ == "__main__":
    demo_basic()
    demo_medical()
    demo_planning()
    demo_sudoku()
    demo_llm_guard()
