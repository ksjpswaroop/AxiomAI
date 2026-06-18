"""
Proof — Structured proof tree nodes for explanation.
"""

from __future__ import annotations

import uuid
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class StepType(Enum):
    FACT = "fact"
    RULE = "rule"
    UNIFY = "unify"
    CONCLUDE = "conclude"
    FAIL = "fail"
    ASSUME = "assume"
    RETRACT = "retract"
    CONFLICT = "conflict"
    RESOLVE = "resolve"


@dataclass
class ProofStep:
    """A single step in a proof."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    step: int = 0
    type: StepType = StepType.FACT
    content: str = ""
    justification: str = ""
    derived_from: list[str] = field(default_factory=list)  # IDs of source steps
    rule_id: Optional[str] = None
    substitution: dict = field(default_factory=dict)
    bindings: dict = field(default_factory=dict)  # Variable bindings at this step

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "step": self.step,
            "type": self.type.value,
            "content": self.content,
            "justification": self.justification,
            "derived_from": self.derived_from,
            "rule_id": self.rule_id,
            "substitution": self.substitution,
            "bindings": self.bindings,
        }


@dataclass
class ProofTree:
    """A complete proof tree for a query result."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query: str = ""
    result: str = "UNKNOWN"  # PROVED, DISPROVED, UNKNOWN, INCONSISTENT
    steps: list[ProofStep] = field(default_factory=list)
    conclusion: Optional[str] = None
    bindings: dict = field(default_factory=dict)
    duration_ms: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_step(self, step: ProofStep):
        self.steps.append(step)

    def to_text(self) -> str:
        """Human-readable proof trace."""
        lines = [
            "=" * 55,
            f"  PROOF: {self.query}",
            f"  RESULT: {self.result}",
            "=" * 55,
        ]
        for s in self.steps:
            icon = {
                StepType.FACT: "📋",
                StepType.RULE: "📐",
                StepType.UNIFY: "🔗",
                StepType.CONCLUDE: "✅",
                StepType.FAIL: "❌",
                StepType.ASSUME: "💭",
                StepType.RETRACT: "🗑",
                StepType.CONFLICT: "⚠️",
            }.get(s.type, "•")

            lines.append(f"\n  Step {s.step}: {icon} {s.type.value.upper()}")
            lines.append(f"    Content:     {s.content}")
            lines.append(f"    Justification: {s.justification}")
            if s.bindings:
                lines.append(f"    Bindings: {s.bindings}")
            if s.derived_from:
                lines.append(f"    From steps: {', '.join(s.derived_from)}")

        lines.append(f"\n  Conclusion: {self.conclusion or self.result}")
        lines.append("=" * 55)
        return "\n".join(lines)

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "query": self.query,
            "result": self.result,
            "conclusion": self.conclusion,
            "bindings": self.bindings,
            "duration_ms": self.duration_ms,
            "steps": [s.to_dict() for s in self.steps],
            "created_at": self.created_at.isoformat(),
        }, indent=2)

    def summary(self) -> dict:
        return {
            "result": self.result,
            "total_steps": len(self.steps),
            "conclusions": [s.content for s in self.steps if s.type == StepType.CONCLUDE],
            "failures": [s.content for s in self.steps if s.type == StepType.FAIL],
            "conflicts": [s.content for s in self.steps if s.type == StepType.CONFLICT],
        }

    def minimal_explanation(self) -> str:
        """Shortest explanation for end users."""
        concs = [s for s in self.steps if s.type == StepType.CONCLUDE]
        if not concs:
            fails = [s for s in self.steps if s.type == StepType.FAIL]
            if fails:
                return f"Could not prove: {fails[-1].content}"
            return f"Result: {self.result}"

        last = concs[-1]
        return f"✅ {last.content} — because {last.justification}"
