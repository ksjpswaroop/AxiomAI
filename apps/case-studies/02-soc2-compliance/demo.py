#!/usr/bin/env python3
"""CS-02 SOC2 compliance automation demo."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.case_studies._base import DemoRunner
from apps.case_studies.cs02_soc2.engine import GapAnalysisEngine
from apps.case_studies.cs02_soc2.report import (
    export_gap_report_json,
    export_gap_report_markdown,
)
from axiomai.connectors import AWSConfigConnector, AzureADConnector

OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def main() -> None:
    holder: dict = {}

    def run_audit() -> None:
        engine = GapAnalysisEngine()
        engine.load_connectors(AzureADConnector(), AWSConfigConnector())
        holder["report"] = engine.run_audit()

    def export_reports() -> None:
        OUTPUT_DIR.mkdir(exist_ok=True)
        report = holder["report"]
        md_path = OUTPUT_DIR / "gap_report.md"
        json_path = OUTPUT_DIR / "gap_report.json"
        md_path.write_text(export_gap_report_markdown(report), encoding="utf-8")
        json_path.write_text(export_gap_report_json(report), encoding="utf-8")
        print(export_gap_report_markdown(report))
        print(f"\nExported: {md_path}")
        print(f"Exported: {json_path}")

    runner = DemoRunner("CS-02 SOC2 Compliance Automation")
    runner.add_step("Collect Azure AD + AWS evidence", run_audit)
    runner.add_step("Run gap analysis and export reports", export_reports)
    runner.run()


if __name__ == "__main__":
    main()
