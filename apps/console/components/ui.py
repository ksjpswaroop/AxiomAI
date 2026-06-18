"""Shared Streamlit UI components for investor demo."""

from __future__ import annotations

from typing import Any

import streamlit as st

TIER_LABELS = {"1": "Flagship", "2": "Enterprise", "3": "Vertical", "4": "Operations", "5": "Agentic AI"}
OUTCOME_COLORS = {
    "ALLOW": "green", "PROVED": "green", "AUDIT_COMPLETE": "blue", "CONFIRMED": "green",
    "ROOT_CAUSE_FOUND": "green", "DIAGNOSIS_FOUND": "green", "ROUTED": "blue",
    "OBLIGATION_TRIGGERED": "orange",
    "DENY": "red", "BLOCKED": "red", "DISPROVED": "red",
    "ESCALATE": "orange", "PROBABLE": "orange", "UNKNOWN": "gray",
}


def render_outcome_badge(outcome: str) -> None:
    color = OUTCOME_COLORS.get(outcome, "gray")
    st.markdown(f":{color}[**{outcome}**]")


def render_case_card(case: dict[str, Any], key: str) -> bool:
    tier = TIER_LABELS.get(str(case.get("tier", "")), f"Tier {case.get('tier', '')}")
    with st.container(border=True):
        st.caption(f"{case.get('module', '')} · {tier}")
        st.subheader(case.get("name", case.get("id", "")))
        st.write(case.get("description", ""))
        scenarios = case.get("scenarios", [])
        if scenarios:
            st.caption(f"{len(scenarios)} scenario(s)")
        return st.button("Open demo", key=f"open_{key}", use_container_width=True)


def render_data_sources(sources: list[dict[str, Any]]) -> None:
    if not sources:
        return
    with st.expander("Data sources (open reference)"):
        for src in sources:
            name = src.get("name", "Source")
            url = src.get("url", "")
            license_ = src.get("license", "")
            note = src.get("note", "")
            if url:
                st.markdown(f"- [{name}]({url}) — {license_}")
            else:
                st.markdown(f"- **{name}** — {license_}")
            if note:
                st.caption(note)


def render_result_panel(result: dict[str, Any]) -> None:
    case_id = result.get("case_study_id", "")
    outcome = result.get("outcome", "UNKNOWN")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Outcome", outcome)
    with col2:
        st.metric("Case study", case_id.upper())
    with col3:
        st.metric("Scenario", result.get("scenario_id", "default"))

    if result.get("story"):
        st.info(result["story"])
    if result.get("explanation"):
        st.write(result["explanation"])

    if case_id == "cs-07":
        st.metric("Root cause", result.get("root_cause", ""))
        mttr = result.get("mttr", {})
        st.write(f"MTTR: {mttr.get('before_minutes', '?')} min → {mttr.get('after_minutes', '?')} min")
        for step in result.get("attack_chain", []):
            st.write(f"- {step}")
        if result.get("report"):
            with st.expander("Incident report"):
                st.code(result["report"])

    elif case_id == "cs-02":
        c1, c2 = st.columns(2)
        c1.metric("PASS", result.get("pass_count", 0))
        c2.metric("FAIL", result.get("fail_count", 0))
        for ctrl in result.get("controls", []):
            icon = "🔴" if ctrl.get("status") == "FAIL" else "🟢"
            st.write(f"{icon} **{ctrl.get('control_id')}** — {ctrl.get('name')}: {ctrl.get('status')}")

    elif case_id == "cs-03":
        decision = result.get("decision", {})
        st.write(decision.get("explanation", ""))
        if result.get("scenario_description"):
            st.caption(result["scenario_description"])

    else:
        if result.get("conclusions"):
            st.markdown("**Conclusions**")
            for c in result["conclusions"]:
                st.write(f"- {c}")
        if result.get("metadata", {}).get("facts_input"):
            with st.expander("Input facts"):
                for f in result["metadata"]["facts_input"]:
                    st.code(f)
        if result.get("metadata", {}).get("escalation_queue"):
            st.warning(f"Escalation queue: {result['metadata']['escalation_queue']}")

    proofs = result.get("proofs") or []
    if proofs:
        with st.expander("Proof trace"):
            st.json(proofs[0] if len(proofs) == 1 else proofs)

    render_data_sources(result.get("data_sources", []))

    with st.expander("Raw JSON"):
        st.json(result)
