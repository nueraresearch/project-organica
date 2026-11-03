"""Measure the Stage B predictor -- DI onset -- on the world that carries the outcome.

Protocol 3.3 left one question open and named it: the withholding world carries
`held_out_next_tag`, but no `DI` onset has ever been measured on it, so the
predictor's distribution there is unknown. This module measures it, and nothing
else: no outcome is scored, no relation between onset and behaviour is computed.

Per design-block cell it runs the FROZEN engine over the withholding world's
stream and records the per-cycle DI trajectory, then applies the protocol's own
onset rule -- the first cycle of a qualifying sustained run, not the first
non-zero reading -- with the sustention rule at 10 cycles and the 5- and 20-cycle
rules carried beside it as a robustness check. A cell with no qualifying run is
CENSORED, reported as censored, and never placed at a boundary.

The engine is imported and never modified. No Stage B seed is spent: these are
consumed Phase L design-block seeds, regenerated.

A cell costs about two minutes of engine time, so the run is done in rounds and
cached, then assembled -- a single call would outlive the shell's timeout:

    ./.venv/bin/python -m benchmarks.stage_b_onset_withholding --seed-index 0
    ./.venv/bin/python -m benchmarks.stage_b_onset_withholding --seed-index 1
    ./.venv/bin/python -m benchmarks.stage_b_onset_withholding --seed-index 2
    ./.venv/bin/python -m benchmarks.stage_b_onset_withholding --assemble

`--probe N` runs one cell for N cycles and prints only the timing.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.phase_l_campaign import _available  # noqa: E402
from benchmarks.phase_l_campaign import _pairs_from_report as pairs_from_report  # noqa: E402
from benchmarks.stage_b_stream_withholding import (  # noqa: E402
    CONFIRMATION_CYCLE, CONFIG_RATIOS, DESIGN_SEEDS, build_world,
)

OUT = ROOT / "docs" / "stage_b_onset_withholding.json"
CACHE_DIR = ROOT / ".scratch"
LEARN_CYCLES = 50
TEST_CYCLES = 50
SUSTAINED = 10
SUSTENTION_RULES = (5, 10, 20)


def cache_path(label: str, index: int) -> Path:
    return CACHE_DIR / f"onset_cells_{label.replace(':', 'x')}_{index}.json"


def _gold(world) -> tuple[set, set]:
    """The two groups' pairs, rebuilt from the world's own entities.

    `gold_groups` reads `world["gold"]`, which the Phase L generator builds; the
    withholding world returns entities instead, so the same definition is applied
    here: every unordered pair inside one entity's feature set.
    """
    early, late = set(), set()
    for entity in world["entities"]:
        pairs = {tuple(sorted((a, b))) for i, a in enumerate(entity.features)
                 for b in entity.features[i + 1:]}
        if entity.name.startswith("early_"):
            early |= pairs
        elif entity.name.startswith("late_"):
            late |= pairs
    return early, late


def onset(trajectory: list[float | None], sustained: int = SUSTAINED) -> int | None:
    """First cycle of the first qualifying sustained run, or None (censored).

    "Qualifying" means every reading in the run is non-zero -- the construct's
    rule -- and the run must be complete inside the record, so a run cut off by
    the end of the world is censored rather than placed at the boundary.
    """
    n = len(trajectory)
    for start in range(0, n - sustained + 1):
        window = trajectory[start:start + sustained]
        if all(v is not None and v > 0 for v in window):
            return start
    return None


def ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    out = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            out[order[k]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return out


def spearman(a: list[float], b: list[float]) -> float | None:
    if len(a) < 3 or len(a) != len(b):
        return None
    ra, rb = ranks(a), ranks(b)
    ma, mb = statistics.fmean(ra), statistics.fmean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return round(num / den, 4) if den else None


def run_cell(label: str, seed: int, cycles: int | None = None,
             margin: int = 25, budget: float | None = None) -> dict:
    """Run one world until its onset is known, then a margin further.

    The cell stops `margin` cycles after the first qualifying sustained run, because
    the quantity being measured is the onset: running to the full horizon would spend
    minutes per cell learning nothing further about it. A cell with no qualifying run
    runs the whole committed horizon and is CENSORED there. The fields say which
    happened, and `final_di` is the DI at the stop point, not at the end of the
    behavioural window.

    The loop mirrors `phase_l_campaign.organica_run` step for step -- store the
    cycle's chunk, run one sleep cycle, read the asserted pairs -- because the early
    exit has to live inside the loop. The engine is imported, never modified.
    """
    from organica.memory import MemoryService
    from organica.paths import temp_db
    from organica.sleep import SleepService

    ratio = CONFIG_RATIOS[label]
    confirmation = CONFIRMATION_CYCLE[label]
    cycles = cycles if cycles is not None else confirmation + LEARN_CYCLES + TEST_CYCLES + 1
    world = build_world(seed, ratio, cycles, withhold=True,
                        withhold_until=confirmation + LEARN_CYCLES)
    early_gold, late_gold = _gold(world)
    early_available = _available(world, early_gold)
    late_available = _available(world, late_gold)
    events, epc = world["events"], world["events_per_cycle"]
    started = time.time()
    db = temp_db("stage_b_onset.db")
    db.unlink(missing_ok=True)
    mem = MemoryService(db_path=str(db))
    svc = SleepService(mem)
    if hasattr(svc, "_rng"):
        svc._rng.seed(seed)
    di: list[float | None] = []
    cycles_run = 0
    stopped_after_onset = False
    stopped_at_budget = False
    try:
        for cycle in range(cycles):
            chunk = events[cycle * epc:(cycle + 1) * epc]
            for event in chunk:
                mem.store(event, event_type="event", source=f"cycle:{cycle}")
            if not chunk:
                continue
            pairs = pairs_from_report(svc.run_sleep_cycle())
            late_ret = len(pairs & late_gold)
            di.append(round(late_ret / late_available, 6) if late_available else None)
            cycles_run = cycle + 1
            found = onset(di, SUSTAINED)
            if found is not None and cycle >= found + margin:
                stopped_after_onset = True
                break
            if budget is not None and time.time() - started > budget:
                stopped_at_budget = True
                break
    finally:
        mem.close()
        db.unlink(missing_ok=True)
        try:
            db.parent.rmdir()
        except OSError:
            pass
    elapsed = time.time() - started
    onsets = {str(rule): onset(di, rule) for rule in SUSTENTION_RULES}
    return {
        "configuration": label,
        "design_block_cell": seed,
        "horizon_cycles": cycles,
        "cycles_run": cycles_run,
        "stopped_after_onset": stopped_after_onset,
        "stopped_at_budget": stopped_at_budget,
        "confirmation_cycle_used": confirmation,
        "arrival_cycle": world["entities"][3].start,
        "late_available": late_available,
        "early_available": early_available,
        "compensations": world["compensations"],
        "onset_by_sustention_rule": onsets,
        "onset": onsets[str(SUSTAINED)],
        "censored": onsets[str(SUSTAINED)] is None,
        "final_di": di[-1] if di else None,
        "cycles_with_nonzero_di": sum(1 for v in di if v),
        "di_trajectory": di,
        "engine_seconds": round(elapsed, 2),
    }


def run_many(jobs: list[tuple[str, int]], workers: int = 4,
             budget: float | None = None) -> list[dict]:
    cells = []
    if workers > 1 and len(jobs) > 1:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(run_cell, label, seed, None, 25, budget)
                       for label, seed in jobs]
            for done in as_completed(futures):
                cell = done.result()
                cells.append(cell)
                print(f"  {cell['configuration']} {cell['design_block_cell']}: "
                      f"onset {cell['onset']} "
                      f"(rules {cell['onset_by_sustention_rule']}) "
                      f"late_avail {cell['late_available']} "
                      f"{cell['engine_seconds']} s", flush=True)
    else:
        for label, seed in jobs:
            cell = run_cell(label, seed, None, 25, budget)
            cells.append(cell)
            print(f"  {label} {seed}: onset {cell['onset']} "
                  f"(rules {cell['onset_by_sustention_rule']}) "
                  f"late_avail {cell['late_available']} "
                  f"{cell['engine_seconds']} s", flush=True)
    cells.sort(key=lambda c: (list(CONFIG_RATIOS).index(c["configuration"]),
                              DESIGN_SEEDS.index(c["design_block_cell"])))
    return cells


def summarise(cells: list[dict]) -> dict:
    by_config = {label: _summary([c for c in cells if c["configuration"] == label])
                 for label in CONFIG_RATIOS if any(
                     c["configuration"] == label for c in cells)}
    placed = [c for c in cells if c["onset"] is not None]
    rules = {}
    if len(placed) >= 3:
        for a, b in (("5", "10"), ("10", "20"), ("5", "20")):
            x = [c["onset_by_sustention_rule"][a] for c in placed]
            y = [c["onset_by_sustention_rule"][b] for c in placed]
            if all(v is not None for v in x) and all(v is not None for v in y):
                rules[f"{a} vs {b}"] = spearman([float(v) for v in x],
                                                [float(v) for v in y])
            else:
                rules[f"{a} vs {b}"] = None
    medians = [s["median"] for s in by_config.values() if s.get("measurable")]
    checks = {
        "cells": len(cells),
        "cells_with_a_late_structure_available": sum(
            1 for c in cells if c["late_available"] > 0),
        "cells_that_ever_leave_zero": sum(
            1 for c in cells if c["cycles_with_nonzero_di"] > 0),
        "censored_cells": sum(1 for c in cells if c["censored"]),
        "onset_spread_within_configurations": {
            label: s.get("spread") for label, s in by_config.items()},
        "configuration_medians_differ": (max(medians) - min(medians)) if len(medians) > 1 else 0,
        "any_within_configuration_spread": any(
            (s.get("spread") or 0) > 0 for s in by_config.values()),
        "sustention_rule_agreement": rules,
    }
    checks["the_predictor_is_measurable_here"] = (
        checks["cells_with_a_late_structure_available"] == len(cells))
    checks["the_predictor_moves"] = checks["cells_that_ever_leave_zero"] > 0
    checks["onset_varies_within_at_least_one_configuration"] = \
        checks["any_within_configuration_spread"]
    return {
        "what_this_is": "DI onset on the Stage B withholding world, measured with the frozen "
                        "engine on consumed design-block seeds in each claimed configuration. "
                        "It measures the predictor only; no outcome is scored.",
        "why_it_exists": "protocol 3.3: the world that carries `held_out_next_tag` had never had "
                         "its predictor measured, so the run could not start.",
        "predictor": "DI onset under the protocol's rule -- the first cycle of the first "
                     "qualifying sustained run, not the first non-zero reading",
        "sustention_rule_cycles": SUSTAINED,
        "sustention_rules_carried": list(SUSTENTION_RULES),
        "confirmation_cycle_used": CONFIRMATION_CYCLE,
        "cells_are": "consumed Phase L seeds, regenerated; no Stage B seed is spent",
        "checks": checks,
        "configurations": by_config,
        "cells": cells,
        "limits": [
            "design-block seeds per configuration characterise the onset distribution; they are "
            "not the confirmatory block and they authorise nothing",
            "the world is a reconstruction of the scale family, so an onset measured here is "
            "not the Phase L onset and may not be compared with the published medians",
            "the confirmation cycles are the protocol's Phase L medians, used to size each run; "
            "they are not re-derived from these onsets",
            "no relation between onset and any behavioural outcome is computed here, and none "
            "may be read off this artifact",
            "the engine is single-threaded per cell and deterministic per seed, so a cell is not "
            "a replication of itself; these are different seeds, not repeated measurements",
            "a cell stops a margin after its onset, so `final_di` is the DI at the stop point and "
            "not at the end of the behavioural window; a censored cell ran the full horizon",
            "the 5- and 20-cycle rules are evaluated on a trajectory truncated 25 cycles after the "
            "10-cycle onset, so a longer rule can be censored where the shorter one is not",
        ],
    }


def _summary(cells: list[dict]) -> dict:
    placed = [c["onset"] for c in cells if c["onset"] is not None]
    if not placed:
        return {"cells": len(cells), "censored": len(cells), "measurable": False}
    return {
        "cells": len(cells),
        "censored": sum(1 for c in cells if c["censored"]),
        "measurable": True,
        "median": statistics.median(placed),
        "sd": round(statistics.pstdev(placed), 2) if len(placed) > 1 else 0.0,
        "range": [min(placed), max(placed)],
        "spread": max(placed) - min(placed),
        "distinct": len(set(placed)),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-index", type=int, default=None,
                    help="run the four configurations on DESIGN_SEEDS[index]")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--assemble", action="store_true")
    ap.add_argument("--budget", type=float, default=None,
                    help="stop each cell after this many seconds and record where it got to")
    ap.add_argument("--run", type=str, default=None,
                    help="comma-separated cells, e.g. 6:1:0,4:1:0")
    ap.add_argument("--probe", type=int, default=None,
                    help="run one cell for this many cycles and print the timing only")
    args = ap.parse_args()

    if args.probe:
        cell = run_cell("2:1", DESIGN_SEEDS[0], cycles=args.probe)
        per = cell["engine_seconds"] / max(1, args.probe)
        print(f"probe: {args.probe} cycles in {cell['engine_seconds']} s "
              f"({per:.3f} s/cycle); a 640-cycle cell is about {per * 640:.0f} s",
              flush=True)
        return 0

    if args.assemble:
        seen: dict = {}
        for path in sorted(CACHE_DIR.glob("onset_cells_*.json")):
            for cell in json.loads(path.read_text(encoding="utf-8")):
                seen[(cell["configuration"], cell["design_block_cell"])] = cell
        cells = list(seen.values())
        if len(cells) < 4:
            raise SystemExit(f"only {len(cells)} cells cached; run the seed indices first")
        result = summarise(cells)
        OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        c = result["checks"]
        print("checks:", {k: c[k] for k in ("cells", "censored_cells",
                                            "cells_that_ever_leave_zero",
                                            "any_within_configuration_spread",
                                            "configuration_medians_differ")})
        for label, row in result["configurations"].items():
            print(f"  {label}: {row}")
        print("wrote", OUT.relative_to(ROOT))
        return 0

    if args.run:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        jobs = []
        for spec in args.run.split(","):
            label, _, index = spec.rpartition(":")
            if label not in CONFIG_RATIOS or not index.isdigit():
                raise SystemExit(f"bad cell spec {spec!r}")
            jobs.append((label, DESIGN_SEEDS[int(index)]))
        workers = min(args.workers, len(jobs))
        cells = run_many(jobs, workers, args.budget)
        for cell in cells:
            index = DESIGN_SEEDS.index(cell["design_block_cell"])
            path = cache_path(cell["configuration"], index)
            path.write_text(json.dumps([cell], indent=2) + "\n", encoding="utf-8")
            print("cached", path.name, flush=True)
        return 0

    if args.seed_index is not None:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        seed = DESIGN_SEEDS[args.seed_index]
        cells = run_many([(label, seed) for label in CONFIG_RATIOS], args.workers)
        for cell in cells:
            index = DESIGN_SEEDS.index(cell["design_block_cell"])
            path = cache_path(cell["configuration"], index)
            path.write_text(json.dumps([cell], indent=2) + "\n", encoding="utf-8")
            print("cached", path.name, flush=True)
        return 0
    raise SystemExit("choose --run, --seed-index or --assemble")


if __name__ == "__main__":
    raise SystemExit(main())
