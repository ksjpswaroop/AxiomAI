"""Case study registry — re-exports for API and console."""

from apps.case_studies.registry import CASE_STUDY_CATALOG, list_case_studies, run_case_study

__all__ = ["CASE_STUDY_CATALOG", "list_case_studies", "run_case_study"]
