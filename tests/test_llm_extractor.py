"""LLM extractor and client tests."""

from __future__ import annotations

from axiomai.reasoner.integrations.llm_client import MockLLMClient
from axiomai.reasoner.integrations.llm_extractor import LLMExtractor


def test_fallback_extract_facts_and_rules():
    extractor = LLMExtractor()
    result = extractor.extract("Socrates is a human. All humans are mortal.")
    assert len(result["facts"]) >= 1
    assert len(result["rules"]) >= 1
    assert str(result["facts"][0].predicate).startswith("Human")


def test_mock_llm_client_extraction():
    mock = MockLLMClient(
        responses={
            "Socrates": {
                "facts": [{"predicate": "Human(Socrates)", "source": "llm"}],
                "rules": [],
            },
            "mortal": {
                "facts": [],
                "rules": [{"rule": "IF Human(x) THEN Mortal(x)", "priority": 1}],
            },
        }
    )
    extractor = LLMExtractor(mock)
    facts = extractor.extract_facts("Socrates is mentioned here")
    assert len(facts) == 1
    assert str(facts[0].predicate) == "Human(Socrates)"

    rules = extractor.extract_rules("All about mortal things")
    assert len(rules) == 1
    assert "Mortal" in str(rules[0])


def test_validate_extraction_rejects_empty_rule():
    extractor = LLMExtractor()
    from axiomai.reasoner.core.models import Rule

    bad = Rule(antecedents=[], consequent=None)
    assert extractor.validate_extraction(bad) is False


def test_reasoner_extract_with_mock_llm():
    from axiomai import Reasoner

    mock = MockLLMClient(
        responses={
            "Plato": {
                "facts": [{"predicate": "Human(Plato)", "source": "llm"}],
                "rules": [{"rule": "IF Human(x) THEN Mortal(x)", "priority": 1}],
            }
        }
    )
    r = Reasoner(llm_client=mock)
    result = r.extract("Plato is mentioned")
    assert len(result["facts"]) == 1
    assert r.kb.query_fact("Human(Plato)")


def test_reasoner_extract_without_load():
    from axiomai import Reasoner

    r = Reasoner()
    before = len(r.list_facts())
    r.extract("Socrates is a human.", load=False)
    assert len(r.list_facts()) == before


def test_llm_stats_tracked():
    extractor = LLMExtractor()
    extractor.extract("Socrates is a human.")
    stats = extractor.stats()
    assert stats["extractions"] >= 1
