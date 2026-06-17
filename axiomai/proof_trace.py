"""
Proof Trace — Step-by-step reasoning explanation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import json


@dataclass
class ProofStep:
    """A single step in a proof."""
    step: int
    type: str  # "fact", "rule", "unify", "conclude", "fail"
    content: str
    justification: str
    derived_from: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "step": self.step,
            "type": self.type,
            "content": self.content,
            "justification": self.justification,
            "derived_from": self.derived_from,
        }


class ProofTrace:
    """Container for all proof steps."""

    def __init__(self):
        self._steps: list[ProofStep] = []

    def add_step(self, step: ProofStep):
        self._steps.append(step)

    def steps(self) -> list[ProofStep]:
        return list(self._steps)

    def clear(self):
        self._steps.clear()

    def to_text(self) -> str:
        """Render as human-readable text."""
        lines = ["=" * 50, "PROOF TRACE", "=" * 50]
        for s in self._steps:
            icon = {
                "fact": "📋",
                "rule": "📐",
                "unify": "🔗",
                "conclude": "✅",
                "fail": "❌",
            }.get(s.type, "•")

            lines.append(f"\nStep {s.step}: {icon} {s.type.upper()}")
            lines.append(f"  Content: {s.content}")
            lines.append(f"  Why: {s.justification}")
            if s.derived_from:
                lines.append(f"  From: {', '.join(s.derived_from)}")

        lines.append("\n" + "=" * 50)
        return "\n".join(lines)

    def to_json(self) -> str:
        return json.dumps({
            "steps": [s.to_dict() for s in self._steps],
            "total_steps": len(self._steps),
        }, indent=2)

    def summary(self) -> dict:
        return {
            "total_steps": len(self._steps),
            "conclusions": [s.content for s in self._steps if s.type == "conclude"],
            "failed_goals": [s.content for s in self._steps if s.type == "fail"],
        }
