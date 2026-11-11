"""PRESENCE-BAND-3 is a fresh-world band block with a grant but no run."""
LAYER = "static"

import copy

import pytest

from benchmarks import presence_band_rank_3_prereg as band3


def _cell(**overrides):
    cell = {
        "cap": 112,
        "allocation": [{"transitions": 56}],
        "windows": [["amber>olive"]],
        "windows_world": [["amber>olive"]],
        "present_edges": [["amber", "olive"]],
        "universe": [[{"edge": ["amber", "olive"], "rank": 56, "relation": "transition"}]],
    }
    cell.update(overrides)
    return cell


def _problems(doc):
    return band3.problems(doc, page=band3.render(doc))


def test_the_record_checks_and_page_matches():
    assert band3.problems() == []
    page = band3.PAGE.read_text(encoding="utf-8")
    assert "PRESENCE-BAND-3" in page
    assert "fresh" in page
    assert "B5 that can fail" in page


def test_the_block_is_frozen_granted_and_unrun():
    doc = band3.record()
    assert doc["status"] == "FROZEN, NOT RUN"
    assert doc["no_cells_run"] is True
    assert doc["authorisation"]["granted"] is True
    assert doc["authorisation"]["granted_on"] == "2026-11-11"
    assert doc["runner"]["built"] is False
    assert doc["runner"]["cells_run"] == 0
    assert not band3.RUN.exists()
    assert not band3.ARM.exists()


def test_the_six_seeds_are_fresh():
    from benchmarks.presence_cap_experiment import seed_collisions

    seeds = band3.record()["design"]["seeds"]
    assert len(seeds) == len(set(seeds)) == 6
    assert seed_collisions(seeds, allow=(band3.RECORD, band3.PAGE, band3.AUTH)) == {}


def test_the_band_is_measured_and_excludes_rank_41_and_cooccurrences():
    cell = _cell(
        present_edges=[["amber", "olive"], ["birch", "cedar"], ["fern", "willow"]],
        universe=[[
            {"edge": ["amber", "olive"], "rank": 25, "relation": "transition"},
            {"edge": ["birch", "cedar"], "rank": 41, "relation": "transition"},
            {"edge": ["fern", "willow"], "rank": 25, "relation": "cooccurrence"},
        ]],
    )
    assert band3.band_edges(cell) == {("amber", "olive"): 25}
    with pytest.raises(ValueError):
        band3.band_edges({**cell, "cap": 40})


def test_b5_passes_the_live_fixture_and_fails_each_repair_case():
    assert band3.b5_cap_live(_cell())["passed"] is True

    short = band3.b5_cap_live(_cell(allocation=[{"transitions": 20}]))
    ceiling = band3.b5_cap_live(_cell(universe=[[
        {"edge": ["amber", "olive"], "rank": 40, "relation": "transition"}
    ]]))
    unranked = band3.b5_cap_live(_cell(windows_world=[["birch>cedar"]]))
    malformed = band3.b5_cap_live(_cell(windows_world=[["amber>olive>bad"]]))

    for result in (short, ceiling, unranked, malformed):
        assert result["passed"] is False
        assert result["reasons"]


def test_an_exact_56_rewrite_is_caught():
    doc = copy.deepcopy(band3.record())
    doc["gates"]["B5_cap_live"] = (
        "the 112 arm's transition allocation is exactly 56 and its served transition "
        "prefix extends past block rank 40; no window above 112 rows"
    )
    assert any("B5" in problem for problem in _problems(doc))


def test_the_grant_quotes_its_document_and_the_acceptance_quote_is_the_decision():
    auth = band3.record()["authorisation"]
    text = band3.AUTH.read_text(encoding="utf-8")
    assert auth["quote"] in text and auth["granted_on"] in text
    quote = band3.record()["acceptance"]["quote"]
    decision = " ".join(band3.DECISION.read_text(encoding="utf-8").split())
    assert quote in decision


def test_a_run_claim_or_stale_page_is_caught():
    doc = copy.deepcopy(band3.record())
    doc["runner"]["cells_run"] = 1
    assert any("runner" in problem or "run" in problem for problem in _problems(doc))

    doc = band3.record()
    stale = band3.render(doc).replace("FROZEN, NOT RUN", "FROZEN, RUN", 1)
    assert any("page" in problem for problem in band3.problems(doc=doc, page=stale))
