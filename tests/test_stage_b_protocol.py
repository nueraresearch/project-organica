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
    assert s["worlds_per_configuration"] == 120
    assert s["worlds_total"] == 120 * len(CLAIMED) == 480
    # the block is the ladder row raised by a lower-bound rule, not by preference
    rule = s["block_floor_rule"]
    assert rule["ladder_row_at_planning_assumption"] == 104
    assert rule["chosen"] == 120
    assert rule["clearing_on_the_lower_bound"] == [120]
    assert 112 in rule["tested_sizes"]
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
    assert seeds["candidate_block"] == [700000001, 700000484]
    assert seeds["candidate_count"] == 484
    assert seeds["overlap_with_consumed"] == []
    assert seeds["candidate_count"] == seeds["preassigned_total"] + seeds["unused"]["count"]
    assert seeds["preassigned_total"] == stage["sample_size"]["worlds_total"] == 480
    assert sorted(seeds["preassigned"]) == sorted(CLAIMED)
    for lab, chunk in seeds["preassigned"].items():
        assert chunk["count"] == 120, lab
    assert seeds["preassigned"]["2:1"]["first"] == 700000001
    assert seeds["preassigned"]["6:1"]["last"] == 700000480
    assert seeds["unused"] == {"first": 700000481, "last": 700000484, "count": 4}
    assert seeds["substitution_allowed"] is False
    assert seeds["consumed_total"] == 192
    assert seeds["disjoint_proved_against"] == 71
    for path in seeds["consumed_blocks"]:
        assert (ROOT / path).exists(), path
    assert "**192** consumed seeds across **71** artifacts" in text
    assert "**0 overlap**" in text
    assert "**four** seeds" in text and "700000481" in text
    assert "**Substitution is prohibited**" in text


def test_the_horizon_is_per_world_and_matches_the_record(stage, construct, text):
    per = construct["behavioural_clock"]["per_config"]
    for lab, horizon in stage["clock"]["median_horizon_by_config_cycles"].items():
        assert horizon == per[lab]["confirmation_cycle_median"] + 101, lab
    assert stage["clock"]["horizon_is_per_world"] is True
    assert stage["cost"]["cycles_total"] == 248880
    assert stage["cost"]["relative_to_phase_l"] == pytest.approx(1.7283, abs=1e-4)
    worlds = stage["sample_size"]["worlds_per_configuration"]
    for lab, horizon in stage["clock"]["median_horizon_by_config_cycles"].items():
        row = "| `%s` | %.0f | %.0f | %d | %s |" % (
            lab, per[lab]["confirmation_cycle_median"], horizon, worlds,
            format(int(horizon * worlds), ","))
        assert row in text, row
    assert "| **total** | — | — | **480** | **248,880** |" in text


def test_the_endpoint_can_be_inspected_in_code(stage, text):
    endpoint = stage["behavioural_endpoint"]
    assert endpoint["name"] == "revision_held_out"
    assert endpoint["resolution_confirmed"] is False
    impl = " ".join(endpoint["implementation_to_inspect"])
    assert "reusable_knowledge.py" in impl
    assert "WITHHELD" in impl
    # rubric 3: the old pointer named a selector that does not produce this score
    assert "NOT this endpoint's withholding rule" in impl
    assert "benchmarks/reusable_knowledge.py" in text
    requirement = endpoint["resolution_requirement"]
    assert "does not start" in requirement
    # second pass, finding 1: the generator must stop restating a quantum it withdrew
    assert "no one-over-count quantum" in requirement
    assert "quantum (one held-out transition)" not in requirement
    assert "proportion" not in requirement
    assert "measured by resampling those withheld transitions" in requirement


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


def test_the_granularity_gate_is_not_passed_on_a_transition_count(stage, text):
    """Second pass, finding 3: the count is a denominator, not a precision."""
    res = stage["endpoint_resolution"]
    assert res["confirmed"] is False
    assert res["status"].startswith("open")
    assert "not a count of independent contributions" in (
        res["endpoint_scale"]["what_the_count_buys"])
    assert "MEASURED" in res["rules"]["too_coarse"]
    assert "s/sqrt(N) over its scored cells" not in res["rules"]["too_coarse"]
    assert "cluster bootstrap" in stage["analysis"]["endpoint_precision_required"]
    assert "measured precision" in stage["outcomes"]["design_defect"]
    assert len(res["effect_gap_is_conditional_on"]) == 3
    assert "2 x rho x sd" in res["effect_gap_is_conditional_on"][0]
    assert res["effect_gap_at_rho_0_50"] == round(
        2.0 * stage["sample_size"]["smallest_effect_spearman"]
        * res["assumed_outcome_sd"], 6)
    probe = res["design_block_precision_probe"]
    assert probe["measured"] is True
    assert probe["artifact"] == "docs/stage_b_endpoint_precision.json"
    assert "bracket straddles the gap" in probe["what_it_does_not_show"]
    for marker in ("not a count of independent contributions",
                   "substitution is **withdrawn**",
                   "**undetermined**, not passed"):
        assert marker in text, marker


