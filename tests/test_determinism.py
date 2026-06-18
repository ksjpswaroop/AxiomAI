"""P2-08: Determinism tests."""

from __future__ import annotations


def test_fingerprint_stable(socrates_kb):
    fp1 = socrates_kb.fingerprint()
    fp2 = socrates_kb.fingerprint()
    assert fp1 == fp2


def test_ask_deterministic_100_runs(socrates_kb):
    results = []
    hashes = []
    for _ in range(100):
        result = socrates_kb.ask("Mortal(Socrates)")
        results.append(result.result)
        hashes.append(socrates_kb.last_run_hash())
    assert len(set(results)) == 1
    assert results[0] == "PROVED"
    assert len(set(hashes)) == 1


def test_fingerprint_changes_on_kb_mutation(reasoner):
    fp1 = reasoner.fingerprint()
    reasoner.add_fact("Human(Socrates)")
    fp2 = reasoner.fingerprint()
    assert fp1 != fp2
