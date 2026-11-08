"""The age-matched addendum must be able to say "age explains it" and "age does not"."""

import json
from pathlib import Path

import pytest

from benchmarks import q052_age_matched as A
from benchmarks import q052_amendment_a2 as a2

ROOT = Path(__file__).resolve().parent.parent


def test_each_reading_rule_branch_is_reachable():
    assert A.reading(0.31, None)[0] == "AGE_MATCH_UNAVAILABLE"
    label, difference = A.reading(0.31, {"mass_ratio": 0.35})
    assert label == "AGE_EXPLAINS_THE_GAP"
    assert difference == pytest.approx(0.04)
    label, difference = A.reading(0.31, {"mass_ratio": 0.57})
    assert label == "AGE_DOES_NOT_EXPLAIN_THE_GAP"
    assert difference == pytest.approx(0.26)
    # the band is inclusive, and it is the committed one
    assert A.reading(0.31, {"mass_ratio": 0.31 + A.MATCH_BAND})[0] == "AGE_EXPLAINS_THE_GAP"


def test_the_live_cycles_were_captured_and_were_live():
    part = A.load_part(A.CONTROL["factor"])
    window = {int(cycle): row for cycle, row in part["window"].items()}
    for cycle in A.LIVE_CYCLES:
        assert cycle - 1 in window and cycle in window, cycle
        assert window[cycle - 1]["theories"], "cycle %d was not live" % (cycle - 1)
    assert A.live_cells(part), "no live cell was derived"


def test_the_committed_artifact_is_the_one_its_matches_imply():
    artifact = json.loads(A.ARTIFACT.read_text(encoding="utf-8"))
    assert A.validate() == []
    assert artifact["amendment"] == "A2a"
    assert artifact["reading_rule"] == A.READING_RULE
    assert artifact["label"] in ("AGE_MATCH_UNAVAILABLE", "AGE_EXPLAINS_THE_GAP",
                                 "AGE_DOES_NOT_EXPLAIN_THE_GAP")
    assert len(artifact["lattice_live"]) == len(A.LIVE_CYCLES)
    assert len(artifact["burst"]) == len(A.BURST_DEATHS)
    assert len(artifact["matches"]) == len(A.BURST_DEATHS)
    assert artifact["no_new_engine"] is True


def test_bracketing_interpolates_between_deaths_and_needs_both_sides():
    deaths = [{"death_cycle": 100, "mass_ratio": 0.60},
              {"death_cycle": 200, "mass_ratio": 0.50}]
    mid = A.bracket(deaths, 150)
    assert mid["estimate"] == pytest.approx(0.55)
    assert (mid["below"], mid["above"]) == (100, 200)
    assert A.bracket(deaths, 50) is None, "no death below the cycle"
    assert A.bracket(deaths, 250) is None, "no death above the cycle"


def test_the_committed_trend_is_flat_and_the_burst_ratios_fall_below_it():
    artifact = json.loads(A.ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["age_flat"] is True
    assert artifact["age_spread"] <= artifact["band"]
    for cell in artifact["bracketed"]:
        assert cell["estimate"] is not None
        assert cell["beyond_band"] is True, cell


def test_the_addendum_does_not_move_the_amended_label():
    a2_artifact = json.loads(a2.ARTIFACT.read_text(encoding="utf-8"))
    assert a2_artifact["label"] == "DIFFERENT_SUPPORT_COLLAPSE"
    assert A.validate() == []
