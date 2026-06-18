"""Runnable demo orchestration for case studies."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class DemoStep:
    name: str
    run: Callable[[], None]


@dataclass
class DemoRunner:
    """Run named demo steps and collect a text report."""

    title: str
    steps: list[DemoStep] = field(default_factory=list)

    def add_step(self, name: str, run: Callable[[], None]) -> None:
        self.steps.append(DemoStep(name=name, run=run))

    def run(self) -> str:
        lines = [f"=== {self.title} ==="]
        for step in self.steps:
            print(f"[demo] {step.name}")
            step.run()
            lines.append(f"- {step.name}: ok")
        lines.append("Demo complete.")
        return "\n".join(lines)
