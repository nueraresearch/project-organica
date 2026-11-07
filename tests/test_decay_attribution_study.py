"""Controls for the decay-attribution replication's decision table and secondary labels."""

from __future__ import annotations

import json

from benchmarks.decay_attribution_study import (
    ARTIFACT,
    PAGE,
    decide,
    render,
    secondary_for,
)


def _cell(arm="engine", seed=1, **overrides):
    row = {
        "arm": arm,
        "seed": seed,
        "peak": 35,
        "peak_coverage": 0.5833,
        "final": 0,
        "first_zero_cycle": 173,
        "first_fall_cycle": 16,
        "last_theory_cycle": 28,
        "half_life_cycles": 65,
        "deaths": 100,
        "by_reason": {"below_threshold": 31, "decayed": 69, "pruned": 0, "unexplained": 0},
        "below_threshold_share": 0.31,
        "decayed_share": 0.69,
        "core_survives": False,
        "decay_factor_seen": [0.95] if arm == "engine" else [1.0],
        "decay_rows_min": 1,
    }
    row.update(overrides)
    return row


def _control(seed=1, **overrides):
    row = _cell("no_temporal_decay", seed, peak=42, peak_coverage=0.7, final=30,
                first_zero_cycle=None, **overrides)
    return row


def _engine(n=12, **overrides):
    return [_cell(seed=i, **overrides) for i in range(1, n + 1)]


def _controls(n=12, **overrides):
    return [_control(seed=i, **overrides) for i in range(1, n + 1)]


def test_all_targets_hold_gives_replicated():
    result = decide(_engine(), _controls())
    assert result["label"] == "REPLICATED"
    assert result["table_gap"] is None


def test_a_dead_perturbation_voids_the_run():
    engine = _engine()
    engine[0]["decay_factor_seen"] = [1.0]
    assert decide(engine, _controls())["label"] == "VOID_INSTRUMENT"


def test_a_missed_ceiling_voids_the_run():
    engine = _engine()
    engine[0]["peak"] = 34
    assert decide(engine, _controls())["label"] == "VOID_INSTRUMENT"


def test_an_unexplained_death_voids_the_run():
    engine = _engine()
    engine[0]["by_reason"] = {"below_threshold": 31, "decayed": 68, "pruned": 0, "unexplained": 1}
    assert decide(engine, _controls())["label"] == "VOID_INSTRUMENT"


def test_a_collapse_that_does_not_happen_is_not_replicated():
    engine = _engine()
    for row in engine[:2]:
        row["first_zero_cycle"] = None
    assert decide(engine, _controls())["label"] == "NOT_REPLICATED"


def test_two_seeds_that_do_not_end_at_zero_are_not_replicated():
    engine = _engine()
    for row in engine[:2]:
        row["final"] = 3
    assert decide(engine, _controls())["label"] == "NOT_REPLICATED"


def test_a_shifted_band_keeps_the_mechanism_but_not_the_constant():
    engine = _engine()
    for row in engine:
        row["below_threshold_share"] = 0.55
    result = decide(engine, _controls())
    assert result["label"] == "REPLICATED_WITH_SHIFT"
    assert result["table_gap"] is None


def test_a_failed_timing_criterion_is_a_recorded_table_gap():
    engine = _engine()
    for row in engine:
        row["first_fall_cycle"] = 40
    result = decide(engine, _controls())
    assert result["label"] == "REPLICATED_WITH_SHIFT"
    assert "outside the WITH_SHIFT condition" in result["table_gap"]


def test_an_unmeasurable_death_share_fails_the_band_rather_than_passing_it():
    engine = _engine()
    engine[0]["deaths"] = 0
    engine[0]["by_reason"] = {}
    engine[0]["below_threshold_share"] = None
    assert decide(engine, _controls())["predictions"]["P5_below_threshold_band"] is False


def test_an_unmeasurable_half_life_fails_the_band_rather_than_passing_it():
    engine = _engine()
    engine[0]["half_life_cycles"] = None
    assert decide(engine, _controls())["predictions"]["P6_half_life_band"] is False


def test_no_core_and_a_tight_zero_range_is_full_collapse_and_scheduled():
    secondary = secondary_for(_engine())
    assert secondary["core"] == "FULL_COLLAPSE"
    assert secondary["collapse"] == "COLLAPSE_SCHEDULED"
    assert secondary["mechanism"] == "DECAY_DOMINANT"


def test_two_surviving_cores_are_named_and_a_wide_range_is_seeded():
    engine = _engine()
    engine[0]["core_survives"] = True
    engine[1]["core_survives"] = True
    for i, row in enumerate(engine):
        row["first_zero_cycle"] = 150 + i * 5
    secondary = secondary_for(engine)
    assert secondary["core"] == "CORE_SURVIVES"
    assert secondary["collapse"] == "COLLAPSE_SEEDED"


def test_a_below_threshold_majority_is_threshold_dominant():
    engine = _engine()
    for row in engine:
        row["decayed_share"] = 0.40
        row["below_threshold_share"] = 0.60
    assert secondary_for(engine)["mechanism"] == "THRESHOLD_DOMINANT"


def test_the_page_is_the_render_of_the_artifact_and_names_its_label():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["label"] in {
        "REPLICATED", "REPLICATED_WITH_SHIFT", "NOT_REPLICATED", "VOID_INSTRUMENT"
    }
    assert PAGE.read_text(encoding="utf-8") == render(artifact)
    assert artifact["label"] in render(artifact)
    assert "{}" not in render(artifact)
