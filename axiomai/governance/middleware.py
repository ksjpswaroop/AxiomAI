"""Agent governance middleware — intercept actions before execution."""

from __future__ import annotations

from typing import Any, Callable

from axiomai.governance.audit import AuditLog
from axiomai.governance.engine import Decision, GovernanceEngine
from axiomai.governance.escalation import EscalationRouter
from axiomai.governance.registry import PolicyRegistry
from axiomai.reasoner.engine import Reasoner


class AgentGovernanceMiddleware:
    """
    Pre-action governance hook for AI agents.

    Validates proposed actions against a policy pack, records audit entries,
    and routes DENY/ESCALATE outcomes to configured queues.
    """

    def __init__(
        self,
        registry: PolicyRegistry | None = None,
        router: EscalationRouter | None = None,
        audit: AuditLog | None = None,
        reasoner: Reasoner | None = None,
    ):
        self.registry = registry or PolicyRegistry.default()
        self.router = router or EscalationRouter(
            routes={"DENY": "agent-feedback", "ESCALATE": "manager-queue"}
        )
        self.audit = audit or AuditLog()
        self._reasoner = reasoner

    def validate_action(
        self,
        action: dict[str, Any],
        context: list[str] | None = None,
        *,
        policy_id: str = "refund-policy",
        nl_context: str | None = None,
    ) -> Decision:
        """Validate an action; optionally extract facts from natural language."""
        facts = list(context or [])
        if nl_context:
            reasoner = self._reasoner or Reasoner(namespace="governance")
            extracted = reasoner.extract(nl_context)
            for fact in extracted["facts"]:
                facts.append(str(fact.predicate))

        engine = GovernanceEngine(self.registry.get(policy_id), self._reasoner)
        return engine.validate(action, facts)

    def intercept(
        self,
        action: dict[str, Any],
        context: list[str] | None = None,
        *,
        policy_id: str = "refund-policy",
        nl_context: str | None = None,
        callback: Callable[[], Any] | None = None,
    ) -> dict[str, Any]:
        """
        Validate action, audit, route escalation, and optionally execute callback.

        Callback runs only when outcome is ALLOW.
        """
        decision = self.validate_action(
            action, context, policy_id=policy_id, nl_context=nl_context
        )
        audit_entry = self.audit.record(decision, action=action)
        queue = self.router.route(decision)
        payload: dict[str, Any] = {
            "decision": decision.to_dict(),
            "escalation_queue": queue,
            "audit_id": audit_entry["id"],
            "policy_id": policy_id,
        }
        if decision.outcome == "ALLOW" and callback is not None:
            payload["result"] = callback()
        return payload
