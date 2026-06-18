"""HTTP client for the AxiomAI console."""

from __future__ import annotations

import os
from typing import Any

import httpx

API_URL = os.environ.get("AXIOMAI_API_URL", "http://localhost:8000")


class ApiClient:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or API_URL).rstrip("/")

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def health(self) -> dict[str, Any]:
        r = httpx.get(self._url("/health"), timeout=30.0)
        r.raise_for_status()
        return r.json()

    def list_facts(self) -> list[dict]:
        r = httpx.get(self._url("/facts"), timeout=30.0)
        r.raise_for_status()
        return r.json()

    def add_fact(self, predicate: str) -> dict:
        r = httpx.post(self._url("/facts"), json={"predicate": predicate}, timeout=30.0)
        r.raise_for_status()
        return r.json()

    def list_rules(self) -> list[dict]:
        r = httpx.get(self._url("/rules"), timeout=30.0)
        r.raise_for_status()
        return r.json()

    def add_rule(self, rule_str: str) -> dict:
        r = httpx.post(self._url("/rules"), json={"rule_str": rule_str}, timeout=30.0)
        r.raise_for_status()
        return r.json()

    def query(self, query: str, mode: str = "auto") -> dict:
        r = httpx.post(
            self._url("/query"),
            json={"query": query, "mode": mode},
            timeout=60.0,
        )
        r.raise_for_status()
        return r.json()

    def reset(self) -> None:
        httpx.post(self._url("/reset"), timeout=30.0).raise_for_status()

    def list_case_studies(self) -> list[dict]:
        r = httpx.get(self._url("/case-studies"), timeout=30.0)
        r.raise_for_status()
        return r.json()

    def run_case_study(self, case_id: str) -> dict:
        r = httpx.post(self._url(f"/case-studies/{case_id}/run"), timeout=120.0)
        r.raise_for_status()
        return r.json()

    def validate_governance(
        self,
        action: dict,
        context: list[str],
        case_study: str | None = None,
        policy_id: str = "refund-policy",
        nl_context: str | None = None,
    ) -> dict:
        payload: dict = {
            "action": action,
            "context": context,
            "policy_id": policy_id,
        }
        if case_study:
            payload["case_study"] = case_study
        if nl_context:
            payload["nl_context"] = nl_context
        r = httpx.post(self._url("/governance/validate"), json=payload, timeout=60.0)
        r.raise_for_status()
        return r.json()

    def list_policies(self) -> list[dict]:
        r = httpx.get(self._url("/policies"), timeout=30.0)
        r.raise_for_status()
        return r.json()["policies"]

    def extract(self, text: str, load: bool = True) -> dict:
        r = httpx.post(
            self._url("/extract"),
            json={"text": text, "load": load},
            timeout=60.0,
        )
        r.raise_for_status()
        return r.json()

    def query_audit(self, **params: str) -> dict:
        r = httpx.get(self._url("/audit"), params=params, timeout=30.0)
        r.raise_for_status()
        return r.json()
