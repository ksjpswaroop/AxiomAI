"""CS-03 AI customer support governance case study."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from axiomai.governance import (
    AuditLog,
    Decision,
    EscalationRouter,
    GovernanceEngine,
    PolicyPack,
)


@dataclass
class ScenarioResult:
    scenario_id: str
    description: str
    action: dict[str, Any]
    decision: Decision
    audit_entry: dict[str, Any]


SCENARIOS: dict[str, dict[str, Any]] = {
    "deny_outside_window": {
        "description": "Refund outside 30-day window",
        "action": {"type": "refund", "entity": "order1", "amount": 350},
        "context": [
            "OutsideRefundWindow(order1)",
            "UnderLimit(order1)",
            "ProductReturned(order1)",
            "NotAlreadyRefunded(order1)",
            "NotFinalSale(order1)",
        ],
        "expected": "DENY",
    },
    "deny_not_returned": {
        "description": "Product not returned",
        "action": {"type": "refund", "entity": "order4", "amount": 120},
        "context": [
            "WithinRefundWindow(order4)",
            "UnderLimit(order4)",
            "NotProductReturned(order4)",
            "NotAlreadyRefunded(order4)",
            "NotFinalSale(order4)",
        ],
        "expected": "DENY",
    },
    "allow_compliant": {
        "description": "Compliant refund within policy",
        "action": {"type": "refund", "entity": "order2", "amount": 200},
        "context": [
            "WithinRefundWindow(order2)",
            "UnderLimit(order2)",
            "ProductReturned(order2)",
            "NotAlreadyRefunded(order2)",
            "NotFinalSale(order2)",
        ],
        "expected": "ALLOW",
    },
    "escalate_mid_amount": {
        "description": "Mid-range amount needs manager approval",
        "action": {"type": "refund", "entity": "order3", "amount": 750},
        "context": [
            "WithinRefundWindow(order3)",
            "AmountMidRange(order3)",
            "ProductReturned(order3)",
            "NotAlreadyRefunded(order3)",
            "NotFinalSale(order3)",
        ],
        "expected": "ESCALATE",
    },
    "deny_already_refunded": {
        "description": "Duplicate refund blocked",
        "action": {"type": "refund", "entity": "order5", "amount": 99},
        "context": [
            "WithinRefundWindow(order5)",
            "UnderLimit(order5)",
            "ProductReturned(order5)",
            "AlreadyRefunded(order5)",
            "NotFinalSale(order5)",
        ],
        "expected": "DENY",
    },
}


class SupportGovernanceDemo:
    """Simulate LLM support agent actions governed by refund policy."""

    def __init__(self, policy_path: str | Path) -> None:
        self.engine = GovernanceEngine(PolicyPack.load(policy_path))
        self.audit = AuditLog()
        self.router = EscalationRouter(
            routes={"DENY": "agent-feedback", "ESCALATE": "manager-queue"}
        )

    def run_scenario(self, scenario_id: str) -> ScenarioResult:
        scenario = SCENARIOS[scenario_id]
        decision = self.engine.validate(
            action=scenario["action"],
            context=scenario["context"],
        )
        entry = self.audit.record(decision, action=scenario["action"])
        return ScenarioResult(
            scenario_id=scenario_id,
            description=scenario["description"],
            action=scenario["action"],
            decision=decision,
            audit_entry=entry,
        )

    def run_all_scenarios(self) -> list[ScenarioResult]:
        return [self.run_scenario(sid) for sid in SCENARIOS]

    def simulate_llm_refund_request(
        self,
        customer: str,
        amount: float,
        days_since_purchase: int,
        product_returned: bool,
        already_refunded: bool = False,
    ) -> ScenarioResult:
        context: list[str] = []
        if days_since_purchase <= 30:
            context.append(f"WithinRefundWindow({customer})")
        else:
            context.append(f"OutsideRefundWindow({customer})")
        if amount < 500:
            context.append(f"UnderLimit({customer})")
        elif amount < 2000:
            context.append(f"AmountMidRange({customer})")
        else:
            context.append(f"OverLimit({customer})")
        context.append(
            f"ProductReturned({customer})" if product_returned else f"NotProductReturned({customer})"
        )
        context.append(
            f"AlreadyRefunded({customer})" if already_refunded else f"NotAlreadyRefunded({customer})"
        )
        context.append(f"NotFinalSale({customer})")

        action = {"type": "refund", "entity": customer, "amount": amount, "agent": "llm-support"}
        decision = self.engine.validate(action=action, context=context)
        entry = self.audit.record(decision, action=action)
        return ScenarioResult(
            scenario_id="llm_simulation",
            description="LLM-suggested refund",
            action=action,
            decision=decision,
            audit_entry=entry,
        )
