"""Human-in-the-loop escalation routing."""

from __future__ import annotations

from axiomai.governance.engine import Decision


class EscalationRouter:
    """Route DENY and ESCALATE decisions to configured queues."""

    def __init__(self, routes: dict[str, str] | None = None):
        self.routes = dict(routes or {})

    def route(self, decision: Decision) -> str | None:
        return self.routes.get(decision.outcome)
