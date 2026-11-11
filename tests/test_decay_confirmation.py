"""The confirmation harness must be able to fail.

No engine cycles here: these tests exercise the design audit, the per-arm
calibration rule, the sealed artifact, and every branch of the three-arm
conjunctive decision on synthetic cells.  If a gate cannot fire, the protocol is
decoration, so each rejection label has a test that produces it.
"""
from __future__ import annotations
LAYER = "dry-run"  # benchmarks/test_layers.py: the module's execution layer

import json

import pytest

from benchmarks.decay_confirmation import (
    ARMS, CALIBRATION_SEEDS, DEGREES, GRID, HELDOUT_SEEDS,
    audit_worlds, choose_threshold, decide, harvest_seeds, realised_out_degree,
    degree_world, main, seal, verify_seal,
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
# Calibration rule, applied to each strength arm separately
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


def test_the_two_strength_arms_are_calibrated_independently():
    """One arm's cells must not constrain the other's threshold."""
    ratio = [_cal(0.075, 12, coverage=0.8), _cal(0.10, 12, live=False)]
    transition = [_cal(0.05, 12, live=False), _cal(0.075, 12, coverage=0.6)]
    assert choose_threshold(ratio)["tau_star"] == 0.075
    assert choose_threshold(transition)["tau_star"] == 0.075


# ---------------------------------------------------------------------------
# The conjunctive decision, and every rejection it can return
# ---------------------------------------------------------------------------

def _cells(*, live12=True, precision2=1.0, false12=0, gap=0.2, gap_by_seed=None,
           cov_t=0.6, cov_r=0.5, b_low=0.6, s_live2=True, baseline=0.98,
           r_live12=True):
    seeds = list(HELDOUT_SEEDS[:4])
    cells = []
    for i, seed in enumerate(seeds):
        g = gap_by_seed[i] if gap_by_seed else gap
        for degree in DEGREES:
            cells.append({"kind": "stationary", "arm": "transition", "degree": degree,
                          "seed": seed, "liveness": live12 if degree == 12 else True,
                          "stable_final": 20,
                          "precision": precision2 if degree == 2 else 1.0,
                          "coverage": cov_t if degree in (2, 4) else 0.6,
                          "false_assertions": (5 if degree == 2 and precision2 < 1.0 else 0)
                          if degree != 12 else false12,
                          "theories_final": 3})
            cells.append({"kind": "stationary", "arm": "ratio", "degree": degree,
                          "seed": seed, "liveness": r_live12 if degree == 12 else True,
                          "stable_final": 20, "precision": 1.0,
                          "coverage": cov_r if degree in (2, 4) else 0.6,
                          "false_assertions": 0, "theories_final": 3})
            shipped_live = degree in (2, 4) and (s_live2 if degree == 2 else True)
            cells.append({"kind": "stationary", "arm": "shipped", "degree": degree,
                          "seed": seed, "liveness": shipped_live,
                          "stable_final": 20 if shipped_live else 0,
                          "precision": 0.96 if shipped_live else None,
                          "coverage": 0.4 if shipped_live else None,
                          "false_assertions": 0, "theories_final": 3 if shipped_live else 0})
            cells.append({"kind": "task", "arm": "ratio", "degree": degree,
                          "seed": seed, "log_loss": 1.0 + g,
                          "best_baseline_log_loss": baseline})
            cells.append({"kind": "task", "arm": "transition", "degree": degree,
                          "seed": seed, "log_loss": 1.0,
                          "best_baseline_log_loss": baseline})
            cells.append({"kind": "task", "arm": "shipped", "degree": degree,
                          "seed": seed, "log_loss": 1.5,
                          "best_baseline_log_loss": baseline})
    for degree in (4, 12):
        for seed in seeds:
            cells.append({"kind": "shift", "arm": "ratio", "degree": degree,
                          "seed": seed, "b_coverage_final": 0.4,
                          "a_share_final": 0.45})
            cells.append({"kind": "shift", "arm": "transition", "degree": degree,
                          "seed": seed,
                          "b_coverage_final": b_low if degree == 4 else 0.5,
                          "a_share_final": 0.3})
            cells.append({"kind": "shift", "arm": "shipped", "degree": degree,
                          "seed": seed, "b_coverage_final": 0.2,
                          "a_share_final": 0.5})
    return cells


CAL = {"thresholds": {"ratio": 0.075, "transition": 0.075}}


def test_all_conditions_met_adopts():
    verdict = decide(_cells(), CAL, reps=300)
    assert verdict["all_conditions_met"], json.dumps(verdict["conditions"], indent=1)
    assert verdict["label"] == "adopt"
    assert verdict["verdict"] == "ADOPT"


def test_a_gain_the_ratio_control_reproduces_is_not_a_formula_win():
    """The whole point of amendment 4: no credit when the threshold alone does it."""
    verdict = decide(_cells(gap=0.0), CAL, reps=300)
    assert verdict["conditions"]["4_formula_effect"]["ok"] is False
    assert verdict["label"] == "threshold alone suffices"


def test_high_degree_failure_is_named_not_averaged_away():
    verdict = decide(_cells(live12=False), CAL, reps=300)
    assert verdict["conditions"]["1_comparability"]["ok"] is True
    assert verdict["label"] == "improves low-degree only"
    assert verdict["conditions"]["4_formula_effect"]["ok"] is True


def test_precision_failure_is_named():
    verdict = decide(_cells(precision2=0.90), CAL, reps=300)
    assert verdict["conditions"]["2_high_degree_safety"]["ok"] is True
    assert verdict["label"] == "trades precision for coverage"


def test_worse_than_the_best_simple_baseline_is_named():
    verdict = decide(_cells(baseline=0.5), CAL, reps=300)
    assert verdict["conditions"]["4_formula_effect"]["baseline_failures"] == [2, 4]
    assert verdict["label"] == "worse than the simple baseline"


def test_a_missing_baseline_is_not_measurable_rather_than_a_zero():
    cells = [c for c in _cells() if not (c["kind"] == "task"
                                         and c["arm"] == "transition")]
    cells += [{"kind": "task", "arm": "transition", "degree": d, "seed": s,
               "log_loss": 1.0}
              for d in (2, 4) for s in HELDOUT_SEEDS[:4]]
    verdict = decide(cells, CAL, reps=100)
    assert verdict["label"] == "task endpoint not measurable"


def test_no_task_effect_is_named_when_the_interval_spans_zero():
    verdict = decide(_cells(gap_by_seed=[0.6, 0.6, 0.6, -0.4]), CAL, reps=300)
    assert verdict["label"] == "no task effect"


def test_missing_shipped_baseline_is_not_comparable():
    verdict = decide(_cells(s_live2=False), CAL, reps=300)
    assert verdict["label"] == "not comparable"


def test_coverage_regression_is_named():
    verdict = decide(_cells(cov_t=0.30), CAL, reps=300)
    assert verdict["conditions"]["2_high_degree_safety"]["ok"] is True
    assert verdict["label"] == "coverage regression"


def test_revision_failure_is_named():
    verdict = decide(_cells(b_low=0.30), CAL, reps=300)
    assert verdict["label"] == "no useful revision"


def test_no_cells_is_not_comparable():
    verdict = decide([], None, reps=100)
    assert verdict["label"] == "not comparable"


def test_the_boundary_selection_is_recorded_not_inferred():
    """Amendment 5: 0.075 is flagged; a threshold above it is not."""
    assert decide(_cells(), CAL, reps=50)["boundary_selected"] == {
        "ratio": True, "transition": True}
    above = {"thresholds": {"ratio": 0.10, "transition": 0.10}}
    assert decide(_cells(), above, reps=50)["boundary_selected"] == {
        "ratio": False, "transition": False}


# ---------------------------------------------------------------------------
# The seal, and the seed blocks
# ---------------------------------------------------------------------------

def test_the_seal_detects_tampering(tmp_path):
    path = tmp_path / "calibration.json"
    seal({"protocol": True, "thresholds": {"ratio": 0.075, "transition": 0.075}}, path)
    assert verify_seal(path)["thresholds"]["transition"] == 0.075
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["thresholds"]["transition"] = 0.05
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(SystemExit, match="seal mismatch"):
        verify_seal(path)


def test_the_seed_blocks_are_disjoint_from_each_other_and_from_earlier_work():
    assert not set(CALIBRATION_SEEDS) & set(HELDOUT_SEEDS)
    earlier = harvest_seeds()
    assert not set(CALIBRATION_SEEDS) & earlier
    assert not set(HELDOUT_SEEDS) & earlier
    assert len(CALIBRATION_SEEDS) == 8 and len(HELDOUT_SEEDS) == 20
    assert CALIBRATION_SEEDS[-1] < HELDOUT_SEEDS[0]


def test_the_grid_and_arms_are_the_amended_ones():
    assert GRID == (0.05, 0.075, 0.10, 0.15, 0.20, 0.25, 0.30)
    assert DEGREES == (2, 4, 6, 12)
    assert ARMS == ("shipped", "ratio", "transition")


# ---------------------------------------------------------------------------
# CLI plumbing: the guards the campaign will hit before it produces a cell
# ---------------------------------------------------------------------------

def _sealed(tmp_path, thresholds=None, protocol=True, name="calibration.json"):
    path = tmp_path / name
    seal({"protocol": protocol,
          "thresholds": thresholds or {"ratio": 0.075, "transition": 0.075}}, path)
    return path


def test_heldout_refuses_an_unsealed_calibration(tmp_path):
    path = tmp_path / "calibration.json"
    path.write_text(json.dumps({"protocol": True,
                                "thresholds": {"ratio": 0.075, "transition": 0.075}}),
                    encoding="utf-8")
    with pytest.raises(SystemExit, match="seal mismatch"):
        main(["heldout", "--calibration", str(path), "--seeds", "1"])


def test_heldout_refuses_when_an_arm_has_no_threshold(tmp_path):
    path = _sealed(tmp_path, {"ratio": None, "transition": 0.075})
    with pytest.raises(SystemExit, match="selected no threshold"):
        main(["heldout", "--calibration", str(path), "--seeds", "1"])


def test_heldout_refuses_a_seed_that_already_appears_in_the_repository(tmp_path):
    """The scan must fire before any engine cell is created."""
    path = _sealed(tmp_path)
    with pytest.raises(SystemExit, match="already used"):
        main(["heldout", "--calibration", str(path), "--seeds", "20261201"])


def test_calibration_refuses_a_seed_that_already_appears_in_the_repository(tmp_path):
    with pytest.raises(SystemExit, match="already used"):
        main(["calibrate", "--smoke", "--seeds", "20261201", "--degrees", "2",
              "--cycles", "1", "--workers", "1",
              "--out", str(tmp_path / "calibration.json")])


def test_analyze_cli_prints_the_verdict_and_writes_the_out_file(tmp_path, capsys):
    calibration = _sealed(tmp_path)
    heldout = tmp_path / "heldout.json"
    heldout.write_text(json.dumps({"protocol": True, "cells": _cells()}), encoding="utf-8")
    out = tmp_path / "verdict.json"
    code = main(["analyze", "--calibration", str(calibration),
                 "--heldout", str(heldout), "--reps", "100", "--out", str(out)])
    assert code == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["label"] == "adopt"
    assert printed["protocol"] is True
    assert json.loads(out.read_text(encoding="utf-8"))["label"] == "adopt"


def test_analyze_marks_a_smoke_run_and_never_calls_it_a_verdict(tmp_path, capsys):
    calibration = _sealed(tmp_path)
    heldout = tmp_path / "heldout.json"
    heldout.write_text(json.dumps({"protocol": False, "cells": _cells()}), encoding="utf-8")
    main(["analyze", "--calibration", str(calibration),
          "--heldout", str(heldout), "--reps", "100"])
    printed = json.loads(capsys.readouterr().out)
    assert printed["verdict"] == "SMOKE — not a verdict"
    assert printed["protocol"] is False


def test_analyze_refuses_a_missing_held_out_artifact_without_a_traceback(tmp_path):
    calibration = _sealed(tmp_path)
    with pytest.raises(SystemExit, match="no held-out artifact"):
        main(["analyze", "--calibration", str(calibration),
              "--heldout", str(tmp_path / "absent.json")])


def test_analyze_refuses_a_missing_calibration_without_a_traceback(tmp_path):
    heldout = tmp_path / "heldout.json"
    heldout.write_text(json.dumps({"protocol": True, "cells": _cells()}), encoding="utf-8")
    with pytest.raises(SystemExit, match="no artifact at"):
        main(["analyze", "--calibration", str(tmp_path / "absent.json"),
              "--heldout", str(heldout)])


def test_analyze_refuses_an_artifact_without_cells(tmp_path):
    calibration = _sealed(tmp_path)
    heldout = tmp_path / "heldout.json"
    heldout.write_text(json.dumps({"protocol": True}), encoding="utf-8")
    with pytest.raises(SystemExit, match="carries no cell list"):
        main(["analyze", "--calibration", str(calibration), "--heldout", str(heldout)])


def test_analyze_refuses_a_held_out_run_from_another_calibration(tmp_path):
    calibration = _sealed(tmp_path)
    heldout = tmp_path / "heldout.json"
    heldout.write_text(json.dumps({"protocol": True, "cells": _cells(),
                                   "calibration_sha256": "0" * 64}), encoding="utf-8")
    with pytest.raises(SystemExit, match="different calibration"):
        main(["analyze", "--calibration", str(calibration), "--heldout", str(heldout)])


def test_analyze_accepts_a_held_out_run_from_its_own_calibration(tmp_path, capsys):
    calibration = _sealed(tmp_path)
    digest = json.loads(calibration.read_text(encoding="utf-8"))["sha256"]
    heldout = tmp_path / "heldout.json"
    heldout.write_text(json.dumps({"protocol": True, "cells": _cells(),
                                   "calibration_sha256": digest}), encoding="utf-8")
    assert main(["analyze", "--calibration", str(calibration),
                 "--heldout", str(heldout), "--reps", "100"]) == 0
    assert json.loads(capsys.readouterr().out)["label"] == "adopt"


def test_heldout_writes_an_artifact_analyze_accepts(tmp_path, monkeypatch, capsys):
    """The artifact contract, end to end: heldout's own output, then analyze.

    Only the engine pool is stubbed, so this runs in seconds; the seal, the
    threshold hand-off, the recorded calibration hash and the protocol flag are
    all the real code paths.
    """
    import benchmarks.decay_confirmation as dc

    calibration = _sealed(tmp_path)
    monkeypatch.setattr(dc, "_pool",
                        lambda func, tasks, workers, progress=False:
                        [dict(cell) for cell in _cells()])
    out = tmp_path / "heldout.json"
    assert dc.main(["heldout", "--smoke", "--calibration", str(calibration),
                    "--seeds", "20300109", "--workers", "1",
                    "--out", str(out)]) == 0
    artifact = json.loads(out.read_text(encoding="utf-8"))
    assert artifact["calibration_sha256"] == json.loads(
        calibration.read_text(encoding="utf-8"))["sha256"]
    assert artifact["protocol"] is False, "a smoke run must not claim protocol status"
    assert artifact["thresholds"] == {"ratio": 0.075, "transition": 0.075}

    capsys.readouterr()
    assert main(["analyze", "--calibration", str(calibration),
                 "--heldout", str(out), "--reps", "100"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["verdict"] == "SMOKE — not a verdict"
    assert printed["protocol"] is False


def test_a_calibration_that_selects_nothing_stops_the_campaign(tmp_path, monkeypatch):
    """The 2026-11-07 outcome: no tau clears every degree, so no held-out cell may run.

    The stub reproduces the reported shape -- the precision floor rejecting low
    thresholds at low degree, liveness rejecting high ones at high degree -- so
    the intersection is empty and every gate below is the real code path.
    """
    import benchmarks.decay_confirmation as dc

    def no_threshold_clears_every_degree(func, tasks, workers, progress=False):
        cells = []
        for arm, tau, degree, seed, cycles in tasks:
            live = not (degree >= 6 and tau >= 0.20)
            cells.append({"arm": arm, "tau": tau, "degree": degree, "seed": seed,
                          "cycles": cycles, "liveness": live,
                          "precision": 1.0 if tau >= 0.20 else 0.5,
                          "coverage": 0.5})
        return cells

    monkeypatch.setattr(dc, "_pool", no_threshold_clears_every_degree)
    out = tmp_path / "calibration.json"
    code = dc.main(["calibrate", "--smoke", "--seeds", "20300101",
                    "--degrees", "2", "4", "6", "12", "--cycles", "1",
                    "--workers", "1", "--out", str(out)])
    assert code == 1, "a calibration that selects no threshold is a stop, not a success"
    artifact = verify_seal(out)
    assert artifact["thresholds"] == {"ratio": None, "transition": None}
    assert artifact["boundary_selected"] == {"ratio": False, "transition": False}
    for arm in ("ratio", "transition"):
        assert artifact["choices"][arm]["reason"] == \
            "no global threshold clears all degree regimes"
    with pytest.raises(SystemExit, match="selected no threshold"):
        dc.main(["heldout", "--smoke", "--calibration", str(out),
                 "--seeds", "20300109", "--out", str(tmp_path / "heldout.json")])
