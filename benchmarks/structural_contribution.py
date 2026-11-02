"""The rewiring rule and the outcome table of the structural-contribution study.

This module implements §4 and §6 of
`docs/STRUCTURAL-CONTRIBUTION-PREREGISTRATION.md` and nothing else: the
degree-preserving double-edge swap, the invariants it must preserve, the two
gates that decide whether the rewired arm is a control at all, and the label a
combination of the three bounds carries.

It imports no engine module and reads no study seed, so its gates can run before
any cell exists — the same split as `functional_structure.py`. Standard library
only.

The rule, fixed in the protocol before a harness existed: choose two edges
`(a, b, w1)` and `(c, d, w2)`, exchange their targets to `(a, d, w1)` and
`(c, b, w2)`, and refuse the swap if it would create a self-loop or a duplicate
pair. Each success keeps both sources and both weights where they were, so the
node set, the edge count, per-source out-degree, per-target in-degree and the
multiset of weights are all preserved — and the pairing, hence each row's total
weight, is not.
"""
from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from statistics import median
from typing import Any, Sequence

Rows = dict[str, dict[str, float]]

#: §4: 25 independent draws per seed, mean used, the best draw never used.
DRAWS = 25
#: §4: attempts, not successes.
ATTEMPTS_PER_EDGE = 10
#: §4: the draw seed, so a seed reproduces every graph.
DRAW_SEED_MULTIPLIER = 1009
#: §4, gate S3b: above this the rewiring is not a control and the study stops.
UNCHANGED_LIMIT = 0.20
TOL = 1e-12


# ---------------------------------------------------------------------------
# Edges and rows
# ---------------------------------------------------------------------------

def edges_of(rows: Rows) -> list[tuple[str, str, float]]:
    """The edge list, sorted, so a draw never depends on dict ordering."""
    return [(a, b, float(w)) for a in sorted(rows) for b, w in sorted(rows[a].items())]


def rows_of(edges: Sequence[tuple[str, str, float]]) -> Rows:
    """The inverse of `edges_of`."""
    out: dict[str, dict[str, float]] = {}
    for a, b, w in edges:
        out.setdefault(a, {})[b] = float(w)
    return {a: out[a] for a in sorted(out)}


# ---------------------------------------------------------------------------
# The rewiring rule (§4)
# ---------------------------------------------------------------------------

def rewire(rows: Rows, seed: int, draw: int,
           attempts_per_edge: int = ATTEMPTS_PER_EDGE) -> Rows:
    """One degree-preserving rewiring: Maslov–Sneppen double-edge swaps.

    `seed` is a study seed and `draw` the index of this graph among the `K`, so
    the draw seed is `seed * 1009 + draw` and the graph is reproducible from the
    two numbers alone.
    """
    rng = random.Random(seed * DRAW_SEED_MULTIPLIER + draw)
    edges = edges_of(rows)
    if len(edges) < 2:
        return rows_of(edges)
    pairs = {(a, b) for a, b, _ in edges}
    for _ in range(attempts_per_edge * len(edges)):
        i, j = rng.sample(range(len(edges)), 2)
        a, b, w1 = edges[i]
        c, d, w2 = edges[j]
        # Same source or same target: the swap would be a no-op or a duplicate.
        if a == c or b == d:
            continue
        # Self-loop.
        if a == d or c == b:
            continue
        # Duplicate edge.
        if (a, d) in pairs or (c, b) in pairs:
            continue
        pairs.discard((a, b))
        pairs.discard((c, d))
        pairs.update(((a, d), (c, b)))
        edges[i] = (a, d, w1)
        edges[j] = (c, b, w2)
    return rows_of(edges)


def rewire_many(rows: Rows, seed: int, draws: int = DRAWS) -> list[Rows]:
    """The `K` graphs of one seed, in draw order."""
    base = rows_of(edges_of(rows))
    return [rewire(base, seed, draw) for draw in range(draws)]


# ---------------------------------------------------------------------------
# Gates S3b, S4 and S6 (§4, §8)
# ---------------------------------------------------------------------------

