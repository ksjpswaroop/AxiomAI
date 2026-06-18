"""Knowledge Base — facts, rules, queries, and LLM extraction."""

from __future__ import annotations

import streamlit as st

from apps.console.api_client import ApiClient

st.header("Knowledge Base")
st.caption("Live reasoning engine — add facts, rules, query with proof")

client = ApiClient()

tab_kb, tab_extract = st.tabs(["Query engine", "LLM extract"])

with tab_kb:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Facts")
        fact_input = st.text_input("Add fact", placeholder="Human(Socrates)")
        if st.button("Add fact", key="add_fact"):
            try:
                client.add_fact(fact_input)
                st.success(f"Added {fact_input}")
            except Exception as exc:
                st.error(str(exc))
        try:
            facts = client.list_facts()
            for f in facts:
                st.code(str(f.get("predicate", f)))
        except Exception as exc:
            st.warning(str(exc))

    with col2:
        st.subheader("Rules")
        rule_input = st.text_input("Add rule", placeholder="IF Human(x) THEN Mortal(x)")
        if st.button("Add rule", key="add_rule"):
            try:
                client.add_rule(rule_input)
                st.success("Rule added")
            except Exception as exc:
                st.error(str(exc))
        try:
            rules = client.list_rules()
            for r in rules:
                st.code(str(r.get("rule_str", r)))
        except Exception as exc:
            st.warning(str(exc))

    st.divider()
    query = st.text_input("Query", value="Mortal(Socrates)")
    mode = st.selectbox("Mode", ["auto", "backward", "forward", "resolution"])
    if st.button("Run query", type="primary"):
        try:
            result = client.query(query, mode=mode)
            st.metric("Result", result["result"])
            st.caption(f"{result['reasoning_mode']} · {result['duration_ms']:.1f} ms")
            st.write(result["explain"]["short"])
            with st.expander("Proof"):
                st.json(result["proof_json"])
        except Exception as exc:
            st.error(str(exc))

    c1, c2 = st.columns(2)
    if c1.button("Load Socrates"):
        import httpx
        httpx.post(f"{client.base_url}/load/socrates", timeout=30.0)
        st.success("Loaded")
    if c2.button("Reset KB"):
        client.reset()
        st.info("Cleared")

with tab_extract:
    text = st.text_area("Natural language", "Socrates is a human. All humans are mortal.")
    load = st.checkbox("Load into KB", value=True)
    if st.button("Extract facts & rules"):
        try:
            result = client.extract(text, load=load)
            st.write(f"Facts: {result.get('facts', [])}")
            st.write(f"Rules: {result.get('rules', [])}")
            st.json(result.get("stats", {}))
        except Exception as exc:
            st.error(str(exc))
