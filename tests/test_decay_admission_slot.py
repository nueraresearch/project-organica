"""Controls for the admission-versus-slot instrument and its pre-registration guard."""

from __future__ import annotations

import json

from benchmarks.decay_admission_slot import classify_miss, label_for
from benchmarks.decay_admission_slot_prereg import (
    ARTIFACT,
    BUCKETS,
    PREREG,
    REGISTRY,
    SEEDS,
    protocol_digest,
    state_errors,
    validate,
)


def _pooled(admission: int, slot: int) -> dict[str, int]:
    return {"below_admission": admission, "slot_loss": slot}


def test_a_miss_below_the_floor_is_an_admission_loss():
    assert classify_miss(("a", "b"), admitted=set(), emitted=set(), count=3) == "below_admission"


def test_an_admitted_miss_is_a_slot_loss_even_when_its_count_is_low():
    assert classify_miss(("a", "b"), admitted={("a", "b")}, emitted=set(), count=3) == "slot_loss"


def test_a_reemitted_edge_is_not_a_miss():
    assert classify_miss(("a", "b"), admitted={("a", "b")}, emitted={("a", "b")}, count=9) == "reemitted"


def test_an_edge_above_the_floor_that_was_never_built_is_unexplained():
    assert classify_miss(("a", "b"), admitted=set(), emitted=set(), count=9) == "unexplained"


def test_a_void_outranks_every_bucket():
    assert label_for(_pooled(90, 10), 8, 0, 40, gates_ok=False) == "VOID_INSTRUMENT"


def test_a_slot_that_never_binds_is_named_not_scored():
    assert label_for(_pooled(90, 10), 8, 0, 0, gates_ok=True) == "SLOT_NEVER_BOUND"


def test_admission_dominance_needs_both_the_share_and_the_seed_majority():
    assert label_for(_pooled(70, 30), 7, 1, 12, gates_ok=True) == "ADMISSION_DOMINANT"


def test_a_high_share_without_the_seed_majority_is_mixed():
    assert label_for(_pooled(70, 30), 5, 3, 12, gates_ok=True) == "MIXED"


def test_slot_dominance_needs_both_the_share_and_the_seed_majority():
    assert label_for(_pooled(20, 80), 1, 7, 12, gates_ok=True) == "SLOT_DOMINANT"


def test_the_digest_covers_the_protocol_and_not_the_outcome():
    text = PREREG.read_text(encoding="utf-8")
    frozen = protocol_digest(text)
    assert protocol_digest(text.replace("## 10. Outcome", "## 10. Outcome\n\nEdited.")) == frozen
    assert protocol_digest(text.replace("## 2. The instrument", "## 2. The instrument!")) != frozen


def test_the_guard_rejects_a_protocol_that_claims_an_execution_without_an_artifact():
    errors = state_errors({"executions": "1"}, None, "## 10. Outcome\n\nNot yet written.")
    assert any("records an execution" in error for error in errors)


def test_the_guard_rejects_an_artifact_under_an_unexecuted_protocol():
    errors = state_errors({"executions": "0"}, {"protocol_digest": "x", "label": "MIXED", "seeds": list(SEEDS)}, "MIXED")
    assert any("0 executions" in error for error in errors)


def test_the_guard_rejects_a_label_outside_the_pre_registered_buckets():
    errors = state_errors(
        {"executions": "1"},
        {"protocol_digest": "x", "label": "PROBABLY_SLOT", "seeds": list(SEEDS)},
        "PROBABLY_SLOT",
    )
    assert any("pre-registered buckets" in error for error in errors)


def test_the_committed_protocol_matches_its_own_state():
    text = PREREG.read_text(encoding="utf-8")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8")) if ARTIFACT.exists() else None
    assert validate(text, registry, artifact, set()) == []
    if artifact is not None:
        assert artifact["label"] in BUCKETS
        assert set(artifact["seeds"]) == set(SEEDS)
