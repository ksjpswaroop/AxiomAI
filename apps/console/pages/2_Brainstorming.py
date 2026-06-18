"""Brainstorming — scope check and no-code implementation path."""

from __future__ import annotations

import streamlit as st

from apps.console.api_client import ApiClient

st.header("Brainstorming")
st.caption("Describe your problem — we'll tell you if AxiomAI is in scope and how to test without coding")

client = ApiClient()

description = st.text_area(
    "Describe your use case",
    height=150,
    placeholder="e.g. Our AI support agent approves refunds outside policy. We need proof and audit for compliance...",
)

examples = [
    "LLM support agent refund governance with audit trail",
    "SOC2 compliance gap analysis from Azure AD and AWS",
    "Ransomware root cause analysis from SIEM alerts",
    "Block AI procurement agent from unapproved vendor purchases",
    "Prior authorization for healthcare procedures",
]
st.caption("Examples: " + " · ".join(examples))

if st.button("Analyze scope", type="primary", disabled=not description or len(description) < 10):
    try:
        result = client.brainstorm(description)
    except Exception as exc:
        st.error(str(exc))
        st.stop()

    if result.get("in_scope"):
        st.success(f"In scope ({result.get('confidence', '')} confidence)")
        st.write(result.get("summary", ""))
    else:
        st.warning("Likely out of scope")
        st.write(result.get("out_of_scope_reason", ""))

    if result.get("matched_case_studies"):
        st.markdown("**Matching case studies**")
        for cs in result["matched_case_studies"]:
            st.write(f"- `{cs}` — run in Case Study Gallery")

    if result.get("matched_features"):
        st.markdown("**Matching platform features**")
        for feat in result["matched_features"]:
            st.write(f"- {feat}")

    if result.get("how_to_test"):
        st.markdown("**How to test (no code)**")
        for i, step in enumerate(result["how_to_test"], 1):
            st.write(f"{i}. {step}")

    if result.get("how_to_production"):
        st.markdown("**Path to production**")
        for i, step in enumerate(result["how_to_production"], 1):
            st.write(f"{i}. {step}")

    with st.expander("Raw analysis"):
        st.json(result)
