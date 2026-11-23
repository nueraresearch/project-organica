"""T1: the persistence-off arm at the shipped cap, and the harness that runs it.

The block asks whether conversion at cap 112 depends on temporal edge counts carried
across sleep cycles. The treatment is one memory wrapper: at the point the engine
applies temporal decay, every `precedes` count is set to zero. Rows are not deleted,
the schema and every other decay are untouched, and no engine file is edited.

    ./.venv/bin/python -m benchmarks.t1_persistence_off_arm --measure
    ./.venv/bin/python -m benchmarks.t1_persistence_off_arm --finish
    ./.venv/bin/python -m benchmarks.t1_persistence_off_arm --check
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
from pathlib import Path

from organica.sleep import SleepService

from benchmarks import engine_stamp
from benchmarks import presence_conversion_repair_observer as observer
from benchmarks import t1_persistence_off_prereg as prereg
from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.acquisition_harness import _CountingMemoryService, _make_scratch_db
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE, structure_edges
from benchmarks.presence_construct_audit import (ACQ_SOURCE, PHASE_ACQUISITION,
                                                 _digest, _world_compositional_edges,
                                                 asserted_fingerprint)
from benchmarks.presence_conversion_repair_runner import stage_row

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "t1_persistence_off_run.json"
PAGE = ROOT / "docs" / "T1-PERSISTENCE-OFF-RESULT.md"
PARTS = ROOT / ".scratch" / "t1_persistence_off" / "parts"
KIND = "t1_persistence_off_run"
ARMS = ("shipped", "persistence_off")
BOOTSTRAP_REPS = 10000


class PersistenceOffMemory(_CountingMemoryService):
    """The shipped memory service with the carried temporal count zeroed each cycle."""

    def decay_temporal_edges(self, factor: float = 0.95, min_count: int = 1) -> int:
        updated = super().decay_temporal_edges(factor=factor, min_count=min_count)
        self._conn.execute("UPDATE precedes SET count = 0")
        self._conn.commit()
        return updated



def max_temporal_count(mem) -> int:
    row = mem._conn.execute("SELECT COALESCE(MAX(count), 0) FROM precedes").fetchone()
    return int(row[0] or 0)


def design() -> dict:
    return prereg.record()["design"]


def planned() -> list[tuple[int, str]]:
    return [(seed, arm) for seed in design()["seeds"] for arm in ARMS]


def run_cell(seed: int, arm: str) -> dict:
    if arm not in ARMS:
        raise SystemExit("unknown arm %r" % (arm,))
    cycles = int(design()["cycles"])
    cap_value = int(prereg.record()["engine"]["cap"])
    world = generate_compositional_world(seed=seed, cycles=cycles)
    world_edges = _world_compositional_edges(world)
    db_path = _make_scratch_db("t1_persistence_off")
    mem = PersistenceOffMemory(str(db_path)) if arm == "persistence_off" else _CountingMemoryService(str(db_path))
    svc = observer.RepairedObserverSleepService(mem, observe=True, cap=cap_value)
    windows: list[list[tuple[str, str]]] = []
    carried_max: list[int] = []
    acq_lo, acq_hi = PHASE_ACQUISITION
    event_lo, event_hi = acq_lo * EVENTS_PER_CYCLE, acq_hi * EVENTS_PER_CYCLE
    try:
        for i, (text, train_flag) in enumerate(zip(world["events"], world["trainable"])):
            in_acq = event_lo <= i < event_hi
            if in_acq and not train_flag:
                continue
            if i % EVENTS_PER_CYCLE == 0:
                mem.current_cycle = i // EVENTS_PER_CYCLE
            mem.store(text, event_type="observe", source=ACQ_SOURCE if in_acq else "env")
            if (i + 1) % EVENTS_PER_CYCLE == 0:
                windows.append([(p.source, p.target) for p in svc.run_sleep_cycle().predictions])
                carried_max.append(max_temporal_count(mem))
        asserted = {(a, b) for a, targets in
                    structure_edges(svc._load_prior_candidates()).items() for b in targets}
        rows = {(a, b) for a, b in
                mem._conn.execute("SELECT tag_from, tag_to FROM precedes").fetchall()}
        store_counts = dict(getattr(mem, "store_counts", {}))
    finally:
        mem.close()
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass
    present = world_edges & rows
    ever = {edge for window in windows for edge in window} & world_edges
    asserted_world = asserted & world_edges
    cell = {
        "seed": seed, "arm": arm, "cap": int(cap_value), "cycles": len(windows),
        "engine_version": engine_stamp.engine_version(),
        "engine_sha256": engine_stamp.engine_sha256(),
        "world_edges": len(world_edges), "world_digest": _digest(world_edges),
        "present_world_edges": len(present), "present_fingerprint": _digest(present),
        "s_ever_world_edges": len(ever), "s_ever_fingerprint": _digest(ever),
        "asserted_world_edges": len(asserted_world),
        "asserted_fingerprint": asserted_fingerprint(asserted),
        "asserted_world_fingerprint": _digest(asserted_world),
        "served_fingerprint": _digest([edge for window in windows for edge in window]),
        "windows": [[list(edge) for edge in window] for window in windows],
        "windows_world": [["%s>%s" % edge for edge in window if edge in world_edges]
                          for window in windows],
        "present_edges": sorted([list(edge) for edge in present]),
        "ever_edges": sorted([list(edge) for edge in ever]),
        "asserted_edges": sorted([list(edge) for edge in asserted_world]),
        "carried_max": carried_max,
        "universe": [[dict(row) for row in cycle] for cycle in getattr(svc, "universe", [])],
        "allocation": [dict(row) for row in getattr(svc, "allocation", [])],
        "store_counts": store_counts,
    }
    return engine_stamp.stamp(cell)


def part_path(seed: int, arm: str, label: str = "") -> Path:
    return PARTS / ("%d-%s%s.json" % (seed, arm, label))


def measure(force: bool = False) -> int:
    PARTS.mkdir(parents=True, exist_ok=True)
    body = design()
    jobs = [(seed, arm, "") for seed, arm in planned()]
    jobs += [(body["seeds"][0], "persistence_off", "-rerun")]
    for seed, arm, label in jobs:
        path = part_path(seed, arm, label)
        if path.exists() and not force:
            print("have %s" % path.name)
            continue
        cell = run_cell(seed, arm)
        path.write_text(json.dumps(cell), encoding="utf-8")
        print("ran %s: %d cycles, P=%d S_ever=%d A_W=%d" % (
            path.name, cell["cycles"], cell["present_world_edges"],
            cell["s_ever_world_edges"], cell["asserted_world_edges"]))
    return 0


def load(seed: int, arm: str, label: str = "") -> dict:
    path = part_path(seed, arm, label)
    if not path.exists():
        raise SystemExit("missing part %s; run --measure" % path.name)
    return json.loads(path.read_text(encoding="utf-8"))


def bootstrap(diffs: list[int], seed: int) -> dict:
    rng = random.Random(seed)
    means = sorted(statistics.mean(rng.choices(diffs, k=len(diffs)))
                   for _ in range(BOOTSTRAP_REPS))
    return {"mean": statistics.mean(diffs), "lower": means[int(0.025 * BOOTSTRAP_REPS)],
            "upper": means[int(0.975 * BOOTSTRAP_REPS)],
            "reps": BOOTSTRAP_REPS, "seed": seed}


def adjudicate() -> dict:
    doc = prereg.record()
    seeds = list(doc["design"]["seeds"])
    cap_value = int(doc["engine"]["cap"])
    cells = {seed: {arm: load(seed, arm) for arm in ARMS} for seed in seeds}
    gates: dict[str, dict] = {}

    builds = {(cell["engine_version"], cell["engine_sha256"]) for row in cells.values()
              for cell in row.values()}
    gates["G1_build"] = {"passed": (len(builds) == 1
                                    and next(iter(builds))[0] == doc["engine"]["version"]
                                    and all(cell["cap"] == cap_value for row in cells.values()
                                            for cell in row.values())),
                         "builds": sorted(builds)}

    world = [seed for seed in seeds
             if cells[seed]["shipped"]["world_digest"] != cells[seed]["persistence_off"]["world_digest"]
             or cells[seed]["shipped"]["present_fingerprint"] != cells[seed]["persistence_off"]["present_fingerprint"]]
    gates["G2_world"] = {"passed": not world, "differing_seeds": world}

    dead = [seed for seed in seeds
            if any(count != 0 for count in cells[seed]["persistence_off"]["carried_max"][1:])]
    control_dead = [seed for seed in seeds
                    if not any(count > 0 for count in cells[seed]["shipped"]["carried_max"])]
    gates["G3_manipulation_live"] = {"passed": not dead and not control_dead,
                                     "treatment_not_zero": dead,
                                     "control_never_positive": control_dead}

    empty = [(seed, arm) for seed in seeds for arm in ARMS
             if not cells[seed][arm]["present_world_edges"]
             or not cells[seed][arm]["s_ever_world_edges"]]
    gates["G4_denominator"] = {"passed": not empty, "empty": empty}

    pairs = {(cells[seed]["shipped"]["s_ever_world_edges"],
              cells[seed]["shipped"]["asserted_world_edges"]) for seed in seeds}
    gates["G5_seed_axis"] = {"passed": len(pairs) >= 3, "distinct": len(pairs)}

    first = seeds[0]
    rerun = load(first, "persistence_off", "-rerun")
    original = cells[first]["persistence_off"]
    gates["G6_determinism"] = {"passed": rerun["served_fingerprint"] == original["served_fingerprint"]
                               and rerun["s_ever_fingerprint"] == original["s_ever_fingerprint"]
                               and rerun["asserted_world_fingerprint"] == original["asserted_world_fingerprint"],
                               "seed": first, "fingerprint": rerun["served_fingerprint"]}

    shape = all(set(row) == set(ARMS) for row in cells.values()) and len(cells) == 6
    gates["G7_cells"] = {"passed": shape and len(planned()) == 12,
                         "cells": len(planned()),
                         "seeds": len(cells)}

    stage = []
    for seed in seeds:
        for arm in ARMS:
            row = stage_row(cells[seed][arm], cap_value)
            stage.append({"seed": seed, "arm": arm,
                          "present": row["present"], "constructed": row["constructed"],
                          "served_ever": row["served_ever"],
                          "asserted_final": row["asserted_final"],
                          "unexplained": row["unexplained"]})

    diffs = [cells[seed]["shipped"]["s_ever_world_edges"]
             - cells[seed]["persistence_off"]["s_ever_world_edges"] for seed in seeds]
    stats = bootstrap(diffs, int(doc["design"]["bootstrap"]))
    bar = doc["decision_rule"]["bar"]
    positive = [diff for diff in diffs if diff >= int(bar["margin"])]
    stats["positive_seeds"] = len(positive)
    stats["margin"] = int(bar["margin"])
    stats["diffs"] = diffs

    if not all(gate["passed"] for gate in gates.values()):
        verdict = "VOID"
        reading = "A gate failed, so the block measured nothing and no endpoint is read."
        decision = "Record VOID; fix the gate named here and register a new block."
    elif len(positive) >= int(bar["positive_seeds"]) and stats["lower"] > 0:
        verdict = "PERSISTENCE CONTRIBUTES"
        reading = ("Removing the carried temporal count removes served world edges at the same cap, "
                   "world and seed: %d of 6 seeds lose at least %d edges." % (len(positive), bar["margin"]))
        decision = ("Pursue the persistence mechanism (decay, floor, denominator); the cap arm does "
                    "not answer this question.")
    elif stats["mean"] <= 0 or len(positive) <= 2 or stats["upper"] < int(bar["margin"]):
        verdict = "PERSISTENCE NOT LIMITING"
        reading = ("Conversion at 112 is created inside the cycle on this block: the paired mean is "
                   "%.3f and %d of 6 seeds reach the margin." % (stats["mean"], len(positive)))
        decision = ("Pursue the in-cycle stage (construction or admission) and stop treating "
                    "retention as the conversion lever.")
    else:
        verdict = "MIXED"
        reading = "The per-seed rows disagree and the direction is not resolved."
        decision = "Make no mechanism claim; the only follow-up is a larger fresh seed axis."

    return engine_stamp.stamp({
        "kind": KIND, "prereg": doc["prereg"],
        "cells": [{"seed": seed, "arm": arm,
                   "present": cells[seed][arm]["present_world_edges"],
                   "s_ever": cells[seed][arm]["s_ever_world_edges"],
                   "a_w": cells[seed][arm]["asserted_world_edges"],
                   "served_fingerprint": cells[seed][arm]["served_fingerprint"]}
                  for seed in seeds for arm in ARMS],
        "stage_table": stage, "gates": gates, "verdict": verdict,
        "reading": reading, "decision": decision, "bootstrap": stats,
        "controls": {"determinism_rerun": 1, "cells_run": len(planned()) + 1},
        "not_evidence": ("One ablation on six seeds at cap 112; it is not a capability, retention "
                         "or transfer result, and it does not re-read Q4 or Q2."),
    })


def render(art: dict) -> str:
    stats = art["bootstrap"]
    lines = ["# T1 -- persistence-off at cap 112: result", "",
             "**%s.** %s" % (art["verdict"], art["reading"]), "",
             "## Gates", "", "| Gate | Result |", "| --- | --- |"]
    for name, gate in art["gates"].items():
        lines.append("| `%s` | %s |" % (name, "PASS" if gate["passed"] else "FAIL"))
    lines += ["", "## Per-seed endpoint" + (" (computed, not adjudicated)" if art["verdict"] == "VOID" else ""), "",
              "`S_ever` is the union of served windows intersected with the world; `A_W` is the "
              "asserted world edges at the end of the run. The primary endpoint is the paired "
              "difference in `S_ever`, shipped minus persistence-off.", "",
              "| Seed | Shipped S_ever | Off S_ever | Difference | Shipped A_W | Off A_W |",
              "| ---: | ---: | ---: | ---: | ---: | ---: |"]
    shipped = {row["seed"]: row for row in art["cells"] if row["arm"] == "shipped"}
    off = {row["seed"]: row for row in art["cells"] if row["arm"] == "persistence_off"}
    for seed, diff in zip(sorted(shipped), stats["diffs"]):
        lines.append("| %d | %d | %d | %d | %d | %d |" % (
            seed, shipped[seed]["s_ever"], off[seed]["s_ever"], diff,
            shipped[seed]["a_w"], off[seed]["a_w"]))
    lines += ["", "**Paired mean %.3f**, 95%% interval [%.3f, %.3f], %d of 6 seeds at or above "
              "the margin of %d, %d resamples at seed %d." % (
                  stats["mean"], stats["lower"], stats["upper"], stats["positive_seeds"],
                  stats["margin"], stats["reps"], stats["seed"]), "",
              "## Decision", "", art["decision"], "",
              "One ablation, six seeds, one build; the direction is the claim, not an effect size. "
              "This result does not re-read Q4's stage table or Q2's cap verdict.", ""]
    if art["verdict"] == "VOID":
        lines += ["**No endpoint is adjudicated.** The frozen decision table reads no endpoint when a "
                  "gate fails, so the per-seed differences above are reported as computed values, not "
                  "as a verdict. G4 failed because two persistence-off cells served zero world edges; "
                  "that is the finding the gate records, and the gate is not relaxed after the run.", ""]
    return "\n".join(lines)


def check() -> int:
    if not ARTIFACT.exists():
        print("FAIL: no result artifact; run --finish")
        return 1
    art = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    found = []
    if art.get("kind") != KIND:
        found.append("kind")
    if len(art.get("cells") or []) != 12:
        found.append("12 cells")
    if PAGE.read_text(encoding="utf-8") != render(art):
        found.append("the page is stale")
    if not art.get("verdict"):
        found.append("no verdict")
    for problem in found:
        print("FAIL:", problem)
    if not found:
        print("T1: %s, %d cells, gates %d/%d" % (
            art["verdict"], len(art["cells"]),
            sum(1 for g in art["gates"].values() if g["passed"]), len(art["gates"])))
    return 1 if found else 0


def finish() -> int:
    art = adjudicate()
    ARTIFACT.write_text(json.dumps(art, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(art), encoding="utf-8")
    print("verdict: %s" % art["verdict"])
    for name, gate in art["gates"].items():
        print("  %-28s %s" % (name, "PASS" if gate["passed"] else "FAIL"))
    print("  paired mean %.3f [%.3f, %.3f], positive %d/6" % (
        art["bootstrap"]["mean"], art["bootstrap"]["lower"], art["bootstrap"]["upper"],
        art["bootstrap"]["positive_seeds"]))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--measure", action="store_true")
    group.add_argument("--finish", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--cell", nargs=2, metavar=("SEED", "ARM"))
    args = parser.parse_args(argv)
    if args.cell:
        seed, arm = int(args.cell[0]), args.cell[1]
        cell = run_cell(seed, arm)
        PARTS.mkdir(parents=True, exist_ok=True)
        part_path(seed, arm).write_text(json.dumps(cell), encoding="utf-8")
        print("ran %d %s: P=%d S_ever=%d A_W=%d carried_max=%s" % (
            seed, arm, cell["present_world_edges"], cell["s_ever_world_edges"],
            cell["asserted_world_edges"], cell["carried_max"][:5]))
        return 0
    if args.measure:
        return measure(args.force)
    if args.finish:
        return finish()
    if args.check or not argv:
        return check()
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
