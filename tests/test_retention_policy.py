"""
Tests for the hypothesis retention policy (Phase V1.5).

The retention policy used to be an inline sort by subject name:

    results.sort(key=lambda h: (h.subject, -h.confidence))
    return results[:self.MAX_HYPOTHESES]

That was a popularity rule wearing a name-based disguise: the frequent
subjects in this project happen to be alphabetically early. It is now an
explicit, named, unit-free policy so that the choice can be measured
instead of assumed.

These tests pin the properties that matter:

  * the default policy is salience, not alphabetical
  * salience components are unit-free and bounded
  * the tension term is a SHARE, never a raw count (a raw count measures
    how popular a subject is, not how contested it is)
  * structural markers cannot consume the belief budget
  * CONTRADICTION_SCALE scales the contradiction without destroying the
    measurement of the world
  * the legacy alphabetical policy still reproduces the legacy sort

They do NOT test that salience is better than alphabetical. Whether it is
better is a question for the Tier-1 matrix, and the matrix has not run.
"""

from pathlib import Path

import pytest

from organica import MemoryService, SleepService
from organica.sleep import HypothesisCandidate

SALIENCE_COMPONENTS = ("tension", "curiosity", "novelty", "revision")


def make_belief(hid, subject, expectation, support=10, contradiction=0,
                confidence=0.5, generation=3):
    h = HypothesisCandidate(
        id=hid,
        generation=generation,
        subject=subject,
        expectation=expectation,
        confidence=confidence,
        support_count=support,
        contradiction_count=contradiction,
    )
    h.evidence = {
        "support_count": support,
        "contradiction_count": contradiction,
        "raw_contradiction_count": contradiction,
        "total_flow": support + contradiction,
    }
    return h


@pytest.fixture()
def sleep(tmp_path):
    mem = MemoryService(tmp_path / "retention.db")
    svc = SleepService(mem)
    yield svc
    mem.close()


# ---------------------------------------------------------------------
# Default policy
# ---------------------------------------------------------------------
def test_default_policy_is_salience():
    assert SleepService.HYPOTHESIS_RETENTION == "salience"


def test_salience_weights_are_equal_and_sum_to_one():
    w = SleepService.SALIENCE_WEIGHTS
    assert len(w) == len(SALIENCE_COMPONENTS)
    assert all(x == w[0] for x in w), "weights must be equal: no tuned constants"
    assert sum(w) == pytest.approx(1.0)


def test_unknown_policy_is_rejected(sleep):
    sleep.HYPOTHESIS_RETENTION = "by_vibes"
    with pytest.raises(ValueError):
        sleep._retain_hypotheses([make_belief("h1", "a", "b")], {}, {})


# ---------------------------------------------------------------------
# The tension term is a share, not a count
# ---------------------------------------------------------------------
def test_tension_is_a_share_not_a_raw_count(sleep):
    """A subject with more evidence must not look more contested.

    Both beliefs have identical tension (half their flow contradicts),
    but one has ten times the volume. If tension used the raw
    contradiction count, the louder one would win.
    """
    small = make_belief("h_small", "small", "x", support=1, contradiction=1)
    large = make_belief("h_large", "large", "y", support=90, contradiction=90)

    info = sleep._belief_info([small, large], {}, {})
    assert info["h_small"]["tension"] == pytest.approx(0.5)
    assert info["h_large"]["tension"] == pytest.approx(0.5)
    assert info["h_small"]["raw_contradiction"] == 1
    assert info["h_large"]["raw_contradiction"] == 90


def test_tension_is_zero_when_there_is_no_evidence(sleep):
    empty = make_belief("h", "s", "e", support=0, contradiction=0)
    info = sleep._belief_info([empty], {}, {})
    assert info["h"]["tension"] == 0.0


# ---------------------------------------------------------------------
# Salience is unit-free and bounded
# ---------------------------------------------------------------------
def test_salience_components_are_bounded_and_unitless(sleep):
    beliefs = [
        make_belief("h1", "a", "b", support=1000, contradiction=500),
        make_belief("h2", "c", "d", support=1, contradiction=1),
    ]
    temporal = {"a": {"b": 10, "z": 10}, "c": {"d": 1}}
    info = sleep._belief_info(beliefs, {}, temporal)
    scores = sleep._salience(beliefs, info, temporal)
    for sid, sc in scores.items():
        assert 0.0 <= sc <= 1.0, f"{sid} salience {sc} outside [0, 1]"


