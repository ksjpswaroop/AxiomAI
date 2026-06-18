"""P2-06: Planning engine tests."""

from __future__ import annotations


def test_blocks_world_plan(reasoner):
    reasoner.add_action("pickup", ["clear(A)", "on(A,B)"], ["holding(A)"], ["clear(A)", "on(A,B)"])
    reasoner.add_action("putdown", ["holding(A)"], ["on(A,B)", "clear(A)"], ["holding(A)"])
    plan = reasoner.plan(
        initial_state={"on(A,B)", "clear(A)"},
        goal={"on(A,B)"},
        max_depth=5,
    )
    assert plan.found


def test_plan_already_at_goal(reasoner):
    plan = reasoner.plan(
        initial_state={"on(A,B)", "clear(A)"},
        goal={"on(A,B)"},
    )
    assert plan.found
    assert len(plan.actions) == 0


def test_plan_unreachable(reasoner):
    reasoner.add_action("move", ["at(A)"], ["at(B)"], ["at(A)"])
    plan = reasoner.plan(
        initial_state={"at(A)"},
        goal={"at(C)"},
        max_depth=3,
    )
    assert not plan.found


def test_plan_finds_sequence(reasoner):
    reasoner.add_action("a_to_b", ["at(A)"], ["at(B)"], ["at(A)"])
    reasoner.add_action("b_to_c", ["at(B)"], ["at(C)"], ["at(B)"])
    plan = reasoner.plan(
        initial_state={"at(A)"},
        goal={"at(C)"},
        max_depth=5,
    )
    assert plan.found
    assert len(plan.actions) == 2
