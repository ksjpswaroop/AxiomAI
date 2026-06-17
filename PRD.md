# AxiomAI — Product Requirements Document

## 1. Concept & Vision

AxiomAI is an **open-source deterministic reasoning engine** — a Python library and REST API that gives the same answer every time for the same facts, rules, and query. It is the anti-guessing AI: every conclusion is provable, every step is traceable, and every answer is reproducible.

The personality is: **mathematically rigorous, transparently honest, developer-first**. It doesn't try to sound smart — it shows its work.

**Tagline:** *"Facts + Rules = Proven Answers"*

---

## 2. Design Language

### Aesthetic Direction
Inspired by formal logic systems (Prolog, Coq, Isabelle) — clean, sparse, academic. White space is correctness. Monospace fonts are truth.

### Color Palette
- **Primary:** `#1a1a2e` (deep navy — authority)
- **Secondary:** `#16213e` (dark blue — precision)
- **Accent:** `#e94560` (red — contradiction/alert)
- **Success:** `#0f9b6e` (green — proven truth)
- **Background:** `#f8f9fa` (off-white — clean slate)
- **Text:** `#2d3436` (near-black)
- **Code/Mono:** `#6c5ce7` (purple — logic)

### Typography
- **Headings:** Inter (weight 700)
- **Body:** Inter (weight 400)
- **Code/Logic:** JetBrains Mono

### Visual Assets
- Minimal iconography — mathematical symbols (∧, ∨, →, ∴)
- Proof trees rendered as ASCII or SVG
- No stock photography — diagrams only

---

## 3. Layout & Structure

### Repository Layout
```
AxiomAI/
├── axiomai/              # Core library
│   ├── __init__.py
│   ├── engine.py         # Main inference engine
│   ├── facts.py          # Fact store
│   ├── rules.py          # Rule store
│   ├── unification.py    # Unification engine
│   ├── forward_chain.py  # Forward chaining
│   ├── backward_chain.py # Backward chaining
│   ├── resolution.py     # Resolution theorem prover
│   ├── constraints.py    # Z3-backed CSP
│   ├── proof_trace.py    # Proof generation
│   ├── contradiction.py   # Truth maintenance
│   └── api.py            # FastAPI routes
├── tests/
│   ├── test_facts.py
│   ├── test_rules.py
│   ├── test_unification.py
│   ├── test_forward_chain.py
│   ├── test_backward_chain.py
│   └── test_integration.py
├── examples/
│   ├── socrates.py       # Basic example
│   ├── medical_diagnosis.py
│   └── scheduling.py     # CSP/Z3
├── docs/
│   ├── README.md
│   ├── API.md
│   └── LOGIC.md
├── requirements.txt
├── pyproject.toml
└── LICENSE
```

---

## 4. Features & Interactions

### Core Features

#### 4.1 Fact Store
- Add facts as predicates: `Human(Socrates)`, `Loves(John, Mary)`
- List all facts
- Query if a fact exists
- Delete retract facts
- Import/export facts as JSON

#### 4.2 Rule Store
- Add rules as IF-THEN: `IF Human(x) THEN Mortal(x)`
- Multiple antecedents: `IF Human(x) AND Rational(x) THEN Person(x)`
- List, query, delete rules
- Rule priority ordering

#### 4.3 Forward Chaining Engine
- Input: initial facts
- Output: all derivable facts
- Algorithm: iterate rules, apply modus ponens, add conclusions
- Stop when no new facts generated
- Return proof trace for each new fact

#### 4.4 Backward Chaining Engine
- Input: goal predicate
- Output: provable/unprovable with trace
- Algorithm: recursive goal reduction
- Proves sub-goals recursively
- Returns `TRUE/FALSE/UNKNOWN` with proof path

#### 4.5 Unification Engine
- Input: two predicates with variables
- Output: variable bindings or failure
- Example: `Parent(x, Mary)` unify with `Parent(John, y)` → `{x: John, y: Mary}`

#### 4.6 Proof Trace Generator
- Every inference step documented
- Output format: JSON or plain text
- Structure: `{step: int, rule: str, facts_matched: [], conclusion: str}`
- Human-readable tree view

