"""Append-only audit log for governance decisions."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from axiomai.governance.engine import Decision


@dataclass
class AuditEntry:
    """Single immutable audit record."""

    id: str
    timestamp: str
    outcome: str
    action: dict[str, Any]
    explanation: str
    violated_rules: list[str]
    proof: dict[str, Any] | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "outcome": self.outcome,
            "action": self.action,
            "explanation": self.explanation,
            "violated_rules": self.violated_rules,
            "proof": self.proof,
        }


class AuditLog:
    """Append-only decision log with proof payloads."""

    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    @property
    def entries(self) -> list[dict[str, Any]]:
        return [e.to_dict() for e in self._entries]

    def record(self, decision: Decision, action: dict[str, Any]) -> dict[str, Any]:
        entry = AuditEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            outcome=decision.outcome,
            action=dict(action),
            explanation=decision.explanation,
            violated_rules=list(decision.violated_rules),
            proof=decision.proof,
        )
        self._entries.append(entry)
        return entry.to_dict()

    def export_json(self) -> str:
        return json.dumps(self.entries, indent=2)
