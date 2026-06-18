"""CS-03 audit trail formatting."""

from __future__ import annotations

from apps.case_studies.cs03_support_governance.engine import ScenarioResult


def format_audit_trail(results: list[ScenarioResult]) -> list[dict]:
    return [r.audit_entry for r in results]


def format_llm_denial_report(result: ScenarioResult) -> str:
    lines = [
        f"Refund: {result.decision.outcome}",
        "",
        "Reason:",
    ]
    if result.decision.outcome == "DENY":
        parts = result.decision.explanation.split(". ")
        for idx, part in enumerate(parts, start=1):
            if part.strip():
                lines.append(f"  {idx}. {part.strip().rstrip('.')}.")
    else:
        lines.append(f"  {result.decision.explanation}")
    if result.decision.violated_rules:
        lines.extend(["", "Rule violated:", f"  {result.decision.violated_rules[0]}"])
    lines.extend(["", "Request returned to:", "  L1 agent with explanation"])
    return "\n".join(lines)
