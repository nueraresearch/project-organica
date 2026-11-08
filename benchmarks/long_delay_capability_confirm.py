"""Q051 confirmatory block: ten seeds judged once against the frozen bar.

The design block fixed ``delta`` at 0.0412 from a late-gap sd of 0.0275.
This runner reads that artifact, requires the design gates to have passed,
and applies the frozen decision table with that bar.  No result is re-scored
and no seed is reused.

Cells are persisted per seed under ``docs/capability_confirm/parts`` so the
twenty cells fit inside the command timeout; ``--finish`` loads them, applies
the gates and the classifier, and writes the single artifact.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks.decay_confirmation import harvest_seeds              # noqa: E402
from benchmarks.long_delay_capability import (                      # noqa: E402
    _control,
    _window,
    run_cell,
)
from benchmarks.long_delay_capability_prereg import (               # noqa: E402
    PROTOCOL,
    classify,
    delta,
    seed_live,
    unused_seeds,
    validate,
)

SEEDS = tuple(PROTOCOL["confirm_seeds"])
FACTORS = tuple(PROTOCOL["primary"])
CYCLES = PROTOCOL["cycles"]
EARLY = tuple(PROTOCOL["windows"]["early"])
LATE = tuple(PROTOCOL["windows"]["late"])
PARTS = REPO / "docs" / "capability_confirm" / "parts"
OUT = REPO / "docs" / "long_delay_capability_confirm.json"
DESIGN = REPO / "docs" / "long_delay_capability_design.json"
BOOTSTRAP_SEED = 20302999
BOOTSTRAP_REPS = 10000


def part_path(seed: int, factor: float) -> Path:
    return PARTS / ("%d_%g.json" % (seed, factor))


def measure_seed(seed: int) -> dict:
    PARTS.mkdir(parents=True, exist_ok=True)
    cells = {}
    for factor in FACTORS:
        path = part_path(seed, factor)
        if path.exists():
            part = json.loads(path.read_text(encoding="utf-8"))
        else:
            part = run_cell(seed, factor, CYCLES)
            path.write_text(json.dumps(part), encoding="utf-8")
        cells["%g" % factor] = part
    return {"seed": seed, "cells": cells}


def _interval(values: list[float], reps: int = BOOTSTRAP_REPS) -> list[float]:
    rng = random.Random(BOOTSTRAP_SEED)
    medians = sorted(statistics.median(rng.choices(values, k=len(values)))
                     for _ in range(reps))
    return [round(medians[int(0.025 * reps)], 6),
            round(medians[int(0.975 * reps) - 1], 6)]


def _theories(part: dict, label: str, lo: int, hi: int) -> list[int]:
    rows = part["cells"][label]["rows"]
    return [r["theories"] for r in rows
            if lo <= r["cycle"] < hi and r.get("theories") is not None]


def finish() -> int:
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    if design.get("void") or not all(design.get("gates", {}).values()):
        raise SystemExit("design block did not pass its gates")
    bar = float(design["delta"])
    sd = float(design["late_gap_sd"])
    if abs(bar - delta(sd)) > 1e-6:
        raise SystemExit("design bar does not match the frozen delta rule")

    parts = {}
    for seed in SEEDS:
        cells = {}
        for factor in FACTORS:
            path = part_path(seed, factor)
            if not path.exists():
                raise SystemExit("missing part %s" % path)
            cells["%g" % factor] = json.loads(path.read_text(encoding="utf-8"))
        parts[seed] = {"seed": seed, "cells": cells}

    early, late, gaps, logloss = {}, {}, {}, {}
    summaries = {}
    for seed in SEEDS:
        early[seed], late[seed] = {}, {}
        summaries[str(seed)] = {}
        for factor in FACTORS:
            label = "%g" % factor
            early[seed][label] = _window(parts[seed]["cells"][label]["rows"],
                                          EARLY)
            late[seed][label] = _window(parts[seed]["cells"][label]["rows"],
                                        LATE)
            summaries[str(seed)][label] = {
                "early": early[seed][label],
                "late": late[seed][label],
                "final_theories":
                    parts[seed]["cells"][label]["final_theories"],
                "stream_digest":
                    parts[seed]["cells"][label]["stream_digest"],
            }
        gaps[str(seed)] = {
            "early": round(early[seed]["0.9925"]["mean_recall_at_5"]
                           - early[seed]["0.95"]["mean_recall_at_5"], 6),
            "late": round(late[seed]["0.9925"]["mean_recall_at_5"]
                          - late[seed]["0.95"]["mean_recall_at_5"], 6),
        }
        logloss[str(seed)] = round(
            late[seed]["0.9925"]["mean_log_loss"]
            - late[seed]["0.95"]["mean_log_loss"], 6)

    late_gaps = [gaps[str(seed)]["late"] for seed in SEEDS]
    early_gaps = [gaps[str(seed)]["early"] for seed in SEEDS]
    late_median = round(statistics.median(late_gaps), 6)
    early_median = round(statistics.median(early_gaps), 6)
    late_positive = sum(1 for gap in late_gaps if gap > 0)
    transition_positive = sum(1 for seed in SEEDS
                              if gaps[str(seed)]["late"]
                              > gaps[str(seed)]["early"])
    logloss_values = [logloss[str(seed)] for seed in SEEDS]

    per_arm_early = {
        label: [early[seed][label]["mean_recall_at_5"] for seed in SEEDS]
        for label in ("0.95", "0.9925")
    }

    def arm_live() -> bool:
        for seed in SEEDS:
            shipped = _theories(parts[seed], "0.95", LATE[0], LATE[1])
            survivor = parts[seed]["cells"]["0.9925"]["final_theories"]
            if not shipped or max(shipped) != 0:
                return False
            if survivor is None or survivor <= 0:
                return False
        return True

    gates = {
        "G1_seed_live": seed_live(per_arm_early),
        "G2_arm_live": arm_live(),
        "G3_predictor_live": all(
            late[seed][label]["predictions"] > 0
            for seed in SEEDS for label in ("0.95", "0.9925")),
        "G4_denominator": all(
            early[seed][label]["labels"] > 0 and late[seed][label]["labels"] > 0
            for seed in SEEDS for label in ("0.95", "0.9925")),
        "G5_control": _control(),
        # The design block already consumed its own block; G6 at this stage
        # is the confirmatory half: no confirmatory seed was harvested.
        "G6_seed_disjoint": unused_seeds(harvest_seeds()),
        "G7_digest": validate() == [],
    }
    void = not all(gates.values())

    label = classify(early_gap=early_median,
                     late_gap=late_median,
                     late_positive=late_positive,
                     transition_positive=transition_positive,
                     gates_ok=not void,
                     bar=bar)

    artifact = {
        "kind": "q051_confirmatory_block",
        "date": "2026-11-08",
        "cycles": CYCLES,
        "confirm_seeds": list(SEEDS),
        "factors": list(FACTORS),
        "windows": {"early": list(EARLY), "late": list(LATE)},
        "design_bar": bar,
        "design_sd": sd,
        "cells": summaries,
        "gaps": gaps,
        "late_gap_median": late_median,
        "late_gap_interval": _interval(late_gaps),
        "early_gap_median": early_median,
        "late_positive": late_positive,
        "transition_positive": transition_positive,
        "logloss_gap_median": round(statistics.median(logloss_values), 6),
        "logloss_gap_interval": _interval(logloss_values),
        "gates": gates,
        "void": void,
        "label": label,
        "note": ("Judged once against the frozen bar. Recall@5 is primary; "
                 "log loss is reported only. This is one world family and "
                 "one engine, and it does not license adoption."),
    }
    OUT.write_text(json.dumps(artifact, indent=2), encoding="utf-8")

    print("seed       early gap   late gap   logloss gap")
    for seed in SEEDS:
        print("%-10d %+0.4f      %+0.4f     %+0.4f"
              % (seed, gaps[str(seed)]["early"], gaps[str(seed)]["late"],
                 logloss[str(seed)]))
    print("\nlate median %+0.4f  interval %s  bar %.4f"
          % (late_median, _interval(late_gaps), bar))
    print("early median %+0.4f  late positive %d/10  growth %d/10"
          % (early_median, late_positive, transition_positive))
    print("log loss gap median %+0.4f  interval %s"
          % (statistics.median(logloss_values), _interval(logloss_values)))
    for name, value in gates.items():
        print("%-18s %s" % (name, "PASS" if value else "FAIL"))
    print("\nLABEL: %s" % label)
    return 0 if not void else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int)
    parser.add_argument("--finish", action="store_true")
    args = parser.parse_args(argv)
    if args.seed is not None:
        part = measure_seed(args.seed)
        print("measured seed %d (%d cells)" % (args.seed, len(part["cells"])))
        return 0
    if args.finish:
        return finish()
    parser.error("pass --seed N or --finish")


if __name__ == "__main__":
    raise SystemExit(main())
