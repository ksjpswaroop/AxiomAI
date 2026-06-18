"""AxiomAI Console — Streamlit pilot product shell."""

from __future__ import annotations

import streamlit as st

from apps.console.api_client import ApiClient

st.set_page_config(
    page_title="AxiomAI Console",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("AxiomAI Console")
st.caption("Deterministic reasoning engine — facts + rules = proven answers")

client = ApiClient()

with st.sidebar:
    st.header("Connection")
    api_url = st.text_input("API URL", value=client.base_url)
    if api_url != client.base_url:
        client = ApiClient(api_url)
    try:
        health = client.health()
        st.success(f"API {health['status']} (v{health['version']})")
    except Exception as exc:
        st.error(f"API unreachable: {exc}")

st.markdown(
    """
Use the sidebar pages to:

- **Knowledge Base** — add facts and rules, run queries with proof viewer
- **Case Studies** — launch all 18 vertical demos (Tier 1–5)
- **Governance** — simulate agent actions across policy packs (ALLOW/DENY/ESCALATE)
- **Audit Trail** — browse governance decision log

**Stack:** Streamlit UI + FastAPI backend + SQLite persistence (optional).
"""
)
