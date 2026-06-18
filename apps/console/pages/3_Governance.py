"""Governance simulator — validate agent actions with proof."""

from __future__ import annotations

import streamlit as st

from apps.console.api_client import ApiClient

st.header("Governance Simulator")

client = ApiClient()

st.caption("Simulate an LLM support agent proposing a refund — policy check returns ALLOW/DENY/ESCALATE.")

entity = st.text_input("Order entity", value="order1")
amount = st.number_input("Refund amount ($)", min_value=0.0, value=350.0)
days = st.number_input("Days since purchase", min_value=0, value=43)
returned = st.checkbox("Product returned", value=False)
already_refunded = st.checkbox("Already refunded", value=False)

context: list[str] = []
if days <= 30:
    context.append(f"WithinRefundWindow({entity})")
else:
    context.append(f"OutsideRefundWindow({entity})")
if amount < 500:
    context.append(f"UnderLimit({entity})")
elif amount < 2000:
    context.append(f"AmountMidRange({entity})")
else:
    context.append(f"OverLimit({entity})")
context.append(f"ProductReturned({entity})" if returned else f"NotProductReturned({entity})")
context.append(f"AlreadyRefunded({entity})" if already_refunded else f"NotAlreadyRefunded({entity})")
context.append(f"NotFinalSale({entity})")

st.markdown("**Context facts**")
st.code("\n".join(context))

action = {"type": "refund", "entity": entity, "amount": amount, "agent": "streamlit-sim"}

if st.button("Validate action", type="primary"):
    try:
        result = client.validate_governance(action, context, case_study="cs-03")
        outcome = result.get("outcome", "UNKNOWN")
        if outcome == "ALLOW":
            st.success(f"Decision: {outcome}")
        elif outcome == "ESCALATE":
            st.warning(f"Decision: {outcome}")
        else:
            st.error(f"Decision: {outcome}")
        st.write(result.get("explanation", ""))
        if result.get("violated_rules"):
            st.markdown("**Violated rules**")
            for rule in result["violated_rules"]:
                st.write(f"- {rule}")
        with st.expander("Proof trace"):
            st.json(result.get("proof"))
    except Exception as exc:
        st.error(str(exc))
