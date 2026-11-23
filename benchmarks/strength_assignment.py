"""The strength-assignment intervention and its gates.

Implements §4 and §7 of `docs/STRENGTH-ASSIGNMENT-PREREGISTRATION.md` and
nothing else, following the split `benchmarks/structural_contribution.py` uses
for the closed study: this module holds the intervention, the invariants it must
preserve, the gates that decide whether a draw tests anything, and the outcome
table. It needs no engine run, so its gates can fire before any study seed is
read. Standard library only.

The intervention, fixed in the protocol before this file existed: for each
source row independently, permute the row's weight values among the row's
existing targets. Topology is untouched by construction — every node, every
`(source, target)` pair, every out-degree, every in-degree, every row's weight
multiset and every row total are identical to the original. What changes is
which target inside a row carries which weight, and nothing else.

Why a permutation and not a rewiring: the closed study's null had to change the
graph while preserving degrees, and at this density those two requirements are
mutually unsatisfiable for most pairs — 95–96 % of pairs survived. A row-wise
permutation is always admissible, never re-pairs a source with a new target,
and its only "unchanged" case is the identity permutation of a row.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter
from statistics import median
from typing import Any, Sequence

Rows = dict[str, dict[str, float]]

#: §3: 25 independent draws per seed, mean used, the best draw never used.
DRAWS = 25
#: §4: this study's own draw multiplier, so its graphs differ from the closed
#: study's for the same seed and the same draw index.
DRAW_SEED_MULTIPLIER = 1013
#: §4, gate S2: the median draw must move at least this share of the edges.
MOVED_LIMIT = 0.5
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
# The intervention (§4)
# ---------------------------------------------------------------------------

def shuffle_once(rows: Rows, seed: int, draw: int) -> Rows:
    """One draw: permute each row's weights among that row's own targets.

    The draw seed is `seed * 1013 + draw`, so a graph is reproducible from two
    integers. Rows and targets are visited in sorted order, so the result does
    not depend on dict insertion order.
    """
    rng = random.Random(seed * DRAW_SEED_MULTIPLIER + draw)
    out: Rows = {}
    for a in sorted(rows):
        targets = sorted(rows[a])
        weights = [float(rows[a][b]) for b in targets]
        rng.shuffle(weights)                      # Fisher–Yates, in place
        out[a] = {b: w for b, w in zip(targets, weights)}
    return out


def shuffle_many(rows: Rows, seed: int, draws: int = DRAWS) -> list[Rows]:
    """The `K` graphs of one seed, in draw order."""
    return [shuffle_once(rows, seed, draw) for draw in range(draws)]


# ---------------------------------------------------------------------------
# Invariants (gate S1) and movement (gate S2)
# ---------------------------------------------------------------------------

def invariants(original: Rows, shuffled: Rows) -> dict[str, Any]:
    """Gate S1: what this intervention must leave exactly unchanged.

    Out-degree and in-degree are counts of edges; the row weight multiset and
    the row total are compared per row, because the permutation moves weights
    only within a row — a total that changed would mean a weight crossed rows.
    """
    o, s = edges_of(original), edges_of(shuffled)
    out_o = Counter(a for a, _, _ in o)
    out_s = Counter(a for a, _, _ in s)
    in_o = Counter(b for _, b, _ in o)
    in_s = Counter(b for _, b, _ in s)
    pairs_o = {(a, b) for a, b, _ in o}
    pairs_s = {(a, b) for a, b, _ in s}
    rows_o = {a: sorted(t.values()) for a, t in original.items()}
    rows_s = {a: sorted(t.values()) for a, t in shuffled.items()}
    totals_o = {a: sum(t.values()) for a, t in original.items()}
    totals_s = {a: sum(t.values()) for a, t in shuffled.items()}
    total_o, total_s = sum(totals_o.values()), sum(totals_s.values())
    checks = {
        "node_set": set(out_o) | set(in_o) == set(out_s) | set(in_s),
        "edge_pairs": pairs_o == pairs_s,
        "out_degree": out_o == out_s,
        "in_degree": in_o == in_s,
        "row_weight_multiset": rows_o == rows_s,
        "row_totals": all(abs(totals_o[a] - totals_s[a]) <= TOL * max(1.0, abs(totals_o[a]))
                          for a in totals_o),
        "total_weight": abs(total_o - total_s) <= TOL * max(1.0, abs(total_o)),
    }
    return {**checks, "preserved": all(checks.values())}


def moved_share(original: Rows, shuffled: Rows) -> float:
    """The fraction of edges whose weight differs from the original.

    Exact comparison, not a tolerance: a permuted weight that happens to equal
    the one it replaced moved nothing and should not be counted as movement.
    """
    pairs = [(a, b) for a in original for b in original[a]]
    if not pairs:
        return 0.0
    moved = sum(1 for a, b in pairs if original[a][b] != shuffled[a][b])
    return moved / len(pairs)


def changed_rows(original: Rows, shuffled: Rows) -> int:
    """Rows whose assignment is not the identity permutation."""
    return sum(1 for a in original if original[a] != shuffled[a])


def report(rows: Rows, seed: int, draws: int = DRAWS) -> dict[str, Any]:
    """Everything the design audit needs to know about one seed's draws."""
    original = rows_of(edges_of(rows))
    graphs = shuffle_many(original, seed, draws)
    checks = [invariants(original, graph) for graph in graphs]
    shares = [moved_share(original, graph) for graph in graphs]
    again = shuffle_many(original, seed, draws)
    failed = [i for i, check in enumerate(checks) if not check["preserved"]]
    multi = [a for a, t in original.items() if len(t) > 1]
    return {
        "edges": len(edges_of(original)),
        "rows": len(original),
        "multi_target_rows": len(multi),
        "draws": len(graphs),
        "draw_seed_rule": f"seed * {DRAW_SEED_MULTIPLIER} + draw",
        "all_invariants_preserved": not failed,
        "draws_failing_invariants": failed[:5],
        "moved_share_min": round(min(shares), 6) if shares else 0.0,
        "moved_share_median": round(median(shares), 6) if shares else 0.0,
        "moved_share_max": round(max(shares), 6) if shares else 0.0,
        "moved_limit": MOVED_LIMIT,
        "movement_within_limit": bool(shares) and median(shares) >= MOVED_LIMIT,
        "changed_rows_median": median([changed_rows(original, g) for g in graphs]) if graphs else 0,
        "deterministic": graphs == again,
    }


