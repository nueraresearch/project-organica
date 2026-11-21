"""The K1 implementability review is checked against the artifacts it quotes.

The review's table is generated from `docs/phase_k_results_0.15.0.json` and
`docs/phase_k_results.json`; these tests hold it to them, prove the checker can
fail, and hold the registration to the pointer it now carries.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from benchmarks import k1_implementability as review

# Reads committed artifacts and one page; runs no engine and no harness path.
LAYER = "static"

ROOT = Path(__file__).resolve().parents[1]
REGISTRATION = ROOT / "docs" / "constraint_registrations" / "K1-served-path.json"


def test_the_review_panel_is_the_table_the_artifacts_produce():
    payload = review.panel()
    text = review.DOC.read_text(encoding="utf-8")
    assert review.problems(text, payload) == []
    assert review.PANEL_BEGIN in text and review.PANEL_END in text


def test_every_claim_the_page_makes_holds_on_its_artifact():
    payload = review.panel()
    assert payload["claims"], "the review states no checkable claim"
    assert all(check["holds"] for check in payload["claims"].values())
    # The two findings the review turns on, stated directly.
    shipped = payload["builds"]["0.15.0"]
    archival = payload["builds"]["0.9.0"]
    assert shipped["recall_min"] == 1.0 and shipped["recall_full"] == shipped["seeds"]
    assert archival["late_zero_seeds"] and archival["recall_max"] < 1.0


def test_the_checker_rejects_a_tampered_panel_and_a_non_full_recall():
    assert review.self_test() == []


def test_the_panel_is_not_vacuous_when_an_artifact_is_missing(tmp_path):
    with pytest.raises((OSError, ValueError)):
        review.k1_rows({"per_model_detail": []})


def test_the_superseded_result_carries_the_artifacts_numbers():
    """The retirement record quotes the panel, so every figure must match it."""
    payload = review.panel()
    shipped = payload["builds"]["0.15.0"]
    archival = payload["builds"]["0.9.0"]
    record = json.loads((ROOT / "docs" / "constraint_results"
                         / "K1-SUPERSEDED.json").read_text(encoding="utf-8"))
    evidence = record["evidence"]
    gold = review.GOLD_PAIRS
    assert record["cells_started"] == 0
    assert record["criteria_read"] is False
    assert evidence["seeds"] == shipped["seeds"]
    assert evidence["recall_full_seeds"] == shipped["recall_full"]
    assert evidence["recall_min"] == shipped["recall_min"] == 1.0
    assert evidence["recall_max"] == shipped["recall_max"]
    assert evidence["true_positives"] == gold
    assert evidence["false_negatives"] == gold - gold * shipped["recall_min"]
    assert evidence["precision_min"] == shipped["precision_min"]
    assert evidence["precision_max"] == shipped["precision_max"]
    assert evidence["late_group_f1_min"] == shipped["late_min"]
    assert evidence["late_group_f1_max"] == shipped["late_max"]
    assert evidence["archival_late_group_f1"] == archival["late_min"]
    assert evidence["archival_late_group_f1"] == archival["late_max"]
    assert evidence["archival_recall_max"] == archival["recall_max"]
    assert evidence["false_positives_min"] == shipped["emitted_min"] - gold
    assert evidence["false_positives_max"] == shipped["emitted_max"] - gold
    assert evidence["pass_f1_required"] == round(
        -0.623961 + 0.10 + shipped["baseline_mean"], 6)


def test_the_registration_points_at_the_review_without_changing_a_term():
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    pointer = registration["feasibility_review"]
    assert "docs/K1-IMPLEMENTABILITY-REVIEW.md" in pointer
    assert "re-scoped" in pointer
    # The pointer adds no allocation and moves no threshold.
    assert registration["does_not_allocate"]
    assert registration["threshold_values"]["baseline_gap"] == -0.623961
