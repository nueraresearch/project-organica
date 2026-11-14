"""At a 120-loop window, does A become the C1 binding path?

The loop-cap counterfactual raised candidate K from 714 to 1,498 by widening
the loop window.  If K is no longer scarce there, the C1 ceiling
``min(A_available, K_available)`` may be governed by A instead.

This read-only replay measures both paths on the same 18 candidate streams at
loop caps 15 and 120:

* A: candidate edges served by the prediction window at least once;
* K: candidate edges carried by a loop or dream at least once;
* C1 ceiling: ``min(A, K)``, with a floor of 60.

The cap-15 counts must match the committed predictor rows, and cap-120 K must
match the loop-cap counterfactual.  It runs no A1 cell, selects no target,
freezes nothing and issues no grant.

    python -m benchmarks.a1_c1_cap120 --write
    python -m benchmarks.a1_c1_cap120 --check
    python -m benchmarks.a1_c1_cap120 --self-test
"""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from benchmarks import a1_arms
from benchmarks import a1_larger_universe
from benchmarks import engine_stamp
from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.acquisition_harness import (
    PHASE_ACQUISITION,
    _CountingMemoryService,
    _make_scratch_db,
)
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SUPPLY_PATH = DOCS / "a1_k_carrier_supply.json"
PREDICTORS_PATH = DOCS / "a1_k_total_predictors.json"
COUNTERFACTUAL_PATH = DOCS / "a1_loop_cap_counterfactual.json"
OUT_PATH = DOCS / "a1_c1_cap120.json"
PAGE_PATH = DOCS / "A1-C1-CAP120.md"
ID = "A1-C1-CAP120-1"
DATE = "2026-11-14"
KIND = "a1_c1_cap120"
STATUS = "COUNTERFACTUAL C1 DIAGNOSTIC — AVAILABILITY ONLY; NO TARGET, FREEZE, GRANT OR A1 CELL"
CYCLES = 120
PREDICTION_CAP = 40
LOOP_CAPS = (15, 120)
C1_FLOOR = 60
BLOCKS = (
    {
        "label": "current-16",
        "tags": 16,
        "seeds": (20630101, 20630102, 20630103, 20630104, 20630105, 20630106),
        "world": lambda seed: generate_compositional_world(seed=seed, cycles=CYCLES),
    },
    {
        "label": "fresh-16",
        "tags": 16,
        "seeds": (20650101, 20650102, 20650103, 20650104, 20650105, 20650106),
        "world": lambda seed: generate_compositional_world(seed=seed, cycles=CYCLES),
    },
    {
        "label": "larger-28",
        "tags": 28,
        "seeds": (20660101, 20660102, 20660103, 20660104, 20660105, 20660106),
        "world": a1_larger_universe.generate_world,
    },
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sources() -> tuple[dict, dict, dict]:
    supply = _load(SUPPLY_PATH)
    predictors = _load(PREDICTORS_PATH)
    counterfactual = _load(COUNTERFACTUAL_PATH)
    candidates = {}
    for seed in supply["seeds"]:
        summary = seed["summary"]
        candidates[(summary["block"], summary["seed"])] = {
            "edges": {row["edge"] for row in seed["edges"]},
            "K": {row["edge"] for row in seed["edges"] if row["K"]},
        }
    expected = {
        (row["block"], row["seed"]): {
            "A": row["A_available"], "K": row["K_available"],
        }
        for row in predictors["seed_rows"]
    }
    counterfactual_k = {
        (row["block"], row["seed"]): row["candidate_K"]
        for row in counterfactual["rows"] if row["cap"] == 120
    }
    return candidates, expected, counterfactual_k


def _world(label: str, seed: int) -> dict:
    for block in BLOCKS:
        if block["label"] == label:
            return block["world"](seed)
    raise KeyError(label)


def _replay(task: tuple[str, int, int]) -> dict:
    label, seed, cap = task
    source, _, _ = _sources()
    candidates = source[(label, seed)]["edges"]
    world = _world(label, seed)
    db_path = _make_scratch_db("a1_c1_cap120")
    memory = _CountingMemoryService(str(db_path))
    service = a1_arms.A1ArmSleepService(memory)
    service.MAX_PREDICTIONS = PREDICTION_CAP
    service.MAX_LOOPS = cap
    a_edges: set[str] = set()
    k_edges: set[str] = set()
    acq_lo, acq_hi = PHASE_ACQUISITION
    event_lo = acq_lo * EVENTS_PER_CYCLE
    event_hi = acq_hi * EVENTS_PER_CYCLE
    try:
        for index, (text, trainable) in enumerate(
                zip(world["events"], world["trainable"])):
            in_acq = event_lo <= index < event_hi
            if in_acq and not trainable:
                continue
            if index % EVENTS_PER_CYCLE == 0:
                memory.current_cycle = index // EVENTS_PER_CYCLE
            memory.store(text, event_type="observe",
                         source=a1_arms.ACQ_SOURCE if in_acq else "env")
            if (index + 1) % EVENTS_PER_CYCLE != 0:
                continue
            report = service.run_sleep_cycle()
            predictions = {
                "%s>%s" % (prediction.source, prediction.target)
                for prediction in report.predictions
            }
            carried = {"%s>%s" % edge for edge in a1_arms._carrier_edges(report)}
            a_edges |= predictions & candidates
            k_edges |= carried & candidates
    finally:
        memory.close()
        db_path.unlink(missing_ok=True)
    both = a_edges & k_edges
    ceiling = min(len(a_edges), len(k_edges))
    if len(a_edges) < len(k_edges):
        binding = "A"
    elif len(k_edges) < len(a_edges):
        binding = "K"
    else:
        binding = "both"
    return {
        "block": label,
        "seed": seed,
        "cap": cap,
        "candidate_edges": len(candidates),
        "A": len(a_edges),
        "K": len(k_edges),
        "A_and_K": len(both),
        "C1_ceiling": ceiling,
        "gap_to_60": C1_FLOOR - ceiling,
        "C1_floor_pass": ceiling >= C1_FLOOR,
        "binding": binding,
        "A_edges": sorted(a_edges),
        "K_edges": sorted(k_edges),
    }


def build() -> dict:
    candidates, expected, counterfactual_k = _sources()
    tasks = [
        (block["label"], seed, cap)
        for block in BLOCKS
        for seed in block["seeds"]
        for cap in LOOP_CAPS
    ]
    with ProcessPoolExecutor(max_workers=min(6, len(tasks))) as pool:
        raw = list(pool.map(_replay, tasks))
    by_key = {(row["block"], row["seed"], row["cap"]): row for row in raw}
    for (label, seed) in candidates:
        control = by_key[(label, seed, 15)]
        if control["A"] != expected[(label, seed)]["A"]:
            raise SystemExit(
                "REFUSED: control %s/%d A %d, expected %d"
                % (label, seed, control["A"], expected[(label, seed)]["A"]))
        if control["K"] != expected[(label, seed)]["K"]:
            raise SystemExit(
                "REFUSED: control %s/%d K %d, expected %d"
                % (label, seed, control["K"], expected[(label, seed)]["K"]))
        widened = by_key[(label, seed, 120)]
        if widened["K"] != counterfactual_k[(label, seed)]:
            raise SystemExit(
                "REFUSED: cap 120 %s/%d K %d, counterfactual %d"
                % (label, seed, widened["K"], counterfactual_k[(label, seed)]))
        if control["A_edges"] != widened["A_edges"]:
            raise SystemExit(
                "REFUSED: %s/%d A changed with the loop cap" % (label, seed))
    rows = []
    for row in sorted(raw, key=lambda item: (item["cap"], item["block"], item["seed"])):
        rows.append({key: value for key, value in row.items()
                     if key not in ("A_edges", "K_edges")})
    summaries = []
    for cap in LOOP_CAPS:
        group = [row for row in rows if row["cap"] == cap]
        summaries.append({
            "cap": cap,
            "seeds": len(group),
            "A_total": sum(row["A"] for row in group),
            "K_total": sum(row["K"] for row in group),
            "C1_ceiling_min": min(row["C1_ceiling"] for row in group),
            "C1_ceiling_max": max(row["C1_ceiling"] for row in group),
            "C1_pass": sum(row["C1_floor_pass"] for row in group),
            "binding_A": sum(row["binding"] == "A" for row in group),
            "binding_K": sum(row["binding"] == "K" for row in group),
            "binding_both": sum(row["binding"] == "both" for row in group),
        })
    blocks = []
    for block in BLOCKS:
        entry = {"label": block["label"], "tags": block["tags"]}
        for cap in LOOP_CAPS:
            group = [row for row in rows
                     if row["block"] == block["label"] and row["cap"] == cap]
            entry[str(cap)] = {
                "candidate_edges": sum(row["candidate_edges"] for row in group),
                "A": sum(row["A"] for row in group),
                "K": sum(row["K"] for row in group),
                "C1_ceiling_min": min(row["C1_ceiling"] for row in group),
                "C1_ceiling_max": max(row["C1_ceiling"] for row in group),
                "C1_pass": sum(row["C1_floor_pass"] for row in group),
                "binding_A": sum(row["binding"] == "A" for row in group),
                "binding_K": sum(row["binding"] == "K" for row in group),
            }
        blocks.append(entry)
    summary_120 = next(row for row in summaries if row["cap"] == 120)
    if summary_120["binding_A"] == summary_120["seeds"]:
        reading = (
            "At cap 120, A is the C1 binding path on every seed. Widening the "
            "loop window removes K as the blocker; the remaining C1 ceiling is "
            "the prediction path."
        )
    elif summary_120["binding_A"] > summary_120["binding_K"]:
        reading = (
            "At cap 120, A is the C1 binding path on most seeds; widening the "
            "loop window removes K as the primary blocker."
        )
    elif summary_120["binding_K"] > 0:
        reading = (
            "At cap 120, K remains the binding path on at least some seeds; the "
            "loop window is not sufficient to explain the C1 ceiling."
        )
    else:
        reading = (
            "At cap 120, A and K tie on every seed; the C1 ceiling has no single "
            "binding path."
        )
    return engine_stamp.stamp({
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "not_a_result": True,
        "question": (
            "At loop cap 120, does A become the binding path in the C1 ceiling "
            "min(A_available, K_available)?"
        ),
        "definition": (
            "A and K availability over the same 18 candidate streams at loop caps "
            "15 and 120, with the prediction cap fixed at 40, and the C1 ceiling "
            "min(A,K) against the 60-row floor."
        ),
        "method": (
            "One no-arm replay per seed and cap. Cap-15 A/K counts must match the "
            "committed predictor rows; cap-120 K must match the loop-cap "
            "counterfactual; and the A edge set must be identical at both caps."
        ),
        "constants": {
            "cycles": CYCLES,
            "prediction_cap": PREDICTION_CAP,
            "loop_caps": list(LOOP_CAPS),
            "c1_floor": C1_FLOOR,
        },
        "governance": {
            "freeze": False,
            "grant": False,
            "run": False,
            "authorization": "none",
        },
        "reading": reading,
        "summaries": summaries,
        "by_block": blocks,
        "rows": rows,
        "not_evidence": (
            "An availability-only counterfactual on 18 no-arm seeds. It measures "
            "the C1 ceiling, not a treatment effect, target viability or a "
            "successor. Widening the loop window is an engine-behaviour change, "
            "not an A1 cell; no target, freeze, grant or run follows."
        ),
    })


def render(doc: dict) -> str:
    summaries = {row["cap"]: row for row in doc["summaries"]}
    control = summaries[15]
    widened = summaries[120]
    lines = [
        "# A1 C1 ceiling at loop cap 120",
        "",
        "Generated from `docs/a1_c1_cap120.json` by "
        "`python -m benchmarks.a1_c1_cap120 --write`. Do not edit by hand.",
        "",
        "**Availability-only counterfactual, not an A1 result.** Same 18 candidate "
        "streams at loop caps **15/120**, prediction cap fixed at **40**. No target, "
        "freeze, grant or A1 cell.",
        "",
        "## Result",
        "",
        doc["reading"],
        "",
        "| Loop cap | A total | K total | C1 ceiling range | Pass 60 | Binding A | Binding K | Tie |",
        "| ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for cap in (15, 120):
        row = summaries[cap]
        lines.append("| %d | %d | %d | %d-%d | %d/18 | %d | %d | %d |" % (
            cap, row["A_total"], row["K_total"], row["C1_ceiling_min"],
            row["C1_ceiling_max"], row["C1_pass"], row["binding_A"],
            row["binding_K"], row["binding_both"]))
    lines += [
        "",
        "The cap-15 control reproduces the committed A/K counts; cap-120 K "
        "reproduces the loop-cap counterfactual. The A edge set is identical at "
        "both caps, so the loop window changes K without changing which edges are "
        "served.",
        "",
        "## Per block",
        "",
        "| Block | Candidates | A at 15 | K at 15 | C1 at 15 | A at 120 | K at 120 | C1 at 120 | Pass at 120 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for block in doc["by_block"]:
        low = block["15"]
        high = block["120"]
        lines.append("| %s | %d | %d | %d | %d-%d | %d | %d | %d-%d | %d/6 |" % (
            block["label"], low["candidate_edges"], low["A"], low["K"],
            low["C1_ceiling_min"], low["C1_ceiling_max"], high["A"], high["K"],
            high["C1_ceiling_min"], high["C1_ceiling_max"], high["C1_pass"]))
    lines += [
        "",
        "## Per-seed rows at cap 120",
        "",
        "| Block | Seed | Candidates | A | K | A∩K | C1 ceiling | Gap to 60 | Binding | Pass |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in doc["rows"]:
        if row["cap"] != 120:
            continue
        lines.append("| %s | %d | %d | %d | %d | %d | %d | %d | %s | %s |" % (
            row["block"], row["seed"], row["candidate_edges"], row["A"], row["K"],
            row["A_and_K"], row["C1_ceiling"], row["gap_to_60"], row["binding"],
            "yes" if row["C1_floor_pass"] else "no"))
    lines += [
        "",
        "## Reading",
        "",
        "A widening loop window removes K as the C1 blocker in the 16-tag blocks "
        "and in most of the 28-tag block. The remaining ceiling is the prediction "
        "path A, which is unchanged by the loop cap. This is a reason to test the "
        "prediction window next; it is not evidence that A can clear 60, and it is "
        "not an A1 run.",
        "",
        "## What this does not claim",
        "",
        doc["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def problems(doc: dict | None = None) -> list[str]:
    doc = _load(OUT_PATH) if doc is None else doc
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("artifact kind")
    if doc.get("not_a_result") is not True:
        found.append("the artifact does not say it is not a result")
    if engine_stamp.missing(doc):
        found.append("the artifact is not fully stamped")
    if doc.get("governance") != {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none"}:
        found.append("governance changed")
    rows = doc.get("rows") or []
    if len(rows) != 36:
        found.append("%d rows, expected 36" % len(rows))
    for row in rows:
        if row.get("C1_ceiling") != min(row.get("A", -1), row.get("K", -1)):
            found.append("C1 ceiling at %r" % ((row.get("block"), row.get("seed"),
                                                 row.get("cap")),))
        if row.get("gap_to_60") != C1_FLOOR - row.get("C1_ceiling", -1):
            found.append("gap at %r" % ((row.get("block"), row.get("seed"),
                                         row.get("cap")),))
        expected = ("A" if row.get("A", 0) < row.get("K", 0)
                    else "K" if row.get("K", 0) < row.get("A", 0)
                    else "both")
        if row.get("binding") != expected:
            found.append("binding at %r" % ((row.get("block"), row.get("seed"),
                                              row.get("cap")),))
    for summary in doc.get("summaries") or []:
        group = [row for row in rows if row["cap"] == summary["cap"]]
        if summary.get("A_total") != sum(row["A"] for row in group):
            found.append("A total at cap %s" % summary.get("cap"))
        if summary.get("K_total") != sum(row["K"] for row in group):
            found.append("K total at cap %s" % summary.get("cap"))
        if summary.get("C1_pass") != sum(row["C1_floor_pass"] for row in group):
            found.append("C1 pass count at cap %s" % summary.get("cap"))
    if PAGE_PATH.exists() and PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("the page is stale")
    return found


def self_test() -> list[str]:
    failures: list[str] = []
    def row(a, k, cap=120):
        return {
            "block": "x", "seed": 1, "cap": cap, "candidate_edges": 10,
            "A": a, "K": k, "A_and_K": min(a, k),
            "C1_ceiling": min(a, k), "gap_to_60": 60 - min(a, k),
            "C1_floor_pass": min(a, k) >= 60,
            "binding": "A" if a < k else "K" if k < a else "both",
        }
    r = row(44, 64)
    if r["C1_ceiling"] != 44 or r["binding"] != "A":
        failures.append("A must bind when A<K")
    r = row(64, 44)
    if r["C1_ceiling"] != 44 or r["binding"] != "K":
        failures.append("K must bind when K<A")
    r = row(44, 44)
    if r["binding"] != "both":
        failures.append("equal paths must tie")
    return failures


def write() -> int:
    body = build()
    OUT_PATH.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(body), encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print(body["reading"])
    for row in body["summaries"]:
        print("cap %d: A %d, K %d, C1 pass %d/18, binding A/K/tie %d/%d/%d"
              % (row["cap"], row["A_total"], row["K_total"], row["C1_pass"],
                 row["binding_A"], row["binding_K"], row["binding_both"]))
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        raise SystemExit("no C1 cap-120 artifact; run --write")
    body = _load(OUT_PATH)
    found = problems(body)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("C1 cap-120: clean")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.write:
        return write()
    if args.self_test:
        found = self_test()
        if found:
            raise SystemExit("FAIL: " + "; ".join(found))
        print("C1 cap-120 self-test: clean")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
