"""P5 API routes — case studies, governance, audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from axiomai.governance import AgentGovernanceMiddleware, EscalationRouter, PolicyRegistry
from axiomai.reasoner.api.audit_store import audit_store
from axiomai.reasoner.api.case_study_service import list_case_studies, list_scenarios, run_case_study

router = APIRouter()

_policy_registry = PolicyRegistry.default()
_escalation_router = EscalationRouter(
    routes={"DENY": "agent-feedback", "ESCALATE": "manager-queue"}
)
_governance_middleware = AgentGovernanceMiddleware(
    registry=_policy_registry,
    router=_escalation_router,
    audit=audit_store._log,  # noqa: SLF001 — shared audit log
)


class GovernanceValidateRequest(BaseModel):
    action: dict[str, Any]
    context: list[str] = Field(default_factory=list)
    case_study: Optional[str] = None
    policy_id: str = "refund-policy"
    nl_context: Optional[str] = None


@router.get("/policies", tags=["Governance"])
def list_policies():
    """List available governance policy packs."""
    return {"policies": _policy_registry.list_policies()}


class CaseStudyRunRequest(BaseModel):
    scenario: str = "default"


class BrainstormRequest(BaseModel):
    description: str = Field(..., min_length=10)


@router.get("/case-studies", tags=["Case Studies"])
def get_case_studies():
    """List all 18 case study demos with metadata."""
    return list_case_studies()


@router.get("/case-studies/{case_study_id}/scenarios", tags=["Case Studies"])
def get_case_study_scenarios(case_study_id: str):
    """List runnable scenarios for a case study."""
    try:
        return {"case_study_id": case_study_id, "scenarios": list_scenarios(case_study_id)}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Unknown case study: {case_study_id}")


@router.post("/case-studies/{case_study_id}/run", tags=["Case Studies"])
def run_case_study_endpoint(case_study_id: str, req: CaseStudyRunRequest | None = None):
    """Execute a case study demo scenario and return structured results."""
    scenario = req.scenario if req else "default"
    try:
        result = run_case_study(case_study_id, scenario_id=scenario)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Unknown case study: {case_study_id}")
    if case_study_id == "cs-03" and "decision" in result:
        audit_store.record(
            _decision_from_dict(result["decision"]),
            action=result.get("action", {}),
            case_study=case_study_id,
            policy_id="refund-policy",
        )
    elif result.get("outcome") in ("DENY", "BLOCKED", "ESCALATE"):
        from axiomai.governance import Decision

        audit_store.record(
            Decision(
                outcome="DENY" if result["outcome"] == "BLOCKED" else result["outcome"],
                explanation=result.get("explanation", ""),
                violated_rules=result.get("conclusions", []),
                proof=result.get("proofs", [None])[0] if result.get("proofs") else None,
            ),
            action={"case_study_run": case_study_id},
            case_study=case_study_id,
        )
    return result


@router.post("/governance/validate", tags=["Governance"])
def governance_validate(req: GovernanceValidateRequest):
    """Validate a proposed agent action against a governance policy pack."""
    try:
        _policy_registry.get(req.policy_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Unknown policy: {req.policy_id}")

    result = _governance_middleware.intercept(
        action=req.action,
        context=req.context,
        policy_id=req.policy_id,
        nl_context=req.nl_context,
    )
    decision = result["decision"]
    audit_store.record(
        _decision_from_dict(decision),
        action=req.action,
        case_study=req.case_study,
        policy_id=req.policy_id,
    )
    return {
        **decision,
        "escalation_queue": result.get("escalation_queue"),
        "audit_id": result.get("audit_id"),
        "policy_id": req.policy_id,
    }


@router.get("/audit", tags=["Audit"])
def query_audit(
    outcome: Optional[str] = Query(None),
    case_study: Optional[str] = Query(None),
    policy_id: Optional[str] = Query(None),
    since: Optional[str] = Query(None),
):
    """Query the append-only governance audit log."""
    entries = audit_store.query(
        outcome=outcome, case_study=case_study, policy_id=policy_id, since=since
    )
    return {"count": len(entries), "entries": entries}


@router.post("/brainstorm", tags=["Brainstorming"])
def brainstorm(req: BrainstormRequest):
    """Analyze whether a described problem fits AxiomAI scope."""
    from apps.case_studies._base.scope_matcher import analyze_problem

    return analyze_problem(req.description).to_dict()


@router.delete("/audit", tags=["Audit"])
def clear_audit():
    """Clear audit log (testing / reset)."""
    audit_store.clear()
    return {"status": "cleared"}


def _decision_from_dict(data: dict[str, Any]):
    from axiomai.governance import Decision

    return Decision(
        outcome=data["outcome"],
        explanation=data.get("explanation", ""),
        violated_rules=data.get("violated_rules", []),
        proof=data.get("proof"),
        proofs=data.get("proofs", []),
    )
