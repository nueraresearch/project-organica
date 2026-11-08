"""Q051 design block: five seeds, the seven gates, and the delta calibration.

This is the design block, not the confirmatory block.  It runs the two
primary arms on the five design seeds, checks that the world and the arms
are live, and fixes ``delta`` from the observed late-gap spread.  No
confirmatory seed is read here.

Cells are persisted one seed at a time under
``docs/capability_design/parts`` so the ten cells fit inside the command
timeout; ``--finish`` loads them and writes the single artifact.
"""
from __future__ import annotations

import argparse
import json
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
    seed_live,
    unused_seeds,
    validate,
)
from benchmarks import engine_stamp

SEEDS = tuple(PROTOCOL["design_seeds"])
FACTORS = tuple(PROTOCOL["primary"])
CYCLES = PROTOCOL["cycles"]
EARLY = tuple(PROTOCOL["windows"]["early"])
LATE = tuple(PROTOCOL["windows"]["late"])
PARTS = REPO / "docs" / "capability_design" / "parts"
OUT = REPO / "docs" / "long_delay_capability_design.json"


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
            path.write_text(json.dumps(engine_stamp.stamp(part)), encoding="utf-8")
        cells["%g" % factor] = part
    return {"seed": seed, "cells": cells}


def _theories(part: dict, label: str, lo: int, hi: int) -> list[int]:
    rows = part["cells"][label]["rows"]
    return [r["theories"] for r in rows
            if lo <= r["cycle"] < hi and r.get("theories") is not None]


def finish() -> int:
    parts = []
    for seed in SEEDS:
        cells = {}
        for factor in FACTORS:
            path = part_path(seed, factor)
            if not path.exists():
                raise SystemExit("missing part %s" % path)
            cells["%g" % factor] = json.loads(path.read_text(encoding="utf-8"))
        parts.append({"seed": seed, "cells": cells})

    early, late, gaps = {}, {}, {}
    for part in parts:
        seed = part["seed"]
        early[seed], late[seed] = {}, {}
        for factor in FACTORS:
            label = "%g" % factor
            early[seed][label] = _window(part["cells"][label]["rows"], EARLY)
            late[seed][label] = _window(part["cells"][label]["rows"], LATE)
        gaps[str(seed)] = {
            "early": round(early[seed]["0.9925"]["mean_recall_at_5"]
                           - early[seed]["0.95"]["mean_recall_at_5"], 6),
            "late": round(late[seed]["0.9925"]["mean_recall_at_5"]
                          - late[seed]["0.95"]["mean_recall_at_5"], 6),
        }

    late_gaps = [gaps[str(seed)]["late"] for seed in SEEDS]
    sd = statistics.stdev(late_gaps) if len(late_gaps) > 1 else 0.0
    bar = max(PROTOCOL["delta_floor"],
              PROTOCOL["delta_sd_factor"] * sd)

    per_arm = {
        label: [early[seed][label]["mean_recall_at_5"] for seed in SEEDS]
        for label in ("0.95", "0.9925")
    }

    def arm_live() -> bool:
        for part in parts:
            shipped = _theories(part, "0.95", LATE[0], LATE[1])
            survivor = part["cells"]["0.9925"]["final_theories"]
            if not shipped or max(shipped) != 0:
                return False
            if survivor is None or survivor <= 0:
                return False
        return True

    gates = {
        "G1_seed_live": seed_live(per_arm),
        "G2_arm_live": arm_live(),
        "G3_predictor_live": all(
            late[seed][label]["predictions"] > 0
            for seed in SEEDS for label in ("0.95", "0.9925")),
        "G4_denominator": all(
            early[seed][label]["labels"] > 0 and late[seed][label]["labels"] > 0
            for seed in SEEDS for label in ("0.95", "0.9925")),
        "G5_control": _control(),
        "G6_seed_disjoint": unused_seeds(harvest_seeds()),
        "G7_digest": validate() == [],
    }
    void = not all(gates.values())

    artifact = {
        "kind": "q051_design_block",
        "date": "2026-11-08",
        "cycles": CYCLES,
        "design_seeds": list(SEEDS),
        "factors": list(FACTORS),
        "windows": {"early": list(EARLY), "late": list(LATE)},
        "cells": {str(p["seed"]): p["cells"] for p in parts},
        "gaps": gaps,
        "late_gap_median": round(statistics.median(late_gaps), 6),
        "late_gap_sd": round(sd, 6),
        "delta": round(bar, 6),
        "gates": gates,
        "void": void,
        "note": ("Design block only: the gates and the bar calibration. "
                 "No confirmatory seed is read and no capability claim is made."),
    }
    OUT.write_text(json.dumps(engine_stamp.stamp(artifact), indent=2), encoding="utf-8")

    print("seed       early gap   late gap")
    for seed in SEEDS:
        print("%-10d %+0.4f      %+0.4f"
              % (seed, gaps[str(seed)]["early"], gaps[str(seed)]["late"]))
    print("\nlate median %+0.4f  sd %.4f  delta %.4f"
          % (statistics.median(late_gaps), sd, bar))
    for name, value in gates.items():
        print("%-18s %s" % (name, "PASS" if value else "FAIL"))
    print("\n%s -> %s" % ("DESIGN_GATES_PASS" if not void else "VOID",
                          OUT.relative_to(REPO)))
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
