"""Feature guides — all platform capabilities."""

from __future__ import annotations

import streamlit as st

st.header("Feature Guides")
st.caption("How to use every AxiomAI capability — no coding required")

GUIDES = {
    "Reasoning engine": {
        "summary": "Add facts and rules, ask queries, get PROVED/DISPROVED with proof trees.",
        "steps": [
            "Knowledge Base → add fact `Human(Socrates)`",
            "Add rule `IF Human(x) THEN Mortal(x)`",
            "Query `Mortal(Socrates)` → PROVED with proof",
            "API: POST /query, POST /forward, POST /resolution",
        ],
        "production": "Reasoner(persist='sqlite:///kb.db') for durable knowledge",
    },
    "Agent governance": {
        "summary": "Validate agent actions against YAML policy packs before execution.",
        "steps": [
            "Governance → select policy (refund, procurement, data-access, cloud-cost)",
            "Enter action + context facts → ALLOW / DENY / ESCALATE",
            "View proof trace and escalation queue",
            "API: POST /governance/validate with policy_id",
        ],
        "production": "AgentGovernanceMiddleware().intercept(action, context, policy_id=...)",
    },
    "Resolution theorem proving": {
        "summary": "Full refutation prover with SOS, subsumption, Z3 fallback.",
        "steps": [
            "Knowledge Base → load Socrates example",
            "Query with mode=resolution",
            "View resolution steps in proof tree",
        ],
        "production": "reasoner.ask(query, mode='resolution')",
    },
    "Connectors": {
        "summary": "Ingest evidence from files, webhooks, and mock enterprise systems.",
        "steps": [
            "POST /connectors/webhook/facts with predicate list",
            "POST /connectors/file/ingest for JSON/CSV",
            "CS-02 demo: Azure AD + AWS Config mock connectors",
            "CS-07 demo: SIEM connector merges alert facts",
        ],
        "production": "FileConnector, WebhookConnector, custom Connector protocol",
    },
    "Persistent storage": {
        "summary": "SQLite-backed facts, rules, proofs, inference runs, contradictions.",
        "steps": [
            "Set AXIOMAI_PERSIST=sqlite:////data/axiomai.db",
            "Run queries — proofs auto-persisted",
            "GET /proofs and GET /inference-runs",
        ],
        "production": "Reasoner(persist='sqlite:///prod.db')",
    },
    "LLM extraction": {
        "summary": "NL → facts/rules (LLM translates, engine proves). Fallback regex without API key.",
        "steps": [
            "Knowledge Base → Extract tab or POST /extract",
            "CLI: axiomai extract \"Socrates is human\"",
            "Set OPENAI_API_KEY for real LLM path",
        ],
        "production": "Reasoner(llm='openai') — never let LLM make final decisions",
    },
    "Audit trail": {
        "summary": "Append-only governance decision log with proof JSON.",
        "steps": [
            "Run governance validations or case studies",
            "Audit Trail page → filter by outcome / case study",
            "Set AXIOMAI_AUDIT_PERSIST for file-backed audit",
        ],
        "production": "GET /audit?outcome=DENY&policy_id=refund-policy",
    },
    "Constraints & planning": {
        "summary": "Z3 CSP solver, Sudoku demo, STRIPS planner.",
        "steps": [
            "POST /sudoku for constraint demo",
            "POST /planning/plan for goal planning",
        ],
        "production": "ConstraintSolver, PlanningEngine via Reasoner facade",
    },
}

for name, guide in GUIDES.items():
    with st.expander(name, expanded=name == "Reasoning engine"):
        st.write(guide["summary"])
        st.markdown("**Try it now**")
        for step in guide["steps"]:
            st.write(f"- {step}")
        st.markdown("**Production**")
        st.code(guide["production"])

st.markdown("---")
st.markdown("Full docs: `docs/guides/FEATURES.md` · Per case study: `docs/guides/case-studies/`")
