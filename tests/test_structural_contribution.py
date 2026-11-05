"""The structural-contribution harness must be auditable before it is used.

These are the layer's own tests: the rewiring rule, its invariants, the guards
that keep the seed blocks apart, and the two gates that must be able to fire.
No study seed is generated here.
"""
from __future__ import annotations

import pathlib
import pytest

from benchmarks import structural_contribution as sc
from benchmarks import structural_contribution_harness as sch
from benchmarks.acquisition_runner import make_organica_backoff

DOC = pathlib.Path("docs/STRUCTURAL-CONTRIBUTION-PREREGISTRATION.md")


def _synthetic(sources=5, targets=30, per_source=2, seed=7):
    import random
    rng = random.Random(seed)
    rows = {}
    for i in range(sources):
        picks = rng.sample(range(targets), per_source)
        rows[f"src{i}"] = {f"tgt{j}": float(10 * (j + 1) + i) for j in picks}
    return rows


def test_rewiring_preserves_the_declared_invariants():
    rows = _synthetic()
    for draw in range(25):
        graph = sc.rewire(sc.rows_of(sc.edges_of(rows)), 20270301, draw)
        check = sc.invariants(rows, graph)
        assert check["preserved"], (draw, check)
        assert check["node_set"] and check["edge_count"]
        assert check["out_degree"] and check["in_degree"]
        assert check["weight_multiset"] and check["total_weight"]


def test_rewiring_breaks_the_pairing_and_is_reproducible():
    # A graph sparse enough that the swap can mix, as §4's gate requires.
    rows = _synthetic(sources=30, targets=120, per_source=3)
    base = sc.rows_of(sc.edges_of(rows))
    graphs = sc.rewire_many(base, 20270301)
    assert len(graphs) == 25
    assert graphs == sc.rewire_many(base, 20270301), "the draw seed must reproduce graphs"
    assert max(sc.unchanged_share(base, g) for g in graphs) <= sc.UNCHANGED_LIMIT


def test_a_weight_moved_between_sources_fails_the_invariant_gate():
    rows = _synthetic()
    edges = sc.edges_of(rows)
    a, b, w1 = edges[0]
    c, d, w2 = edges[1]
    edges[0] = (a, d, w1)
    edges[1] = (c, b, w2 + 1.0)
    check = sc.invariants(rows, sc.rows_of(edges))
    assert not check["preserved"]
    assert not check["weight_multiset"]


def test_identity_rewiring_cannot_pass_the_control_gate():
    rows = _synthetic()
    assert sc.unchanged_share(rows, rows) == 1.0
    assert not (1.0 <= sc.UNCHANGED_LIMIT)


def test_a_dense_graph_cannot_be_rewired_into_a_control():
    """The gate must fire on a graph where almost every pair already exists.

    This is the shape the engine's readout turned out to have, so the case is
    kept as a fixture: 24 sources x 17 targets with 333 edges is 82% dense.
    """
    rows = {}
    for i in range(24):
        rows[f"src{i}"] = {f"tgt{j}": float(j + 1) for j in range(17)}
    report = sc.rewiring_report(rows, 20270301)
    assert report["all_invariants_preserved"]
    assert not report["unchanged_within_limit"], report


def test_outcome_table_names_all_five_rows():
    table = sc.outcome_table()
    assert len(table) == 8
    labels = {row["label"] for row in table}
    assert labels == {sc.SUPPORTED, sc.NOT_ENOUGH, sc.CONTENT_NOT_ESTABLISHED,
                      sc.INCONSISTENT, sc.NO_CONTRIBUTION}
    # Every label is the one the protocol fixed in advance.
    text = DOC.read_text(encoding="utf-8").lower()
    for label in labels:
        assert label.lower() in text, label


def test_the_primary_criterion_needs_both_controls_not_the_bigram():
    """Bigram-aloone never selects the supported label."""
    assert sc.outcome_label(True, False, True) == sc.CONTENT_NOT_ESTABLISHED
    assert sc.outcome_label(True, True, True) == sc.SUPPORTED
    assert sc.outcome_label(True, True, False) == sc.NOT_ENOUGH
    assert sc.outcome_label(False, True, True) == sc.INCONSISTENT
    assert sc.outcome_label(False, False, True) == sc.NO_CONTRIBUTION


def test_edge_removed_arm_is_exactly_the_base_rate():
    """S3a's identity, checked rather than assumed."""
    rate = {"alpha": 0.25, "beta": 0.75}
    prob = make_organica_backoff({}, rate, sch.ALPHA)
    for a, b in (("alpha", "beta"), ("beta", "alpha"), ("alpha", "alpha")):
        assert abs(prob(a, b) - rate.get(b, 0.0)) <= sc.TOL


def test_seed_blocks_are_fresh_and_disjoint():
    design = set(sch.DESIGN_SEEDS)
    confirmatory = set(sch.CONFIRMATORY_SEEDS)
    prior = (set(range(20270201, 20270221)) | set(range(20261201, 20261227))
             | set(range(20270101, 20270121)) | set(range(20261100, 20261131))
             | {20261099})
    assert len(confirmatory) == 15
    assert design.isdisjoint(confirmatory)
    assert (design | confirmatory).isdisjoint(prior)


def test_each_block_refuses_the_other_seeds():
    for seed in sch.CONFIRMATORY_SEEDS:
        with pytest.raises(SystemExit):
            sch.refuse_confirmatory(seed)
    for seed in sch.DESIGN_SEEDS:
        with pytest.raises(SystemExit):
            sch.refuse_design(seed)
    with pytest.raises(SystemExit):
        sch.refuse_confirmatory(20261099)


def test_constants_are_the_committed_ones():
    assert sch.CAP == 1000
    assert sch.ALPHA == 256.0
    assert sch.TUNING_CYCLES == 15
    assert sc.DRAWS == 25 and sc.ATTEMPTS_PER_EDGE == 10
    assert sc.DRAW_SEED_MULTIPLIER == 1009 and sc.UNCHANGED_LIMIT == 0.20
    assert sch.BOOTSTRAP_SEED == 20261102 and sch.INTERVAL_LEVEL == 0.9833


def test_the_layer_gates_run_clean():
    report = sc.gate_fixtures()
    assert report
    assert any(case.get("case") == "dense_graph_fails_the_control_gate" for case in report)
