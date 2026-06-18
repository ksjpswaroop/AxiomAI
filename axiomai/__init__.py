"""AxiomAI — Top-level package. Import from here: from axiomai import Reasoner"""

from axiomai.governance import (
    AgentGovernanceMiddleware,
    AuditLog,
    Decision,
    EscalationRouter,
    GovernanceEngine,
    PolicyPack,
    PolicyRegistry,
)
from axiomai.reasoner.core.models import Entity, Fact, Predicate, Rule
from axiomai.reasoner.engine import QueryResult, Reasoner
from axiomai.reasoner.explain.proof import ProofTree
from axiomai.reasoner.integrations.llm_extractor import LLMExtractor
from axiomai.reasoner.kb.store import KnowledgeBase

__version__ = "0.3.0"
__all__ = [
    "Reasoner",
    "QueryResult",
    "Fact",
    "Rule",
    "Predicate",
    "Entity",
    "ProofTree",
    "KnowledgeBase",
    "LLMExtractor",
    "AgentGovernanceMiddleware",
    "AuditLog",
    "Decision",
    "EscalationRouter",
    "GovernanceEngine",
    "PolicyPack",
    "PolicyRegistry",
]
