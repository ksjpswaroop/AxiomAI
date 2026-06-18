"""Format governance and reasoning results for case study reports."""

from __future__ import annotations

from typing import Any

from axiomai.governance.engine import Decision


def format_decision_report(
    title: str,
    action: dict[str, Any],
    decision: Decision,
) -> str:
    """Render a human-readable governance decision report."""
    entity = action.get("entity", action.get("id", "unknown"))
    amount = action.get("amount")
    amount_line = f"Amount: ${amount}\n" if amount is not None else ""
    violations = "\n".join(f"  - {rule}" for rule in decision.violated_rules) or "  (none)"
    return (
        f"{title}\n"
        f"{'=' * len(title)}\n"
        f"Action: {action.get('type', 'unknown')} ({entity})\n"
        f"{amount_line}"
        f"Decision: {decision.outcome}\n"
        f"Explanation: {decision.explanation}\n"
        f"Violated rules:\n{violations}\n"
    )


def format_proof_summary(decision: Decision) -> str:
    """Summarize proof payload attached to a decision."""
    if not decision.proof:
        return "No proof recorded."
    query = decision.proof.get("query", "")
    result = decision.proof.get("result", "UNKNOWN")
    steps = decision.proof.get("steps", [])
    return f"Query: {query}\nResult: {result}\nSteps: {len(steps)}"
