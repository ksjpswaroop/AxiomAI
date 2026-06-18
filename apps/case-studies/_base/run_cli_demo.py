"""CLI helper for case study demos."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.case_studies.registry import run_case_study


def main(case_study_id: str) -> None:
    result = run_case_study(case_study_id)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_cli_demo.py <case-study-id>")
        sys.exit(1)
    main(sys.argv[1])
