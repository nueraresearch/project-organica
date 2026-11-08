"""The ranking experiment's runner: two orderings over one engine pool, plus harness audits.

This module owns the *execution* half of `docs/RANK-ORDERING-PREREGISTRATION.md`; the
verdict is `benchmarks/score_rank_ordering.py`'s alone. It builds one pool per
(seed, density) with the frozen engine, ranks it two ways at two caps, and writes the
cells the scorer expects.

    ./.venv/bin/python -m benchmarks.run_rank_ordering --self-test   # no engine
    ./.venv/bin/python -m benchmarks.run_rank_ordering --plan
    ./.venv/bin/python -m benchmarks.run_rank_ordering --run

No judged cell was run when this file was committed: `--run` is the run ticket, and
`--self-test` audits the harness without an engine or a world.

The engine is used, never edited: `organica/sleep.py` and `organica/memory.py` are
frozen, and the ingest loop below is the one `benchmarks/probe_allocation_rule.py`
used for the Gate 13 tables. Every database is a scratch database.

**The world generator is fixed here, before any cell.** It is part of the run ticket,
not of the pre-registered criteria: the 16-tag vocabulary, the edge subset per density,
the event stream and the intra-cell filler are all deterministic from the seed and the
density, and `--self-test` audits that each of them does what this docstring says.

**The treatment is audited against the world, not only against its control.** Liveness
can be satisfied by two arms choosing different *filler* rows while neither reaches a
world edge, and that is a decisive false negative waiting to happen. `reach_audit` asks
whether the diversity arm's selection contains a world edge at the primary point, on the
pool the world design implies, with no engine spent. The first construction crowded every
source, the gate failed, and the filler was moved into two of the four cells; the gate now
passes, and the unrepaired construction is kept as a fixture that proves the gate can
still fail.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter
from pathlib import Path
from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parent.parent
PREREG = ROOT / "docs" / "rank_ordering_prereg.json"
OUT = ROOT / "docs" / "rank_ordering_run.json"

# The Gate 13 world family's vocabulary: four groups of four, every tag >= 4 letters
# (AGENTS rule 9). 16 tags, so |P_world| = 16 x 15 = 240 directed non-self pairs.
VOCAB: tuple[str, ...] = (
    "amber", "birch", "cedar", "maple",
    "indigo", "fern", "willow", "yarrow",
    "olive", "sable", "umber", "verdant",
    "ochre", "crimson", "teal", "slate",
)
EVENTS_PER_CYCLE = 8
#: Each world edge is emitted this many times, as one two-tag event per emission.
EDGE_REPEATS = 2
#: The intra-cell filler: every pair inside a *filler* cell, repeated more often than a
#: world edge, so a count ordering spends its budget on them as Gate 13's top-20 did.
FILLER_REPEATS = 6
#: How many of the four cells emit filler. Fewer than four, so the crowding is partial:
#: eight sources are crowded and eight are free, and spreading off the crowded ones
#: reaches world rows. With every source crowded the diversity arm cannot reach at all
#: (the smoke run of 2026-11-07), which is what the reach gate is for.
FILLER_CELLS = 2


def prereg(path: Path = PREREG) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# The world
# ---------------------------------------------------------------------------

def vocabulary() -> tuple[str, ...]:
    if len(VOCAB) != 16 or len(set(VOCAB)) != 16:
        raise SystemExit("the world family must have 16 distinct tags")
    short = [tag for tag in VOCAB if len(tag) < 4]
    if short:
        raise SystemExit("tags shorter than four letters are invisible: %r" % (short,))
    return VOCAB


def cells() -> list[tuple[str, ...]]:
    """Four four-tag cells. A pair inside one cell is an intra-cell row."""
    tags = vocabulary()
    return [tuple(tags[i:i + 4]) for i in range(0, len(tags), 4)]


def all_pairs() -> list[tuple[str, str]]:
    return [(a, b) for a in vocabulary() for b in vocabulary() if a != b]


def cross_cell_pairs() -> list[tuple[str, str]]:
    """The ordered pairs that cross a cell boundary: the law's candidate universe."""
    out = []
    groups = cells()
    for i, left in enumerate(groups):
        for j, right in enumerate(groups):
            if i != j:
                out.extend((a, b) for a in left for b in right)
    return out


