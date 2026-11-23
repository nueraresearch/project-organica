"""Tests for the frozen long-delay capability protocol."""
from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks.decay_confirmation import harvest_seeds  # noqa: E402
from benchmarks.long_delay_capability_prereg import (  # noqa: E402
    PROTOCOL,
    PROTOCOL_DIGEST,
    classify,
    delta,
    digest,
    seed_live,
    unused_seeds,
    validate,
)


def test_digest_matches_the_frozen_constant():
    assert digest() == PROTOCOL_DIGEST


def test_validate_has_no_problems():
    assert validate() == []


def test_delta_floor_and_factor():
    assert delta(0.0) == PROTOCOL["delta_floor"]
    assert delta(0.01) == PROTOCOL["delta_sd_factor"] * 0.01


def test_classify_capability_earned():
    assert classify(early_gap=0.001, late_gap=0.02, late_positive=9,
                    transition_positive=9, gates_ok=True) == "CAPABILITY_EARNED"


def test_classify_late_gain_early_cost():
    assert classify(early_gap=0.02, late_gap=0.02, late_positive=9,
                    transition_positive=9, gates_ok=True) == "LATE_GAIN_EARLY_COST"


def test_classify_persistence_without_capability():
    assert classify(early_gap=0.0, late_gap=-0.001, late_positive=3,
                    transition_positive=3, gates_ok=True) == \
        "PERSISTENCE_WITHOUT_CAPABILITY"


def test_classify_void_when_a_gate_fails():
    assert classify(early_gap=0.0, late_gap=0.05, late_positive=10,
                    transition_positive=10, gates_ok=False) == "VOID"


def test_classify_uses_the_calibrated_bar():
    assert classify(early_gap=0.0, late_gap=0.02, late_positive=9,
                    transition_positive=9, gates_ok=True,
                    bar=0.0412) == "INCONCLUSIVE"


def test_seed_live_can_fail():
    assert not seed_live({"0.95": [0.90, 0.90], "0.9925": [0.91, 0.91]})
    assert seed_live({"0.95": [0.90, 0.91], "0.9925": [0.91, 0.91]})


def test_seed_blocks_were_consumed_and_are_disjoint():
    harvested = harvest_seeds()
    assert set(PROTOCOL["design_seeds"]) <= harvested
    assert set(PROTOCOL["confirm_seeds"]) <= harvested
    assert not (set(PROTOCOL["design_seeds"])
                & set(PROTOCOL["confirm_seeds"]))
    assert unused_seeds(set())
    assert not unused_seeds({PROTOCOL["confirm_seeds"][0]})


def test_windows_do_not_overlap():
    assert PROTOCOL["windows"]["early"][1] <= PROTOCOL["windows"]["late"][0]
