"""Why the persistence-off arm serves zero world edges on some seeds.

The treatment zeroes every `precedes` count at the end of each cycle. The engine loads
temporal edges at the start of the next cycle and `_build_predictions` admits only edges
with `PREDICTION_MIN_COUNT = 5`, so a temporal edge must reach 5 observations *inside one
cycle* after the reset. This module does two things for each T1 and T1b seed:

1. replays the store sequence without a sleep cycle and counts the world edges that ever
   reach the floor (the admissibility ceiling);
2. runs the full observer/sleep path for the five zero-S_ever cells and two positive
   controls, and records the world edges actually served.

Both stages are diagnostics on stored seeds. They adjudicate no block and re-score no
cell; the full run is a fresh scratch replay, not a substitute for the frozen cells.

    ./.venv/bin/python -m benchmarks.persistence_zero_diagnostic --check
    ./.venv/bin/python -m benchmarks.persistence_zero_diagnostic --write
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from organica.sleep import SleepService

from benchmarks import engine_stamp
from benchmarks import presence_conversion_repair_observer as observer
from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.acquisition_harness import _CountingMemoryService, _make_scratch_db
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE
from benchmarks.presence_construct_audit import (ACQ_SOURCE, PHASE_ACQUISITION,
                                                 _world_compositional_edges)
from benchmarks.t1_persistence_off_arm import PersistenceOffMemory

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "persistence_zero_served_diagnostic.json"
PAGE = ROOT / "docs" / "PERSISTENCE-ZERO-SERVED-NOTE.md"
KIND = "persistence_zero_served_diagnostic"
FLOOR = 5
BLOCKS = {
    "T1": ROOT / "docs" / "t1_persistence_off_run.json",
    "T1b": ROOT / "docs" / "t1b_persistence_off_run.json",
}
ARMS = ("shipped", "persistence_off")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _loop(world: dict, mem, on_cycle) -> None:
    lo, hi = PHASE_ACQUISITION
    event_lo, event_hi = lo * EVENTS_PER_CYCLE, hi * EVENTS_PER_CYCLE
    for i, (text, train) in enumerate(zip(world["events"], world["trainable"])):
        in_acq = event_lo <= i < event_hi
        if in_acq and not train:
            continue
        if i % EVENTS_PER_CYCLE == 0:
            mem.current_cycle = i // EVENTS_PER_CYCLE
        mem.store(text, event_type="observe", source=ACQ_SOURCE if in_acq else "env")
        if (i + 1) % EVENTS_PER_CYCLE == 0:
            on_cycle()


def replay(seed: int, arm: str, cycles: int = 120) -> dict:
    world = generate_compositional_world(seed=seed, cycles=cycles)
    world_edges = _world_compositional_edges(world)
    db = _make_scratch_db("persistence_zero_diagnostic")
    mem = (PersistenceOffMemory(str(db)) if arm == "persistence_off"
           else _CountingMemoryService(str(db)))
    admissible: set[tuple[str, str]] = set()
    max_world = 0
    cycles_hit = 0

    def on_cycle() -> None:
        nonlocal max_world, cycles_hit
        rows = mem._conn.execute("SELECT tag_from, tag_to, count FROM precedes").fetchall()
        hits = {(a, b) for a, b, count in rows
                if count >= FLOOR and (a, b) in world_edges}
        admissible.update(hits)
        cycles_hit += 1 if hits else 0
        max_world = max([max_world] + [count for a, b, count in rows
                                       if (a, b) in world_edges])
        mem.decay_temporal_edges(factor=0.95, min_count=1)

    try:
        _loop(world, mem, on_cycle)
    finally:
        mem.close()
        db.unlink(missing_ok=True)
    return {"admissible_world_edges": len(admissible), "max_world_count": max_world,
            "cycles_with_admissible": cycles_hit}


def serve(seed: int, arm: str = "persistence_off", cycles: int = 120) -> dict:
    """Run the real observer/sleep path and keep the world edges it served."""
    world = generate_compositional_world(seed=seed, cycles=cycles)
    world_edges = _world_compositional_edges(world)
    db = _make_scratch_db("persistence_zero_diagnostic_serve")
    mem = (PersistenceOffMemory(str(db)) if arm == "persistence_off"
           else _CountingMemoryService(str(db)))
    svc = observer.RepairedObserverSleepService(
        mem, observe=True, cap=SleepService.MAX_PREDICTIONS)
    served: set[tuple[str, str]] = set()
    predictions = 0
    windows = 0

    def on_cycle() -> None:
        nonlocal predictions, windows
        result = svc.run_sleep_cycle()
        pairs = [(p.source, p.target) for p in result.predictions]
        predictions += len(pairs)
        windows += 1
        served.update(edge for edge in pairs if edge in world_edges)

    try:
        _loop(world, mem, on_cycle)
    finally:
        mem.close()
        db.unlink(missing_ok=True)
    return {"served_world_edges": len(served), "windows": windows,
            "predictions_total": predictions, "arm": arm}


def build() -> dict:
    rows = []
    observed = {}
    for block, path in BLOCKS.items():
        art = load(path)
        for cell in art["cells"]:
            observed[(block, cell["seed"], cell["arm"])] = cell["s_ever"]
        for seed in sorted({cell["seed"] for cell in art["cells"]}):
            for arm in ARMS:
                row = {"block": block, "seed": seed, "arm": arm,
                       "observed_s_ever": observed[(block, seed, arm)]}
                row.update(replay(seed, arm))
                rows.append(row)

    zero_off = [row for row in rows if row["arm"] == "persistence_off"
                and row["observed_s_ever"] == 0]
    control_off = []
    for block in BLOCKS:
        block_rows = [row for row in rows if row["block"] == block
                      and row["arm"] == "persistence_off" and row["observed_s_ever"] > 0]
        control_off.append(max(block_rows, key=lambda row: row["observed_s_ever"]))
    serving = []
    for row in zero_off + control_off:
        run = serve(row["seed"], "persistence_off")
        run.update({"block": row["block"], "seed": row["seed"],
                    "observed_s_ever": row["observed_s_ever"]})
        serving.append(run)

    zero_serving = [row for row in serving if row["observed_s_ever"] == 0]
    controls = [row for row in serving if row["observed_s_ever"] > 0]
    finding = (
        "Every zero-S_ever persistence-off cell is a seed on which no world edge reaches "
        "the prediction floor of %d inside a single cycle after the reset: %d such cells, "
        "all with 0 admissible world edges and a maximum observed world-edge count of %s. "
        "The full observer/sleep path confirms it: all %d zero cells serve 0 world edges. "
        "On the %d non-zero cells the admissibility ceiling equals the observed S_ever "
        "exactly (%s), and the two positive controls serve %s world edges. The zero is a "
        "threshold consequence, not a failed measurement: the reset removes the cross-cycle "
        "counts that carry a world edge over the floor, and within-cycle repetition alone "
        "reaches %d only on some seeds."
        % (FLOOR, len(zero_off),
           sorted({row["max_world_count"] for row in zero_off}) or "n/a",
           len(zero_serving),
           len([row for row in rows if row["arm"] == "persistence_off"
                and row["observed_s_ever"] > 0]),
           "; ".join("%s/%s %d=%d" % (row["block"], row["seed"],
                                      row["admissible_world_edges"], row["observed_s_ever"])
                     for row in rows if row["arm"] == "persistence_off"
                     and row["observed_s_ever"] > 0) or "none",
           ", ".join("%s/%s %d" % (row["block"], row["seed"], row["served_world_edges"])
                     for row in controls) or "none", FLOOR))
    return engine_stamp.stamp({
        "kind": KIND, "not_a_result": True,
        "question": ("Why does the persistence-off arm serve zero world edges on some seeds, "
                     "and is the zero a threshold consequence or a failed measurement?"),
        "method": {
            "replay": ("the committed world and store sequence are replayed through the same "
                       "memory service, without running a sleep cycle; counts are read before "
                       "the end-of-cycle decay/reset and the world edges at or above the floor "
                       "are accumulated"),
            "serving": ("the five zero-S_ever cells and the highest-S_ever non-zero cell of each "
                        "block are run through the real observer and sleep cycle at the shipped "
                        "cap; the world edges actually served are counted"),
            "prediction_floor": FLOOR,
            "reset": "PersistenceOffMemory sets every precedes count to 0 after the engine's decay",
            "load_order": ("SleepService.run loads temporal edges at the start of the cycle; the "
                           "reset runs at the end, so the arm reads only within-cycle counts"),
            "lookback": 3,
            "acquisition_filter": "non-trainable events are skipped inside PHASE_ACQUISITION, as in the cells",
        },
        "rows": rows,
        "serving": serving,
        "summary": {
            "zero_s_ever_cells": len(zero_off),
            "zero_cells_have_no_admissible_world_edge": all(
                row["admissible_world_edges"] == 0 for row in zero_off),
            "zero_cells_serve_zero_world_edges": all(
                row["served_world_edges"] == 0 for row in zero_serving),
            "controls_serve_positive_world_edges": all(
                row["served_world_edges"] > 0 for row in controls),
            "nonzero_cells_match_their_ceiling": all(
                row["admissible_world_edges"] == row["observed_s_ever"]
                for row in rows if row["arm"] == "persistence_off"
                and row["observed_s_ever"] > 0),
            "shipped_observed_within_ceiling": all(
                row["observed_s_ever"] <= row["admissible_world_edges"]
                for row in rows if row["arm"] == "shipped"),
            "finding": finding,
        },
        "not_evidence": ("A diagnostic replay and a fresh scratch serving run on stored seeds; it "
                         "adjudicates no block, changes no gate or verdict, and makes no capability "
                         "claim. It explains the zero S_ever cells in T1 and T1b."),
    })


def render(art: dict) -> str:
    lines = [
        "# Why the persistence-off arm serves zero world edges on some seeds",
        "",
        "**Status: diagnostic, not a result.** Generated from "
        "`docs/persistence_zero_served_diagnostic.json` by "
        "`python -m benchmarks.persistence_zero_diagnostic --write`.",
        "",
        "## The mechanism",
        "",
        "`PersistenceOffMemory` zeroes every `precedes` count at the end of each cycle. "
        "`SleepService.run` loads temporal edges at the start of the next cycle, and "
        "`_build_predictions` admits a transition only when `count >= PREDICTION_MIN_COUNT = %d`. "
        "The reset therefore leaves only counts accumulated inside one cycle; a world edge "
        "must be observed at least %d times in that cycle to become a candidate at all."
        % (FLOOR, FLOOR),
        "",
        "## Admissibility replay",
        "",
        "| Block | Seed | Arm | Observed S_ever | Admissible world edges | Max world count | Cycles with one |",
        "| --- | ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in art["rows"]:
        lines.append("| %s | %d | %s | %d | %d | %d | %d |" % (
            row["block"], row["seed"], row["arm"], row["observed_s_ever"],
            row["admissible_world_edges"], row["max_world_count"],
            row["cycles_with_admissible"]))
    lines += [
        "",
        "## Full serving run",
        "",
        "The five zero cells and the highest-`S_ever` non-zero cell of each block were run "
        "through the real observer and sleep cycle on fresh scratch databases. The controls "
        "are present so the check can fail.",
        "",
        "| Block | Seed | Observed S_ever | Served world edges | Windows | Predictions |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in art["serving"]:
        lines.append("| %s | %d | %d | %d | %d | %d |" % (
            row["block"], row["seed"], row["observed_s_ever"],
            row["served_world_edges"], row["windows"], row["predictions_total"]))
    lines += [
        "",
        "## Finding",
        "",
        art["summary"]["finding"],
        "",
        "The replay is a ceiling, not a re-scoring: on the shipped arm the observed `S_ever` "
        "is at or below the admissible set because the cap and ranking still choose among "
        "candidates; on the persistence-off arm the two coincide, so the zero cells are "
        "exactly the seeds where the ceiling is zero. The full serving run confirms the "
        "zero cells serve nothing and the controls serve what the stored cells recorded.",
        "",
        "## What this establishes",
        "",
        "This is a mechanism-level statement for these seeds: cross-cycle accumulation is "
        "required to reach `PREDICTION_MIN_COUNT = 5` within a cycle when the reset removes "
        "the carried counts. It is not evidence that threshold 5 is mis-calibrated. The "
        "measured 3-4 within-cycle ceiling is the next question: topology, tag pattern, "
        "lookback and calibration are untested explanations. Lowering the floor is a "
        "separate intervention, not licensed by this diagnostic.",
        "",
        art["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def problems(art: dict | None = None, page: str | None = None) -> list[str]:
    art = load(ARTIFACT) if art is None else art
    page = PAGE.read_text(encoding="utf-8") if page is None else page
    found: list[str] = []
    if art.get("kind") != KIND:
        found.append("kind")
    if art.get("not_a_result") is not True:
        found.append("the artifact does not say it is not a result")
    rows = art.get("rows") or []
    if len(rows) != 24:
        found.append("the replay does not hold 24 rows (2 blocks x 6 seeds x 2 arms)")
    zero = [row for row in rows if row["arm"] == "persistence_off"
            and row["observed_s_ever"] == 0]
    if not zero:
        found.append("no zero-S_ever cell is recorded")
    for row in zero:
        if row["admissible_world_edges"] != 0:
            found.append("a zero cell has admissible world edges: %s/%s"
                         % (row["block"], row["seed"]))
        if row["max_world_count"] >= FLOOR:
            found.append("a zero cell reached the floor: %s/%s" % (row["block"], row["seed"]))
    for row in rows:
        if row["arm"] == "persistence_off" and row["observed_s_ever"] > 0:
            if row["admissible_world_edges"] != row["observed_s_ever"]:
                found.append("a non-zero off cell's ceiling differs from S_ever: %s/%s"
                             % (row["block"], row["seed"]))
        if row["arm"] == "shipped" and row["observed_s_ever"] > row["admissible_world_edges"]:
            found.append("the shipped arm exceeds its ceiling: %s/%s"
                         % (row["block"], row["seed"]))
    serving = art.get("serving") or []
    if len(serving) != len(zero) + 2:
        found.append("the serving run does not hold the zero cells plus two controls")
    for row in serving:
        if row["served_world_edges"] != row["observed_s_ever"]:
            found.append("the serving run does not match the cell: %s/%s %d != %d"
                         % (row["block"], row["seed"], row["served_world_edges"],
                            row["observed_s_ever"]))
        if row["observed_s_ever"] == 0 and row["served_world_edges"] != 0:
            found.append("a zero cell served world edges: %s/%s"
                         % (row["block"], row["seed"]))
    if serving and not any(row["served_world_edges"] > 0 for row in serving):
        found.append("no positive control served a world edge")
    if page.strip() != render(art).strip():
        found.append("the page does not match the artifact; run --write")
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    if args.write:
        art = build()
        ARTIFACT.write_text(json.dumps(art, indent=1) + "\n", encoding="utf-8")
        PAGE.write_text(render(art), encoding="utf-8")
        print("wrote %s and %s" % (ARTIFACT.relative_to(ROOT).as_posix(), PAGE.relative_to(ROOT).as_posix()))
        print(art["summary"]["finding"])
        return 0
    found = problems()
    for problem in found:
        print("FAIL:", problem)
    if found:
        return 1
    art = load(ARTIFACT)
    print("zero cells: %d, all with no admissible world edge and none served"
          % art["summary"]["zero_s_ever_cells"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