def world_edges(seed: int, rho: float) -> set[tuple[str, str]]:
    """The world's true edges at this density: a deterministic subset of the 240 pairs.

    The subset is drawn by shuffling the full pair list with a generator keyed on
    (seed, density), so it is reproducible and independent of which arm ranks it.
    """
    universe = cross_cell_pairs()
    k = round(rho * len(all_pairs()))
    if k > len(universe):
        raise SystemExit("density %r wants %d edges; only %d cross-cell pairs exist"
                         % (rho, k, len(universe)))
    rng = random.Random("%d:%.2f" % (seed, rho))
    rng.shuffle(universe)
    return set(universe[:k])


def filler_cells() -> list[tuple[str, ...]]:
    """The cells that emit intra-cell filler. The crowding is deliberately partial."""
    return list(cells()[:FILLER_CELLS])


def filler_pairs() -> list[tuple[str, str]]:
    """Every ordered pair inside a filler cell: the intra-cell rows counted most."""
    out = []
    for group in filler_cells():
        out.extend((a, b) for a in group for b in group if a != b)
    return out


def density_stream(seed: int, rho: float) -> list[str]:
    """The event stream for one (seed, density) cell.

    Each world edge becomes `EDGE_REPEATS` two-tag events, so the edge is present as a
    temporal transition by construction; each filler cell's four-tag event is emitted
    `FILLER_REPEATS` times, so its intra-cell pairs outcount a world edge and a count
    ordering prefers them. Only `FILLER_CELLS` cells emit filler, so half the sources are
    crowded and half are free.
    """
    events: list[str] = []
    for a, b in sorted(world_edges(seed, rho)):
        events.extend(["%s %s" % (a, b)] * EDGE_REPEATS)
    for group in filler_cells():
        events.extend([" ".join(group)] * FILLER_REPEATS)
    return events


def designed_pairs(stream: list[str]) -> set[tuple[str, str]]:
    """Every tag pair the stream can produce as a temporal edge, engine rules aside.

    Within-event pairs and consecutive-event pairs are both included, which is the
    widest the engine can see; the audit uses this to prove non-world rows exist.
    """
    pairs: set[tuple[str, str]] = set()
    previous: list[str] = []
    for text in stream:
        tags = text.split()
        for a in tags:
            for b in tags:
                if a != b:
                    pairs.add((a, b))
        for a in previous:
            for b in tags:
                if a != b:
                    pairs.add((a, b))
        previous = tags
    return pairs


# ---------------------------------------------------------------------------
# The two orderings
# ---------------------------------------------------------------------------

def rank_control(rows: list[tuple[str, str, int]], k: int) -> list[tuple[str, str]]:
    """The engine's own rule: top-k by count, ties on a stable key."""
    ordered = sorted(rows, key=lambda r: (-r[2], r[0], r[1]))
    return [(a, b) for a, b, _c in ordered[:k]]


def rank_diversity(rows: list[tuple[str, str, int]], k: int) -> list[tuple[str, str]]:
    """Greedy max-marginal coverage over the left-hand tag.

    Each slot takes the remaining candidate whose source already owns the fewest
    selected outgoing edges; ties break on count, then on the stable key. The primary
    term counts *selected* edges per source, not the candidate's own frequency.
    """
    remaining = sorted(rows, key=lambda r: (-r[2], r[0], r[1]))
    per_source: Counter[str] = Counter()
    selected: list[tuple[str, str]] = []
    while remaining and len(selected) < k:
        best = min(remaining, key=lambda r: (per_source[r[0]], -r[2], r[0], r[1]))
        selected.append((best[0], best[1]))
        per_source[best[0]] += 1
        remaining.remove(best)
    return selected


def measure(pool: list[tuple[str, str, int]], world: set[tuple[str, str]],
            selected: list[tuple[str, str]]) -> dict:
    covered = sum(1 for edge in selected if edge in world)
    present = sum(1 for edge in world if any((a, b) == edge for a, b, _c in pool))
    return {
        "asserted": len(selected),
        "covered": covered,
        "coverage": round(covered / len(world), 6) if world else None,
        "precision": round(covered / len(selected), 6) if selected else None,
        "rho_rank": round(present / len(pool), 6) if pool else None,
        "presence": round(present / len(world), 6) if world else None,
    }


