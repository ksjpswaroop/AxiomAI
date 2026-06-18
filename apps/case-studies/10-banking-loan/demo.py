#!/usr/bin/env python3
"""Case study demo — cs-10"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from apps.case_studies.registry import run_case_study

def main() -> None:
    result = run_case_study("cs-10")
    print(f"Case Study: cs-10")
    print(f"Outcome: {result.get('outcome', 'N/A')}")
    if result.get("explanation"):
        print(f"Explanation: {result['explanation']}")
    if result.get("conclusions"):
        for c in result["conclusions"]:
            print(f"  - {c}")

if __name__ == "__main__":
    main()