#### 4.7 Contradiction Detector
- Detect `P(x)` and `¬P(x)` simultaneously
- Block inference on contradiction
- Report which facts/rules conflict

#### 4.8 (Phase 2) Constraint Solver
- Z3-backed CSP interface
- Sudoku, scheduling, resource allocation
- Full proof trace for constraint solutions

#### 4.9 (Phase 2) Causal Reasoning
- NetworkX-backed causal graphs
- Cause → Effect链条
- Counterfactual: "what if X had not occurred"

---

## 5. Component Inventory

### FactStore
- `add_fact(predicate)` → success/error
- `retract_fact(predicate)` → success/error
- `query_fact(predicate)` → bool
- `list_facts()` → [predicates]
- States: empty, populated, conflicting

### RuleStore
- `add_rule(antecedents, consequent)` → rule_id
- `retract_rule(rule_id)` → success
- `list_rules()` → [rules]
- `get_rules_for_consequent(consequent)` → [rules]

### InferenceEngine
- `forward_chain()` → {new_facts, proof_trace}
- `backward_chain(goal)` → {result, proof_trace}
- `resolve(goal)` → provable/unprovable

### ProofTrace
- `generate_trace(inference_steps)` → trace_object
- `to_text(trace)` → human-readable string
- `to_json(trace)` → serializable format

### API Server (FastAPI)
- `POST /facts` — add fact
- `GET /facts` — list facts
- `DELETE /facts/{id}` — retract
- `POST /rules` — add rule
- `GET /rules` — list rules
- `POST /query` — run query (auto-selects chain direction)
- `POST /forward` — forward chain from facts
- `POST /backward` — backward chain to goal
- `GET /proof/{query_id}` — get proof trace
- `GET /health` — server health

---

## 6. Technical Approach

### Language & Framework
- **Python 3.11+**
- **FastAPI** — async REST API
- **Pydantic v2** — data models
- **SQLite** — default storage (swap to Postgres for production)
- **kanren** — logic programming / unification
- **z3-solver** — constraint satisfaction
- **NetworkX** — causal graphs
- **pytest** — testing

### Data Model

**Fact:**
```python
{
    "id": "uuid",
    "predicate": "Human(Socrates)",
    "terms": ["Socrates"],
    "relation": "Human",
    "created_at": "2024-01-01T00:00:00Z"
}
```

**Rule:**
```python
{
    "id": "uuid",
    "antecedents": ["Human(x)"],
    "consequent": "Mortal(x)",
    "priority": 1,
    "created_at": "2024-01-01T00:00:00Z"
}
```

**ProofStep:**
```python
{
    "step": 1,
    "type": "fact | rule | unify | conclude",
    "content": "Human(Socrates)",
    "justification": "Given",
    "derived_from": []
}
```

### Reasoning Algorithms

**Forward Chaining:**
1. Load all facts into working memory
2. For each rule, try to unify antecedents with facts
3. On match, add consequent to working memory
4. Repeat until no new facts (fixpoint)
5. Return all derived facts + trace

**Backward Chaining:**
1. Receive goal predicate G
2. Find rules with consequent matching G
3. For each rule, prove all antecedents recursively
4. If all antecedents provable → G is TRUE
5. Track proof tree; if no rule fires → G is FALSE

**Unification:**
- Use kanren's `unify()` for first-order unification
- Return most general unifier (MGU)

---

## 7. Non-Goals (Out of Scope for MVP)

- LLM integration (translator-only, not reasoner)
- Natural language query parsing
- Probabilistic/Bayesian reasoning
- Learning/induction from data
- Distributed knowledge base
- Graphical UI

---

## 8. Success Criteria

- [ ] `pip install axiomai` works
- [ ] Forward chain produces same results every run
- [ ] Backward chain proves Socrates is mortal correctly
- [ ] Proof trace is human-readable
- [ ] API responds < 100ms for 1000 facts/rules
- [ ] All reasoning modes return deterministic results
- [ ] Contradiction detection fires on conflict
- [ ] Z3 CSP solves Sudoku 9x9
