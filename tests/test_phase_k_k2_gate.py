"""The K2 build's refusal gates, proved reachable and proved able to pass.

The block has not run.  These are dry-run checks: they build synthetic
candidates, synthetic results and forged attempt records, and never open a
database or execute a sleep cycle.
"""
from __future__ import annotations

LAYER = "dry-run"  # benchmarks/test_layers.py: no cell is executed

import hashlib
import json
from functools import partial
from unittest.mock import patch

import pytest

from benchmarks import k2_block as runner
from benchmarks import k2_gate as gate
from benchmarks.k2_pre_switch_retention import (
    ASSOCIATION_TYPES,
    K2PreSwitchRetentionService,
    apply_demotions,
    empty_evidence,
)
from organica.candidates import LoopCandidate, PredictionCandidate
from organica.sleep import SleepService


def _out(tmp_path):
    return tmp_path / "phase_k_k2_results.json"


def _base(tmp_path, **overrides):
    out = _out(tmp_path)
    kwargs = {
        "families": list(gate.EXPECTED_FAMILIES),
        "seeds": list(gate.K2_SEEDS),
        "scale": 1,
        "smoke": False,
        "out_path": out,
        "checkpoint_path": tmp_path / "phase_k_k2_results.ndjson",
        "lease_path": tmp_path / "phase_k_k2_block_lease.json",
        "marker_path": tmp_path / "phase_k_k2_attempt.json",
        "primary_factory": partial(
            K2PreSwitchRetentionService, boundary_cycle=gate.K2_BOUNDARY_CYCLE),
        "k1_factory": partial(
            K2PreSwitchRetentionService, boundary_cycle=None),
        "env": {"PYTHONHASHSEED": "0"},
        "engine_tree_sha256": gate.expected_engine_tree(),
        "bootstrap_seed": gate.stable_bootstrap_seed(),
        "allowed_outputs": [out],
        "k1_noop_evidence": runner.k1_noop_evidence(),
    }
    kwargs.update(overrides)
    return kwargs


def _refused(code, **kwargs):
    with pytest.raises(gate.GateRefusal) as caught:
        gate.preflight(**kwargs)
    assert caught.value.code == code, caught.value.receipt()
    return caught.value


def _evidence(demoted=2, pre=0, before=1.0, after=0.5, counts=None):
    return {
        "boundary_cycle": 200,
        "association_types": list(ASSOCIATION_TYPES),
        "cycles_observed": 300,
        "pre_boundary_key_count": 4,
        "post_boundary_target_count": 2,
        "demoted_count": demoted,
        "pre_boundary_demotions": pre,
        "priority_before_sum": before,
        "priority_after_sum": after,
        "mean_priority_delta": round((after - before) / demoted, 6)
        if demoted else None,
        "min_priority_delta": round(after - before, 6) if demoted else None,
        "max_priority_delta": round(after - before, 6) if demoted else None,
        "target_type_counts": counts or {
            "loop_candidate": 1,
            "prediction_candidate": 1,
            "hypothesis": 0,
        },
        "sample_keys": ["k1", "k2"] if demoted else [],
    }


def _result(**overrides):
    body = {
        "attempt_id": "attempt-k2-1",
        "arm": {"class_hash": gate.class_hash(K2PreSwitchRetentionService)},
        "engine_tree_sha256": gate.expected_engine_tree(),
        "k2_gap": -0.4735,
        "k1": {"pre_value": gate.K1_PRE_VALUE, "abs_change": 0.0},
        "records": [],
    }
    for seed in gate.K2_SEEDS:
        body["records"].append(
            {"family": "K2", "seed": seed, "manipulation": _evidence()})
        body["records"].append(
            {"family": "K1", "seed": seed,
             "manipulation": _evidence(demoted=0, before=0.0, after=0.0,
                                       counts={name: 0 for name in ASSOCIATION_TYPES})})
    body.update(overrides)
    return body


def test_preflight_passes_with_the_frozen_contract(tmp_path):
    report = gate.preflight(**_base(tmp_path))
    assert report["state"] == "PREFLIGHT_OK"
    assert report["arms"]["primary_boundary_cycle"] == gate.K2_BOUNDARY_CYCLE
    assert report["arms"]["k1_boundary_cycle"] is None
    assert report["bootstrap_seed"] == gate.stable_bootstrap_seed()
    assert gate.stable_bootstrap_seed("K2") == gate.stable_bootstrap_seed()
    assert gate.stable_bootstrap_seed("K1") != gate.stable_bootstrap_seed()


