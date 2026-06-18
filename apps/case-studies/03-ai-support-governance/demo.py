#!/usr/bin/env python3
"""CS-03 AI customer support governance demo."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.case_studies._base import DemoRunner, format_decision_report
from apps.case_studies.cs03_support_governance.engine import SupportGovernanceDemo
from apps.case_studies.cs03_support_governance.report import (
    format_audit_trail,
    format_llm_denial_report,
)

POLICY = ROOT / "axiomai" / "governance" / "policies" / "refund-policy.yaml"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def main() -> None:
    holder: dict = {}

    def simulate_llm() -> None:
        demo = SupportGovernanceDemo(POLICY)
        holder["llm_result"] = demo.simulate_llm_refund_request(
            customer="order1",
            amount=350,
            days_since_purchase=43,
            product_returned=False,
        )
        holder["all_results"] = demo.run_all_scenarios()

    def print_reports() -> None:
        result = holder["llm_result"]
        print("LLM Agent suggests: Refund customer $350")
        print()
        print(format_llm_denial_report(result))
        print()
        print(format_decision_report("Refund Governance", result.action, result.decision))

        trail = format_audit_trail(holder["all_results"])
        OUTPUT_DIR.mkdir(exist_ok=True)
        audit_path = OUTPUT_DIR / "audit_log.json"
        audit_path.write_text(json.dumps(trail, indent=2), encoding="utf-8")
        print(f"\nAudit log ({len(trail)} entries) → {audit_path}")

    runner = DemoRunner("CS-03 AI Customer Support Governance")
    runner.add_step("Simulate LLM refund request", simulate_llm)
    runner.add_step("Governance check + audit trail", print_reports)
    runner.run()


if __name__ == "__main__":
    main()
