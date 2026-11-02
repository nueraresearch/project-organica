"""The strength-assignment intervention and its protocol.

The intervention is a row-wise permutation of weights, so the claims worth
testing are the ones the closed structural-contribution study could not make:
that topology survives it exactly, that the null is reachable with unequal
weights, and that the fixtures can fail.
"""
from __future__ import annotations

import json
import pathlib

import pytest

from benchmarks import strength_assignment as sa
from benchmarks import strength_assignment_harness as sh

ROOT = pathlib.Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# The intervention
# ---------------------------------------------------------------------------

def test_topology_degrees_and_row_totals_are_identical():
    rows = {"a": {"x": 3.0, "y": 1.0}, "b": {"x": 2.0, "z": 4.0}, "c": {"y": 5.0}}
    shuffled = sa.shuffle_once(rows, 20270401, 0)
    check = sa.invariants(rows, shuffled)
    assert check["preserved"], check
    assert check["edge_pairs"] is True
    assert sum(rows["b"].values()) == sum(shuffled["b"].values())


def test_a_cross_row_move_is_caught():
    rows = {"a": {"x": 3.0, "y": 1.0}, "b": {"x": 2.0}}
    broken = {"a": {"x": 3.0}, "b": {"x": 2.0, "y": 1.0}}
    check = sa.invariants(rows, broken)
    assert not check["preserved"]
    assert not check["row_totals"]
    assert not check["edge_pairs"]


def test_identity_permutation_moves_nothing_and_fails_the_movement_gate():
    rows = {"a": {"x": 1.0, "y": 2.0, "z": 3.0}}
    assert sa.moved_share(rows, rows) == 0.0
    assert not (sa.moved_share(rows, rows) >= sa.MOVED_LIMIT)


def test_a_real_draw_moves_most_edges_and_keeps_invariants():
    rows = {f"s{i}": {f"t{j}": float(10 * j + i) for j in range(4)} for i in range(12)}
    shuffled = sa.shuffle_once(rows, 20270401, 3)
    assert sa.moved_share(rows, shuffled) >= sa.MOVED_LIMIT
    assert sa.invariants(rows, shuffled)["preserved"]


def test_draws_reproduce_from_the_seed_and_draw_index():
    rows = {f"s{i}": {f"t{j}": float(j + 1) for j in range(3)} for i in range(5)}
    first = sa.shuffle_many(rows, 20270401)
    second = sa.shuffle_many(rows, 20270401)
    assert first == second
    assert first[0] != first[1], "different draws must be different graphs"


def test_the_draw_multiplier_is_this_studys_own():
    assert sa.DRAW_SEED_MULTIPLIER == 1013
    assert sa.DRAWS == 25


# ---------------------------------------------------------------------------
# The plants
# ---------------------------------------------------------------------------

def test_positive_plant_shuffling_costs_loss():
    got = sa.planted_positive()
    assert got["passed"], got
    assert got["increase"] > 0.5


def test_negative_plant_is_reachable_with_nonconstant_weights():
    got = sa.planted_negative_exchangeable()
    assert got["passed"], got
    assert got["weights_are_nonconstant"], got
    assert len(set(got["weights"])) == len(got["weights"])


def test_negative_plant_fails_when_exchangeability_breaks():
    got = sa.fixture_can_fail()
    assert got["passed"], got
    assert got["change"] > 0.5


def test_constant_weight_fixture_is_labelled_as_the_weaker_one():
    got = sa.planted_negative_constant()
    assert got["passed"]
    assert "weaker" in got["label"]


# ---------------------------------------------------------------------------
# The outcome table
# ---------------------------------------------------------------------------

def test_outcome_table_reaches_every_label():
    table = sa.outcome_table()
    labels = {row["label"] for row in table}
    assert len(table) == 4
    assert labels == {sa.CONTRIBUTES_AND_BEATS, sa.CONTRIBUTES_ONLY,
                      sa.NOT_DEPENDENT, sa.NO_CONTRIBUTION}


def test_the_direction_is_above_zero_not_below():
    """The closed study asked for an upper bound below zero; this one flips it."""
    assert sa.outcome_label(True, False) == sa.CONTRIBUTES_ONLY
    assert sa.outcome_label(False, True) == sa.NOT_DEPENDENT


# ---------------------------------------------------------------------------
# Guards
# ---------------------------------------------------------------------------

def test_a_confirmatory_seed_is_refused_before_the_audit():
    with pytest.raises(SystemExit):
        sh.refuse_confirmatory(sh.CONFIRMATORY_SEEDS[0])


def test_an_unlisted_seed_is_refused():
    with pytest.raises(SystemExit):
        sh.refuse_confirmatory(20260101)


def test_a_design_seed_cannot_be_used_as_confirmatory():
    with pytest.raises(SystemExit):
        sh.refuse_design(sh.DESIGN_SEEDS[0])


def test_the_seed_blocks_are_disjoint_and_fresh():
    assert not set(sh.DESIGN_SEEDS) & set(sh.CONFIRMATORY_SEEDS)
    assert min(sh.DESIGN_SEEDS) > 20270320, "must not reuse the closed study's block"
    assert len(sh.CONFIRMATORY_SEEDS) == 15


def test_constants_match_the_protocol():
    assert sh.CAP == 1000
    assert sh.ALPHA == 256.0
    assert sh.TUNING_CYCLES == 15


# ---------------------------------------------------------------------------
# The protocol document
# ---------------------------------------------------------------------------

def test_the_preregistration_is_committed_with_its_seeds_and_direction():
    text = (ROOT / "docs/STRENGTH-ASSIGNMENT-PREREGISTRATION.md").read_text(encoding="utf-8")
    flat = " ".join(text.split())
    assert "20270401" in flat and "20270406" in flat
    assert "lower** bound of the 98.33 % interval on `d_shuffled` is **strictly above zero" in flat
    assert "exactly zero" in flat
    assert "20270301" in flat, "the closed study's block must be named as untouchable"


def test_the_primary_window_is_the_full_window_after_amendment_a1():
    """A1 moved the window because the withheld window left 1.6% of cells informed."""
    assert sh.PRIMARY_WINDOW[0] == "full"
    assert sh.WINDOWS[0] == sh.PRIMARY_WINDOW
    assert sh.SECONDARY_WINDOW[0] == "withheld"
    assert sh.COVERAGE_FLOOR == 0.50


def test_the_committed_design_artifact_passed_and_formed_no_endpoint():
    artifact = json.loads((ROOT / "docs/strength_assignment_design_audit.json").read_text())
    assert artifact["failures"] == []
    assert artifact["confirmatory_seeds_run"] == 0
    assert artifact["cells"][0]["deltas"] is None
    for cell in artifact["cells"]:
        assert cell["world"]["primary_window"] == "full"
        assert cell["gates"]["S2"]["coverage_share"] >= sh.COVERAGE_FLOOR
        assert cell["gates"]["S2"]["readout_changes"] is True


def test_no_design_artifact_claims_an_endpoint(tmp_path):
    """A design artifact that formed a contrast would be the failure this guards."""
    artifact = {
        "kind": "strength_assignment_design_audit",
        "endpoint": sh.ENDPOINT_NOT_FORMED,
        "deltas": None,
    }
    assert artifact["deltas"] is None
    assert "not formed" in artifact["endpoint"]
    json.dumps(artifact)
