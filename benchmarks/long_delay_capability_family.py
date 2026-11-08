"""Calibrate which decay arms survive late in a capability world family.

A family can only carry the Q051 contrast if the shipped arm is dead by
cycle 240 and the comparison arm is still alive at 300.  That is not
guaranteed by construction: ``burst_L1`` introduces a novelty triangle every
30 cycles, and its late survival turns out to be non-monotonic in the decay
factor.  This script measures the four arms and writes the calibration, so a
future protocol can choose a matched pair instead of assuming the lattice
pair transfers.

This is an arm calibration, not a capability result.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks.long_delay_capability import (                      # noqa: E402
    ARMS,
    FAMILIES,
    _window,
    run_cell,
)
from benchmarks import engine_stamp

EARLY = (40, 90)
LATE = (240, 300)


def calibrate(family: str, seed: int, cycles: int) -> dict:
    arms = {}
    for factor in sorted(set(ARMS.values())):
        label = "%g" % factor
        cell = run_cell(seed, factor, cycles, family)
        late_theories = [r["theories"] for r in cell["rows"]
                         if LATE[0] <= r["cycle"] < LATE[1]
                         and r.get("theories") is not None]
        arms[label] = {
            "final_theories": cell["final_theories"],
            "late_theories": {
                "min": min(late_theories) if late_theories else None,
                "max": max(late_theories) if late_theories else None,
            },
            "early": _window(cell["rows"], EARLY),
            "late": _window(cell["rows"], LATE),
            "stream_digest": cell["stream_digest"],
        }
        print("%-8s final %-3s late theories %s"
              % (label, cell["final_theories"],
                 arms[label]["late_theories"]))

    survivors = [label for label, arm in arms.items()
                 if (arm["final_theories"] or 0) > 0]
    return {
        "kind": "capability_family_calibration",
        "date": "2026-11-08",
        "family": family,
        "seed": seed,
        "cycles": cycles,
        "windows": {"early": list(EARLY), "late": list(LATE)},
        "arms": arms,
        "survivors_at_300": survivors,
        "shipped_survives": (arms["0.95"]["final_theories"] or 0) > 0,
        "contrast_ready": ((arms["0.95"]["final_theories"] or 0) == 0
                           and any((arms[label]["final_theories"] or 0) > 0
                                   for label in arms if label != "0.95")),
        "note": ("Arm calibration only; no capability claim. A family carries "
                 "the Q051 contrast only when 0.95 is dead by 240 and the "
                 "comparison arm is alive at 300."),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=FAMILIES, default="burst_L1")
    parser.add_argument("--seed", type=int, default=20302801)
    parser.add_argument("--cycles", type=int, default=300)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    artifact = calibrate(args.family, args.seed, args.cycles)
    out = args.out or (REPO / "docs" / ("long_delay_capability_%s_calibration.json"
                                        % args.family))
    out.write_text(json.dumps(engine_stamp.stamp(artifact), indent=2), encoding="utf-8")
    print("\nsurvivors at 300:", artifact["survivors_at_300"])
    print("contrast ready:", artifact["contrast_ready"])
    print("wrote", out.relative_to(REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