# --- G-01 output destination -------------------------------------------------

def test_g01_output_destination_cases(tmp_path):
    _refused(
        "OUTPUT_IS_FROZEN",
        **_base(tmp_path, out_path=gate.FROZEN_RESULT,
                allowed_outputs=[gate.FROZEN_RESULT]))

    existing = _out(tmp_path)
    existing.write_text("sentinel", encoding="utf-8")
    _refused("OUTPUT_EXISTS", **_base(tmp_path, out_path=existing))

    target = tmp_path / "target.json"
    target.write_text("{}", encoding="utf-8")
    link = tmp_path / "link.json"
    link.symlink_to(target)
    _refused("OUTPUT_NOT_REGULAR", **_base(
        tmp_path, out_path=link, allowed_outputs=[link]))

    unregistered = tmp_path / "elsewhere.json"
    _refused("OUTPUT_PATH_NOT_REGISTERED", **_base(
        tmp_path, out_path=unregistered,
        allowed_outputs=[tmp_path / "registered.json"]))


# --- G-02 block identity -----------------------------------------------------

def test_g02_seed_block_family_and_scale_cases(tmp_path):
    _refused("SEED_BLOCK_MISMATCH", **_base(
        tmp_path, seeds=list(gate.K2_SEEDS[:-1])))
    _refused("SEED_BLOCK_MISMATCH", **_base(
        tmp_path, seeds=list(gate.K2_SEEDS) + [20261033]))
    _refused("FAMILY_SET_MISMATCH", **_base(tmp_path, families=["K2"]))
    _refused("FAMILY_SET_MISMATCH", **_base(
        tmp_path, families=["K1", "K2", "K3"]))
    _refused("SMOKE_NOT_A_JUDGED_CELL", **_base(tmp_path, smoke=True))
    _refused("JUDGED_RUN_REQUIRES_SCALE_1", **_base(tmp_path, scale=10))


# --- G-03 lease and attempt exclusivity --------------------------------------

def test_g03_lease_attempt_and_duplicate_records(tmp_path):
    lease = tmp_path / "phase_k_k2_block_lease.json"
    lease.write_text(json.dumps({"state": "ACTIVE", "owner": "other"}),
                     encoding="utf-8")
    _refused("K2_BLOCK_LEASE_HELD", **_base(tmp_path, lease_path=lease))

    marker = tmp_path / "phase_k_k2_attempt.json"
    marker.write_text(json.dumps({"state": "COMPLETE", "attempt_id": "old"}),
                      encoding="utf-8")
    _refused("K2_ATTEMPT_ALREADY_COMPLETED", **_base(
        tmp_path, marker_path=marker))

    (tmp_path / "attempt.log").write_text("duplicate", encoding="utf-8")
    _refused("DUPLICATE_AUDIT_LAYER", **_base(tmp_path))
    (tmp_path / "attempt.log").unlink()

    (tmp_path / "phase_k_k2_seed_20261023_lease.json").write_text(
        "{}", encoding="utf-8")
    _refused("K2_PER_SEED_LEASE_FORBIDDEN", **_base(tmp_path))


# --- G-04 arm wiring ---------------------------------------------------------

def test_g04_primary_and_noop_arm_cases(tmp_path):
    _refused("K2_PRIMARY_ARM_MISSING", **_base(
        tmp_path, primary_factory=None))
    _refused("K2_PRIMARY_ARM_NOT_TREATMENT", **_base(
        tmp_path, primary_factory=partial(SleepService, boundary_cycle=200)))
    _refused("K1_PRIMARY_ARM_MISSING", **_base(tmp_path, k1_factory=None))
    _refused("K1_NOOP_BOUNDARY_NOT_NONE", **_base(
        tmp_path, k1_factory=partial(
            K2PreSwitchRetentionService, boundary_cycle=200)))
    _refused("K1_NOOP_FIXTURE_MISMATCH", **_base(
        tmp_path, k1_noop_evidence={
            "demoted_count": 0, "priority_before_sum": 0.0,
            "priority_after_sum": 0.0, "shipped_hash": "a", "noop_hash": "b"}))