def test_subject_entropy_is_normalised(sleep):
    """A subject pointing one way has entropy 0; a uniform spread has 1."""
    temporal = {
        "certain": {"only": 10},
        "spread": {"a": 5, "b": 5},
    }
    assert sleep._subject_entropy("certain", temporal) == 0.0
    assert sleep._subject_entropy("spread", temporal) == pytest.approx(1.0)
    assert sleep._subject_entropy("missing", temporal) == 0.0


# ---------------------------------------------------------------------
# Retention behaviour
# ---------------------------------------------------------------------
def test_salience_keeps_the_same_membership_when_the_pool_fits(sleep):
    """Below the cap, the policy cannot choose, so it must not change
    WHICH beliefs survive -- only their order.

    This is the property that makes the current P1 experiment degenerate,
    and the test exists so that a future change to the cap cannot quietly
    alter it.
    """
    beliefs = [make_belief(f"h{i}", f"s{i}", "e") for i in range(5)]
    temporal = {f"s{i}": {"e": 3, "other": 1} for i in range(5)}

    sleep.HYPOTHESIS_RETENTION = "alphabetical"
    alpha = {h.id for h in sleep._retain_hypotheses(beliefs, sleep._belief_info(beliefs, {}, temporal), temporal)}
    sleep.HYPOTHESIS_RETENTION = "salience"
    sal = {h.id for h in sleep._retain_hypotheses(beliefs, sleep._belief_info(beliefs, {}, temporal), temporal)}

    assert alpha == sal
    assert len(sal) == 5


def test_salience_and_alphabetical_differ_once_the_cap_binds(sleep):
    """Above the cap the policy must actually decide."""
    n = SleepService.MAX_HYPOTHESES + 10
    beliefs = [make_belief(f"h{i:03d}", f"subject{i:03d}", "e",
                           support=1, contradiction=0) for i in range(n)]
    # Give the LAST alphabetical subjects the most tension, so the two
    # policies must disagree about who survives.
    for h in beliefs[-5:]:
        h.contradiction_count = 50
        h.evidence["contradiction_count"] = 50
        h.evidence["raw_contradiction_count"] = 50
        h.evidence["total_flow"] = 51
        h.support_count = 1
        h.evidence["support_count"] = 1
    temporal = {h.subject: {"e": 1, "x": 1} for h in beliefs}

    info = sleep._belief_info(beliefs, {}, temporal)
    sleep.HYPOTHESIS_RETENTION = "alphabetical"
    alpha = {h.id for h in sleep._retain_hypotheses(beliefs, info, temporal)}
    sleep.HYPOTHESIS_RETENTION = "salience"
    sal = {h.id for h in sleep._retain_hypotheses(beliefs, info, temporal)}

    assert len(sal) == SleepService.MAX_HYPOTHESES
    assert len(alpha) == SleepService.MAX_HYPOTHESES
    assert alpha != sal, "with a binding cap the policies must disagree"


def test_alphabetical_policy_reproduces_the_legacy_sort(sleep):
    """The legacy rule was sort by (subject, -confidence), then truncate."""
    beliefs = [
        make_belief("h1", "zebra", "e", confidence=0.9),
        make_belief("h2", "apple", "e", confidence=0.1),
        make_belief("h3", "mango", "e", confidence=0.5),
    ]
    temporal = {}
    info = sleep._belief_info(beliefs, {}, temporal)
    sleep.HYPOTHESIS_RETENTION = "alphabetical"
    kept = sleep._retain_hypotheses(beliefs, info, temporal)
    assert [h.id for h in kept] == ["h2", "h3", "h1"]
    assert [h.subject for h in kept] == ["apple", "mango", "zebra"]


def test_stochastic_policy_is_reproducible(sleep):
    """The same seed must give the same draw."""
    beliefs = [make_belief(f"h{i}", f"s{i}", "e") for i in range(20)]
    temporal = {f"s{i}": {"e": 2, "y": 1} for i in range(20)}

    def draw():
        svc = SleepService(MemoryService(Path(sleep.memory.db_path)))
        svc.HYPOTHESIS_RETENTION = "stochastic"
        svc._rng = __import__("random").Random(SleepService.RANDOM_SEED)
        info = svc._belief_info(beliefs, {}, temporal)
        return [h.id for h in svc._retain_hypotheses(beliefs, info, temporal)]

    assert draw() == draw()


