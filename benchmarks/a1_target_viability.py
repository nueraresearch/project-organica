"""A1 target viability: N4 vs N20 carrier-missing rows and C2 exposure.

This is a read-only report over existing no-arm artifacts.  It does not run a
cell, freeze a target, issue a grant or score C2.  It asks a narrower pre-freeze
question: can the registered target rows support C2's four manipulated cells?

C2 requires, per target row and per seed:

* ``A-K+``:  A blocked, K present;
* ``A+K-``:  A present, K blocked;
* ``Y_MINUS_A+K+``: Y blocked, A present, K present;
* ``Y_MINUS_A-K+``: Y blocked, A blocked, K present.

A target with no observed carrier fails the three K-requiring cells.  A target
with no observed admission also fails the two A-requiring cells.  Because C2
is an all-row, per-seed gate, one exposed row fails the seed.

    python -m benchmarks.a1_target_viability --write
    python -m benchmarks.a1_target_viability --check
    python -m benchmarks.a1_target_viability --self-test
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
N4_PATH = DOCS / "a1_target_selection.json"
N20_PATH = DOCS / "a1_c8_target_selection.json"
C5_PATH = DOCS / "a1_c5_target_timing.json"
BASELINE_PATH = DOCS / "a1_baseline_availability.json"
OUT_PATH = DOCS / "a1_target_viability.json"
PAGE_PATH = DOCS / "A1-TARGET-VIABILITY.md"
ID = "A1-TARGET-VIABILITY-1"
DATE = "2026-11-14"
KIND = "a1_target_viability"
N4 = "N4"
N20 = "N20"
SEEDS = (20630101, 20630102, 20630103, 20630104, 20630105, 20630106)
C2_CELLS = 4
C2_K_REQUIRED = 3
C2_A_REQUIRED = 2


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _selected(path: Path) -> dict[int, list[str]]:
    doc = _load(path)
    return {
        seed: list((doc.get("per_seed") or {}).get(str(seed), {}).get("selected") or [])
        for seed in SEEDS
    }


def _c5_rows() -> dict[tuple[int, str], dict]:
    doc = _load(C5_PATH)
    found: dict[tuple[int, str], dict] = {}
    for group in doc.get("per_seed") or []:
        seed = int(group["seed"])
        for row in group.get("rows") or []:
            found[(seed, str(row["edge"]))] = row
    return found


def _baseline() -> dict[tuple[int, str], dict]:
    doc = _load(BASELINE_PATH)
    found: dict[tuple[int, str], dict] = {}
    for group in doc.get("per_seed") or []:
        seed = int(group["seed"])
        for row in group.get("rows") or []:
            found[(seed, str(row["edge"]))] = row
    return found


def c2_failing_cells(a_available: bool, k_available: bool) -> int:
    """How many of C2's four target cells cannot pass from this baseline.

    The filters are assumed to work: A- blocks admission, K- blocks the
    carrier, Y- blocks assertion.  The only question is whether the required
    unmanipulated path exists to be observed.
    """
    if k_available and a_available:
        return 0
    if k_available and not a_available:
        return C2_A_REQUIRED  # A+K- and Y_MINUS_A+K+
    if a_available and not k_available:
        return C2_K_REQUIRED  # A-K+, Y_MINUS_A+K+, Y_MINUS_A-K+
    return C2_CELLS         # both required paths are absent


def _row(seed: int, edge: str, baseline: dict, timing: dict) -> dict:
    a = bool(baseline.get("A"))
    k = bool(baseline.get("K"))
    carrier_cycle = (timing or {}).get("carrier_cycle")
    return {
        "edge": edge,
        "A": a,
        "K": k,
        "Y": bool(baseline.get("Y")),
        "carrier_cycle": carrier_cycle,
        "carrier_missing": not k,
        "A_missing": not a,
        "c2_failing_cells": c2_failing_cells(a, k),
        "fully_c2_viable": bool(a and k),
    }


def _summarise(design: str, selected: dict[int, list[str]],
               baseline: dict, timing: dict) -> dict:
    per_seed = []
    for seed in SEEDS:
        rows = []
        for edge in selected[seed]:
            base = baseline.get((seed, edge))
            run = timing.get((seed, edge))
            if base is None or run is None:
                raise ValueError("seed %d target %s is missing from the source artifacts"
                                 % (seed, edge))
            if (run.get("carrier_cycle") is None) != (not bool(base.get("K"))):
                raise ValueError("seed %d target %s carrier sources disagree" % (seed, edge))
            rows.append(_row(seed, edge, base, run))
        carrier_missing = sum(1 for row in rows if row["carrier_missing"])
        a_missing = sum(1 for row in rows if row["A_missing"])
        both_missing = sum(1 for row in rows if row["A_missing"] and row["carrier_missing"])
        a_only_missing = sum(1 for row in rows if row["A_missing"] and not row["carrier_missing"])
        failing = sum(row["c2_failing_cells"] for row in rows)
        total_cells = C2_CELLS * len(rows)
        per_seed.append({
            "seed": seed,
            "target_rows": len(rows),
            "carrier_missing": carrier_missing,
            "carrier_missing_rate": round(carrier_missing / len(rows), 6) if rows else 0.0,
            "A_missing": a_missing,
            "both_missing": both_missing,
            "A_only_missing": a_only_missing,
            "fully_c2_viable": sum(1 for row in rows if row["fully_c2_viable"]),
            "c2_failing_cells": failing,
            "c2_cells_total": total_cells,
            "c2_failing_rate": round(failing / total_cells, 6) if total_cells else 0.0,
            "seeds_with_missing": 1 if carrier_missing else 0,
            "c2_seed_viable": bool(rows and failing == 0),
            "rows": rows,
        })
    target_rows = sum(row["target_rows"] for row in per_seed)
    missing = sum(row["carrier_missing"] for row in per_seed)
    a_missing = sum(row["A_missing"] for row in per_seed)
    both = sum(row["both_missing"] for row in per_seed)
    a_only = sum(row["A_only_missing"] for row in per_seed)
    failing = sum(row["c2_failing_cells"] for row in per_seed)
    total_cells = sum(row["c2_cells_total"] for row in per_seed)
    return {
        "design": design,
        "per_seed": per_seed,
        "totals": {
            "target_rows": target_rows,
            "carrier_missing": missing,
            "carrier_missing_rate": round(missing / target_rows, 6) if target_rows else 0.0,
            "A_missing": a_missing,
            "both_missing": both,
            "A_only_missing": a_only,
            "fully_c2_viable": sum(row["fully_c2_viable"] for row in per_seed),
            "c2_failing_cells": failing,
            "c2_cells_total": total_cells,
            "c2_failing_rate": round(failing / total_cells, 6) if total_cells else 0.0,
            "seeds_with_missing": sum(row["seeds_with_missing"] for row in per_seed),
            "c2_viable_seeds": sum(1 for row in per_seed if row["c2_seed_viable"]),
            "c2_failing_seeds": sum(1 for row in per_seed if not row["c2_seed_viable"]),
        },
    }


def build() -> dict:
    baseline = _baseline()
    timing = _c5_rows()
    n4 = _summarise(N4, _selected(N4_PATH), baseline, timing)
    n20 = _summarise(N20, _selected(N20_PATH), baseline, timing)
    for seed in SEEDS:
        n4_edges = {row["edge"] for row in n4["per_seed"][SEEDS.index(seed)]["rows"]}
        n20_edges = {row["edge"] for row in n20["per_seed"][SEEDS.index(seed)]["rows"]}
        if not n4_edges <= n20_edges:
            raise ValueError("seed %d N4 is not a subset of N20" % seed)
    t4, t20 = n4["totals"], n20["totals"]
    added_rows = t20["target_rows"] - t4["target_rows"]
    added_missing = t20["carrier_missing"] - t4["carrier_missing"]
    added_cells = t20["c2_failing_cells"] - t4["c2_failing_cells"]
    n4_missing = {
        (row["seed"], r["edge"]) for row in n4["per_seed"] for r in row["rows"]
        if r["carrier_missing"]
    }
    n20_missing = {
        (row["seed"], r["edge"]) for row in n20["per_seed"] for r in row["rows"]
        if r["carrier_missing"]
    }
    return {
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": (
            "FLAGGED — C2 NOT PASSABLE UNDER EITHER TARGET SET"
            if t4["c2_viable_seeds"] == 0 and t20["c2_viable_seeds"] == 0
            else "CHECK — C2 VIABILITY DIFFERS BETWEEN N4 AND N20"
        ),
        "source_artifacts": {
            "N4_targets": N4_PATH.relative_to(ROOT).as_posix(),
            "N20_targets": N20_PATH.relative_to(ROOT).as_posix(),
            "carrier_timing": C5_PATH.relative_to(ROOT).as_posix(),
            "baseline_availability": BASELINE_PATH.relative_to(ROOT).as_posix(),
        },
        "c2_rule": (
            "C2 requires every target row in A-K+ to keep K, in A+K- to keep A, "
            "in Y_MINUS_A+K+ to keep A and K while Y is blocked, and in "
            "Y_MINUS_A-K+ to keep K while A and Y are blocked. A row that cannot "
            "meet a cell fails the seed because C2 is all-row and per-seed."
        ),
        "designs": {N4: n4, N20: n20},
        "comparison": {
            "added_rows": added_rows,
            "added_missing_carriers": added_missing,
            "added_missing_rate": round(added_missing / added_rows, 6) if added_rows else 0.0,
            "retained_N4_missing_carriers": len(n4_missing & n20_missing),
            "added_c2_failing_cells": added_cells,
            "carrier_missing_rate_delta": round(
                t20["carrier_missing_rate"] - t4["carrier_missing_rate"], 6),
            "c2_failing_rate_delta": round(
                t20["c2_failing_rate"] - t4["c2_failing_rate"], 6),
            "C2_viable_seed_delta": t20["c2_viable_seeds"] - t4["c2_viable_seeds"],
            "added_rows_are_C2_viable": added_rows - added_missing,
            "disposition": (
                "N20 does not reduce C2 exposure. It adds rows and failing cells, "
                "retains every N4 carrier-missing row, and leaves both designs with "
                "no C2-viable seed. The C2 gate is therefore not adjudicable under "
                "either target set as currently selected."
            ),
        },
        "disposition": (
            "Do not treat N20 as a C2 repair. If C2 must be adjudicable, the target "
            "block needs a new pre-outcome viability criterion; a post-outcome swap "
            "is not permitted. Until then, record C2 as not adjudicable rather than "
            "freezing a target set that cannot pass it."
        ),
        "not_evidence": (
            "A read-only target-viability report over no-arm artifacts. It runs no "
            "A1 cell, freezes no target, makes no causal or capability claim, and "
            "does not measure C2 or any treatment effect."
        ),
    }


def problems(doc: dict) -> list[str]:
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("report kind")
    if doc.get("id") != ID:
        found.append("report id")
    designs = doc.get("designs") or {}
    if set(designs) != {N4, N20}:
        found.append("design block is not N4/N20")
        return found
    for key in (N4, N20):
        design = designs[key]
        rows = design.get("per_seed") or []
        if [row.get("seed") for row in rows] != list(SEEDS):
            found.append("%s seed block changed" % key)
            continue
        for row in rows:
            if row.get("target_rows") != len(row.get("rows") or []):
                found.append("%s seed %s row count is inconsistent" % (key, row.get("seed")))
            if row.get("carrier_missing") != sum(
                    1 for item in row.get("rows") or [] if item.get("carrier_missing")):
                found.append("%s seed %s missing count is inconsistent" % (key, row.get("seed")))
            if row.get("c2_failing_cells") != sum(
                    item.get("c2_failing_cells", 0) for item in row.get("rows") or []):
                found.append("%s seed %s C2 count is inconsistent" % (key, row.get("seed")))
            if row.get("c2_seed_viable") != (row.get("c2_failing_cells") == 0):
                found.append("%s seed %s C2 viability is inconsistent" % (key, row.get("seed")))
            for item in row.get("rows") or []:
                if item.get("carrier_missing") != (not item.get("K")):
                    found.append("%s seed %s edge %s carrier flag is inconsistent"
                                 % (key, row.get("seed"), item.get("edge")))
                if item.get("c2_failing_cells") != c2_failing_cells(
                        bool(item.get("A")), bool(item.get("K"))):
                    found.append("%s seed %s edge %s C2 cells are inconsistent"
                                 % (key, row.get("seed"), item.get("edge")))
        totals = design.get("totals") or {}
        if totals.get("target_rows") != sum(
                row.get("target_rows", 0) for row in rows):
            found.append("%s total rows are inconsistent" % key)
        if totals.get("carrier_missing") != sum(
                row.get("carrier_missing", 0) for row in rows):
            found.append("%s total missing carriers are inconsistent" % key)
        if totals.get("c2_failing_cells") != sum(
                row.get("c2_failing_cells", 0) for row in rows):
            found.append("%s total C2 failures are inconsistent" % key)
        if totals.get("c2_viable_seeds") != sum(
                1 for row in rows if row.get("c2_seed_viable")):
            found.append("%s C2-viable seed count is inconsistent" % key)
    comparison = doc.get("comparison") or {}
    t4 = designs[N4]["totals"]
    t20 = designs[N20]["totals"]
    if comparison.get("added_rows") != t20["target_rows"] - t4["target_rows"]:
        found.append("comparison added rows are inconsistent")
    if comparison.get("added_missing_carriers") != (
            t20["carrier_missing"] - t4["carrier_missing"]):
        found.append("comparison added missing carriers are inconsistent")
    if comparison.get("added_c2_failing_cells") != (
            t20["c2_failing_cells"] - t4["c2_failing_cells"]):
        found.append("comparison added C2 failures are inconsistent")
    return found


def _fixture_row(a: bool, k: bool) -> dict:
    return {"A": a, "K": k, "carrier_missing": not k,
            "c2_failing_cells": c2_failing_cells(a, k)}


def self_test() -> list[str]:
    found: list[str] = []
    if c2_failing_cells(True, True) != 0:
        found.append("a fully available row is not C2-viable")
    if c2_failing_cells(True, False) != 3:
        found.append("a carrier-missing row does not fail three C2 cells")
    if c2_failing_cells(False, True) != 2:
        found.append("an admission-missing row does not fail two C2 cells")
    if c2_failing_cells(False, False) != 4:
        found.append("a row missing both paths does not fail all four C2 cells")
    return found


def _summary_table(doc: dict) -> list[str]:
    lines = [
        "| Design | Target rows | Carrier-missing | Missing rate | Seeds with a missing row | C2 failing cell-rows | C2 failing rate | Fully C2-viable rows | C2-viable seeds |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for key in (N4, N20):
        t = doc["designs"][key]["totals"]
        lines.append(
            "| **%s** | %d | %d | %.1f%% | %d/6 | %d/%d | %.1f%% | %d | %d/6 |" % (
                key, t["target_rows"], t["carrier_missing"],
                t["carrier_missing_rate"] * 100, t["seeds_with_missing"],
                t["c2_failing_cells"], t["c2_cells_total"],
                t["c2_failing_rate"] * 100, t["fully_c2_viable"],
                t["c2_viable_seeds"],
            )
        )
    return lines


def _per_seed_table(doc: dict, key: str) -> list[str]:
    lines = [
        "| Seed | Targets | Carrier-missing | Missing rate | C2 failing cells | C2 failing rate | Fully C2-viable | Seed C2-viable? |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in doc["designs"][key]["per_seed"]:
        lines.append(
            "| `%d` | %d | %d | %.1f%% | %d/%d | %.1f%% | %d | %s |" % (
                row["seed"], row["target_rows"], row["carrier_missing"],
                row["carrier_missing_rate"] * 100, row["c2_failing_cells"],
                row["c2_cells_total"], row["c2_failing_rate"] * 100,
                row["fully_c2_viable"], "YES" if row["c2_seed_viable"] else "NO",
            )
        )
    return lines


def render(doc: dict) -> str:
    t4 = doc["designs"][N4]["totals"]
    t20 = doc["designs"][N20]["totals"]
    cmp = doc["comparison"]
    lines = [
        "# A1 target viability — N4 vs N20 carrier-missing rows and C2",
        "",
        "**ID:** `%s`" % doc["id"],
        "**Status:** `%s`" % doc["status"],
        "",
        "**This is not an A1 result.** It is a read-only report over the no-arm carrier and baseline-availability artifacts; no cell was run and no target was changed.",
        "",
        "## C2 contract",
        "",
        doc["c2_rule"],
        "",
        "A carrier-missing target loses the three K-requiring cells. If it also lacks admission, it loses all four. Because C2 is all-row and per-seed, one such target makes the seed unable to pass C2.",
        "",
        "## N4 vs N20",
        "",
    ]
    lines += _summary_table(doc)
    lines += [
        "",
        "**N20 does not repair C2.** It adds **%d** target rows, of which **%d** lack a carrier (%.1f%%), retains all **%d** N4 carrier-missing rows, and leaves **%d/6** seeds C2-viable versus **%d/6** at N4. Its C2 failing cell-rows rise from **%d** to **%d** (%.1f%% to %.1f%%)." % (
            cmp["added_rows"], cmp["added_missing_carriers"],
            cmp["added_missing_rate"] * 100,
            cmp["retained_N4_missing_carriers"],
            t20["c2_viable_seeds"], t4["c2_viable_seeds"],
            t4["c2_failing_cells"], t20["c2_failing_cells"],
            t4["c2_failing_rate"] * 100, t20["c2_failing_rate"] * 100,
        ),
        "",
        "## Per-seed rows",
        "",
        "### N4",
        "",
    ]
    lines += _per_seed_table(doc, N4)
    lines += ["", "### N20", ""]
    lines += _per_seed_table(doc, N20)
    lines += [
        "",
        "## What the counts mean",
        "",
        "| Category | N4 | N20 |",
        "| --- | ---: | ---: |",
        "| Target rows | %d | %d |" % (t4["target_rows"], t20["target_rows"]),
        "| Carrier-missing rows | %d | %d |" % (t4["carrier_missing"], t20["carrier_missing"]),
        "| Carrier + admission missing | %d | %d |" % (t4["both_missing"], t20["both_missing"]),
        "| Admission missing, carrier present | %d | %d |" % (t4["A_only_missing"], t20["A_only_missing"]),
        "| Fully C2-viable rows | %d | %d |" % (t4["fully_c2_viable"], t20["fully_c2_viable"]),
        "| C2 failing cell-rows | %d | %d |" % (t4["c2_failing_cells"], t20["c2_failing_cells"]),
        "| C2-viable seeds | %d/6 | %d/6 |" % (t4["c2_viable_seeds"], t20["c2_viable_seeds"]),
        "",
        "The carrier-missing count is not a substitute for the C2 count: a target with a carrier but no admission still fails two C2 cells, and a target missing both fails four.",
        "",
        "## Disposition",
        "",
        doc["disposition"],
        "",
        "**Limits:** C2 treatment effects, C1, C4, C7 and C8 remain unmeasured. The 60-row C1 floor is separately below the observed baseline denominator. This report does not choose a replacement target set and does not freeze, grant or run one.",
        "",
        "**Not evidence:** %s" % doc["not_evidence"],
        "",
        "## Reproduce",
        "",
        "```bash",
        "python -m benchmarks.a1_target_viability --check",
        "python -m benchmarks.a1_target_viability --self-test",
        "```",
        "",
    ]
    return "\n".join(lines).rstrip("\n")


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
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        print("FAIL: %s is missing" % OUT_PATH)
        return 1
    doc = _load(OUT_PATH)
    found = problems(doc)
    if PAGE_PATH.read_text(encoding="utf-8") != render(doc) + "\n":
        found.append("the page is stale")
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("A1 target viability: clean; N4 %d/%d missing, N20 %d/%d missing; "
          "C2-viable seeds N4 %d, N20 %d"
          % (doc["designs"][N4]["totals"]["carrier_missing"],
             doc["designs"][N4]["totals"]["target_rows"],
             doc["designs"][N20]["totals"]["carrier_missing"],
             doc["designs"][N20]["totals"]["target_rows"],
             doc["designs"][N4]["totals"]["c2_viable_seeds"],
             doc["designs"][N20]["totals"]["c2_viable_seeds"]))
    return 0


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
        print("A1 target viability: self-test clean")
        return 0
    if args.write:
        return write()
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
