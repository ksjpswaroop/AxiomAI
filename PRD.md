# AxiomAI — Product Requirements Document

**Version:** 0.2.0
**Status:** Alpha
**Last Updated:** 2026-06-17

---

## 1. Vision

A deterministic reasoning engine that gives the same answer every time for the same facts, rules, and query. Every conclusion is provable, every step is traceable, and every contradiction is caught. AxiomAI is the "trust layer" for AI systems — it verifies what LLMs claim, flags hallucinations, and enforces business rules with mathematical certainty.

**Core principle:** LLM translates. AxiomAI proves.

---

## 2. Problem Statement

LLMs hallucinate. They generate confident but false claims. Current AI systems have no way to verify logical claims against a structured knowledge base. Businesses need deterministic, auditable reasoning for compliance, medical, legal, and financial decisions.

---

## 3. Product Goal

Build a Python reasoning engine that takes:
- **Facts** (known truths)
- **Rules** (IF-THEN logic)
- **Query** (question)

And returns:
- **Answer** (PROVED / DISPROVED / UNKNOWN / INCONSISTENT)
- **Proof Trace** (step-by-step explanation)
- **Contradictions** (what conflicts exist)
- **Confidence Source** (where facts came from)

---

## 4. Core Features

### 4.1 Knowledge Base

| Feature | Purpose |
|---------|---------|
| Fact Store | Atomic facts with provenance, timestamps, validity periods |
| Rule Store | IF-THEN rules with priority, author, domain, confidence source |
| Entity Registry | Track objects (Socrates, Patient1, ServerA) |
| Type System | Classes: Person, Device, Disease |
| Namespace Support | Separate domains (medical, legal, engineering) |
| Versioning | Track rule/fact changes over time |
| Source Tracking | Know where each fact came from |
| Validity Period | Facts true only during time ranges |

### 4.2 Logic Representation

| Logic Type | Example |
|------------|---------|
| Predicate logic | `Human(Socrates)` |
| Propositional | `A → B` |
| Conjunction | `A AND B` |
| Disjunction | `A OR B` |
| Negation | `NOT A` |
| Implication | `A → B` |
| Quantifiers | `forall x`, `exists x` |
| Equality / Inequality | `x = y`, `x != y` |

### 4.3 Inference Engines

| Engine | Mode | Description |
|--------|------|-------------|
| Forward Chaining | Data-driven | Apply all matching rules to facts, generate new facts, repeat to fixpoint |
| Backward Chaining | Goal-driven | Prove query by recursively proving subgoals (Prolog-style) |
| Resolution | Theorem proving | CNF conversion + refutation via Z3 |
| Constraint Solver | CSP | Z3-backed Sudoku, scheduling, resource allocation |
| Planning | STRIPS | BFS action planner from initial state to goal |
| Causal | Causal graph | NetworkX causal chains, root cause analysis |

### 4.4 Trust Layer

| Feature | Purpose |
|---------|---------|
| Unification | First-order with occurs check, deterministic |
| Contradiction Detection | Direct, rule-based, type, temporal, constraint |
| Truth Maintenance | Justifications, dependency graph, retraction |
| Proof Trace | Human-readable step-by-step explanations |
| Explanation Narrator | one_line / short / medium / detailed styles |
| Source Provenance | Every fact tagged with origin |
| KB Fingerprinting | SHA-256 hash for deterministic verification |

### 4.5 LLM Integration Layer

> **Critical:** LLM translates. Reasoning engine proves.

| LLM Does | LLM Does NOT |
|----------|--------------|
| Natural language → facts/rules/query | Final logical proof |
| Explanation polishing | Contradiction decision |
| Domain ontology suggestion | Rule firing |
| Rule extraction from documents | Truth decision |

LLM Extractor uses structured Pydantic output to constrain LLM responses.

---

## 5. Answer Types

```
PROVED       — logically derived from facts + rules
DISPROVED    — proven not to follow from KB
UNKNOWN      — cannot be determined from current KB
INCONSISTENT — KB contains contradictions
```

---

## 6. Reasoning Modes

```
Deterministic Reasoning Engine
├── Deduction
├── Forward Chaining
├── Backward Chaining
├── Resolution
├── Unification
├── Constraint Solving
├── Rule Priority
├── Contradiction Detection
├── Proof Generation
├── Explanation
├── Planning (STRIPS/HTN)
├── Causal Reasoning
└── Temporal Reasoning
```

---

## 7. MVP Build Order

### Phase 1: Core Logic Engine
1. ✅ Predicate model
2. ✅ Fact model
3. ✅ Rule model
4. ✅ Parser
5. ✅ Unification
6. ✅ Forward chaining
7. ✅ Backward chaining
8. ✅ Proof trace

### Phase 2: Trust Layer
9. ✅ Contradiction detection
10. ✅ Source tracking
11. ✅ Truth maintenance
12. ✅ Explanation engine
13. ✅ KB fingerprinting

### Phase 3: Solvers
14. ✅ Z3 integration
15. ✅ CSP solver (Sudoku)
16. ✅ Planning (STRIPS)
17. ✅ Causal reasoning

### Phase 4: Product Layer
18. ✅ FastAPI REST
19. ✅ Typer CLI
20. ✅ Examples
21. Tests
22. LLM extractor (optional)

---

## 8. Stack

```
Core:       pydantic, lark, kanren, unification, z3-solver, networkx
API:        fastapi, uvicorn, pydantic
CLI:        typer, rich
Storage:    aiosqlite, sqlalchemy
Testing:    pytest, hypothesis
LLM:        openai / anthropic (optional)
```

