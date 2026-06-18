"""Unified case study runner — executes any rule-based case from JSON definitions."""

from __future__ import annotations

from typing import Any

from axiomai.governance import AgentGovernanceMiddleware

from apps.case_studies._base.scenario_loader import load_definition, load_scenario
from apps.case_studies._base.simple_engine import CaseStudyResult, SimpleRuleEngine


def run_rule_case(case_id: str, scenario_id: str = "default") -> CaseStudyResult:
    """Run a SimpleRuleEngine case study from JSON definition."""
    scenario = load_scenario(case_id, scenario_id)
    entity = scenario["entity"]
    facts = [f.replace("{entity}", entity) for f in scenario.get("facts", [])]

    result = SimpleRuleEngine().analyze(
        scenario["rules"],
        facts,
        entity=entity,
        deny_queries=scenario.get("deny_queries"),
        allow_queries=scenario.get("allow_queries"),
        escalate_queries=scenario.get("escalate_queries"),
        goal_queries=scenario.get("goal_queries"),
    )

    outcome_map = scenario.get("outcome_map", {})
    if result.outcome in outcome_map:
        result.outcome = outcome_map[result.outcome]

    if scenario.get("expected_outcome"):
        result.metadata["expected_outcome"] = scenario["expected_outcome"]
    if scenario.get("explanation"):
        result.explanation = scenario["explanation"]
    elif scenario.get("story"):
        result.explanation = scenario["story"]

    result.metadata.update(
        {
            "case_id": case_id,
            "scenario_id": scenario_id,
            "story": scenario.get("story", ""),
            "problem": scenario.get("problem", ""),
            "data_sources": scenario.get("data_sources", []),
            "facts_input": facts,
            "rules_count": len(scenario.get("rules", [])),
        }
    )
    return result


def run_governance_case(
    case_id: str,
    scenario_id: str = "default",
    policy_id: str | None = None,
) -> CaseStudyResult:
    """Run a governance-backed case study (CS-06, CS-12, CS-13)."""
    scenario = load_scenario(case_id, scenario_id)
    definition = load_definition(case_id)
    policy = policy_id or definition.get("policy_id", "refund-policy")
    entity = scenario["entity"]
    context = [f.replace("{entity}", entity) for f in scenario.get("facts", [])]
    action = dict(scenario.get("action", {"type": definition.get("action_type", "action"), "entity": entity}))
    for k, v in action.items():
        if isinstance(v, str):
            action[k] = v.replace("{entity}", entity)

    middleware = AgentGovernanceMiddleware()
    payload = middleware.intercept(action=action, context=context, policy_id=policy)
    decision = payload["decision"]

    return CaseStudyResult(
        outcome=decision["outcome"],
        explanation=decision.get("explanation", scenario.get("explanation", "")),
        conclusions=decision.get("violated_rules", []),
        proofs=decision.get("proofs") or ([decision["proof"]] if decision.get("proof") else []),
        metadata={
            "case_id": case_id,
            "scenario_id": scenario_id,
            "policy_id": policy,
            "escalation_queue": payload.get("escalation_queue"),
            "audit_id": payload.get("audit_id"),
            "story": scenario.get("story", ""),
            "data_sources": scenario.get("data_sources", []),
            "action": action,
            "context": context,
            "expected_outcome": scenario.get("expected_outcome"),
        },
    )


def run_case(case_id: str, scenario_id: str = "default") -> dict[str, Any]:
    """Dispatch to the correct runner for a case study."""
    definition = load_definition(case_id)
    runner_type = definition.get("runner", "rules")

    if runner_type == "governance":
        result = run_governance_case(case_id, scenario_id)
    else:
        result = run_rule_case(case_id, scenario_id)

    payload = result.to_dict()
    payload["case_study_id"] = case_id
    payload["scenario_id"] = scenario_id
    return payload
