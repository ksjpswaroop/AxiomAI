"""P2-10: Property-based unification tests."""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from axiomai.reasoner.core.models import Predicate
from axiomai.reasoner.core.unification import UnificationEngine


@given(st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=8))
def test_unify_same_predicate_no_crash(name):
    uni = UnificationEngine()
    p = Predicate.parse(f"Rel({name})")
    result = uni.unify(p, p)
    assert result.success


@given(
    st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=6),
    st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=6),
)
def test_unify_var_const_no_crash(var_name, const_name):
    if var_name in ("true", "false", "null", "none"):
        return
    uni = UnificationEngine()
    p1 = Predicate.parse(f"Rel({var_name})")
    p2 = Predicate.parse(f"Rel({const_name})")
    result = uni.unify(p1, p2)
    assert isinstance(result.success, bool)
