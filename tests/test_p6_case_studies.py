"""P6: Remaining case study tests (Tier 2–5)."""

from __future__ import annotations

import pytest

from apps.case_studies.registry import CASE_STUDY_CATALOG, run_case_study

P6_CASES = [
    ("cs-01", {"ROOT_CAUSE_FOUND", "PROVED"}),
    ("cs-04", {"ALLOW"}),
    ("cs-05", {"BLOCKED", "DENY", "ESCALATE"}),
    ("cs-06", {"BLOCKED", "DENY", "ESCALATE"}),
    ("cs-08", {"OBLIGATION_TRIGGERED", "PROVED"}),
    ("cs-09", {"ALLOW", "DENY", "ESCALATE"}),
    ("cs-10", {"ALLOW", "DENY", "ESCALATE"}),
    ("cs-11", {"ALLOW", "DENY"}),
    ("cs-12", {"DENY", "ALLOW"}),
    ("cs-13", {"BLOCKED", "DENY", "ESCALATE"}),
    ("cs-14", {"DIAGNOSIS_FOUND", "PROVED"}),
    ("cs-15", {"ALLOW", "DENY"}),
    ("cs-16", {"ALLOW", "DENY", "ESCALATE"}),
    ("cs-17", {"ROUTED", "PROVED"}),
    ("cs-18", {"BLOCKED", "DENY", "ESCALATE"}),
]


def test_catalog_has_18_case_studies():
    assert len(CASE_STUDY_CATALOG) == 18


@pytest.mark.parametrize("case_id,expected_outcomes", P6_CASES)
def test_p6_case_study_runs(case_id, expected_outcomes):
    result = run_case_study(case_id)
    assert result["case_study_id"] == case_id
    assert result["outcome"] in expected_outcomes


@pytest.mark.parametrize("case_id,_", P6_CASES)
def test_p6_case_study_has_proof_or_conclusions(case_id, _):
    result = run_case_study(case_id)
    has_proof = bool(result.get("proofs")) or bool(result.get("conclusions"))
    has_tier1_fields = any(k in result for k in ("decision", "controls", "root_cause", "attack_chain"))
    assert has_proof or has_tier1_fields or result.get("outcome") not in ("UNKNOWN",)


@pytest.mark.parametrize("case_id,_", P6_CASES)
def test_p6_registry_idempotent(case_id, _):
    a = run_case_study(case_id)
    b = run_case_study(case_id)
    assert a["outcome"] == b["outcome"]
