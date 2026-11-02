"""Stage B must be a protocol: nothing spent, nothing allocated, nothing computed.

The artifact is checked for the block size, the reliability ladder, the per-world
horizon and the seed pre-assignment; the document is checked against the artifact
for every number it quotes; and both are checked for the two claims this design may
not make -- that onset is validated, and that a relation has been measured.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from benchmarks.stage_b_protocol import CLAIMED, OUT, PUBLISHED_FLOOR, _worlds_for, build

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "STAGE-B-PROTOCOL.md"
CONSTRUCT = ROOT / "docs" / "di_transition_construct.json"
DESIGN = ROOT / "docs" / "STRUCTURE-BEHAVIOR-DESIGN.md"


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
    assert stage["behavioural_endpoint"]["resolution_confirmed"] is False
    assert "No engine ran" in stage["no_engine"]
    assert "**Status: DRAFT PROTOCOL FOR REVIEW. Stage B is not authorised.**" in text
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


def test_agreement_is_reported_as_robustness_and_not_used_as_reliability(stage, text):
    """The correction: 0.972 is an ordering result, not a reliability coefficient."""
    agree = stage["sustention_rule_agreement"]
    assert agree["worst_pair_spearman"] == pytest.approx(0.9721, abs=1e-3)
    assert agree["used_in_the_block_size"] is False
    assert "robust" in agree["establishes"]
    assert "does_not_establish" in agree
    assert "not the reliability of onset" in agree["does_not_establish"]
    assert stage["sample_size"]["reliability_measured"] is False
    assert "not used in the block-size arithmetic" in text
    assert "used_in_the_block_size" in text
    # ... and it is on the reviewer's history as a correction, not a feature.
    history = " ".join(stage["review_gate"]["history_for_the_reviewer"])
    assert "0.972" in history and "correction" in history
    withdrawn = json.dumps(stage["withdrawn_claims"])
    assert "reliability of 0.972" in withdrawn
    assert "withdrawn in place" in withdrawn


def test_the_block_is_solved_from_the_claim_at_a_declared_assumption(stage, text):
    s = stage["sample_size"]
    # the closed form reproduces the project's published floor on this endpoint
    assert _worlds_for(0.50) == PUBLISHED_FLOOR == 48
    assert s["worlds_per_configuration_at_reliability_1"] == 48
    assert s["reliability_planning_assumption"] == 0.50
    assert s["worlds_per_configuration"] == 104
    assert s["worlds_total"] == 104 * len(CLAIMED) == 416
    assert s["reportable_floor_per_configuration"] == 48
    assert s["worlds_per_configuration"] > s["reportable_floor_per_configuration"]
    assert s["worlds_total_if_reviewer_accepts_0_70"] == 288
    # the ladder must be monotone and every row must be quoted in the document
    ladder = s["attenuation_ladder"]
    # Reliability descends down the ladder, so the requirement ascends.
    n = [ladder[k]["worlds_per_configuration"] for k in ladder]
    assert n == sorted(n), n
    for rel, row in ladder.items():
        if rel == "0.50":
            line = ("| **0.50 (planning assumption)** | **%.4f** | **%d** | **%d** |"
                    % (row["observed_effect_spearman"],
                       row["worlds_per_configuration"],
                       row["worlds_per_configuration"] * len(CLAIMED)))
        else:
            line = "| %s | %.4f | %d | %d |" % (
                rel, row["observed_effect_spearman"], row["worlds_per_configuration"],
                row["worlds_per_configuration"] * len(CLAIMED))
        assert line in text, line
    assert "0.70 gives 288" in text


def test_the_seed_block_is_preassigned_spares_named_and_substitution_closed(stage, text):
    seeds = stage["seeds"]
    assert seeds["candidate_block"] == [700000001, 700000420]
    assert seeds["candidate_count"] == 420
    assert seeds["overlap_with_consumed"] == []
    assert seeds["candidate_count"] == seeds["preassigned_total"] + seeds["unused"]["count"]
    assert seeds["preassigned_total"] == stage["sample_size"]["worlds_total"] == 416
    assert sorted(seeds["preassigned"]) == sorted(CLAIMED)
    for lab, chunk in seeds["preassigned"].items():
        assert chunk["count"] == 104, lab
    assert seeds["preassigned"]["2:1"]["first"] == 700000001
    assert seeds["preassigned"]["6:1"]["last"] == 700000416
    assert seeds["unused"] == {"first": 700000417, "last": 700000420, "count": 4}
    assert seeds["substitution_allowed"] is False
    assert seeds["consumed_total"] == 192
    assert seeds["disjoint_proved_against"] == 71
    for path in seeds["consumed_blocks"]:
        assert (ROOT / path).exists(), path
    assert "**192** consumed seeds across **71** artifacts" in text
    assert "**0 overlap**" in text
    assert "**four** seeds" in text and "700000417" in text
    assert "**Substitution is prohibited**" in text


def test_the_horizon_is_per_world_and_matches_the_record(stage, construct, text):
    per = construct["behavioural_clock"]["per_config"]
    for lab, horizon in stage["clock"]["median_horizon_by_config_cycles"].items():
        assert horizon == per[lab]["confirmation_cycle_median"] + 101, lab
    assert stage["clock"]["horizon_is_per_world"] is True
    assert stage["cost"]["cycles_total"] == 215696
    assert stage["cost"]["relative_to_phase_l"] == pytest.approx(1.4979, abs=1e-4)
    worlds = stage["sample_size"]["worlds_per_configuration"]
    for lab, horizon in stage["clock"]["median_horizon_by_config_cycles"].items():
        row = "| `%s` | %.0f | %.0f | %d | %s |" % (
            lab, per[lab]["confirmation_cycle_median"], horizon, worlds,
            format(int(horizon * worlds), ","))
        assert row in text, row
    assert "| **total** | — | — | **416** | **215,696** |" in text


def test_the_endpoint_can_be_inspected_in_code(stage, text):
    endpoint = stage["behavioural_endpoint"]
    assert endpoint["name"] == "revision_held_out"
    assert endpoint["resolution_confirmed"] is False
    impl = " ".join(endpoint["implementation_to_inspect"])
    assert "reusable_knowledge.py" in impl
    assert "formation_provenance_study.py" in impl
    assert "held_out_pairs" in impl
    assert "benchmarks/reusable_knowledge.py" in text
    assert "benchmarks/formation_provenance_study.py" in text
    assert "does not start" in endpoint["resolution_requirement"]


def test_the_aggregation_rule_cannot_pick_a_winner(stage, text):
    rule = stage["analysis"]["aggregation_rule"]
    assert "every claimed configuration" in rule
    assert "mixed" in rule
    assert stage["analysis"]["pooling"].startswith("none")
    assert "**every** claimed configuration" in text
    assert "not supported as stated" in text


def test_the_four_falsifiers_and_the_underpowered_outcome_are_present(stage, text):
    assert [f["id"] for f in stage["falsifiers"]] == ["A", "B", "C", "D"]
    for marker in ("1. **Absence.**", "2. **Reversal.**",
                   "3. **Dead configuration.**", "4. **Pooled only.**"):
        assert marker in text
    assert "underpowered_for_the_claim" in stage["outcomes"]
    assert "**underpowered for the claim**" in text


def test_censored_worlds_are_excluded_and_never_replaced(stage, text):
    assert "not replaced" in stage["sample_size"]["no_replacement"]
    assert "censored" in stage["eligibility"]["worlds_below_denominator_are"]
    assert "**not replaced**" in text
    assert "inconclusive" in text


def test_the_reviewer_gets_the_corrections_too(stage, text):
    gate = stage["review_gate"]
    assert gate["outcome_recorded"] is False
    assert gate["may_reject"] is True
    questions = " ".join(gate["questions_for_the_reviewer"])
    assert "block size" in questions and "reliability" in questions
    assert "spare seeds" in questions or "unused seeds" in questions
    assert len(gate["questions_for_the_reviewer"]) == 5
    assert "**The reviewer is authorised to reject this protocol**" in text
    history = " ".join(gate["history_for_the_reviewer"])
    assert "0.44 pairs" in history
    assert "index-versus-count" in history
    assert "**withdrawal in place**" in text
    # the published design's rounded table is the source of the ladder's mapping
    assert "104" in DESIGN.read_text(encoding="utf-8")


def test_the_endpoint_granularity_is_measured_not_assumed(stage, text):
    """A non-zero count is not a resolution test; the quantum is what decides."""
    res = stage["endpoint_resolution"]
    assert res["confirmed"] is False
    assert res["evidence_kind"].startswith("design-block")
    counts = res["held_out_transitions"]
    assert counts["min"] == 82
    assert counts["median"] == 106
    assert counts["max"] == 110
    assert counts["cells"] == 5
    assert res["quantum_at_median"] == pytest.approx(1 / 106, abs=1e-6)
    assert res["distinguishable_levels_at_median"] == 107
    assert res["effect_gap_at_rho_0_50"] == pytest.approx(0.05, abs=1e-9)
    assert res["quantum_relative_to_effect_gap"] == pytest.approx(5.3, abs=0.05)
    assert res["resolves_the_declared_effect_on_this_evidence"] is True
    assert set(res["rules"]) == {"too_coarse", "too_sparse", "saturated",
                                 "undefined", "screening"}
    # the document carries the same numbers, and the four failure rules
    assert "**82 to 110**, median **106**" in text
    assert "**0.009434**" in text
    assert "**107**" in text
    assert "**5.3**" in text
    for word in ("**too coarse**", "**too sparse**", "**saturated**", "**undefined**"):
        assert word in text, word
    assert "`resolution_confirmed` stays **false**" in text
    # and it stays a gate, not a conclusion
    assert "is** the gate" in text


def test_pre_assigned_allocated_and_reserved_are_distinguished(stage, text):
    """The protocol must not use 'assigned' and 'allocated' as synonyms."""
    glossary = stage["glossary"]
    assert set(glossary) == {"pre-assigned", "allocated", "reserved"}
    assert "No seed is allocated by this document" in glossary["allocated"]
    assert "| **pre-assigned** |" in text
    assert "| **allocated** |" in text
    assert "| **reserved** |" in text
    assert "both be true" in text


def test_the_assumption_is_not_presented_as_an_established_bound(stage, text):
    s = stage["sample_size"]
    assert s["planning_assumption_is_established_lower_bound"] is False
    assert s["block_is_conditional_on_the_assumption"] is True
    assert "**declared planning assumption, not an established lower bound**" in text
    assert "conditional on this assumption" in text
    assert "may reject the assumption without" in text
