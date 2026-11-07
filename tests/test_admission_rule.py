"""The adopted admission rule must be the only thing that changed.

The licence is `docs/DECISION-ADMISSION-RULE.md`. These tests hold it to four
promises: the ``COUNT`` arm returns exactly what the frozen engine returns (so
the reference behaviour is delegated to, not re-implemented), the ``DIVERSITY``
arm admits a different set where a source is crowded (so the manipulation
occurred), every adopted admission was already eligible under the engine's own
filter, and no engine file was edited.

``_build_predictions`` needs no database, so the engine is exercised through
``object.__new__``: building a substrate would test the substrate, not the rule.
"""

from __future__ import annotations

import subprocess
from collections import Counter
from pathlib import Path

import pytest

from organica import admission as A
from organica.sleep import PredictionCandidate, SleepService

ROOT = Path(__file__).resolve().parent.parent

#: The seven files the freeze record names, plus the engine modules this
#: decision promises not to touch either.
ENGINE = (
    "organica/sleep.py",
    "organica/memory.py",
    "organica/paths.py",
    "organica/streams.py",
    "organica/branch_streams.py",
    "organica/scale_streams.py",
    "organica/ground_truth_worlds.py",
    "organica/sleep_extraction.py",
    "organica/sleep_inquiry.py",
    "organica/sleep_synthesis.py",
    "organica/sleep_selection.py",
    "organica/candidates.py",
)

#: One source owns four high-count edges; five sources own one each. Every count
#: is at or above the engine's own ``PREDICTION_MIN_COUNT``, so nothing here is
#: filtered out before admission can see it.
CROWDED = {
    "aaaa": {"bbbb": 9, "cccc": 8, "dddd": 7, "eeee": 6,
             "pppp": 5, "qqqq": 5, "rrrr": 5, "ssss": 5},
    "ffff": {"gggg": 5},
    "hhhh": {"iiii": 5},
    "jjjj": {"kkkk": 5},
    "llll": {"mmmm": 5},
    "nnnn": {"oooo": 5},
}
FREQS = {tag: 20 for tag in (
    "aaaa", "bbbb", "cccc", "dddd", "eeee", "pppp", "qqqq", "rrrr", "ssss",
    "ffff", "gggg", "hhhh", "iiii", "jjjj", "kkkk", "llll", "mmmm", "nnnn",
    "oooo")}


def _service(cls, policy=None, cap=40):
    svc = object.__new__(cls)
    svc.PREDICTION_MIN_COUNT = SleepService.PREDICTION_MIN_COUNT
    svc.MAX_PREDICTIONS = cap
    if policy is not None:
        svc.admission_policy = policy
    return svc


def _engine(cap=40, temporal=None, freqs=None):
    return _service(SleepService, None, cap)._build_predictions(
        temporal or CROWDED, freqs or FREQS)


def _adopted(policy, cap=40, temporal=None, freqs=None):
    return _service(A.DiversityFirstSleepService, policy, cap)._build_predictions(
        temporal or CROWDED, freqs or FREQS)


def _ids(predictions):
    return [(p.source, p.target) for p in predictions]


# ---------------------------------------------------------------------------
# The reference rule is delegated to, not re-implemented
# ---------------------------------------------------------------------------

def test_the_count_arm_returns_exactly_what_the_engine_returns():
    engine = _engine()
    adopted = _adopted(A.COUNT)
    assert [(p.id, p.source, p.target, p.strength, p.evidence) for p in adopted] == \
           [(p.id, p.source, p.target, p.strength, p.evidence) for p in engine]


def test_the_count_arm_matches_the_engine_at_every_cap():
    for cap in (1, 3, 6, 40):
        assert _ids(_adopted(A.COUNT, cap=cap)) == _ids(_engine(cap=cap))


def test_the_reference_engine_still_returns_its_own_admission():
    engine = _engine(cap=6)
    assert _ids(engine) == _ids(_adopted(A.COUNT, cap=6))
    assert len(engine) == 6


def test_the_floor_is_inert_at_the_engines_own_caps():
    for cap in (SleepService.MAX_PREDICTIONS, 20, 40):
        assert A.effective_cap(cap, 16) == cap


# ---------------------------------------------------------------------------
# The adopted rule does something, and it is the right something
# ---------------------------------------------------------------------------

