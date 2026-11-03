"""The Stage B runner: one world, its onset, its eligibility, and its outcome.

What this implements, and nothing else
--------------------------------------
Protocol §4-§7 and the owner's decision record §D13 fix the design. This module is
the executor of that design, not a place to choose it:

* the **world** is the withholding world (`stage_b_stream_withholding.build_world`):
  the scale-stream reconstruction whose declared transition `early_0 -> late_0` is
  refused while the organism is exposed;
* the **predictor** is the confirmed onset of `DI`, the first cycle of the first
  qualifying 10-cycle sustained run, censored rather than placed at a boundary;
* the **outcome** is `revision_held_out`: averaged pairwise log loss of the
  organism's readout on the declared withheld tag pairs that occur in the world's
  own behavioural window, with the readout frozen at onset and no refit during
  evaluation -- the calibrated backoff readout the acquisition harness uses;
* the **eligibility rule** is §4's: a world is eligible iff `onset + 101 <= horizon`,
  so its follow-up is complete inside the world built for it. An ineligible world is
  reported with its onset and horizon and **excluded**, never truncated;
* the **analysis** is §5's: Spearman within configuration, a percentile bootstrap
  over worlds at 98.33 %, the standardised slope beside it, a permutation control,
  and a structural-*size* baseline, with the claim supported only if the predicted
  relation holds with an interval excluding zero in **every** configuration.

The allocation guard is deliberate and is the most important line in the file.

The 720 confirmatory worlds are pre-assigned, **not allocated**. This module refuses
to run a confirmatory seed unless `docs/stage_b_allocation.json` says it has been
allocated, and it refuses the four reserved spares unconditionally. That is not
defensiveness: running a pre-assigned seed is the act that spends the block, and it
belongs to the owner (`docs/DECISION-STAGE-B-SEQUENCE.md` §D2 step 3). A runner that
could silently spend it would make the allocation guard decorative.

Modes
-----
    ./.venv/bin/python -m benchmarks.stage_b_runner --self-test
        No engine, no seed. Checks the guards, the eligibility arithmetic, the
        scoring shape, and that the analysis can both detect a planted relation and
        fail the permutation control. Writes docs/stage_b_runner_self_test.json.

    ./.venv/bin/python -m benchmarks.stage_b_runner --audit
        The degeneracy audit of the world on a consumed design-block seed, through
        the stream module's own audit. No engine.

    ./.venv/bin/python -m benchmarks.stage_b_runner --cell 6:1:20261023
        One design-block world through the engine, to exercise the whole path. This
        is a smoke run on a consumed seed and never a measurement.

    ./.venv/bin/python -m benchmarks.stage_b_runner --all
        The confirmatory block. Refuses unless the seeds are allocated.

The engine is imported and never modified. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks import reusable_knowledge as rk  # noqa: E402
from benchmarks.acquisition_compositional import score as house_score  # noqa: E402
from benchmarks.acquisition_runner import make_organica_backoff  # noqa: E402
from benchmarks.phase_l_campaign import _pairs_from_report as pairs_from_report  # noqa: E402
from benchmarks.stage_b_onset_withholding import onset as sustained_onset  # noqa: E402
from benchmarks.stage_b_onset_withholding import spearman  # noqa: E402
from benchmarks.stage_b_onset_withholding import _available as available  # noqa: E402
from benchmarks.stage_b_onset_withholding import _gold as gold  # noqa: E402
from benchmarks.stage_b_stream_withholding import (  # noqa: E402
    CONFIG_RATIOS, CONFIRMATION_CYCLE, DESIGN_SEEDS, LEARN_CYCLES, TEST_CYCLES,
    build_world, withheld_tag_pairs, window,
)

OUT = ROOT / "docs" / "stage_b_runner.json"
SELF_TEST_OUT = ROOT / "docs" / "stage_b_runner_self_test.json"
CACHE = ROOT / ".scratch" / "stage_b_runner"
ALLOCATION = ROOT / "docs" / "stage_b_allocation.json"

CLAIMED = ("2:1", "3:1", "4:1", "6:1")
BLOCK = {"2:1": (700000001, 700000180), "3:1": (700000181, 700000360),
         "4:1": (700000361, 700000540), "6:1": (700000541, 700000720)}
SPARES = (700000721, 700000724)
PER_CONFIG = 180
SUSTAINED = 10
FOLLOW_UP = LEARN_CYCLES + TEST_CYCLES + 1        # 101, protocol §4
LEVEL = 0.9833                                    # the project's convention
REPS = 10_000
PRNG = 20261107
ALPHA = rk.ALPHA                                  # the frozen readout's alpha
PREDICTED_SIGN = -1                               # earlier onset -> lower log loss

LIMITS = [
    "the readout is the frozen backoff the acquisition harness uses, with its "
    "alpha imported rather than tuned here; no Stage B world was used to fit it",
    "the withheld pair set is the one the world declares, and the behavioural "
    "window is the world's own onset + 1 to + 100, not a fixed cycle number",
    "a world with no withheld pair in its behavioural window is reported as not "
    "measurable and excluded -- never as a zero (AGENTS 13b)",
]


def horizon_cycles(label: str) -> int:
    return CONFIRMATION_CYCLE[label] + LEARN_CYCLES + TEST_CYCLES + 1


def parse_cell(value: str) -> tuple[str, int]:
    """`6:1:20261023` -> (`6:1`, 20261023). The configuration itself has a colon."""
    config, _, seed = value.rpartition(":")
    if config not in CONFIG_RATIOS:
        raise ValueError(f"unknown configuration {config!r}; expected one of {CLAIMED}")
    return config, int(seed)


def seed_block(config: str) -> list[int]:
    first, last = BLOCK[config]
    return list(range(first, last + 1))


def cell_path(config: str, seed: int) -> Path:
    return CACHE / f"cell_{config.replace(':', 'x')}_{seed}.json"


def save_cell(cell: dict) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = cell_path(cell["configuration"], cell["seed"])
    path.write_text(json.dumps(cell, indent=2) + "\n", encoding="utf-8")
    return path


def load_cell(config: str, seed: int) -> dict | None:
    path = cell_path(config, seed)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def cell_is_done(cell: dict | None) -> bool:
    """A cached cell counts only if it finished; a paused one is re-run."""
    return bool(cell) and bool(cell.get("complete"))


def run_many(jobs: list[tuple[str, int]], workers: int = 1,
             budget: float | None = None) -> list[dict]:
    """Run cells, refusing the whole batch BEFORE dispatching if any seed is unallocated.

    The guard is validated for every job first, on purpose: a pool that started and
    then refused would have spent work, and a run that spent anything must have been
    authorised as a whole.
    """
    for _config, seed in jobs:
        assert_runnable(seed)
    done: list[dict] = []
    if workers > 1 and len(jobs) > 1:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(run_cell, config, seed, budget): (config, seed)
                       for config, seed in jobs}
            for future in as_completed(futures):
                cell = future.result()
                save_cell(cell)
                done.append(cell)
                print(f"  {cell['configuration']} {cell['seed']}: onset {cell.get('onset')} "
                      f"outcome {cell.get('outcome')} pid {cell.get('pid')}", flush=True)
    else:
        for config, seed in jobs:
            cell = run_cell(config, seed, budget=budget)
            save_cell(cell)
            done.append(cell)
    return done


def config_of(seed: int) -> str | None:
    for config, (first, last) in BLOCK.items():
        if first <= seed <= last:
            return config
    return None


def allocation() -> dict:
    """The allocation record, or an empty one. Absence means nothing is allocated."""
    if not ALLOCATION.exists():
        return {"allocated": False, "seeds": [], "why": "no allocation record exists"}
    record = json.loads(ALLOCATION.read_text(encoding="utf-8"))
    record.setdefault("allocated", False)
    record.setdefault("seeds", [])
    return record


def assert_runnable(seed: int) -> None:
    """Refuse to spend a seed that has not been allocated. The guard is the point."""
    if seed in DESIGN_SEEDS:          # consumed design-block seeds: smoke runs only
        return
    if SPARES[0] <= seed <= SPARES[1]:
        raise RuntimeError(
            f"seed {seed} is a reserved spare; a spare is never drawn and a censored "
            "world does not release its seed (protocol §10)")
    config = config_of(seed)
    if config is None:
        raise RuntimeError(f"seed {seed} is not in the Stage B block 700000001-700000720")
    if seed not in DESIGN_SEEDS:
        record = allocation()
        if not record["allocated"] or seed not in record["seeds"]:
            raise RuntimeError(
                f"seed {seed} is pre-assigned but NOT allocated: {record.get('why', '')}. "
                "Allocating the block is the owner's act (decision record §D2 step 3), "
                "and a runner that spent a pre-assigned seed would make the guard "
                "decorative")


def eligible(onset: int | None, horizon: int) -> bool:
    return onset is not None and onset + FOLLOW_UP <= horizon


def base_rate(events: list[str]) -> dict[str, float]:
    counts: dict[str, float] = {}
    for event in events:
        for tag in set(event.split()):
            counts[tag] = counts.get(tag, 0.0) + 1.0
    total = sum(counts.values())
    return {tag: (n / total if total else 0.0) for tag, n in counts.items()}


def score_withheld(prob, events: list[str], withheld: set[tuple[str, str]]) -> dict:
    """Mean pairwise log loss on the withheld pairs that occur, and their count.

    The shape is the house scorer's: each context tag is crossed with every target
    tag in the vocabulary, so a negative cell exists for every positive one. The
    contexts are the withheld pairs that occur in the window -- that is the set the
    endpoint is defined on -- and the vocabulary is every tag in the window.
    """
    vocabulary = {tag for event in events for tag in event.split()}
    contexts, observations = [], []
    for i in range(len(events) - 1):
        here, nxt = set(events[i].split()), set(events[i + 1].split())
        for u in here:
            for v in nxt:
                if (u, v) in withheld:
                    contexts.append([u])
                    observations.append([v])
    if not contexts:
        return {"log_loss": None, "cells": 0, "occurrences": 0,
                "measurable": False}
    result = house_score(prob, contexts, observations, vocabulary)
    cells = len(contexts) * len(vocabulary)   # the house scorer's own cell count
    return {"log_loss": round(result["log_loss"], 6), "cells": cells,
            "occurrences": len(contexts), "measurable": True}


def run_cell(config: str, seed: int, budget: float | None = None,
             horizon: int | None = None) -> dict:
    """One world: formation to onset, learning, then the behavioural window."""
    from organica.memory import MemoryService
    from organica.sleep import SleepService

    assert_runnable(seed)
    horizon = horizon or horizon_cycles(config)
    pair = CONFIG_RATIOS[config]
    world = build_world(seed, pair, horizon, withhold=True,
                        withhold_until=CONFIRMATION_CYCLE[config] + LEARN_CYCLES)
    withheld = withheld_tag_pairs()
    events, epc = world["events"], world["events_per_cycle"]
    CACHE.mkdir(parents=True, exist_ok=True)
    db = CACHE / f"runner_{config.replace(':', 'x')}_{seed}.sqlite"
    for suffix in ("", "-wal", "-shm"):
        Path(str(db) + suffix).unlink(missing_ok=True)
    started = time.time()
    di: list[float | None] = []
    mem = MemoryService(db_path=str(db))
    svc = SleepService(mem)
    if hasattr(svc, "_rng"):
        svc._rng.seed(seed)
    # the predictor's definition is the harness's, imported rather than re-derived,
    # so DI here is the same quantity `docs/stage_b_onset_withholding.json` measured
    _early_gold, late_gold = gold(world)
    late_available = available(world, late_gold)
    try:
        # The world's withholding is released on the PLANNED confirmation clock, because
        # the world is generated before any onset is measured. The behavioural window is
        # therefore the protocol's fixed one -- learn 50 cycles after the planned
        # confirmation, then test 50 -- and the eligibility rule is what carries the
        # ordering requirement: an onset after the window opens cannot be paired with an
        # outcome that preceded it. Placing the window at onset + 50 instead empties the
        # scored set, which the smoke run showed before this comment existed.
        planned = CONFIRMATION_CYCLE[config]
        cycle = 0
        confirmation = None
        while cycle < planned + LEARN_CYCLES:
            chunk = events[cycle * epc:(cycle + 1) * epc]
            for event in chunk:
                mem.store(event, event_type="event", source=f"cycle:{cycle}")
            pairs = pairs_from_report(svc.run_sleep_cycle())
            retained = len(pairs & late_gold)
            di.append(round(retained / late_available, 6) if late_available else None)
            confirmation = sustained_onset(di, SUSTAINED)
            cycle += 1
            if budget is not None and time.time() - started > budget:
                return {"configuration": config, "seed": seed, "horizon": horizon,
                        "cycles_run": cycle, "complete": False,
                        "stopped_at_budget": True, "onset": confirmation,
                        "eligible": None, "outcome": None}
        if confirmation is None:
            return {"configuration": config, "seed": seed, "horizon": horizon,
                    "cycles_run": cycle, "complete": True, "stopped_at_budget": False,
                    "onset": None, "censored": True, "eligible": False,
                    "ineligible_because": "no qualifying sustained run",
                    "outcome": None, "di_trajectory": di,
                    "engine_seconds": round(time.time() - started, 2)}
        is_eligible = eligible(confirmation, horizon)
        if not is_eligible:
            return {"configuration": config, "seed": seed, "horizon": horizon,
                    "cycles_run": cycle, "complete": True, "stopped_at_budget": False,
                    "onset": confirmation, "censored": False, "eligible": False,
                    "ineligible_because": "onset does not precede the behavioural "
                                          "window (onset + 101 exceeds the horizon)",
                    "outcome": None, "di_trajectory": di,
                    "engine_seconds": round(time.time() - started, 2)}
        # the readout is frozen here, after the learning window, and never refitted
        rows: dict[str, dict[str, float]] = {}
        for a, b in sorted(pairs):
            rows.setdefault(a, {})
            rows[a][b] = rows[a].get(b, 0.0) + 1.0
        prob = make_organica_backoff(rows, base_rate(window(world, 0, planned)), ALPHA)
        test_events = window(world, planned + LEARN_CYCLES,
                             planned + LEARN_CYCLES + TEST_CYCLES)
        for event in test_events:
            mem.store(event, event_type="event", source="test")
        outcome = score_withheld(prob, test_events, withheld)
        return {"configuration": config, "seed": seed, "horizon": horizon,
                "cycles_run": cycle, "complete": True, "stopped_at_budget": False,
                "pid": os.getpid(),
                "onset": confirmation, "censored": False, "eligible": True,
                "asserted_pairs_at_onset": len(pairs),
                "late_available": late_available,
                "outcome": outcome["log_loss"], "outcome_cells": outcome["cells"],
                "outcome_occurrences": outcome["occurrences"],
                "outcome_measurable": outcome["measurable"],
                "di_trajectory": di,
                "engine_seconds": round(time.time() - started, 2)}
    finally:
        mem.close()
        for suffix in ("", "-wal", "-shm"):
            Path(str(db) + suffix).unlink(missing_ok=True)


def _percentile(values: list[float], level: float) -> tuple[float, float]:
    ordered = sorted(values)
    lo = ordered[int((1.0 - level) / 2.0 * (len(ordered) - 1))]
    hi = ordered[int((1.0 + level) / 2.0 * (len(ordered) - 1))]
    return round(lo, 4), round(hi, 4)


def analyse(cells: list[dict], reps: int = REPS) -> dict:
    """§5's statistics, per configuration, and the conjunction across all four."""
    rng = random.Random(PRNG)
    out: dict[str, dict] = {}
    for config in CLAIMED:
        rows = [c for c in cells if c["configuration"] == config and c.get("complete")]
        scored = [c for c in rows if c.get("eligible") and c.get("outcome") is not None]
        onsets = [c["onset"] for c in scored]
        outcomes = [c["outcome"] for c in scored]
        sizes = [c["asserted_pairs_at_onset"] for c in scored]
        entry = {
            "worlds": len(rows),
            "eligible_scored": len(scored),
            "ineligible": len([c for c in rows if c.get("eligible") is False]),
            "censored": len([c for c in rows if c.get("censored")]),
            "not_measurable": len([c for c in rows
                                   if c.get("eligible") and not c.get("outcome_measurable")]),
            "onset_median": statistics.median(onsets) if onsets else None,
            "spearman": None, "interval": None, "slope": None,
            "permutation_interval": None, "size_spearman": None,
        }
        if len(scored) >= 3:
            rho = spearman(onsets, outcomes)
            entry["spearman"] = rho
            boot = []
            for _ in range(reps):
                pick = [rng.randrange(len(scored)) for _ in scored]
                value = spearman([onsets[i] for i in pick], [outcomes[i] for i in pick])
                if value is not None:
                    boot.append(value)
            entry["interval"] = _percentile(boot, LEVEL) if boot else None
            entry["slope"] = _slope(onsets, outcomes)
            perm = []
            shuffled = list(onsets)
            for _ in range(reps):
                rng.shuffle(shuffled)
                value = spearman(shuffled, outcomes)
                if value is not None:
                    perm.append(value)
            entry["permutation_interval"] = _percentile(perm, LEVEL) if perm else None
            entry["size_spearman"] = spearman(sizes, outcomes)
        interval = entry["interval"]
        if interval is None or entry["spearman"] is None:
            entry["predicted_sign_held"] = False
        elif PREDICTED_SIGN < 0:
            entry["predicted_sign_held"] = bool(interval[1] < 0)
        else:
            entry["predicted_sign_held"] = bool(interval[0] > 0)
        out[config] = entry
    claimed = [c for c in CLAIMED if out[c]["worlds"]]
    held = [c for c in claimed if out[c]["predicted_sign_held"]]
    if not claimed:
        verdict = "NO WORLD RAN"
    elif len(held) == len(claimed) and len(claimed) == len(CLAIMED):
        verdict = "SUPPORTED"
    elif held:
        verdict = "MIXED"
    else:
        verdict = "NOT SUPPORTED"
    return {"by_configuration": out, "verdict": verdict,
            "aggregation_rule": "supported only if the predicted relation holds with "
                                "an interval excluding zero in every claimed "
                                "configuration; otherwise mixed, never a best-configuration "
                                "finding",
            "level": LEVEL, "replicates": reps, "prng_state": PRNG,
            "predicted_sign": "negative: earlier onset predicts a lower held-out log loss"}