def test_g04_k1_noop_fixture_hashes_and_manipulation_are_checked(tmp_path):
    passing = runner.k1_noop_evidence()
    assert passing["counterfactual_demoted_count"] > 0
    assert passing["noop_manipulation"] == empty_evidence(None)
    assert gate.preflight(**(
        _base(tmp_path, k1_noop_evidence=passing)))["state"] == "PREFLIGHT_OK"
    _refused("K1_NOOP_FIXTURE_MISSING", **_base(
        tmp_path, k1_noop_evidence=None))

    broken = dict(passing)
    broken["noop_hash"] = "not-the-shipped-digest"
    refusal = _refused("K1_NOOP_FIXTURE_MISMATCH", **_base(
        tmp_path, k1_noop_evidence=broken))
    assert "selection_digest" in refusal.evidence["fixture_problems"]
    assert "argument_set" not in refusal.evidence["fixture_problems"]
    assert refusal.evidence["selection_detail"] == ["returned_digest"]

    # The argument set is one detail of that check, not a second condition:
    # the returned digest already contains the argument digest, so a forged
    # argument-only mismatch is still caught, and caught by the same code.
    broken = dict(passing)
    broken["noop_arguments_sha256"] = "not-the-shipped-arguments"
    refusal = _refused("K1_NOOP_FIXTURE_MISMATCH", **_base(
        tmp_path, k1_noop_evidence=broken))
    assert refusal.evidence["fixture_problems"] == ["selection_digest"]
    assert refusal.evidence["selection_detail"] == ["argument_set"]

    broken = dict(passing)
    broken["noop_fixture_sha256"] = "different-candidates"
    refusal = _refused("K1_NOOP_FIXTURE_MISMATCH", **_base(
        tmp_path, k1_noop_evidence=broken))
    assert "different_fixtures" in refusal.evidence["fixture_problems"]

    broken = dict(passing)
    broken["counterfactual_demoted_count"] = 0
    refusal = _refused("K1_NOOP_FIXTURE_MISMATCH", **_base(
        tmp_path, k1_noop_evidence=broken))
    assert "fixture_not_discriminating" in refusal.evidence["fixture_problems"]

    leaking = dict(passing)
    leaking["noop_manipulation"] = dict(
        passing["noop_manipulation"], demoted_count=2,
        priority_after_sum=0.5,
        target_type_counts={"loop_candidate": 1, "prediction_candidate": 1,
                            "hypothesis": 0})
    refusal = _refused("K1_NOOP_MANIPULATION_MISMATCH", **_base(
        tmp_path, k1_noop_evidence=leaking))
    assert "demoted_count" in refusal.evidence["differing_fields"]
    assert "priority_after_sum" in refusal.evidence["differing_fields"]


# --- G-05 signature and provenance ------------------------------------------

class _BadMultiple(K2PreSwitchRetentionService):
    def _retain_hypotheses(self, beliefs, info, temporal):
        return []


class _BadSignature(K2PreSwitchRetentionService):
    def _natural_selection(self, prior):
        return (0, 0, 0)


class _BadNoSuper(K2PreSwitchRetentionService):
    def _natural_selection(
        self, prior, concepts, phrases, loops, predictions,
        meta_concepts=None, processes=None, roles=None, workflows=None, schemas=None,
        hypotheses=None, theories=None, questions=None,
        dreams=None, investigations=None, experiments=None,
    ):
        return (0, 0, 0)


class _BadConstant(K2PreSwitchRetentionService):
    def _natural_selection(
        self, prior, concepts, phrases, loops, predictions,
        meta_concepts=None, processes=None, roles=None, workflows=None, schemas=None,
        hypotheses=None, theories=None, questions=None,
        dreams=None, investigations=None, experiments=None,
    ):
        self.DEATH_THRESHOLD = -1.0
        return (0, 0, 0)


def test_g05_signature_is_single_variable_and_can_fail():
    clean = gate.signature_evidence(K2PreSwitchRetentionService)
    assert clean["overrides"] == ["_natural_selection"]
    assert clean["extra_methods"] == []
    assert clean["super_calls"] == 1
    assert gate.signature_problems(K2PreSwitchRetentionService) == []

    assert gate.signature_problems(_BadMultiple)[0][0] == "K2_SIGNATURE_MULTIPLE_OVERRIDES"
    assert gate.signature_problems(_BadSignature)[0][0] == "K2_SIGNATURE_MISMATCH"
    assert any(code == "K2_SIGNATURE_NO_SUPER"
               for code, _ in gate.signature_problems(_BadNoSuper))
    assert any(code == "K2_ENGINE_CONSTANT_CHANGED"
               for code, _ in gate.signature_problems(_BadConstant))


