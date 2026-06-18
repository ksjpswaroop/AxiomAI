"""Shared pytest fixtures for AxiomAI."""

from __future__ import annotations

import pytest

from axiomai import Reasoner


@pytest.fixture
def reasoner() -> Reasoner:
    """Fresh Reasoner instance per test."""
    return Reasoner()


@pytest.fixture
def socrates_kb(reasoner: Reasoner) -> Reasoner:
    """Reasoner loaded with the classic Socrates example."""
    reasoner.load_socrates()
    return reasoner