# ---------------------------------------------------------------------------
# A readout for the synthetic fixtures
# ---------------------------------------------------------------------------

def readout(rows: Rows, vocab: Sequence[str], alpha: float = 1.0):
    """`(w + alpha·m(b)) / (W(a) + alpha)`, the frozen readout's shape.

    Used only by the fixtures: the harness scores the real arms with the real
    `make_organica_backoff`, so nothing here can drift from the study's readout
    without the harness noticing.
    """
    uniform = 1.0 / max(1, len(vocab))
    totals = {a: sum(t.values()) for a, t in rows.items()}

    def prob(a: str, b: str) -> float:
        w = rows.get(a, {}).get(b, 0.0)
        return (w + alpha * uniform) / (totals.get(a, 0.0) + alpha)

    return prob


def _loss(prob, ctx, obs, vocab) -> float:
    """Mean per-cell log-loss over every vocab tag, as the frozen study scores."""
    total, n = 0.0, 0
    for c, o in zip(ctx, obs):
        truth = set(o) & set(vocab)
        for a in c:
            for b in vocab:
                p = min(1.0 - 1e-12, max(1e-12, prob(a, b)))
                y = 1 if (b in truth and b != a) else 0
                total += -(y * math.log(p) + (1 - y) * math.log(1 - p))
                n += 1
    return total / n if n else float("nan")


# ---------------------------------------------------------------------------
# The plants (§7 S3, S4)
# ---------------------------------------------------------------------------

PLANT_VOCAB = ("alpha", "bravo", "delta")
#: Nonconstant weights: the fixture that matters must not be able to pass on
#: equal weights, where every observation set is exchangeable trivially.
PLANT_WEIGHTS = (0.85, 0.10, 0.05)


def _planted_rows() -> Rows:
    row = dict(zip(PLANT_VOCAB, PLANT_WEIGHTS))
    return {"src": row}


