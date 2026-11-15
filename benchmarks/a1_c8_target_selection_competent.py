"""A1 C8 target selection under the competence screen — the artifact the estimand needs.

`a1_c8_target_selection.json` is a *representative* selection: its hash-order walk over the
eligible universe never asks whether the no-arm baseline records both paths for an edge.  The
competence contract in `DECISION-A1-C8-NMIN-1` counts only competent rows, so the selection a
freeze act would freeze has to be drawn from the competent subset.  This module produces it.

The rule is a restriction of the published one and nothing else:

  * the same 36-cycle universe, the same positive-strength and cycle-member eligibility, the
    same `A1-TARGET-1` hash order and the same endpoint cap of three;
  * one predicate added — both baseline paths, A and K, must be present;
  * the block size falls back from 20 to the largest size that exists, never below
    `N_min = 17`, and no non-competent row is ever substituted.

Size is decided by an exact search, not by a heuristic witness.  A feasible size yields a
witness; an infeasible one is proved by exhaustion.  When the node budget runs out the seed is
reported `UNDECIDED`, never `IMPOSSIBLE` — an unfinished search is not a proof.

    python -m benchmarks.a1_c8_target_selection_competent --write
    python -m benchmarks.a1_c8_target_selection_competent --check
    python -m benchmarks.a1_c8_target_selection_competent --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from benchmarks import a1_competence_filter_draft as draft

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT_PATH = DOCS / "a1_c8_target_selection_competent.json"
PAGE_PATH = DOCS / "A1-C8-TARGET-SELECTION-COMPETENT.md"
BASELINE_PATH = DOCS / "a1_baseline_availability_adopted.json"
ID = "A1-C8-EXPANSION-COMPETENT-1"
DATE = "2026-11-15"
KIND = "a1_c8_target_selection_competent"
SEEDS = draft.SEEDS
CAP = 3
PREFERRED = 20
N_MIN = 17
# Large enough to exhaust every infeasible size on the adopted block: the heaviest is
# 20740105 at 19 rows, proved at 26,087,624 nodes.  A smaller budget left 19 and 20
# undecided there, which is a weaker statement than the one that is now available.
NODE_BUDGET = 40_000_000


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _availability() -> dict[int, dict[str, tuple[bool, bool]]]:
    doc = draft._load(BASELINE_PATH)
    return {int(row["seed"]): {record["edge"]: (bool(record["A"]), bool(record["K"]))
                               for record in row["rows"]}
            for row in doc["per_seed"]}


def _universe(seed: int) -> tuple[dict, dict]:
    doc = draft._load(draft.N4_PATH)
    block = (doc.get("per_seed") or {})[str(seed)]
    return block["u"], block["cycle_member"]


def _eligible(u: dict, members: dict) -> list[str]:
    return sorted(edge for edge in u
                  if int((u.get(edge) or {}).get("strength") or 0) > 0
                  and members.get(edge) is True)


def _competent(eligible: list[str], flags: dict) -> list[str]:
    return [edge for edge in eligible
            if flags.get(edge, (False, False))[0] and flags.get(edge, (False, False))[1]]


def _witness(pool: list[str], need: int, cap: int = CAP,
             budget: int = NODE_BUDGET) -> dict:
    """Exact: the first ``need``-subset with every tag's degree at most ``cap``.

    Returns a witness when one exists, a proved exhaustion when the whole search finished
    without one, and ``exhausted=False`` when the node budget ran out first.
    """
    nodes = 0
    chosen: list[str] = []
    tags = {edge.split(">", 1)[0] for edge in pool} | {edge.split(">", 1)[1] for edge in pool}
    capacity = len(tags) * cap

    def choose(start: int, degree: dict[str, int]) -> bool:
        nonlocal nodes
        nodes += 1
        if nodes > budget:
            raise TimeoutError(
                "the search exceeded %d nodes; feasibility is undecided" % budget)
        if len(chosen) == need:
            return True
        if len(pool) - start < need - len(chosen):
            return False
        # Every further edge spends two endpoint slots, so the slots still free bound how
        # many more can be taken.  Without this the exhaustive proof at 20 rows runs for
        # millions of nodes on the seeds where the cap leaves almost no room.
        free_slots = capacity - 2 * len(chosen)
        if len(chosen) + min(free_slots // 2, len(pool) - start) < need:
            return False
        for index in range(start, len(pool)):
            left, right = pool[index].split(">", 1)
            if degree.get(left, 0) >= cap or degree.get(right, 0) >= cap:
                continue
            degree[left] = degree.get(left, 0) + 1
            degree[right] = degree.get(right, 0) + 1
            chosen.append(pool[index])
            if choose(index + 1, degree):
                return True
            chosen.pop()
            degree[left] -= 1
            degree[right] -= 1
            if not degree[left]:
                del degree[left]
            if not degree[right]:
                del degree[right]
        return False

    try:
        found = choose(0, {})
    except TimeoutError:
        return {"n": need, "feasible": None, "exhausted": False,
                "rows": [], "nodes": nodes}
    return {"n": need, "feasible": found, "exhausted": not found,
            "rows": list(chosen) if found else [], "nodes": nodes}


def _endpoint_degrees(selected: list[str]) -> dict[str, int]:
    degree: dict[str, int] = {}
    for value in selected:
        a, b = value.split(">", 1)
        degree[a] = degree.get(a, 0) + 1
        degree[b] = degree.get(b, 0) + 1
    return dict(sorted(degree.items()))


def _c1_counts(flags: dict) -> dict:
    """C1's denominator over the whole recorded stream.

    It counts every recorded row, targets included, so it is a property of the universe and
    not of the target set: the same three numbers come out of the representative artifact.
    """
    a_minus = sum(1 for edge, (_, k) in flags.items() if k)
    k_minus = sum(1 for edge, (a, _) in flags.items() if a)
    return {"rows": len(flags), "c1_a_minus_denominator": a_minus,
            "c1_k_minus_denominator": k_minus,
            "c1_min_denominator": min(a_minus, k_minus)}


def _seed_row(seed: int, flags: dict) -> dict:
    u, members = _universe(seed)
    eligible = _eligible(u, members)
    pool = _competent(eligible, flags)
    searches = []
    block: list[str] = []
    undecided: list[int] = []
    for need in range(PREFERRED, N_MIN - 1, -1):
        result = _witness(pool, need)
        searches.append({k: result[k] for k in ("n", "feasible", "exhausted", "nodes")})
        if result["feasible"]:
            block = result["rows"]
            break
        if not result["exhausted"]:
            # A budget stop is not a ceiling: keep looking below it, and record that the
            # larger size remains undecided rather than claimed impossible.
            undecided.append(need)
    if block:
        verdict = "FORMED — EXACT WITNESS"
        if undecided:
            verdict += "; LARGER SIZES UNDECIDED"
    elif undecided:
        verdict = "UNDECIDED — NODE BUDGET EXHAUSTED"
    else:
        verdict = "NO BLOCK — BELOW N_MIN BY EXHAUSTION"
    return {
        "seed": seed,
        "eligible": len(eligible),
        "competent_pool": len(pool),
        "n_requested": PREFERRED,
        "n_selected": len(block),
        "verdict": verdict,
        "undecided_sizes": undecided,
        "searches": searches,
        "selected": block,
        "endpoint_degree": _endpoint_degrees(block),
        "competent": {edge: True for edge in block},
        "c1": _c1_counts(flags),
        "selection_digest": _hash(json.dumps({"seed": seed, "selected": block,
                                              "cap": CAP}, sort_keys=True))[:16],
    }


def build() -> dict:
    availability = _availability()
    if set(availability) != set(SEEDS):
        raise ValueError("availability is not on the adopted block")
    per_seed = {str(seed): _seed_row(seed, availability[seed]) for seed in SEEDS}
    return {
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": ("TARGET SETS FORMED UNDER THE COMPETENCE SCREEN — NOT FROZEN, "
                   "NOT A RESULT, NO GRANT, NO RUN"),
        "parent_artifact": "docs/a1_c8_target_selection.json",
        "baseline_artifact": "docs/a1_baseline_availability_adopted.json",
        "design_record": "docs/DECISION-A1-COMPETENT-ESTIMAND.md",
        "competence_rule": "docs/DECISION-A1-C8-NMIN.md",
        "block": draft.BLOCK,
        "seed_block": list(SEEDS),
        "cap": CAP,
        "n_preferred": PREFERRED,
        "n_min": N_MIN,
        "threshold": 0.05,
        "threshold_changed": False,
        "selection_rule": (
            "The published 20-row rule with one predicate added: an edge is eligible only "
            "when the no-arm A+K+ replay records both an A carrier and a K path for it. "
            "Universe, strength and cycle-member test, A1-TARGET-1 hash order and the "
            "endpoint cap of three are unchanged. The block size is the largest the "
            "competent pool admits at that cap, searched from 20 down and never below 17; "
            "no non-competent row is substituted and no cap is raised."),
        "per_seed": per_seed,
        "sizes": [per_seed[str(seed)]["n_selected"] for seed in SEEDS],
        "totals": {"rows": sum(per_seed[str(seed)]["n_selected"] for seed in SEEDS)},
        "not_evidence": (
            "A no-arm target selection for a registered design. It freezes no manifest, "
            "reserves no seed, authorises no cell and records no C8 measurement."),
    }


def problems(doc: dict) -> list[str]:
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("kind")
    if doc.get("id") != ID:
        found.append("id")
    if doc.get("cap") != CAP or doc.get("n_min") != N_MIN:
        found.append("cap or N_min")
    if doc.get("threshold") != 0.05 or doc.get("threshold_changed") is not False:
        found.append("the 0.05 ceiling moved")
    per_seed = doc.get("per_seed") or {}
    if set(per_seed) != {str(seed) for seed in SEEDS}:
        return found + ["seed block"]
    availability = _availability()
    sizes = []
    for seed in SEEDS:
        row = per_seed[str(seed)]
        selected = row.get("selected") or []
        sizes.append(len(selected))
        flags = availability[seed]
        if not (row.get("verdict") or "").startswith("FORMED"):
            found.append("seed %d formed no block: %s" % (seed, row.get("verdict")))
        if len(selected) < N_MIN:
            found.append("seed %d has %d rows, below N_min" % (seed, len(selected)))
        if len(set(selected)) != len(selected):
            found.append("seed %d repeats an edge" % seed)
        for edge in selected:
            if edge.count(">") != 1:
                found.append("seed %d has an invalid edge %r" % (seed, edge))
                continue
            if not (flags.get(edge, (False, False))[0] and flags.get(edge, (False, False))[1]):
                found.append("seed %d edge %s is not baseline-competent" % (seed, edge))
            u, members = _universe(seed)
            if not members.get(edge):
                found.append("seed %d edge %s is not cycle-member" % (seed, edge))
            if int((u.get(edge) or {}).get("strength") or 0) <= 0:
                found.append("seed %d edge %s has no positive strength" % (seed, edge))
        degree = _endpoint_degrees(selected)
        if any(value > CAP for value in degree.values()):
            found.append("seed %d exceeds the endpoint cap" % seed)
        if row.get("endpoint_degree") != degree:
            found.append("seed %d endpoint degrees are stale" % seed)
        if row.get("c1") != _c1_counts(flags):
            found.append("seed %d C1 counts do not match the artifacts" % seed)
        digest = _hash(json.dumps({"seed": seed, "selected": selected, "cap": CAP},
                                  sort_keys=True))[:16]
        if row.get("selection_digest") != digest:
            found.append("seed %d selection digest is stale" % seed)
    if doc.get("sizes") != sizes:
        found.append("the recorded size list does not match the blocks")
    if doc.get("totals", {}).get("rows") != sum(sizes):
        found.append("the row total does not match the blocks")
    # A short block must be short for a reason: every larger size is proved infeasible, or
    # the record names it as undecided.  An unsearched size is a gap, not a ceiling.
    for seed in SEEDS:
        row = per_seed[str(seed)]
        size = len(row.get("selected") or [])
        searches = {item["n"]: item for item in row.get("searches") or []}
        undecided = set(row.get("undecided_sizes") or [])
        for need in range(size + 1, PREFERRED + 1):
            item = searches.get(need)
            if item is None:
                found.append("seed %d never searched %d rows" % (seed, need))
            elif item.get("feasible"):
                found.append("seed %d admits %d rows but recorded %d"
                             % (seed, need, size))
            elif item.get("exhausted") and need in undecided:
                found.append("seed %d calls %d both exhausted and undecided" % (seed, need))
        for need in undecided:
            if (searches.get(need) or {}).get("exhausted"):
                found.append("seed %d hides an exhaustion as undecided" % seed)
            if need <= size:
                found.append("seed %d marks %d undecided below its block" % (seed, need))
    return found


def render(doc: dict) -> str:
    lines = [
        "# A1 C8 target selection under the competence screen",
        "",
        "**ID:** `%s`  " % doc["id"],
        "**Date:** %s  " % doc["date"],
        "**Status:** `%s`" % doc["status"],
        "",
        "**This is not an experimental result.** No arm cell ran; no manifest was frozen.",
        "",
        "The published 20-row rule, with one predicate added: the no-arm A+K+ replay must record "
        "**both** an A carrier and a K path. Universe, strength test, hash order, salt and the "
        "endpoint cap of **%d** are unchanged. The block falls back from 20 to the largest size "
        "that exists, never below **%d**, and never to a non-competent row." % (doc["cap"], doc["n_min"]),
        "",
        "| Seed | Eligible | Competent pool | Rows | Max degree | Largest searched | Verdict |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for seed in SEEDS:
        row = doc["per_seed"][str(seed)]
        undecided = set(row.get("undecided_sizes") or [])
        searched = ", ".join("%d%s" % (item["n"], " (undecided)" if item["n"] in undecided else "")
                              for item in row["searches"])
        lines.append("| %d | %d | %d | **%d** | %d | %s | %s |" % (
            seed, row["eligible"], row["competent_pool"], row["n_selected"],
            max(row["endpoint_degree"].values()), searched, row["verdict"]))
    lines += [
        "",
        "Sizes: **%s** — %d target rows across the block. Sizes are decided by an exact "
        "search: a feasible size yields a witness, an infeasible one is proved by exhaustion, "
        "and a search that runs out of budget is reported `UNDECIDED` rather than as a ceiling."
        % ("/".join(str(size) for size in doc["sizes"]), doc["totals"]["rows"]),
        "",
        "## C1's denominator does not move",
        "",
        "| Seed | A− denominator | K− denominator | Minimum |",
        "| ---: | ---: | ---: | ---: |",
    ]
    for seed in SEEDS:
        c1 = doc["per_seed"][str(seed)]["c1"]
        lines.append("| %d | %d | %d | **%d** |" % (
            seed, c1["c1_a_minus_denominator"], c1["c1_k_minus_denominator"],
            c1["c1_min_denominator"]))
    lines += [
        "",
        "C1 counts every recorded row of the cell stream, targets included, so its denominator "
        "is a property of the universe rather than of the target set — these are the same "
        "numbers the representative selection produces. Changing which edges are targets changes "
        "which rows are *not* targets, and C4's stream, but not this.",
        "",
        "**Not evidence:** %s" % doc["not_evidence"],
        "",
        "Reproduce with `python -m benchmarks.a1_c8_target_selection_competent --write`; "
        "`--check` re-derives every block from the artifacts.",
        "",
    ]
    return "\n".join(lines)


def write() -> int:
    doc = build()
    found = problems(doc)
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    OUT_PATH.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(doc), encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print("  sizes %s" % ("/".join(str(size) for size in doc["sizes"])))
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        print("FAIL: %s is missing" % OUT_PATH)
        return 1
    doc = json.loads(OUT_PATH.read_text(encoding="utf-8"))
    found = problems(doc)
    if doc != build():
        found.append("the selection is stale against its source artifacts")
    if not PAGE_PATH.exists() or PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("the page is stale")
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("A1 competent C8 selection: clean; sizes %s"
          % "/".join(str(size) for size in doc["sizes"]))
    return 0


def self_test() -> list[str]:
    found: list[str] = []
    # Five tags and cap 3 give 15 endpoint slots, so at most seven edges fit and eight cannot.
    tags = [chr(ord("a") + i) for i in range(5)]
    pool = ["%s>%s" % (tags[i], tags[j])
            for i in range(5) for j in range(i + 1, 5)]
    seven = _witness(pool, 7)
    if not seven["feasible"] or len(seven["rows"]) != 7:
        found.append("a feasible seven-row pool produced no witness")
    eight = _witness(pool, 8)
    if eight["feasible"]:
        found.append("eight rows were reported feasible over five tags at cap 3")
    if not eight["exhausted"]:
        found.append("an infeasible search was not reported as exhaustion")
    none = _witness([], 3)
    if none["feasible"] or not none["exhausted"]:
        found.append("an empty pool did not exhaust")
    doc = build()
    if problems(doc):
        found.append("the built selection was rejected: %s" % problems(doc))
    broken = json.loads(json.dumps(doc))
    seed = str(SEEDS[0])
    broken["per_seed"][seed]["selected"] = broken["per_seed"][seed]["selected"][:5]
    broken["per_seed"][seed]["selection_digest"] = "stale"
    if not problems(broken):
        found.append("a truncated block was accepted")
    broken = json.loads(json.dumps(doc))
    broken["per_seed"][seed]["selected"][0] = broken["per_seed"][seed]["selected"][1]
    if not problems(broken):
        found.append("a repeated edge was accepted")
    broken = json.loads(json.dumps(doc))
    broken["sizes"] = [1, 2, 3, 4, 5, 6]
    if not problems(broken):
        found.append("a size list that contradicts the blocks was accepted")
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
        print("A1 competent C8 selection: self-test clean")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
