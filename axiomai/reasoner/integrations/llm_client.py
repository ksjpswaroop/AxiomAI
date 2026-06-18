"""
LLM client abstraction — decouples extraction from a specific provider.
"""

from __future__ import annotations

import json
import os
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    """Protocol for JSON-completion LLM backends."""

    def complete_json(self, system: str, user: str, *, model: str | None = None) -> dict[str, Any]:
        """Return parsed JSON object from the model."""
        ...


class OpenAIClient:
    """OpenAI Chat Completions adapter."""

    def __init__(self, client: Any = None, model: str = "gpt-4o"):
        if client is None:
            try:
                from openai import OpenAI

                client = OpenAI()
            except ImportError as exc:
                raise ImportError(
                    "openai package required. Install with: pip install axiomai[llm]"
                ) from exc
        self._client = client
        self._default_model = model

    def complete_json(self, system: str, user: str, *, model: str | None = None) -> dict[str, Any]:
        response = self._client.chat.completions.create(
            model=model or self._default_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        return json.loads(content)


class MockLLMClient:
    """Deterministic mock for tests — returns canned JSON per user text substring."""

    def __init__(self, responses: dict[str, dict[str, Any]] | None = None):
        self._responses = responses or {}
        self.calls: list[tuple[str, str]] = []

    def complete_json(self, system: str, user: str, *, model: str | None = None) -> dict[str, Any]:
        self.calls.append((system, user))
        for key, payload in self._responses.items():
            if key in user:
                return payload
        return {"facts": [], "rules": []}


def create_llm_client(
    provider: str | None = None,
    *,
    model: str = "gpt-4o",
) -> LLMClient | None:
    """
    Factory: create an LLM client from provider name or environment.

    Checks ``AXIOMAI_LLM_PROVIDER`` then ``OPENAI_API_KEY``.
    Returns ``None`` when no provider is configured (fallback extraction used).
    """
    provider = (provider or os.environ.get("AXIOMAI_LLM_PROVIDER", "")).lower()
    if not provider and os.environ.get("OPENAI_API_KEY"):
        provider = "openai"
    if provider == "openai":
        try:
            return OpenAIClient(model=model)
        except ImportError:
            return None
    if provider == "mock":
        return MockLLMClient()
    return None
