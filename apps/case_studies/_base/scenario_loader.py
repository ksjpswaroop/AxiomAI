"""Load case study definitions and scenarios from JSON data files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def list_definitions() -> list[dict[str, Any]]:
    """Return metadata for all case study definition files."""
    items: list[dict[str, Any]] = []
    for path in sorted(DATA_DIR.glob("cs-*.json")):
        data = load_definition(path.stem)
        items.append(
            {
                "id": data["id"],
                "name": data["name"],
                "description": data.get("description", ""),
                "tier": data.get("tier", ""),
                "module": data.get("module", ""),
                "slug": data.get("slug", ""),
                "scenarios": list(data.get("scenarios", {}).keys()),
                "data_sources": data.get("data_sources", []),
            }
        )
    return items


def load_definition(case_id: str) -> dict[str, Any]:
    """Load full case study definition by ID (e.g. cs-01)."""
    path = DATA_DIR / f"{case_id}.json"
    if not path.exists():
        raise KeyError(f"No definition for case study: {case_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_scenario(case_id: str, scenario_id: str = "default") -> dict[str, Any]:
    """Load a single scenario from a case study definition."""
    definition = load_definition(case_id)
    scenarios = definition.get("scenarios", {})
    if scenario_id not in scenarios:
        raise KeyError(f"Unknown scenario '{scenario_id}' for {case_id}")
    return {
        **scenarios[scenario_id],
        "case_id": case_id,
        "scenario_id": scenario_id,
        "entity": scenarios[scenario_id].get("entity", definition.get("entity", "entity1")),
        "rules": definition.get("rules", []),
        "outcome_map": definition.get("outcome_map", {}),
        "story": definition.get("story", ""),
        "problem": definition.get("problem", ""),
        "data_sources": definition.get("data_sources", []),
    }
