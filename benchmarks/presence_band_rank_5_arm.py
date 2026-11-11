"""PRESENCE-BAND-5: run the twelve-cell fresh-world band block and write its ledger."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from organica.sleep import SleepService

from benchmarks import engine_stamp
from benchmarks import presence_band_rank_4_prereg as band4
from benchmarks import presence_band_rank_5_prereg as band5
from benchmarks import presence_conversion_repair_observer as observer
from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.acquisition_harness import _CountingMemoryService, _make_scratch_db
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE, structure_edges
from benchmarks.presence_construct_audit import (ACQ_SOURCE, PHASE_ACQUISITION,
                                                 _digest, _world_compositional_edges,
                                                 asserted_fingerprint)

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "presence_band_rank_5_run.json"
PAGE = ROOT / "docs" / "PRESENCE-BAND-RANK-5-RESULT.md"
PARTS = ROOT / ".scratch" / "presence_band_5" / "parts"
CAPS = (40, 112)
KIND = "presence_band_rank_5_run"


def record() -> dict:
    return band5.record()


def design() -> dict:
    return record()["design"]


def planned() -> list[tuple[int, int]]:
    return [(seed, cap) for seed in design()["seeds"] for cap in CAPS]


def preflight() -> list[str]:
    doc = record()
    found: list[str] = []
    if doc.get("status") != "FROZEN, NOT RUN":
        found.append("the block is %r, not FROZEN, NOT RUN" % doc.get("status"))
    if not (doc.get("authorisation") or {}).get("granted"):
        found.append("the dated grant is not recorded")
    if getattr(__import__("organica"), "__version__", None) != "0.15.0":
        found.append("the shipped build is not 0.15.0")
    if SleepService.MAX_PREDICTIONS != 112:
        found.append("the shipped cap is not 112")
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
    db_path = _make_scratch_db("presence_band_5")
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


def ledger(parts: dict, seed: int) -> list[dict]:
    low, high = parts[seed][40], parts[seed][112]
    band = band4.band_edges(high)
    asserted = {tuple(edge) for edge in high["asserted_edges"]}
    rows = []
    for edge, rank in sorted(band.items()):
        rows.append({
            "edge": "%s>%s" % edge,
            "rank_112": rank,
            "rank_40": next((r["rank"] for cycle in low["universe"] for r in cycle
                             if tuple(r["edge"]) == edge), None),
            "served_40": sum(1 for window in low["windows_world"] if "%s>%s" % edge in window),
            "served_112": sum(1 for window in high["windows_world"] if "%s>%s" % edge in window),
            "asserted_112": edge in asserted,
        })
    return rows


def _counts_law(cell: dict, cap: int, floor: int, cooc_max: int) -> tuple[bool, str]:
    rows = cell.get("allocation") or []
    windows = cell.get("windows") or []
    if not rows or len(rows) != len(windows):
        return False, "allocation rows do not match windows"
    full = 0
    for index, (row, window) in enumerate(zip(rows, windows), start=1):
        transitions = row.get("transitions")
        cooccurrences = row.get("cooccurrences")
        if transitions is None or cooccurrences is None:
            return False, "cycle %d lacks both counts" % index
        transitions, cooccurrences = int(transitions), int(cooccurrences)
        if transitions + cooccurrences != len(window):
            return False, "cycle %d does not sum to its window" % index
        if cooccurrences > cooc_max:
            return False, "cycle %d exceeds the cooccurrence ceiling" % index
        if len(window) == cap:
            full += 1
            if transitions < floor:
                return False, "cycle %d is below the transition floor" % index
    if full == 0:
        return False, "no full %d-row window" % cap
    return True, "ok"


def adjudicate(parts: dict) -> dict:
    seeds = list(design()["seeds"])
    gates: dict[str, dict] = {}
    builds = {(cell["engine_version"], cell["engine_sha256"])
              for seed in seeds for cell in parts[seed].values()}
    gates["B1_build"] = {
        "passed": len(builds) == 1 and next(iter(builds))[0] == record()["engine"]["version"],
        "builds": sorted(builds),
    }
    bad_world = [seed for seed in seeds
                 if parts[seed][40]["world_digest"] != parts[seed][112]["world_digest"]
                 or parts[seed][40]["present_fingerprint"] != parts[seed][112]["present_fingerprint"]]
    gates["B2_world"] = {"passed": not bad_world, "seeds": bad_world}

    bands = {}
    for seed in seeds:
        bands[seed] = band4.band_edges(parts[seed][112])
    gates["B3_band_identity"] = {
        "passed": all(bool(bands[seed]) for seed in seeds),
        "sizes": {str(seed): len(bands[seed]) for seed in seeds},
    }

    low_rows = []
    for seed in seeds:
        low = parts[seed][40]
        rows = low.get("allocation") or []
        sum_ok = bool(rows) and all(
            row.get("sum_matches") is True
            and int(row.get("transitions") or 0) + int(row.get("cooccurrences") or 0)
            == int(row.get("served") or 0)
            for row in rows
        )
        max_rows = max((len(window) for window in low.get("windows") or []), default=0)
        served_band = len(set(bands[seed]) & _served(low))
        low_rows.append({"seed": seed,
                         "passed": sum_ok and max_rows <= 40 and served_band == 0,
                         "why": "ok" if sum_ok and max_rows <= 40 else "cap-40 count/ceiling",
                         "served_band": served_band,
                         "max_rows": max_rows})
    gates["B4_control_40"] = {"passed": all(row["passed"] for row in low_rows),
                              "rows": low_rows}

    high_rows = []
    for seed in seeds:
        law = band4.allocation_law(parts[seed][112], cap=112, floor=56, cooc_max=56)
        high_rows.append({"seed": seed, **law})
    gates["B5_allocation_law"] = {
        "passed": all(row["passed"] for row in high_rows),
        "rows": high_rows,
    }

    ledgers = {seed: ledger(parts, seed) for seed in seeds}
    missing = {seed: len(bands[seed]) - len(ledgers[seed]) for seed in seeds}
    zero = [seed for seed in seeds if not bands[seed]]
    gates["B6_denominator"] = {"passed": not any(missing.values()) and not zero,
                               "missing": missing, "zero": zero}

    rerun = ledger({seeds[0]: {40: parts[seeds[0]][40],
                              112: load(seeds[0], 112, "-rerun")}}, seeds[0])
    gates["B7_determinism"] = {"passed": rerun == ledgers[seeds[0]], "seed": seeds[0]}

    served_sets = {seed: {row["edge"] for row in ledgers[seed] if row["served_112"] > 0}
                   for seed in seeds}
    gates["B8_seed_axis"] = {"passed": len({tuple(sorted(v)) for v in served_sets.values()}) >= 3,
                             "sets": {str(k): len(v) for k, v in served_sets.items()}}

    commands = [row["served_112"] > 0 for seed in seeds for row in ledgers[seed]]
    all_served = all(commands)
    none_served = not any(commands)
    if not gates["B5_allocation_law"]["passed"]:
        verdict = "ALLOCATION LAW NOT CONFIRMED"
        reading = "The cap-112 full-window allocation law failed, so the band result cannot confirm it."
        decision = "Report the allocation failure; do not call the band confirmed; fix the allocation rule before another band block."
    elif not gates["B3_band_identity"]["passed"]:
        verdict = "BAND NOT REPRODUCED"
        reading = "The measured rank-21-40 band is empty or not identifiable on this build."
        decision = "Report the build dependence; do not substitute a band."
    elif not all(gates[name]["passed"] for name in ("B1_build", "B2_world", "B4_control_40",
                                                    "B6_denominator", "B7_determinism", "B8_seed_axis")):
        verdict = "VOID"
        reading = "A non-allocation infrastructure gate failed; no acceptance is read."
        decision = "Record VOID; fix the failed gate and register a new block."
    elif all_served:
        verdict = "CONFIRMED"
        reading = "The allocation law and fresh-world rank-21-40 service both hold."
        decision = "Record the confirmation; the owner decides any engine or promotion step; no capability claim."
    elif none_served:
        verdict = "BAND NOT CONFIRMED"
        reading = "The allocation law holds but no measured band edge enters service."
        decision = "Report the refutation; the next step is the admission rule, not another cap level."
    else:
        verdict = "BAND PARTLY NOT CONFIRMED"
        reading = "The allocation law holds but some measured band edges do not enter service."
        decision = "Report the per-edge misses; the next step is the admission rule."

    return engine_stamp.stamp({
        "kind": KIND, "prereg": record()["prereg"], "gates": gates,
        "verdict": verdict, "reading": reading, "decision": decision,
        "ledger": {str(seed): ledgers[seed] for seed in seeds},
        "bands": {str(seed): len(bands[seed]) for seed in seeds},
        "cells": [{"seed": seed, "cap": cap, "served": len(
            [row for row in ledgers[seed] if row["served_%d" % cap] > 0])}
            for seed in seeds for cap in CAPS],
        "not_evidence": "Fresh-world allocation and service, not a capability, retention or transfer claim.",
    })


def render(art: dict) -> str:
    lines = ["# PRESENCE-BAND-5 -- per-edge result", "",
             "**%s.** %s" % (art["verdict"], art["reading"]), "",
             "## Gates", "", "| Gate | Result |", "| --- | --- |"]
    for name, gate in art["gates"].items():
        lines.append("| `%s` | %s |" % (name, "PASS" if gate["passed"] else "FAIL"))
    lines += ["", "## Band sizes", "", "| Seed | Band edges | Served at 112 |",
              "| ---: | ---: | ---: |"]
    for seed, size in art["bands"].items():
        served = sum(1 for row in art["ledger"][seed] if row["served_112"] > 0)
        lines.append("| %s | %d | %d |" % (seed, size, served))
    lines += ["", "## Per-edge ledger", "",
              "| Seed | Edge | Rank at 112 | Served at 40 | Served at 112 | Asserted |",
              "| ---: | --- | ---: | ---: | ---: | --- |"]
    for seed, rows in art["ledger"].items():
        for row in rows:
            lines.append("| %s | `%s` | %s | %d | %d | %s |" % (
                seed, row["edge"], row["rank_112"], row["served_40"], row["served_112"],
                "yes" if row["asserted_112"] else "no"))
    lines += ["", "## Decision", "", art["decision"], "", art["not_evidence"], ""]
    return "\n".join(lines)


def check() -> int:
    doc = record()
    problems = band5.problems()
    if doc["status"] == "FROZEN, RUN":
        if not ARTIFACT.exists():
            problems.append("run artifact missing")
        if not PAGE.exists():
            problems.append("result page missing")
        if doc["runner"]["cells_run"] != 13:
            problems.append("runner did not record 13 cells")
    for problem in problems:
        print("FAIL:", problem)
    if not problems:
        print("band 5 arm: %s, runner %s cells" % (doc["status"], doc["runner"]["cells_run"]))
    return 1 if problems else 0


def finish() -> int:
    refuse()
    seeds = list(design()["seeds"])
    parts = {seed: {cap: load(seed, cap) for cap in CAPS} for seed in seeds}
    art = adjudicate(parts)
    ARTIFACT.write_text(json.dumps(art, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(art), encoding="utf-8")
    band5.mark_result(art)
    print("verdict: %s" % art["verdict"])
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--measure", action="store_true")
    group.add_argument("--finish", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--cell", nargs=2, metavar=("SEED", "CAP"))
    args = parser.parse_args(argv)
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
