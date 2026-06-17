"""
AxiomAI Reasoner — Deterministic Reasoning Engine
Facts + Rules = Proven Answers
"""

__version__ = "0.2.0"

from axiomai.reasoner.engine import Reasoner, QueryResult
from axiomai.reasoner.core.models import Fact, Rule, Predicate, Entity
from axiomai.reasoner.explain.proof import ProofTree
from axiomai.reasoner.kb.store import KnowledgeBase

__all__ = [
    "Reasoner",
    "QueryResult",
    "Fact",
    "Rule",
    "Predicate",
    "Entity",
    "ProofTree",
    "KnowledgeBase",
]
