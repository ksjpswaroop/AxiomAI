# AxiomAI

**Deterministic Reasoning Engine — Facts + Rules = Proven Answers**

AxiomAI is an open-source reasoning engine that gives the same answer every time for the same facts, rules, and query. It is the anti-guessing AI: every conclusion is provable, every step is traceable.

## Quick Start

```bash
pip install axiomai
```

```python
from axiomai import AxiomEngine

engine = AxiomEngine()
engine.add_fact("Human(Socrates)")
engine.add_rule("IF Human(x) THEN Mortal(x)")

result = engine.query("Mortal(Socrates)")
print(result.proof_trace.to_text())
# ✅ TRUE — with full proof trace
```

## Features

- **Forward Chaining** — Data-driven inference from facts
- **Backward Chaining** — Goal-driven Prolog-style proving
- **Unification** — First-order variable binding
- **Constraint Solving** — Z3-backed CSP (Sudoku, scheduling)
- **Proof Traces** — Human-readable step-by-step explanations
- **Contradiction Detection** — Truth maintenance

## Architecture

```
Facts → Knowledge Base → Rules → Inference Engine → Proof Trace → Answer
```

## Install

```bash
pip install -e .
```

## Run Examples

```bash
python examples/socrates.py
python examples/medical_diagnosis.py
python examples/scheduling.py
```

## Run API Server

```bash
uvicorn axiomai.api:app --reload --port 8000
```

## Run Tests

```bash
pytest tests/ -v
```

## License

MIT
