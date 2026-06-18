"""
FastAPI routes for AxiomAI Reasoner.
"""

from __future__ import annotations

import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ..engine import Reasoner
from ..engines.constraints import ConstraintSolver, solve_sudoku
from ..explain.narrator import Narrator
from .routes_app import router as app_router

app = FastAPI(
    title="AxiomAI Reasoner",
    version="0.3.0",
    description="Deterministic reasoning engine with governance, case studies, and audit APIs.",
)
app.include_router(app_router)
_persist = os.environ.get("AXIOMAI_PERSIST")
reasoner = Reasoner(persist=_persist) if _persist else Reasoner()


# ── Request Models ───────────────────────────────────────────────────────────

class FactRequest(BaseModel):
    predicate: str
    source: str = "api"


class RuleRequest(BaseModel):
    rule_str: str
    priority: int = 1
    author: Optional[str] = None
    domain: Optional[str] = None


class QueryRequest(BaseModel):
    query: str
    mode: str = "auto"  # auto, backward, forward, resolution


class PlanRequest(BaseModel):
    initial_state: list[str]
    goal: list[str]
    max_depth: int = 20


class CSPSolverRequest(BaseModel):
    variables: dict[str, tuple[int, int]]  # name -> (min, max)
    constraints: list[str]  # Python expressions as strings


class CausalRequest(BaseModel):
    cause: str
    effect: str


class ActionRequest(BaseModel):
    name: str
    preconditions: list[str]
    add_effects: list[str]
    del_effects: list[str] = []
    cost: int = 1


class SudokuRequest(BaseModel):
    grid: list[list[int]] | None = None


# ── Fact Endpoints ───────────────────────────────────────────────────────────

@app.post("/facts", tags=["Facts"])
def add_fact(req: FactRequest):
    """Add a fact to the knowledge base."""
    try:
        fact = reasoner.add_fact(req.predicate, source=req.source)
        return fact.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/facts", tags=["Facts"])
def list_facts():
    """List all facts."""
    return [f.to_dict() for f in reasoner.list_facts()]


@app.delete("/facts", tags=["Facts"])
def retract_fact(predicate: str):
    removed = reasoner.retract_fact(predicate)
    return {"removed": removed, "predicate": predicate}


# ── Rule Endpoints ───────────────────────────────────────────────────────────

@app.post("/rules", tags=["Rules"])
def add_rule(req: RuleRequest):
    """Add a rule."""
    try:
        rule = reasoner.add_rule(req.rule_str, priority=req.priority)
        if req.author:
            rule.author = req.author
        if req.domain:
            rule.domain = req.domain
        return rule.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/rules", tags=["Rules"])
def list_rules():
    """List all rules."""
    return [r.to_dict() for r in reasoner.list_rules()]


@app.delete("/rules/{rule_id}", tags=["Rules"])
def retract_rule(rule_id: str):
    removed = reasoner.retract_rule(rule_id)
    return {"removed": removed, "rule_id": rule_id}


# ── Query / Reasoning Endpoints ─────────────────────────────────────────────

@app.post("/query", tags=["Reasoning"])
def query(req: QueryRequest):
    """Ask a query with optional mode selection."""
    result = reasoner.ask(req.query, mode=req.mode)
    return {
        "query": result.query,
        "result": result.result,
        "status": result.status,
        "bindings": result.bindings,
        "duration_ms": round(result.duration_ms, 2),
        "reasoning_mode": result.reasoning_mode,
        "explain": {
            "one_line": result.explain("one_line"),
            "short": result.explain("short"),
            "medium": Narrator.medium(result.proof),
            "detailed": Narrator.detailed(result.proof),
        },
        "proof_json": result.proof.to_json(),
    }


@app.post("/forward", tags=["Reasoning"])
def forward_chain():
    """Run forward chaining — derive all possible facts."""
    result = reasoner.derive_all()
    return {
        "new_facts": [str(f.predicate) for f in result.new_facts],
        "all_derived": [str(f.predicate) for f in result.all_derived],
        "duration_ms": round(result.duration_ms, 2),
        "proof_json": result.proof.to_json(),
        "summary": result.proof.summary(),
    }


