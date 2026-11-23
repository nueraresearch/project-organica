"""PRESENCE-BAND-4 is a frozen, ungranted confirmatory allocation block."""

LAYER = "static"

import copy

import pytest

from benchmarks import presence_band_rank_4_prereg as band4


def _cell(**overrides):
    cell = {
        "cap": 112,
        "allocation": [{"transitions": 64, "cooccurrences": 48}],
        "windows": [["amber>olive"] * 112],
        "windows_world": [["amber>olive"] * 112],
        "present_edges": [["amber", "olive"]],
        "universe": [[{"edge": ["amber", "olive"], "rank": 64, "relation": "transition"}]],
    }
    cell.update(overrides)
    return cell


def _problems(doc):
    return band4.problems(doc, page=band4.render(doc))


def test_the_record_checks_and_page_matches():
    assert band4.problems() == []
    page = band4.PAGE.read_text(encoding="utf-8")
    assert "PRESENCE-BAND-4" in page
    assert "allocation" in page
    assert "64-69" in page
    assert "CONFIRMED" in page


def test_the_record_is_frozen_ungranted_and_unrun():
    doc = band4.record()
    assert doc["status"] == "FROZEN, NOT RUN"
    assert doc["no_cells_run"] is True
    assert doc["authorisation"]["granted"] is False
    assert doc["runner"]["built"] is False
    assert doc["runner"]["cells_run"] == 0
    assert not band4.RUN.exists()
    assert not band4.ARM.exists()


def test_the_six_seeds_are_fresh():
    from benchmarks.presence_cap_experiment import seed_collisions

    seeds = band4.record()["design"]["seeds"]
    assert len(seeds) == len(set(seeds)) == 6
    assert seed_collisions(seeds, allow=(band4.RECORD, band4.PAGE)) == {}


def test_the_band_is_measured_and_excludes_rank_41_and_cooccurrences():
    cell = _cell(
        present_edges=[["amber", "olive"], ["birch", "cedar"], ["fern", "willow"]],
        universe=[[
            {"edge": ["amber", "olive"], "rank": 25, "relation": "transition"},
            {"edge": ["birch", "cedar"], "rank": 41, "relation": "transition"},
            {"edge": ["fern", "willow"], "rank": 25, "relation": "cooccurrence"},
        ]],
    )
    assert band4.band_edges(cell) == {("amber", "olive"): 25}
    with pytest.raises(ValueError):
        band4.band_edges({**cell, "cap": 40})


def test_the_allocation_law_accepts_both_observed_backfill_and_the_floor():
    backfill = band4.allocation_law(
        _cell(), cap=112, floor=56, cooc_max=56
    )
    floor = band4.allocation_law(
        _cell(allocation=[{"transitions": 56, "cooccurrences": 56}]),
        cap=112,
        floor=56,
        cooc_max=56,
    )
    assert backfill["passed"] is True, backfill["reasons"]
    assert floor["passed"] is True, floor["reasons"]
    assert backfill["max_transitions"] == 64


def test_each_b5_failure_fixture_fails_and_the_exact_56_is_rejected():
    results = band4.b5_fixture_results()
    assert results["pass_64_plus_48"]["passed"] is True
    assert results["pass_56_plus_56"]["passed"] is True
    for name, result in results.items():
        if name.startswith("fail_"):
            assert result["passed"] is False, name
            assert result["reasons"], name


def test_the_acceptance_states_two_independent_failures():
    doc = band4.record()
    acceptance = doc["acceptance"]
    assert "co-primary" in acceptance["kind"]
    assert "independently" in acceptance["independent_failure"].lower()
    assert "not used as a threshold" in acceptance["not_fitted"]
    verdicts = {row["verdict"] for row in doc["decision_table"]}
    assert {"ALLOCATION LAW NOT CONFIRMED", "BAND NOT CONFIRMED", "CONFIRMED"} <= verdicts


def test_a_floor_only_or_exact_56_b5_is_caught():
    floor_only = copy.deepcopy(band4.record())
    floor_only["gates"]["B5_allocation_law"] = (
        "the 112 arm has at least 56 transitions; no window above 112"
    )
    assert any("B5" in problem for problem in _problems(floor_only))

    exact = copy.deepcopy(band4.record())
    exact["gates"]["B5_allocation_law"] = (
        "the 112 arm's transition allocation is exactly 56 and its rank ceiling is live"
    )
    assert any("B5" in problem for problem in _problems(exact))


def test_a_run_claim_or_stale_page_is_caught():
    doc = copy.deepcopy(band4.record())
    doc["runner"]["cells_run"] = 1
    assert any("runner" in problem or "run" in problem for problem in _problems(doc))

    doc = band4.record()
    stale = band4.render(doc).replace("FROZEN, NOT RUN", "FROZEN, RUN", 1)
    assert any("page" in problem for problem in band4.problems(doc=doc, page=stale))
