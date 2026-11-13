"""POST-HOC STORED-FIELD-TIEBREAK-1.

The shipped transition sort ends in a lexical source/target tie-break:

    schema first, target entropy, -probability, -count, source, target

This diagnostic replaces the lexical pair with the stored strength field,
``min(1, ratio)``, so the alternative key is:

    schema first, target entropy, -probability, -count, -strength, source, target

The question is whether a stored field changes the served top-20 set.  The
answer here is no: it changes only the internal order of tie groups.  No engine
cell runs and no fresh seed is spent.

    python -m benchmarks.stored_field_tiebreak --write
    python -m benchmarks.stored_field_tiebreak --check
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks import engine_stamp                                      # noqa: E402

ID = "POST-HOC-STORED-FIELD-TIEBREAK-1"
SEEDS = [20611601, 20611602, 20611603, 20611604, 20611605, 20611606]
CACHE = ROOT / ".scratch" / "rank_sort_probe"
ARTIFACT = ROOT / "docs" / "stored_field_tiebreak.json"
PAGE = ROOT / "docs" / "STORED-FIELD-TIEBREAK.md"
TOP_N = 20


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _feature_path(seed: int) -> Path:
    return CACHE / ("%d_features.json" % seed)


def _load_cycles() -> dict[tuple[int, int], list[dict]]:
    missing = [seed for seed in SEEDS if not _feature_path(seed).exists()]
    if missing:
        raise SystemExit("missing ranking feature caches: %r" % missing)
    cycles = {}
    for seed in SEEDS:
        body = _load(_feature_path(seed))
        if body.get("seed") != seed:
            raise SystemExit("REFUSED: seed mismatch in %s" % _feature_path(seed))
        rows = body.get("cycles") or []
        if len(rows) != 120:
            raise SystemExit("REFUSED: seed %d has %d cycles" % (seed, len(rows)))
        for index, cycle in enumerate(rows):
            cycles[(seed, index)] = cycle
    return cycles


def _primary(row: dict):
    return (
        0 if row["schema"] else 1,
        float(row["entropy"]),
        -float(row["prob"]),
        -int(row["count"]),
    )


def _base_key(row: dict):
    return _primary(row) + (row["edge"][0], row["edge"][1])


def _alt_key(row: dict):
    return _primary(row) + (-float(row["strength"]), row["edge"][0], row["edge"][1])


def _top(rows: list[dict], alternative: bool) -> list[dict]:
    return sorted(rows, key=_alt_key if alternative else _base_key)[:TOP_N]


def _ordered_edges(rows: list[dict]) -> list[tuple[str, str]]:
    return [tuple(row["edge"]) for row in rows]


def _tie_stats(cycles: dict[tuple[int, int], list[dict]]) -> dict:
    cutoff_ties = 0
    cutoff_resolved = 0
    cutoff_saturated = 0
    adjacent_top = 0
    adjacent_top_tied = 0
    adjacent_all = 0
    adjacent_all_tied = 0
    top_rows = 0
    top_rows_tied = 0
    diff_groups = 0
    diff_rows = 0
    diff_top_groups = 0
    diff_top_rows = 0
    for rows in cycles.values():
        ordered = sorted(rows, key=_base_key)
        if len(ordered) >= TOP_N + 1:
            if _primary(ordered[TOP_N - 1]) == _primary(ordered[TOP_N]):
                cutoff_ties += 1
                if (ordered[TOP_N - 1]["strength"]
                        != ordered[TOP_N]["strength"]):
                    cutoff_resolved += 1
                if (ordered[TOP_N - 1]["strength"]
                        == ordered[TOP_N]["strength"] == 1.0):
                    cutoff_saturated += 1
        for i in range(min(TOP_N, len(ordered)) - 1):
            adjacent_top += 1
            if _primary(ordered[i]) == _primary(ordered[i + 1]):
                adjacent_top_tied += 1
        for i in range(len(ordered) - 1):
            adjacent_all += 1
            if _primary(ordered[i]) == _primary(ordered[i + 1]):
                adjacent_all_tied += 1
        for i in range(min(TOP_N, len(ordered))):
            top_rows += 1
            tied = ((i > 0 and _primary(ordered[i]) == _primary(ordered[i - 1]))
                    or (i + 1 < min(TOP_N, len(ordered))
                        and _primary(ordered[i]) == _primary(ordered[i + 1])))
            if tied:
                top_rows_tied += 1
        i = 0
        while i < len(ordered):
            j = i + 1
            while j < len(ordered) and _primary(ordered[j]) == _primary(ordered[i]):
                j += 1
            if j - i > 1:
                values = {round(float(ordered[x]["strength"]), 12)
                          for x in range(i, j)}
                if len(values) > 1:
                    diff_groups += 1
                    diff_rows += j - i
                    if i < TOP_N:
                        diff_top_groups += 1
                        diff_top_rows += min(j, TOP_N) - i
            i = j
    populated = sum(1 for rows in cycles.values() if rows)
    return {
        "cutoff_ties": cutoff_ties,
        "populated_cycles": populated,
        "cutoff_tie_share": cutoff_ties / populated,
        "cutoff_ties_resolved_by_strength": cutoff_resolved,
        "cutoff_ties_saturated_at_one": cutoff_saturated,
        "adjacent_top20_ties": adjacent_top_tied,
        "adjacent_top20_pairs": adjacent_top,
        "adjacent_top20_tie_share": adjacent_top_tied / adjacent_top,
        "adjacent_full_ties": adjacent_all_tied,
        "adjacent_full_pairs": adjacent_all,
        "adjacent_full_tie_share": adjacent_all_tied / adjacent_all,
        "top20_rows_in_tie": top_rows_tied,
        "top20_rows": top_rows,
        "top20_row_tie_share": top_rows_tied / top_rows,
        "different_strength_tie_groups": diff_groups,
        "different_strength_tie_rows": diff_rows,
        "different_strength_top20_groups": diff_top_groups,
        "different_strength_top20_rows": diff_top_rows,
    }


def build() -> dict:
    cycles = _load_cycles()
    rows = [row for cycle in cycles.values() for row in cycle]
    base = {key: _top(cycle, False) for key, cycle in cycles.items()}
    alt = {key: _top(cycle, True) for key, cycle in cycles.items()}
    seats = sum(len(value) for value in base.values())

    changed_cycles = 0
    changed_seats = 0
    order_changed_cycles = 0
    positions_changed = 0
    shifts = []
    entering = []
    leaving = []
    for key in base:
        base_edges = _ordered_edges(base[key])
        alt_edges = _ordered_edges(alt[key])
        base_set = set(base_edges)
        alt_set = set(alt_edges)
        if base_set != alt_set:
            changed_cycles += 1
            changed_seats += len(base_set ^ alt_set)
            entering.extend(alt_set - base_set)
            leaving.extend(base_set - alt_set)
        if base_edges != alt_edges and base_set == alt_set:
            order_changed_cycles += 1
            positions = {edge: i for i, edge in enumerate(base_edges)}
            for position, edge in enumerate(alt_edges):
                if base_edges[position] != edge:
                    positions_changed += 1
                    shifts.append(abs(positions[edge] - position))

    base_pairs = {(key[0], edge) for key, rows_ in base.items()
                  for edge in _ordered_edges(rows_)}
    alt_pairs = {(key[0], edge) for key, rows_ in alt.items()
                 for edge in _ordered_edges(rows_)}
    new_pairs = sorted(alt_pairs - base_pairs)
    lost_pairs = sorted(base_pairs - alt_pairs)
    ties = _tie_stats(cycles)

    checks = {
        "all_cycles_present": len(cycles) == 120 * len(SEEDS),
        "nonempty_cycles": sum(1 for cycle in cycles.values() if cycle) == 701,
        "same_top20_membership": changed_cycles == 0 and changed_seats == 0,
        "no_pairs_gained_or_lost": not new_pairs and not lost_pairs,
        "stored_field_engages": order_changed_cycles > 0,
        "cutoff_ties_present": ties["cutoff_ties"] > 0,
        "cutoff_ties_have_equal_strength": (
            ties["cutoff_ties_resolved_by_strength"] == 0),
        "different_strength_ties_not_at_cutoff": (
            ties["different_strength_tie_groups"] > 0
            and ties["cutoff_ties_resolved_by_strength"] == 0),
    }
    if not all(checks.values()):
        raise SystemExit("REFUSED: checks " +
                         ", ".join(key for key, value in checks.items() if not value))

    summary = {
        "seeds": len(SEEDS),
        "cycles": len(cycles),
        "nonempty_cycles": sum(1 for cycle in cycles.values() if cycle),
        "ranked_rows": len(rows),
        "top20_seats": seats,
        "base_unique_edge_seed_pairs": len(base_pairs),
        "alt_unique_edge_seed_pairs": len(alt_pairs),
        "served_set": {
            "changed_cycles": changed_cycles,
            "changed_seats": changed_seats,
            "entering_pairs": len(entering),
            "leaving_pairs": len(leaving),
            "new_edge_seed_pairs": len(new_pairs),
            "lost_edge_seed_pairs": len(lost_pairs),
        },
        "order": {
            "changed_cycles": order_changed_cycles,
            "positions_changed": positions_changed,
            "mean_absolute_shift": statistics.fmean(shifts) if shifts else 0.0,
            "max_absolute_shift": max(shifts) if shifts else 0,
        },
        "ties": ties,
        "checks": checks,
        "verdict": ("SERVED SET UNCHANGED; ORDER CHANGES IN %d CYCLES"
                    % order_changed_cycles),
    }
    return engine_stamp.stamp({
        "kind": "stored_field_tiebreak",
        "status": "POST-HOC DIAGNOSTIC",
        "prereg": None,
        "posthoc": True,
        "engine": "no engine run; cached ranking features only",
        "question": (
            "Does using the stored strength/ratio field instead of source/target "
            "as the last tie-break change the top-20 served set?"
        ),
        "scope": (
            "Six consumed schema-prime seeds, 120 cycles each, cached ranking "
            "features. Top 20 by the engine's transition sort. No fresh seed."
        ),
        "design": {
            "seeds": SEEDS,
            "top_n": TOP_N,
            "base_key": (
                "schema priority, target entropy ascending, transition probability "
                "descending, count descending, source, target"
            ),
            "alternative_key": (
                "same, but stored strength descending before source and target"
            ),
            "stored_field": (
                "strength = min(1, ratio), where ratio = count / source frequency"
            ),
            "served_set": "top-20 membership, not full cap allocation",
        },
        "cache": CACHE.relative_to(ROOT).as_posix(),
        "summary": summary,
        "not_evidence": (
            "A post-hoc diagnostic on six already-consumed seeds. The stored "
            "strength is capped at 1, so an exact uncapped ratio is not tested "
            "where both tied rows are saturated. The result is candidate ordering, "
            "not served prediction, assertion, transfer or capability."
        ),
    })


def render(art: dict) -> str:
    s = art["summary"]
    served = s["served_set"]
    order = s["order"]
    ties = s["ties"]
    lines = [
        "# Stored-field tie-break — post hoc diagnostic",
        "",
        "Generated from `%s` by `python -m benchmarks.stored_field_tiebreak --write`. "
        "Do not edit by hand." % ARTIFACT.relative_to(ROOT).as_posix(),
        "",
        "**Verdict: `%s`.** Replacing source/target with the stored strength/ratio "
        "proxy changes no top-20 membership. It changes only the order inside "
        "tie groups." % s["verdict"],
        "",
        "## Design",
        "",
        "- Six consumed seeds (`%s`), 120 cycles each, **%d** ranked rows."
        % (", ".join(str(seed) for seed in art["design"]["seeds"]), s["ranked_rows"]),
        "- **%d** nonempty cycles and **%d** top-20 seats."
        % (s["nonempty_cycles"], s["top20_seats"]),
        "- Baseline tie-break: `source`, then `target`.",
        "- Alternative tie-break: stored `strength` descending, then `source`, "
        "then `target`.",
        "- The stored field is **`min(1, ratio)`**, not the uncapped ratio.",
        "- **Served set** means top-20 membership, not the full cap allocation.",
        "",
        "## Served-set change",
        "",
        "| Quantity | Change |",
        "| --- | ---: |",
        "| Top-20 seats changed | **%d** |" % served["changed_seats"],
        "| Windows changed | **%d** |" % served["changed_cycles"],
        "| Edge–seed pairs gained | **%d** |" % served["new_edge_seed_pairs"],
        "| Edge–seed pairs lost | **%d** |" % served["lost_edge_seed_pairs"],
        "",
        "The unique edge–seed set is identical: **%d** pairs in both orders."
        % s["base_unique_edge_seed_pairs"],
        "",
        "## Order change",
        "",
        "The stored field does change the order inside tie groups:",
        "",
        "| Quantity | Value |",
        "| --- | ---: |",
        "| Windows with a changed top-20 order | **%d** |" % order["changed_cycles"],
        "| Top-20 positions changed | **%d** |" % order["positions_changed"],
        "| Mean absolute shift | **%.3f** |" % order["mean_absolute_shift"],
        "| Maximum absolute shift | **%d** |" % order["max_absolute_shift"],
        "",
        "## Tie structure",
        "",
        "| Quantity | Value |",
        "| --- | ---: |",
        "| Windows with a cutoff tie | **%d / %d (%.2f%%)**"
        % (ties["cutoff_ties"], s["nonempty_cycles"],
           100 * ties["cutoff_tie_share"]),
        "| Cutoff ties resolved by strength | **%d** |"
        % ties["cutoff_ties_resolved_by_strength"],
        "| Cutoff ties with both strengths at 1.0 | **%d** |"
        % ties["cutoff_ties_saturated_at_one"],
        "| Adjacent top-20 primary ties | **%d / %d (%.2f%%)**"
        % (ties["adjacent_top20_ties"], ties["adjacent_top20_pairs"],
           100 * ties["adjacent_top20_tie_share"]),
        "| Adjacent full-list primary ties | **%d / %d (%.2f%%)**"
        % (ties["adjacent_full_ties"], ties["adjacent_full_pairs"],
           100 * ties["adjacent_full_tie_share"]),
        "| Top-20 rows involved in a primary tie | **%d / %d (%.2f%%)**"
        % (ties["top20_rows_in_tie"], ties["top20_rows"],
           100 * ties["top20_row_tie_share"]),
        "| Tie groups with different stored strength | **%d** |"
        % ties["different_strength_tie_groups"],
        "| Those groups inside the top 20 | **%d** |"
        % ties["different_strength_top20_groups"],
        "",
        "Every cutoff tie has the same stored strength. The 24 cutoff ties where "
        "both rows are saturated at 1.0 are the cases where an exact uncapped "
        "ratio could still separate them; that comparison is not available from "
        "this cache.",
        "",
        "## Checks",
        "",
        "| Check | Passes |",
        "| --- | --- |",
    ]
    for name, passed in s["checks"].items():
        lines.append("| `%s` | %s |" % (name, "yes" if passed else "no"))
    lines += [
        "",
        "## What this does and does not establish",
        "",
        "This is a null on top-20 membership under a stored-field tie-break. It "
        "does not show that ratio is irrelevant to ranking: it shows that the "
        "stored capped ratio is constant within every cutoff tie in these six "
        "worlds, so it cannot choose among the rows that decide the boundary.",
        "",
        "The result is candidate ordering only. It does not measure served "
        "predictions, asserted edges, downstream acquisition, transfer or "
        "capability, and the six seeds are reused. No engine file changed.",
        "",
        art["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def problems(art: dict | None = None) -> list[str]:
    art = _load(ARTIFACT) if art is None else art
    found: list[str] = []
    if art.get("kind") != "stored_field_tiebreak":
        found.append("artifact kind")
    if art.get("status") != "POST-HOC DIAGNOSTIC" or not art.get("posthoc"):
        found.append("diagnostic status")
    if art.get("prereg") is not None:
        found.append("prereg present")
    if engine_stamp.missing(art):
        found.append("stamp: %r" % (engine_stamp.missing(art),))
    s = art.get("summary") or {}
    if s.get("top20_seats") != 13604:
        found.append("seat count")
    if s.get("served_set", {}).get("changed_seats") != 0:
        found.append("served set changed")
    if s.get("served_set", {}).get("new_edge_seed_pairs") != 0:
        found.append("new pairs")
    if s.get("served_set", {}).get("lost_edge_seed_pairs") != 0:
        found.append("lost pairs")
    if s.get("order", {}).get("positions_changed", 0) <= 0:
        found.append("tie-break did not engage")
    if not all((s.get("checks") or {}).values()):
        found.append("checks")
    if PAGE.exists() and PAGE.read_text(encoding="utf-8") != render(art):
        found.append("page stale")
    return found


def write() -> int:
    art = build()
    ARTIFACT.write_text(json.dumps(art, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(art), encoding="utf-8")
    s = art["summary"]
    print("stored-field tie-break: %s %s"
          % (s["verdict"], json.dumps({
              "seats": s["top20_seats"],
              "changed_seats": s["served_set"]["changed_seats"],
              "changed_windows": s["served_set"]["changed_cycles"],
              "order_changes": s["order"]["positions_changed"],
              "cutoff_ties": s["ties"]["cutoff_ties"],
              "saturated_cutoff_ties": s["ties"]["cutoff_ties_saturated_at_one"],
          })))
    return 0


def check() -> int:
    if not ARTIFACT.exists():
        raise SystemExit("no artifact; run --write")
    art = _load(ARTIFACT)
    found = problems(art)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    s = art["summary"]
    print("stored-field tie-break: %s %s"
          % (s["verdict"], json.dumps({
              "changed_seats": s["served_set"]["changed_seats"],
              "order_changes": s["order"]["positions_changed"],
          })))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return write() if args.write else check()


if __name__ == "__main__":
    raise SystemExit(main())