@app.post("/resolution", tags=["Reasoning"])
def resolve(req: QueryRequest):
    """Prove via resolution (refutation)."""
    result = reasoner.resolution_engine.prove(req.query)
    return {
        "query": req.query,
        "provable": result.provable,
        "duration_ms": round(result.duration_ms, 2),
        "proof_json": result.proof.to_json(),
    }


# ── Contradiction Endpoints ─────────────────────────────────────────────────

@app.get("/contradictions", tags=["Consistency"])
def check_contradictions():
    """Check for logical contradictions in the KB."""
    reports = reasoner.check_consistency()
    return {
        "consistent": len(reports) == 0,
        "contradictions": [
            {
                "fact1": str(r.fact1.predicate),
                "fact2": str(r.fact2.predicate),
                "explanation": r.explanation,
            }
            for r in reports
        ],
    }


# ── Constraint / Planning Endpoints ─────────────────────────────────────────

@app.post("/constraints/solve", tags=["Constraints"])
def solve_csp(req: CSPSolverRequest):
    """Solve a constraint satisfaction problem."""
    solver = ConstraintSolver()
    for name, (min_val, max_val) in req.variables.items():
        solver.var(name, min_val, max_val)
    for constraint in req.constraints:
        solver.add(constraint)
    result = solver.solve()
    return {
        "satisfiable": result is not None,
        "solution": result,
    }


@app.post("/sudoku", tags=["Constraints"])
def solve_sudoku_endpoint(req: SudokuRequest = SudokuRequest()):
    """Solve a Sudoku puzzle. Pass 9x9 grid with 0 = empty."""
    grid = req.grid
    if grid is None:
        grid = [
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
    solution = solve_sudoku(grid)
    return {"grid": grid, "solution": solution}


@app.post("/planning/plan", tags=["Planning"])
def plan(req: PlanRequest):
    """Generate a plan from initial state to goal."""
    plan_result = reasoner.plan(
        set(req.initial_state), set(req.goal), req.max_depth
    )
    return {
        "found": plan_result.found,
        "failure_reason": plan_result.failure_reason,
        "actions": [str(a) for a in plan_result.actions],
        "cost": plan_result.cost,
    }


@app.post("/planning/action", tags=["Planning"])
def add_action(req: ActionRequest):
    """Add a planning action."""
    action = reasoner.add_action(
        req.name, req.preconditions, req.add_effects, req.del_effects, req.cost
    )
    return {"name": action.name, "status": "added"}


# ── Causal Endpoints ───────────────────────────────────────────────────────

@app.post("/causal", tags=["Causal"])
def add_causal(req: CausalRequest):
    """Add a causal edge: cause → effect."""
    reasoner.add_causal(req.cause, req.effect)
    return {"cause": req.cause, "effect": req.effect}


@app.get("/causal/root-causes/{effect}", tags=["Causal"])
def root_causes(effect: str):
    """Find root causes of an effect."""
    roots = reasoner.causal_engine.root_causes(effect)
    return {"effect": effect, "root_causes": roots}


# ── Utility Endpoints ───────────────────────────────────────────────────────

@app.post("/reset", tags=["Utility"])
def reset():
    """Clear all knowledge."""
    reasoner.reset()
    return {"status": "reset"}


@app.post("/load/socrates", tags=["Utility"])
def load_socrates():
    """Load the classic Socrates example."""
    reasoner.load_socrates()
    return {
        "loaded": True,
        "facts": [str(f) for f in reasoner.list_facts()],
        "rules": [str(r) for r in reasoner.list_rules()],
    }


@app.get("/stats", tags=["Utility"])
def stats():
    """KB and engine statistics."""
    return {
        "kb_stats": reasoner.kb.stats(),
        "fingerprint": reasoner.fingerprint(),
        "run_count": reasoner._run_count,
        "unification_stats": reasoner.unification.stats(),
    }


@app.get("/health", tags=["Utility"])
def health():
    return {"status": "healthy", "version": "0.3.0"}


# ── Run ─────────────────────────────────────────────────────────────────────

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
