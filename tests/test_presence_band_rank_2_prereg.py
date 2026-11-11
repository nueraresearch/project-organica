"""The frozen BAND-2 record: corrected B5, fixed rank reading, no cells."""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import copy
import json

import pytest

from benchmarks import presence_band_rank_2_prereg as band2


def _doc():
    return band2.record()


def _problems(doc):
    return band2.problems(doc, page=band2.render(doc))


def test_the_record_checks_and_page_match():
    assert band2.problems() == []
    page = band2.PAGE.read_text(encoding="utf-8")
    assert "PRESENCE-BAND-2" in page
    assert "at least 56" in page
    assert "exactly one" in page
    assert "No cell has run" in page


def test_the_block_is_frozen_unrun_and_ungranted():
    doc = _doc()
    assert doc["status"] == "FROZEN, NOT RUN"
    assert doc["no_cells_run"] is True
    assert doc["authorisation"]["granted"] is False
    assert doc["authorisation"]["document"] is None
    assert doc["runner"]["built"] is False
    assert doc["runner"]["cells_run"] == 0
    assert not band2.RUN.exists()
    assert not band2.ARM.exists()


def test_b5_is_a_floor_with_backfill_not_an_exact_56():
    gate = _doc()["gates"]["B5_cap_live"].lower()
    assert "at least 56" in gate
    assert "floor" in gate
    assert "backfill" in gate
    assert "block rank 40" in gate
    assert "== 56" not in gate
    assert "exactly 56" not in gate


def test_b5_is_derived_from_the_engine_source():
    correction = _doc()["b5_correction"]
    assert correction["source"] == "organica/sleep_extraction.py:511-525"
    source = band2.SOURCE.read_text(encoding="utf-8")
    assert "transition_budget = returned_budget // 2" in source
    assert "more_trans" in source
    assert "64-69" in correction["why_it_was_wrong"]


def test_the_rank_reader_parses_the_edge_and_takes_the_minimum():
    cell = {
        "windows_world": [["amber>olive", "birch>cedar"]],
        "universe": [[
            {"edge": ["amber", "olive"], "rank": 41, "relation": "transition"},
            {"edge": ["birch", "cedar"], "rank": 23, "relation": "transition"},
        ]],
    }
    reading = band2.rank_reading(cell)
    assert reading["served"] == 2
    assert reading["served_transitions"] == 2
    assert reading["max_served_transition_rank"] == 41
    assert reading["missing_rank"] == []
    assert band2.read_served_edge("amber>olive") == ("amber", "olive")


def test_a_missing_rank_fails_and_is_never_zero():
    cell = {
        "windows_world": [["amber>olive", "birch>cedar"]],
        "universe": [[{"edge": ["amber", "olive"], "rank": 41, "relation": "transition"}]],
    }
    reading = band2.rank_reading(cell)
    assert reading["max_served_transition_rank"] == 41
    assert reading["missing_rank"] == ["birch>cedar"]


def test_malformed_served_edges_are_rejected():
    for bad in ("amberolive", "a>b>c", ">target", "source>", ("a", "b"), ""):
        with pytest.raises(ValueError):
            band2.read_served_edge(bad)


def test_the_band_matches_q4_and_band1():
    doc = _doc()
    q4 = json.loads(band2.Q4.read_text(encoding="utf-8"))
    table = {str(row["seed"]): row for row in q4["stage_table"]}
    band1 = json.loads(band2.BAND1.read_text(encoding="utf-8"))
    assert doc["band"]["total"] == 62
    for seed, row in doc["band"]["seeds"].items():
        assert len(row["edges"]) == table[seed]["never_served_rank_half_to_cap"]
        assert row["world_digest"] == band1["band"]["seeds"][seed]["world_digest"]
        assert all(21 <= edge[2] <= 40 for edge in row["edges"])


def test_the_decision_table_covers_every_frozen_verdict():
    verdicts = {row["verdict"] for row in _doc()["decision_table"]}
    assert verdicts == {"VOID", "BAND NOT REPRODUCED", "BAND IN SERVICE",
                        "BAND PARTLY IN SERVICE", "BAND NOT IN SERVICE"}


def test_a_reverted_exact_count_is_caught():
    doc = copy.deepcopy(_doc())
    doc["gates"]["B5_cap_live"] = (
        "the 112 arm's transition allocation is exactly 56 and its served transition prefix "
        "extends past block rank 40; 40 never returns more than 40 rows"
    )
    assert any("B5" in problem for problem in _problems(doc))


def test_a_dropped_edge_or_a_runner_claim_is_caught():
    dropped = copy.deepcopy(_doc())
    dropped["band"]["seeds"]["20611601"]["edges"].pop()
    assert _problems(dropped)

    claimed = copy.deepcopy(_doc())
    claimed["runner"]["cells_run"] = 1
    assert any("runner" in problem for problem in _problems(claimed))

    ran = copy.deepcopy(_doc())
    ran["no_cells_run"] = False
    assert any("no cell" in problem for problem in _problems(ran))


def test_a_grant_without_a_document_is_caught():
    doc = copy.deepcopy(_doc())
    doc["authorisation"]["granted"] = True
    assert any("grant" in problem for problem in _problems(doc))


def test_the_acceptance_quote_is_the_admission_decision_sentence():
    quote = _doc()["acceptance"]["quote"]
    text = " ".join(band2.DECISION.read_text(encoding="utf-8").split())
    assert quote in text
