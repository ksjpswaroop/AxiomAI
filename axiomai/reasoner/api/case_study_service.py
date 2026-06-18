"""Case study API service — delegates to central registry."""

from __future__ import annotations

from apps.case_studies.registry import list_case_studies, list_scenarios, run_case_study

__all__ = ["list_case_studies", "list_scenarios", "run_case_study", "CASE_STUDY_CATALOG"]

CASE_STUDY_CATALOG = list_case_studies()
