"""The loop-cap counterfactual must preserve its control and expose the ceiling."""
import copy
import json
from pathlib import Path

from benchmarks import a1_loop_cap_counterfactual as counterfactual

DOC = json.loads(
    Path("docs/a1_loop_cap_counterfactual.json").read_text(encoding="utf-8"))
SUPPLY = json.loads(
    Path("docs/a1_k_carrier_supply.json").read_text(encoding="utf-8"))


def test_record_is_clean_and_governed_off():
    assert counterfactual.problems(DOC) == []
    assert counterfactual.self_test() == []
    assert DOC["not_a_result"] is True
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }
    assert len(DOC["rows"]) == 72


def test_cap_totals_are_exact():
    rows = {row["cap"]: row for row in DOC["summaries"]}
    assert [rows[cap]["candidate_K"] for cap in (15, 30, 60, 120)] == [
        714, 1001, 1294, 1498,
    ]
    assert [rows[cap]["new_vs_control"] for cap in (15, 30, 60, 120)] == [
        0, 292, 583, 786,
    ]
    assert [rows[cap]["lost_vs_control"] for cap in (15, 30, 60, 120)] == [
        0, 5, 3, 2,
    ]
    assert [rows[cap]["all_K"] for cap in (15, 30, 60, 120)] == [
        3548, 4693, 5832, 6608,
    ]


def test_blocks_show_the_window_is_still_binding_at_28_tags():
    blocks = {row["label"]: row for row in DOC["by_block"]}
    for label, values in (
            ("current-16", (228, 302, 362, 382)),
            ("fresh-16", (242, 303, 360, 383)),
            ("larger-28", (244, 396, 572, 733))):
        assert [blocks[label][str(cap)]["candidate_K"]
                for cap in (15, 30, 60, 120)] == list(values)


def test_cap_15_reproduces_the_carrier_supply_sets():
    supply = {
        (seed["summary"]["block"], seed["summary"]["seed"]):
        {row["edge"] for row in seed["edges"] if row["K"]}
        for seed in SUPPLY["seeds"]
    }
    assert all(
        row["candidate_K"] == len(supply[(row["block"], row["seed"])])
        for row in DOC["rows"] if row["cap"] == 15
    )


def test_direction_is_positive_but_the_strict_verdict_is_mixed():
    assert DOC["verdict"].startswith("MIXED")
    assert DOC["reading"].startswith("Raising the loop cap from 15 to 120")
    assert "714" in DOC["reading"] and "1498" in DOC["reading"]
    assert "10 edges are lost" in DOC["reading"]
    assert DOC["verdict_rule"]


def test_a_tampered_total_is_reported():
    bad = copy.deepcopy(DOC)
    next(row for row in bad["summaries"] if row["cap"] == 120)["candidate_K"] += 1

    assert counterfactual.problems(bad), "a total that disagrees with rows must fail"


def test_page_is_current():
    assert counterfactual.PAGE_PATH.read_text(encoding="utf-8") == \
        counterfactual.render(DOC)
    text = counterfactual.PAGE_PATH.read_text(encoding="utf-8")
    assert "MIXED" in text and "1,498" not in text
    assert "714" in text and "1498" in text
    assert "382/383" in text and "733/1,000" in text
