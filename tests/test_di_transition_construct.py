"""The transition construct must be chosen on measurement grounds, not on outcomes.

The artifact is checked for the three candidate summaries' properties and for the
three settling criteria the owner separated; the document is checked against the
artifact; and both documents are checked for the retirement of the word
"asymptote" and for the correction of the Stage A floor comparison.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from benchmarks.di_transition_construct import OUT, build

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "DI-TRANSITION-CONSTRUCT.md"
WINDOW = ROOT / "docs" / "DI-MEASUREMENT-WINDOW.md"


@pytest.fixture(scope="module")
def stage() -> dict:
    return build()


@pytest.fixture(scope="module")
def text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_the_stored_artifact_is_current(stage):
    assert json.loads(OUT.read_text(encoding="utf-8")) == stage


def test_no_behavioural_endpoint_was_read(stage):
    assert "No correlation between any summary" in stage["no_behaviour_read"]
    assert stage["exploratory"] is True


def test_the_three_candidates_are_characterised(stage):
    cand = stage["candidates"]
    assert cand["onset"]["censored_records"] == 121
    assert cand["onset"]["defined_for_every_record"] is False
    assert cand["exposure"]["defined_for_every_record"] is True
    assert cand["exposure"]["censored_records"] == 0
    assert cand["slope"]["censored_records"] == 156
    assert cand["slope"]["defined_for_every_record"] is False


def test_slope_reverses_under_truncation(stage):
    """The evidence that disqualifies slope, not a preference."""
    tr = stage["truncation"]
    assert tr["slope_rank_stability_450"] < 0
    assert tr["exposure_rank_stability_450"] > 0.9
    assert tr["onset_rank_stability_450"] == pytest.approx(1.0)
    assert tr["onset_defined_at_450"] == 88
    assert tr["onset_defined_full"] == 119


def test_onset_outruns_its_own_resolution(stage):
    six = stage["per_config"]["6:1"]["onset_cycles"]
    assert six["median"] == 329
    assert six["sd"] > 10          # twelve cycles on a one-cycle grid
    assert six["max"] - six["min"] == 65


def test_the_dead_configurations_have_no_onset(stage):
    for lab in ("1:1", "1:2", "1:3", "1:4"):
        assert stage["per_config"][lab]["censored_onset"] == 30, lab
        assert stage["per_config"][lab]["onset_cycles"]["n"] == 0, lab


def test_the_three_settling_criteria_are_separated(stage):
    s = stage["settling_criteria"]
    assert s["population"] == 119
    assert s["entry_median_cycle"] == 587
    assert s["entry_max_cycle"] == 599
    assert s["persistence_median_cycles"] == 13
    assert s["persistence_at_least"] == {"30": 37, "50": 17, "100": 4}
    trend = s["remaining_trend_pairs_last_100"]
    assert trend["zero_trend"] == 23
    assert trend["at_least_one_pair"] == 96
    assert trend["at_least_two_pairs"] == 96
    assert trend["zero_trend"] + trend["at_least_one_pair"] == s["population"]
    assert s["satisfy_persistence_50_and_zero_trend"] == 4


def test_the_document_quotes_the_artifact(text, stage):
    per = stage["per_config"]
    for lab in ("2:1", "3:1", "4:1", "6:1"):
        o = per[lab]["onset_cycles"]
        e = per[lab]["exposure_pairs"]
        row = ("| `%s` | %d | %.0f | %.1f | %.0f–%.0f | %.2f ± %.2f |"
               % (lab, per[lab]["records"] - per[lab]["censored_onset"],
                  o["median"], o["sd"], o["min"], o["max"], e["median"], e["sd"]))
        assert row in text, row
    assert "| `1:1`–`1:4` | 0 | — | — | — | 0.00 ± 0.00 |" in text

    share = stage["variance_share_within_config"]
    assert "%.1f %%" % (share["onset"] * 100) in text
    assert "%.1f %%" % (share["exposure_pairs"] * 100) in text
    assert "%.1f %%" % (share["slope_pairs_per_100_cycles"] * 100) in text

    tr = stage["truncation"]
    assert "%.3f" % tr["exposure_rank_stability_450"] in text
    assert "%.3f" % tr["slope_rank_stability_450"] in text
    assert "%.3f" % stage["overlap"]["onset_vs_exposure_pairs_movers"] in text

    s = stage["settling_criteria"]
    assert str(s["entry_median_cycle"]) in text
    assert str(s["persistence_median_cycles"]) in text
    assert "%.1f pairs" % s["remaining_trend_pairs_last_100"]["median"] in text
    assert "%.1f" % s["remaining_trend_pairs_last_100"]["min"] in text
    assert "%.1f" % s["remaining_trend_pairs_last_100"]["max"] in text


def test_the_population_difference_between_the_two_documents_is_disclosed(text):
    """586 (all runs that move) and 587 (sustained onset) are not two facts."""
    window = WINDOW.read_text(encoding="utf-8")
    assert "586" in window and "587" in window
    assert "123 runs" in text and "119 runs" in text


def test_the_document_names_one_primary_and_labels_the_rest(text):
    assert "**Primary: onset.**" in text
    assert "retained as exploratory" in text
    assert "currently unusable" in text
    assert "out of scope for this construct" in text


def test_the_document_states_the_falsifiers(text):
    for marker in ("1. **Absence.**", "2. **Reversal.**",
                   "3. **Dead configuration.**", "4. **Pooled only.**"):
        assert marker in text


def test_the_word_asymptote_is_retired_not_used(text):
    assert "The word **asymptote** is retired" in text
    assert "no demonstrated asymptote" in text.lower() or "no asymptote is claimed" in text.lower()
    window = WINDOW.read_text(encoding="utf-8")
    # The retirement itself may name the word; a claim may not.
    assert "contain the asymptote" not in window
    assert "The asymptote is reached" not in window
    assert "the asymptote is configuration-dominated" not in window


def test_the_stage_a_floor_claim_is_corrected_in_place(text):
    window = WINDOW.read_text(encoding="utf-8")
    assert "**Correction (2026-11-02).**" in window
    assert "withdrawn" in window
    assert "1/(18 × 40)" in window


def test_stage_b_is_still_not_authorised(text):
    assert "not authorised here" in text
    assert "no seed is allocated" in text


def test_the_onset_convention_is_the_one_the_code_applies(stage, text):
    """Anchor, confirmation, interruptions, missing readings and the end boundary."""
    conv = stage["onset_conventions"]
    assert conv["sustained_cycles"] == 10
    assert "first cycle of the qualifying run" in conv["anchor"]
    assert "never the first non-zero reading" in conv["anchor"]
    assert "confirmed only once" in conv["confirmation"]
    assert conv["assigned_retrospectively"] is True
    assert "resumes at the cycle after the zero" in conv["interruption_before_confirmation"]
    assert "does not move a confirmed onset" in conv["interruption_after_confirmation"]
    assert "breaks the run" in conv["missing_reading"]
    assert "never an onset at the boundary" in conv["end_boundary"]

    c = stage["onset_convention_counts"]
    assert c["records"] == 240
    assert c["trajectory_lengths"] == [600]
    assert c["records_with_missing_readings"] == 0
    assert c["records_where_anchor_is_first_nonzero"] == 99
    assert c["records_where_anchor_follows_first_nonzero"] == 20
    assert c["max_anchor_lag_cycles"] == 279
    assert c["latest_confirmation_cycle"] == 598
    assert c["interrupted_attempts_total"] == 2353
    assert c["records_with_an_interrupted_attempt"] == 24
    assert c["censored_end_of_record"] == 0
    assert c["censored_interrupted"] == 4
    assert c["censored_no_nonzero_reading"] == 117
    # Every record is accounted for: onsets, interrupted short runs, no reading at all.
    assert (c["records_where_anchor_is_first_nonzero"]
            + c["records_where_anchor_follows_first_nonzero"]
            + c["censored_interrupted"]
            + c["censored_no_nonzero_reading"]) == c["records"]

    assert "first cycle of the qualifying sustained run" in text
    assert ("**%d are later**, one by as much as %d cycles"
            % (c["records_where_anchor_follows_first_nonzero"],
               c["max_anchor_lag_cycles"])) in text
    assert "latest confirmation cycle **%d**" % c["latest_confirmation_cycle"] in text
    assert ("**%d** such attempts across %d records"
            % (c["interrupted_attempts_total"],
               c["records_with_an_interrupted_attempt"])) in text


def test_the_sustention_rule_is_swept_and_the_document_quotes_it(stage, text):
    sw = stage["sustention_sensitivity"]
    assert set(sw) == {"5", "10", "20"}
    assert sw["10"]["records_whose_onset_moves"] == 0
    for k in ("5", "20"):
        r = sw[k]
        row = ("| %s | %d | %s | %.1f | %s | %d |"
               % (k, r["defined"], r["median"], r["sd"],
                  r["max_abs_shift_cycles_vs_10"], r["records_whose_onset_moves"]))
        assert row in text, row
    b = sw["10"]
    assert ("| **10 (declared)** | **%d** | **%s** | **%.1f** | — | — |"
            % (b["defined"], b["median"], b["sd"])) in text


def test_eligibility_is_reported_for_every_configuration_without_drops(stage, text):
    el = stage["eligibility"]
    assert sorted(el) == ["1:1", "1:2", "1:3", "1:4", "2:1", "3:1", "4:1", "6:1"]
    for lab, e in el.items():
        assert e["excluded_from_construct"] is not e["eligible"], lab
        assert e["eligible"] is (e["runs_with_sustained_onset"] / e["records"]
                                >= stage["stage_b_measurement_criteria"]["min_defined_share"]), lab
        row = ("| `%s` | %d | %d | %d | %.3f | %s | %s |"
               % (lab, e["records"], e["runs_that_ever_move"],
                  e["runs_with_sustained_onset"], e["defined_share"],
                  "without sustained emergence" if e["excluded_from_construct"]
                  else "with sustained emergence",
                  "no" if e["excluded_from_construct"] else "yes"))
        assert row in text, row

    acc = stage["accounting"]
    assert acc["records_total"] == 240
    assert acc["records_in_eligible_configurations"] == 120
    assert acc["records_in_ineligible_configurations"] == 120
    assert acc["records_dropped"] == 0
    assert (acc["records_in_eligible_configurations"]
            + acc["records_in_ineligible_configurations"]) == acc["records_total"]
    flat = " ".join(text.split())   # the sentence wraps across a line in the document
    assert ("240 records — %d in the four configurations with sustained emergence, "
            "%d in the four without, %d dropped"
            % (acc["records_in_eligible_configurations"],
               acc["records_in_ineligible_configurations"],
               acc["records_dropped"])) in flat


def test_the_claim_is_scoped_to_configurations_that_emerge(text):
    assert ("evaluated among configurations in which sustained structure "
            "emerges") in text
    assert "not a claim across configurations" in text


def test_resolution_is_evaluated_per_configuration_with_the_distribution(stage, text):
    blk = stage["stage_b_measurement_criteria"]
    assert blk["evaluated_per_configuration"] is True
    assert sorted(blk["per_config"]) == ["2:1", "3:1", "4:1", "6:1"]
    for lab, c in blk["per_config"].items():
        assert c["pass"] is True, lab
        assert c["defined_share_pass"] is True, lab
        assert c["sd_pass"] is True, lab
        assert c["sd_cycles"] >= c["sd_threshold_cycles"], lab
        assert c["range_cycles"][0] < c["range_cycles"][1], lab
        assert c["iqr_cycles"] > 0, lab
        dist = stage["onset_distribution"][lab]
        row = ("| `%s` | %.3f | %.0f | %.1f | %.2f | %.0f–%.0f | %d | %.2f |"
               % (lab, c["defined_share"], dist["median"], dist["sd"], dist["iqr"],
                  dist["min"], dist["max"], dist["distinct"],
                  dist["share_within_sd_threshold_of_median"]))
        assert row in text, row
    assert blk["all_pass"] is True
    # The pass is not vacuous: the closest approach is still four times the floor.
    assert min(c["sd_cycles"] for c in blk["per_config"].values()) > 4 * 3.0
    assert min(c["defined_share"] for c in blk["per_config"].values()) > 0.96
    # ... and the distributions are broad, so no clump is hiding behind the SD.
    for dist in stage["onset_distribution"].values():
        if dist["n"]:
            assert dist["share_within_sd_threshold_of_median"] < 0.3


def test_the_sweep_is_checked_on_the_ordering_not_the_median(stage, text):
    """A stable median says nothing about whether a world keeps its rank."""
    t = stage["threshold_rank_sensitivity"]
    assert t["rules_swept"] == [5, 10, 20]
    assert t["declared_rule"] == 10
    # No configuration reaches a different verdict under a different rule.
    assert t["configurations_whose_conclusions_change"] == []
    assert t["records_whose_eligibility_changes_by_rule"] == {
        "5_vs_10": 0, "10_vs_20": 2, "5_vs_20": 2}

    pass_marks = {k: ("yes" if c["pass"] else "no")
                  for k, c in t["per_config"]["6:1"]["criteria_under_each_rule"].items()}
    for lab in ("6:1", "4:1", "3:1", "2:1"):
        r = t["per_config"][lab]
        assert r["conclusions_change"] is False, lab
        for pair in ("5_vs_10", "10_vs_20", "5_vs_20"):
            c = r["comparisons"][pair]
            assert c["spearman"] > 0.96, (lab, pair)
            # an inversion per twenty orderings is the most any configuration shows
            assert c["pairwise_rank_inversions"] * 20 < c["comparable_pairs"], (lab, pair)

        marks = {k: ("yes" if c["pass"] else "no")
                 for k, c in r["criteria_under_each_rule"].items()}
        row = ("| `%s` | %.3f | %.3f | %.3f | %s | %s | %s |"
               % (lab, r["comparisons"]["5_vs_10"]["spearman"],
                  r["comparisons"]["10_vs_20"]["spearman"],
                  r["comparisons"]["5_vs_20"]["spearman"],
                  marks["5"], marks["10"], marks["20"]))
        assert row in text, row

        changes = max(r["comparisons"][p]["records_whose_eligibility_changes"]
                      for p in ("5_vs_10", "10_vs_20"))
        shift = max(r["comparisons"][p]["max_rank_shift"] for p in r["comparisons"])
        row = ("| `%s` | %.3f | %.3f | %.3f | %d | %d |"
               % (lab,
                  r["comparisons"]["5_vs_10"]["inversion_share_of_comparable_pairs"],
                  r["comparisons"]["10_vs_20"]["inversion_share_of_comparable_pairs"],
                  r["comparisons"]["5_vs_20"]["inversion_share_of_comparable_pairs"],
                  shift, changes))
        assert row in text, row

    # The marginal case is named, not averaged away: at 20 cycles the slow
    # configuration sits exactly on the 90% share criterion.
    assert t["per_config"]["2:1"]["criteria_under_each_rule"]["20"]["defined_share"] == 0.9
    assert "0.900", "the document must name the marginal share" not in ()
    assert "**0.900**" in text
    assert "0.900" in text and "marginal" in text
    assert pass_marks == {"5": "yes", "10": "yes", "20": "yes"}


def test_the_behavioural_clock_is_fixed_and_disjoint_from_onset(stage, text):
    """Equal opportunity, unequal developmental age, and both clocks reported."""
    b = stage["behavioural_clock"]
    assert b["post_confirmation_margin_cycles"] == 1
    assert (b["learn_cycles"], b["test_cycles"], b["follow_up_cycles"]) == (50, 50, 100)
    assert b["first_behavioural_cycle"] == "confirmation_cycle + 1"
    assert b["last_behavioural_cycle"] == "confirmation_cycle + 100"
    assert b["follow_up_length_is_identical_in_every_world"] is True
    assert b["first_behavioural_cycle_differs_by_world"] is True
    assert b["exposure_interval_must_end_before_first_behavioural_cycle"] is True
    assert b["reporting_required_per_observation"] == [
        "absolute cycle", "cycles since confirmation"]

    # No behavioural cycle can feed the predictor.
    assert b["behavioural_cycles_at_or_before_confirmation"] == 0
    assert b["runs_with_a_clock"] == 119

    assert b["absolute_start_min"] == 299
    assert b["absolute_start_max"] == 599
    assert b["absolute_start_span_cycles"] == 300
    assert b["run_length_needed_cycles"] == 699
    assert b["runs_that_fit_a_600_cycle_run"] == 91

    for lab, c in b["per_config"].items():
        assert c["first_behavioural_cycle_min"] == c["confirmation_cycle_min"] + 1, lab
        assert c["first_behavioural_cycle_max"] == c["confirmation_cycle_max"] + 1, lab
        assert c["run_length_needed_cycles"] == c["first_behavioural_cycle_max"] + 100, lab
        row = ("| `%s` | %d | %.0f–%.0f–%.0f | %.0f–%.0f–%.0f | %d | %d of %d |"
               % (lab, c["runs_with_a_clock"],
                  c["confirmation_cycle_min"], c["confirmation_cycle_median"],
                  c["confirmation_cycle_max"],
                  c["first_behavioural_cycle_min"], c["first_behavioural_cycle_median"],
                  c["first_behavioural_cycle_max"], c["run_length_needed_cycles"],
                  c["runs_that_fit_a_600_cycle_run"], c["runs_with_a_clock"]))
        assert row in text, row

    assert "confirmation + 1" in text and "confirmation + 100" in text
    assert "**0 of 119**" in text
    # The record's own runs mostly could not host the follow-up in 600 cycles.
    assert ("**%d of %d**" % (b["runs_that_fit_a_600_cycle_run"], b["runs_with_a_clock"])) in text
    assert "per world" in text
