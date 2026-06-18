"""SOC2 gap report exporters."""

from __future__ import annotations

import json

from apps.case_studies.cs02_soc2.engine import GapReport


def export_gap_report_json(report: GapReport) -> str:
    payload = {
        "audit_id": report.audit_id,
        "generated_at": report.generated_at,
        "summary": {"pass": report.pass_count, "fail": report.fail_count},
        "controls": [
            {
                "control_id": c.control_id,
                "name": c.name,
                "status": c.status,
                "severity": c.severity,
                "gap": c.gap_summary,
                "evidence": c.evidence,
            }
            for c in report.controls
        ],
    }
    return json.dumps(payload, indent=2)


def export_gap_report_markdown(report: GapReport) -> str:
    lines = [
        "# SOC2 Control Gap Report",
        "",
        f"Audit ID: {report.audit_id}",
        f"Generated: {report.generated_at}",
        f"Summary: {report.pass_count} PASS / {report.fail_count} FAIL",
        "",
    ]
    for control in report.controls:
        lines.extend([
            f"## Control: {control.name}",
            f"Control ID: {control.control_id}",
            f"Status: **{control.status}**",
            "",
        ])
        if control.status == "FAIL":
            lines.append("Evidence:")
            for item in control.evidence:
                mark = "✗" if "Gap" in item or "Disabled" in item or "Not" in item else "✓"
                lines.append(f"  • {item} {mark}")
            lines.append(f"Gap: {control.gap_summary}")
            lines.append(f"Severity: {control.severity}")
        else:
            lines.append("Evidence:")
            for item in control.evidence:
                lines.append(f"  • {item} ✓")
        lines.append("")
    return "\n".join(lines)
