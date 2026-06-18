"""Case study gallery — all 18 vertical demos."""

from __future__ import annotations

import streamlit as st

from apps.console.api_client import ApiClient
from apps.console.components.ui import TIER_LABELS, render_case_card, render_result_panel

st.header("Case Study Gallery")
st.caption("18 real-world vertical demos — synthetic data modeled on open standards")

client = ApiClient()

if "selected_case" not in st.session_state:
    st.session_state.selected_case = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None

try:
    studies = client.list_case_studies()
except Exception as exc:
    st.error(f"Cannot load case studies: {exc}")
    st.stop()

tier_filter = st.selectbox("Filter by tier", ["All"] + sorted({TIER_LABELS.get(str(s.get("tier")), f"T{s.get('tier')}") for s in studies}))

filtered = studies
if tier_filter != "All":
    filtered = [s for s in studies if TIER_LABELS.get(str(s.get("tier")), f"T{s.get('tier')}") == tier_filter]

cols = st.columns(3)
for i, case in enumerate(filtered):
    with cols[i % 3]:
        if render_case_card(case, case["id"]):
            st.session_state.selected_case = case["id"]

st.markdown("---")

selected = st.session_state.selected_case
if selected:
    case_meta = next((c for c in studies if c["id"] == selected), {})
    st.subheader(f"{case_meta.get('module', '')} — {case_meta.get('name', selected)}")

    try:
        scenarios = client.list_scenarios(selected)
    except Exception as exc:
        st.error(str(exc))
        scenarios = [{"id": "default", "label": "Default"}]

    scenario_labels = {s["id"]: s.get("label", s["id"]) for s in scenarios}
    scenario_id = st.radio(
        "Scenario",
        options=list(scenario_labels.keys()),
        format_func=lambda k: scenario_labels[k],
        horizontal=True,
    )

    if st.button("Run demo", type="primary"):
        with st.spinner("Running deterministic analysis..."):
            try:
                st.session_state.last_result = client.run_case_study(selected, scenario_id)
            except Exception as exc:
                st.error(str(exc))

if st.session_state.last_result:
    st.markdown("### Results")
    render_result_panel(st.session_state.last_result)
