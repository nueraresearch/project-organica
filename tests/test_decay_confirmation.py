"""The confirmation harness must be able to fail.

These tests use no engine cycles: they exercise the design audit, the
calibration rule, the sealed artifact and every branch of the conjunctive
decision on synthetic cells.  If a gate cannot fire, the protocol is
decoration, so each rejection label has a test that produces it.
"""
from __future__ import annotations

import json

import pytest

from benchmarks.decay_confirmation import (
    CALIBRATION_SEEDS, DEGREES, GRID, HELDOUT_SEEDS,
    audit_worlds, choose_threshold, decide, harvest_seeds, realised_out_degree,
    degree_world, seal, verify_seal,
)


# ---------------------------------------------------------------------------
# Design audit: the degree axis is live, and tags are visible
# ---------------------------------------------------------------------------

def test_every_degree_world_has_the_degree_it_claims():
    report = audit_worlds()
    assert report["ok"], report["problems"]
    for row in report["worlds"]:
        assert row["realised"] == row["degree"], row
        assert not row["short_tags"], row


def test_an_odd_degree_is_rejected_rather_than_rounded():
    with pytest.raises(ValueError, match="even hub out-degrees"):
        degree_world(3)


def test_the_audit_can_fail_when_a_hub_is_too_small():
    """Rule 9: a three-letter hub is invisible to the engine; the audit must say so."""
    assert realised_out_degree(degree_world(2)) == 2
    assert realised_out_degree(["hub leafaa leafab"], hub="hub") == 0


# ---------------------------------------------------------------------------
# Calibration rule
# ---------------------------------------------------------------------------

def _cal(tau, degree, precision=1.0, coverage=0.5, live=True):
    return {"tau": tau, "degree": degree, "seed": CALIBRATION_SEEDS[0],
            "liveness": live, "precision": precision, "coverage": coverage}


def test_calibration_takes_the_highest_coverage_threshold_that_clears_every_cell():
    cells = [
        _cal(0.05, 2, coverage=0.40), _cal(0.05, 12, coverage=0.55),
        _cal(0.10, 2, coverage=0.70), _cal(0.10, 12, coverage=0.60),
        _cal(0.15, 2, coverage=0.90), _cal(0.15, 12, precision=0.90, coverage=0.90),
    ]
    choice = choose_threshold(cells)
    assert choice["tau_star"] == 0.10
    assert "0.15" in choice["rejected"]


def test_calibration_tie_breaks_toward_the_larger_threshold():
    cells = [
        _cal(0.05, 2, coverage=0.50), _cal(0.05, 12, coverage=0.50),
        _cal(0.10, 2, coverage=0.50), _cal(0.10, 12, coverage=0.50),
    ]
    assert choose_threshold(cells)["tau_star"] == 0.10


def test_calibration_returns_none_when_no_threshold_clears_all_degrees():
    cells = [_cal(tau, degree, live=(degree != 12))
             for tau in (0.10, 0.15) for degree in (2, 12)]
    choice = choose_threshold(cells)
    assert choice["tau_star"] is None
    assert "no global threshold" in choice["reason"]


# ---------------------------------------------------------------------------
# The conjunctive decision, and every rejection it can return
# ---------------------------------------------------------------------------

def _cells(*, live12=True, precision2=1.0, false12=0, gap=0.2, cov_low=0.6,
           s_cov=0.5, b_low=0.6, s_live2=True, a_share_s=0.3, baseline=1.5):
    seeds = list(HELDOUT_SEEDS[:4])
    cells = []
    for degree in DEGREES:
        for seed in seeds:
            cells.append({"kind": "stationary", "arm": "transition", "degree": degree,
                          "seed": seed, "liveness": live12 if degree == 12 else True,
                          "stable_final": 20, "precision": precision2 if degree == 2 else 1.0,
                          "coverage": cov_low if degree in (2, 4) else 0.6,
                          "false_assertions": (5 if degree == 2 and precision2 < 1.0 else 0)
                          if degree != 12 else false12,
                          "theories_final": 3})
            shipped_live = degree in (2, 4) and (s_live2 if degree == 2 else True)
            cells.append({"kind": "stationary", "arm": "shipped", "degree": degree,
                          "seed": seed, "liveness": shipped_live,
                          "stable_final": 20 if shipped_live else 0,
                          "precision": 0.96 if shipped_live else None,
                          "coverage": s_cov if shipped_live else None,
                          "false_assertions": 0, "theories_final": 3 if shipped_live else 0})
            cells.append({"kind": "task", "arm": "transition", "degree": degree,
                          "seed": seed, "log_loss": 1.0,
                          "best_baseline_log_loss": baseline})
            cells.append({"kind": "task", "arm": "shipped", "degree": degree,
                          "seed": seed, "log_loss": 1.0 + gap})
    for degree in (4, 12):
        for seed in seeds:
            cells.append({"kind": "shift", "arm": "transition", "degree": degree,
                          "seed": seed,
                          "b_coverage_final": b_low if degree == 4 else 0.5,
                          "a_share_final": 0.3})
            cells.append({"kind": "shift", "arm": "shipped", "degree": degree,
                          "seed": seed, "b_coverage_final": 0.4,
                          "a_share_final": a_share_s})
    return cells