def _slope(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3:
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sx = (sum((x - mx) ** 2 for x in xs) / len(xs)) ** 0.5
    sy = (sum((y - my) ** 2 for y in ys) / len(ys)) ** 0.5
    if sx == 0 or sy == 0:
        return None
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / len(xs)
    return round(cov / (sx * sy), 4)


def self_test() -> dict:
    """Guards, eligibility, scoring shape, and an analysis that can pass and fail."""
    checks: dict[str, object] = {}

    # 1. the allocation guard
    try:
        assert_runnable(700000001)
        checks["refuses_an_unallocated_confirmatory_seed"] = False
    except RuntimeError as exc:
        checks["refuses_an_unallocated_confirmatory_seed"] = "NOT allocated" in str(exc)
    try:
        assert_runnable(700000721)
        checks["refuses_a_reserved_spare"] = False
    except RuntimeError as exc:
        checks["refuses_a_reserved_spare"] = "never drawn" in str(exc)
    assert_runnable(DESIGN_SEEDS[0])
    checks["accepts_a_consumed_design_block_seed"] = True

    # 2. the eligibility rule
    checks["eligible_exactly_when_the_follow_up_fits"] = (
        eligible(539, 640) is True and eligible(540, 640) is False
        and eligible(None, 640) is False)

    # 3. the scoring shape: a readout that knows the withheld pair must beat one
    #    that does not, and an empty window must be not-measurable rather than zero
    withheld = {("alpha", "beta")}
    events = ["alpha", "beta", "alpha", "beta"]
    knows = make_organica_backoff({"alpha": {"beta": 10.0}}, {"beta": 0.5}, ALPHA)
    blind = make_organica_backoff({}, {"beta": 0.5}, ALPHA)
    good = score_withheld(knows, events, withheld)
    bad = score_withheld(blind, events, withheld)
    checks["a_readout_that_knows_the_pair_scores_better"] = (
        good["measurable"] and bad["measurable"] and good["log_loss"] < bad["log_loss"])
    empty = score_withheld(knows, ["alpha", "gamma"], withheld)
    checks["an_empty_window_is_not_measurable_not_zero"] = (
        empty["log_loss"] is None and empty["measurable"] is False)

    # 4. the analysis can detect a planted relation, and its permutation control
    #    can fail to find one
    planted = []
    for i in range(40):
        # the predicted direction is negative: later onset, higher log loss
        value = 0.16 - 0.001 * i
        planted.append({"configuration": "2:1", "seed": 1000 + i, "complete": True,
                        "eligible": True, "censored": False, "onset": 100 + i,
                        "asserted_pairs_at_onset": 10,
                        "outcome": value, "outcome_cells": 1, "outcome_occurrences": 1,
                        "outcome_measurable": True})
    found = analyse(planted, reps=200)["by_configuration"]["2:1"]
    checks["detects_a_planted_relation"] = bool(found["predicted_sign_held"])
    checks["permutation_control_includes_zero"] = (
        found["permutation_interval"] is not None
        and found["permutation_interval"][0] <= 0 <= found["permutation_interval"][1])

    flat = [dict(c, outcome=0.5) for c in planted]
    checks["does_not_detect_a_flat_outcome"] = not bool(
        analyse(flat, reps=200)["by_configuration"]["2:1"]["predicted_sign_held"])

    # 5. the conjunction: one configuration short is MIXED, never SUPPORTED
    cells = list(planted)
    for config in ("3:1", "4:1", "6:1"):
        cells += [dict(c, configuration=config) for c in planted]
    checks["all_four_holding_is_supported"] = analyse(cells, reps=100)["verdict"] == "SUPPORTED"
    broken = [c for c in cells if not (c["configuration"] == "6:1")]
    broken += [dict(c, configuration="6:1", outcome=0.5) for c in planted]
    checks["one_configuration_short_is_mixed"] = analyse(broken, reps=100)["verdict"] == "MIXED"

    return {"what_this_is": "The runner's own controls: the allocation guard, the "
                            "eligibility arithmetic, the scoring shape, and an analysis "
                            "that both detects a planted relation and fails to detect a "
                            "flat one. No engine ran and no seed was touched.",
            "checks": checks, "passed": all(bool(v) for v in checks.values()),
            "prng_state": PRNG, "alpha": ALPHA,
            "no_engine": "No engine ran and no Stage B seed was read or written."}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--cell", help="CONFIG:SEED, e.g. 6:1:20261023")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--assemble", action="store_true")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--budget", type=float, default=None)
    args = parser.parse_args(argv)

    if args.self_test:
        result = self_test()
        SELF_TEST_OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        return 0 if result["passed"] else 1

    if args.audit:
        from benchmarks.stage_b_stream_withholding import audit
        result = audit()
        print(json.dumps(result["checks"], indent=2))
        failures = [k for k, v in result["checks"].items()
                    if isinstance(v, bool) and not v]
        return 0 if not failures else 1

    if args.cell:
        config, seed = parse_cell(args.cell)
        cell = None if args.no_cache else load_cell(config, seed)
        if cell is not None:
            print(f"cached: {config} {seed} (use --no-cache to re-run)")
        else:
            cell = run_cell(config, seed, budget=args.budget)
            save_cell(cell)
        print(json.dumps({k: v for k, v in cell.items() if k != "di_trajectory"},
                         indent=2))
        return 0

    if args.assemble:
        cells = [json.loads(p.read_text(encoding="utf-8"))
                 for p in sorted(CACHE.glob("cell_*.json"))]
        result = {"what_this_is": "Stage B cells assembled from the cache, with §5's "
                                  "analysis. No world is generated here.",
                  "cells": cells, "analysis": analyse(cells), "limits": LIMITS}
        OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result["analysis"], indent=2))
        return 0

    if args.all:
        record = allocation()
        if not record["allocated"]:
            print("REFUSED: no seed is allocated. " + str(record.get("why", "")) +
                  " Allocating the block is the owner's act (decision record §D2 step 3).")
            return 2
        jobs = [(config, seed) for config in CLAIMED for seed in seed_block(config)]
        pending = [(config, seed) for config, seed in jobs
                   if not cell_is_done(load_cell(config, seed))]
        print(f"{len(jobs) - len(pending)} cached, {len(pending)} pending, "
              f"{args.workers} worker(s)")
        run_many(pending, workers=args.workers, budget=args.budget)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