def cells_for(seed: int, rho: float, pool: list[tuple[str, str, int]],
              world: set[tuple[str, str]], record: dict | None = None) -> list[dict]:
    """Both arms at both caps for one pool. The pool is shared, so the cells are paired."""
    record = record or prereg()
    cells = []
    for cap in record["design"]["caps"]:
        for arm, ranker in (("control", rank_control), ("diversity", rank_diversity)):
            selected = ranker(pool, cap)
            stats = measure(pool, world, selected)
            cells.append({
                "arm": arm, "cap": cap, "rho_world": rho, "seed": seed,
                "coverage": stats["coverage"], "precision": stats["precision"],
                "rho_rank": stats["rho_rank"], "presence": stats["presence"],
                "selected": ["%s>%s" % edge for edge in selected],
                "asserted": stats["asserted"], "covered": stats["covered"],
            })
    return cells


# ---------------------------------------------------------------------------
# The engine pool
# ---------------------------------------------------------------------------

def run_pool(seed: int, rho: float) -> list[tuple[str, str, int]]:
    """Ingest one world with the frozen engine and return its `precedes` rows.

    The ingest loop is `probe_allocation_rule.run_seed`'s: store the event, run a sleep
    cycle every `EVENTS_PER_CYCLE` events, then read the table. The database is a
    scratch database and the live one is refused before anything is opened.
    """
    from organica.memory import MemoryService
    from organica.paths import LIVE_DB, temp_db
    from organica.sleep import SleepService

    db_path = temp_db("rankorder_%d_%d" % (seed, round(rho * 100)))
    if db_path.resolve() == LIVE_DB.resolve():
        raise SystemExit("refusing to open the live database")

    mem = MemoryService(str(db_path))
    try:
        service = SleepService(mem)
        for index, text in enumerate(density_stream(seed, rho), start=1):
            mem.store(text, event_type="observe", source="env")
            if index % EVENTS_PER_CYCLE == 0:
                service.run_sleep_cycle()
        rows = mem._conn.execute(
            "SELECT tag_from, tag_to, count FROM precedes").fetchall()
        return [(str(a), str(b), int(c)) for a, b, c in rows]
    finally:
        mem.close()
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Harness self-tests: no engine, no world, no judged cell
# ---------------------------------------------------------------------------

def generator_audit(record: dict | None = None) -> dict:
    record = record or prereg()
    problems = []
    checked = 0
    for seed in record["design"]["seeds"]:
        for rho in record["design"]["densities"]:
            world = world_edges(seed, rho)
            stream = density_stream(seed, rho)
            expected = round(rho * 240)
            if len(world) != expected:
                problems.append("%d/%s: %d edges, expected %d"
                                % (seed, rho, len(world), expected))
            if any(a == b for a, b in world):
                problems.append("%d/%s: a self pair" % (seed, rho))
            if any(a not in VOCAB or b not in VOCAB for a, b in world):
                problems.append("%d/%s: a pair outside the vocabulary" % (seed, rho))
            if len(world) != len(set(world)):
                problems.append("%d/%s: duplicate edges" % (seed, rho))
            # presence by construction: every edge appears as a two-tag event
            emitted = {"%s>%s" % (text.split()[0], text.split()[1]) for text in stream}
            missing = [edge for edge in world
                       if "%s>%s" % edge not in emitted]
            if missing:
                problems.append("%d/%s: %d edges never emitted"
                                % (seed, rho, len(missing)))
            extra = designed_pairs(stream) - world
            if not extra:
                problems.append("%d/%s: no non-world rows, so nothing competes"
                                % (seed, rho))
            baseline = 1 + FILLER_REPEATS
            if any((a, b) in world for a, b in filler_pairs()):
                problems.append("%d/%s: an intra-cell row is a world edge" % (seed, rho))
            if EDGE_REPEATS >= baseline:
                problems.append("a world edge must be rarer than the filler")
            crowded = {a for a, _b in filler_pairs()}
            if len(crowded) >= len(VOCAB):
                problems.append("%d/%s: every source is crowded, so spreading cannot "
                                "escape the filler" % (seed, rho))
            if len(filler_pairs()) != 3 * len(crowded):
                problems.append("the filler is not three rows per crowded source")
            checked += 1
    return {"passed": not problems, "cells_checked": checked, "problems": problems[:8]}


