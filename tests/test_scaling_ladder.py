"""The scaling ladder's guards and its diagnostics, without running a world.

The ladder itself is five engine runs; these tests cover the parts that decide
whether its numbers mean anything: the seed guard, the decision rule, the
clustering diagnostic, and the prefix check the slicing depends on.
"""
from __future__ import annotations

import json
import pathlib
import re

import pytest

from benchmarks import scaling_ladder as sl

ROOT = pathlib.Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Guards and the rule
# ---------------------------------------------------------------------------

def test_a_study_seed_is_refused_before_a_database_opens():
    """Design and confirmatory seeds of both studies are off limits."""
    for seed in (20270401, 20270407, 20261201, 20261210):
        with pytest.raises(SystemExit):
            sl.refuse_study_seed(seed)


def test_the_methodology_block_is_itself_refused_when_not_asked_for():
    with pytest.raises(SystemExit):
        sl.refuse_study_seed(20270101)


def test_its_own_seeds_are_allowed_and_fresh():
    for seed in sl.SEEDS:
        assert sl.refuse_study_seed(seed) == seed
    assert not set(sl.SEEDS) & sl.FORBIDDEN_SEEDS


def test_the_verdict_table_is_the_one_that_was_committed():
    """§5, at its boundaries: the rule cannot drift with the numbers."""
    assert sl.verdict(None) == "not measurable"
    assert sl.verdict(0.10) == "replication-limited"
    assert sl.verdict(0.50) == "replication-limited"
    assert sl.verdict(0.51) == "both"
    assert sl.verdict(0.99) == "both"
    assert sl.verdict(1.00) == "resolution-limited"
    assert sl.verdict(3.00) == "resolution-limited"


# ---------------------------------------------------------------------------
# The diagnostics
# ---------------------------------------------------------------------------

def test_clustering_is_detected_not_assumed():
    """Two series with the same mean and spread: one clustered, one not.

    A block bootstrap must return a much larger error for the clustered series.
    If it did not, the quarters would be decoration.
    """
    import random
    rng = random.Random(11)
    clustered = ([0.10] * 100 + [0.12] * 100 + [0.08] * 100 + [0.11] * 100)
    independent = [0.10 + rng.gauss(0.0, 0.01) for _ in range(400)]
    c = sl.block_stats(clustered)
    i = sl.block_stats(independent)
    assert c["block_over_iid"] and i["block_over_iid"]
    assert c["block_over_iid"] > 5 * i["block_over_iid"], (c, i)
    assert abs(sum(clustered) / len(clustered) - sum(independent) / len(independent)) < 0.005


def test_consistency_counts_the_quarters():
    same = sl.block_stats([0.05] * 400)
    assert same["quarters_positive"] == sl.BLOCKS
    flipped = sl.block_stats([0.05] * 200 + [-0.05] * 200)
    assert flipped["quarters_positive"] == 2
    assert flipped["spread"] > 0


def test_runs_for_precision_is_derived_and_can_be_unreachable():
    assert sl.runs_for_precision(0.05, 0.01) == pytest.approx(4.76, abs=0.01)
    assert sl.runs_for_precision(0.05, 0.03) is None      # within already exceeds the target
    assert sl.runs_for_precision(None, 0.01) is None


# ---------------------------------------------------------------------------
# The slicing the ladder depends on
# ---------------------------------------------------------------------------

def test_the_window_arithmetic_and_the_dead_axis_guard():
    """A scale is a length; the scorer takes an end cycle. Empty must shout.

    The first ladder run passed a length where an end belonged, scored `150 -> 50`
    — no observations — and only failed when an empty list was averaged.
    """
    assert sl.window_end(1) == sl.PHASE_TRANSFER[1]
    assert sl.window_end(16) == 950
    with pytest.raises(AssertionError):
        sl.window_pairs(["alpha beta gamma delta"] * 100, 50)


def test_the_shorter_worlds_are_prefixes_of_the_longest():
    """Every scale must score the same world, just less of it."""
    check = sl.prefix_check(sl.SEEDS[0])
    assert check["consistent"], check["checked"]
    assert len(check["checked"]) == len(sl.SCALES)


# ---------------------------------------------------------------------------
# The document must contain the artifact's numbers
# ---------------------------------------------------------------------------

def test_the_document_quotes_the_artifact():
    """Every delta in the results table is the artifact's, to six decimals."""
    art_path = ROOT / sl.OUT
    doc = (ROOT / "docs/SCALING-LADDER.md").read_text(encoding="utf-8")
    if not art_path.exists():
        pytest.skip("the ladder has not been run yet")
    art = json.loads(art_path.read_text(encoding="utf-8"))
    if "| `1x` |" not in doc or "## 7." not in doc:
        pytest.skip("the results section has not been written yet")
    block = doc.split("## 7.", 1)[1]
    for label in sl.SCALES:
        row = art["summary"][label]
        for value in (row["delta_mean"], row["within_se_block_mean"],
                      row["delta_sd_between"]):
            assert f"{value:.6f}".lstrip("-") in block, (label, value)
        assert re.search(rf"`{re.escape(label)}`", block), label