def invariants(original: Rows, rewired: Rows) -> dict[str, Any]:
    """Gate S4: what a double-edge swap must leave exactly unchanged.

    Out-degree and in-degree are counts of edges, not sums of weights; the weight
    multiset is compared exactly, because a swap moves weights and never
    recomputes them.
    """
    o = edges_of(original)
    r = edges_of(rewired)
    out_o = Counter(a for a, _, _ in o)
    out_r = Counter(a for a, _, _ in r)
    in_o = Counter(b for _, b, _ in o)
    in_r = Counter(b for _, b, _ in r)
    weights_o = sorted(w for _, _, w in o)
    weights_r = sorted(w for _, _, w in r)
    total_o, total_r = sum(weights_o), sum(weights_r)
    nodes_o = set(out_o) | set(in_o)
    nodes_r = set(out_r) | set(in_r)
    checks = {
        "node_set": nodes_o == nodes_r,
        "edge_count": len(o) == len(r),
        "out_degree": out_o == out_r,
        "in_degree": in_o == in_r,
        "weight_multiset": weights_o == weights_r,
        "total_weight": abs(total_o - total_r) <= TOL * max(1.0, abs(total_o)),
    }
    return {**checks, "preserved": all(checks.values())}


def unchanged_share(original: Rows, rewired: Rows) -> float:
    """Gate S3b: the fraction of `(source, target)` pairs the swap left in place."""
    before = {(a, b) for a, b, _ in edges_of(original)}
    after = {(a, b) for a, b, _ in edges_of(rewired)}
    if not before:
        return 1.0
    return len(before & after) / len(before)


def rewiring_report(rows: Rows, seed: int, draws: int = DRAWS) -> dict[str, Any]:
    """Everything the design audit needs to know about one seed's rewiring."""
    original = rows_of(edges_of(rows))
    graphs = rewire_many(original, seed, draws)
    checks = [invariants(original, graph) for graph in graphs]
    shares = [unchanged_share(original, graph) for graph in graphs]
    again = rewire_many(original, seed, draws)
    failed = [i for i, check in enumerate(checks) if not check["preserved"]]
    return {
        "edges": len(edges_of(original)),
        "draws": len(graphs),
        "attempts_per_edge": ATTEMPTS_PER_EDGE,
        "draw_seed_rule": f"seed * {DRAW_SEED_MULTIPLIER} + draw",
        "all_invariants_preserved": not failed,
        "draws_failing_invariants": failed[:5],
        "unchanged_share_max": round(max(shares), 6) if shares else 1.0,
        "unchanged_share_median": round(median(shares), 6) if shares else 1.0,
        "unchanged_limit": UNCHANGED_LIMIT,
        "unchanged_within_limit": bool(shares) and max(shares) <= UNCHANGED_LIMIT,
        "deterministic": graphs == again,
    }


# ---------------------------------------------------------------------------
# The outcome table (§6)
# ---------------------------------------------------------------------------

SUPPORTED = "structural contribution supported within this design"
NOT_ENOUGH = ("structure carries information the ablations destroy, and it is not "
              "enough for a predictive advantage over the simple baseline")
CONTENT_NOT_ESTABLISHED = ("graph structure helps; its specific content is not "
                           "established")
INCONSISTENT = ("inconsistent, and the current interpretation needs rethinking")
NO_CONTRIBUTION = "no detectable contribution from the formed edges on this window"

OUTCOME_ROW = "d_removed, d_rewired, d_bigram → label"


def outcome_label(removed: bool, rewired: bool, bigram: bool) -> str:
    """§6, fixed before any number exists: three bounds, five labels.

    `removed` and `rewired` are "the upper bound of that interval is below zero";
    `bigram` is the same for the comparator and never decides the primary
    criterion by itself.
    """
    if removed and rewired:
        return SUPPORTED if bigram else NOT_ENOUGH
    if removed and not rewired:
        return CONTENT_NOT_ESTABLISHED
    if rewired and not removed:
        return INCONSISTENT
    return NO_CONTRIBUTION


