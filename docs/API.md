# AxiomAI — API Reference

## Reasoner Engine

### `Reasoner()`

Main engine. Combines all reasoning modes.

```python
from axiomai import Reasoner
r = Reasoner()
```

### Facts

```python
r.add_fact("Human(Socrates)")
r.add_facts("Human(Plato)", "Rational(Socrates)")
r.retract_fact("Human(Socrates)")
r.list_facts()  # → [Fact, Fact, ...]
```

### Rules

```python
r.add_rule("IF Human(x) THEN Mortal(x)")
r.add_rule("IF Human(x) AND Rational(x) THEN Person(x)", priority=2)
r.list_rules()
```

### Query

```python
result = r.ask("Mortal(Socrates)")
# result.result:  PROVED | DISPROVED | UNKNOWN | INCONSISTENT
# result.proof:   ProofTree
# result.bindings: {x: Socrates}
# result.explain(): one-liner explanation
```

### Forward Chaining

```python
result = r.derive_all()
# result.new_facts: list of newly derived facts
# result.proof: ProofTree with full trace
# result.duration_ms: execution time
```

### Contradiction Detection

```python
r.is_consistent()          # True/False
r.check_consistency()       # list of ContradictionReports
```

### Causal

```python
r.add_causal("HeavyRain", "FloodRisk")
r.causal_engine.root_causes("FloodRisk")
r.causal_engine.trace_path("HeavyRain", "FloodRisk")
```

### Planning

```python
r.add_action("DriveToAirport",
    preconditions=["HasCar", "License"],
    add_effects=["AtAirport"],
    del_effects=["AtHome"])
plan = r.plan(
    initial_state={"HasCar", "License", "AtHome"},
    goal={"AtAirport"}
)
```

### Constraint Solving

```python
from axiomai.reasoner.engines.constraints import solve_sudoku
solve_sudoku(grid)  # 9x9 list of lists
```

## REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/facts` | Add a fact |
| GET | `/facts` | List all facts |
| DELETE | `/facts` | Retract a fact |
| POST | `/rules` | Add a rule |
| GET | `/rules` | List all rules |
| POST | `/query` | Ask a query |
| POST | `/forward` | Forward chain |
| POST | `/resolution` | Resolution proof |
| GET | `/contradictions` | Check consistency |
| POST | `/constraints/solve` | Solve CSP |
| POST | `/sudoku` | Solve Sudoku |
| POST | `/planning/plan` | Generate plan |
| POST | `/planning/action` | Add action |
| POST | `/causal` | Add causal edge |
| GET | `/causal/root-causes/{effect}` | Root causes |
| POST | `/reset` | Clear KB |
| POST | `/load/socrates` | Load demo |
| GET | `/stats` | Engine stats |
