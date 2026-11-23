"""A1 adopted-block target competence — the C2/C8 numbers as a checked record.

The A1 design-viability report measured target competence on the superseded 2063
block, and the adopted-block figures (how many of the 2074 selected rows can carry
a C2 cell set and a C8 double block) lived only in a chat computation. The
competence-rule decision rests on those numbers, so they belong in a record with a
guard rather than in a message.

This module joins the committed no-arm availability record to the two committed
target selections. For each seed it counts how many of the four N=4 rows and the
twenty N=20 rows have both baseline paths present, how large the competent pool is,
and whether a clean block is possible at all. It runs no engine, selects nothing,
freezes nothing and changes no threshold: it reads three artifacts and counts.

The competence reading is the one the viability record states as an assumption —
baseline A *and* K present at the recorded no-arm baseline — and it carries the
same limit: C2 is a treatment gate, so the no-arm baseline cannot show that an
absent path stays absent under treatment. These counts are a target-selection
incompatibility, not a proof that C2 or C8 must fail.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
AVAILABILITY_PATH = DOCS / "a1_baseline_availability_adopted.json"
N4_PATH = DOCS / "a1_target_selection.json"
N20_PATH = DOCS / "a1_c8_target_selection.json"
OUT_PATH = DOCS / "a1_competence_adopted.json"
PAGE_PATH = DOCS / "A1-COMPETENCE-ADOPTED.md"
ID = "A1-COMPETENCE-ADOPTED-1"
DATE = "2026-11-15"
KIND = "a1_competence_adopted"

BLOCK = 2074
SEEDS = tuple(BLOCK * 10000 + 100 + i for i in range(1, 7))
REQUIRED = {"N4": 4, "N20": 20}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _selected(selection: dict, seed: int) -> list[str]:
    row = (selection.get("per_seed") or {}).get(str(seed)) or {}
    selected = row.get("selected")
    if not selected:
        raise ValueError("selection artifact has no selected rows for %d" % seed)
    return list(selected)


def _competent_rows(edges: list[str], flags: dict[str, tuple[bool, bool]],
                    recorded: set[str]) -> dict:
    """Count competent rows, and refuse to call an unrecorded edge incompetent."""
    missing = [edge for edge in edges if edge not in recorded]
    competent = [edge for edge in edges
                 if edge in recorded and flags[edge][0] and flags[edge][1]]
    return {
        "selected": len(edges),
        "competent": len(competent),
        "non_competent": [edge for edge in edges
                          if edge in recorded and not (flags[edge][0] and flags[edge][1])],
        "unrecorded": missing,
        "competent_edges": competent,
    }


def build() -> dict:
    availability = _load(AVAILABILITY_PATH)
    n4_selection = _load(N4_PATH)
    n20_selection = _load(N20_PATH)
    by_seed = {int(row["seed"]): row for row in availability.get("per_seed") or []}
    if set(by_seed) != set(SEEDS):
        raise ValueError("availability is not on the adopted block %d" % BLOCK)

    per_seed = []
    for seed in SEEDS:
        source = by_seed[seed]
        rows = source["rows"]
        flags = {row["edge"]: (bool(row["A"]), bool(row["K"])) for row in rows}
        recorded = set(flags)
        universe = set(source.get("candidate_edges") or []) or set(
            (n4_selection.get("per_seed") or {}).get(str(seed), {}).get("u") or [])
        if not universe:
            raise ValueError("candidate universe is not recorded for %d" % seed)
        pool = sorted(edge for edge in universe
                      if edge in recorded and flags[edge][0] and flags[edge][1])
        n4 = _competent_rows(_selected(n4_selection, seed), flags, recorded)
        n20 = _competent_rows(_selected(n20_selection, seed), flags, recorded)
        per_seed.append({
            "seed": seed,
            "universe": len(universe),
            "N4": {**n4,
                   "required": REQUIRED["N4"],
                   "shortfall": max(0, REQUIRED["N4"] - n4["competent"]),
                   "clean_block_possible": n4["competent"] == REQUIRED["N4"]},
            "N20": {**n20,
                    "required": REQUIRED["N20"],
                    "shortfall": max(0, REQUIRED["N20"] - n20["competent"]),
                    "clean_block_possible": n20["competent"] == REQUIRED["N20"],
                    "off_universe": [edge for edge in n20["competent_edges"]
                                     if edge not in universe]},
            "competent_pool": len(pool),
            "pool_sufficient_for_N20": len(pool) >= REQUIRED["N20"],
        })

    def _summary(key: str, required: int) -> dict:
        counts = [row[key]["competent"] for row in per_seed]
        return {
            "required_per_seed": required,
            "rows": sum(required for _ in per_seed),
            "competent": sum(counts),
            "per_seed_min": min(counts),
            "per_seed_max": max(counts),
            "seeds_with_clean_block": sum(1 for row in per_seed
                                          if row[key]["clean_block_possible"]),
            "seeds": len(per_seed),
        }

    pools = [row["competent_pool"] for row in per_seed]
    n4, n20 = _summary("N4", REQUIRED["N4"]), _summary("N20", REQUIRED["N20"])
    unrecorded = sum(len(row[key]["unrecorded"]) for row in per_seed
                     for key in ("N4", "N20"))
    off_universe = sum(len(row["N20"]["off_universe"]) for row in per_seed)
    return {
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": (
            "MEASURED — NO SEED SUPPLIES A CLEAN BLOCK UNDER THE CURRENT "
            "SELECTION; THE COMPETENT POOL DOES"),
        "block": BLOCK,
        "seed_block": list(SEEDS),
        "seed_block_note": (
            "the reserved A1-TWO-PATH-1 candidate block; this record names it and "
            "measures it only from committed no-arm artifacts"),
        "source_artifacts": {
            "availability": AVAILABILITY_PATH.relative_to(ROOT).as_posix(),
            "n4_selection": N4_PATH.relative_to(ROOT).as_posix(),
            "n20_selection": N20_PATH.relative_to(ROOT).as_posix(),
        },
        "reading": {
            "definition": (
                "a row is competent when both baseline paths, A and K, are present "
                "at the recorded no-arm baseline for that directed edge"),
            "induction_caveat": (
                "C2 is a treatment gate, not a no-arm gate. The no-arm baseline "
                "cannot show that a missing path stays missing under A- or K+ "
                "treatment, so these counts are a conditional target-selection "
                "incompatibility and not a proof that C2 or C8 must fail."),
            "inherited_from": "docs/A1-DESIGN-VIABILITY.md (c2_c8_competence)",
        },
        "N4": n4,
        "N20": n20,
        "competent_pool": {
            "per_seed_min": min(pools),
            "per_seed_max": max(pools),
            "required_for_N20": REQUIRED["N20"],
            "sufficient_on_every_seed": all(row["pool_sufficient_for_N20"]
                                            for row in per_seed),
        },
        "per_seed": per_seed,
        "integrity": {
            "unrecorded_selected_rows": unrecorded,
            "n20_rows_off_the_universe": off_universe,
            "note": (
                "a selected row with no availability record is not called "
                "incompetent; the count is zero here, which is what makes the "
                "competence figures exact rather than lower bounds"),
        },
        "finding": {
            "selection_not_supply": (
                "On the adopted block the current N=4 selection supplies %d competent "
                "rows of %d and the N=20 selection %d of %d, while the competent pool "
                "is %d-%d per seed against %d required. The block has no seed on which "
                "either selection can be adjudicated. The pool comparison is a "
                "count, not a construction: with the endpoint cap in force no "
                "twenty-row competent block exists on every adopted seed (see "
                "A1-COMPETENCE-FILTER-DRAFT-1)." % (n4["competent"], n4["rows"], n20["competent"],
                                n20["rows"], min(pools), max(pools),
                                REQUIRED["N20"])),
            "what_this_does_not_establish": (
                "that C8 would pass on a competent block, that the 2063 block "
                "behaves the same way per seed, or that any treatment effect "
                "exists. It counts availability, not outcomes."),
            "consequence_for_the_rule": (
                "under the drafted C2/C8 competence rule a block with any "
                "non-competent row is VOID rather than partial-scored, so both "
                "current selections would be void as recorded"),
        },
        "not_evidence": (
            "A read-only join of committed no-arm artifacts. It runs no A1 cell, "
            "selects no target, freezes no target, changes no threshold and "
            "measures no treatment effect."),
    }


def problems(doc: dict) -> list[str]:
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("kind")
    if doc.get("id") != ID:
        found.append("id")
    if doc.get("block") != BLOCK:
        found.append("block is not the adopted block")
    per_seed = doc.get("per_seed") or []
    if [row.get("seed") for row in per_seed] != list(SEEDS):
        return found + ["seed block"]
    for row in per_seed:
        for key in ("N4", "N20"):
            block = row.get(key) or {}
            required = REQUIRED[key]
            if block.get("required") != required:
                found.append("seed %s %s requirement" % (row["seed"], key))
            if block.get("selected") != required:
                found.append("seed %s %s does not select %d rows"
                             % (row["seed"], key, required))
            if block.get("competent", -1) + len(block.get("non_competent") or []) != required:
                found.append("seed %s %s counts do not partition the rows"
                             % (row["seed"], key))
            if block.get("unrecorded"):
                found.append("seed %s %s has unrecorded rows" % (row["seed"], key))
            if block.get("shortfall") != max(0, required - block.get("competent", 0)):
                found.append("seed %s %s shortfall" % (row["seed"], key))
            if block.get("clean_block_possible") != (block.get("competent") == required):
                found.append("seed %s %s clean-block flag" % (row["seed"], key))
        if len(row.get("competent_edges", row["N4"].get("competent_edges") or [])) != \
                row["N4"].get("competent"):
            found.append("seed %s N4 competent edge list" % row["seed"])
        if row.get("competent_pool", 0) < row["N20"].get("competent", 0):
            found.append("seed %s pool is smaller than its N20 competent rows"
                         % row["seed"])
        if row.get("pool_sufficient_for_N20") != (row.get("competent_pool", 0)
                                                  >= REQUIRED["N20"]):
            found.append("seed %s pool-sufficiency flag" % row["seed"])
    for key in ("N4", "N20"):
        summary = doc.get(key) or {}
        counts = [row[key]["competent"] for row in per_seed]
        if summary.get("competent") != sum(counts):
            found.append("%s total is not the per-seed sum" % key)
        if summary.get("per_seed_min") != min(counts):
            found.append("%s minimum is inconsistent" % key)
        if summary.get("per_seed_max") != max(counts):
            found.append("%s maximum is inconsistent" % key)
        if summary.get("seeds_with_clean_block") != sum(
                1 for row in per_seed if row[key]["clean_block_possible"]):
            found.append("%s clean-block count is inconsistent" % key)
        if summary.get("rows") != summary.get("required_per_seed", 0) * len(per_seed):
            found.append("%s row total is inconsistent" % key)
    pool = doc.get("competent_pool") or {}
    pools = [row["competent_pool"] for row in per_seed]
    if pool.get("per_seed_min") != min(pools) or pool.get("per_seed_max") != max(pools):
        found.append("pool range is inconsistent")
    if pool.get("sufficient_on_every_seed") != all(
            row["pool_sufficient_for_N20"] for row in per_seed):
        found.append("pool sufficiency is inconsistent")
    integrity = doc.get("integrity") or {}
    if integrity.get("unrecorded_selected_rows") != sum(
            len(row[key]["unrecorded"]) for row in per_seed for key in ("N4", "N20")):
        found.append("unrecorded-row count is inconsistent")
    return found


def _table(doc: dict) -> list[str]:
    lines = [
        "| Seed | Universe | N=4 competent | N=20 competent | Competent pool | Clean N=4 block | Clean N=20 block |",
        "| ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in doc["per_seed"]:
        lines.append("| %d | %d | **%d of 4** | **%d of 20** | %d | %s | %s |" % (
            row["seed"], row["universe"], row["N4"]["competent"],
            row["N20"]["competent"], row["competent_pool"],
            "yes" if row["N4"]["clean_block_possible"] else "no",
            "yes" if row["N20"]["clean_block_possible"] else "no"))
    return lines


def render(doc: dict) -> str:
    n4, n20 = doc["N4"], doc["N20"]
    pool = doc["competent_pool"]
    lines = [
        "# A1 adopted-block target competence — the C2/C8 numbers as a record",
        "",
        "**ID:** `%s`" % doc["id"],
        "",
        "**Date:** %s" % doc["date"],
        "",
        "**Status:** `%s`" % doc["status"],
        "",
        "**Block:** `%d` — `%s`" % (doc["block"], doc["seed_block_note"]),
        "",
        "## Reading",
        "",
        "A row is **competent** when both baseline paths, A and K, are present at the "
        "recorded no-arm baseline for that directed edge. %s" % doc["reading"][
            "induction_caveat"],
        "",
        "## Per seed",
        "",
    ]
    lines += _table(doc)
    lines += [
        "",
        "## Summary",
        "",
        "| Design | Rows | Competent | Per seed | Seeds with a clean block |",
        "| --- | ---: | ---: | --- | ---: |",
        "| **N=4** | %d | **%d** | %d-%d | **%d of %d** |" % (
            n4["rows"], n4["competent"], n4["per_seed_min"], n4["per_seed_max"],
            n4["seeds_with_clean_block"], n4["seeds"]),
        "| **N=20** | %d | **%d** | %d-%d | **%d of %d** |" % (
            n20["rows"], n20["competent"], n20["per_seed_min"], n20["per_seed_max"],
            n20["seeds_with_clean_block"], n20["seeds"]),
        "",
        "Competent pool: **%d-%d** per seed, %d required for an N=20 block; "
        "sufficient on every seed: **%s**." % (
            pool["per_seed_min"], pool["per_seed_max"], pool["required_for_N20"],
            pool["sufficient_on_every_seed"]),
        "",
        "## What the record establishes",
        "",
        doc["finding"]["selection_not_supply"],
        "",
        doc["finding"]["consequence_for_the_rule"],
        "",
        "**What this does not establish:** %s" % doc["finding"][
            "what_this_does_not_establish"],
        "",
        "## Integrity",
        "",
        "Selected rows with no availability record: **%d**. N=20 rows outside the "
        "candidate universe: **%d**. %s" % (
            doc["integrity"]["unrecorded_selected_rows"],
            doc["integrity"]["n20_rows_off_the_universe"],
            doc["integrity"]["note"]),
        "",
        "**Not evidence:** %s" % doc["not_evidence"],
        "",
        "Reproduce with `python -m benchmarks.a1_competence_adopted --write`; "
        "`--check` re-derives every figure from the source artifacts.",
    ]
    return "\n".join(lines)


def write() -> int:
    doc = build()
    OUT_PATH.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(doc) + "\n", encoding="utf-8")
    found = problems(doc)
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print("  N=4 competent %d/%d, N=20 competent %d/%d, pool %d-%d" % (
        doc["N4"]["competent"], doc["N4"]["rows"], doc["N20"]["competent"],
        doc["N20"]["rows"], doc["competent_pool"]["per_seed_min"],
        doc["competent_pool"]["per_seed_max"]))
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        print("FAIL: %s is missing" % OUT_PATH)
        return 1
    doc = json.loads(OUT_PATH.read_text(encoding="utf-8"))
    found = problems(doc)
    if doc != build():
        found.append("the record is stale against its source artifacts")
    if PAGE_PATH.read_text(encoding="utf-8") != render(doc) + "\n":
        found.append("the page is stale")
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("A1 adopted-block competence: clean; N=4 %d of %d, N=20 %d of %d, "
          "clean blocks %d/%d and %d/%d" % (
              doc["N4"]["competent"], doc["N4"]["rows"], doc["N20"]["competent"],
              doc["N20"]["rows"], doc["N4"]["seeds_with_clean_block"],
              doc["N4"]["seeds"], doc["N20"]["seeds_with_clean_block"],
              doc["N20"]["seeds"]))
    return 0


def _fixture() -> dict:
    """A small consistent document: the guard is exercised on input it must accept."""
    n4_counts = [1, 2, 3, 1, 3, 2]          # 12 of 24
    n20_counts = [7, 10, 11, 13, 10, 7]     # 58 of 120
    pools = [27, 31, 34, 40, 30, 28]
    rows = []
    for index, seed in enumerate(SEEDS):
        n4, n20 = n4_counts[index], n20_counts[index]
        rows.append({
            "seed": seed,
            "universe": 64,
            "competent_pool": pools[index],
            "pool_sufficient_for_N20": pools[index] >= REQUIRED["N20"],
            "N4": {"required": 4, "selected": 4, "competent": n4,
                   "non_competent": ["n4x>%d" % seed] * (4 - n4),
                   "unrecorded": [], "shortfall": 4 - n4,
                   "clean_block_possible": n4 == 4,
                   "competent_edges": ["n4c>%d" % (seed + i) for i in range(n4)]},
            "N20": {"required": 20, "selected": 20, "competent": n20,
                    "non_competent": ["n20x>%d" % seed] * (20 - n20),
                    "unrecorded": [], "shortfall": 20 - n20,
                    "clean_block_possible": n20 == 20, "off_universe": []},
        })
    return {
        "kind": KIND,
        "id": ID,
        "block": BLOCK,
        "N4": {"required_per_seed": 4, "rows": 24, "competent": sum(n4_counts),
               "per_seed_min": min(n4_counts), "per_seed_max": max(n4_counts),
               "seeds_with_clean_block": 0, "seeds": 6},
        "N20": {"required_per_seed": 20, "rows": 120,
                "competent": sum(n20_counts), "per_seed_min": min(n20_counts),
                "per_seed_max": max(n20_counts), "seeds_with_clean_block": 0,
                "seeds": 6},
        "competent_pool": {"per_seed_min": min(pools), "per_seed_max": max(pools),
                           "sufficient_on_every_seed": True},
        "integrity": {"unrecorded_selected_rows": 0},
        "per_seed": rows,
    }


def self_test() -> list[str]:
    found: list[str] = []
    doc = _fixture()
    if problems(doc):
        found.append("a consistent fixture was rejected: %s" % problems(doc))
    broken = json.loads(json.dumps(doc))
    broken["N20"]["competent"] += 1
    if not problems(broken):
        found.append("a total that is not the per-seed sum was accepted")
    broken = json.loads(json.dumps(doc))
    broken["per_seed"][0]["N4"]["clean_block_possible"] = True
    if not problems(broken):
        found.append("a clean-block flag that contradicts the count was accepted")
    broken = json.loads(json.dumps(doc))
    broken["per_seed"][0]["N4"]["unrecorded"] = ["missing>edge"]
    if not problems(broken):
        found.append("an unrecorded selected row was accepted")
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        found = self_test()
        if found:
            for problem in found:
                print("FAIL:", problem)
            return 1
        print("A1 adopted-block competence: self-test clean")
        return 0
    if args.write:
        return write()
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
