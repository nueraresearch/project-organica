"""The onset instrument's analysis, checked without running the engine.

The run itself is expensive; these tests pin the rules the run must obey, on
synthetic parts with the same shape the worker writes.  Each one is written to
fail if the corresponding rule is broken.
"""
from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "benchmarks"))

import divergence_onset as onset  # noqa: E402


def part(cycles: dict[int, list[str] | None]) -> dict:
    """A part whose arm B holds ``cycles``; ``None`` means a refused window."""
    arms = {}
    for cycle, ids in cycles.items():
        if ids is None:
            arms[str(cycle)] = {"addressed": False, "candidates": []}
        else:
            arms[str(cycle)] = {"addressed": True,
                                "candidates": [{"id": i, "type": "exp"} for i in ids]}
    return {"arms": {"B": arms}}


def test_engine_cycle_is_the_audit_index_plus_one():
    # The defect this whole line of work corrected: an index is not a cycle.
    assert onset.engine_cycle(0) == 1
    assert onset.engine_cycle(11) == 12


def test_a_refused_window_is_not_measured_and_not_an_empty_pool():
    ids, captured = onset.pool(part({3: None}), "B", 3)
    assert captured is False
    assert ids == []
    # A missing cycle behaves the same way, rather than raising or comparing equal.
    assert onset.pool(part({}), "B", 5) == ([], False)


def test_onset_is_the_first_cycle_that_differs_after_an_identical_one():
    camp = part({1: ["a"], 2: ["a"], 3: ["a", "b"], 4: ["a", "b"]})
    ours = part({1: ["a"], 2: ["a"], 3: ["a"], 4: ["a"]})
    info = onset.onset_for_arm(camp, ours, "B", 4)
    assert info["state"] == "onset"
    assert info["onset_cycle"] == 3
    assert info["entered"] == ["b"]
    assert info["left"] == []


def test_onset_at_cycle_one_is_reported_as_at_or_before_one():
    info = onset.onset_for_arm(part({1: ["a"], 2: ["a"]}),
                               part({1: ["b"], 2: ["b"]}), "B", 2)
    # There is no cycle 0 window, so the claim is "<= 1", never "at cycle 1".
    assert info["state"] == "at_or_before_1"
    assert info["onset_cycle"] == 1


def test_identical_pools_at_every_cycle_report_no_onset():
    info = onset.onset_for_arm(part({1: ["a"], 2: ["a", "b"]}),
                               part({1: ["a"], 2: ["b", "a"]}), "B", 2)
    # Same membership, different order: the onset is about membership only.
    assert info["state"] == "none"


def test_an_unmeasured_cycle_cannot_produce_an_onset():
    camp = part({1: ["a"], 2: None, 3: ["a", "b"]})
    ours = part({1: ["a"], 2: ["a"], 3: ["a"]})
    info = onset.onset_for_arm(camp, ours, "B", 3)
    # The bracket at cycle 2 is missing, so no onset may be asserted from it.
    assert info["state"] in ("not_measured", "none")
    assert info["onset_cycle"] is None


def test_a_differing_set_always_names_what_moved():
    # F4's invariant: an onset with an empty transition record is impossible,
    # so a renderer that prints one has a defect rather than a finding.
    # Identical at cycle 1, differing at cycle 2, so the bracket is a real one.
    camp = part({1: ["a"], 2: ["a", "b", "c"]})
    ours = part({1: ["a"], 2: ["a"]})
    info = onset.onset_for_arm(camp, ours, "B", 2)
    assert info["state"] == "onset"
    assert info["entered"] or info["left"]


def test_a_control_with_one_hash_seed_cannot_fail():
    # The control the run actually used: both sides at seed 0. Comparing a run
    # with itself always returns "identical", so the gauge claim is void.
    assert onset.control_is_valid(0, 0) is False
    assert onset.control_is_valid(0, 1) is True
