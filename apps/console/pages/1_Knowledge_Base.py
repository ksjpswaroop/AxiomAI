"""Knowledge Base editor — facts, rules, and query console."""

from __future__ import annotations

import streamlit as st

from apps.console.api_client import ApiClient

st.header("Knowledge Base Editor")

client = ApiClient()

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
        st.json([f.get("predicate", f) for f in facts])
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
        st.json([r.get("rule_str", r) for r in rules])
    except Exception as exc:
        st.warning(str(exc))

st.divider()
st.subheader("Query Console")

query = st.text_input("Query", value="Mortal(Socrates)")
mode = st.selectbox("Mode", ["auto", "backward", "forward", "resolution"])

if st.button("Run query"):
    try:
        result = client.query(query, mode=mode)
        st.metric("Result", result["result"])
        st.caption(f"Mode: {result['reasoning_mode']} · {result['duration_ms']:.1f} ms")
        st.markdown("**Explanation**")
        st.write(result["explain"]["short"])
        with st.expander("Proof tree (JSON)"):
            st.json(result["proof_json"])
    except Exception as exc:
        st.error(str(exc))

if st.button("Load Socrates example"):
    import httpx

    base = client.base_url
    httpx.post(f"{base}/load/socrates", timeout=30.0)
    st.success("Socrates example loaded")

if st.button("Reset KB", type="secondary"):
    client.reset()
    st.info("Knowledge base cleared")