def planted_positive(draw: int = 1) -> dict[str, Any]:
    """S3: a concentrated true successor, observed — shuffling must cost loss.

    The observation set is *open* under the permutation: it names exactly one of
    the row's targets, so which target carries the large weight decides the
    score. A harness that could not detect this could not detect anything.
    """
    rows = _planted_rows()
    vocab = list(PLANT_VOCAB)
    ctx, obs = [["src"]], [["alpha"]]
    full = _loss(readout(rows, vocab), ctx, obs, vocab)
    shuffled = _loss(readout(shuffle_once(rows, 20270401, draw), vocab), ctx, obs, vocab)
    return {"case": "positive_plant_shuffling_costs_loss",
            "full_log_loss": round(full, 9),
            "shuffled_log_loss": round(shuffled, 9),
            "increase": round(shuffled - full, 9),
            "passed": shuffled - full > 0.5}


def planted_negative_exchangeable(draw: int = 1) -> dict[str, Any]:
    """S4(a): nonconstant weights, closed observation set — exactly zero change.

    Every target in the row is observed, so the loss is a sum over the row's
    probability multiset and does not depend on which target carries which
    weight. This is the fixture the closed study's design lacked: a null that is
    reachable with *unequal* weights, so a zero result cannot be discounted as
    "the weights were all equal anyway".
    """
    rows = _planted_rows()
    vocab = list(PLANT_VOCAB)
    ctx, obs = [["src"]], [list(PLANT_VOCAB)]
    full = _loss(readout(rows, vocab), ctx, obs, vocab)
    shuffled = _loss(readout(shuffle_once(rows, 20270401, draw), vocab), ctx, obs, vocab)
    weights = sorted(rows["src"].values())
    return {"case": "negative_plant_exchangeable_nonconstant_weights",
            "weights": weights,
            "weights_are_nonconstant": len(set(weights)) == len(weights),
            "observation_set": "closed under the permutation (every target observed)",
            "change": round(shuffled - full, 15),
            "passed": abs(shuffled - full) <= TOL}


def planted_negative_constant() -> dict[str, Any]:
    """S4(b): constant weights — exchangeable under *any* observation set.

    Kept because it was the earlier study's fixture, and reported as the weaker
    of the two: it passes for a reason that does not test the design.
    """
    rows = {"src": {t: 0.25 for t in PLANT_VOCAB}}
    vocab = list(PLANT_VOCAB)
    ctx, obs = [["src"]], [["alpha"]]
    full = _loss(readout(rows, vocab), ctx, obs, vocab)
    shuffled = _loss(readout(shuffle_once(rows, 20270401, 1), vocab), ctx, obs, vocab)
    return {"case": "negative_plant_constant_weights",
            "label": "weaker fixture: passes trivially, not evidence about the design",
            "change": round(shuffled - full, 15),
            "passed": abs(shuffled - full) <= TOL}


def fixture_can_fail() -> dict[str, Any]:
    """The negative fixture must fail when its exchangeability is broken.

    Same nonconstant weights, same row, observation set opened to one target:
    the change must be large. A fixture that returned zero here would be
    measuring its own arithmetic rather than the design.
    """
    rows = _planted_rows()
    vocab = list(PLANT_VOCAB)
    ctx, obs = [["src"]], [["alpha"]]
    full = _loss(readout(rows, vocab), ctx, obs, vocab)
    shuffled = _loss(readout(shuffle_once(rows, 20270401, 1), vocab), ctx, obs, vocab)
    return {"case": "negative_fixture_fails_when_exchangeability_breaks",
            "change": round(shuffled - full, 9),
            "passed": shuffled - full > 0.5}


# ---------------------------------------------------------------------------
# The outcome table (§6)
# ---------------------------------------------------------------------------

CONTRIBUTES_AND_BEATS = ("strength assignment contributes, and the readout beats "
                         "the tuned bigram")
CONTRIBUTES_ONLY = ("strength assignment contributes; not enough for an advantage "
                    "over the simple baseline")
NOT_DEPENDENT = "the readout's advantage does not depend on which weight is where"
NO_CONTRIBUTION = "no detectable contribution of the strength assignment on this window"


