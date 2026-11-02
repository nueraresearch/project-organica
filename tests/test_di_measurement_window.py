"""Stage A of the measurement-window design must agree with the records.

The document makes three kinds of claim that a test can hold: numbers taken from
the artifact, a refusal (no cycle number, no reliability coefficient), and a
scope limit (Stage B specified but not authorised). All three are checked here.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from benchmarks.di_window_design import OUT, build

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "DI-MEASUREMENT-WINDOW.md"
DESIGN = ROOT / "docs" / "STRUCTURE-BEHAVIOR-DESIGN.md"


@pytest.fixture(scope="module")
def stage_a() -> dict:
    return build()


@pytest.fixture(scope="module")
def text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_the_stored_artifact_is_current(stage_a):
    assert json.loads(OUT.read_text(encoding="utf-8")) == stage_a


def test_it_reads_the_records_it_claims(stage_a):
    assert stage_a["source"]["records"] == 240
    assert stage_a["units"]["late_pairs_per_record"] == 18
    assert stage_a["exploratory"] is True
    assert "Stage B" in stage_a["selection_risk"]


def test_the_dead_arms_are_counted_not_scored(stage_a):
    emergence = stage_a["emergence"]
    for arm in ("1:1", "1:2", "1:3", "1:4"):
        assert emergence[arm]["runs_ever_nonzero"] == 1, arm
        assert emergence[arm]["runs_never_sustained"] == 30, arm
        assert emergence[arm]["median_sustained_nonzero"] is None, arm
    assert stage_a["schedule"]["runs_identically_zero"] == 117
    for arm in ("2:1", "3:1", "4:1", "6:1"):
        assert emergence[arm]["median_sustained_nonzero"] is not None, arm


def test_the_transition_is_still_running_at_the_end(stage_a):
    """The record must not be described as containing an asymptote."""
    assert stage_a["schedule"]["median_settle_cycle_moving_runs"] == 586
    assert stage_a["schedule"]["max_settle_cycle_moving_runs"] == 599
    for arm in ("2:1", "3:1", "4:1", "6:1"):
        moving = stage_a["settling"][arm]["runs_moving_in_last_50_cycles"]
        assert 25 <= moving <= 27, (arm, moving)


def test_the_schedule_arithmetic(stage_a):
    schedule = stage_a["schedule"]
    assert schedule["protocol_run_length"] == 150
    assert schedule["learning_cycles"] == 50
    assert schedule["test_cycles"] == 50
    assert schedule["run_length_needed_for_settled_measurement_then_learning_then_test"] == pytest.approx(
        schedule["median_settle_cycle_moving_runs"] + 100)


def test_the_predictor_barely_varies_inside_a_configuration(stage_a):
    by_cycles = {tuple(c["cycles"]): c for c in stage_a["candidate_windows"]}
    settled = by_cycles[(560, 600)]
    assert settled["within_config_sd_pairs_median"] == pytest.approx(0.4409, abs=5e-4)
    assert settled["within_config_share_of_variance"] == pytest.approx(0.0200, abs=5e-5)
    assert settled["arms_with_single_value"] == ["1:1", "1:2", "1:3", "1:4"]
    # Never more than about two pairs anywhere in the record.
    assert max(c["within_config_sd_pairs_max"] for c in stage_a["candidate_windows"]) < 3.0


def test_the_document_quotes_the_artifact(text, stage_a):
    schedule = stage_a["schedule"]
    by_cycles = {tuple(c["cycles"]): c for c in stage_a["candidate_windows"]}
    settled = by_cycles[(560, 600)]

    assert f"**{schedule['runs_identically_zero']} of the\n240 runs never leave zero at all**" in text
    assert str(schedule["median_settle_cycle_moving_runs"]) in text
    assert str(schedule["run_length_needed_for_settled_measurement_then_learning_then_test"]) in text
    assert f"{schedule['run_length_needed_for_settled_measurement_then_learning_then_test'] / 150:.1f}×" in text
    assert f"{settled['within_config_sd_pairs_median']:.2f} pairs" in text
    assert f"{settled['within_config_sd_pairs_max']:.2f}" in text
    assert "at least 97 %" in text.lower() or "At least 97 %" in text
    for arm, row in stage_a["settling"].items():
        if row["runs_that_ever_move"] > 5:
            assert str(row["median_settle_cycle"]).replace(".0", "") in text


def test_the_document_refuses_a_cycle_number_and_a_coefficient(text):
    assert "no window adopted" in text
    assert "It refuses to propose a cycle number." in text
    assert "no reliability coefficient" in text
    assert "not authorised here" in text


def test_the_document_answers_the_five_questions(text):
    for q in (
        "When does meaningful `DI` emergence begin?",
        "When does the transition reach an informative state?",
        "Is there a defensible interval across all configurations?",
        "Is the snapshot sufficiently informative there?",
        "Does the behavioural endpoint occur after the measurement?",
    ):
        assert q in text


def test_the_design_record_points_at_the_stage_a_result():
    design = DESIGN.read_text(encoding="utf-8")
    assert "docs/DI-MEASUREMENT-WINDOW.md" in design