def _pool():
    """A crowded pool in the engine's own candidate type, with no engine ordering."""
    rows = [("aaaa", "bbbb", 9), ("aaaa", "cccc", 8), ("aaaa", "dddd", 7),
            ("aaaa", "eeee", 6), ("ffff", "gggg", 5), ("hhhh", "iiii", 5),
            ("jjjj", "kkkk", 5), ("llll", "mmmm", 5), ("nnnn", "oooo", 5)]
    return [PredictionCandidate(
        id="pred:%s>%s" % (a, b), source=a, target=b, strength=1.0,
        evidence={"temporal_count": c, "source_frequency": 20,
                  "target_frequency": c, "ratio": 1.0})
        for a, b, c in rows]


def test_the_two_orderings_differ_on_a_crowded_pool():
    pool = _pool()
    count = A.rank(pool, 6, A.COUNT)
    diversity = A.rank(pool, 6, A.DIVERSITY)
    assert sum(1 for p in count if p.source == "aaaa") == 4
    assert sum(1 for p in diversity if p.source == "aaaa") == 1
    assert len({p.source for p in diversity}) == 6


def test_the_adopted_arm_changes_which_edges_are_admitted_at_the_same_budget():
    count = _adopted(A.COUNT, cap=6)
    diversity = _adopted(A.DIVERSITY, cap=6)
    assert len(count) == len(diversity) == 6
    assert _ids(count) != _ids(diversity), \
        "identical admissions would be an unrun experiment"
    assert max(Counter(p.source for p in diversity).values()) == 1


def test_the_adopted_arm_spreads_across_sources_and_honours_the_budget():
    chosen = _adopted(A.DIVERSITY, cap=6)
    assert len(chosen) == 6
    assert len({p.source for p in chosen}) == 6
    for cap in (1, 2, 3, 6):
        picked = _adopted(A.DIVERSITY, cap=cap)
        assert len(picked) <= max(cap, 6)


def test_every_adopted_admission_was_already_eligible():
    pool = {p.id for p in _engine(cap=A.DiversityFirstSleepService._POOL_PROBE)}
    assert {p.id for p in _adopted(A.DIVERSITY)} <= pool


def test_each_slot_takes_the_least_crowded_source_available():
    """The invariant, checked against the pool rather than against the orderer."""
    chosen = _adopted(A.DIVERSITY, cap=6)
    pool = {p.id: p for p in _engine(cap=A.DiversityFirstSleepService._POOL_PROBE)}
    admitted: dict[str, int] = {}
    for picked in chosen:
        best = min(pool.values(),
                   key=lambda p: (admitted.get(p.source, 0),
                                  -p.evidence["temporal_count"], p.source, p.target))
        assert picked.id == best.id
        admitted[picked.source] = admitted.get(picked.source, 0) + 1
        pool.pop(picked.id)


def test_ranking_is_deterministic():
    assert _ids(_adopted(A.DIVERSITY, cap=6)) == _ids(_adopted(A.DIVERSITY, cap=6))


def test_an_unknown_policy_is_refused():
    with pytest.raises(ValueError, match="unknown admission policy"):
        A.rank([], 3, "frequency")


def test_a_non_positive_budget_admits_nothing():
    assert A.rank(_engine(), 0) == []
    assert A.rank(_engine(), -2) == []


# ---------------------------------------------------------------------------
# The floor
# ---------------------------------------------------------------------------

def test_the_floor_binds_below_the_source_count():
    assert A.effective_cap(4, 16) == 16
    assert A.effective_cap(0, 16) == 16


def test_the_floor_does_not_apply_to_the_reference_rule():
    assert A.effective_cap(4, 16, A.COUNT) == 4


def test_the_floor_is_never_a_reduction():
    assert A.effective_cap(100, 16) == 100


# ---------------------------------------------------------------------------
# The frozen boundary, checked rather than asserted
# ---------------------------------------------------------------------------

def test_no_engine_file_is_modified():
    changed = subprocess.run(["git", "status", "--porcelain", "--", *ENGINE],
                             cwd=str(ROOT), capture_output=True, text=True)
    assert changed.returncode == 0
    assert changed.stdout.strip() == "", changed.stdout
    diff = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", *ENGINE],
                          cwd=str(ROOT), capture_output=True, text=True)
    assert diff.returncode == 0, "an engine file differs from HEAD"


def test_the_adoption_is_a_subclass_and_not_a_monkeypatch():
    assert issubclass(A.DiversityFirstSleepService, SleepService)
    assert A.DiversityFirstSleepService is not SleepService
    source = (ROOT / "organica" / "admission.py").read_text(encoding="utf-8")
    assert "SleepService._build_predictions =" not in source
    assert "setattr(SleepService" not in source


def test_the_pool_probe_is_restored_after_use():
    svc = _service(A.DiversityFirstSleepService, A.DIVERSITY, cap=6)
    svc._build_predictions(CROWDED, FREQS)
    assert svc.MAX_PREDICTIONS == 6
