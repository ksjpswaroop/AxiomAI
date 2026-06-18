"""CS-05 AI code review guardrail."""

from __future__ import annotations

from apps.case_studies._base.simple_engine import CaseStudyResult, SimpleRuleEngine

RULES = [
    "IF SecretInCode(pr) THEN BlockDeploy_Secret(pr)",
    "IF RouteWithoutAuth(pr) THEN BlockDeploy_Auth(pr)",
    "IF FrontendSqlDirect(pr) THEN FlagViolation_Sql(pr)",
    "IF NewDependency(pr, d) AND NotApprovedDependency(d) THEN SecurityReviewRequired(pr)",
    "IF BlockDeploy_Secret(pr) THEN DeployBlocked(pr)",
    "IF BlockDeploy_Auth(pr) THEN DeployBlocked(pr)",
]

DEFAULT_FACTS = [
    "SecretInCode(pr42)",
    "RouteWithoutAuth(pr42)",
    "NewDependency(pr42, lodash-pro)",
    "NotApprovedDependency(lodash-pro)",
]


def run(entity: str = "pr42") -> CaseStudyResult:
    facts = [f.replace("pr42", entity) for f in DEFAULT_FACTS]
    result = SimpleRuleEngine().analyze(
        RULES,
        facts,
        entity=entity,
        deny_queries=["DeployBlocked({entity})"],
        escalate_queries=["SecurityReviewRequired({entity})", "FlagViolation_Sql({entity})"],
    )
    if result.outcome in ("DENY", "ESCALATE"):
        result.outcome = "BLOCKED"
    return result
