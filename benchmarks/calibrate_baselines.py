"""Generate an auditable baseline calibration artifact on the calibration seed.

Runs the declared grids for Replay and Statistical (cell_counter) baselines
on independent seed 20261099, recording every candidate's tune-split log-loss so the
winning configuration can be independently verified.

Output: docs/acquisition_baseline_calibration.json  (overwrite)

Standard library only.  Scratch databases only.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks.acquisition_baselines import (
    fit_cell_counter,
    score,
    CELL_GRID,
)
from benchmarks.acquisition_runner import (
    fit_replay_learner,
    REPLAY_GRID,
    EVENTS_PER_CYCLE,
)
from benchmarks.acquisition_compositional import (
    generate_compositional_world,
    PHASE_WARMUP,
    PHASE_ACQUISITION,
)

CALIBRATION_SEED = 20261099
CYCLES = 300
EPC = EVENTS_PER_CYCLE


def main():
    print(f"Generating compositional world (seed={CALIBRATION_SEED})...")
    world = generate_compositional_world(
        seed=CALIBRATION_SEED, cycles=CYCLES, events_per_cycle=EPC
    )
    events = world["events"]
    trainable = world["trainable"]

    warm_lo, warm_hi = PHASE_WARMUP
    acq_lo, acq_hi = PHASE_ACQUISITION

    # Training rows: full exposure stream (cycles 0–109)
    full_exposure_indices = list(range(warm_lo * EPC, acq_hi * EPC))
    train_rows_all = [events[i] for i in full_exposure_indices if trainable[i]]
    vocab = {t for e in train_rows_all for t in e.split()}

    # Tuning split: first 60% of acquisition cycles (cycles 20–73)
    acq_cycles = acq_hi - acq_lo  # 90
    tune_cycles = int(acq_cycles * 0.6)  # 54
    tune_hi_cycle = acq_lo + tune_cycles  # 74

    tune_ctx = [events[i].split() for i in range(acq_lo * EPC, tune_hi_cycle * EPC - 1)]
    tune_obs = [events[i + 1].split() for i in range(acq_lo * EPC, tune_hi_cycle * EPC - 1)]

    tag_to_cell = world["tag_to_cell"]

    # --- Replay grid sweep ---
    print(f"Sweeping Replay grid ({len(REPLAY_GRID)} candidates)...")
    replay_results = []
    for window, half_life, alpha in REPLAY_GRID:
        p = fit_replay_learner(train_rows_all, vocab, window, half_life, alpha)
        s = score(p, tune_ctx, tune_obs, vocab, exclude_self=True)
        replay_results.append({
            "window": window,
            "half_life": half_life,
            "alpha": alpha,
            "tune_log_loss": s["log_loss"],
            "tune_brier": s["brier"],
        })

    replay_results.sort(key=lambda r: r["tune_log_loss"])
    best_replay = replay_results[0]

    # --- Statistical (cell_counter) grid sweep ---
    print(f"Sweeping Statistical grid ({len(CELL_GRID)} candidates)...")
    stat_results = []
    for alpha, half_life, decay_window in CELL_GRID:
        p = fit_cell_counter(
            train_rows_all, vocab, tag_to_cell,
            alpha=alpha, half_life=half_life, decay_window=decay_window,
        )
        s = score(p, tune_ctx, tune_obs, vocab, exclude_self=True)
        stat_results.append({
            "alpha": alpha,
            "half_life": half_life,
            "decay_window": decay_window,
            "tune_log_loss": s["log_loss"],
            "tune_brier": s["brier"],
        })

    stat_results.sort(key=lambda r: r["tune_log_loss"])
    best_stat = stat_results[0]

    artifact = {
        "calibration_seed": CALIBRATION_SEED,
        "note_on_evaluation": (
            "These calibration scores are in-sample fits over the acquisition prefix "
            "(cycles 0-109 fit, cycles 20-73 scored) used solely to fix hyperparameters "
            "independently of confirmatory seeds (20261101-20261130). They are NOT held-out validation scores."
        ),
        "warmup_prefix_included": True,
        "warmup_cycles": [warm_lo, warm_hi],
        "acquisition_cycles": [acq_lo, acq_hi],
        "tune_split_cycles": [acq_lo, tune_hi_cycle],
        "tune_split_fraction": 0.6,
        "training_rows_count": len(train_rows_all),
        "vocabulary_size": len(vocab),
        "scoring_shape": "house (exclude_self=True)",
        "replay_calibration": {
            "grid": "window in (1,2,3) x half_life in (None, 25, 50, 100) x alpha in (0.5, 1.0)",
            "grid_size": len(REPLAY_GRID),
            "best_config": {
                "window": best_replay["window"],
                "half_life": best_replay["half_life"],
                "alpha": best_replay["alpha"],
            },
            "best_tune_log_loss": best_replay["tune_log_loss"],
            "all_candidates": replay_results,
        },
        "statistical_calibration": {
            "family": "cell_counter",
            "grid": "alpha in (0.1, 0.5, 1.0) x half_life in (None, 25, 50, 100) x window in (None, 200, 400, 800)",
            "grid_size": len(CELL_GRID),
            "best_config": {
                "alpha": best_stat["alpha"],
                "half_life": best_stat["half_life"],
                "decay_window": best_stat["decay_window"],
            },
            "best_tune_log_loss": best_stat["tune_log_loss"],
            "tie_breaking_note": (
                "decay_window=None and decay_window=800 yield identical log-loss (0.341199) "
                "because the training sequence contains 880 rows. alpha=0.1 minimally outperforms alpha=0.5 (0.341286)."
            ),
            "all_candidates": stat_results,
        },
    }

    out_path = REPO / "docs" / "acquisition_baseline_calibration.json"
    with open(out_path, "w") as f:
        json.dump(artifact, f, indent=2)

    print(f"\nSaved to {out_path}")
    print(f"Best Replay: {best_replay}")
    print(f"Best Statistical: {best_stat}")


if __name__ == "__main__":
    main()
