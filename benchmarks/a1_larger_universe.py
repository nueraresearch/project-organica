"""A predeclared larger successor universe and its no-arm candidate.

The 16-tag world tops out at 64 independent candidate edges.  This module
declares a larger family before looking at K: 28 tags, 7 per cell, same four
cells, same flip-P/flip-Q law, same 8 events per cycle and same 120-cycle
horizon.  The candidate universe is still the first 36-cycle, one-orientation
stream, so the pre-37 selection rule is unchanged.

The construction is fixed by the tag pool and cell rule, not by a K screen.
It writes a candidate spec and a separate preflight record; it selects no
target, freezes no manifest, reserves no seed, issues no grant and runs no A1
cell.

    python -m benchmarks.a1_larger_universe --write
    python -m benchmarks.a1_larger_universe --check
    python -m benchmarks.a1_larger_universe --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

from benchmarks import a1_baseline_availability
from benchmarks import a1_successor_preflight
from benchmarks import a1_successor_schema
from benchmarks import a1_target_selection
from benchmarks.acquisition_compositional import CELLS, TAG_POOL

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT_PATH = DOCS / "a1_larger_universe_candidate.json"
PAGE_PATH = DOCS / "A1-LARGER-UNIVERSE-CANDIDATE.md"
PREFLIGHT_PATH = DOCS / "a1_larger_universe_preflight.json"
PREFLIGHT_PAGE_PATH = DOCS / "A1-LARGER-UNIVERSE-PREFLIGHT.md"
ID = "A1-LARGER-UNIVERSE-CANDIDATE-1"
PREFLIGHT_ID = "A1-LARGER-UNIVERSE-PREFLIGHT-1"
DATE = "2026-11-14"
KIND = "a1_successor_candidate"
STATUS = "CANDIDATE SPEC — NO ARM, NO TARGET, NOT FROZEN, NOT RUN"
SEEDS = (20660101, 20660102, 20660103, 20660104, 20660105, 20660106)
TAGS_PER_CELL = 7
TAGS_PER_EVENT = 2
EVENTS_PER_CYCLE = 8
CYCLES = 120
U_CYCLE = 36


def _tag_pool(tags_per_cell: int) -> tuple[str, ...]:
    count = tags_per_cell * len(CELLS)
    extra = tuple("tag%s" % (chr(97 + i) * 2) for i in range(count - len(TAG_POOL)))
    pool = TAG_POOL + extra
    if len(pool) != count or len(set(pool)) != count:
        raise ValueError("tag pool is not unique at the requested size")
    return pool


TAGS = _tag_pool(TAGS_PER_CELL)
assert len(TAGS) == TAGS_PER_CELL * len(CELLS)


def generate_world(seed: int, cycles: int = CYCLES,
                   tags_per_cell: int | None = None) -> dict:
    """Generate the declared larger compositional world.

    This mirrors ``generate_compositional_world`` with a larger, fixed pool.
    The tag-to-cell mapping is shuffled per seed, so a seed cannot choose a
    favourable set of tag pairs.  ``tags_per_cell`` is injectable only for the
    structural size probe; the candidate always uses the module constant.
    """
    if cycles < 1:
        raise ValueError("cycles must be positive")
    per_cell = TAGS_PER_CELL if tags_per_cell is None else tags_per_cell
    tags = _tag_pool(per_cell)
    rng = random.Random(seed)
    pool = list(tags)
    rng.shuffle(pool)
    cell_tags = {
        cell: sorted(pool[i * per_cell:(i + 1) * per_cell])
        for i, cell in enumerate(CELLS)
    }
    held = CELLS[rng.randrange(len(CELLS))]
    held_flip_p = (1 - held[0], held[1])
    events: list[str] = []
    cells: list[str] = []
    regimes: list[int] = []
    trainable: list[bool] = []
    withheld: list[bool] = []
    state = CELLS[rng.randrange(len(CELLS))]
    for cycle in range(cycles):
        regime = (cycle // 200) % 2
        law = ({"flip_p": 0.65, "flip_q": 0.35} if regime == 0
               else {"flip_p": 0.35, "flip_q": 0.65})
        for _ in range(EVENTS_PER_CYCLE):
            kind = rng.choices(
                ("flip_p", "flip_q"),
                weights=[law["flip_p"], law["flip_q"]], k=1)[0]
            nxt = ((1 - state[0], state[1]) if kind == "flip_p"
                   else (state[0], 1 - state[1]))
            pair = rng.sample(cell_tags[nxt], TAGS_PER_EVENT)
            events.append(" ".join(sorted(pair)))
            cells.append("p%dq%d" % nxt)
            regimes.append(regime)
            in_acq = 20 * EVENTS_PER_CYCLE <= len(events) - 1 < 110 * EVENTS_PER_CYCLE
            is_withheld = state == held and nxt == held_flip_p and in_acq
            trainable.append(not is_withheld)
            withheld.append(is_withheld)
            state = nxt
    return {
        "events": events,
        "cells": cells,
        "regimes": regimes,
        "trainable": trainable,
        "withheld": withheld,
        "tag_pool": sorted(tags),
        "tags_per_cell": per_cell,
        "world_family": "larger compositional %d-tag" % len(tags),
    }


def _rows(seed: int) -> tuple[dict, dict]:
    world = generate_world(seed)
    selection = a1_target_selection.run_seed(
        seed, world=world, boundary_safe=True)
    baseline = a1_baseline_availability._run_seed(seed, world=world)
    available = {row["edge"]: row for row in baseline["rows"]}
    rows = []
    for edge in sorted(selection["u"]):
        row = available[edge]
        rows.append({
            "edge": edge,
            "A": bool(row["A"]),
            "K": bool(row["K"]),
        })
    return selection, rows


def build() -> dict:
    per_seed = {}
    summaries = []
    for seed in SEEDS:
        selection, rows = _rows(seed)
        per_seed[str(seed)] = rows
        summaries.append({
            "seed": seed,
            "candidate_edges": len(rows),
            "independent_edges": len({
                tuple(sorted(edge.split(">", 1))) for edge in (r["edge"] for r in rows)
            }),
            "A_available": sum(row["A"] for row in rows),
            "K_available": sum(row["K"] for row in rows),
            "A_and_K": sum(row["A"] and row["K"] for row in rows),
            "selection_status": selection["status"],
        })
    doc = {
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "seed_block": list(SEEDS),
        "targets_in_scope": True,
        "selection": {
            "source": "A1-LARGER-UNIVERSE-1",
            "u_cycle": U_CYCLE,
            "cycles": CYCLES,
            "one_orientation_per_pair": True,
            "boundary_safe": True,
            "boundary_note": "cycle-boundary correction retained from the fresh-block candidate",
            "screen": "none — the 28-tag construction was fixed before K; the edge count is structural",
            "targets_selected": 0,
            "k_screened": False,
            "prior_k_exposure": "none; the 28-tag construction and size were fixed before any K measurement",
        },
        "baseline": {
            "source": "A1-LARGER-UNIVERSE-BASELINE-1",
            "cycles": CYCLES,
            "treatment": "none",
            "A": "prediction path available at least once",
            "K": "carrier path available at least once",
        },
        "per_seed": per_seed,
        "summaries": summaries,
        "governance": {
            "preflight_required": True,
            "freeze": False,
            "grant": False,
            "run": False,
            "authorization": "none",
        },
        "not_evidence": (
            "A no-arm candidate specification for a separately declared larger "
            "world family. It selects no target, freezes no target, reserves no "
            "seed, issues no grant and runs no A1 cell."
        ),
    }
    doc["universe"] = {
        "id": ID + "-U1",
        "digest": a1_successor_schema.universe_digest(doc),
        "selector": "candidate-stream",
        "runner": "candidate-stream",
        "scorer": "candidate-stream",
    }
    return doc


def _preflight(doc: dict) -> dict:
    return a1_successor_preflight.evaluate(doc)


def _record(doc: dict) -> dict:
    return a1_successor_preflight.build(doc)


def _render(doc: dict, result: dict) -> str:
    lines = [
        "# A1 larger-universe candidate",
        "",
        "**ID:** `%s`  " % doc["id"],
        "**Status:** `%s`" % doc["status"],
        "",
        "**No target is selected, frozen or run.** This is a separately declared **28-tag**, 7-tags-per-cell world on the same four-cell law and 120-cycle horizon, evaluated through the no-arm preflight.",
        "",
        "## Construction",
        "",
        "The 16-tag world tops out at 64 independent candidate edges. This candidate fixes a **28-tag** pool before measuring K, with 7 tags per cell, 8 events per cycle, and the same first-36-cycle one-orientation rule. The edge count is structural; no K value chose the pool or the size.",
        "",
        "| Seed | Candidate edges | Independent | A | K | A&K |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["summaries"]:
        lines.append(
            "| `%d` | %d | %d | %d | %d | %d |" % (
                row["seed"], row["candidate_edges"], row["independent_edges"],
                row["A_available"], row["K_available"], row["A_and_K"],
            )
        )
    lines += [
        "",
        "## Preflight result",
        "",
        "**`%s`** — %d/%d seeds pass." % (
            result["status"], result["seeds_passed"], result["seeds_total"]),
        "",
        "| Seed | C1 ceiling | Gap to 60 | 20-row matching | Result |",
        "| ---: | ---: | ---: | ---: | --- |",
    ]
    for row in result["per_seed"]:
        lines.append(
            "| `%d` | %d | %d | %d | %s |" % (
                row["seed"], row["C1_ceiling"], row["gap_to_60"],
                row["target_matching"], "PASS" if row["pass"] else "FAIL",
            )
        )
    lines += [
        "",
        "**This is a candidate result, not a freeze or a run.** A PASS would only mean the declared universe clears the 60-row C1 gate and, if in scope, the 20-row matching; a new protocol, freeze, seed reservation and grant remain separate acts.",
        "",
        "**Not evidence:** a no-arm candidate and preflight. It selects no target, reserves no seed, freezes no target, issues no grant and runs no cell.",
        "",
        "## Reproduce",
        "",
        "```bash",
        "python -m benchmarks.a1_larger_universe --check",
        "python -m benchmarks.a1_larger_universe --self-test",
        "python -m benchmarks.a1_successor_schema --check",
        "```",
        "",
    ]
    return "\n".join(lines).rstrip("\n")


def render_preflight(doc: dict, result: dict) -> str:
    return _render(doc, result)


def write() -> int:
    doc = build()
    result = _preflight(doc)
    record = _record(doc)
    OUT_PATH.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(_render(doc, result) + "\n", encoding="utf-8")
    PREFLIGHT_PATH.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    PREFLIGHT_PAGE_PATH.write_text(
        a1_successor_preflight.render(record) + "\n", encoding="utf-8")
    schema_result = a1_successor_schema.validate(doc)
    print("candidate schema:", "clean" if schema_result["schema_ok"] else schema_result["schema"])
    print("preflight:", result["status"], "%d/%d" % (result["seeds_passed"], result["seeds_total"]))
    return 0 if schema_result["schema_ok"] else 1


def check() -> int:
    found: list[str] = []
    if not OUT_PATH.exists():
        found.append("candidate artifact is missing")
    elif not PAGE_PATH.exists():
        found.append("candidate page is missing")
    else:
        doc = json.loads(OUT_PATH.read_text(encoding="utf-8"))
        result = _preflight(doc)
        if PAGE_PATH.read_text(encoding="utf-8") != _render(doc, result) + "\n":
            found.append("candidate page is stale")
        schema_result = a1_successor_schema.validate(doc)
        if not schema_result["schema_ok"]:
            found.append("candidate schema refusals: %r" % schema_result["schema"])
    if not PREFLIGHT_PATH.exists() or not PREFLIGHT_PAGE_PATH.exists():
        found.append("preflight artifact or page is missing")
    elif OUT_PATH.exists():
        doc = json.loads(OUT_PATH.read_text(encoding="utf-8"))
        result = _preflight(doc)
        record = _record(doc)
        if json.loads(PREFLIGHT_PATH.read_text(encoding="utf-8")) != record:
            found.append("preflight artifact is stale")
        if PREFLIGHT_PAGE_PATH.read_text(encoding="utf-8") != (
                a1_successor_preflight.render(record) + "\n"):
            found.append("preflight page is stale")
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("A1 larger-universe candidate: clean")
    return 0


def self_test() -> list[str]:
    found: list[str] = []
    world = generate_world(SEEDS[0])
    if len(world["events"]) != CYCLES * EVENTS_PER_CYCLE:
        found.append("world length")
    if len(world["tag_pool"]) != TAGS_PER_CELL * 4 or len(set(world["tag_pool"])) != TAGS_PER_CELL * 4:
        found.append("tag pool")
    if any(len(text.split()) != 2 for text in world["events"][:10]):
        found.append("event shape")
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.write:
        return write()
    if args.check:
        return check()
    found = self_test()
    for problem in found:
        print("FAIL:", problem)
    if not found:
        print("A1 larger-universe candidate: self-test clean")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
