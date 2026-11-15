"""A1 competence filter — the A&K-available selection rule and what it would change.

Option A of the C2/C8 competence draft was "adopt the filter and re-select", and
that needs a rule plus an answer to a prior question: can a competent block be
built at all? This module states the rule and answers both, for the adopted block:

  * the candidate universe, the 36-cycle boundary, the positive-strength and
    cycle-member eligibility test, the hash order, the row counts and the endpoint
    caps are unchanged;
  * one predicate is added — both baseline paths, A and K, must be present for that
    directed edge in the recorded no-arm availability;
  * there is no fallback. If fewer than n competent rows can be selected, the seed
    forms no target set and the block is VOID rather than filled with
    non-competent rows.

The measurement returned something the draft did not assume. On the four-row
design the filter is easy: a competent set forms on every seed. On the twenty-row
design it is not. A hash-order greedy walk over the competent rows forms a block on
three of six seeds, and on 20740102 **no** twenty-row competent block exists at all
under the endpoint cap — every one of the 888,030 candidate subsets was checked and
none satisfies it. A count comparison ("the pool holds 27-40 competent rows, more
than 20 needed") is therefore not a construction, and this record says so instead
of implying one.

The module runs no engine: the universe, strengths, membership and current
selections are read from committed artifacts, and the availability flags from the
adopted no-arm record. Its central check is that the *unfiltered* pass reproduces
each recorded selection edge for edge — if it does not, the rule has been
mis-implemented and this is not a draft of the published rule.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
AVAILABILITY_PATH = DOCS / "a1_baseline_availability_adopted.json"
N4_PATH = DOCS / "a1_target_selection.json"
N20_PATH = DOCS / "a1_c8_target_selection.json"
OUT_PATH = DOCS / "a1_competence_filter_draft.json"
PAGE_PATH = DOCS / "A1-COMPETENCE-FILTER-DRAFT.md"
ID = "A1-COMPETENCE-FILTER-DRAFT-1"
DATE = "2026-11-15"
KIND = "a1_competence_filter_draft"

BLOCK = 2074
SEEDS = tuple(BLOCK * 10000 + 100 + i for i in range(1, 7))
SALT = "A1-TARGET-1"          # the published order salt; unchanged by this draft
RESTARTS = 4000               # deterministic restarts of the constructive search
ENUMERATION_LIMIT = 1_000_000  # exhaustive feasibility verdict above this is skipped
DESIGNS = {
    "N4": {"n": 4, "limit": 1, "path": N4_PATH,
           "existing_rule": "A1-TARGET-SELECTION-1 (disjoint, four rows per seed)"},
    "N20": {"n": 20, "limit": 3, "path": N20_PATH,
            "existing_rule": "A1-N20-COMPETENT-1 (endpoint degree cap 3)"},
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _order(candidates: list[str], seed: int) -> list[str]:
    return sorted(candidates, key=lambda edge: (
        _hash("%s|%d|%s" % (SALT, seed, edge)), edge))


def _greedy(candidates: list[str], seed: int, n: int, limit: int | None) -> list[str]:
    """The published loop: hash order, endpoint cap, exactly n rows or none."""
    selected: list[str] = []
    degree: dict[str, int] = {}
    for edge in _order(candidates, seed):
        a, b = edge.split(">", 1)
        if limit is not None and (degree.get(a, 0) >= limit or degree.get(b, 0) >= limit):
            continue
        selected.append(edge)
        degree[a] = degree.get(a, 0) + 1
        degree[b] = degree.get(b, 0) + 1
        if len(selected) == n:
            return selected
    return selected


def _walk(order: list[str], n: int, limit: int) -> list[str]:
    selected: list[str] = []
    degree: dict[str, int] = {}
    for edge in order:
        a, b = edge.split(">", 1)
        if degree.get(a, 0) >= limit or degree.get(b, 0) >= limit:
            continue
        selected.append(edge)
        degree[a] = degree.get(a, 0) + 1
        degree[b] = degree.get(b, 0) + 1
        if len(selected) == n:
            break
    return selected


def _construct(pool: list[str], seed: int, n: int, limit: int) -> list[str]:
    """Best block this record can exhibit: hash order first, then restarts.

    Deterministic: the restart generator is seeded by the seed block, so the same
    input always produces the same witness. A witness proves a block exists; the
    absence of one proves nothing, which is why ``_exhaustive`` exists.
    """
    ordered = _order(pool, seed)
    best = _walk(ordered, n, limit)
    if len(best) == n:
        return best
    rng = random.Random(seed)
    for _ in range(RESTARTS):
        shuffled = ordered[:]
        rng.shuffle(shuffled)
        candidate = _walk(shuffled, n, limit)
        if len(candidate) > len(best):
            best = candidate
            if len(best) == n:
                return best
    return best


def _exhaustive(pool: list[str], n: int, limit: int) -> bool | None:
    """Decide feasibility exactly when the enumeration is affordable."""
    total = 1
    for i in range(n):
        total = total * (len(pool) - i) // (i + 1)
    if total > ENUMERATION_LIMIT:
        return None
    for combo in itertools.combinations(pool, n):
        degree: dict[str, int] = {}
        for edge in combo:
            a, b = edge.split(">", 1)
            degree[a] = degree.get(a, 0) + 1
            degree[b] = degree.get(b, 0) + 1
            if degree[a] > limit or degree[b] > limit:
                break
        else:
            return True
    return False


def _design_rows(design: str, availability: dict, universe: dict) -> list[dict]:
    spec = DESIGNS[design]
    selection = _load(spec["path"])
    rows = []
    for seed in SEEDS:
        key = str(seed)
        recorded = (selection.get("per_seed") or {}).get(key) or {}
        # Both designs run over the same 36-cycle candidate universe; the N=20
        # artifact records only its twenty selections, so the universe comes
        # from the four-target artifact that enumerated it in full.
        u = universe[seed]["u"]
        members = universe[seed]["members"]
        eligible = sorted(
            edge for edge in u
            if int((u.get(edge) or {}).get("strength") or 0) > 0
            and members.get(edge) is True)
        flags = availability[seed]
        unrecorded = [edge for edge in eligible if edge not in flags]
        competent = [edge for edge in eligible
                     if edge in flags and flags[edge][0] and flags[edge][1]]
        current = list(recorded.get("selected") or [])
        reproduced = _greedy(eligible, seed, spec["n"], spec["limit"])
        greedy = _greedy(competent, seed, spec["n"], spec["limit"])
        best = _construct(competent, seed, spec["n"], spec["limit"])
        exhaustive = _exhaustive(competent, spec["n"], spec["limit"])
        formed = len(best) == spec["n"]
        if formed:
            verdict = "FORMED — WITNESS RECORDED"
        elif exhaustive is False:
            verdict = "IMPOSSIBLE — EXHAUSTIVE"
        elif exhaustive is True:
            verdict = "FORMED — WITNESS RECORDED"
        else:
            verdict = "UNDECIDED — BEST FOUND ONLY"
        rows.append({
            "seed": seed,
            "eligible": len(eligible),
            "competent_pool": len(competent),
            "eligible_unrecorded": unrecorded,
            "current": current,
            "reproduced": reproduced,
            "reproduces_recorded": reproduced == current,
            "greedy": greedy,
            "greedy_formed": len(greedy) == spec["n"],
            "best_found": best,
            "best_found_rows": len(best),
            "verdict": verdict,
            "exhaustive": exhaustive,
            "kept": [edge for edge in best if edge in current] if formed else [],
            "removed": [edge for edge in current if edge not in best] if formed else [],
            "added": [edge for edge in best if edge not in current] if formed else [],
            "all_competent": all(
                edge in flags and flags[edge][0] and flags[edge][1]
                for edge in best),
        })
    return rows


def build() -> dict:
    availability_doc = _load(AVAILABILITY_PATH)
    availability = {
        int(row["seed"]): {r["edge"]: (bool(r["A"]), bool(r["K"]))
                           for r in row["rows"]}
        for row in availability_doc.get("per_seed") or []
    }
    if set(availability) != set(SEEDS):
        raise ValueError("availability is not on the adopted block")

    universe_doc = _load(N4_PATH)
    universe = {}
    for seed in SEEDS:
        row = (universe_doc.get("per_seed") or {}).get(str(seed)) or {}
        if not row.get("u") or not row.get("cycle_member"):
            raise ValueError("the candidate universe is not recorded for %d" % seed)
        universe[seed] = {"u": row["u"], "members": row["cycle_member"]}

    designs = {}
    for design, spec in DESIGNS.items():
        rows = _design_rows(design, availability, universe)
        if not all(row["reproduces_recorded"] for row in rows):
            raise ValueError(
                "%s: the unfiltered pass does not reproduce the recorded "
                "selection, so this draft is not the published rule" % design)
        if not all(row["all_competent"] for row in rows):
            raise ValueError("%s: a selected row is not competent" % design)
        designs[design] = {
            "n_per_seed": spec["n"],
            "endpoint_limit": spec["limit"],
            "existing_rule": spec["existing_rule"],
            "rows": rows,
            "kept": sum(len(row["kept"]) for row in rows),
            "removed": sum(len(row["removed"]) for row in rows),
            "added": sum(len(row["added"]) for row in rows),
            "rows_requested": spec["n"] * len(rows),
            "seeds_formed": sum(1 for row in rows
                                if row["verdict"].startswith("FORMED")),
            "seeds_greedy_formed": sum(1 for row in rows if row["greedy_formed"]),
            "seeds_impossible": sum(1 for row in rows
                                    if row["verdict"].startswith("IMPOSSIBLE")),
            "seeds_undecided": sum(1 for row in rows
                                   if row["verdict"].startswith("UNDECIDED")),
            "seeds": len(rows),
            "changed_seeds": sum(1 for row in rows
                                 if row["best_found"] and row["best_found"] != row["current"]),
        }

    n4, n20 = designs["N4"], designs["N20"]
    impossible = [row["seed"] for row in n20["rows"]
                  if row["verdict"].startswith("IMPOSSIBLE")]
    return {
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": (
            "DRAFT — RULE STATED, CHANGE MEASURED, AND THE N=20 FILTER DOES NOT "
            "FORM ON EVERY SEED; NOT APPLIED, NOT FROZEN, NO GRANT, NO RUN"),
        "block": BLOCK,
        "seed_block": list(SEEDS),
        "seed_block_note": (
            "the reserved A1-TWO-PATH-1 candidate block; this draft re-selects it "
            "from committed artifacts and spends nothing"),
        "rule": {
            "name": "A1-COMPETENCE-FILTER-1",
            "one_line": (
                "Restrict each published selection's eligible set to the rows whose "
                "baseline A and K paths are both present, and leave everything else "
                "in the rule alone."),
            "steps": [
                "Rebuild the candidate universe exactly as the published rule does: "
                "the first 36 acquisition cycles, one orientation per unordered pair.",
                "Apply the published eligibility test: positive cycle-36 U strength "
                "and cycle membership.",
                "Add one predicate: both baseline paths, A and K, must be true for "
                "that directed edge in the recorded no-arm availability.",
                "Order the remaining edges by ascending sha256('A1-TARGET-1|seed|a>b') "
                "— the published salt, unchanged — and walk that order, skipping an "
                "edge whose endpoint already holds its cap, until n rows are taken.",
                "For this draft the walk is repeated under deterministic shuffles to "
                "exhibit the best block that exists at all; the published order is "
                "reported beside it, because the two differ.",
                "Stop at n = 4 (endpoint cap 1) or n = 20 (endpoint cap 3). One "
                "orientation per pair; no edge repeated.",
                "If fewer than n edges are accepted, the seed forms no target set and "
                "the block is VOID. No non-competent row is ever added as a fallback.",
            ],
            "unchanged_by_this_draft": [
                "the candidate universe and the 36-cycle boundary",
                "the strength and cycle-member eligibility test",
                "the hash order and its salt",
                "the row counts (4 and 20) and the endpoint caps",
                "every threshold: no gate, floor or criterion moves",
            ],
            "changed_by_this_draft": [
                "which rows are eligible: A-and-K-available only",
                "therefore which rows are selected, on every seed",
                "and, in consequence, the population the C8 result would speak about",
            ],
        },
        "designs": designs,
        "estimand": {
            "before": (
                "The effect on the n selected rows of each seed, where selection is a "
                "hash over a universe screened only for strength and cycle membership."),
            "after": (
                "The effect on the n selected rows of each seed, where selection is a "
                "hash over that same universe screened additionally for baseline A "
                "and K availability — the rows on which a C2 cell set and an A-K- "
                "double block can be observed at all."),
            "what_moves": [
                "The population narrows: rows that cannot carry both paths leave the "
                "target set, so the measurement no longer averages over rows whose "
                "outcome is mechanically unavailable.",
                "Rates can rise by construction. A competent-only block removes rows "
                "that could not have produced the outcome, which is a denominator "
                "change, not evidence of a treatment effect.",
                "External validity narrows with it: a C8 result would speak about "
                "A-and-K-available edges on this universe, not about selected edges "
                "in general.",
                "Eligibility is measured before any arm is applied, so the filter is "
                "pre-treatment — which is what makes it admissible as a selection "
                "rule rather than a post-hoc exclusion.",
            ],
            "what_does_not_move": [
                "C1's denominator: it counts observed paired-control rows over the "
                "whole cell stream, so changing which rows are targets changes no "
                "count. C1 remains unscored.",
                "C4's exposure: the non-target set is the cell stream minus N, which "
                "is set by N and not by which edges are target rows. Filtering buys "
                "no relief from the 108 non-target rows per seed.",
                "Nothing about C2's treatment gate: a no-arm filter cannot show that "
                "an absent path stays absent under treatment.",
            ],
        },
        "consequences": {
            "N4": (
                "%d of %d rows are kept and %d replaced across the block; a competent "
                "four-row set forms on %d of %d seeds."
                % (n4["kept"], n4["rows_requested"], n4["removed"],
                   n4["seeds_formed"], n4["seeds"])),
            "N20": (
                "a competent twenty-row block forms on only %d of %d seeds; the "
                "published hash-order walk forms %d of %d. %d seed(s) are proven "
                "impossible by exhaustive enumeration — every candidate subset was "
                "checked and none satisfies the endpoint cap — and %d are undecided "
                "with a best block of fewer than twenty rows. The count comparison "
                "(27-40 competent rows against 20 needed) was therefore not a "
                "construction: under the cap, competence is short at the block level."
                % (n20["seeds_formed"], n20["seeds"], n20["seeds_greedy_formed"],
                   n20["seeds"], n20["seeds_impossible"], n20["seeds_undecided"])),
            "acts_and_records": (
                "Adopting this rule re-issues both target tables and therefore both "
                "freeze acts' recorded target sets, the C5 carrier-cycle record (its "
                "N=20 rows would be re-selected) and every artifact that quotes the "
                "current selections. It cannot be adopted for C8 as it stands: the "
                "filter leaves at least one seed without a block."),
        },
        "finding": {
            "what_this_means_for_option_a": (
                "The filter is necessary and, on its own, not sufficient. It fixes the "
                "rows a C8 result would speak about, but it cannot produce a twenty-row "
                "block on every seed under the endpoint cap the rule already carries. "
                "The remaining levers are a different cap, a wider universe (option C) "
                "or declining to adjudicate C8 on this block (option B). None of them "
                "is a no-op, and none is chosen here."),
            "impossible_seeds": impossible,
            "what_this_does_not_establish": (
                "that a competent block exists on the undecided seeds, or that no "
                "block exists there under a different cap. A witness proves a block "
                "exists; the absence of one proves nothing, which is why the "
                "exhaustive verdict is reported separately from the search."),
        },
        "integrity": {
            "unfiltered_reproduces_recorded": all(
                row["reproduces_recorded"] for design in designs.values()
                for row in design["rows"]),
            "eligible_rows_without_availability": sum(
                len(row["eligible_unrecorded"]) for design in designs.values()
                for row in design["rows"]),
            "selected_rows_not_competent": sum(
                0 if row["all_competent"] else 1
                for design in designs.values() for row in design["rows"]),
            "note": (
                "The unfiltered pass reproduces every recorded selection edge for "
                "edge on all six seeds for both designs; that is what licenses "
                "calling the filtered pass a restriction of the published rule "
                "rather than a new one."),
        },
        "not_evidence": (
            "A draft selection rule and the change it would make. It applies "
            "nothing, freezes nothing, runs no cell, changes no threshold and makes "
            "no claim that C8 or C2 would pass under it. It does not select, reserve "
            "or spend a seed block."),
    }


def problems(doc: dict) -> list[str]:
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("kind")
    if doc.get("id") != ID:
        found.append("id")
    if doc.get("block") != BLOCK:
        found.append("block")
    designs = doc.get("designs") or {}
    if set(designs) != set(DESIGNS):
        return found + ["designs"]
    for design, block in designs.items():
        n = DESIGNS[design]["n"]
        limit = DESIGNS[design]["limit"]
        rows = block.get("rows") or []
        if [row.get("seed") for row in rows] != list(SEEDS):
            found.append("%s seed block" % design)
            continue
        for row in rows:
            if not row.get("reproduces_recorded"):
                found.append("%s seed %s does not reproduce the recorded selection"
                             % (design, row.get("seed")))
            if not row.get("all_competent"):
                found.append("%s seed %s has a non-competent selected row"
                             % (design, row.get("seed")))
            if row.get("eligible_unrecorded"):
                found.append("%s seed %s has eligible rows without availability"
                             % (design, row.get("seed")))
            best = row.get("best_found") or []
            if row.get("best_found_rows") != len(best):
                found.append("%s seed %s best-found count" % (design, row.get("seed")))
            if len(best) > n:
                found.append("%s seed %s best-found exceeds n"
                             % (design, row.get("seed")))
            if len(best) > row.get("competent_pool", 0):
                found.append("%s seed %s best-found exceeds the pool"
                             % (design, row.get("seed")))
            degree: dict[str, int] = {}
            for edge in best:
                a, b = edge.split(">", 1)
                degree[a] = degree.get(a, 0) + 1
                degree[b] = degree.get(b, 0) + 1
            if any(value > limit for value in degree.values()):
                found.append("%s seed %s witness breaks the endpoint cap"
                             % (design, row.get("seed")))
            formed = len(best) == n
            verdict = row.get("verdict") or ""
            if formed and not verdict.startswith("FORMED"):
                found.append("%s seed %s verdict contradicts the witness"
                             % (design, row.get("seed")))
            if not formed and verdict.startswith("FORMED"):
                found.append("%s seed %s claims a block it does not have"
                             % (design, row.get("seed")))
            if verdict.startswith("IMPOSSIBLE") and row.get("exhaustive") is not False:
                found.append("%s seed %s impossibility is not exhaustive"
                             % (design, row.get("seed")))
            if verdict.startswith("UNDECIDED") and row.get("exhaustive") is not None:
                found.append("%s seed %s undecided despite an exact verdict"
                             % (design, row.get("seed")))
            current = row.get("current") or []
            if len(current) != n:
                found.append("%s seed %s current set is not %d rows"
                             % (design, row.get("seed"), n))
            if formed:
                if row.get("kept") != [e for e in best if e in current]:
                    found.append("%s seed %s kept set" % (design, row.get("seed")))
                if row.get("removed") != [e for e in current if e not in best]:
                    found.append("%s seed %s removed set" % (design, row.get("seed")))
                if row.get("added") != [e for e in best if e not in current]:
                    found.append("%s seed %s added set" % (design, row.get("seed")))
            elif row.get("kept") or row.get("removed") or row.get("added"):
                found.append("%s seed %s reports a diff without a block"
                             % (design, row.get("seed")))
        for field in ("kept", "removed", "added"):
            expected = sum(len(row[field]) for row in rows)
            if block.get(field) != expected:
                found.append("%s %s total" % (design, field))
        if block.get("rows_requested") != n * len(rows):
            found.append("%s rows_requested" % design)
        if block.get("seeds_formed") != sum(
                1 for row in rows if (row.get("verdict") or "").startswith("FORMED")):
            found.append("%s seeds_formed" % design)
        if block.get("seeds_greedy_formed") != sum(
                1 for row in rows if row.get("greedy_formed")):
            found.append("%s seeds_greedy_formed" % design)
        if block.get("seeds_impossible") != sum(
                1 for row in rows if (row.get("verdict") or "").startswith("IMPOSSIBLE")):
            found.append("%s seeds_impossible" % design)
        if block.get("seeds_undecided") != sum(
                1 for row in rows if (row.get("verdict") or "").startswith("UNDECIDED")):
            found.append("%s seeds_undecided" % design)
    integrity = doc.get("integrity") or {}
    if integrity.get("unfiltered_reproduces_recorded") is not True:
        found.append("the unfiltered pass does not reproduce the record")
    return found


def _row_table(design: str, block: dict) -> list[str]:
    lines = [
        "| Seed | Competent pool | Published walk | Best found | Kept | Replaced | Added | Verdict |",
        "| ---: | ---: | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in block["rows"]:
        formed = len(row["best_found"]) == DESIGN_ROWS[design]
        lines.append("| %d | %d | %d rows | **%d rows** | %d | %d | %d | %s |" % (
            row["seed"], row["competent_pool"], len(row["greedy"]),
            row["best_found_rows"], len(row["kept"]), len(row["removed"]),
            len(row["added"]), row["verdict"]))
    return lines


DESIGN_ROWS = {key: spec["n"] for key, spec in DESIGNS.items()}


def render(doc: dict) -> str:
    n4, n20 = doc["designs"]["N4"], doc["designs"]["N20"]
    rule = doc["rule"]
    estimand = doc["estimand"]
    lines = [
        "# A1 competence filter — the rule, and what it would change",
        "",
        "**ID:** `%s`" % doc["id"],
        "",
        "**Date:** %s" % doc["date"],
        "",
        "**Status:** `%s`" % doc["status"],
        "",
        "**Block:** `%d` — %s" % (doc["block"], doc["seed_block_note"]),
        "",
        "## The rule",
        "",
        "**%s.** %s" % (rule["name"], rule["one_line"]),
        "",
    ]
    for index, step in enumerate(rule["steps"], start=1):
        lines.append("%d. %s" % (index, step))
    lines += ["", "**Unchanged:** " + "; ".join(rule["unchanged_by_this_draft"]) + "."]
    lines += ["", "**Changed:** " + "; ".join(rule["changed_by_this_draft"]) + "."]
    lines += [
        "",
        "## What it would change — N=4",
        "",
        "| Design | Rows | Kept | Replaced | Added | Seeds with a block | Seeds changed |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        "| **N=4** | %d | %d | %d | %d | **%d of %d** | %d of %d |" % (
            n4["rows_requested"], n4["kept"], n4["removed"], n4["added"],
            n4["seeds_formed"], n4["seeds"], n4["changed_seeds"], n4["seeds"]),
        "",
    ]
    lines += _row_table("N4", n4)
    lines += [
        "",
        "## What it would change — N=20",
        "",
        "| Design | Rows | Kept | Replaced | Added | Seeds with a block | Seeds changed |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        "| **N=20** | %d | %d | %d | %d | **%d of %d** | %d of %d |" % (
            n20["rows_requested"], n20["kept"], n20["removed"], n20["added"],
            n20["seeds_formed"], n20["seeds"], n20["changed_seeds"], n20["seeds"]),
        "",
    ]
    lines += _row_table("N20", n20)
    lines += [
        "",
        "**The N=20 result is the one that matters for the decision.** "
        + doc["consequences"]["N20"],
        "",
        doc["finding"]["what_this_means_for_option_a"],
        "",
        "**Impossible by exhaustion:** %s. **Does not establish:** %s" % (
            ", ".join(str(seed) for seed in doc["finding"]["impossible_seeds"]) or "none",
            doc["finding"]["what_this_does_not_establish"]),
        "",
        "## What it does to the estimand",
        "",
        "**Before.** %s" % estimand["before"],
        "",
        "**After.** %s" % estimand["after"],
        "",
    ]
    for item in estimand["what_moves"]:
        lines.append("- %s" % item)
    lines += ["", "**What does not move:**"]
    for item in estimand["what_does_not_move"]:
        lines.append("- %s" % item)
    lines += [
        "",
        "## Consequences of adopting it",
        "",
        "- **N=4:** %s" % doc["consequences"]["N4"],
        "- **N=20:** %s" % doc["consequences"]["N20"],
        "- **Records:** %s" % doc["consequences"]["acts_and_records"],
        "",
        "## Integrity",
        "",
        doc["integrity"]["note"],
        "",
        "Eligible rows without an availability record: **%d**. Selected rows that "
        "are not competent: **%d**." % (
            doc["integrity"]["eligible_rows_without_availability"],
            doc["integrity"]["selected_rows_not_competent"]),
        "",
        "**Not evidence:** %s" % doc["not_evidence"],
        "",
        "Reproduce with `python -m benchmarks.a1_competence_filter_draft --write`; "
        "`--check` re-derives the whole draft from the source artifacts.",
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
    for design, block in doc["designs"].items():
        print("  %s: blocks %d/%d (published walk %d/%d), impossible %d, "
              "undecided %d, replaced %d" % (
                  design, block["seeds_formed"], block["seeds"],
                  block["seeds_greedy_formed"], block["seeds"],
                  block["seeds_impossible"], block["seeds_undecided"],
                  block["removed"]))
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        print("FAIL: %s is missing" % OUT_PATH)
        return 1
    doc = json.loads(OUT_PATH.read_text(encoding="utf-8"))
    found = problems(doc)
    if doc != build():
        found.append("the draft is stale against its source artifacts")
    if PAGE_PATH.read_text(encoding="utf-8") != render(doc) + "\n":
        found.append("the page is stale")
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("A1 competence filter draft: clean; N=4 blocks %d/6, N=20 blocks %d/6, "
          "N=20 impossible %d" % (
              doc["designs"]["N4"]["seeds_formed"],
              doc["designs"]["N20"]["seeds_formed"],
              doc["designs"]["N20"]["seeds_impossible"]))
    return 0


def _fixture_design(n: int, limit: int, rows_requested: int,
                    verdict: str, exhaustive) -> dict:
    rows = []
    for index, seed in enumerate(SEEDS):
        base = index * 100
        current = ["a%d>b%d" % (base + i, base + i) for i in range(n)]
        formed = verdict.startswith("FORMED")
        best = (current[: n - 2]
                + ["a%d>b%d" % (base + 500 + i, base + 500 + i) for i in range(2)]
                if formed else current[: n - 1])
        rows.append({
            "seed": seed, "eligible": 64, "competent_pool": 30,
            "eligible_unrecorded": [], "current": current, "reproduced": current,
            "reproduces_recorded": True, "greedy": current,
            "greedy_formed": True, "best_found": best,
            "best_found_rows": len(best), "verdict": verdict,
            "exhaustive": exhaustive,
            "kept": [e for e in best if e in current] if formed else [],
            "removed": [e for e in current if e not in best] if formed else [],
            "added": [e for e in best if e not in current] if formed else [],
            "all_competent": True,
        })
    return {"n_per_seed": n, "endpoint_limit": limit, "existing_rule": "x",
            "rows": rows,
            "kept": sum(len(r["kept"]) for r in rows),
            "removed": sum(len(r["removed"]) for r in rows),
            "added": sum(len(r["added"]) for r in rows),
            "rows_requested": rows_requested,
            "seeds_formed": sum(1 for r in rows if r["verdict"].startswith("FORMED")),
            "seeds_greedy_formed": 6,
            "seeds_impossible": sum(1 for r in rows
                                    if r["verdict"].startswith("IMPOSSIBLE")),
            "seeds_undecided": sum(1 for r in rows
                                   if r["verdict"].startswith("UNDECIDED")),
            "seeds": 6, "changed_seeds": 6}


def self_test() -> list[str]:
    found: list[str] = []
    doc = {
        "kind": KIND, "id": ID, "block": BLOCK,
        "designs": {"N4": _fixture_design(4, 1, 24, "FORMED — WITNESS RECORDED", True),
                    "N20": _fixture_design(20, 3, 120, "IMPOSSIBLE — EXHAUSTIVE", False)},
        "integrity": {"unfiltered_reproduces_recorded": True,
                      "eligible_rows_without_availability": 0,
                      "selected_rows_not_competent": 0},
    }
    if problems(doc):
        found.append("a consistent fixture was rejected: %s" % problems(doc))
    broken = json.loads(json.dumps(doc))
    broken["integrity"]["unfiltered_reproduces_recorded"] = False
    if not problems(broken):
        found.append("a draft that does not reproduce the record was accepted")
    broken = json.loads(json.dumps(doc))
    broken["designs"]["N4"]["rows"][0]["all_competent"] = False
    if not problems(broken):
        found.append("a non-competent selected row was accepted")
    broken = json.loads(json.dumps(doc))
    broken["designs"]["N4"]["rows"][0]["kept"] = ["x>y"]
    if not problems(broken):
        found.append("a kept set that is not the intersection was accepted")
    broken = json.loads(json.dumps(doc))
    broken["designs"]["N20"]["rows"][0]["verdict"] = "FORMED — WITNESS RECORDED"
    if not problems(broken):
        found.append("a claim of a block without a witness was accepted")
    broken = json.loads(json.dumps(doc))
    broken["designs"]["N20"]["rows"][0]["exhaustive"] = None
    if not problems(broken):
        found.append("an impossibility that is not exhaustive was accepted")
    broken = json.loads(json.dumps(doc))
    broken["designs"]["N20"]["rows"][0]["best_found"] = \
        [doc["designs"]["N20"]["rows"][0]["current"][0]] * 20
    if not problems(broken):
        found.append("a witness that repeats an edge was accepted")
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
        print("A1 competence filter draft: self-test clean")
        return 0
    if args.write:
        return write()
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
