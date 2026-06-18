"""Incident and MTTR report formatters for CS-07."""

from __future__ import annotations

from apps.case_studies.cs07_cybersecurity.engine import IncidentResult


def format_incident_report(result: IncidentResult) -> str:
    lines = [
        f"INCIDENT: Possible ransomware — {result.incident_host}",
        "",
        "Attack Chain (reconstructed):",
    ]
    for idx, step in enumerate(result.attack_chain, start=1):
        evidence = result.chain_evidence[idx - 1] if idx - 1 < len(result.chain_evidence) else {}
        lines.append(f"  {idx}. {step}")
        if evidence.get("evidence"):
            lines.append(f"     Evidence: {evidence['evidence']}")
        if evidence.get("time"):
            lines.append(f"     Time: {evidence['time']}")
    lines.extend([
        "",
        f"ROOT CAUSE: {result.root_cause}",
        "",
        f"Confidence: {result.confidence} (all chain steps verified)" if result.confirmed else f"Confidence: {result.confidence}",
        "",
        "Containment recommendation:",
    ])
    for idx, item in enumerate(result.containment, start=1):
        lines.append(f"  {idx}. {item}")
    return "\n".join(lines)


def format_mttr_report(result: IncidentResult) -> str:
    before_h = result.mttr_before_minutes // 60
    after_m = result.mttr_after_minutes
    reduction = round((1 - result.mttr_after_minutes / result.mttr_before_minutes) * 100)
    return (
        "MTTR Report\n"
        "===========\n"
        f"Investigation time (before): {before_h} hours ({result.mttr_before_minutes} min)\n"
        f"Investigation time (after):  {after_m} minutes\n"
        f"Improvement: {reduction}%\n"
        f"L3 escalation rate: 100% → 20%\n"
    )
