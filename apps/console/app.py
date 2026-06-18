"""AxiomAI Investor Console — desktop demo for all features and 18 case studies."""

from __future__ import annotations

import streamlit as st

from apps.console.api_client import ApiClient

st.set_page_config(
    page_title="AxiomAI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("AxiomAI")
st.caption("Deterministic reasoning for enterprise AI — facts + rules = proven answers")

client = ApiClient()

with st.sidebar:
    st.header("Connection")
    api_url = st.text_input("API URL", value=client.base_url)
    if api_url != client.base_url:
        client = ApiClient(api_url)
    try:
        health = client.health()
        st.success(f"API {health['status']} · v{health['version']}")
    except Exception as exc:
        st.error(f"API unreachable: {exc}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Case studies", "18")
col2.metric("Policy packs", "4")
col3.metric("Inference modes", "6")
col4.metric("Proof", "Always")

st.markdown("---")

st.subheader("Investor demo path (5 minutes)")
path = st.columns(3)
with path[0]:
    st.markdown("**1. Cybersecurity** — CS-07 ransomware RCA with attack chain + MTTR")
with path[1]:
    st.markdown("**2. Governance** — CS-03 refund agent blocked with audit proof")
with path[2]:
    st.markdown("**3. Compliance** — CS-02 SOC2 gap analysis from cloud connectors")

st.markdown("---")
st.subheader("Platform capabilities")

features = [
    ("Reasoning engine", "Backward / forward / resolution chaining with proof trees", "Knowledge Base"),
    ("Agent governance", "ALLOW · DENY · ESCALATE with policy packs + audit", "Governance"),
    ("18 vertical demos", "Real scenarios with open-reference data sources", "Case Study Gallery"),
    ("Scope brainstorm", "Describe your problem — in-scope check + no-code path", "Brainstorming"),
    ("Connectors", "Webhook + file ingest + Azure/AWS/SIEM mocks", "Feature Guides"),
]
for title, desc, page in features:
    with st.expander(title):
        st.write(desc)
        st.caption(f"→ Sidebar: {page}")

st.info(
    "All demo data is **synthetic** — modeled on open standards (MITRE ATT&CK, SOC2, NIST, OWASP). "
    "No customer PII. Production deployments connect your policies and evidence sources."
)

st.markdown("**Quick start:** `docker compose up` → open http://localhost:8501")