---

## 9. API Design

### REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/facts` | Add a fact |
| GET | `/facts` | List all facts |
| DELETE | `/facts` | Retract a fact |
| POST | `/rules` | Add a rule |
| GET | `/rules` | List all rules |
| POST | `/query` | Ask a query (auto mode) |
| POST | `/reason/forward` | Forward chain |
| POST | `/reason/backward` | Backward chain |
| POST | `/reason/resolution` | Resolution proof |
| POST | `/explain` | Get explanation |
| GET | `/contradictions` | Check consistency |
| POST | `/constraints/solve` | Solve CSP |
| POST | `/constraints/sudoku` | Solve Sudoku |
| POST | `/plan` | Generate plan |
| POST | `/causal` | Add causal edge |
| GET | `/causal/root-causes/{effect}` | Root causes |
| POST | `/reset` | Clear KB |
| POST | `/load/socrates` | Load demo |
| GET | `/stats` | KB + engine stats |
| GET | `/health` | Health check |

### CLI Commands

```
axiomai add-fact "Human(Socrates)"
axiomai add-rule "IF Human(x) THEN Mortal(x)"
axiomai ask "Mortal(Socrates)"
axiomai prove "Mortal(Socrates)"
axiomai explain "Mortal(Socrates)"
axiomai forward
axiomai contradictions
axiomai socrates
axiomai solve-sudoku
axiomai reset
```

---

## 10. Storage Design

### Tables
- facts
- rules
- predicates
- entities
- proofs
- inference_runs
- contradictions
- assumptions
- sources
- ontology_classes
- ontology_relations
- constraints
- plans

### Storage Options
- **MVP:** SQLite
- **Production:** PostgreSQL + Redis
- **Graph:** NetworkX for in-memory graph operations

---

## 11. Determinism Requirements

To make the engine truly deterministic:
1. Stable rule ordering (priority field)
2. Stable fact ordering (deterministic sort)
3. Rule priority for execution order
4. Fixed tie-breakers
5. No random sampling
6. Immutable inference snapshots
7. Same inputs = same outputs (verified by fingerprint)
8. Versioned KB
9. Hash every reasoning run
10. Full proof trace always

---

## 12. Best Product Angle

**Trust Layer for LLM / Agent Output**

```
LLM generates answer
    ↓
Reasoner extracts claims
    ↓
Claims become facts/rules
    ↓
Deterministic engine verifies:
  - contradiction?
  - missing premise?
  - unsupported claim?
  - rule violation?
  - compliance issue?
    ↓
Output verified answer with proof trace
```

### Target Markets
- **Agent Governance Engine** — verify agent decisions
- **AI Compliance Verifier** — regulatory rule enforcement
- **Hallucination Detection Layer** — catch LLM errors
- **Code Reasoning Engine** — logical code verification
- **Cybersecurity Expert System** — rule-based threat analysis
- **Business Rule Validator** — policy enforcement
- **Medical/Legal Decision Support Guardrail** — deterministic recommendations

### MVP for Market
**LLM claim verifier + deterministic proof trace**

This is commercially stronger than a generic logic engine because it directly addresses the hallucination problem in production AI systems.

---

## 13. Folder Structure

```
AxiomAI/
├── axiomai/
│   ├── __init__.py
│   ├── reasoner/
│   │   ├── __init__.py
│   │   ├── engine.py          # Main facade
│   │   ├── cli.py             # Typer CLI
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── models.py      # Predicate, Fact, Rule, Entity, Term
│   │   │   ├── parser.py      # String → structured objects
│   │   │   ├── unification.py  # First-order unification
│   │   │   ├── substitution.py
│   │   │   └── ordering.py    # Deterministic ordering
│   │   ├── engines/
│   │   │   ├── __init__.py
│   │   │   ├── forward.py    # Forward chaining
│   │   │   ├── backward.py    # Backward chaining
│   │   │   ├── resolution.py  # Resolution theorem prover
│   │   │   ├── constraints.py # Z3 CSP solver
│   │   │   ├── planner.py    # STRIPS planner
│   │   │   └── causal.py      # Causal reasoning
│   │   ├── kb/
│   │   │   ├── __init__.py
│   │   │   └── store.py      # Knowledge base + contradictions
│   │   ├── explain/
│   │   │   ├── __init__.py
│   │   │   ├── proof.py      # Proof tree
│   │   │   └── narrator.py   # Human-readable explanations
│   │   ├── integrations/
│   │   │   ├── __init__.py
│   │   │   ├── z3_adapter.py
│   │   │   └── llm_extractor.py
│   │   └── api/
│   │       ├── __init__.py
│   │       └── main.py       # FastAPI routes
│   └── reasoner.egg-info/
├── tests/
│   └── test_reasoner.py
├── docs/
│   ├── README.md
│   └── API.md
├── examples/
│   └── socrates.py
├── pyproject.toml
├── requirements.txt
└── .gitignore
```

---

## 14. Example Usage

```python
from axiomai import Reasoner

r = Reasoner()
r.add_fact("Human(Socrates)")
r.add_fact("Human(Plato)")
r.add_rule("IF Human(x) THEN Mortal(x)")

result = r.ask("Mortal(Socrates)")
print(result.result)   # PROVED
print(result.explain()) # ✅ Yes — because Human(Socrates) ...
```

```
CLI:
axiomai add-fact "Human(Socrates)"
axiomai add-rule "IF Human(x) THEN Mortal(x)"
axiomai ask "Mortal(Socrates)"
```
