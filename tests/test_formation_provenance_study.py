"""The study runner's arithmetic and its preregistered seed sets."""
from __future__ import annotations

import json
import pathlib
import random

from benchmarks import formation_provenance_study as s


def test_seed_blocks_are_preregistered_and_disjoint_from_every_closed_seed():
    assert s.DESIGN_SEEDS == tuple(range(20270101, 20270106))
    assert s.CONFIRMATORY_SEEDS == tuple(range(20270106, 20270121))
    closed = set(range(20261201, 20261227))
    assert closed.isdisjoint(s.DESIGN_SEEDS + s.CONFIRMATORY_SEEDS)


def test_held_out_pairs_come_only_from_the_held_out_window():
    epc = s.EVENTS_PER_CYCLE
    lo, hi = s.PHASE_TRANSFER
    events = ["xray xray"] * (lo * epc)
    events += ["zulu yank"] * ((hi - lo) * epc)
    events += ["whiskey xray"] * (epc * 2)
    pairs = s.held_out_pairs({"events": events})
    assert ("zulu", "yank") in pairs
    assert not any("whiskey" in pair for pair in pairs)


def test_endpoint_is_the_difference_between_the_two_arms():
    rows = [{"seed": 1, "status": "pair_world_attributed", "held_out": True},
            {"seed": 1, "status": "pair_self_sourced", "held_out": False}]
    assert s._difference(rows) == 1.0
    ci = s._interval(s._bootstrap_cluster(rows, [1], random.Random(0)))
    assert ci[0] > 0.0


def test_a_missing_arm_is_not_measurable_not_zero():
    rows = [{"seed": 1, "status": "pair_world_attributed", "held_out": True}]
    assert s._difference(rows) != s._difference(rows)   # NaN: no denominator


def test_permutation_shuffles_labels_within_seed_and_cycle_only():
    rows = [{"seed": 1, "cycle": 1, "status": "pair_world_attributed", "held_out": True},
            {"seed": 1, "cycle": 1, "status": "pair_self_sourced", "held_out": False},
            {"seed": 1, "cycle": 2, "status": "pair_mixed", "held_out": True}]
    permuted = s._permuted(rows, random.Random(0))
    group = sorted(r["status"] for r in permuted if r["cycle"] == 1)
    assert group == ["pair_self_sourced", "pair_world_attributed"]
    assert [r["status"] for r in permuted if r["cycle"] == 2] == ["pair_mixed"]


def test_artifact_records_the_endpoint_and_its_limits():
    art = json.loads(pathlib.Path(s.RESULT_OUT).read_text(encoding="utf-8"))
    assert art["arms"]["pair_world_attributed"]["n"] >= 30
    assert art["arms"]["origin_includes_self"]["n"] >= 30
    assert art["interval"][0] <= art["interval"][1]
    assert art["interval_method"] and art["bootstrap_replicates"] == 10_000
    assert art["gates"]["G3_permutation_includes_zero"] is True
    assert art["does_not_establish"]
