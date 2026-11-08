"""Tests for Q052 amendment A2: the cohort mass, the calibrated floor, and the label.

The property that matters is discrimination, not arithmetic: the amended mass must not move when
something outside the cohort is pruned, because that is exactly what the first definition did.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from benchmarks import q052_amendment_a2 as a2

ROOT = Path(__file__).resolve().parents[1]


def row(pairs, theories=None):
    """A captured cycle: `pairs` is (subject, expectation, support); theories default to one."""
    retained = [{"subject": s, "expectation": e, "support_count": c} for s, e, c in pairs]
    if theories is None:
        theories = [("alpha", 100)]
    cycles = []
    for subject, support in theories:
        cycles.append({"subject": subject, "support_count": support,
                       "hypotheses": [{"expectation": e, "support_count": c}
                                      for s, e, c in pairs if s == subject]})
    return {"theories": cycles, "retained_hypotheses": retained}


def cell(ratio, competing_at_death=None, competing_at_live=None, pairs_at_death=2):
    return {"mass_ratio": ratio,
            "subjects_with_competing_at_death": dict(competing_at_death or {}),
            "subjects_with_competing_at_last_live": dict(competing_at_live or {}),
            "subjects_with_pairs_at_death": {"s%d" % i: 2 for i in range(pairs_at_death)}}


def test_cohort_mass_is_not_moved_by_pruning_outside_the_cohort():
    before = row([("a", "x", 10), ("a", "y", 10)])
    at = row([("a", "x", 8), ("a", "y", 8)])
    baseline = a2.cohort_census(before, at)["mass_ratio"]

    # The same two cohort members, surviving with the same supports, while an unrelated
    # hypothesis is pruned at the death cycle.
    at_with_stranger = row([("a", "x", 8), ("a", "y", 8), ("b", "z", 400)])
    with_stranger = a2.cohort_census(before, at_with_stranger)["mass_ratio"]

    assert baseline == pytest.approx(0.8)
    assert with_stranger == baseline, "a hypothesis outside the cohort moved the ratio"

    # The total-mass definition does move, which is the defect A2 replaces.
    total_before = sum(10 for _ in range(2))
    total_with = (8 + 8 + 400) / total_before
    assert total_with != baseline


def test_cohort_member_gone_at_death_counts_as_zero():
    before = row([("a", "x", 10), ("a", "y", 10)])
    at = row([("a", "x", 10)])
    census = a2.cohort_census(before, at)
    assert census["cohort_size"] == 2
    assert census["cohort_survived"] == 1
    assert census["mass_ratio"] == pytest.approx(0.5)


def test_the_three_branches_the_amendment_can_take(monkeypatch):
    monkeypatch.setattr(a2, "FLOOR", 0.5)
    control = {"reproduced": True, "mass_floor_met": True}
    transitions = {"1": 1, "2": 1, "3": 1}

    collapsed = [cell(0.3), cell(0.31), cell(0.03)]
    label, fired = a2.classify(collapsed, control, transitions)
    assert label == "DIFFERENT_SUPPORT_COLLAPSE"
    assert fired["support_collapse"] is True

    same = [cell(0.9, competing_at_live={"alpha": 2}),
            cell(0.9, competing_at_live={"alpha": 2}),
            cell(0.9, competing_at_live={"alpha": 2})]
    label, fired = a2.classify(same, control, transitions)
    assert label == "SAME_COMPETITION_LOSS"
    assert fired["same"] is True

    void_control = {"reproduced": True, "mass_floor_met": False}
    assert a2.classify(collapsed, void_control, transitions)[0] == "VOID"
    interrupted = {"1": 2, "2": 1, "3": 1}
    assert a2.classify(collapsed, control, interrupted)[0] == "DIFFERENT_INTERMITTENT"
    assert a2.classify(collapsed[:1], control, transitions)[0] == "VOID"


def test_calibration_never_uses_the_cell_it_judges():
    assert a2.CONTROL["seed"] not in a2.CALIBRATION_SEEDS
    record = a2.calibration()
    assert set(record["ratios"]) == {str(seed) for seed in a2.CALIBRATION_SEEDS}
    lowest = min(value for value in record["ratios"].values() if value is not None)
    assert record["floor"] == pytest.approx(round(lowest - a2.CALIBRATION_MARGIN, 4), abs=1e-9)


def test_the_committed_artifact_is_the_one_its_cells_imply():
    artifact = __import__("json").loads(a2.ARTIFACT.read_text(encoding="utf-8"))
    assert a2.validate() == []
    assert artifact["label"] == "DIFFERENT_SUPPORT_COLLAPSE"
    assert artifact["control"]["reproduced"] is True
    assert artifact["control"]["mass_floor_met"] is True
    assert artifact["probed"]["seeds"] == list(a2.SEEDS)
    for held in a2.SEEDS:
        assert held not in a2.cc.PROBED["seeds"], "an A2 seed is reused from the A1 block"
    assert a2.PARTS != a2.cc.PARTS, "the amendment reuses the A1 parts directory"
