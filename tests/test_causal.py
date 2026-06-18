"""P2-07: Causal engine tests."""

from __future__ import annotations


def test_root_causes(reasoner):
    reasoner.add_causal("phishing", "execution")
    reasoner.add_causal("execution", "lateral_movement")
    reasoner.add_causal("lateral_movement", "ransomware")
    roots = reasoner.causal_engine.root_causes("ransomware")
    assert "phishing" in roots


def test_explain_chain(reasoner):
    reasoner.add_causal("A", "B")
    reasoner.add_causal("B", "C")
    chain = reasoner.causal_engine.explain_chain("C")
    assert "A" in chain
    assert "B" in chain


def test_trace_path(reasoner):
    reasoner.add_causal("A", "B")
    reasoner.add_causal("B", "C")
    path = reasoner.causal_engine.trace_path("A", "C")
    assert path == ["A", "B", "C"]


def test_no_path_returns_none(reasoner):
    reasoner.add_causal("A", "B")
    path = reasoner.causal_engine.trace_path("A", "C")
    assert path is None


def test_topological_order(reasoner):
    reasoner.add_causal("A", "B")
    reasoner.add_causal("B", "C")
    order = reasoner.causal_engine.topological_order()
    assert order.index("A") < order.index("B") < order.index("C")
