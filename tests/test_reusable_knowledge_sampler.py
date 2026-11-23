"""Proof tests for the generator-only reusable-knowledge sampler."""
from __future__ import annotations

import random

import pytest

from benchmarks import reusable_knowledge_sampler as sampler

LAYER = "synthetic"  # generates compositional worlds; runs no engine cell


class TestProtocolConfiguration:
    def test_reads_fixed_variant_and_relation_counts(self):
        variant, gate = sampler.protocol_config()
        assert variant["name"] == "V1.1-cap(1000)"
        assert variant["max_predictions"] == 1000
        assert variant["transfer_floor_per_withheld_transition"] == 20
        assert gate["total_relations"] == 128
        assert gate["withheld_relations"] == 32
        assert gate["available_during_formation"] == 96

    def test_rejects_wrong_capacity(self, monkeypatch):
        original = sampler._load_json

        def wrong_capacity(path):
            value = original(path)
            if path == sampler.VARIANT_CONFIG:
                value["max_predictions"] = 20
            return value

        monkeypatch.setattr(sampler, "_load_json", wrong_capacity)
        with pytest.raises(ValueError, match="not cap 1,000"):
            sampler.protocol_config()

    def test_rejects_wrong_gate_denominator(self, monkeypatch):
        original = sampler._load_json

        def wrong_denominator(path):
            value = original(path)
            if path == sampler.GATE_CONFIG:
                value["available_during_formation"] = 128
            return value

        monkeypatch.setattr(sampler, "_load_json", wrong_denominator)
        with pytest.raises(ValueError, match="denominator"):
            sampler.protocol_config()

    def test_rejects_withholding_rule_drift(self, monkeypatch):
        original = sampler._load_json

        def different_rule(path):
            value = original(path)
            if path == sampler.FEASIBILITY_CONFIG:
                value["chosen_rule"] = [["(1, 0)", "flip_p"], ["(1, 1)", "flip_q"]]
            return value

        monkeypatch.setattr(sampler, "_load_json", different_rule)
        with pytest.raises(ValueError, match="withholding rule disagrees"):
            sampler.protocol_config()


class TestRelationSets:
    def test_available_and_withheld_relations_partition_the_128(self):
        world = sampler.generate_compositional_world(seed=20261201)
        available = sampler.available_relations(world)
        withheld = sampler.withheld_relations(world)
        assert len(available) == 96
        assert len(withheld) == 32
        assert available.isdisjoint(withheld)
        assert len(available | withheld) == 128


class TestConditionedSampler:
    def test_generates_full_continuous_formation_without_withheld_pairs(self):
        result = sampler.build_conditioned_study_world(20261201)
        formation = result["formation"]
        audit = result["formation_audit"]
        assert audit["events_generated"] == 110 * 8
        assert audit["all_events_stored"] is True
        assert audit["consecutive_event_pairs"] == 110 * 8 - 1
        assert audit["forbidden_pairs"] == 0
        assert audit["withheld_transition_instances"] == 0
        assert audit["conditioned_resamples"] > 0
        assert audit["warmup_resamples"] > 0
        assert audit["acquisition_resamples"] > 0
        assert audit["both_formation_phases_conditioned"] is True
        assert len(formation["events"]) == len(formation["cells"])
        assert len(formation["cells"]) == len(formation["transition_kinds"])
        assert result["legacy_mask_reused"] is False
        assert "trainable" not in result["world"]
        assert "withheld" not in result["world"]

    def test_is_reproducible_for_a_seed(self):
        left = sampler.build_conditioned_study_world(20261202)
        right = sampler.build_conditioned_study_world(20261202)
        assert left["formation"]["events"] == right["formation"]["events"]
        assert left["formation"]["cells"] == right["formation"]["cells"]
        assert left["formation_audit"] == right["formation_audit"]
        assert left["transfer_audit"] == right["transfer_audit"]

    def test_transfer_floor_is_counted_in_the_real_50_cycle_window(self):
        result = sampler.build_conditioned_study_world(20261201)
        audit = result["transfer_audit"]
        assert audit["phase_cycles"] == [150, 200]
        assert audit["window_cycles"] == 50
        assert len(audit["withheld_transition_counts"]) == 2
        assert audit["minimum_per_transition"] >= 20
        assert audit["floor_passed"] is True

    def test_short_world_rejects_missing_scoring_windows(self):
        with pytest.raises(ValueError, match="complete retention and transfer"):
            sampler.build_conditioned_study_world(20261203, cycles=199)


def test_all_calibration_seeds_meet_the_transfer_floor_without_engine_runs():
    variant, _ = sampler.protocol_config()
    results = [sampler.build_conditioned_study_world(seed)
               for seed in variant["gate_f_calibration"]["seeds"]]
    assert [r["seed"] for r in results] == variant["gate_f_calibration"]["seeds"]
    assert all(r["transfer_audit"]["floor_passed"] for r in results)
    assert all(r["formation_audit"]["both_formation_phases_conditioned"]
               for r in results)


def test_the_oracle_reproduces_the_study_formation_stream():
    """The study's stream is the harness's; the oracle must produce the same events."""
    from benchmarks import reusable_knowledge as harness
    from benchmarks.acquisition_compositional import CYCLES, generate_compositional_world

    variant, _ = sampler.protocol_config()
    for seed in variant["gate_f_calibration"]["seeds"]:
        world = generate_compositional_world(seed=seed, cycles=CYCLES)
        study = harness.conditioned_formation_stream(world, seed)
        oracle = sampler.build_conditioned_study_world(seed)["formation"]
        assert oracle["events"] == study["events"], "formation events diverge on %d" % seed
        assert oracle["cells"] == study["cells"], "formation cells diverge on %d" % seed


def test_the_oracle_check_can_fail(monkeypatch):
    """A different stream must be caught, so the equality above is not decoration."""
    from benchmarks import reusable_knowledge as harness
    from benchmarks.acquisition_compositional import CYCLES, generate_compositional_world

    seed = 20261201
    world = generate_compositional_world(seed=seed, cycles=CYCLES)
    study = harness.conditioned_formation_stream(world, seed)
    monkeypatch.setattr(sampler, "study_formation_rng",
                        lambda s: random.Random(s * 31 + 8))
    oracle = sampler.build_conditioned_study_world(seed)["formation"]
    assert oracle["events"] != study["events"]
