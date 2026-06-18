"""Policy packs — load domain rules from YAML or JSON."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PolicyPack:
    """Versioned set of policy rules and decision queries."""

    name: str
    version: str = "1.0"
    action_type: str = "action"
    rules: list[str] = field(default_factory=list)
    allow_query: str = ""
    deny_queries: list[str] = field(default_factory=list)
    escalate_queries: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str | Path) -> PolicyPack:
        """Load a policy pack from a YAML or JSON file."""
        path = Path(path)
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() in (".yaml", ".yml"):
            try:
                import yaml
            except ImportError as exc:
                raise ImportError(
                    "PyYAML is required to load YAML policy packs. "
                    "Install with: pip install pyyaml"
                ) from exc
            data = yaml.safe_load(text)
        else:
            data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError(f"Policy file must contain a mapping: {path}")
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PolicyPack:
        known = {
            "name",
            "version",
            "action_type",
            "rules",
            "allow_query",
            "deny_queries",
            "escalate_queries",
        }
        metadata = {k: v for k, v in data.items() if k not in known}
        return cls(
            name=str(data.get("name", "unnamed-policy")),
            version=str(data.get("version", "1.0")),
            action_type=str(data.get("action_type", "action")),
            rules=[str(r) for r in data.get("rules", [])],
            allow_query=str(data.get("allow_query", "")),
            deny_queries=[str(q) for q in data.get("deny_queries", [])],
            escalate_queries=[str(q) for q in data.get("escalate_queries", [])],
            metadata=metadata,
        )

    def format_query(self, template: str, entity: str) -> str:
        return template.format(entity=entity)
