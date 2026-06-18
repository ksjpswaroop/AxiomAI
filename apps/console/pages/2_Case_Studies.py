"""Case study launcher for Tier 1 vertical demos."""

from __future__ import annotations

import streamlit as st

from apps.console.api_client import ApiClient

st.header("Case Study Launcher")
st.caption("All 18 vertical demos — Tier 1 through Tier 5")

client = ApiClient()

try:
    studies = client.list_case_studies()
except Exception as exc:
    st.error(f"Cannot load case studies: {exc}")
    st.stop()

labels = {s["id"]: f"{s['module']} — {s['name']}" for s in studies}
selected = st.selectbox("Select case study", options=list(labels.keys()), format_func=lambda k: labels[k])

if st.button("Run demo", type="primary"):
    with st.spinner("Running deterministic demo..."):
        try:
            result = client.run_case_study(selected)
            st.session_state["last_cs_result"] = result
        except Exception as exc:
            st.error(str(exc))
            st.stop()

if "last_cs_result" in st.session_state:
    result = st.session_state["last_cs_result"]
    st.success(f"Completed: {result.get('case_study_id', selected)}")

    if result.get("case_study_id") == "cs-07":
        st.metric("Root cause", result.get("root_cause", ""))
        st.metric("Confidence", result.get("confidence", ""))
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**MTTR**")
            mttr = result.get("mttr", {})
            st.write(f"Before: {mttr.get('before_minutes', '?')} min")
            st.write(f"After: {mttr.get('after_minutes', '?')} min")
        with col2:
            st.markdown("**Attack chain**")
            for step in result.get("attack_chain", []):
                st.write(f"- {step}")
        with st.expander("Full incident report"):
            st.code(result.get("report", ""))

    elif result.get("case_study_id") == "cs-02":
        st.metric("PASS", result.get("pass_count", 0))
        st.metric("FAIL", result.get("fail_count", 0))
        for ctrl in result.get("controls", []):
            icon = "🔴" if ctrl["status"] == "FAIL" else "🟢"
            st.write(f"{icon} **{ctrl['control_id']}** — {ctrl['name']}: {ctrl['status']}")
            if ctrl.get("gap_summary"):
                st.caption(ctrl["gap_summary"])

    elif result.get("case_study_id") == "cs-03":
        decision = result.get("decision", {})
        st.metric("Decision", result.get("outcome") or decision.get("outcome", ""))
        st.write(decision.get("explanation", result.get("explanation", "")))
        with st.expander("Proof"):
            st.json(decision.get("proof") or result.get("proofs"))

    else:
        st.metric("Outcome", result.get("outcome", ""))
        if result.get("explanation"):
            st.write(result["explanation"])
        if result.get("conclusions"):
            for c in result["conclusions"]:
                st.write(f"- {c}")

    with st.expander("Raw JSON"):
        st.json(result)
