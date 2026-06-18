"""Brainstorming scope matcher — map user problems to AxiomAI capabilities."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ScopeMatch:
    in_scope: bool
    confidence: str  # high | medium | low
    summary: str
    matched_case_studies: list[str] = field(default_factory=list)
    matched_features: list[str] = field(default_factory=list)
    how_to_test: list[str] = field(default_factory=list)
    how_to_production: list[str] = field(default_factory=list)
    out_of_scope_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "in_scope": self.in_scope,
            "confidence": self.confidence,
            "summary": self.summary,
            "matched_case_studies": self.matched_case_studies,
            "matched_features": self.matched_features,
            "how_to_test": self.how_to_test,
            "how_to_production": self.how_to_production,
            "out_of_scope_reason": self.out_of_scope_reason,
        }


# Keywords → case study IDs + features
_SCOPE_RULES: list[dict[str, Any]] = [
  {
    "keywords": ["refund", "support agent", "customer service", "chargeback", "return policy"],
    "cases": ["cs-03"],
    "features": ["governance", "audit", "backward_chaining"],
    "summary": "Agent governance for customer support actions with proof and audit trail.",
  },
  {
    "keywords": ["soc2", "compliance", "audit control", "hipaa", "pci", "gdpr gap", "azure ad", "aws config"],
    "cases": ["cs-02", "cs-12"],
    "features": ["connectors", "forward_chaining", "contradiction_detection"],
    "summary": "Automated compliance gap analysis and data access governance.",
  },
  {
    "keywords": ["ransomware", "breach", "incident", "root cause", "attack chain", "siem", "cyber", "security"],
    "cases": ["cs-07", "cs-05"],
    "features": ["causal", "backward_chaining", "connectors"],
    "summary": "Cybersecurity root cause analysis and code deploy guardrails.",
  },
  {
    "keywords": ["procurement", "purchase", "vendor", "contract approval", "spend"],
    "cases": ["cs-06"],
    "features": ["governance", "policy_packs"],
    "summary": "Procurement agent governance — block unapproved purchases.",
  },
  {
    "keywords": ["cloud cost", "finops", "gpu", "aws bill", "azure spend", "budget"],
    "cases": ["cs-13"],
    "features": ["governance", "policy_packs"],
    "summary": "Cloud cost governance and resource approval policies.",
  },
  {
    "keywords": ["prior auth", "healthcare", "clinical", "patient", "hipaa", "medical"],
    "cases": ["cs-04"],
    "features": ["backward_chaining", "rules"],
    "summary": "Healthcare prior authorization with clinical criteria rules.",
  },
  {
    "keywords": ["loan", "underwriting", "credit", "banking", "mortgage", "fraud"],
    "cases": ["cs-10"],
    "features": ["backward_chaining", "rules"],
    "summary": "Banking loan eligibility and decline rules.",
  },
  {
    "keywords": ["insurance", "claim", "coverage", "policy holder"],
    "cases": ["cs-09"],
    "features": ["backward_chaining", "rules"],
    "summary": "Insurance claims validation against coverage rules.",
  },
  {
    "keywords": ["contract", "sla", "breach", "obligation", "renewal"],
    "cases": ["cs-08"],
    "features": ["forward_chaining", "rules"],
    "summary": "Contract SLA breach detection and obligation triggers.",
  },
  {
    "keywords": ["vpn", "network", "outage", "certificate", "msp", "dns"],
    "cases": ["cs-01"],
    "features": ["backward_chaining", "causal"],
    "summary": "MSP network operations root cause analysis.",
  },
  {
    "keywords": ["hr", "leave", "benefits", "parental", "pto", "employee policy"],
    "cases": ["cs-11"],
    "features": ["rules", "backward_chaining"],
    "summary": "HR policy engine for benefits and leave eligibility.",
  },
  {
    "keywords": ["manufacturing", "defect", "quality", "qc", "scrap", "assembly"],
    "cases": ["cs-14"],
    "features": ["backward_chaining", "causal"],
    "summary": "Manufacturing defect root cause diagnosis.",
  },
  {
    "keywords": ["education", "degree", "graduation", "enrollment", "transcript"],
    "cases": ["cs-15"],
    "features": ["rules", "forward_chaining"],
    "summary": "Education degree audit and graduation eligibility.",
  },
  {
    "keywords": ["immigration", "h-1b", "h1b", "visa", "petition"],
    "cases": ["cs-16"],
    "features": ["rules", "checklist"],
    "summary": "Immigration filing eligibility checklist.",
  },
  {
    "keywords": ["sales", "lead", "qualification", "icp", "routing", "crm"],
    "cases": ["cs-17"],
    "features": ["rules", "forward_chaining"],
    "summary": "Sales lead qualification and routing.",
  },
  {
    "keywords": ["trading", "position limit", "portfolio", "halt", "broker", "agentic trading"],
    "cases": ["cs-18"],
    "features": ["governance", "constraints"],
    "summary": "Agentic trading guardrails and position limits.",
  },
  {
    "keywords": ["secret", "deploy", "code review", "vulnerability", "insecure", "api key"],
    "cases": ["cs-05"],
    "features": ["governance", "rules"],
    "summary": "AI code review guardrail before deployment.",
  },
  {
    "keywords": ["pii", "phi", "pci", "data access", "salesforce", "access control"],
    "cases": ["cs-12"],
    "features": ["governance", "policy_packs"],
    "summary": "Data governance and role-based access control.",
  },
  {
    "keywords": ["prove", "deduce", "logic", "rule", "fact", "inference", "reasoning"],
    "cases": [],
    "features": ["backward_chaining", "forward_chaining", "resolution", "query"],
    "summary": "Core deterministic reasoning — facts + rules = proven answers.",
  },
  {
    "keywords": ["sudoku", "constraint", "csp", "optimization", "schedule"],
    "cases": [],
    "features": ["constraints", "z3"],
    "summary": "Constraint solving with Z3 (CSP, Sudoku, scheduling).",
  },
  {
    "keywords": ["plan", "strips", "robot", "workflow steps"],
    "cases": [],
    "features": ["planning"],
    "summary": "STRIPS planning from goals and actions.",
  },
]

_FEATURE_GUIDE: dict[str, list[str]] = {
    "governance": [
        "Open Governance page → select policy pack → validate agent action",
        "API: POST /governance/validate with action + context facts",
        "Production: set AXIOMAI_AUDIT_PERSIST for audit trail persistence",
    ],
    "backward_chaining": [
        "Open Knowledge Base → add facts and rules → ask a query",
        "API: POST /query with mode=backward",
        "Production: Reasoner(persist='sqlite:///kb.db') for durable KB",
    ],
    "forward_chaining": [
        "Knowledge Base → add rules → POST /forward to derive all facts",
        "Use for compliance checks where all implications must be found",
    ],
    "resolution": [
        "POST /query with mode=resolution for theorem-proving style proofs",
        "Best for small KBs and refutation proofs",
    ],
    "connectors": [
        "POST /connectors/webhook/facts to ingest evidence",
        "Use FileConnector for CSV/JSON batch ingest",
        "CS-02 demo shows Azure AD + AWS mock connectors",
    ],
    "constraints": [
        "POST /sudoku or /constraints/solve for CSP problems",
    ],
    "audit": [
        "Governance Audit Trail page or GET /audit",
        "Filter by outcome, case study, policy_id",
    ],
    "query": [
        "Describe facts as predicates: Human(Socrates)",
        "Add rules: IF Human(x) THEN Mortal(x)",
        "Ask: Mortal(Socrates) → PROVED with proof tree",
    ],
}


def _keyword_matches(keyword: str, text: str) -> bool:
    """Match keywords without substring false positives (e.g. phi in graphics)."""
    if " " in keyword:
        return keyword in text
    return re.search(rf"\b{re.escape(keyword)}s?\b", text) is not None


def analyze_problem(description: str) -> ScopeMatch:
    """Match a natural-language problem description to AxiomAI scope."""
    text = description.lower()
    matched_cases: list[str] = []
    matched_features: list[str] = []
    summaries: list[str] = []
    best_score = 0

    for rule in _SCOPE_RULES:
        score = sum(1 for kw in rule["keywords"] if _keyword_matches(kw, text))
        if score > 0:
            matched_cases.extend(rule["cases"])
            matched_features.extend(rule["features"])
            summaries.append(rule["summary"])
            best_score = max(best_score, score)

    matched_cases = list(dict.fromkeys(matched_cases))
    matched_features = list(dict.fromkeys(matched_features))

    if best_score == 0:
        return ScopeMatch(
            in_scope=False,
            confidence="low",
            summary="No strong match to AxiomAI's deterministic reasoning scope.",
            out_of_scope_reason=(
                "AxiomAI proves answers from explicit facts and rules — it does not replace "
                "general LLM chat, image generation, or unstructured data mining. "
                "Try describing policies, rules, or logical constraints you need enforced."
            ),
            how_to_test=["Open Brainstorming page and add domain-specific keywords (refund, compliance, etc.)"],
        )

    confidence = "high" if best_score >= 2 else "medium"
    how_to_test: list[str] = []
    how_to_production: list[str] = []

    for case_id in matched_cases[:3]:
        how_to_test.append(f"Case Studies → run {case_id.upper()} demo (try default + blocked scenarios)")
    for feat in matched_features[:4]:
        how_to_test.extend(_FEATURE_GUIDE.get(feat, [])[:1])
        how_to_production.append(f"Enable {feat} via API or Reasoner facade in your agent pipeline")

    how_to_production.extend([
        "docker compose up — run API + UI locally",
        "Set AXIOMAI_PERSIST and AXIOMAI_AUDIT_PERSIST for production audit",
        "Load domain rules from YAML policy packs or REST /facts + /rules",
    ])

    return ScopeMatch(
        in_scope=True,
        confidence=confidence,
        summary=" ".join(summaries[:2]),
        matched_case_studies=matched_cases,
        matched_features=matched_features,
        how_to_test=list(dict.fromkeys(how_to_test))[:6],
        how_to_production=list(dict.fromkeys(how_to_production))[:6],
    )