def test_g05_pre_boundary_age_requires_treatment_state(tmp_path):
    _refused("PRE_BOUNDARY_AGE_UNAVAILABLE", **_base(
        tmp_path, association_age_source="engine"))


# --- G-06 engine and parameter freeze ---------------------------------------

def test_g06_engine_and_parameter_drift(tmp_path):
    _refused("ENGINE_PIN_MISMATCH", **_base(
        tmp_path, engine_tree_sha256="not-the-pin"))
    _refused("ARM_PARAMETER_DRIFT", **_base(
        tmp_path, primary_factory=partial(
            K2PreSwitchRetentionService, boundary_cycle=201)))
    _refused("ARM_PARAMETER_DRIFT", **_base(
        tmp_path, primary_factory=partial(
            K2PreSwitchRetentionService, boundary_cycle=200, penalty=0.4)))


# --- G-07 bootstrap determinism ---------------------------------------------

def test_g07_hash_seed_and_bootstrap_seed(tmp_path):
    _refused("PYTHONHASHSEED_NOT_ZERO", **_base(
        tmp_path, env={"PYTHONHASHSEED": "1"}))
    _refused("BOOTSTRAP_SEED_UNSTABLE", **_base(
        tmp_path, bootstrap_seed=gate.stable_bootstrap_seed() + 1))


# --- G-08 resume identity ----------------------------------------------------

def test_g08_resume_and_checkpoint_identity(tmp_path):
    out = _out(tmp_path)
    out.write_text(json.dumps({
        "attempt_id": "old", "arm_signature": "shipped",
        "protocol": {"seeds": list(gate.K2_SEEDS)}}), encoding="utf-8")
    _refused("RESUME_ARM_MISMATCH", **_base(
        tmp_path, resume=True, attempt_id="new", arm_signature="treatment"))

    checkpoint = tmp_path / "phase_k_k2_results.ndjson"
    checkpoint.write_text(json.dumps({
        "attempt_id": "foreign", "family": "K2", "seed": gate.K2_SEEDS[0]})
        + "\n", encoding="utf-8")
    out.write_text(json.dumps({
        "attempt_id": "new", "arm_signature": "treatment",
        "protocol": {"seeds": list(gate.K2_SEEDS)}}), encoding="utf-8")
    _refused("CHECKPOINT_ATTEMPT_MISMATCH", **_base(
        tmp_path, resume=True, attempt_id="new", arm_signature="treatment"))


# --- G-09 baseline provenance ------------------------------------------------

def test_g09_baseline_and_k1_pre_value(tmp_path):
    _refused("BASELINE_PROVENANCE_DRIFT", **_base(
        tmp_path, baseline_gap=-0.5734))
    _refused("K1_PRE_VALUE_MISSING", **_base(
        tmp_path, k1_pre_value=-0.3437))


# --- V gates ----------------------------------------------------------------

def _void(result):
    report = gate.validate_result(result)
    assert report["verdict"] == "VOID", report
    assert report["criteria_read"] is False
    return report


def test_v01_manipulation_cases_void():
    result = _result()
    result["records"][0]["manipulation"]["demoted_count"] = 0
    assert "G3_manipulation_occurred" in _void(result)["failed_gates"]

    result = _result()
    result["records"][0]["manipulation"]["pre_boundary_demotions"] = 3
    assert "G4_no_pre_boundary_demotions" in _void(result)["failed_gates"]

    result = _result()
    result["records"][0]["manipulation"]["target_type_counts"][
        "concept_candidate"] = 1
    assert "G5_target_scope" in _void(result)["failed_gates"]


def test_v02_incomplete_cells_void():
    result = _result()
    result["records"] = result["records"][1:]
    assert "G6_cell_completeness" in _void(result)["failed_gates"]


def test_v03_supported_label_cannot_bypass_gate():
    result = _result(verdict="SUPPORTED")
    assert "G7_gate_before_criterion" in _void(result)["failed_gates"]


def test_v04_engine_drift_voids():
    result = _result(engine_tree_sha256="changed")
    assert "G8_engine_pin_stable" in _void(result)["failed_gates"]


# --- A stops ----------------------------------------------------------------

def test_a01_missing_evidence_and_arithmetic_are_inconclusive():
    result = _result()
    del result["records"][0]["manipulation"]["mean_priority_delta"]
    report = gate.validate_result(result)
    assert report["verdict"] == "INCONCLUSIVE"
    assert report["criteria_read"] is False
    assert "A1_evidence_complete" in report["failed_gates"]

    result = _result()
    result["records"][0]["manipulation"]["priority_after_sum"] = 1.0
    report = gate.validate_result(result)
    assert report["verdict"] == "INCONCLUSIVE"
    assert "A1_evidence_complete" in report["failed_gates"]


