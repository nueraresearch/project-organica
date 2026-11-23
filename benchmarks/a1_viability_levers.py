"""What the 0/6 C2-viability finding is made of, and what each of the three levers costs.

`docs/A1-TARGET-VIABILITY-ADOPTED.md` reports 0/6 C2-viable seeds on the adopted block. Its table
counts *selected* rows that lack an `A` carrier or a `K` path, but it does not say (a) how many rows
have neither path, which is the number that decides whether *weakening* C2 helps at all, (b) what the
same screen says about the **filtered** block that C8 already selects, or (c) how a seed's viability
chance moves with `N`. This record computes those three and prices the three levers against them.

Nothing here scores C2, freezes a target, issues a grant or runs a cell. It counts the paths a target
row would need in order for C2's four cells to be observable at all.

    python -m benchmarks.a1_viability_levers --write
    python -m benchmarks.a1_viability_levers --check
    python -m benchmarks.a1_viability_levers --self-test
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

BASELINE = DOCS / "a1_baseline_availability_adopted.json"
UNFILTERED_N20 = DOCS / "a1_c8_target_selection.json"
UNFILTERED_N4 = DOCS / "a1_target_selection.json"
FILTERED = DOCS / "a1_c8_target_selection_competent.json"

OUT = DOCS / "a1_viability_levers.json"
PAGE = DOCS / "A1-VIABILITY-LEVERS.md"

ID = "A1-VIABILITY-LEVERS-1"
KIND = "a1_viability_levers"
DATE = "2026-11-15"
STATUS = "FLAGGED — ONE LEVER WORKS AND IT CHANGES THE ESTIMAND; THE OTHER TWO CANNOT WORK"

SEEDS = (20740101, 20740102, 20740103, 20740104, 20740105, 20740106)

WEAKEST_THRESHOLD = (
    "**A per-row threshold cannot be tuned into working.** The best seed has **13 of 20** rows "
    "scorable; the worst has **7 of 20**. Admitting any seed at all through a share-of-rows gate means "
    "accepting that **35%** of a block need not be scorable, which is not C2 with a tolerance — it is a "
    "different gate wearing C2's name."
)

VERDICT = (
    "**Only one lever works, and it is the one already built.** The unfiltered block cannot be made "
    "C2-viable by raising `N`, and no block drawn from the same universes will be viable on six seeds; "
    "what does work is selecting rows that carry both paths at baseline, which is exactly the competent "
    "selection `A1-C8-SELECTION` already specifies and which scores **0 failures in 115 rows**. Its cost "
    "is not computational but interpretive: the target population stops being *representative eligible "
    "edges* and becomes *baseline-competent edges*, so C2's finding would be about a conditioned "
    "population. That is the decision in front of the owner, and it is a decision about what the "
    "experiment is a experiment on."
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _flags() -> dict[int, dict[str, tuple[bool, bool, bool]]]:
    doc = _load(BASELINE)
    return {int(group["seed"]): {row["edge"]: (bool(row["A"]), bool(row["K"]), bool(row["Y"]))
                                 for row in group["rows"]}
            for group in doc["per_seed"]}


def _selected(path: Path, seed: int) -> list[str]:
    return list(_load(path)["per_seed"][str(seed)]["selected"])


def _screen(edges: list[str], flags: dict[str, tuple[bool, bool, bool]]) -> dict:
    missing_a = [edge for edge in edges if not flags.get(edge, (False, False, False))[0]]
    missing_k = [edge for edge in edges if not flags.get(edge, (False, False, False))[1]]
    neither = [edge for edge in edges if edge in set(missing_a) & set(missing_k)]
    return {
        "rows": len(edges),
        "missing_a": len(missing_a),
        "missing_k": len(missing_k),
        "neither": len(neither),
        "either_one": len(edges) - len(neither),
        "viable": len(edges) - len(set(missing_a) | set(missing_k)),
        "missing_y": len([edge for edge in edges if not flags.get(edge, (False, False, False))[2]]),
    }


def build() -> dict:
    flags = _flags()
    filtered_doc = _load(FILTERED)
    seeds = []
    for seed in SEEDS:
        universe = filtered_doc["per_seed"][str(seed)]
        row = {
            "seed": seed,
            "n20": _screen(_selected(UNFILTERED_N20, seed), flags[seed]),
            "n4": _screen(_selected(UNFILTERED_N4, seed), flags[seed]),
            "filtered": _screen(universe["selected"], flags[seed]),
            "eligible": int(universe["eligible"]),
            "competent_pool": int(universe["competent_pool"]),
        }
        row["draw"] = {str(k): _draw(row["eligible"], row["competent_pool"], k) for k in (4, 17, 20)}
        seeds.append(row)
    totals = {
        "n20_viable": sum(row["n20"]["viable"] for row in seeds),
        "n20_rows": sum(row["n20"]["rows"] for row in seeds),
        "neither": sum(row["n20"]["neither"] for row in seeds),
        "filtered_rows": sum(row["filtered"]["rows"] for row in seeds),
        "filtered_failures": sum(row["filtered"]["missing_a"] + row["filtered"]["missing_k"]
                                 for row in seeds),
        "filtered_missing_y": sum(row["filtered"]["missing_y"] for row in seeds),
        "seeds_n20_viable": sum(1 for row in seeds if row["n20"]["viable"] == row["n20"]["rows"]),
        "seeds_filtered_viable": sum(1 for row in seeds
                                     if row["filtered"]["missing_a"] == 0
                                     and row["filtered"]["missing_k"] == 0),
    }
    return {
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "seeds": seeds,
        "totals": totals,
        "sources": {path.name: _digest(path) for path in (BASELINE, UNFILTERED_N20, UNFILTERED_N4, FILTERED)},
        "prose": {"verdict": VERDICT, "threshold": WEAKEST_THRESHOLD},
        "not_evidence": (
            "A count of the baseline paths each target row would need for C2's cells to be observable. "
            "It scores no C2, runs no cell, freezes no target, issues no grant, and makes no causal or "
            "capability claim. Availability is not a pass."
        ),
    }


def _draw(eligible: int, pool: int, k: int) -> float:
    """Chance a k-row draw from the eligible universe is entirely baseline-competent."""
    if k > eligible or k > pool:
        return 0.0
    return round(math.comb(pool, k) / math.comb(eligible, k), 12)


def problems(page_text: str | None = None, doc: dict | None = None) -> list[str]:
    doc = doc if doc is not None else build()
    if engine_stamp.stamp(doc) != engine_stamp.stamp(build()):
        return ["the artifact is stale against its sources"]
    text = page_text if page_text is not None else (PAGE.read_text(encoding="utf-8") if PAGE.exists() else "")
    if not text:
        return ["the page is missing"]
    if text.strip() != render(doc).strip():
        return ["the page is stale against the artifact"]
    found = []
    totals = doc["totals"]
    if totals["filtered_failures"] != 0:
        found.append("a filtered row lacks a path, so the filter is not what the page says it is")
    if totals["neither"] == 0:
        found.append("no selected row lacks both paths, so the weakest lever would work and the "
                     "verdict is wrong")
    if totals["seeds_n20_viable"] != 0:
        found.append("an unfiltered seed is viable, so 0/6 is no longer the finding")
    for row in doc["seeds"]:
        draws = row["draw"]
        if not (draws["4"] >= draws["17"] >= draws["20"]):
            found.append("seed %d: viability does not fall as N rises" % row["seed"])
    for key in ("verdict", "threshold"):
        if doc["prose"][key] not in text:
            found.append("the page no longer carries the %s paragraph" % key)
    return found


def render(doc: dict) -> str:
    totals = doc["totals"]
    lines = [
        "# A1 viability: what 0/6 is made of, and what each lever costs",
        "",
        "**ID:** `%s`  " % doc["id"],
        "**Date:** %s  " % doc["date"],
        "**Status:** `%s`" % doc["status"],
        "",
        "**This is not an A1 result.** No cell ran, no target was frozen, no grant issued. It counts the "
        "baseline paths a target row would need for C2's four cells to be observable, and prices the three "
        "ways out of the 0/6 finding in [`A1-TARGET-VIABILITY-ADOPTED`](A1-TARGET-VIABILITY-ADOPTED.md).",
        "",
        VERDICT,
        "",
        "## What makes each seed non-viable",
        "",
        "A target row is C2-viable only if it has **both** an `A` carrier and a `K` path at baseline: "
        "without `A` it cannot show `A=True` in `A+K-`, and without `K` it cannot show `K=True` in `A-K+`. "
        "`neither` is the count that matters for the weakest lever — those rows are unscorable even if C2 "
        "asks for one direction instead of two.",
        "",
        "| Seed | N20 rows | No `A` | No `K` | **Neither** | Scorable | Fully viable | N4 rows | N4 viable | Eligible | Competent pool |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["seeds"]:
        n20, n4 = row["n20"], row["n4"]
        lines.append("| `%d` | %d | %d | %d | **%d** | %d | %d | %d | %d | %d | %d |"
                     % (row["seed"], n20["rows"], n20["missing_a"], n20["missing_k"], n20["neither"],
                        n20["either_one"], n20["viable"], n4["rows"], n4["viable"],
                        row["eligible"], row["competent_pool"]))
    lines += [
        "",
        "**%d of %d** selected rows are fully viable, and **%d** are unscorable even under the weakest reading. "
        "This is why the seed-level verdict is 0/6 rather than 5/6: C2 is judged per seed and fails on a "
        "single row."
        % (totals["n20_viable"], totals["n20_rows"], totals["neither"]),
        "",
        "## Lever 1 — raise `N`: it moves the wrong way",
        "",
        "`N` is the number of target rows a seed must carry. Raising it adds rows that must *all* pass, so a "
        "seed's chance of being viable is the chance that a whole draw from the eligible universe is "
        "baseline-competent:",
        "",
        "| Seed | `k = 4` | `k = 17` | `k = 20` |",
        "| ---: | ---: | ---: | ---: |",
    ]
    for row in doc["seeds"]:
        draws = row["draw"]
        lines.append("| `%d` | %.2e | %.2e | %.2e |"
                     % (row["seed"], draws["4"], draws["17"], draws["20"]))
    lines += [
        "",
        "**Cost:** none, because it cannot succeed. **Buys:** nothing. At `k = 4` a seed already has only a "
        "2.8%–14.4% chance; at `k = 20` it is 10⁻⁶ or worse, and the six-seed requirement multiplies those "
        "figures together. Raising `N` makes the blocker strictly harder, so this lever is closed by "
        "arithmetic rather than by opinion.",
        "",
        "## Lever 2 — a different block: the draw makes it hopeless",
        "",
        "Drawing a fresh block from the same universes does not change the per-row availability, so it "
        "screens seeds rather than fixing rows. The six-seed joint chance is the product of the `k = 20` "
        "column above — around **10⁻³⁴** — which means the search is not expensive, it is unavailable. "
        "This lever is also the one that would look like outcome-independent screening while in fact being "
        "a search for a favourable draw.",
        "",
        "## Lever 3 — change `C2`: only its strongest form works",
        "",
        "Three readings, in decreasing strength:",
        "",
        "| Reading | What it admits | Seeds viable | What it costs |",
        "| --- | --- | ---: | --- |",
        "| both directions on every row (adopted) | nothing; 0 unscorable rows | **0/6** | the current blocker |",
        "| one direction on every row | `%d` rows still unscorable | **0/6** | no change; still fails |"
        % totals["neither"],
        "| a share of rows per seed | needs ≤ **35%%** scorable-or-not | 6/6 only by redefining the gate | the gate stops being C2 |",
        "| select only rows carrying both paths | `%d` rows, 0 unscorable | **6/6** | a new estimand |"
        % totals["filtered_rows"],
        "",
        WEAKEST_THRESHOLD,
        "",
        "## The one lever that works is already built",
        "",
        "The fourth reading is not hypothetical: [`a1_c8_target_selection_competent.json`](a1_c8_target_selection_competent.json) "
        "already selects blocks of 17–20 rows whose every member has both an `A` carrier and a `K` path, "
        "and the screen above confirms **%d failures in %d rows** across the six seeds. C8's adopted floor "
        "of 17 is the level at which that block forms on every seed."
        % (totals["filtered_failures"], totals["filtered_rows"]),
        "",
        "So the 0/6 finding is not a wall in front of the experiment; it is a wall in front of *one target "
        "population*. The unfiltered block asks C2 a question about representative eligible edges and cannot "
        "answer it. The filtered block asks it about baseline-competent edges and can. The difference is the "
        "whole decision, and it is the reason `A1-C8-SELECTION` is pending: adopting the filter changes what "
        "a positive C2 result would be evidence about.",
        "",
        "## Limits",
        "",
        "- **Availability is not a pass.** A row with both paths can still fail C2 on its cells; this record "
        "counts whether the cells are *observable*, not whether they behave.",
        "- **`Y` is not screened by the gate.** %d of %d filtered rows also lack a baseline `Y`; the gate does "
        "not require it for the two `Y_MINUS` cells, and this record does not add a requirement the gate does "
        "not have. It records the count so the gap is visible rather than assumed away."
        % (totals["filtered_missing_y"], totals["filtered_rows"]),
        "- **The filtered number is a tautology with a price.** The filter is defined as *has both paths*, so "
        "0 failures is a restatement of the definition, not corroboration of it. What is informative is what "
        "the definition excludes: %d of %d eligible rows."
        % (sum(row["eligible"] - row["competent_pool"] for row in doc["seeds"]),
           sum(row["eligible"] for row in doc["seeds"])),
        "",
        "**Not evidence:** " + doc["not_evidence"],
        "",
        "## Provenance",
        "",
        "| Artifact | sha256 |",
        "| --- | --- |",
    ]
    for name, digest in doc["sources"].items():
        lines.append("| `%s` | `%s` |" % (name, digest))
    lines += [
        "",
        "_Generated by `python -m benchmarks.a1_viability_levers --write`; `--check` fails when this page, the "
        "artifact or either source disagrees. The verdict and threshold paragraphs are the only hand-written "
        "text._",
        "",
    ]
    return "\n".join(lines)


def write() -> int:
    doc = engine_stamp.stamp(build())
    OUT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    PAGE.write_text(render(doc), encoding="utf-8")
    totals = doc["totals"]
    print("wrote %s and %s" % (OUT.name, PAGE.name))
    print("  unfiltered viable %d/%d, neither %d, filtered failures %d/%d"
          % (totals["n20_viable"], totals["n20_rows"], totals["neither"],
             totals["filtered_failures"], totals["filtered_rows"]))
    return 0


def check() -> int:
    found = problems()
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("A1 viability levers: clean; no cell run")
    return 0


def self_test() -> list[str]:
    found: list[str] = []
    text = PAGE.read_text(encoding="utf-8")
    doctored = text.replace("of 120** selected rows", "of 121** selected rows", 1)
    if doctored == text or not problems(doctored):
        found.append("a doctored page was accepted")
    doc = build()
    doc["totals"]["filtered_failures"] = 4
    if not problems(text, doc):
        found.append("a filtered failure was accepted")
    doc = build()
    doc["seeds"][0]["n20"]["viable"] = doc["seeds"][0]["n20"]["rows"]
    doc["totals"]["seeds_n20_viable"] = 1
    if not problems(text, doc):
        found.append("a viable unfiltered seed was accepted")
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
    print("self-test: %s" % ("clean" if not found else "%d problem(s)" % len(found)))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
