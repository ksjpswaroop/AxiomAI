# AxiomAI — Deterministic Reasoning Engine

## The Problem

LLMs guess. Every response is probabilistic — same question, different answer. This makes LLMs unsuitable for:

- Legal/compliance reasoning (must be reproducible)
- Medical diagnosis support (must be traceable)
- Financial calculations (must be auditable)
- Industrial rule systems (must be deterministic)

## The Solution

**AxiomAI** is a deterministic reasoning engine — give it the same facts, rules, and query, and it will *always* produce the same answer with a full proof trace.

```
Input Facts
   ↓
Knowledge Base
   ↓
Rules / Logic
   ↓
Inference Engine
   ↓
Proof Trace
   ↓
Answer (Guaranteed)
```

## Why "AxiomAI"?

- **Axiom** — a self-evident truth, the foundation of logical reasoning
- **AI** — augmented intelligence, not artificial guessing
- **Axiom** implies: provable, deterministic, trustworthy
- Clean, memorable, contrasts sharply with "AI that guesses"

## Core Architecture

```
┌─────────────────────────────────────────────────────┐
│                   AxiomAI Engine                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────┐   ┌──────────┐   ┌───────────────┐  │
│  │  Fact    │   │  Rule    │   │   Query       │  │
│  │  Store   │   │  Store   │   │   Interface   │  │
│  └────┬─────┘   └────┬─────┘   └──────┬────────┘  │
│       │              │                 │            │
│       └────────┬─────┘─────────────────┘            │
│                ↓                                     │
│       ┌────────────────┐                             │
│       │  Unification   │  ← Variable binding engine  │
│       │  Engine        │                             │
│       └───────┬────────┘                             │
│               │                                       │
│       ┌───────▼────────┐                             │
│       │  Inference      │                             │
│       │  Engine         │                             │
│       ├────────────────┤                             │
│       │ Forward Chain   │  ← Data-driven              │
│       │ Backward Chain  │  ← Goal-driven              │
│       │ Resolution      │  ← Theorem proving          │
│       │ Constraint Solve│  ← CSP (Z3-backed)          │
│       └───────┬────────┘                             │
│               │                                       │
│       ┌───────▼────────┐                             │
│       │  Proof Trace   │  ← Explains every step      │
│       │  Generator     │                             │
│       └───────┬────────┘                             │
│               │                                       │
│       ┌───────▼────────┐                             │
│       │  Answer +      │                             │
│       │  Explanation   │                             │
│       └────────────────┘                             │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Reasoning Modes Supported

| Mode | Description |
|------|-------------|
| Deduction | General → Specific (modus ponens) |
| Forward Chaining | Data-driven, facts → conclusions |
| Backward Chaining | Goal-driven, prove from goals |
| Resolution | Theorem proving, refutation |
| Unification | Variable binding across predicates |
| Constraint Solving | CSP via Z3 (scheduling, Sudoku) |
| Contradiction Detection | Truth maintenance |
| Proof Generation | Full step-by-step trace |
| Causal Reasoning | Cause-effect chains |

## Example

**Facts:**
```
Human(Socrates)
Human(Plato)
```

**Rule:**
```
IF Human(x) THEN Mortal(x)
```

**Query:** `Mortal(Socrates)?`

**Result:**
```
TRUE

Proof Trace:
1. Human(Socrates) — given fact
2. Rule: Human(x) → Mortal(x)
3. Unify: x = Socrates
4. Therefore: Mortal(Socrates) ✓
```

## Build Stack

```
Python
├── FastAPI          — REST API server
├── Pydantic         — Data validation
├── SQLite/Postgres  — Persistent storage
├── NetworkX         — Graph reasoning / causal
├── Z3 Solver        — Constraint solving
├── kanren           — Logic programming / unification
├── numba            — Performance-critical inference
└── LLM (optional)    — NL → facts/rules translator only
```

## Key Principle

> **Use LLMs for:** Natural language → facts/rules/query (translation layer)
> **Use AxiomAI for:** facts + rules → guaranteed reasoning (trust layer)

This gives you a **neuro-symbolic AI system** you can actually trust.

## MVP Components

1. **Fact Store** — SQLite-backed predicate storage
2. **Rule Store** — IF-THEN rule repository
3. **Forward Chaining Engine** — Data-driven inference
4. **Backward Chaining Engine** — Goal-driven inference
5. **Unification Engine** — Variable binding via kanren
6. **Proof Trace Generator** — Full explanation output
7. **Contradiction Detector** — Truth maintenance

## Project Type

Open-source Python library + REST API
Target users: developers building compliant AI systems
