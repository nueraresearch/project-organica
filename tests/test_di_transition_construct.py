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