def outcome_label(shuffled_wins: bool, bigram_wins: bool) -> str:
    """§6, fixed before any number exists: two bounds, four labels.

    `shuffled_wins` is "the lower bound of the interval on full − shuffled is
    above zero", the direction this study is built to detect; `bigram_wins` is
    the same for full − bigram and never decides the primary criterion.
    """
    if shuffled_wins:
        return CONTRIBUTES_AND_BEATS if bigram_wins else CONTRIBUTES_ONLY
    return NOT_DEPENDENT if bigram_wins else NO_CONTRIBUTION


def outcome_table() -> list[dict[str, Any]]:
    """All four combinations, so §6's rows can be read off the artifact."""
    return [{"d_shuffled_lower_bound_above_zero": s,
             "d_bigram_lower_bound_above_zero": b,
             "label": outcome_label(s, b)}
            for s in (True, False) for b in (True, False)]


# ---------------------------------------------------------------------------
# The layer's own gates
# ---------------------------------------------------------------------------

def gate_fixtures() -> list[dict[str, Any]]:
    """Every fixture, proved able to pass and, where it must, to fail."""
    report_: list[dict[str, Any]] = []

    rows = {"s1": {"t1": 4.0, "t2": 3.0, "t3": 2.0},
            "s2": {"t1": 1.0, "t4": 5.0},
            "s3": {"t5": 7.0}}
    shuffled = shuffle_once(rows, 20270401, 1)
    check = invariants(rows, shuffled)
    assert check["preserved"], check
    assert check["edge_pairs"], "topology must be identical, not merely similar"
    report_.append({"case": "invariants_preserved", "checks":
                    {k: v for k, v in check.items() if k != "preserved"}})

    # A weight that crosses rows breaks the row totals and the row multiset.
    broken = {a: dict(t) for a, t in rows.items()}
    moved = broken["s2"].pop("t4")
    broken["s3"]["t4"] = moved
    bad = invariants(rows, broken)
    assert not bad["preserved"], bad
    assert not bad["row_totals"], bad
    report_.append({"case": "cross_row_move_fails_invariants",
                    "checks": {k: v for k, v in bad.items() if k != "preserved"}})

    # The identity permutation is not a draw: it moves nothing.
    identity_share = moved_share(rows, rows)
    assert identity_share == 0.0
    assert not (identity_share >= MOVED_LIMIT)
    report_.append({"case": "identity_permutation_moves_nothing",
                    "moved_share": identity_share, "limit": MOVED_LIMIT})

    # A real draw moves most edges, and its invariants still hold.
    share = moved_share(rows, shuffled)
    assert share >= MOVED_LIMIT, share
    report_.append({"case": "real_draw_moves_most_edges", "moved_share": round(share, 6),
                    "limit": MOVED_LIMIT, "changed_rows": changed_rows(rows, shuffled)})

    for fixture in (planted_positive(), planted_negative_exchangeable(),
                    planted_negative_constant(), fixture_can_fail()):
        assert fixture["passed"], fixture
        report_.append(fixture)

    # The negative fixture's own weights must be unequal, or it proves nothing.
    assert len(set(PLANT_WEIGHTS)) == len(PLANT_WEIGHTS)
    report_.append({"case": "negative_fixture_weights_are_nonconstant",
                    "weights": sorted(PLANT_WEIGHTS)})

    table = outcome_table()
    assert len(table) == 4, table
    assert {row["label"] for row in table} == {
        CONTRIBUTES_AND_BEATS, CONTRIBUTES_ONLY, NOT_DEPENDENT, NO_CONTRIBUTION}
    report_.append({"case": "outcome_table_reaches_four_labels",
                    "labels": sorted({row["label"] for row in table})})

    # Determinism, twice in one process: the same seed and draw reproduce.
    first = shuffle_many(rows, 20270401)
    assert first == shuffle_many(rows, 20270401), "draws are not reproducible"
    report_.append({"case": "draws_reproduce_within_a_process", "draws": len(first)})
    return report_


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gates", action="store_true", help="run the layer's fixtures")
    args = ap.parse_args(argv)
    if not args.gates:
        ap.error("nothing to do; pass --gates")
    print(json.dumps(gate_fixtures(), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
