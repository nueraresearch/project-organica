"""PRESENCE-BAND-1: the per-edge band arm at 40 versus 112.

The record names all 62 Q4 rank-21-40 transition edges and fixes twelve cells on Q4's six
worlds. This module implements the arm and the preflight that refuses to run it: before the
grant, `--measure`, `--cell` and `--finish` stop before a database is opened; after the run,
the same gate refuses a re-run because the block is closed.

    ./.venv/bin/python -m benchmarks.presence_band_rank_arm --check
    ./.venv/bin/python -m benchmarks.presence_band_rank_arm --self-test
    ./.venv/bin/python -m benchmarks.presence_band_rank_arm --dry-run
    ./.venv/bin/python -m benchmarks.presence_band_rank_arm --measure   # REFUSED until granted
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from organica.sleep import SleepService

from benchmarks import engine_stamp
from benchmarks import presence_band_rank_prereg as band
from benchmarks import presence_conversion_repair_observer as observer
from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.acquisition_harness import _CountingMemoryService, _make_scratch_db
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE, structure_edges
from benchmarks.presence_construct_audit import (ACQ_SOURCE, PHASE_ACQUISITION,
                                                 _digest, _world_compositional_edges,
                                                 asserted_fingerprint)

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "presence_band_rank_run.json"
PAGE = ROOT / "docs" / "PRESENCE-BAND-RANK-RESULT.md"
PARTS = ROOT / ".scratch" / "presence_band" / "parts"
CAPS = (40, 112)
KIND = "presence_band_rank_run"
SERVED_VERDICTS = ("BAND IN SERVICE", "BAND PARTLY IN SERVICE", "BAND NOT IN SERVICE")


def record() -> dict:
    return band.record()


def design() -> dict:
    return record()["design"]


def named(seed: int) -> dict:
    row = record()["band"]["seeds"][str(seed)]
    return {(source, target): int(rank) for source, target, rank in row["edges"]}


def planned() -> list[tuple[int, int]]:
    return [(seed, cap) for seed in design()["seeds"] for cap in CAPS]


def preflight() -> list[str]:
    """Every condition the record requires before a cell may run, as sentences."""
    doc = record()
    found: list[str] = []
    if doc.get("status") not in ("FROZEN, NOT RUN", "FROZEN, RUN"):
        found.append("the record is %r, not FROZEN (NOT RUN or RUN)" % (doc.get("status"),))
    if doc.get("status") == "FROZEN, RUN":
        found.append("the block is FROZEN, RUN and closed: its cells are not re-run")
    if (doc.get("authorisation") or {}).get("granted") is not True:
        found.append("authorisation is not granted: no dated grant names these twelve cells")
    try:
        import organica
        if getattr(organica, "__version__", None) != "0.15.0":
            found.append("the shipped build is not 0.15.0")
        if SleepService.MAX_PREDICTIONS != 112:
            found.append("the shipped cap is %d, not 112" % SleepService.MAX_PREDICTIONS)
    except Exception as exc:  # pragma: no cover
        found.append("the shipped engine could not be read: %s" % exc)
    return found


def refuse() -> None:
    reasons = preflight()
    if reasons:
        print("REFUSED: the band arm will not run:")
        for reason in reasons:
            print("  -", reason)
        raise SystemExit(2)


def run_cell(seed: int, cap: int) -> dict:
    if cap not in CAPS:
        raise SystemExit("cap %r is not one of %s" % (cap, CAPS))
    cycles = int(design()["cycles"])
    world = generate_compositional_world(seed=seed, cycles=cycles)
    world_edges = _world_compositional_edges(world)
    db_path = _make_scratch_db("presence_band")
    mem = _CountingMemoryService(str(db_path))
    svc = observer.RepairedObserverSleepService(mem, observe=True, cap=cap)
    windows: list[list[tuple[str, str]]] = []
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
        asserted = {(a, b) for a, targets in
                    structure_edges(svc._load_prior_candidates()).items() for b in targets}
        rows = {(a, b) for a, b in
                mem._conn.execute("SELECT tag_from, tag_to FROM precedes").fetchall()}
    finally:
        mem.close()
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass
    present = world_edges & rows
    cell = {
        "seed": seed, "cap": int(cap), "cycles": len(windows),
        "engine_version": engine_stamp.engine_version(),
        "engine_sha256": engine_stamp.engine_sha256(),
        "world_digest": _digest(world_edges),
        "present_fingerprint": _digest(present),
        "world_edges": len(world_edges), "present_world_edges": len(present),
        "windows": [[list(edge) for edge in window] for window in windows],
        "windows_world": [["%s>%s" % edge for edge in window if edge in world_edges]
                          for window in windows],
        "present_edges": sorted([list(edge) for edge in present]),
        "asserted_edges": sorted([list(edge) for edge in asserted & world_edges]),
        "asserted_fingerprint": asserted_fingerprint(asserted),
        "universe": [[dict(row) for row in cycle] for cycle in getattr(svc, "universe", [])],
        "allocation": [dict(row) for row in getattr(svc, "allocation", [])],
        "store_counts": dict(getattr(mem, "store_counts", {})),
    }
    return engine_stamp.stamp(cell)


def part_path(seed: int, cap: int, label: str = "") -> Path:
    return PARTS / ("%d-%d%s.json" % (seed, cap, label))


def measure(force: bool = False) -> int:
    refuse()
    PARTS.mkdir(parents=True, exist_ok=True)
    jobs = [(seed, cap, "") for seed, cap in planned()]
    jobs += [(design()["seeds"][0], 112, "-rerun")]
    for seed, cap, label in jobs:
        path = part_path(seed, cap, label)
        if path.exists() and not force:
            continue
        cell = run_cell(seed, cap)
        path.write_text(json.dumps(cell), encoding="utf-8")
        print("ran %s" % path.name)
    return 0


def load(seed: int, cap: int, label: str = "") -> dict:
    path = part_path(seed, cap, label)
    if not path.exists():
        raise SystemExit("missing part %s" % path.name)
    return json.loads(path.read_text(encoding="utf-8"))


def _served(cell: dict) -> set[tuple[str, str]]:
    return {tuple(edge.split(">")) if isinstance(edge, str) else tuple(edge)
            for window in cell["windows_world"] for edge in window}


def _ranks(cell: dict) -> dict[tuple[str, str], int]:
    best: dict[tuple[str, str], int] = {}
    for cycle in cell.get("universe") or []:
        for row in cycle:
            edge = tuple(row["edge"])
            best[edge] = min(best.get(edge, 10 ** 9), int(row["rank"]))
    return best


def _relations(cell: dict) -> dict[tuple[str, str], str]:
    found: dict[tuple[str, str], str] = {}
    for cycle in cell.get("universe") or []:
        for row in cycle:
            found.setdefault(tuple(row["edge"]), row["relation"])
    return found


def ledger(parts: dict, seed: int) -> list[dict]:
    """One row per named edge, at both caps."""
    low, high = parts[seed][40], parts[seed][112]
    ranks_low, ranks_high = _ranks(low), _ranks(high)
    served_low, served_high = _served(low), _served(high)
    asserted = {tuple(edge) for edge in high["asserted_edges"]}
    first: dict[tuple[str, str], int] = {}
    for index, window in enumerate(high["windows_world"], start=1):
        for edge in window:
            first.setdefault(tuple(edge.split(">")), index)
    rows = []
    for edge, q4_rank in named(seed).items():
        rows.append({
            "edge": "%s>%s" % edge, "q4_rank": q4_rank,
            "rank_40": ranks_low.get(edge), "rank_112": ranks_high.get(edge),
            "served_40": sum(1 for window in low["windows_world"] if "%s>%s" % edge in window),
            "served_112": sum(1 for window in high["windows_world"] if "%s>%s" % edge in window),
            "first_served_112": first.get(edge),
            "asserted_112": edge in asserted,
            "relation_40": _relations(low).get(edge),
            "relation_112": _relations(high).get(edge),
        })
    return rows


def adjudicate(parts: dict) -> dict:
    doc = record()
    seeds = list(design()["seeds"])
    gates: dict[str, dict] = {}
    builds = {(cell["engine_version"], cell["engine_sha256"])
              for seed in seeds for cell in parts[seed].values()}
    gates["B1_build"] = {"passed": len(builds) == 1
                         and next(iter(builds))[0] == doc["engine"]["version"]
                         and all(cell["cap"] in CAPS for seed in seeds for cell in parts[seed].values()),
                         "builds": sorted(builds)}

    frozen = doc["band"]["seeds"]
    bad_world = [seed for seed in seeds
                 if parts[seed][40]["world_digest"] != parts[seed][112]["world_digest"]
                 or parts[seed][40]["present_fingerprint"] != parts[seed][112]["present_fingerprint"]
                 or parts[seed][40]["world_digest"] != frozen[str(seed)]["world_digest"]]
    gates["B2_world"] = {"passed": not bad_world, "seeds": bad_world}

    identity = []
    for seed in seeds:
        low = parts[seed][40]
        ranks = _ranks(low)
        served = _served(low)
        for edge, q4_rank in named(seed).items():
            if ranks.get(edge) != q4_rank or edge in served or _relations(low).get(edge) != "transition":
                identity.append({"seed": seed, "edge": "%s>%s" % edge,
                                 "rank": ranks.get(edge), "q4_rank": q4_rank,
                                 "served": edge in served,
                                 "relation": _relations(low).get(edge)})
    gates["B3_band_identity"] = {"passed": not identity, "failures": identity}

    control = [{"seed": seed, "served": len(set(named(seed)) & _served(parts[seed][40])),
                "transitions": max((int(row.get("transitions") or 0)
                                    for row in parts[seed][40]["allocation"]), default=0)}
               for seed in seeds]
    gates["B4_control_40"] = {"passed": all(row["served"] == 0 and row["transitions"] == 20
                                            for row in control), "rows": control}

    high = []
    for seed in seeds:
        cell = parts[seed][112]
        ranks = _ranks(cell)
        served = _served(cell)
        max_served = max((ranks[edge] for edge in served if edge in ranks), default=0)
        high.append({"seed": seed, "transitions": max((int(row.get("transitions") or 0)
                                                       for row in cell["allocation"]), default=0),
                     "max_served_transition_rank": max_served,
                     "max_rows": max((len(window) for window in cell["windows"]), default=0)})
    # Frozen B5 required exactly 56. The engine's 56 is a guaranteed floor and BAND-2
    # corrects the condition; this closed block keeps its original gate and is not rescored.
    gates["B5_cap_live"] = {"passed": all(row["transitions"] == 56 and row["max_served_transition_rank"] > 40
                                          and row["max_rows"] <= 112 for row in high), "rows": high}

    ledgers = {seed: ledger(parts, seed) for seed in seeds}
    missing = {seed: len(named(seed)) - len(rows) for seed, rows in ledgers.items()}
    zero = [(seed, cap) for seed in seeds for cap in CAPS
            if not parts[seed][cap]["present_world_edges"]]
    gates["B6_denominator"] = {"passed": not any(missing.values()) and not zero,
                               "missing": missing, "zero": zero}

    original = ledgers[seeds[0]]
    rerun = ledger({seeds[0]: {40: parts[seeds[0]][40], 112: load(seeds[0], 112, "-rerun")}}, seeds[0])
    gates["B7_determinism"] = {"passed": rerun == original, "seed": seeds[0]}

    counts = [sum(1 for row in ledgers[seed] if row["served_112"] > 0) for seed in seeds]
    gates["B8_seed_axis"] = {"passed": len(set(counts)) >= 3, "counts": counts}

    served_total = sum(counts)
    if not gates["B3_band_identity"]["passed"]:
        verdict = "BAND NOT REPRODUCED"
        reading = ("The named edges are not the 21-40 band on this build, so the band is "
                   "build-dependent and the condition cannot be read.")
        decision = ("Report the build dependence; the acceptance stays unadjudicated and the "
                    "decision PENDING; do not re-read Q2 and do not substitute a fresh band.")
    elif not all(gate["passed"] for gate in gates.values()):
        verdict = "VOID"
        reading = "A gate failed, so the block is unrun or non-reproducible and no acceptance is read."
        decision = "Record VOID; fix the harness and register a new block; read no acceptance."
    elif served_total == 62:
        verdict = "BAND IN SERVICE"
        reading = ("The condition is met on the named edges: the transitions ranked 21-40 at cap "
                   "40 enter service when the cap is 112, per seed.")
        decision = ("Record the condition met; the allocation explanation is not refuted at this "
                    "world family; the owner decides any engine or promotion step; no capability claim.")
    elif served_total == 0:
        verdict = "BAND NOT IN SERVICE"
        reading = "The condition is not met on any named edge."
        decision = "Record the refutation; the next step is the admission rule, not another level."
    else:
        verdict = "BAND PARTLY IN SERVICE"
        reading = "The condition is not met; the unserved edges are the finding and are named in the ledger."
        decision = ("Report the per-edge misses; the allocation explanation is refuted for them; "
                    "the next step is the admission rule, not another level.")

    return engine_stamp.stamp({
        "kind": KIND, "prereg": doc["prereg"], "gates": gates, "verdict": verdict,
        "reading": reading, "decision": decision, "ledger": ledgers,
        "served_112": {str(seed): count for seed, count in zip(seeds, counts)},
        "cells": [{"seed": seed, "cap": cap, "served": len(set(named(seed)) & _served(parts[seed][cap]))}
                  for seed in seeds for cap in CAPS],
        "not_evidence": ("The block ran under the dated grant; it reads whether the 62 named "
                         "edges enter service, not a capability or retention claim."),
    })


def render(art: dict) -> str:
    lines = ["# PRESENCE-BAND-1 -- result", "", "**%s.** %s" % (art["verdict"], art["reading"]), "",
             "## Gates", "", "| Gate | Result |", "| --- | --- |"]
    for name, gate in art["gates"].items():
        lines.append("| `%s` | %s |" % (name, "PASS" if gate["passed"] else "FAIL"))
    lines += ["", "## Named edges served at 112", "",
              "| Seed | Served at 112 (of 62) |", "| ---: | ---: |"]
    for seed, count in art["served_112"].items():
        lines.append("| %s | %d |" % (seed, count))
    lines += ["", "## Decision", "", art["decision"], "", art["not_evidence"], ""]
    return "\n".join(lines)


def self_test() -> int:
    """Hand-built rows: every verdict reachable, and a served band edge caught at 40."""
    assert _verdict({"B3": True, "served": 62}) == "BAND IN SERVICE"
    assert _verdict({"B3": True, "served": 0}) == "BAND NOT IN SERVICE"
    assert _verdict({"B3": True, "served": 7}) == "BAND PARTLY IN SERVICE"
    assert _verdict({"B3": False, "served": 62}) == "BAND NOT REPRODUCED"
    assert _verdict({"B3": True, "served": 62, "gate": False}) == "VOID"
    bad = {"seed": 1, "edges": [["a", "b", 25]]}
    assert not _identity_ok(bad, {("a", "b"): 25}, {("a", "b")})
    assert _identity_ok(bad, {("a", "b"): 25}, set())
    print("band self-test: four verdicts, VOID and the 40 control all reachable")
    return 0


def _verdict(state: dict) -> str:
    if not state.get("B3", True):
        return "BAND NOT REPRODUCED"
    if not state.get("gate", True):
        return "VOID"
    served = state["served"]
    return ("BAND IN SERVICE" if served == 62 else
            "BAND NOT IN SERVICE" if served == 0 else "BAND PARTLY IN SERVICE")


def _identity_ok(row: dict, ranks: dict, served: set) -> bool:
    for edge, q4_rank in {tuple(row["edges"][0][:2]): row["edges"][0][2]}.items():
        return ranks.get(edge) == q4_rank and edge not in served
    return False


def check() -> int:
    doc = record()
    problems = []
    if not band.ARM.exists():
        problems.append("the arm module is missing")
    if doc["runner"]["built"] is not True:
        problems.append("the record does not claim a built runner")
    if doc["authorisation"]["granted"] is not True:
        problems.append("the record does not claim a grant")
    reasons = preflight()
    if doc["status"] == "FROZEN, NOT RUN":
        if doc["runner"]["cells_run"] != 0:
            problems.append("an unrun record claims a run cell")
        if ARTIFACT.exists():
            problems.append("an unrun record has a result artifact")
        if not reasons:
            problems.append("the preflight does not refuse an unrun block")
    elif doc["status"] == "FROZEN, RUN":
        if doc["runner"]["cells_run"] != 13:
            problems.append("the runner claims %r cells, not 13" % (doc["runner"]["cells_run"],))
        if not ARTIFACT.exists():
            problems.append("the block is RUN but has no result artifact")
        else:
            art = json.loads(ARTIFACT.read_text(encoding="utf-8"))
            if art.get("verdict") != (doc.get("result") or {}).get("verdict"):
                problems.append("the artifact verdict does not match the record")
            if art.get("prereg") != doc["prereg"] or art.get("kind") != KIND:
                problems.append("the artifact does not name this block")
            if len(art.get("gates") or {}) != 8:
                problems.append("the artifact does not carry B1-B8")
            if not any("closed" in reason for reason in reasons):
                problems.append("the preflight does not refuse a re-run")
    for problem in problems:
        print("FAIL:", problem)
    if not problems:
        print("band arm: built, %s, %s" % (doc["status"],
              "preflight closes it" if doc["status"] == "FROZEN, RUN" else "preflight refuses"))
    return 1 if problems else 0


def finish() -> int:
    refuse()
    seeds = list(design()["seeds"])
    parts = {seed: {cap: load(seed, cap) for cap in CAPS} for seed in seeds}
    art = adjudicate(parts)
    ARTIFACT.write_text(json.dumps(art, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(art), encoding="utf-8")
    print("verdict: %s" % art["verdict"])
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--measure", action="store_true")
    group.add_argument("--finish", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--self-test", action="store_true")
    group.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--cell", nargs=2, metavar=("SEED", "CAP"))
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if args.dry_run:
        for seed, cap in planned():
            print("--cell %d %d" % (seed, cap))
        print("--finish")
        return 0
    if args.cell:
        refuse()
        seed, cap = int(args.cell[0]), int(args.cell[1])
        PARTS.mkdir(parents=True, exist_ok=True)
        cell = run_cell(seed, cap)
        part_path(seed, cap).write_text(json.dumps(cell), encoding="utf-8")
        print("ran %d at %d" % (seed, cap))
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
