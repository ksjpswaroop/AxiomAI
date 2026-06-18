"""Reusable forward/backward rule engine for case study demos."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from axiomai import Reasoner


@dataclass
class CaseStudyResult:
    """Standard result payload for case study analysis."""

    outcome: str
    explanation: str = ""
    conclusions: list[str] = field(default_factory=list)
    derived_facts: list[str] = field(default_factory=list)
    proofs: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome,
            "explanation": self.explanation,
            "conclusions": self.conclusions,
            "derived_facts": self.derived_facts,
            "proofs": self.proofs,
            "metadata": self.metadata,
        }


class SimpleRuleEngine:
    """Run domain rules and evaluate success/failure query templates."""

    def analyze(
        self,
        rules: list[str],
        facts: list[str],
        *,
        entity: str = "entity1",
        deny_queries: list[str] | None = None,
        allow_queries: list[str] | None = None,
        escalate_queries: list[str] | None = None,
        goal_queries: list[str] | None = None,
    ) -> CaseStudyResult:
        reasoner = Reasoner(namespace="default")
        reasoner.kb.clear()
        for rule in rules:
            reasoner.add_rule(rule)
        reasoner.add_facts(*facts)

        forward = reasoner.forward_engine.run()
        derived = [str(f.predicate) for f in forward.all_derived]

        def check_queries(templates: list[str]) -> list[tuple[str, dict]]:
            hits: list[tuple[str, dict]] = []
            for template in templates:
                query = template.format(entity=entity)
                if query in derived:
                    hits.append((query, {"query": query, "result": "PROVED", "mode": "forward"}))
                    continue
                result = reasoner.ask(query, mode="backward")
                if result.result == "PROVED":
                    hits.append((query, result.proof.to_json()))
            return hits

        deny_hits = check_queries(deny_queries or [])
        if deny_hits:
            return CaseStudyResult(
                outcome="DENY",
                explanation=_join_queries(deny_hits),
                conclusions=[q for q, _ in deny_hits],
                derived_facts=derived,
                proofs=[p for _, p in deny_hits],
            )

        esc_hits = check_queries(escalate_queries or [])
        if esc_hits:
            return CaseStudyResult(
                outcome="ESCALATE",
                explanation=_join_queries(esc_hits),
                conclusions=[q for q, _ in esc_hits],
                derived_facts=derived,
                proofs=[p for _, p in esc_hits],
            )

        allow_hits = check_queries(allow_queries or [])
        if allow_hits:
            return CaseStudyResult(
                outcome="ALLOW",
                explanation="Policy requirements satisfied.",
                conclusions=[q for q, _ in allow_hits],
                derived_facts=derived,
                proofs=[p for _, p in allow_hits],
            )

        goal_hits = check_queries(goal_queries or [])
        if goal_hits:
            return CaseStudyResult(
                outcome="PROVED",
                explanation="Goal derived from evidence and rules.",
                conclusions=[q for q, _ in goal_hits],
                derived_facts=derived,
                proofs=[p for _, p in goal_hits],
            )

        return CaseStudyResult(
            outcome="UNKNOWN",
            explanation="No matching conclusion from rules.",
            derived_facts=derived,
        )


def _join_queries(hits: list[tuple[str, dict]]) -> str:
    return "; ".join(q for q, _ in hits)