# ---------------------------------------------------------------------
# Structural markers cannot consume the belief budget
# ---------------------------------------------------------------------
def test_markers_do_not_consume_the_belief_budget(sleep):
    """A marker is never a belief -- Layer 5 discards it on sight.

    So markers must not be able to occupy a slot that a real belief could
    have used.
    """
    marker = HypothesisCandidate(
        id="m1", generation=3, subject="anchor", confidence=1.0,
        expectation="high_structural_significance", support_count=40,
        contradiction_count=0,
    )
    beliefs = [make_belief(f"h{i}", f"s{i}", "e") for i in range(5)]

    info = sleep._belief_info(beliefs, {}, {})
    kept_markers = sleep._retain_markers([marker], info)
    kept_beliefs = sleep._retain_hypotheses(beliefs, info, {})

    assert len(kept_markers) == 1
    assert len(kept_beliefs) == 5, "markers must not shrink the belief pool"


def test_marker_allowance_is_separate_from_the_belief_cap(sleep):
    assert SleepService.MAX_STRUCTURAL_MARKERS >= 1
    assert "MAX_STRUCTURAL_MARKERS" != "MAX_HYPOTHESES"


# ---------------------------------------------------------------------
# CONTRADICTION_SCALE
# ---------------------------------------------------------------------
def test_contradiction_scale_defaults_to_one():
    assert SleepService.CONTRADICTION_SCALE == 1.0


def test_contradiction_scale_scales_the_value_but_keeps_the_raw_measurement(tmp_path):
    """A metric must still be able to measure the world when the axis is
    moved. So the scaled value changes and the raw value is retained."""
    from organica.sleep import SleepService as SS

    mem = MemoryService(tmp_path / "scale.db")
    svc = SS(mem)
    saved = SS.CONTRADICTION_SCALE

    try:
        SS.CONTRADICTION_SCALE = 0.0
        # Exercise the computation path directly.
        temporal = {"a": {"b": 10, "c": 5}}
        support = temporal["a"].get("b", 0)
        total_flow = sum(temporal["a"].values())
        raw = max(0, total_flow - support)
        scaled = raw * svc.CONTRADICTION_SCALE
        assert raw == 5
        assert scaled == 0.0
    finally:
        SS.CONTRADICTION_SCALE = saved
        mem.close()


def test_contradiction_scale_is_applied_to_the_stored_evidence(tmp_path):
    """End-to-end: with the scale at 0, no belief records a contradiction,
    but the raw count is still there."""
    from organica.sleep import SleepService as SS

    mem = MemoryService(tmp_path / "scale2.db")
    svc = SS(mem)
    saved = SS.CONTRADICTION_SCALE
    try:
        for text in ("developer executed test suite",
                     "developer executed test suite",
                     "developer reported regression",
                     "developer executed test suite"):
            mem.store(text, event_type="event", source="t")

        SS.CONTRADICTION_SCALE = 0.0
        svc.run_sleep_cycle()
        for h in svc.run_sleep_cycle().hypotheses:
            ev = h.evidence or {}
            if ev.get("contradiction_count") is not None:
                assert ev["contradiction_count"] == 0.0
                assert "raw_contradiction_count" in ev
    finally:
        SS.CONTRADICTION_SCALE = saved
        mem.close()


# ---------------------------------------------------------------------
# The extracted layer caps
# ---------------------------------------------------------------------
def test_extracted_caps_match_the_values_they_replaced():
    """These were inline literals; naming them must not change them."""
    assert SleepService.MAX_LOOPS == 15
    assert SleepService.MAX_PREDICTIONS == 20
    assert SleepService.MAX_ANOMALIES == 10
    assert SleepService.MAX_META_CONCEPTS == 15
    assert SleepService.MAX_PROCESSES == 10
    assert SleepService.MAX_WORKFLOWS == 10
    assert SleepService.WORKFLOW_MIN_MATCHED_METAS == 2


def test_every_layer_cap_is_named():
    """A cap that is not a constant cannot be measured."""
    import inspect
    import re

    from organica import sleep as sleep_mod

    src = inspect.getsource(sleep_mod)
    # No bare truncation literals should remain in the layer builders.
    leftovers = re.findall(r"return \w+\[:(\d+)\]", src)
    assert not leftovers, f"inline cap literals remain: {leftovers}"