def test_the_simulation_does_not_claim_a_size_it_cannot_separate():
    """Second pass, finding 2: MC error spans the bar, and the artifact says so."""
    doc = json.loads((ROOT / "docs" / "stage_b_resolution_simulation.json")
                     .read_text(encoding="utf-8"))
    joined = " ".join(doc["limits"])
    assert "slightly conservative" not in joined
    assert "NOT measured here" in joined
    assert "does not establish which side" in doc["what_the_monte_carlo_allows"]
    for row in doc["size_sensitivity_at_planning_effect"].values():
        assert row["monte_carlo_se"] > 0


def test_the_endpoint_scale_is_the_scorer_not_a_proportion(stage, text):
    """The pre-pass found the quantum computed for an endpoint this protocol lacks.

    `documents/AI-REVIEW-2026-11-02.md` rubric 1: the score is an averaged pairwise
    log loss, so `1/count` is not its quantum. The figures are withdrawn, the scale is
    named, and the rules are restated on quantities that can actually be measured.
    """
    res = stage["endpoint_resolution"]
    assert res["confirmed"] is False
    assert res["evidence_kind"].startswith("design-block")
    scale = res["endpoint_scale"]
    assert scale["is_a_proportion"] is False
    assert "log loss" in scale["unit"]
    assert "acquisition_compositional" in scale["where_defined"]
    assert "withdrawn" in scale["one_over_count_quantum"]
    for gone in ("quantum_at_median", "distinguishable_levels_at_median",
                 "quantum_relative_to_effect_gap",
                 "resolves_the_declared_effect_on_this_evidence"):
        assert gone not in res, gone
    counts = res["held_out_transitions"]
    assert (counts["cells"], counts["min"], counts["median"], counts["max"]) \
        == (5, 82, 106, 110)
    assert res["effect_gap_at_rho_0_50"] == pytest.approx(0.05, abs=1e-9)
    assert set(res["rules"]) == {"too_coarse", "too_sparse", "saturated",
                                 "undefined", "screening"}
    flat = " ".join(text.split())
    assert "not a proportion" in flat
    assert "withdrawn" in flat
    assert "**82 to 110**, median **106**" in flat
    assert "twice a world's standard error" in flat
    for word in ("**too coarse**", "**too sparse**", "**saturated**", "**undefined**"):
        assert word in flat, word
    assert "`resolution_confirmed` stays **false**" in flat
    # and it stays a gate, not a conclusion
    assert "is** the gate" in flat


def test_the_ladder_is_checked_with_the_committed_interval(text):
    """The ladder is Fisher-z; the analysis is a percentile bootstrap (rubric 4).

    The document's simulated column must equal the artifact's, and the planning row
    must be reported with its own Monte-Carlo error rather than settled by it.
    """
    sim = json.loads((ROOT / "docs" / "stage_b_resolution_simulation.json")
                     .read_text(encoding="utf-8"))
    row = sim["points"]["0.50"]
    assert row["worlds_per_configuration"] == 104
    assert row["fisher_z_says"] == pytest.approx(0.9026, abs=1e-4)
    assert row["clears_bar"] is False
    flat = " ".join(text.split())
    # the document must quote the artifact's own rounded values, not nearby ones
    quoted = f"**{row['resolved_share']:.3f} ± {row['monte_carlo_se']:.3f}**"
    assert quoted in flat, quoted
    sizes = sim["size_sensitivity_at_planning_effect"]
    assert sizes["112"]["clears_bar"] is True
    assert sizes["120"]["clears_bar"] is True
    for n in ("112", "120"):
        cell = (f"{sizes[n]['resolved_share']:.3f} "
                f"(SE {sizes[n]['monte_carlo_se']:.3f})")
        assert cell in flat, cell
    # second pass, finding 2: the point estimate is NOT separable from the bar, so
    # the sentence claiming it does not clear the bar had to go too
    assert "does not clear the 90 % bar at the point estimate" not in flat
    assert "**0.7 SE below**" in flat and "3.6 SE**" in flat
    # the block-size question is now decided by a rule, not left open
    assert "The block is 120, and the rule that chose it was fixed" in flat
    assert "recorded here as **open**" not in flat


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
