"""Shared audit log for API governance and case study decisions."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from axiomai.governance import AuditLog, Decision


class AuditStore:
    """Process-wide audit log with query filters."""

    def __init__(self) -> None:
        self._log = AuditLog()

    def record(
        self,
        decision: Decision,
        action: dict[str, Any],
        *,
        case_study: str | None = None,
    ) -> dict[str, Any]:
        entry = self._log.record(decision, action=action)
        if case_study:
            entry["case_study"] = case_study
        return entry

    def query(
        self,
        *,
        outcome: str | None = None,
        case_study: str | None = None,
        since: str | None = None,
    ) -> list[dict[str, Any]]:
        entries = list(self._log.entries)
        if outcome:
            entries = [e for e in entries if e.get("outcome") == outcome]
        if case_study:
            entries = [e for e in entries if e.get("case_study") == case_study]
        if since:
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
            entries = [
                e
                for e in entries
                if datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00")) >= since_dt
            ]
        return entries

    def clear(self) -> None:
        self._log = AuditLog()


audit_store = AuditStore()
