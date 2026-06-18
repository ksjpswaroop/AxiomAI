"""File-based connector — load facts from CSV or JSON files."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from axiomai.connectors.base import BaseConnector
from axiomai.reasoner.core.models import Fact


class FileConnector(BaseConnector):
    """Ingest facts from a local CSV or JSON file."""

    def __init__(self, path: str | Path, source: str = "file"):
        self.path = Path(path)
        self.source = source

    def health(self) -> bool:
        return self.path.is_file()

    def fetch_evidence(self) -> list[Fact]:
        if not self.health():
            raise FileNotFoundError(f"Connector file not found: {self.path}")
        suffix = self.path.suffix.lower()
        if suffix == ".json":
            return self._load_json()
        if suffix == ".csv":
            return self._load_csv()
        raise ValueError(f"Unsupported file type: {self.path.suffix}")

    def _load_json(self) -> list[Fact]:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            predicates = [str(item) for item in data]
        elif isinstance(data, dict):
            raw = data.get("facts", data.get("predicates", []))
            predicates = [str(item) for item in raw]
        else:
            raise ValueError("JSON must be a list or object with a facts key")
        return self._facts_from_predicates(predicates)

    def _load_csv(self) -> list[Fact]:
        predicates: list[str] = []
        with self.path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames and "predicate" in reader.fieldnames:
                for row in reader:
                    value = (row.get("predicate") or "").strip()
                    if value:
                        predicates.append(value)
            else:
                handle.seek(0)
                plain = csv.reader(handle)
                for row in plain:
                    if not row:
                        continue
                    if row[0].lower() == "predicate":
                        continue
                    predicates.append(row[0].strip())
        return self._facts_from_predicates(predicates)
