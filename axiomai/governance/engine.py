"""Governance engine — validate agent actions against policy rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from axiomai.governance.policy import PolicyPack
from axiomai.reasoner.engine import Reasoner


@dataclass
class Decision:
    """Outcome of a governance validation check."""

    outcome: str  # ALLOW | DENY | ESCALATE
    explanation: str = ""
    violated_rules: list[str] = field(default_factory=list)
    proof: dict[str, Any] | None = None
    proofs: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome,
            "explanation": self.explanation,
            "violated_rules": self.violated_rules,
            "proof": self.proof,
            "proofs": self.proofs,
        }


class GovernanceEngine:
    """Validate proposed agent actions using deterministic policy reasoning."""

    def __init__(self, policy: PolicyPack, reasoner: Reasoner | None = None):
        self.policy = policy
        self._reasoner = reasoner

    def validate(
        self,
        action: dict[str, Any],
        context: list[str] | None = None,
    ) -> Decision:
        entity = str(action.get("entity", action.get("id", "entity")))
        facts = list(context or [])
        if action.get("type"):
            facts.append(f"ActionType({entity}, {action['type']})")
        if action.get("amount") is not None:
            facts.append(f"ActionAmount({entity}, {action['amount']})")

        reasoner = self._reasoner or Reasoner(namespace="default")
        reasoner.kb.clear()
        for rule in self.policy.rules:
            reasoner.add_rule(rule)
        reasoner.add_facts(*facts)

        deny_hits = self._check_queries(reasoner, self.policy.deny_queries, entity)
        if deny_hits:
            return self._build_decision(
                outcome="DENY",
                hits=deny_hits,
                entity=entity,
            )

        escalate_hits = self._check_queries(reasoner, self.policy.escalate_queries, entity)
        if escalate_hits:
            return self._build_decision(
                outcome="ESCALATE",
                hits=escalate_hits,
                entity=entity,
            )

        if self.policy.allow_query:
            allow_hits = self._check_queries(reasoner, [self.policy.allow_query], entity)
            if allow_hits:
                return self._build_decision(
                    outcome="ALLOW",
                    hits=allow_hits,
                    entity=entity,
                )

        return Decision(
            outcome="DENY",
            explanation="No allow rule matched policy requirements.",
            violated_rules=[],
            proof=None,
        )

    def _check_queries(
        self,
        reasoner: Reasoner,
        templates: list[str],
        entity: str,
    ) -> list[tuple[str, dict]]:
        hits: list[tuple[str, dict]] = []
        for template in templates:
            query = self.policy.format_query(template, entity)
            result = reasoner.ask(query, mode="backward")
            if result.result == "PROVED":
                hits.append((query, result.proof.to_json()))
        return hits

    def _build_decision(
        self,
        outcome: str,
        hits: list[tuple[str, dict]],
        entity: str,
    ) -> Decision:
        proofs = [proof for _, proof in hits]
        violated = [query for query, _ in hits if outcome == "DENY"]
        explanation = self._explain(outcome, hits, entity)
        return Decision(
            outcome=outcome,
            explanation=explanation,
            violated_rules=violated,
            proof=proofs[0] if proofs else None,
            proofs=proofs,
        )

    @staticmethod
    def _explain(outcome: str, hits: list[tuple[str, dict]], entity: str) -> str:
        if outcome == "ALLOW":
            return f"Action for {entity} satisfies all policy requirements."
        if outcome == "ESCALATE":
            queries = ", ".join(q for q, _ in hits)
            return f"Action for {entity} requires human approval ({queries})."
        reasons: list[str] = []
        for query, _ in hits:
            if "PolicyViolation_Window" in query:
                reasons.append("Purchase outside 30-day refund window.")
            elif "PolicyViolation_Return" in query:
                reasons.append("Product not yet returned.")
            elif "RefundDenied" in query:
                reasons.append("Order was already refunded.")
            else:
                reasons.append(f"Policy violation: {query}")
        return " ".join(reasons) if reasons else f"Action for {entity} denied by policy."
