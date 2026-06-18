"""P1-05–P1-06: Parser and model extension tests."""

from __future__ import annotations

import pytest

from axiomai.reasoner.core.models import Predicate, Rule
from axiomai.reasoner.core.parser import Parser, ParserError


def test_parse_or_rule_antecedents():
    rule = Rule.parse("IF Human(x) OR Rational(x) THEN Person(x)")
    assert rule.antecedent_operator == "or"
    assert len(rule.antecedents) == 2


def test_parse_namespace_predicate():
    pred = Predicate.parse("medical:Diagnosis(x)")
    assert pred.namespace == "medical"
    assert pred.relation == "Diagnosis"


def test_parser_parse_rule_with_or():
    parser = Parser()
    rule = parser.parse_rule("IF A(x) OR B(x) THEN C(x)")
    assert rule.antecedent_operator == "or"


def test_invalid_predicate_raises():
    with pytest.raises((ValueError, ParserError)):
        Predicate.parse("not valid")
