"""
Medical Diagnosis Expert System — Backward chaining demo.
"""

from axiomai import AxiomEngine


def main():
    engine = AxiomEngine()

    # Symptoms (observed facts)
    engine.add_fact("Symptom(Patient, Fever)")
    engine.add_fact("Symptom(Patient, Cough)")
    engine.add_fact("Symptom(Patient, Fatigue)")

    # Medical knowledge base
    # Rule 1: IF has fever AND cough THEN likely Flu
    engine.add_rule("IF Symptom(x, Fever) AND Symptom(x, Cough) THEN Has(x, Flu)")

    # Rule 2: IF has fever AND fatigue THEN could be Mono
    engine.add_rule("IF Symptom(x, Fever) AND Symptom(x, Fatigue) THEN Has(x, Mononucleosis)")

    # Rule 3: IF has Flu THEN give Rest
    engine.add_rule("IF Has(x, Flu) THEN Recommend(x, Rest)")

    # Rule 4: IF has Flu THEN give Antiviral
    engine.add_rule("IF Has(x, Flu) THEN Recommend(x, Antiviral)")

    print("=== Medical Diagnosis Expert System ===")
    print(f"Patient symptoms: Fever, Cough, Fatigue\n")

    print("--- Forward chaining (what can we derive?) ---")
    result = engine.forward_chain()
    print(f"Derived facts: {result.new_facts}")
    print()

    print("--- Diagnosis: Does patient have Flu? ---")
    result = engine.backward_chain("Has(Patient, Flu)")
    print(f"Result: {result.result}")
    print(result.proof_trace.to_text())
    print()

    print("--- What treatments are recommended? ---")
    result = engine.backward_chain("Recommend(Patient, Rest)")
    print(f"Result: {result.result}")
    print(result.proof_trace.to_text())


if __name__ == "__main__":
    main()
