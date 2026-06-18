#!/usr/bin/env python3
"""CS-07 Cybersecurity root cause analysis demo."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.case_studies._base import DemoRunner
from apps.case_studies.cs07_cybersecurity.engine import IncidentAnalyzer, load_scenario
from apps.case_studies.cs07_cybersecurity.report import (
    format_incident_report,
    format_mttr_report,
)
from axiomai.connectors import SIEMConnector

SCENARIO = Path(__file__).resolve().parent / "scenarios" / "ransomware_incident.json"
PACKAGE_SCENARIO = ROOT / "apps" / "case_studies" / "cs07_cybersecurity" / "scenarios" / "ransomware_incident.json"


def main() -> None:
    scenario_path = SCENARIO if SCENARIO.exists() else PACKAGE_SCENARIO
    holder: dict = {}

    def ingest() -> None:
        scenario = load_scenario(scenario_path)
        siem_facts = [str(f.predicate) for f in SIEMConnector().fetch_evidence()]
        scenario["facts"].extend(
            {"predicate": p, "timestamp": "", "evidence": f"SIEM: {p}"} for p in siem_facts
        )
        holder["result"] = IncidentAnalyzer().analyze(scenario)

    def report() -> None:
        print(format_incident_report(holder["result"]))
        print()
        print(format_mttr_report(holder["result"]))

    runner = DemoRunner("CS-07 Cybersecurity Root Cause Analysis")
    runner.add_step("Ingest SIEM + scenario facts", ingest)
    runner.add_step("Generate incident + MTTR report", report)
    runner.run()


if __name__ == "__main__":
    main()
