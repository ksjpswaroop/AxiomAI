"""Audit trail viewer."""

from __future__ import annotations

import streamlit as st

from apps.console.api_client import ApiClient

st.header("Audit Trail")

client = ApiClient()

outcome = st.selectbox("Filter by outcome", ["", "ALLOW", "DENY", "ESCALATE"])
case_study = st.selectbox(
    "Filter by case study",
    ["", "cs-01", "cs-02", "cs-03", "cs-04", "cs-05", "cs-06", "cs-07", "cs-08",
     "cs-09", "cs-10", "cs-11", "cs-12", "cs-13", "cs-14", "cs-15", "cs-16", "cs-17", "cs-18"],
)
policy_id = st.text_input("Filter by policy_id (optional)", "")

params: dict[str, str] = {}
if outcome:
    params["outcome"] = outcome
if case_study:
    params["case_study"] = case_study
if policy_id:
    params["policy_id"] = policy_id

if st.button("Refresh"):
    try:
        data = client.query_audit(**params)
        st.metric("Entries", data.get("count", 0))
        for entry in data.get("entries", []):
            with st.expander(f"{entry.get('outcome')} — {entry.get('timestamp', '')[:19]}"):
                st.json(entry)
    except Exception as exc:
        st.error(str(exc))
