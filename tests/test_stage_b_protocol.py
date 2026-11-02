"""Stage B must be a protocol: nothing spent, nothing allocated, nothing computed.

The artifact is checked for the block size, the per-world horizon and the seed
disjointness; the document is checked against the artifact for every number it
quotes; and both are checked for the two claims this design may not make --
that onset is validated, and that a relation has been measured.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from benchmarks.stage_b_protocol import CLAIMED, OUT, PUBLISHED_FLOOR, _worlds_for, build

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "STAGE-B-PROTOCOL.md"
CONSTRUCT = ROOT / "docs" / "di_transition_construct.json"


@pytest.fixture(scope="module")
def stage() -> dict:
    return build()


@pytest.fixture(scope="module")
def text() -> str:
    return DOC.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def construct() -> dict:
    return json.loads(CONSTRUCT.read_text(encoding="utf-8"))


def test_the_stored_artifact_is_current(stage):
    assert json.loads(OUT.read_text(encoding="utf-8")) == stage


def test_nothing_is_authorised_and_nothing_is_spent(stage, text):
    assert stage["status"]["authorised"] is False
    assert stage["status"]["seeds_allocated"] == 0
    assert stage["status"]["worlds_run"] == 0
    assert stage["seeds"]["allocated"] is False
    assert "No engine ran" in stage["no_engine"]
    assert "**Status: DRAFT PROTOCOL FOR REVIEW. Stage B is not authorised.**" in text
    assert "20270601" in text
    assert "candidate block is not an allocation" in text


def test_no_relation_has_been_computed(stage, text):
    """The design's whole discipline: the predictor was fixed before any outcome."""
    assert "no relation between onset and behaviour" in stage["what_this_is"].lower()
    flat = " ".join(text.lower().split())   # the sentence wraps across a line
    assert "no relation between onset and behaviour has been computed" in flat


def test_the_predictor_is_inherited_and_frozen(stage, construct, text):
    assert stage["predictor"]["sustention_rule_cycles"] == 10
    assert stage["predictor"]["sustention_rule_frozen"] is True
    assert stage["predictor"]["sustention_rule_cycles"] == \
        construct["onset_conventions"]["sustained_cycles"]
    assert stage["clock"]["post_confirmation_margin_cycles"] == 1
    assert stage["clock"]["follow_up_cycles"] == 100
    assert stage["claimed_configurations"] == list(CLAIMED)
    assert sorted(stage["claimed_configurations"]) == \
        sorted(construct["stage_b_measurement_criteria"]["per_config"])
    assert "earlier confirmed onset predicts a higher" in stage["predictor"]["direction"]
    assert "earlier confirmed onset predicts a **higher**" in text


def test_the_block_size_is_solved_not_chosen(stage, text):
    s = stage["sample_size"]
    # the closed form reproduces the project's published floor on this endpoint
    assert _worlds_for(0.50) == PUBLISHED_FLOOR == 48
    assert s["worlds_per_configuration_at_reliability_1"] == 48
    # ... and this block's size follows from the measured agreement
    assert s["agreement_worst"] == pytest.approx(0.9721, abs=1e-3)
    assert s["attenuated_effect_at_proxy"] == pytest.approx(0.4757, abs=1e-3)
    assert s["worlds_per_configuration"] == 54
    assert s["worlds_total"] == 54 * len(CLAIMED) == 216
    assert s["reportable_floor_per_configuration"] == 48
    assert s["worlds_per_configuration"] > s["reportable_floor_per_configuration"]
    assert "| onset-agreement proxy | **0.972** |" in text
    assert "| attenuated effect | **0.4757** |" in text
    assert "| worlds per configuration | **54** |" in text
    assert "| worlds total | **216** |" in text


def test_the_seed_block_is_proved_unused(stage, text):
    seeds = stage["seeds"]
    assert seeds["candidate_block"] == [20270601, 20270820]
    assert seeds["candidate_count"] == 220
    assert seeds["overlap_with_consumed"] == []
    assert seeds["candidate_count"] >= stage["sample_size"]["worlds_total"]
    assert seeds["consumed_total"] == 192
    assert seeds["disjoint_proved_against"] == 71
    # every block is named, so the union can be checked rather than trusted
    for path in seeds["consumed_blocks"]:
        assert (ROOT / path).exists(), path
    assert "**192** consumed seeds across **71** artifacts" in text
    assert "**0 overlap**" in text


def test_the_horizon_is_per_world_and_matches_the_record(stage, construct, text):
    per = construct["behavioural_clock"]["per_config"]
    for lab, horizon in stage["clock"]["median_horizon_by_config_cycles"].items():
        assert horizon == per[lab]["confirmation_cycle_median"] + 101, lab
    assert stage["clock"]["horizon_is_per_world"] is True
    assert stage["cost"]["cycles_total"] == 111996
    assert stage["cost"]["relative_to_phase_l"] == pytest.approx(0.7778, abs=1e-4)
    worlds = stage["sample_size"]["worlds_per_configuration"]
    for lab, horizon in stage["clock"]["median_horizon_by_config_cycles"].items():
        row = "| `%s` | %.0f | %.0f | %d | %s |" % (
            lab, per[lab]["confirmation_cycle_median"], horizon, worlds,
            format(int(horizon * worlds), ","))
        assert row in text, row
    assert "| **total** | — | — | **216** | **111,996** |" in text


def test_the_aggregation_rule_cannot_pick_a_winner(stage, text):
    rule = stage["analysis"]["aggregation_rule"]
    assert "every claimed configuration" in rule
    assert "mixed" in rule
    assert stage["analysis"]["pooling"].startswith("none")
    assert "**every** claimed configuration" in text
    assert "not supported as stated" in text


def test_the_four_falsifiers_are_present(stage, text):
    assert [f["id"] for f in stage["falsifiers"]] == ["A", "B", "C", "D"]
    for marker in ("1. **Absence.**", "2. **Reversal.**",
                   "3. **Dead configuration.**", "4. **Pooled only.**"):
        assert marker in text


def test_censored_worlds_are_excluded_and_never_replaced(stage, text):
    assert "not replaced" in stage["sample_size"]["no_replacement"]
    assert "censored" in stage["eligibility"]["worlds_below_denominator_are"]
    assert "**not replaced**" in text
    assert "inconclusive" in text


def test_the_reviewer_gets_the_corrections_too(stage, text):
    gate = stage["review_gate"]
    assert gate["outcome_recorded"] is False
    assert gate["may_reject"] is True
    history = " ".join(gate["history_for_the_reviewer"])
    assert "withdraw" in history
    assert "0.44 pairs" in history
    assert "index-versus-count" in history
    assert "withdrawn in place" in json.dumps(stage["withdrawn_claims"])
    assert "**withdrawal in place**" in text
    for question in ("whether the ten-cycle onset rule",
                     "whether the predictor is genuinely isolated",
                     "whether the configuration-specific eligibility",
                     "whether the confirmation-relative clock",
                     "whether the falsifiers"):
        assert question in text, question
