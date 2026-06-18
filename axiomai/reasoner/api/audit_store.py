"""Shared audit log for API governance and case study decisions."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from axiomai.governance import AuditLog, Decision
from axiomai.governance.audit import AuditEntry


class AuditStore:
    """Process-wide audit log with optional file persistence."""

    def __init__(self, persist_path: str | None = None) -> None:
        self._log = AuditLog()
        self._persist_path = persist_path or os.environ.get("AXIOMAI_AUDIT_PERSIST")
        if self._persist_path:
            self._load()

    def _load(self) -> None:
        path = Path(self._persist_path)
        if not path.exists():
            return
        data = json.loads(path.read_text(encoding="utf-8"))
        for item in data:
            self._log._entries.append(  # noqa: SLF001
                AuditEntry(
                    id=item["id"],
                    timestamp=item["timestamp"],
                    outcome=item["outcome"],
                    action=item.get("action", {}),
                    explanation=item.get("explanation", ""),
                    violated_rules=item.get("violated_rules", []),
                    proof=item.get("proof"),
                    case_study=item.get("case_study"),
                    policy_id=item.get("policy_id"),
                )
            )

    def _save(self) -> None:
        if not self._persist_path:
            return
        path = Path(self._persist_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self._log.export_json(), encoding="utf-8")

    def record(
        self,
        decision: Decision,
        action: dict[str, Any],
        *,
        case_study: str | None = None,
        policy_id: str | None = None,
    ) -> dict[str, Any]:
        entry = self._log.record(
            decision,
            action=action,
            case_study=case_study,
            policy_id=policy_id,
        )
        self._save()
        return entry

    def query(
        self,
        *,
        outcome: str | None = None,
        case_study: str | None = None,
        policy_id: str | None = None,
        since: str | None = None,
    ) -> list[dict[str, Any]]:
        entries = list(self._log.entries)
        if outcome:
            entries = [e for e in entries if e.get("outcome") == outcome]
        if case_study:
            entries = [e for e in entries if e.get("case_study") == case_study]
        if policy_id:
            entries = [e for e in entries if e.get("policy_id") == policy_id]
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
        if self._persist_path:
            path = Path(self._persist_path)
            if path.exists():
                path.unlink()


audit_store = AuditStore()
