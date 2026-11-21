"""New A edges at cap 112 carry K at the retained rate; the pooled drop is mix."""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer
import copy
import json
from pathlib import Path

from benchmarks import a1_prediction_cap_turnover as turn

DOC = json.loads(Path("docs/a1_prediction_cap_turnover.json").read_text(encoding="utf-8"))


def test_record_is_clean_and_governed_off():
    assert turn.problems(DOC) == []
    assert turn.self_test() == []
    assert DOC["not_a_result"] is True
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }
    assert len(DOC["rows"]) == 18
    assert len(DOC["by_block"]) == 3


def test_a_is_nested_from_cap80_to_cap112():
    pooled = DOC["pooled"]
    assert (pooled["A_low"], pooled["A_high"], pooled["new"],
            pooled["dropped"]) == (1129, 1269, 140, 0)
    assert (pooled["C1_joint_low"], pooled["C1_joint_high"]) == (1025, 1150)
    assert all(row["dropped"] == 0 for row in DOC["rows"])
    assert all(row["retained"] + row["new"] == row["A_high"]
               for row in DOC["rows"])


def test_k_sets_are_identical_at_both_caps():
    assert DOC["pooled"]["seeds_with_identical_K"] == 18
    assert all(row["K_identical"] for row in DOC["rows"])


def test_the_16_tag_seeds_are_k_complete_and_cannot_answer():
    for row in DOC["rows"]:
        if row["block"] == "larger-28":
            continue
        assert row["new_K_rate"] == 1.0
        assert row["retained_K_rate"] == 1.0


def test_larger_28_new_edges_join_k_at_the_retained_rate():
    pooled = DOC["pooled"]
    assert (pooled["retained_in_K"], pooled["new_in_K"]) == (1025, 125)
    assert (pooled["retained_rate"], pooled["new_rate"],
            pooled["rate_difference"]) == (0.907883, 0.892857, -0.015026)
    larger = next(entry for entry in DOC["by_block"]
                  if entry["block"] == "larger-28")
    assert (larger["retained"], larger["new"], larger["retained_in_K"],
            larger["new_in_K"]) == (498, 80, 394, 65)
    assert (larger["retained_rate"], larger["new_rate"]) == (
        0.791165, 0.8125)
    assert pooled["larger_rate_difference"] == 0.021335


def test_the_pooled_drop_is_composition_not_a_lower_rate():
    pooled = DOC["pooled"]
    assert (pooled["new_share_larger"],
            pooled["retained_share_larger"]) == (0.571429, 0.441098)
    assert pooled["block_adjusted_expected_new_in_K"] == 123.2932
    assert pooled["block_adjusted_excess"] == 1.7068


def test_the_sign_tests_report_no_resolvable_difference():
    assert DOC["sign_test"] == {
        "below": 3, "above": 2, "ties": 13, "n": 5, "p_value": 1.0}
    assert DOC["sign_test_larger28"] == {
        "below": 3, "above": 2, "ties": 1, "n": 5, "p_value": 1.0}


def test_a_seed_row_is_exact():
    row = DOC["rows"][0]
    assert (row["block"], row["seed"], row["candidate_edges"]) == (
        "current-16", 20630101, 64)
    assert (row["A_low"], row["A_high"], row["retained"], row["new"],
            row["new_in_K"]) == (51, 57, 51, 6, 6)
    larger = DOC["rows"][12]
    assert (larger["block"], larger["seed"], larger["A_low"],
            larger["A_high"], larger["new"], larger["new_in_K"]) == (
        "larger-28", 20660101, 86, 101, 15, 11)
    assert (larger["new_K_rate"], larger["retained_K_rate"]) == (
        0.733333, 0.790698)


def test_a_tampered_pooled_total_is_reported():
    bad = copy.deepcopy(DOC)
    bad["pooled"]["new_in_K"] = 0

    assert turn.problems(bad)


def test_a_tampered_rate_is_reported():
    bad = copy.deepcopy(DOC)
    bad["rows"][0]["new_K_rate"] = 0.5

    assert turn.problems(bad)


def test_page_is_current():
    assert turn.PAGE_PATH.read_text(encoding="utf-8") == turn.render(DOC)
    text = turn.PAGE_PATH.read_text(encoding="utf-8")
    assert "0.812" in text
    assert "0.893" in text
    assert "123.3" in text
    assert "ties by construction" in text
