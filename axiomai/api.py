"""
FastAPI REST API for AxiomAI Engine.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from axiomai.engine import AxiomEngine
from axiomai.facts import Fact
from axiomai.rules import Rule


app = FastAPI(title="AxiomAI", version="0.1.0", description="Deterministic Reasoning Engine")
engine = AxiomEngine()


# ── Request/Response Models ──────────────────────────────────────────────────

class FactRequest(BaseModel):
    predicate: str


class RuleRequest(BaseModel):
    rule_str: str
    priority: int = 1


class RuleDirectRequest(BaseModel):
    antecedents: list[str]
    consequent: str
    priority: int = 1


class QueryRequest(BaseModel):
    goal: str


# ── Fact Endpoints ────────────────────────────────────────────────────────────

@app.post("/facts", response_model=dict)
def add_fact(req: FactRequest):
    """Add a fact to the knowledge base."""
    try:
        fact = engine.add_fact(req.predicate)
        return fact.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/facts", response_model=list[dict])
def list_facts():
    """List all facts in the knowledge base."""
    return [f.to_dict() for f in engine.list_facts()]


@app.delete("/facts", response_model=dict)
def retract_fact(req: FactRequest):
    """Remove a fact from the knowledge base."""
    removed = engine.retract_fact(req.predicate)
    return {"removed": removed, "predicate": req.predicate}


# ── Rule Endpoints ────────────────────────────────────────────────────────────

@app.post("/rules", response_model=dict)
def add_rule(req: RuleRequest):
    """Add a rule to the knowledge base."""
    try:
        rule = engine.add_rule(req.rule_str, priority=req.priority)
        return rule.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/rules/direct", response_model=dict)
def add_rule_direct(req: RuleDirectRequest):
    """Add a rule directly with antecedents + consequent."""
    rule = engine.add_rule_direct(req.antecedents, req.consequent, priority=req.priority)
    return rule.to_dict()


@app.get("/rules", response_model=list[dict])
def list_rules():
    """List all rules in the knowledge base."""
    return [r.to_dict() for r in engine.list_rules()]


@app.delete("/rules/{rule_id}", response_model=dict)
def retract_rule(rule_id: str):
    """Remove a rule by ID."""
    removed = engine.retract_rule(rule_id)
    return {"removed": removed, "rule_id": rule_id}


# ── Inference Endpoints ────────────────────────────────────────────────────────

@app.post("/forward", response_model=dict)
def forward_chain():
    """Run forward chaining from current facts. Returns all derivable facts."""
    result = engine.forward_chain()
    return {
        "new_facts": result.new_facts,
        "all_derived_facts": result.all_derived_facts,
        "proof_trace": result.proof_trace.to_json(),
        "summary": result.proof_trace.summary(),
    }


@app.post("/backward", response_model=dict)
def backward_chain(req: QueryRequest):
    """Run backward chaining to prove a goal."""
    result = engine.backward_chain(req.goal)
    return {
        "goal": req.goal,
        "result": result.result,
        "bindings": result.bindings,
        "proof_trace": result.proof_trace.to_json(),
    }


@app.post("/query", response_model=dict)
def query(req: QueryRequest):
    """Query the knowledge base (alias for backward chaining)."""
    return backward_chain(req)


@app.get("/proof/{goal_encoded}", response_model=dict)
def get_proof(goal_encoded: str):
    """Retrieve proof for a goal (goal must be URL-encoded predicate)."""
    import urllib.parse
    goal = urllib.parse.unquote(goal_encoded)
    result = engine.backward_chain(goal)
    return {
        "goal": goal,
        "result": result.result,
        "proof_text": result.proof_trace.to_text(),
        "proof_json": result.proof_trace.to_json(),
    }


# ── Utility Endpoints ──────────────────────────────────────────────────────────

@app.post("/reset", response_model=dict)
def reset():
    """Clear all facts and rules."""
    engine.reset()
    return {"status": "reset", "message": "Knowledge base cleared"}


@app.post("/load/socrates", response_model=dict)
def load_socrates():
    """Load the classic Socrates example."""
    engine.load_socrates()
    return {
        "status": "loaded",
        "facts": [f.predicate for f in engine.list_facts()],
        "rules": [str(r) for r in engine.list_rules()],
    }


@app.get("/health")
def health():
    """Server health check."""
    return {
        "status": "healthy",
        "facts": len(engine.facts),
        "rules": len(engine.rules),
    }


# ── Run ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
