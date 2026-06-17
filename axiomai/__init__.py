"""
AxiomAI — Deterministic Reasoning Engine
Facts + Rules = Proven Answers
"""

__version__ = "0.1.0"
__author__ = "AxiomAI Team"

from axiomai.engine import AxiomEngine
from axiomai.facts import FactStore
from axiomai.rules import RuleStore
from axiomai.proof_trace import ProofTrace

__all__ = [
    "AxiomEngine",
    "FactStore",
    "RuleStore",
    "ProofTrace",
]