def test_a02_k1_guard_must_be_computable_and_a_noop():
    result = _result()
    result["records"][1]["manipulation"]["demoted_count"] = 1
    report = gate.validate_result(result)
    assert report["verdict"] == "INCONCLUSIVE"
    assert "A2_k1_guard_computable" in report["failed_gates"]

    result = _result()
    result["k1"] = {"pre_value": gate.K1_PRE_VALUE}
    report = gate.validate_result(result)
    assert report["verdict"] == "INCONCLUSIVE"
    assert "A2_k1_guard_computable" in report["failed_gates"]


def test_a03_provenance_mismatch_is_inconclusive():
    result = _result()
    result["arm"]["class_hash"] = "not-the-class"
    report = gate.validate_result(result)
    assert report["verdict"] == "INCONCLUSIVE"
    assert "A3_provenance" in report["failed_gates"]

    result = _result()
    del result["arm"]
    report = gate.validate_result(result)
    assert report["verdict"] == "INCONCLUSIVE"
    assert "A3_provenance" in report["failed_gates"]


# --- passing twin and decision controls -------------------------------------

def test_valid_result_passes_and_decisions_are_live():
    assert gate.validate_result(_result())["verdict"] == "PASS"
    assert gate.decide(-0.4735, 0.0)["verdict"] == "PASS"
    assert gate.decide(-0.5535, 0.0)["verdict"] == "FAIL"
    assert gate.decide(-0.5035, 0.0)["verdict"] == "INCONCLUSIVE"
    assert gate.decide(-0.4735, 0.06)["verdict"] == "FAIL"


# --- treatment behaviour without an engine cell -----------------------------

def _service(boundary):
    service = object.__new__(K2PreSwitchRetentionService)
    service.boundary_cycle = boundary
    service.penalty = 0.5
    service.association_types = ASSOCIATION_TYPES
    service._seen_pre_boundary = {"loop:old"}
    service.manipulation = empty_evidence(boundary)
    service._count_prior_cycles = lambda prior: 199
    service._candidate_key = lambda record: record.get("id", "")
    return service


def test_treatment_demotes_pre_boundary_after_boundary_only():
    prior = [{"id": "loop:old", "type": "loop_candidate", "strength": 1.0}]
    service = _service(200)
    with patch.object(SleepService, "_natural_selection",
                      return_value=(0, 0, 0)) as base:
        service._natural_selection(prior, [], [], [], [])
    captured = base.call_args.args[0]
    assert captured[0]["strength"] == 0.5
    assert prior[0]["strength"] == 1.0
    assert service.manipulation["demoted_count"] == 1
    assert service.manipulation["pre_boundary_demotions"] == 0


def test_treatment_noop_is_the_same_class_with_no_boundary():
    prior = [{"id": "loop:old", "type": "loop_candidate", "strength": 1.0}]
    service = _service(None)
    with patch.object(SleepService, "_natural_selection",
                      return_value=(0, 0, 0)) as base:
        service._natural_selection(prior, [], [], [], [])
    assert base.call_args.args[0] is prior
    assert service.manipulation["demoted_count"] == 0
    assert service.manipulation["priority_before_sum"] == 0.0


def test_demotion_helper_never_touches_pre_boundary_cycles_or_other_types():
    prior = [
        {"id": "loop:old", "type": "loop_candidate", "strength": 1.0},
        {"id": "concept:old", "type": "concept_candidate", "confidence": 1.0},
    ]
    evidence = empty_evidence(200)
    adjusted = apply_demotions(
        prior, {"loop:old", "concept:old"},
        lambda record: record.get("id", ""),
        cycle=199, boundary_cycle=200, penalty=0.5, evidence=evidence)
    assert evidence["pre_boundary_demotions"] == 1
    assert adjusted[0] is prior[0]
    assert adjusted[1] is prior[1]

    evidence = empty_evidence(200)
    adjusted = apply_demotions(
        prior, {"loop:old", "concept:old"},
        lambda record: record.get("id", ""),
        cycle=200, boundary_cycle=200, penalty=0.5, evidence=evidence)
    assert evidence["demoted_count"] == 1
    assert adjusted[0]["strength"] == 0.5
    assert adjusted[1] is prior[1]
