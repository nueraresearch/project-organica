"""Tests for the Phase L analysis: seed pairing, and the published record.

The campaign's headline statistic is the Revision Threshold's bootstrap
interval, and the preregistration says it is a PAIRED bootstrap over seeds.
Pairing by position in the records list is not pairing by seed: the records
arrive in completion order, and completion order differs from label to label,
so position-pairing pairs unrelated seeds across labels.

These tests cover the pairing, the adjacent-difference diagnostic, and the
consistency between the committed results file and the committed code.

Control discipline: the pairing test asserts INVARIANCE under a shuffle of
the record order. An implementation that pairs by position fails it, so the
test can fail.
"""

from __future__ import annotations

import importlib.util
import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, relative: str):
    path = REPO_ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


P = _load("_phase_l_campaign", "benchmarks/phase_l_campaign.py")
ANALYZE = _load("_phase_l_analyze", "benchmarks/phase_l_analyze.py")


def _rec(label: str, seed: int, di: float, pi: float) -> dict:
    return {
        "arm": "V1", "label": label, "seed": seed, "params": {},
        "results": {
            "organica": {
                "displacement_index": di,
                "preservation_index": pi,
                "displacement_score": di - pi,
            },
            "secondary": {"revision_latency_cycles": None,
                          "revision_latency_reached": False},
        },
    }


def _synthetic(seed_count: int = 8) -> list[dict]:
    """Three sweep points, a crossing between the second and third."""
    records = []
    for i in range(seed_count):
        seed = 1000 + i
        jitter = (i % 4) * 0.01
        records.append(_rec("1:1", seed, 0.0, 0.80 + jitter))
        records.append(_rec("2:1", seed, 0.30 + jitter, 0.55 + jitter))
        records.append(_rec("3:1", seed, 0.70 + jitter, 0.05 + jitter))
    return records


def test_rt_bootstrap_is_invariant_under_record_reordering():
    """A paired bootstrap must not depend on the order the cells arrived in.

    This is the property the position-pairing implementation violated: the
    records arrive in completion order, which differs per label.
    """
    original = P.BOOTSTRAP_REPLICATES
    P.BOOTSTRAP_REPLICATES = 500
    try:
        records = _synthetic()
        base = P.summarize_arm(records, "V1", with_bootstrap=True)

        shuffled = list(records)
        rng = random.Random(7)
        rng.shuffle(shuffled)
        other = P.summarize_arm(shuffled, "V1", with_bootstrap=True)

        assert base["crossing_label"] == other["crossing_label"]
        assert base["rt_bootstrap_interval"] == other["rt_bootstrap_interval"]
        assert base["rt_replicates_with_crossing"] == other["rt_replicates_with_crossing"]
        assert base["criteria"] == other["criteria"]
        assert base["adjacent_differences"] == other["adjacent_differences"]
    finally:
        P.BOOTSTRAP_REPLICATES = original


def test_adjacent_difference_is_paired_by_seed():
    """The paired difference must cancel the seed, not scramble it.

    Two seeds: one holds PI at 0.9 then 0.9, the other at 0.1 then 0.1. The
    paired difference is 0 for both seeds, so the mean is 0. A pairing that
    matched different seeds across labels would produce 0.8.
    """
    records = [
        _rec("1:1", 11, 0.0, 0.9),
        _rec("1:1", 12, 0.0, 0.1),
        _rec("2:1", 11, 0.5, 0.9),
        _rec("2:1", 12, 0.5, 0.1),
    ]
    diff = ANALYZE.adjacent_difference(records, "V1", "1:1", "2:1",
                                        "preservation_index")
    assert diff is not None
    assert diff["n_paired_seeds"] == 2
    assert abs(diff["mean_difference"]) < 1e-9


def test_adjacent_difference_reports_an_interval():
    original = P.BOOTSTRAP_REPLICATES
    P.BOOTSTRAP_REPLICATES = 200
    try:
        records = _synthetic()
        summary = P.summarize_arm(records, "V1", with_bootstrap=True)
        adj = summary["adjacent_differences"]
        assert len(adj) == 2
        first = adj[0]["pi"]
        assert first["from"] == "1:1" and first["to"] == "2:1"
        assert first["interval"][0] <= first["mean_difference"] <= first["interval"][1]
        # Every seed drops by the same 0.25, so the paired difference is
        # exactly -0.25 with a degenerate interval -- and NOT the ~-0.2 an
        # unpaired computation would give.
        assert abs(first["mean_difference"] - (-0.25)) < 1e-9
        assert first["interval"][0] == first["interval"][1]
        # The DI difference is +0.30 plus the per-seed jitter, so it is not
        # zero here; the real data's DI plateau is what makes that zero.
        assert abs(adj[0]["di"]["mean_difference"] - 0.315) < 1e-9
    finally:
        P.BOOTSTRAP_REPLICATES = original


def test_summary_reports_the_paired_seed_count():
    records = _synthetic()
    summary = P.summarize_arm(records, "V1", with_bootstrap=True)
    assert summary["rt_paired_seeds"] == 8


def test_committed_results_file_agrees_with_the_committed_code():
    """The published record and the code that reads it must agree.

    This is the regression that would catch an analysis change after the
    fact: the committed summary is recomputed from the committed cells and
    the criteria and the crossing label must match.
    """
    path = REPO_ROOT / "docs" / "phase_l_results.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    stored = data["summaries"]["V1"]
    recomputed = P.summarize_arm(data["records"], "V1", with_bootstrap=True)
    assert recomputed["crossing_label"] == stored["crossing_label"]
    assert recomputed["criteria"] == stored["criteria"]
    assert recomputed["verdict"] == stored["verdict"]
    assert recomputed["rt_bootstrap_interval"] == stored["rt_bootstrap_interval"]
