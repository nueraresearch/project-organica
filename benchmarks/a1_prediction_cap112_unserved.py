"""Which 16-tag candidate edges does A leave unserved at prediction cap 112?

The cap-112 decomposition covered the ten failing seeds and the edges missing
from the 60-row floor.  This traces every candidate edge in all twelve 16-tag
seeds and records, for each one:

* whether A serves it at cap 112;
* its best rank in the engine's other prediction candidates, with the
  prediction budget raised off during observation so the ranking is the
  engine's own count order rather than the returned window;
* whether it is a transition or cooccurrence candidate, and whether it fell
  inside that kind's share of the 112-slot budget;
* directed-pair support and the structural family (same / flip_p / flip_q /
  diagonal).

Unserved edges are then grouped by family and by where they sit in the
candidate order.  The observation is behaviour-neutral by construction: the
service only records, and every seed's A, K, A∩K and candidate counts must
match the committed cap-112 artifact or the build refuses.

No engine change, target, freeze, grant or A1 cell.

    python -m benchmarks.a1_prediction_cap112_unserved --write
    python -m benchmarks.a1_prediction_cap112_unserved --check
    python -m benchmarks.a1_prediction_cap112_unserved --self-test
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from benchmarks import a1_arms
from benchmarks import a1_k_dilution
from benchmarks import a1_k_supply_discriminator
from benchmarks import a1_prediction_cap_112 as cap
from benchmarks import a1_prediction_cap80_selection as selection
from benchmarks import engine_stamp
from benchmarks.acquisition_harness import (
    PHASE_ACQUISITION,
    _CountingMemoryService,
    _make_scratch_db,
)
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CAP_PATH = DOCS / "a1_prediction_cap_112.json"
SUPPLY_PATH = DOCS / "a1_k_carrier_supply.json"
OUT_PATH = DOCS / "a1_prediction_cap112_unserved.json"
PAGE_PATH = DOCS / "A1-PREDICTION-CAP112-UNSERVED.md"
ID = "A1-PREDICTION-CAP112-UNSERVED-1"
DATE = "2026-11-14"
KIND = "a1_prediction_cap112_unserved"
STATUS = ("DESCRIPTIVE — CAP-112 UNSERVED EDGE TRACE BY CANDIDATE ORDER AND FAMILY; "
          "NO TARGET, FREEZE, GRANT OR A1 CELL")
CAP = 112
LOOP_CAP = 120
SUPPORT_FLOOR = 5
BLOCKS = ("current-16", "fresh-16")
FAMILIES = ("same", "flip_p", "flip_q", "diagonal", "unknown")
RANK_BANDS = (
    ("1-56", 1, 56),
    ("57-112", 57, 112),
    ("113-224", 113, 224),
    ("225+", 225, None),
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _supply() -> dict[tuple[str, int], set[str]]:
    out = {}
    for seed in _load(SUPPLY_PATH)["seeds"]:
        summary = seed["summary"]
        out[(summary["block"], summary["seed"])] = {
            row["edge"] for row in seed["edges"]
        }
    return out


def _rank_band(rank: int | None) -> str:
    if rank is None:
        return "never"
    for label, low, high in RANK_BANDS:
        if rank >= low and (high is None or rank <= high):
            return label
    return "225+"


def _replay(task: tuple[str, int]) -> dict:
    label, seed = task
    candidates = _supply()[(label, seed)]
    world = cap.base._world(label, seed)
    supports = a1_k_supply_discriminator._support_counts(world)
    expected = next(
        row for row in _load(CAP_PATH)["rows"]
        if row["prediction_cap"] == CAP
        and row["block"] == label and row["seed"] == seed
    )
    db_path = _make_scratch_db("a1_cap112_unserved")
    memory = _CountingMemoryService(str(db_path))
    service = selection._TraceService(memory)
    service.MAX_PREDICTIONS = CAP
    service.MAX_LOOPS = LOOP_CAP
    a_edges: set[str] = set()
    k_edges: set[str] = set()
    acq_lo, acq_hi = PHASE_ACQUISITION
    event_lo = acq_lo * EVENTS_PER_CYCLE
    event_hi = acq_hi * EVENTS_PER_CYCLE
    try:
        for index, (text, trainable) in enumerate(
                zip(world["events"], world["trainable"])):
            if event_lo <= index < event_hi and not trainable:
                continue
            if index % EVENTS_PER_CYCLE == 0:
                memory.current_cycle = index // EVENTS_PER_CYCLE
            memory.store(text, event_type="observe",
                         source=a1_arms.ACQ_SOURCE
                         if event_lo <= index < event_hi else "env")
            if (index + 1) % EVENTS_PER_CYCLE != 0:
                continue
            report = service.run_sleep_cycle()
            a_edges |= {
                "%s>%s" % (prediction.source, prediction.target)
                for prediction in report.predictions
            } & candidates
            k_edges |= {
                "%s>%s" % edge for edge in a1_arms._carrier_edges(report)
            } & candidates
    finally:
        memory.close()
        db_path.unlink(missing_ok=True)
    if (len(candidates), len(a_edges), len(k_edges), len(a_edges & k_edges)) != (
            expected["candidate_edges"], expected["A"], expected["K"],
            expected["A_and_K"]):
        raise SystemExit(
            "REFUSED: %s/%d candidates/A/K/A∩K %d/%d/%d/%d, expected "
            "%d/%d/%d/%d" % (label, seed, len(candidates), len(a_edges),
                             len(k_edges), len(a_edges & k_edges),
                             expected["candidate_edges"], expected["A"],
                             expected["K"], expected["A_and_K"]))

    rows = []
    for edge in sorted(candidates):
        source, target = edge.split(">", 1)
        support = int(supports[(source, target)])
        served = edge in a_edges
        transition_rank = service.best_transition_rank.get(edge)
        cooccurrence_rank = service.best_cooccurrence_rank.get(edge)
        if served:
            kind = "served"
            rank = min(value for value in (transition_rank, cooccurrence_rank)
                       if value is not None)
            reason = None
        elif support < SUPPORT_FLOOR:
            kind, rank = "none", None
            reason = "support_below_prediction_floor"
        elif transition_rank is not None:
            kind, rank = "transition", transition_rank
            reason = ("transition_rank_below_budget"
                      if edge not in service.transition_in_budget
                      else "inside_returned_window")
        elif cooccurrence_rank is not None:
            kind, rank = "cooccurrence", cooccurrence_rank
            reason = ("cooccurrence_rank_below_quota"
                      if edge not in service.cooccurrence_in_budget
                      else "inside_returned_window")
        else:
            kind, rank = "none", None
            reason = "no_prediction_candidate"
        rows.append({
            "block": label,
            "seed": seed,
            "edge": edge,
            "support": support,
            "family": a1_k_dilution._cell_relation(world, edge),
            "served": served,
            "kind": kind,
            "rank": rank,
            "rank_band": _rank_band(rank),
            "reason": reason,
            "K112": edge in k_edges,
        })
    return {
        "block": label,
        "seed": seed,
        "candidate_edges": len(candidates),
        "A": len(a_edges),
        "K": len(k_edges),
        "A_and_K": len(a_edges & k_edges),
        "rows": rows,
    }


def build() -> dict:
    tasks = [(block, seed) for block in BLOCKS
             for seed in next(item["seeds"] for item in cap.BLOCKS
                              if item["label"] == block)]
    with ProcessPoolExecutor(max_workers=min(6, len(tasks))) as pool:
        runs = list(pool.map(_replay, tasks))
    rows = [row for run in runs for row in run["rows"]]
    unserved = [row for row in rows if not row["served"]]
    served = [row for row in rows if row["served"]]

    seed_rows = []
    for run in sorted(runs, key=lambda item: (item["block"], item["seed"])):
        group = [row for row in run["rows"] if not row["served"]]
        seed_rows.append({
            "block": run["block"],
            "seed": run["seed"],
            "candidate_edges": run["candidate_edges"],
            "A": run["A"],
            "unserved": len(group),
            "unserved_support_ge_5": sum(row["support"] >= SUPPORT_FLOOR
                                         for row in group),
            "unserved_families": dict(Counter(row["family"] for row in group)),
            "unserved_reasons": dict(Counter(row["reason"] for row in group)),
        })

    by_family = []
    for family in FAMILIES:
        group = [row for row in rows if row["family"] == family]
        if not group:
            continue
        missing = [row for row in group if not row["served"]]
        by_family.append({
            "family": family,
            "candidate_edges": len(group),
            "A": len(group) - len(missing),
            "A_rate": round((len(group) - len(missing)) / len(group), 6),
            "unserved": len(missing),
            "unserved_rate": round(len(missing) / len(group), 6),
        })
    by_kind = []
    for kind in ("transition", "cooccurrence", "none"):
        group = [row for row in unserved if row["kind"] == kind]
        by_kind.append({
            "kind": kind,
            "unserved": len(group),
            "unserved_families": dict(Counter(row["family"] for row in group)),
        })
    by_band = []
    for label, _, _ in RANK_BANDS:
        group = [row for row in unserved if row["rank_band"] == label]
        by_band.append({
            "band": label,
            "unserved": len(group),
            "unserved_families": dict(Counter(row["family"] for row in group)),
        })
    found = {
        "candidate_edges": len(rows),
        "served": len(served),
        "unserved": len(unserved),
        "unserved_support_ge_5": sum(row["support"] >= SUPPORT_FLOOR
                                     for row in unserved),
        "unserved_transitions": sum(row["kind"] == "transition"
                                    for row in unserved),
        "unserved_cooccurrences": sum(row["kind"] == "cooccurrence"
                                      for row in unserved),
        "unserved_no_candidate": sum(row["kind"] == "none"
                                     for row in unserved),
        "unserved_in_K": sum(row["K112"] for row in unserved),
        "reasons": dict(Counter(row["reason"] for row in unserved)),
        "families": dict(Counter(row["family"] for row in unserved)),
        "seeds": len(runs),
    }
    ranks = sorted(row["rank"] for row in unserved if row["rank"] is not None)
    found["rank_min"] = ranks[0] if ranks else None
    found["rank_median"] = (ranks[(len(ranks) - 1) // 2] if ranks else None)
    found["rank_max"] = ranks[-1] if ranks else None
    flip_q = sum(1 for row in unserved if row["family"] == "flip_q")
    flip_p = sum(1 for row in unserved if row["family"] == "flip_p")
    bands = {row["band"]: row["unserved"] for row in by_band}
    rates = {row["family"]: row["A_rate"] for row in by_family}
    reading = (
        "Across the twelve 16-tag seeds, A leaves %d of %d candidate edges "
        "unserved at cap 112 (%d served). The unserved edges are %s support-"
        "eligible on the stream (%d below the %d floor), so the window, not "
        "supply, is the binding constraint: %d are transition candidates, %d "
        "are cooccurrence candidates, and %d never became a candidate at all. "
        "Their candidate-order ranks run %s to %s (median %s): %d fall in the "
        "tail of the nominal window at ranks 57-112 and %d beyond it. That is "
        "the transition share talking, not the raw cap: transitions get the "
        "first half of the budget plus whatever the cooccurrence quota leaves "
        "unused, so an edge at rank 90 is still outside the window whenever "
        "cooccurrences claim their share. By family the unserved split is %s: "
        "flip_q supplies %d and flip_p %d, and the serve rates are %s, so the "
        "window loses flip_q edges %.1f times as fast as flip_p. %d of "
        "the unserved edges are already carried by K, so the shortfall is "
        "prediction-side, not carrier-side."
        % (
            found["unserved"], found["candidate_edges"], found["served"],
            "all" if found["unserved_support_ge_5"] == found["unserved"]
            else "most",
            found["unserved"] - found["unserved_support_ge_5"],
            SUPPORT_FLOOR,
            found["unserved_transitions"], found["unserved_cooccurrences"],
            found["unserved_no_candidate"],
            found["rank_min"], found["rank_max"],
            found["rank_median"],
            bands.get("57-112", 0),
            sum(1 for row in unserved
                if row["rank"] is not None and row["rank"] > CAP),
            ", ".join("%s %d" % (family, count) for family, count
                      in sorted(found["families"].items())),
            flip_q, flip_p,
            ", ".join("%s %.3f" % (family, rates[family])
                      for family in sorted(rates)),
            (1 - rates["flip_q"]) / (1 - rates["flip_p"]),
            found["unserved_in_K"],
        )
    )

    return engine_stamp.stamp({
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "not_a_result": True,
        "question": (
            "Which 16-tag candidate edges stay unserved at prediction cap "
            "112, where do they sit in the engine's candidate order, and "
            "which structural families do they belong to?"
        ),
        "definition": (
            "Every candidate edge in the twelve 16-tag seeds at loop cap 120 / "
            "prediction cap 112. Served means A contains the edge. Rank is "
            "the best position among transition or cooccurrence candidates "
            "with the prediction budget raised off during observation. Family "
            "is the structural cell relation used by the K-dilution report."
        ),
        "method": (
            "One no-arm replay per seed through a recording service that "
            "re-enumerates the full candidate list without truncation, then "
            "restores the real cap for selection. Every seed's candidate, A, "
            "K and A∩K counts must match the committed cap-112 artifact."
        ),
        "constants": {
            "cycles": cap.base.CYCLES,
            "loop_cap": LOOP_CAP,
            "prediction_cap": CAP,
            "support_floor": SUPPORT_FLOOR,
            "blocks": list(BLOCKS),
            "seeds": len(tasks),
            "rank_bands": [label for label, _, _ in RANK_BANDS],
        },
        "governance": {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none",
        },
        "reading": reading,
        "found": found,
        "by_family": by_family,
        "by_kind": by_kind,
        "by_rank_band": by_band,
        "seed_rows": seed_rows,
        "unserved_rows": unserved,
        "not_evidence": (
            "A descriptive trace of the cap-112 prediction window on twelve "
            "no-arm 16-tag seeds. Rank is the engine's candidate order under "
            "observed, signalled stop rules; it is not a counterfactual about "
            "what a different cap would serve. It is not a treatment, target "
            "viability or successor."
        ),
    })


def render(doc: dict) -> str:
    found = doc["found"]
    lines = [
        "# A1 cap-112 unserved edges",
        "",
        "Generated from `docs/a1_prediction_cap112_unserved.json` by "
        "`python -m benchmarks.a1_prediction_cap112_unserved --write`. Do not edit by hand.",
        "",
        "**Descriptive edge trace, not an A1 result.** Twelve 16-tag no-arm "
        "seeds at loop cap **120** / prediction cap **112**. No target, "
        "freeze, grant or A1 cell.",
        "",
        "## Result",
        "",
        doc["reading"],
        "",
        "## Totals",
        "",
        "| Candidate edges | Served | Unserved | Support ≥ %d | Transitions | Cooccurrences | No candidate | Already in K |" % SUPPORT_FLOOR,
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        "| %d | %d | %d | %d | %d | %d | %d | %d |" % (
            found["candidate_edges"], found["served"], found["unserved"],
            found["unserved_support_ge_5"], found["unserved_transitions"],
            found["unserved_cooccurrences"], found["unserved_no_candidate"],
            found["unserved_in_K"]),
        "",
        "## By family",
        "",
        "| Family | Candidates | Served | Serve rate | Unserved |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["by_family"]:
        lines.append("| %s | %d | %d | %.3f | %d |" % (
            row["family"], row["candidate_edges"], row["A"], row["A_rate"],
            row["unserved"]))
    lines += [
        "",
        "## Unserved by kind",
        "",
        "| Kind | Unserved | Families |",
        "| --- | ---: | --- |",
    ]
    for row in doc["by_kind"]:
        lines.append("| %s | %d | %s |" % (
            row["kind"], row["unserved"],
            ", ".join("%s %d" % (family, count)
                      for family, count in sorted(
                          row["unserved_families"].items())) or "-"))
    lines += [
        "",
        "## Unserved by candidate-order band",
        "",
        "| Band | Unserved | Families |",
        "| --- | ---: | --- |",
    ]
    for row in doc["by_rank_band"]:
        lines.append("| %s | %d | %s |" % (
            row["band"], row["unserved"],
            ", ".join("%s %d" % (family, count)
                      for family, count in sorted(
                          row["unserved_families"].items())) or "-"))
    lines += [
        "",
        "## Per seed",
        "",
        "| Block | Seed | Candidates | A | Unserved | Support ≥ %d | Families |" % SUPPORT_FLOOR,
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in doc["seed_rows"]:
        lines.append("| %s | %d | %d | %d | %d | %d | %s |" % (
            row["block"], row["seed"], row["candidate_edges"], row["A"],
            row["unserved"], row["unserved_support_ge_5"],
            ", ".join("%s %d" % (family, count) for family, count
                      in sorted(row["unserved_families"].items())) or "-"))
    lines += [
        "",
        "## Unserved edges",
        "",
        "| Block | Seed | Edge | Support | Family | Kind | Rank | Band | In K |",
        "| --- | ---: | --- | ---: | --- | --- | ---: | --- | --- |",
    ]
    for row in doc["unserved_rows"]:
        lines.append("| %s | %d | `%s` | %d | %s | %s | %s | %s | %s |" % (
            row["block"], row["seed"], row["edge"], row["support"],
            row["family"], row["kind"],
            "-" if row["rank"] is None else row["rank"], row["rank_band"],
            "yes" if row["K112"] else "no"))
    lines += [
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
    seed_rows = doc.get("seed_rows") or []
    if len(seed_rows) != 12:
        found.append("seed count")
    unserved = doc.get("unserved_rows") or []
    totals = doc.get("found") or {}
    if totals.get("unserved") != len(unserved):
        found.append("unserved total")
    if totals.get("candidate_edges") != sum(
            row.get("candidate_edges", 0) for row in seed_rows):
        found.append("candidate total")
    if totals.get("served") != sum(row.get("A", 0) for row in seed_rows):
        found.append("served total")
    for row in unserved:
        if row.get("served") is not False:
            found.append("served row in the unserved list")
        if row.get("rank") is None and row.get("rank_band") != "never":
            found.append("band for an unranked edge")
        if row.get("rank") is not None and row.get("rank") < 1:
            found.append("rank below one")
    for row in seed_rows:
        if row.get("unserved") != sum(
                row.get("unserved_families", {}).values()):
            found.append("per-seed family total for %r" % (row.get("seed"),))
    if PAGE_PATH.exists() and PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("the page is stale")
    return found


def self_test() -> list[str]:
    failures: list[str] = []
    if _rank_band(None) != "never":
        failures.append("an unranked edge has no band")
    if _rank_band(56) != "1-56" or _rank_band(57) != "57-112":
        failures.append("band boundaries")
    if _rank_band(400) != "225+":
        failures.append("open-ended band")
    if CAP != 112 or SUPPORT_FLOOR != 5:
        failures.append("cap or support floor changed")
    if set(FAMILIES) != {"same", "flip_p", "flip_q", "diagonal", "unknown"}:
        failures.append("family vocabulary")
    if math.floor(1.5) != 1:
        failures.append("unreachable sanity check")
    return failures


def write() -> int:
    body = build()
    OUT_PATH.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(body), encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print(body["reading"])
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        raise SystemExit("no unserved-edge artifact; run --write")
    body = _load(OUT_PATH)
    found = problems(body)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("cap-112 unserved edges: clean")
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
        print("unserved-edge self-test: clean")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
