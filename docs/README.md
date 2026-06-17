# AxiomAI Reasoner

**Deterministic Reasoning Engine — Facts + Rules = Proven Answers**

A deterministic reasoning engine that gives the same answer every time for the same facts, rules, and query. Every conclusion is provable, every step is traceable.

## Key Principle

> **LLM translates. Reasoning engine proves.**
> Use LLMs for: Natural language → facts/rules/query
> Use AxiomAI for: facts + rules → guaranteed reasoning

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     AxiomAI Reasoner                       │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Natural Language ──→ │ LLM Extractor │ ──→ Knowledge   │
│                        │               │        Base     │
│                        └───────────────┘                 │
│                                 │                        │
│  ┌──────────────────────────────▼──────────────────────┐  │
│  │              Inference Engines                       │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │  │
│  │  │  Forward     │  │  Backward    │  │ Resolution│  │  │
│  │  │  Chaining    │  │  Chaining    │  │ (Z3)     │  │  │
│  │  └──────────────┘  └──────────────┘  └───────────┘  │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │  │
│  │  │  Constraint  │  │  Planning    │  │  Causal   │  │  │
│  │  │  Solver (Z3) │  │  (STRIPS)   │  │  Engine   │  │  │
│  │  └──────────────┘  └──────────────┘  └───────────┘  │  │
│  └──────────────────────────────┬──────────────────────┘  │
│                                 │                         │
│                    ┌────────────▼────────────┐             │
│                    │    Proof + Explanation  │             │
│                    │    Engine              │             │
│                    └────────────────────────┘             │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Reasoning Modes

| Mode | Description |
|------|-------------|
| **Backward Chaining** | Goal-driven Prolog-style proving |
| **Forward Chaining** | Data-driven, derives all possible facts |
| **Resolution** | Theorem proving via refutation (Z3) |
| **Constraint Solving** | CSP — Sudoku, scheduling, resource allocation |
| **Planning** | STRIPS-style classical planning |
| **Causal Reasoning** | Causal graphs, root cause, counterfactuals |

## Answer Types

```
PROVED      — logically derived from facts + rules
DISPROVED   — proven not to follow from KB
UNKNOWN     — cannot be determined from current KB
INCONSISTENT — KB contains contradictions
```

## Quick Start

```python
from axiomai import Reasoner

r = Reasoner()
r.add_fact("Human(Socrates)")
r.add_rule("IF Human(x) THEN Mortal(x)")

result = r.ask("Mortal(Socrates)")
print(result.result)          # PROVED
print(result.explain())       # ✅ Yes — because Human(Socrates) ...
```

## CLI

```bash
pip install -e .
axiomai add-fact "Human(Socrates)"
axiomai add-rule "IF Human(x) THEN Mortal(x)"
axiomai ask "Mortal(Socrates)"
axiomai prove "Mortal(Socrates)"
axiomai contradictions
axiomai socrates
axiomai solve-sudoku
```

## REST API

```bash
uvicorn axiomai.reasoner.api.main:app --reload --port 8000

# Examples:
curl -X POST http://localhost:8000/facts \
  -d '{"predicate": "Human(Socrates)"}'

curl -X POST http://localhost:8000/query \
  -d '{"query": "Mortal(Socrates)"}'
```

## Features

- **Forward Chaining** — Data-driven inference from facts
- **Backward Chaining** — Goal-driven Prolog-style proving
- **Unification** — First-order variable binding with occurs check
- **Resolution** — Z3-backed theorem proving
- **Constraint Solving** — Z3 CSP (Sudoku, scheduling)
- **Planning** — STRIPS BFS planner
- **Causal Reasoning** — NetworkX causal graphs
- **Proof Traces** — Human-readable step-by-step explanations
- **Contradiction Detection** — Truth maintenance
- **LLM Integration** — Extract facts/rules from NL (optional)

## Project Structure

```
axiomai/
├── src/reasoner/
│   ├── core/           # Models, unification, parser, substitution
│   ├── engines/        # Forward, backward, resolution, constraints, planner
│   ├── kb/             # Knowledge base store
│   ├── explain/        # Proof trees, narrators
│   ├── integrations/    # Z3 adapter, LLM extractor
│   └── api/            # FastAPI routes
├── tests/
├── docs/
└── examples/
```

## Project Documentation

| Document | Description |
|----------|-------------|
| [PROJECT-MODULES.md](./PROJECT-MODULES.md) | Full module breakdown (core engine, platform, apps) |
| [IMPLEMENTATION-TRACKER.md](./IMPLEMENTATION-TRACKER.md) | Phase-by-phase build tracker with task IDs |
| [API.md](./API.md) | REST API reference |
| [business/MASTER-BUSINESS-STRATEGY.md](./business/MASTER-BUSINESS-STRATEGY.md) | GTM strategy and case study priorities |
| [case-studies/](./case-studies/) | 18 vertical case study specifications |

## License

MIT