def liveness_audit() -> dict:
    """The arms must differ on a pool built the way this world builds one."""
    # one source owns four high-count rows, as a cell does in this world
    pool = [("amber", "birch", 9), ("amber", "cedar", 8),
            ("amber", "maple", 7), ("amber", "slate", 6)]
    pool += [(tag, "verdant", 1) for tag in vocabulary() if tag != "verdant"]
    control = rank_control(pool, 6)
    diversity = rank_diversity(pool, 6)
    return {
        "passed": control != diversity,
        "control": ["%s>%s" % e for e in control],
        "diversity": ["%s>%s" % e for e in diversity],
    }


def identity_audit() -> dict:
    """G5: with every candidate a true edge and the cap above the pool, the arms agree."""
    world = set(sorted(world_edges(prereg()["design"]["seeds"][0], 0.80))[:12])
    pool = [(a, b, 1) for a, b in sorted(world)]
    cap = 40
    control = rank_control(pool, cap)
    diversity = rank_diversity(pool, cap)
    delta = (measure(pool, world, diversity)["coverage"]
             - measure(pool, world, control)["coverage"])
    body = {"rho_world": 1.0, "arms_identical": set(control) == set(diversity),
            "delta": round(delta, 12), "pool": len(pool), "cap": cap}
    body["passed"] = body["arms_identical"] and abs(body["delta"]) <= 1e-12
    return body


def harness_pool(seed: int, rho: float):
    """The pool this world *designs*: every world edge, every filler pair, no engine.

    Counts are the design's own (`EDGE_REPEATS`, `FILLER_REPEATS`). The engine adds
    cross-event rows on top, which only crowd a count ordering further, so a pool that
    cannot reach a world edge here cannot reach one in the measured pool either.
    """
    world = world_edges(seed, rho)
    pool = [(a, b, EDGE_REPEATS) for a, b in sorted(world)]
    pool += [(a, b, FILLER_REPEATS) for a, b in filler_pairs() if (a, b) not in world]
    return pool, world


def _first_world_rank(selected: list[tuple[str, str]],
                      world: set[tuple[str, str]]) -> int | None:
    for rank, edge in enumerate(selected, start=1):
        if edge in world:
            return rank
    return None


def reach_stats(pool: list[tuple[str, str, int]], world: set[tuple[str, str]],
                cap: int) -> dict:
    """Selection against the *world* at one cap, for both arms."""
    control = rank_control(pool, len(pool))
    diversity = rank_diversity(pool, len(pool))
    return {
        "cap": cap,
        "pool_rows": len(pool),
        "world_rows": sum(1 for a, b, _c in pool if (a, b) in world),
        "control_reach": sum(1 for edge in control[:cap] if edge in world),
        "diversity_reach": sum(1 for edge in diversity[:cap] if edge in world),
        "control_rank_of_first_world_edge": _first_world_rank(control, world),
        "diversity_rank_of_first_world_edge": _first_world_rank(diversity, world),
    }


def reach_audit(record: dict | None = None) -> dict:
    """The treatment must be able to reach the signal at the primary point.

    This is the audit the smoke run showed was missing: the existing ones compare the
    arms to each other, so two selections that differ only in *which filler* they take
    pass liveness while both cover nothing. A gate that only ever passes is decoration;
    `tests/test_rank_ordering_runner.py` shows this one failing and passing.
    """
    record = record or prereg()
    rho = record["design"]["densities"][0]
    cap = record["design"]["caps"][0]
    rows, problems = [], []
    for seed in record["design"]["seeds"]:
        pool, world = harness_pool(seed, rho)
        stats = reach_stats(pool, world, cap)
        stats["seed"] = seed
        rows.append(stats)
        if stats["world_rows"] == 0:
            problems.append("%d: no world rows in the pool" % seed)
        if stats["diversity_reach"] == 0:
            problems.append("%d: the treatment reaches no world edge at cap %d"
                            % (seed, cap))
    return {"passed": not problems, "rho_world": rho, "cap": cap,
            "seeds": rows, "problems": problems[:8]}


def plan(record: dict | None = None) -> list[dict]:
    record = record or prereg()
    cells = []
    for seed in record["design"]["seeds"]:
        for rho in record["design"]["densities"]:
            for cap in record["design"]["caps"]:
                for arm in record["design"]["arms"]:
                    cells.append({"seed": seed, "rho_world": rho, "cap": cap, "arm": arm})
    expected = record["design"]["cells"]
    if len(cells) != expected:
        raise SystemExit("the plan has %d cells, the pre-registration has %d"
                         % (len(cells), expected))
    return cells


