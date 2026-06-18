# AxiomAI Feature Guide

## Reasoning Engine

Add facts (`Human(Socrates)`), rules (`IF Human(x) THEN Mortal(x)`), ask queries — get **PROVED** / **DISPROVED** with proof trees.

- **Console:** Knowledge Base page
- **API:** `POST /query`, `POST /forward`, `POST /resolution`
- **CLI:** `axiomai ask 'Mortal(Socrates)'`

## Agent Governance

Validate agent actions before execution. Outcomes: **ALLOW**, **DENY**, **ESCALATE** with proof.

- **Console:** Governance page (4 policy packs)
- **API:** `POST /governance/validate`
- **Production:** `AgentGovernanceMiddleware().intercept(action, context, policy_id=...)`

## LLM Extraction

Natural language → facts/rules. LLM translates; engine proves.

- **Console:** Knowledge Base → LLM extract tab
- **API:** `POST /extract`
- **Env:** `OPENAI_API_KEY` for real LLM; regex fallback without key

## Connectors

Ingest evidence from webhooks, files, and mock enterprise systems.

- **API:** `POST /connectors/webhook/facts`, `POST /connectors/file/ingest`
- **Demos:** CS-02 (Azure/AWS), CS-07 (SIEM)

## Persistent Storage

- **Env:** `AXIOMAI_PERSIST=sqlite:////data/axiomai.db`
- **API:** `GET /proofs`, `GET /inference-runs`

## Audit Trail

- **Env:** `AXIOMAI_AUDIT_PERSIST=/data/audit.json`
- **Console:** Audit Trail page
- **API:** `GET /audit`

## Brainstorming

Describe your problem → scope check + no-code test path.

- **Console:** Brainstorming page
- **API:** `POST /brainstorm`

## Desktop Demo

```bash
docker compose up
# API: http://localhost:8000
# UI:  http://localhost:8501
```
