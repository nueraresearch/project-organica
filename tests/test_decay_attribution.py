"""Tests for the decay-attribution ledger (benchmarks/decay_attribution.py)."""

from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import json
from pathlib import Path

from benchmarks import decay_attribution as da


def _series(values, factor=0.95, theories_last=None, emit=None):
    rows = []
    for cycle, stable in enumerate(values, 1):
        emitted = stable if emit is None else min(stable, emit)
        rows.append({
            "cycle": cycle,
            "stable": stable,
            "hits": stable,
            "coverage": round(stable / 60, 4),
            "precision": 1.0 if stable else None,
            "theories": 1 if (theories_last is None or cycle <= theories_last) else 0,
            "beliefs": 2,
            "strengthened": stable,
            "decayed": 0,
            "pruned": 0,
            "emitted": emitted,
            "temporal_sum": 100 + cycle,
            "temporal_ge_min": stable,
            "temporal_max": 5,
            "hub_frequency": 50 + cycle,
            "median_ratio": 1.0,
            "deaths": 0,
            "by_reason": {},
            "decay_factor": factor,
            "decay_rows": 1,
        })
    return rows


def _part(arm, values, seed, theories_last=None, peak_edge_deaths=None):
    factor = 0.95 if arm == "engine" else 1.0
    deaths = peak_edge_deaths or {}
    return {
        "arm": arm,
        "seed": seed,
        "degree": 12,
        "cycles": len(values),
        "world_edges": 60,
        "decay_factor_set": factor,
        "series": _series(values, factor=factor, theories_last=theories_last),
        "peak_edges": 35,
        "peak_edge_deaths": deaths,
        "peak_edge_death_cycles": [20] * sum(deaths.values()),
        "peak_edges_alive_final": 0,
        "cycles_stable_exceeds_emitted": 0,
    }


ENGINE = [1, 5, 12, 20, 28, 35, 35, 34, 30, 26, 20, 14, 8, 4, 2, 1, 0, 0, 0, 0]
CONTROL_ALIVE = [1, 6, 14, 24, 34, 42, 42, 42, 41, 40, 38, 36, 34, 33, 32, 31, 30, 30, 30, 30]
CONTROL_DEAD = [1, 6, 14, 24, 34, 42, 41, 36, 28, 20, 14, 8, 4, 2, 1, 0, 0, 0, 0, 0]


def _parts(engine_values, control_values, engine_theories_last=None):
    parts = []
    for seed in (1, 2, 3):
        parts.append(_part("engine", engine_values, seed,
                           theories_last=engine_theories_last,
                           peak_edge_deaths={"decayed": 30, "below_threshold": 5}))
        parts.append(_part("no_temporal_decay", control_values, seed))
    return parts


def test_the_summary_finds_the_peak_the_first_fall_and_the_half_life():
    summary = da.summarise(_part("engine", ENGINE, 1))
    assert summary["peak"] == 35
    assert summary["peak_cycle"] == 6
    assert summary["first_fall"] == 8
    assert summary["zero_cycle"] == 17
    # 35 -> at most 17.5 at cycle 11 (value 20) is not yet half; cycle 12 (14) is.
    assert summary["half_life_cycles"] == 6


def test_the_theory_zero_is_terminal_not_the_first_empty_cycle():
    revived = [1, 5, 12, 20, 28, 35, 34, 30, 20, 10, 0, 3, 0]
    summary = da.summarise(_part("engine", revived, 1, theories_last=12))
    assert summary["theory_zero_cycle"] == 13

    never_zero = da.summarise(_part("engine", [1, 5, 12, 20], 1, theories_last=None))
    assert never_zero["theory_zero_cycle"] is None


def test_the_death_reasons_follow_the_engines_own_quantities():
    threshold, death = 0.3, 0.15
    assert da._reason(("a", "b"), 0.36, {}, threshold, death) == "decayed"
    # Above the threshold but not re-emitted is not a mechanism: the engine keeps it.
    assert da._reason(("a", "b"), 0.9, {}, threshold, death) == "unexplained"
    assert da._reason(("a", "b"), 0.15, {}, threshold, death) == "pruned"
    assert da._reason(("a", "b"), 0.9, {("a", "b"): 0.2}, threshold, death) == "below_threshold"
    assert da._reason(("a", "b"), 0.9, {("a", "b"): 0.5}, threshold, death) == "unexplained"


def test_a_surviving_control_labels_the_decay_as_the_mechanism():
    record = da.analyse(_parts(ENGINE, CONTROL_ALIVE))
    assert record["verdict"] == "TEMPORAL_EDGE_DECAY"
    assert record["by_arm"]["no_temporal_decay"]["final_stable_range"][0] >= 1
    assert not [f for f in record["failures"] if "unexplained" in f]


def test_a_control_that_collapses_with_the_engine_kills_the_decay_explanation():
    record = da.analyse(_parts(ENGINE, CONTROL_DEAD))
    assert record["verdict"] == "NOT_TEMPORAL_DECAY"


def test_an_engine_that_does_not_collapse_is_void_not_a_mechanism():
    record = da.analyse(_parts(CONTROL_ALIVE, CONTROL_ALIVE))
    assert record["verdict"] == "NO_COLLAPSE"


def test_a_peak_that_is_not_the_ceiling_blocks_every_mechanism_label():
    short = [1, 5, 12, 20, 28, 30, 29, 20, 10, 4, 0]
    record = da.analyse(_parts(short, CONTROL_ALIVE))
    assert record["verdict"] == "CEILING_NOT_REPRODUCED"
    assert any("peak" in failure for failure in record["failures"])


def test_the_page_carries_the_measured_first_fall_and_the_verdict():
    record = da.analyse(_parts(ENGINE, CONTROL_ALIVE))
    page = da.render(record)
    assert "TEMPORAL_EDGE_DECAY" in page
    assert str(record["by_arm"]["engine"]["first_fall_range"][0]) in page
    assert "{" not in page


def test_the_live_ledger_reproduces_the_engines_decision():
    """Regression: the reason must read this cycle's emissions, not the previous cycle's.

    The first build classified deaths against the prior cycle's emitted set and called
    re-emitted edges absent; on 25 cycles that produced unattributable deaths.
    """
    row = da.cell("engine", 20300601, cycles=25)
    reasons = {}
    for cycle in row["series"]:
        for reason, count in cycle["by_reason"].items():
            reasons[reason] = reasons.get(reason, 0) + count
    assert reasons.get("unexplained", 0) == 0, reasons
    assert row["peak_edges"] >= 1


def test_the_protocol_digest_covers_only_the_committed_sections():
    digest = da.protocol_digest()
    if digest is None:
        return
    text = da.PREREG.read_text(encoding="utf-8")
    assert "## 8." in text
    assert len(digest) == 64