def assert_grid(record: dict) -> None:
    """Refuse anything that is not the frozen grid, before an engine is touched."""
    head = record["status"].split("(")[0].split(",")[0].strip()
    ran = record.get("run") or {}
    if head == "RUN COMPLETE":
        # Frozen and executed: the artifacts record the cells, and a second run is refused by
        # main() unless --force is given, so describing the grid stays legal.
        if not ran.get("run_artifact"):
            raise SystemExit("the pre-registration says it ran but names no run artifact")
    elif head != "FROZEN":
        raise SystemExit("the pre-registration is not frozen")
    seeds = list(record["design"]["seeds"])
    if len(seeds) != 8 or len(set(seeds)) != 8:
        raise SystemExit("the grid does not carry eight distinct seeds")
    if seeds != list(range(seeds[0], seeds[0] + 8)):
        raise SystemExit("the seed block is not contiguous")
    if record["design"]["cells"] != 160:
        raise SystemExit("the grid is not 160 cells")
    for rho in record["design"]["densities"]:
        if not 0.0 < rho < 1.0:
            raise SystemExit("density outside (0, 1): %r" % (rho,))


def self_test(record: dict | None = None) -> dict:
    record = record or prereg()
    try:
        assert_grid(record)
        planned = plan(record)
        grid_ok, grid_problem = len(planned) == 160, ""
    except SystemExit as exc:                       # pragma: no cover - guard surface
        grid_ok, grid_problem = False, str(exc)
    checks = {
        "grid": {"passed": grid_ok, "cells": 160, "problem": grid_problem},
        "generator": generator_audit(record),
        "liveness": liveness_audit(),
        "identity": identity_audit(),
    }
    gates = {"reach": reach_audit(record)}
    mechanics = all(c["passed"] for c in checks.values())
    ready = mechanics and all(g["passed"] for g in gates.values())
    return {"all_passed": ready, "mechanics_passed": mechanics, "run_ready": ready,
            "checks": checks, "gates": gates}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def run(out: Path = OUT, record: dict | None = None) -> dict:
    record = record or prereg()
    assert_grid(record)
    blocked = (record.get("pre_run") or {}).get("blocked")
    if blocked:
        raise SystemExit("the block is blocked by a recorded finding; no cell may run: %s"
                         % blocked)
    report = self_test(record)
    if not report["all_passed"]:
        failed = {k: v for k, v in report["checks"].items() if not v["passed"]}
        failed.update({"gate:" + k: v for k, v in report["gates"].items()
                       if not v["passed"]})
        raise SystemExit("the harness self-tests failed; no cell may run: %r" % failed)
    cells: list[dict] = []
    for seed in record["design"]["seeds"]:
        for rho in record["design"]["densities"]:
            pool = run_pool(seed, rho)
            world = world_edges(seed, rho)
            cells.extend(cells_for(seed, rho, pool, world, record))
    payload = {
        "prereg": record["prereg"],
        "cells": cells,
        "identity": identity_audit(),
        "provenance": {
            "runner": "benchmarks/run_rank_ordering.py",
            "engine_runs": len(record["design"]["seeds"]) * len(record["design"]["densities"]),
            "cells": len(cells),
            "world": "16 tags, %d pairs at the top density" % 240,
            "events_per_cycle": EVENTS_PER_CYCLE,
            "edge_repeats": EDGE_REPEATS,
            "filler_repeats": FILLER_REPEATS,
        },
    }
    out.write_text(json.dumps(engine_stamp.stamp(payload), indent=1) + "\n", encoding="utf-8")
    print("wrote", out, "| cells:", len(cells))
    return payload


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true",
                        help="audit the harness; no engine, no world")
    parser.add_argument("--plan", action="store_true", help="print the 160 cells")
    parser.add_argument("--run", action="store_true", help="execute the block")
    parser.add_argument("--out", default=str(OUT))
    parser.add_argument("--force", action="store_true",
                        help="overwrite an existing run artifact")
    args = parser.parse_args(argv)

    if args.run:
        target = Path(args.out)
        if target.exists() and not args.force:
            print("refusing to overwrite %s without --force" % target)
            return 1
        run(target)
        return 0
    if args.plan:
        for cell in plan():
            print("%d  rho=%.1f  cap=%d  %s" % (cell["seed"], cell["rho_world"],
                                                cell["cap"], cell["arm"]))
        return 0
    report = self_test()
    print(json.dumps(report, indent=1))
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
