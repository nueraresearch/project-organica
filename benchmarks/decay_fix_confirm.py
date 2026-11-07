"""Confirm the degree-invariant strength rule on held-out worlds.

The rule under test lives in the engine (`prediction_strength` in
`organica/sleep_extraction.py`): a prediction's strength is its count relative to
a uniform draw from the same source, scaled so the shipped filter admits exactly
`lift >= 1`. That makes strength degree-invariant and decay-invariant without a
threshold sweep, which is what the 0.12.0 collapse needed and what the
transition-probability candidate could not deliver across degrees
(`docs/DECAY-FIX-CONFIRMATION-PREREGISTRATION.md` section 18).

This harness reads the design from `docs/DECAY-FIX-V2-PREREGISTRATION.md`: the
held-out seed block, the two degree regimes, the control arm and the decision
rule are fixed there before any cell. It reuses the existing confirmation
harness's worlds and counters rather than building new ones, so the comparison
between the engine and the shipped control is the same measurement as before.

    ./.venv/bin/python -m benchmarks.decay_fix_confirm --scan
    ./.venv/bin/python -m benchmarks.decay_fix_confirm --run --degrees 4 12 --seeds 4
    ./.venv/bin/python -m benchmarks.decay_fix_confirm --analyze
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from benchmarks.decay_confirmation import (
    Counted,
    _feed,
    _stable,
    degree_world,
    harvest_seeds,
    temp_db,
    world_edges,
)
from organica.branch_streams import lattice_stream
from organica.memory import MemoryService
from organica.scale_streams import expanding_triangles
from organica.sleep import SleepService

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "docs" / "decay_fix_confirm" / "parts"
RESULT = ROOT / "docs" / "decay_fix_confirm.json"

CYCLES = 300
DEGREES = (6, 12)
SEED_BASE = 20300405
SEED_COUNT = 4
ARMS = ("engine", "shipped")


class EngineArm(Counted):
    """The engine as it now stands, with the layer counters the gate reads."""


class ShippedRatio(Counted):
    """The pre-change formula, restored from the candidate's own evidence.

    The engine computes the lift now, so a control that only set a threshold
    would be measuring the change against itself. This subclass overwrites each
    prediction's strength with the recorded `ratio`, which is the shipped
    `count / source_frequency`, leaving everything else identical.
    """

    def _build_predictions(self, temporal, freqs):
        out = super()._build_predictions(temporal, freqs)
        for cand in out:
            cand.strength = min(1.0, float(cand.evidence.get("ratio", 0.0)))
        return out

# The preregistration's decision rule, restated as constants so the analysis
# cannot drift from it. No value here is computed from the cells it judges.
LIVE_RATE = 0.90
COVERAGE_FLOOR_D12 = 0.50


def held_out_seeds() -> list[int]:
    """The pre-registered block, verified unused on every invocation."""
    claimed = harvest_seeds(ROOT / "docs")
    seeds = list(range(SEED_BASE, SEED_BASE + SEED_COUNT))
    overlap = sorted(set(seeds) & claimed)
    if overlap:
        raise SystemExit(
            "the held-out block overlaps seeds already used under docs/: %s" % overlap
        )
    return seeds


def lattice_world(degree: int) -> list[str]:
    """The matrix's own lattice generator, with the hub's triangles scaled.

    `degree_world` in the older harness builds worlds from `scale_stream`, a
    different family: measured on 2026-11-07, no theory forms in it at any
    degree while stable prediction edges do, so the liveness gate cannot be
    evaluated there. This keeps the generator the 0.12.0 diagnosis and the
    matrix use, and varies only the number of triangles sharing the hub.
    """
    if degree < 2 or degree % 2:
        raise ValueError("degree worlds are even hub out-degrees, got %r" % (degree,))
    triangles = expanding_triangles(degree // 2, hub="alpha")
    return lattice_stream([tuple(tri) for tri in triangles])


def _open(arm: str, events: list[str], seed: int):
    db = temp_db("decay_fix_%s_%s.db" % (arm, seed))
    db.unlink(missing_ok=True)
    memory = MemoryService(db_path=str(db))
    service = ShippedRatio(memory) if arm == "shipped" else EngineArm(memory)
    if hasattr(service, "_rng"):
        service._rng.seed(seed)
    for text in events[:12]:
        memory.store(text, event_type="event", source="seed:bootstrap")
    return db, memory, service


def cell(arm: str, degree: int, seed: int, cycles: int = CYCLES) -> dict:
    events = lattice_world(degree)
    world = world_edges(events)
    db, memory, service = _open(arm, events, seed)
    theories, beliefs = [], []
    stable_final = precision = coverage = 0
    false_assertions = 0
    try:
        for cycle in range(cycles):
            _feed(memory, events, cycle)
            service.run_sleep_cycle()
            stable = _stable(service)
            hit = [edge for edge in stable if edge in world]
            theories.append(getattr(service, "theories", 0))
            beliefs.append(getattr(service, "beliefs", 0))
            stable_final = len(stable)
            precision = (len(hit) / len(stable)) if stable else None
            coverage = (len(hit) / len(world)) if world else None
            false_assertions = len(stable) - len(hit)
    finally:
        memory.close()
        db.unlink(missing_ok=True)

    tail = theories[-max(1, cycles // 10):]
    belief_tail = beliefs[-max(1, cycles // 10):]
    return {
        "arm": arm,
        "degree": degree,
        "seed": seed,
        "cycles": cycles,
        "realised_degree": len({tgt for src, tgt in world if src == "alpha"}),
        "world_edges": len(world),
        "liveness": bool(min(tail) >= 1 and statistics.mean(belief_tail) >= 2),
        "theories_final": theories[-1],
        "beliefs_tail_mean": round(statistics.mean(belief_tail), 3),
        "theory_counts": theories,
        "stable_final": stable_final,
        "precision": precision,
        "coverage": coverage,
        "false_assertions": false_assertions,
    }


def _path(arm: str, degree: int, seed: int) -> Path:
    return PARTS / ("cell_%s_d%d_s%d.json" % (arm, degree, seed))


def run(degrees, seeds, arms) -> int:
    PARTS.mkdir(parents=True, exist_ok=True)
    for arm in arms:
        for degree in degrees:
            for seed in seeds:
                path = _path(arm, degree, seed)
                if path.exists():
                    print("cached", path.name)
                    continue
                row = cell(arm, degree, seed)
                path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
                print(
                    "%-8s d%-3d s%d  live=%-5s theories=%3d stable=%3d coverage=%s"
                    % (
                        arm,
                        degree,
                        seed,
                        row["liveness"],
                        row["theories_final"],
                        row["stable_final"],
                        row["coverage"],
                    )
                )
    return 0


def load_cells() -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(PARTS.glob("cell_*.json"))]


def analyse(cells: list[dict]) -> dict:
    by = {}
    for row in cells:
        by.setdefault((row["arm"], row["degree"]), []).append(row)

    def rate(arm, degree):
        rows = by.get((arm, degree), [])
        return (sum(1 for r in rows if r["liveness"]) / len(rows)) if rows else None

    findings, failures = [], []
    for degree in DEGREES:
        rows = by.get(("engine", degree), [])
        if len(rows) < SEED_COUNT:
            failures.append("degree %d has %d of %d engine cells" % (degree, len(rows), SEED_COUNT))
            continue
        live = rate("engine", degree)
        if live < LIVE_RATE:
            failures.append(
                "engine arm live in %d%% of degree-%d cells, below the %d%% bar"
                % (round(100 * live), degree, round(100 * LIVE_RATE))
            )
        honest = [r for r in rows if r["false_assertions"] == 0]
        if len(honest) / len(rows) < LIVE_RATE:
            failures.append(
                "zero false assertions in %d%% of degree-%d cells"
                % (round(100 * len(honest) / len(rows)), degree)
            )
        coverages = [r["coverage"] for r in rows if r["coverage"] is not None]
        if not coverages:
            failures.append("degree %d produced no stable edges, so coverage is not measurable" % degree)
        else:
            findings.append(
                "degree %d: median coverage %s, median stable %s, live %d/%d"
                % (
                    degree,
                    round(statistics.median(coverages), 3),
                    round(statistics.median([r["stable_final"] for r in rows]), 1),
                    sum(1 for r in rows if r["liveness"]),
                    len(rows),
                )
            )
            if degree == 12 and statistics.median(coverages) < COVERAGE_FLOOR_D12:
                failures.append(
                    "median coverage at degree 12 is below the pre-committed %.2f"
                    % COVERAGE_FLOOR_D12
                )

    shipped = {
        degree: rate("shipped", degree)
        for degree in DEGREES
        if by.get(("shipped", degree))
    }
    return {
        "cells": len(cells),
        "engine_live_rate": {
            "degree %d" % d: rate("engine", d) for d in DEGREES if by.get(("engine", d))
        },
        "shipped_live_rate": {"degree %d" % d: v for d, v in shipped.items()},
        "findings": findings,
        "failures": failures,
        "verdict": "CONFIRMED" if not failures else "NOT CONFIRMED",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scan", action="store_true", help="print the free held-out block")
    parser.add_argument("--run", action="store_true", help="run any missing cells")
    parser.add_argument("--analyze", action="store_true", help="apply the decision rule")
    parser.add_argument("--degrees", type=int, nargs="*", default=list(DEGREES))
    parser.add_argument("--seeds", type=int, nargs="*", default=None)
    parser.add_argument("--arms", nargs="*", default=list(ARMS))
    args = parser.parse_args(argv)

    seeds = args.seeds if args.seeds else held_out_seeds()

    if args.scan:
        print("held-out seeds:", seeds, "degrees:", args.degrees)
        return 0
    if args.run:
        return run(args.degrees, seeds, args.arms)
    if args.analyze:
        report = analyse(load_cells())
        RESULT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        for line in report["findings"]:
            print("finding:", line)
        for line in report["failures"]:
            print("FAIL:", line)
        print("verdict:", report["verdict"])
        return 0 if report["verdict"] == "CONFIRMED" else 1

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
