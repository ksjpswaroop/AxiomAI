"""
Socrates Example — The classic logical reasoning demo.
"""

from axiomai import AxiomEngine


def main():
    # Initialize engine
    engine = AxiomEngine()

    # Load facts
    engine.add_fact("Human(Socrates)")
    engine.add_fact("Human(Plato)")

    # Add rule: IF Human(x) THEN Mortal(x)
    engine.add_rule("IF Human(x) THEN Mortal(x)")

    print("=== Knowledge Base ===")
    print(f"Facts: {[f.predicate for f in engine.list_facts()]}")
    print(f"Rules: {[str(r) for r in engine.list_rules()]}")

    print("\n=== Forward Chaining ===")
    result = engine.forward_chain()
    print(f"New facts derived: {result.new_facts}")
    print(f"All facts: {result.all_derived_facts}")
    print(result.proof_trace.to_text())

    print("\n=== Backward Chaining: Mortal(Socrates)? ===")
    result = engine.backward_chain("Mortal(Socrates)")
    print(f"Result: {result.result}")
    print(result.proof_trace.to_text())

    print("\n=== Backward Chaining: Mortal(Plato)? ===")
    result = engine.backward_chain("Mortal(Plato)")
    print(f"Result: {result.result}")
    print(result.proof_trace.to_text())

    print("\n=== Query unknown: LivesIn(Socrates, Athens)? ===")
    result = engine.backward_chain("LivesIn(Socrates, Athens)")
    print(f"Result: {result.result}")
    print(result.proof_trace.to_text())


if __name__ == "__main__":
    main()