def outcome_table() -> list[dict[str, Any]]:
    """All eight combinations, so the table can be read against §6's five rows."""
    return [{"d_removed_below_zero": r, "d_rewired_below_zero": w,
             "d_bigram_below_zero": b, "label": outcome_label(r, w, b)}
            for r in (True, False) for w in (True, False) for b in (True, False)]


# ---------------------------------------------------------------------------
# Layer gates — no engine, no seed
# ---------------------------------------------------------------------------

def _synthetic(seed: int = 7, sources: int = 6, targets: int = 9,
               per_source: int = 4) -> Rows:
    """A small graph with distinct weights, so a broken swap is visible."""
    rng = random.Random(seed)
    rows: dict[str, dict[str, float]] = {}
    for i in range(sources):
        a = f"src{i}"
        picks = rng.sample(range(targets), per_source)
        rows[a] = {f"tgt{j}": float(10 * (j + 1) + i) for j in picks}
    return rows


def gate_fixtures() -> list[dict[str, Any]]:
    """The layer's own gates, proved able to fire. Raises on a mismatch."""
    report: list[dict[str, Any]] = []
    rows = _synthetic()

    # (i) A sparse graph can be rewired into a control: invariants hold, most
    # pairs move, and the same seed yields the same graphs.
    sparse = _synthetic(seed=7, sources=30, targets=120, per_source=3)
    sparse_info = rewiring_report(sparse, seed=20270301)
    assert sparse_info["all_invariants_preserved"], sparse_info
    assert sparse_info["unchanged_within_limit"], sparse_info
    assert sparse_info["deterministic"], sparse_info
    report.append({"case": "sparse_graph_rewires_into_a_control",
                   "edges": sparse_info["edges"],
                   "unchanged_share_max": sparse_info["unchanged_share_max"]})

    # (ii) A dense graph cannot: too few swaps are admissible, so too many pairs
    # survive.  The gate must say so rather than call the result a control.
    dense_info = rewiring_report(rows, seed=20270301)
    assert dense_info["all_invariants_preserved"], dense_info
    assert not dense_info["unchanged_within_limit"], dense_info
    report.append({"case": "dense_graph_fails_the_control_gate",
                   "edges": dense_info["edges"],
                   "unchanged_share_max": dense_info["unchanged_share_max"],
                   "passed": False})

    # (a) A swap that carries a weight to a new source breaks out-degree and the
    # weight multiset: the invariant gate must say so.
    broken = edges_of(rows)
    a, b, w1 = broken[0]
    c, d, w2 = broken[1]
    broken[0] = (a, d, w1)
    broken[1] = (c, b, w2 + 1.0)
    check = invariants(rows, rows_of(broken))
    assert not check["preserved"], check
    assert not check["weight_multiset"], check
    report.append({"case": "weight_moved_between_sources_fails_invariants",
                   "checks": {k: v for k, v in check.items() if k != "preserved"}})

    # (b) A rewiring that changes nothing must fail the control gate.
    assert unchanged_share(rows, rows) == 1.0
    assert not (1.0 <= UNCHANGED_LIMIT)
    report.append({"case": "identity_rewiring_fails_the_control_gate",
                   "unchanged_share": 1.0, "limit": UNCHANGED_LIMIT})

    # (c) An empty graph is not a rewired graph; the report says so rather than
    # quietly passing.
    empty = rewiring_report({}, seed=20270301)
    assert not empty["unchanged_within_limit"], empty
    report.append({"case": "empty_graph_is_not_a_control",
                   "unchanged_share_max": empty["unchanged_share_max"],
                   "passed": False})

    # (d) The outcome table names all eight combinations, and each of §6's five
    # rows is reachable.
    table = outcome_table()
    assert len(table) == 8, table
    labels = {row["label"] for row in table}
    assert labels == {SUPPORTED, NOT_ENOUGH, CONTENT_NOT_ESTABLISHED,
                      INCONSISTENT, NO_CONTRIBUTION}, labels
    report.append({"case": "outcome_table_reaches_five_labels",
                   "labels": sorted(labels)})
    return report


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gates", action="store_true", help="run the layer gates")
    args = ap.parse_args(argv)
    if not args.gates:
        ap.error("nothing to do; pass --gates")
    print(json.dumps(gate_fixtures(), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
