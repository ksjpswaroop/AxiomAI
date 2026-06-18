"""Webhook connector — receive facts via HTTP POST."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from axiomai.connectors.base import BaseConnector
from axiomai.reasoner.core.models import Fact


class WebhookConnector(BaseConnector):
    """Buffer facts posted to a webhook endpoint."""

    def __init__(self, source: str = "webhook"):
        self.source = source
        self._predicates: list[str] = []

    def ingest(self, payload: dict[str, Any] | list[Any]) -> list[Fact]:
        predicates = self._extract_predicates(payload)
        self._predicates.extend(predicates)
        return self._facts_from_predicates(predicates)

    def fetch_evidence(self) -> list[Fact]:
        return self._facts_from_predicates(list(self._predicates))

    def clear(self) -> None:
        self._predicates.clear()

    def as_router(self) -> APIRouter:
        router = APIRouter()

        @router.post("/webhook/facts")
        def receive_facts(payload: dict[str, Any] | list[Any]) -> dict[str, Any]:
            facts = self.ingest(payload)
            return {"received": len(facts), "facts": [str(f.predicate) for f in facts]}

        return router

    @staticmethod
    def _extract_predicates(payload: dict[str, Any] | list[Any]) -> list[str]:
        if isinstance(payload, list):
            return [str(item) for item in payload]
        raw = payload.get("facts", payload.get("predicates", []))
        return [str(item) for item in raw]
