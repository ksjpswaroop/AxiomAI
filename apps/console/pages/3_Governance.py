"""Governance simulator — validate agent actions with proof."""

from __future__ import annotations

import streamlit as st

from apps.console.api_client import ApiClient

st.header("Governance Simulator")

client = ApiClient()

try:
    policies = client.list_policies()
except Exception as exc:
    st.error(f"Cannot load policies: {exc}")
    st.stop()

policy_labels = {p["id"]: f"{p['name']} ({p['action_type']})" for p in policies}
policy_id = st.selectbox(
    "Policy pack",
    options=list(policy_labels.keys()),
    format_func=lambda k: policy_labels[k],
)

st.caption("Simulate an agent action — policy check returns ALLOW / DENY / ESCALATE with proof.")

entity = st.text_input("Entity ID", value="order1")
action_type = st.text_input("Action type", value="refund")
amount = st.number_input("Amount ($)", min_value=0.0, value=350.0)

if policy_id == "refund-policy":
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
elif policy_id == "procurement-policy":
    context = [
        f"PurchaseAmount({entity}, {int(amount)})",
        "OverThreshold1000(45000)" if amount >= 1000 else f"UnderThreshold1000({int(amount)})",
        "OverThreshold10000(45000)" if amount >= 10000 else f"UnderThreshold10000({int(amount)})",
        f"NewVendor({entity}, NewCloudProvider)",
        f"ContractTermMonths({entity}, 24)",
        "Over12Months(24)",
        f"GpuResource({entity})",
    ]
    action_type = "purchase"
else:
    context = st.text_area(
        "Context facts (one per line)",
        value=f"Entity({entity})",
    ).strip().splitlines()

st.markdown("**Context facts**")
st.code("\n".join(context))

nl_context = st.text_area(
    "Natural language context (optional — extracted via LLM)",
    value="",
    placeholder="Customer purchased 43 days ago, product not returned.",
)

action = {"type": action_type, "entity": entity, "amount": amount, "agent": "streamlit-sim"}

if st.button("Validate action", type="primary"):
    try:
        result = client.validate_governance(
            action,
            context,
            case_study="console",
            policy_id=policy_id,
            nl_context=nl_context or None,
        )
        outcome = result.get("outcome", "UNKNOWN")
        if outcome == "ALLOW":
            st.success(f"Decision: {outcome}")
        elif outcome == "ESCALATE":
            st.warning(f"Decision: {outcome}")
        else:
            st.error(f"Decision: {outcome}")
        st.write(result.get("explanation", ""))
        if result.get("escalation_queue"):
            st.info(f"Escalation queue: {result['escalation_queue']}")
        if result.get("violated_rules"):
            st.markdown("**Violated rules**")
            for rule in result["violated_rules"]:
                st.write(f"- {rule}")
        with st.expander("Proof trace"):
            st.json(result.get("proof"))
    except Exception as exc:
        st.error(str(exc))
