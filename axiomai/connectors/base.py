"""Connector protocol and base implementation."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from axiomai.reasoner.core.models import Fact


@runtime_checkable
class Connector(Protocol):
    """Interface for evidence ingestion connectors."""

    def fetch_evidence(self) -> list[Fact]:
        """Return facts fetched from the external system."""
        ...

    def health(self) -> bool:
        """Return True when the connector is operational."""
        ...


class BaseConnector:
    """Base class with shared connector utilities."""

    source: str = "connector"

    def health(self) -> bool:
        return True

    def _facts_from_predicates(self, predicates: list[str]) -> list[Fact]:
        from axiomai.reasoner.core.parser import Parser

        parser = Parser()
        return [parser.parse_fact(p, source=self.source) for p in predicates]
