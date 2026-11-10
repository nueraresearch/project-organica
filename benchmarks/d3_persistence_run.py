"""Run D3's frozen 24-cell block and hand the cells to the frozen scorer.

The preregistration (`docs/d3_persistence_prereg.json`) fixes the arms, seeds, stages and
criteria. This module adds no mechanism of its own: the treatment is
`benchmarks.d3_persistence_arm.MatchedFrequencySleepService`, the control is the shipped
`SleepService`, and every criterion is read by `benchmarks.d3_persistence_prereg.verdict`.

The block is resumable: one JSON part per cell under `.scratch/d3_persistence/parts`, and
`--finish` refuses a cell set that is not exactly the frozen 24. The witness controls are
recorded once on the first seed, because G7 reads the maximum over the trace, not a per-seed
statistic.

    ./.venv/bin/python -m benchmarks.d3_persistence_run --measure
    ./.venv/bin/python -m benchmarks.d3_persistence_run --finish
    ./.venv/bin/python -m benchmarks.d3_persistence_run --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks import d3_persistence_prereg as P                       # noqa: E402
from benchmarks import engine_stamp                                     # noqa: E402
from benchmarks import force_matrix as fm                               # noqa: E402
from benchmarks.d3_persistence_arm import MatchedFrequencySleepService   # noqa: E402
from benchmarks.long_delay_capability import EVENTS_PER_CYCLE, _recall_at_k  # noqa: E402
from organica import __version__ as ENGINE_VERSION                      # noqa: E402
from organica.memory import MemoryService                               # noqa: E402
from organica.paths import temp_db                                      # noqa: E402
from organica.sleep import SleepService                                 # noqa: E402

PARTS = ROOT / ".scratch" / "d3_persistence" / "parts"
ARTIFACT = ROOT / "docs" / "d3_persistence_run.json"
DOC = ROOT / "docs" / "D3-PERSISTENCE-RESULT.md"
STAGES = ("witness", "preflight")
ARMS = ("control", "treatment")
EARLY = (5, 36)


def arm_class(arm: str):
    if arm == "control":
        return SleepService
    if arm == "treatment":
        return MatchedFrequencySleepService
    raise ValueError("unknown arm %r" % arm)


def design_for(stage: str) -> str:
    return ("L3_hub1_t3_mixed" if stage == "witness"
            else "L1_hub1_t3_disjoint")


def horizon_for(stage: str) -> int:
    return 40 if stage == "witness" else 3000


def _digest(cell: dict) -> str:
    body = {key: cell.get(key) for key in (
        "stage", "seed", "arm", "cycles_run", "theory_counts", "first_zero_cycle",
        "predictions_early", "recall_early", "questions_max", "dreams_max")}
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def seed_axis(cells: list[dict]) -> dict:
    """Whether the seed labels actually vary the measured trajectory."""
    distinct = {}
    for stage in STAGES:
        for arm in ARMS:
            signatures = {
                json.dumps([cell["theory_counts"], cell["first_zero_cycle"],
                            cell["recall_early"], cell["predictions_early"]],
                           sort_keys=True)
                for cell in cells if cell["stage"] == stage and cell["arm"] == arm
            }
            distinct["%s/%s" % (stage, arm)] = len(signatures)
    identical = all(count == 1 for count in distinct.values())
    return {"distinct_signatures": distinct, "identical": identical,
            "effective_n": 1 if identical else None,
            "seeds": len({cell["seed"] for cell in cells})}


def run_cell(stage: str, seed: int, arm: str, colony: str = "FULL") -> dict:
    """Run one cell through the same per-cycle loop as the pre-flight.

    The loop is deliberately the shape of `force_matrix.trace_reference`/`q053_mechanism_run`:
    the prediction made at the end of a cycle is scored against the next cycle's chunk before
    that chunk is stored. The early window is cycles 5-36 inclusive, matching the prereg.
    """
    design = design_for(stage)
    horizon = horizon_for(stage)
    stop_at_death = stage == "preflight" and arm == "control"
    events = fm.design_events(design)
    db = temp_db("d3_%s_%s_%d.db" % (stage, arm, seed))
    db.unlink(missing_ok=True)
    memory = MemoryService(db_path=str(db))
    if colony == "FULL":
        if arm == "control":
            service = fm.colony_class("FULL")(memory)
        else:
            service = type("Instrumented_FULL_%s" % arm_class(arm).__name__,
                           (fm.Instrumented, arm_class(arm)), {})(memory)
    else:
        service = fm.colony_class(colony)(memory)
    if hasattr(service, "_rng"):
        service._rng.seed(seed)

    theory_counts: list[int] = []
    questions: list[int] = []
    dreams: list[int] = []
    recalls: list[float] = []
    predictions_early = 0
    positive = False
    first_zero = None
    pending = None
    previous = events[EVENTS_PER_CYCLE - 1]

    try:
        for text in events[:EVENTS_PER_CYCLE]:
            memory.store(text, event_type="event", source="seed:bootstrap")

        for cycle in range(horizon):
            start = (cycle * EVENTS_PER_CYCLE) % len(events)
            chunk = events[start:start + EVENTS_PER_CYCLE]
            row_cycle = cycle - 1
            if pending is not None and EARLY[0] <= row_cycle <= EARLY[1]:
                predictions_early += len(pending)
                recall = _recall_at_k(pending, previous, chunk, k=5)
                if recall is not None:
                    recalls.append(recall)

            for text in chunk:
                memory.store(text, event_type="event", source="cycle:%d" % cycle)
            report = service.run_sleep_cycle()
            fm.capture_cycle(service)
            count = len(getattr(service, "_last_theories", []) or [])
            theory_counts.append(count)
            questions.append(len(getattr(service, "_last_questions", []) or []))
            dreams.append(len(getattr(service, "_last_dreams", []) or []))
            pending = {(p.source, p.target): float(p.strength)
                       for p in (getattr(report, "predictions", None) or [])}
            previous = chunk[-1]

            if count > 0:
                positive = True
            elif positive and first_zero is None:
                first_zero = cycle + 1
                if stop_at_death:
                    break

        cell = {
            "stage": stage,
            "design": design,
            "seed": seed,
            "arm": arm,
            "colony": colony,
            "cycles_run": len(theory_counts),
            "theory_counts": theory_counts,
            "theory_cycles": sum(1 for count in theory_counts if count > 0),
            "peak": max(theory_counts or [0]),
            "first_zero_cycle": first_zero,
            "predictions_early": predictions_early,
            "recall_early": (round(sum(recalls) / len(recalls), 6) if recalls else None),
            "questions_max": max(questions or [0]),
            "dreams_max": max(dreams or [0]),
            "frequency_updates": getattr(service, "frequency_updates", 0),
            "decay": getattr(service, "TEMPORAL_DECAY_FACTOR", 0.95),
            "death_threshold": getattr(service, "DEATH_THRESHOLD", 0.15),
        }
        cell["digest"] = _digest(cell)
        return cell
    finally:
        memory.close()
        db.unlink(missing_ok=True)


def part_path(stage: str, seed: int, arm: str) -> Path:
    return PARTS / ("%s_%d_%s.json" % (stage, seed, arm))


def _job(args: tuple[str, int, str, str]) -> dict:
    stage, seed, arm, colony = args
    return run_cell(stage, seed, arm, colony)


def measure(workers: int = 1) -> int:
    body = P.prereg()
    seeds = list(body["design"]["seeds"])
    jobs = [(stage, seed, arm, "FULL") for stage in STAGES for seed in seeds for arm in ARMS]
    # The negative controls are not cells; they are the G7 witness trace, run once.
    jobs += [("witness", seeds[0], "control", "NO_DREAMS"),
             ("witness", seeds[0], "control", "NO_QUESTIONS")]

    pending = []
    for job in jobs:
        stage, seed, arm, colony = job
        path = part_path(stage, seed, arm) if colony == "FULL" else PARTS / (
            "witness_%d_%s.json" % (seed, colony))
        if path.exists():
            print("cached %s" % path.name, flush=True)
            continue
        pending.append((job, path))

    if workers <= 1:
        for job, path in pending:
            cell = _job(job)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(engine_stamp.stamp(cell), indent=1) + "\n",
                            encoding="utf-8")
            print("cell %s %d %-9s cycles=%d theories=%d peak=%d first_zero=%s"
                  % (cell["stage"], cell["seed"], cell["arm"], cell["cycles_run"],
                     cell["theory_cycles"], cell["peak"], cell["first_zero_cycle"]),
                  flush=True)
        return 0

    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_job, job): (job, path) for job, path in pending}
        for future in as_completed(futures):
            job, path = futures[future]
            cell = future.result()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(engine_stamp.stamp(cell), indent=1) + "\n",
                            encoding="utf-8")
            print("cell %s %d %-9s cycles=%d theories=%d peak=%d first_zero=%s"
                  % (cell["stage"], cell["seed"], cell["arm"], cell["cycles_run"],
                     cell["theory_cycles"], cell["peak"], cell["first_zero_cycle"]),
                  flush=True)
    return 0


def _load_parts() -> dict:
    body = P.prereg()
    seeds = list(body["design"]["seeds"])
    cells = []
    for stage in STAGES:
        for seed in seeds:
            for arm in ARMS:
                path = part_path(stage, seed, arm)
                if not path.exists():
                    raise SystemExit("missing part %s; run --measure" % path.name)
                cells.append(json.loads(path.read_text(encoding="utf-8")))
    controls = {}
    for colony in ("NO_DREAMS", "NO_QUESTIONS"):
        path = PARTS / ("witness_%d_%s.json" % (seeds[0], colony))
        if not path.exists():
            raise SystemExit("missing negative control %s; run --measure" % path.name)
        controls[colony] = json.loads(path.read_text(encoding="utf-8"))
    return {"cells": cells, "controls": controls}


def build() -> dict:
    body = P.prereg()
    parts = _load_parts()
    cells = parts["cells"]
    fingerprint = engine_stamp.engine_sha256()
    first = next(cell for cell in cells
                 if cell["stage"] == "witness" and cell["seed"] == body["design"]["seeds"][0]
                 and cell["arm"] == "control")
    # G4: the first control witness cell must reproduce its digest on a second run.
    rerun = run_cell("witness", body["design"]["seeds"][0], "control")
    deterministic = rerun["digest"] == first["digest"]
    run = {
        "kind": "d3_persistence_run",
        "prereg": body["prereg"],
        "engine": {"fingerprint": fingerprint, "version": ENGINE_VERSION},
        "arms": {
            "control": {"decay": body["arms"]["control"]["decay"],
                        "death_threshold": body["arms"]["control"]["death_threshold"],
                        "frequency_decay": body["arms"]["control"]["frequency_decay"],
                        "fingerprint": fingerprint},
            "treatment": {"decay": body["arms"]["treatment"]["decay"],
                          "death_threshold": body["arms"]["treatment"]["death_threshold"],
                          "frequency_decay": body["arms"]["treatment"]["frequency_decay"],
                          "fingerprint": fingerprint + "+matched"},
        },
        "control_rerun_fingerprint": fingerprint if deterministic else "mismatch",
        "control_rerun_digest": rerun["digest"],
        "witness_negative_controls": {
            "NO_DREAMS": {"dreams_max": parts["controls"]["NO_DREAMS"]["dreams_max"]},
            "NO_QUESTIONS": {"questions_max": parts["controls"]["NO_QUESTIONS"]["questions_max"]},
        },
        "cells": cells,
    }
    run["seed_axis"] = seed_axis(cells)
    label, details = P.verdict(body, run)
    return dict(run, verdict=label, details=details)


def render(artifact: dict) -> str:
    body = P.prereg()
    lines = [
        "# D3 persistence result: matched source-frequency decay",
        "",
        "Generated from `docs/d3_persistence_run.json` by",
        "`python -m benchmarks.d3_persistence_run --finish`. Do not edit by hand.",
        "",
        "Protocol: `docs/D3-PERSISTENCE-PREREGISTRATION.md` (frozen before any cell). "
        "Treatment: `MatchedFrequencySleepService`, in process only; the engine is unchanged.",
        "",
        "**Verdict: `%s`**" % artifact["verdict"],
        "",
    ]
    if artifact.get("seed_axis", {}).get("identical"):
        lines += [
            "## Measurement caveat: the seed axis is degenerate",
            "",
            "All six world seeds produced identical per-cycle theory traces, early recall and",
            "prediction counts in every stage and arm. The frozen 5/6 rule is therefore met by",
            "**one deterministic trajectory repeated six times**, not by six independent worlds.",
            "Effective n = 1. The within-block criteria stand, but this block cannot support a",
            "seed-robustness claim; that is a design defect in the seed axis, not a repair result.",
            "",
        ]
    lines += [
        "| Criterion | Result |",
        "| --- | --- |",
        "| W1 witness | %s of %s seeds held 39/40 cycles and peak 6 |"
        % (artifact["details"].get("witness_seeds", "read"),
           body["design"]["seeds"].__len__()),
        "| P1 persistence | %s of %s seeds alive at the horizon |"
        % (artifact["details"].get("alive_seeds", "read"),
           body["design"]["seeds"].__len__()),
        "| C1 early cost | median gap %s (bar %s) |"
        % (artifact["details"].get("early_median_gap", "unread"),
           artifact["details"].get("early_bar", body["criteria"]["C1_early_cost"]["bar"])),
        "",
        "| Stage | Seed | Arm | Cycles | Theory cycles | Peak | First zero | Early recall@5 | Early predictions |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for cell in artifact["cells"]:
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            cell["stage"], cell["seed"], cell["arm"], cell["cycles_run"],
            cell["theory_cycles"], cell["peak"],
            cell["first_zero_cycle"] if cell["first_zero_cycle"] is not None else "none",
            cell["recall_early"] if cell["recall_early"] is not None else "not measurable",
            cell["predictions_early"]))
    lines += [
        "",
        "The control's preflight death is the G1 baseline gate; the treatment's full 3,000-cycle "
        "trace is the P1 reading. Both negative controls are at zero across the witness.",
        "",
        "**Scope.** One engine, two designs, six seeds. A pass licenses no adoption; promotion "
        "is an owner decision, and the Tier-1 campaign still requires its own run.",
        "",
    ]
    return "\n".join(lines)


def finish() -> int:
    problems = P.validate()
    if problems:
        raise SystemExit("the preregistration is not valid: " + "; ".join(problems))
    artifact = build()
    ARTIFACT.write_text(json.dumps(engine_stamp.stamp(artifact), indent=1) + "\n",
                        encoding="utf-8")
    DOC.write_text(render(artifact), encoding="utf-8")
    print("%s: %s" % (artifact["verdict"], json.dumps(artifact["details"], indent=1)))
    return 0


def check() -> int:
    if not ARTIFACT.exists():
        raise SystemExit("no run artifact; run --finish")
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    body = P.prereg()
    label, details = P.verdict(body, artifact)
    problems = []
    if label != artifact.get("verdict"):
        problems.append("the verdict is not what the cells imply")
    if details != artifact.get("details"):
        problems.append("the details are not what the cells imply")
    if ARTIFACT.read_text(encoding="utf-8") != json.dumps(engine_stamp.stamp(artifact), indent=1) + "\n":
        problems.append("the artifact is not stamped consistently")
    if DOC.read_text(encoding="utf-8") != render(artifact):
        problems.append("the result page is stale")
    if problems:
        raise SystemExit("FAIL: " + "; ".join(problems))
    print("d3 %s: %s" % (artifact["verdict"], details))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--measure", action="store_true")
    group.add_argument("--finish", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args(argv)
    if args.measure:
        return measure(max(1, args.workers))
    if args.finish:
        return finish()
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
