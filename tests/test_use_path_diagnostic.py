"""The use-path diagnostic's own checks.

Each control ships with a test that FIRES: the test mutates the condition the
control exists to detect and asserts the control rejects it.  The D0 gate gets
the strongest test — a 2e-4 perturbation must fail it, and a failed gate must
make the analysis raise and the result document refuse a mechanism section.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import formation_utilization as fu  # noqa: E402
from benchmarks import use_path_diagnostic as d  # noqa: E402


# ---------------------------------------------------------------------------
# Freeze
# ---------------------------------------------------------------------------

def test_freeze_accepts_a_matching_record(tmp_path):
    protocol = tmp_path / "USE-PATH-DIAGNOSTIC-PREREGISTRATION.md"
    protocol.write_text("frozen protocol\n", encoding="utf-8")
    freeze = tmp_path / "freeze.json"
    digest = d._sha256(protocol)
    freeze.write_text(json.dumps({"protocol": str(protocol),
                                  "protocol_sha256": digest}),
                      encoding="utf-8")
    record = d.check_freeze(protocol, freeze)
    assert record["protocol_sha256"] == digest


def test_freeze_fires_when_the_protocol_changes(tmp_path):
    protocol = tmp_path / "USE-PATH-DIAGNOSTIC-PREREGISTRATION.md"
    protocol.write_text("frozen protocol\n", encoding="utf-8")
    freeze = tmp_path / "freeze.json"
    freeze.write_text(json.dumps({
        "protocol": str(protocol),
        "protocol_sha256": d._sha256(protocol),
    }), encoding="utf-8")
    protocol.write_text("edited after the freeze\n", encoding="utf-8")
    with pytest.raises(d.ProtocolNotFrozen):
        d.check_freeze(protocol, freeze)


# ---------------------------------------------------------------------------
# D0 — the validity gate
# ---------------------------------------------------------------------------

def _record(task="T2", seed=20261101):
    return {
        "task": task,
        "seed": seed,
        "d0": {"retention": 0.5, "transfer": 0.4, "revision": 0.45},
        "variants": {
            arm: {"retention": 0.5, "transfer": 0.4, "revision": 0.45}
            for arm in ("D1", "D2", "D3", "D4")
        },
        "d5": {"retention": 0.3, "transfer": 0.3, "revision": 0.3},
        "limb_counts": {
            limb: {"events": 10, "cells": 100} for limb in d.LIMBS
        },
        "attribution": {"ok": True},
    }


def test_d0_passes_on_an_exact_reproduction():
    record = _record()
    campaign = {("T2", record["seed"]): dict(record["d0"])}
    gate = d.audit_d0_reproduction([record], campaign, expected_units=1)
    assert gate["passed"], gate["reason"]
    assert gate["max_abs_diff"] == 0.0


def test_d0_fires_on_a_2e4_perturbation():
    record = _record()
    campaign = {("T2", record["seed"]): dict(record["d0"])}
    record["d0"]["transfer"] += 2e-4
    gate = d.audit_d0_reproduction([record], campaign, expected_units=1)
    assert gate["passed"] is False
    assert gate["max_abs_diff"] >= 2e-4
    assert any(f.get("limb") == "transfer" for f in gate["failures"])


def test_d0_fires_on_a_missing_unit():
    record = _record()
    campaign = {("T2", record["seed"]): dict(record["d0"])}
    gate = d.audit_d0_reproduction([record], campaign, expected_units=2)
    assert gate["passed"] is False
    assert "units missing" in gate["reason"] or gate["failures"]


def test_analyse_refuses_to_map_a_failed_gate():
    record = _record()
    with pytest.raises(d.AuditRequired):
        d.analyse([record, record], d0_gate={"passed": False})


def test_analyse_reports_one_seed_as_not_measurable():
    result = d.analyse([_record()], d0_gate={"passed": True})
    assert result["cells"]["T2"]["D1"]["transfer"]["verdict"] == "not measurable"
    assert result["mapping"]["outcome"] == "not_measurable"


def test_result_generator_cannot_emit_a_mechanism_after_a_failed_gate():
    artifact = {
        "d0_reproduction": {
            "passed": False, "expected_units": 2, "units_present": 1,
            "n_checks": 3, "max_abs_diff": 0.0002, "tolerance": 1e-4,
            "failures": [{"task": "T2", "seed": 1, "limb": "transfer",
                          "abs_diff": 0.0002}],
        },
        "protocol": "docs/USE-PATH-DIAGNOSTIC-PREREGISTRATION.md",
        "protocol_sha256": "x", "freeze_commit": "y",
        "campaign_artifact": "docs/formation_utilization.json",
        "engine_version": "0.10.0",
        "generated_utc": "2026-10-30T00:00:00Z",
    }
    out = d.render_results(artifact)
    assert "AUDIT REQUIRED" in out
    assert "MECHANISM CANDIDATE" not in out
    assert "## 1. The room in the use path" not in out


# ---------------------------------------------------------------------------
# D2 — constants-only, and load-bearing
# ---------------------------------------------------------------------------

def test_d2_constants_are_the_declared_constants():
    assert d.D2_CONSTANTS == {"prediction_candidate": 1.0, "__other__": 0.5}
    assert d.d2_weight("prediction_candidate") == 1.0
    assert d.d2_weight("concept_candidate") == 0.5
    assert d.audit_d2_constants()["passed"]


def test_d2_constants_are_load_bearing(monkeypatch):
    by_type = {
        "prediction_candidate": {"a": {"b": 10.0}},
        "concept_candidate": {"a": {"c": 10.0}},
    }
    with_declared = d.aggregate_type_rows(by_type, d.d2_weight)
    assert with_declared["a"]["c"] == 5.0
    monkeypatch.setitem(d.D2_CONSTANTS, "__other__", 0.0)
    without_other = d.aggregate_type_rows(by_type, d.d2_weight)
    assert without_other.get("a", {}).get("c", 0.0) == 0.0


# ---------------------------------------------------------------------------
# Per-type attribution and the controls
# ---------------------------------------------------------------------------

def test_per_type_edges_reconcile_to_structure_edges():
    candidates = [
        {"id": "p1", "type": "prediction_candidate", "source": "a",
         "target": "b", "evidence": {"temporal_count": 3}},
        {"id": "c1", "type": "concept_candidate", "members": ["b", "c"]},
        {"id": "l1", "type": "loop_candidate", "path": ["a", "b", "c"]},
        {"id": "h1", "type": "hypothesis", "subject": "a", "expectation": "c"},
        {"id": "pr1", "type": "process_candidate", "cycle": ["a", "b", "c"]},
        {"id": "w1", "type": "workflow_concept", "components": ["a", "b", "c"]},
        {"id": "d1", "type": "dream", "path_or_context": ["a", "b"]},
    ]
    full = d.aggregate_type_rows(d.per_type_rows(candidates), lambda _t: 1.0)
    expected = fu.structure_edges(candidates)
    assert d._row_difference(full, expected) == 0.0


def test_known_answer_control_passes():
    assert d.audit_known_answer()["passed"]


def test_shuffled_control_passes():
    assert d.audit_shuffled_collapse()["passed"]


def test_denominator_control_fires_on_an_empty_limb():
    record = _record()
    record["limb_counts"]["revision"] = {"events": 0, "cells": 0}
    audit = d.audit_denominators([record])
    assert audit["passed"] is False
    assert audit["failures"][0]["limb"] == "revision"


def test_attribution_control_fires_on_a_mismatch():
    record = _record()
    record["attribution"] = {"ok": False, "max_edge_diff": 1.0}
    audit = d.audit_attribution([record])
    assert audit["passed"] is False
    assert audit["failures"][0]["max_edge_diff"] == 1.0


def test_calibration_control_fires_when_a_scoring_seed_leaks_in():
    calibration = {
        "seed": d.CALIBRATION_SEED,
        "tasks": {t: {"seed": d.CALIBRATION_SEED, "selected_alpha": 256.0}
                  for t in d.TASKS},
    }
    assert d.audit_calibration_isolation(calibration)["passed"]
    calibration["tasks"]["T2"]["seed"] = d.SEEDS[0]
    assert d.audit_calibration_isolation(calibration)["passed"] is False


def test_one_seed_control_fires():
    assert d.audit_one_seed([_record()])["passed"] is False
    assert d.audit_one_seed([_record(), _record(seed=20261102)])["passed"]


# ---------------------------------------------------------------------------
# Result document
# ---------------------------------------------------------------------------

def _cell(mean=0.0, lo=-0.01, hi=0.01, verdict="tie", helps=False):
    return {"mean": mean, "lo": lo, "hi": hi, "n": 30, "reps": 10000,
            "interval": "0.9833", "verdict": verdict, "helps": helps}


def _pass_artifact() -> dict:
    room = {}
    cells = {}
    for task in d.TASKS:
        room[task] = {
            limb: {**_cell(0.001, -0.002, 0.004, "tie"),
                   "d0_mean": 0.4, "d5_mean": 0.401}
            for limb in d.LIMBS
        }
        cells[task] = {
            arm: {limb: _cell() for limb in d.LIMBS}
            for arm in ("D1", "D2", "D3", "D4")
        }
    return {
        "d0_reproduction": {
            "passed": True, "expected_units": 60, "units_present": 60,
            "n_checks": 180, "max_abs_diff": 0.0, "tolerance": 1e-4,
            "failures": [],
        },
        "protocol_complete": True,
        "protocol": "docs/USE-PATH-DIAGNOSTIC-PREREGISTRATION.md",
        "protocol_sha256": "x", "freeze_commit": "y",
        "campaign_artifact": "docs/formation_utilization.json",
        "engine_version": "0.10.0",
        "generated_utc": "2026-10-30T00:00:00Z",
        "constants": {"room_threshold": 0.01, "effect_threshold": 0.01},
        "room": room,
        "cells": cells,
        "mapping": {"outcome": "evidence_limited",
                    "reason": "the room is below the threshold on both tasks",
                    "room_means": {"T2": 0.001, "T1": 0.001},
                    "helping": {t: {a: False for a in ("D1", "D2", "D3", "D4")}
                                for t in d.TASKS}},
        "audits": {name: {"passed": True} for name in
                   ("known_answer", "shuffled", "denominators", "attribution",
                    "calibration", "d2_constants", "one_seed")},
        "control_failures": [],
        "records": [{"task": "T2", "seed": 20261101}],
        "seeds": list(d.SEEDS),
        "tasks": list(d.TASKS),
    }


def test_result_document_is_generated_and_has_no_placeholder():
    out = d.render_results(_pass_artifact())
    assert "PASS" in out
    assert "EVIDENCE-LIMITED" in out
    assert "{" not in out


def test_result_document_marks_a_non_confirmatory_subset():
    artifact = _pass_artifact()
    artifact["protocol_complete"] = False
    assert "NON-CONFIRMATORY SUBSET" in d.render_results(artifact)


def test_placeholder_guard_fires():
    with pytest.raises(ValueError):
        d._assert_no_placeholder("a number {missing} here")

def test_hash_seed_must_be_pinned(monkeypatch):
    monkeypatch.delenv("PYTHONHASHSEED", raising=False)
    with pytest.raises(RuntimeError):
        d.require_hash_seed()
    monkeypatch.setenv("PYTHONHASHSEED", "0")
    assert d.require_hash_seed() == "0"