def test_all_conditions_met_adopts():
    verdict = decide(_cells(), {"tau_star": 0.075}, reps=300)
    assert verdict["all_conditions_met"], json.dumps(verdict["conditions"], indent=1)
    assert verdict["label"] == "adopt"
    assert verdict["verdict"] == "ADOPT"


def test_high_degree_failure_is_named_not_averaged_away():
    """A dead candidate at degree 12 is a high-degree finding, not incomparability."""
    verdict = decide(_cells(live12=False), {"tau_star": 0.075}, reps=300)
    assert verdict["conditions"]["1_comparability"]["ok"] is True
    assert verdict["label"] == "improves low-degree only"
    assert verdict["conditions"]["4_task"]["ok"] is True


def test_precision_failure_is_named():
    verdict = decide(_cells(precision2=0.90), {"tau_star": 0.075}, reps=300)
    assert verdict["conditions"]["2_high_degree_safety"]["ok"] is True
    assert verdict["label"] == "trades precision for coverage"


def test_no_task_effect_is_named():
    verdict = decide(_cells(gap=0.0), {"tau_star": 0.075}, reps=300)
    assert verdict["label"] == "no task effect"


def test_winning_against_shipped_while_losing_to_the_baseline_is_not_a_task_win():
    """Rule 11/25(a): a win between two arms that both lose to a bigram is no win."""
    verdict = decide(_cells(baseline=0.5), {"tau_star": 0.075}, reps=300)
    assert verdict["conditions"]["4_task"]["baseline_failures"] == [2, 4]
    assert verdict["label"] == "worse than the simple baseline"


def test_missing_shipped_baseline_is_not_comparable():
    verdict = decide(_cells(s_live2=False), {"tau_star": 0.075}, reps=300)
    assert verdict["label"] == "not comparable"


def test_coverage_regression_is_named():
    verdict = decide(_cells(cov_low=0.30), {"tau_star": 0.075}, reps=300)
    assert verdict["conditions"]["2_high_degree_safety"]["ok"] is True
    assert verdict["label"] == "coverage regression"


def test_revision_failure_is_named():
    verdict = decide(_cells(b_low=0.30), {"tau_star": 0.075}, reps=300)
    assert verdict["label"] == "no useful revision"


def test_no_cells_is_not_comparable():
    verdict = decide([], None, reps=100)
    assert verdict["label"] == "not comparable"


# ---------------------------------------------------------------------------
# The seal, and the seed blocks
# ---------------------------------------------------------------------------

def test_the_seal_detects_tampering(tmp_path):
    path = tmp_path / "calibration.json"
    seal({"protocol": True, "tau_star": 0.075, "seeds": [1]}, path)
    assert verify_seal(path)["tau_star"] == 0.075
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["tau_star"] = 0.05
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(SystemExit, match="seal mismatch"):
        verify_seal(path)


def test_the_seed_blocks_are_disjoint_from_each_other_and_from_earlier_work():
    assert not set(CALIBRATION_SEEDS) & set(HELDOUT_SEEDS)
    earlier = harvest_seeds()
    assert not set(CALIBRATION_SEEDS) & earlier
    assert not set(HELDOUT_SEEDS) & earlier


def test_the_grid_and_ladder_are_the_amended_ones():
    assert GRID == (0.05, 0.075, 0.10, 0.15, 0.20, 0.25, 0.30)
    assert DEGREES == (2, 4, 6, 12)
    assert CALIBRATION_SEEDS == tuple(range(20300101, 20300109))
    assert HELDOUT_SEEDS == tuple(range(20300109, 20300129))
