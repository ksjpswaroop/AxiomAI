"""P5 API routes — case studies, governance, audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from axiomai.governance import GovernanceEngine, PolicyPack
from axiomai.reasoner.api.audit_store import audit_store
from axiomai.reasoner.api.case_study_service import list_case_studies, run_case_study

router = APIRouter()

POLICY_PATH = (
    Path(__file__).resolve().parents[2] / "governance" / "policies" / "refund-policy.yaml"
)
_governance_engine = GovernanceEngine(PolicyPack.load(POLICY_PATH))


class GovernanceValidateRequest(BaseModel):
    action: dict[str, Any]
    context: list[str] = Field(default_factory=list)
    case_study: Optional[str] = None


@router.get("/case-studies", tags=["Case Studies"])
def get_case_studies():
    """List available Tier 1 case study demos."""
    return list_case_studies()


@router.post("/case-studies/{case_study_id}/run", tags=["Case Studies"])
def run_case_study_endpoint(case_study_id: str):
    """Execute a case study demo and return structured results."""
    try:
        result = run_case_study(case_study_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Unknown case study: {case_study_id}")
    if case_study_id == "cs-03" and "decision" in result:
        audit_store.record(
            _decision_from_dict(result["decision"]),
            action=result.get("action", {}),
            case_study=case_study_id,
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
    """Validate a proposed agent action against governance policy."""
    decision = _governance_engine.validate(action=req.action, context=req.context)
    audit_store.record(decision, action=req.action, case_study=req.case_study)
    return decision.to_dict()


@router.get("/audit", tags=["Audit"])
def query_audit(
    outcome: Optional[str] = Query(None),
    case_study: Optional[str] = Query(None),
    since: Optional[str] = Query(None),
):
    """Query the append-only governance audit log."""
    entries = audit_store.query(outcome=outcome, case_study=case_study, since=since)
    return {"count": len(entries), "entries": entries}


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
