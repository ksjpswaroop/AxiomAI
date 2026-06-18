"""Audit trail viewer."""

from __future__ import annotations

import streamlit as st

from apps.console.api_client import ApiClient

st.header("Audit Trail")

client = ApiClient()

outcome = st.selectbox("Filter by outcome", ["", "ALLOW", "DENY", "ESCALATE"])
case_study = st.selectbox("Filter by case study", ["", "cs-03", "cs-02", "cs-07"])

params: dict[str, str] = {}
if outcome:
    params["outcome"] = outcome
if case_study:
    params["case_study"] = case_study

if st.button("Refresh"):
    try:
        data = client.query_audit(**params)
        st.metric("Entries", data.get("count", 0))
        for entry in data.get("entries", []):
            with st.expander(f"{entry.get('outcome')} — {entry.get('timestamp', '')[:19]}"):
                st.json(entry)
    except Exception as exc:
        st.error(str(exc))
