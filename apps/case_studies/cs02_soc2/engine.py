"""SOC2 gap analysis engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from apps.case_studies.cs02_soc2.controls import (
    SOC2_CONTROLS,
    SOC2_RULES,
    SUPPLEMENTAL_FACTS,
    ControlDefinition,
)
from axiomai import Reasoner
from axiomai.connectors.base import Connector


@dataclass
class ControlResult:
    control_id: str
    name: str
    status: str  # PASS | FAIL
    severity: str
    gap_summary: str = ""
    evidence: list[str] = field(default_factory=list)


@dataclass
class GapReport:
    audit_id: str
    generated_at: str
    controls: list[ControlResult] = field(default_factory=list)

    @property
    def fail_count(self) -> int:
        return sum(1 for c in self.controls if c.status == "FAIL")

    @property
    def pass_count(self) -> int:
        return sum(1 for c in self.controls if c.status == "PASS")


class GapAnalysisEngine:
    """Run SOC2 control checks against connector evidence."""

    def __init__(self) -> None:
        self._connectors: list[Connector] = []

    def load_connectors(self, *connectors: Connector) -> None:
        self._connectors.extend(connectors)

    def run_audit(self) -> GapReport:
        reasoner = Reasoner(namespace="default")
        reasoner.kb.clear()
        for rule in SOC2_RULES:
            reasoner.add_rule(rule)

        predicates: list[str] = list(SUPPLEMENTAL_FACTS)
        for connector in self._connectors:
            predicates.extend(str(f.predicate) for f in connector.fetch_evidence())
        reasoner.add_facts(*predicates)

        forward = reasoner.forward_engine.run()
        derived = [str(f.predicate) for f in forward.all_derived]

        controls: list[ControlResult] = []
        for control in SOC2_CONTROLS:
            controls.append(self._evaluate_control(control, derived))

        return GapReport(
            audit_id=f"SOC2-{datetime.now(timezone.utc).strftime('%Y%m%d')}",
            generated_at=datetime.now(timezone.utc).isoformat(),
            controls=controls,
        )

    @staticmethod
    def _evaluate_control(control: ControlDefinition, derived: list[str]) -> ControlResult:
        gaps = [d for d in derived if d.startswith(f"{control.gap_prefix}(")]
        passes = [d for d in derived if d.startswith(f"{control.pass_prefix}(")]
        if gaps:
            return ControlResult(
                control_id=control.control_id,
                name=control.name,
                status="FAIL",
                severity=control.severity,
                gap_summary=gaps[0],
                evidence=gaps + passes,
            )
        return ControlResult(
            control_id=control.control_id,
            name=control.name,
            status="PASS",
            severity=control.severity,
            gap_summary="",
            evidence=passes,
        )
