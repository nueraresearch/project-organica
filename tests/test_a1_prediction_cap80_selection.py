"""The cap-80 overlap loss is a loop-rank cut plus a transition half-budget cut."""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer
import copy
import json
from pathlib import Path

from benchmarks import a1_prediction_cap80_selection as sel

DOC = json.loads(Path("docs/a1_prediction_cap80_selection.json").read_text(encoding="utf-8"))


def test_record_is_clean_and_governed_off():
    assert sel.problems(DOC) == []
    assert sel.self_test() == []
    assert DOC["not_a_result"] is True
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }
    assert len(DOC["rows"]) == 442


def test_k_side_is_entirely_the_loop_rank_cut():
    summary = {row["label"]: row["edges"] for row in DOC["summary"]["K_reasons"]}
    assert summary == {
        "no_2_or_3_cycle": 0,
        "loop_rank_above_loop_cap": 104,
        "carried_by_selected_loop": 0,
        "carried_by_dream": 0,
        "unclassified": 0,
    }
    rows = [row for row in DOC["rows"] if row["side"] == "A\\K"]
    assert len(rows) == 104
    assert min(row["best_loop_rank"] for row in rows) == 121
    assert max(row["best_loop_rank"] for row in rows) == 848
    assert all(row["best_loop_rank"] > 120 for row in rows)


def test_a_side_is_mostly_the_transition_half_budget():
    summary = {row["label"]: row["edges"] for row in DOC["summary"]["A_reasons"]}
    assert summary == {
        "support_below_prediction_floor": 68,
        "transition_rank_below_half_budget": 254,
        "cooccurrence_rank_below_quota": 0,
        "no_prediction_candidate": 16,
        "inside_returned_window": 0,
        "unclassified": 0,
    }
    transitions = [row for row in DOC["rows"]
                   if row["reason"] == "transition_rank_below_half_budget"]
    assert len(transitions) == 254
    assert min(row["best_transition_rank"] for row in transitions) == 41
    assert max(row["best_transition_rank"] for row in transitions) == 383
    assert all(row["support"] >= 5 for row in transitions)


def test_support_floor_and_residual_candidate_groups():
    floor = [row for row in DOC["rows"]
             if row["reason"] == "support_below_prediction_floor"]
    no_candidate = [row for row in DOC["rows"]
                    if row["reason"] == "no_prediction_candidate"]
    assert len(floor) == 68
    assert {row["support"] for row in floor} == {1, 2, 3, 4}
    assert len(no_candidate) == 16
    assert all(5 <= row["support"] <= 9 for row in no_candidate)


def test_per_seed_overlap_and_rule_counts():
    rows = {row["seed"]: row for row in DOC["seed_rows"]}
    assert {seed: (row["A"], row["K"], row["A_and_K"], row["A_only"],
                   row["K_only"])
            for seed, row in rows.items()} == {
        20660101: (86, 111, 68, 18, 43),
        20660102: (75, 124, 56, 19, 68),
        20660103: (83, 105, 51, 32, 54),
        20660104: (88, 138, 77, 11, 61),
        20660105: (91, 121, 72, 19, 49),
        20660106: (75, 133, 70, 5, 63),
    }
    for row in DOC["summary"]["K_reason_by_seed"]:
        assert row["A_only"] == row["loop_rank_above_loop_cap"]
    for row in DOC["summary"]["A_reason_by_seed"]:
        assert row["K_only"] == (
            row["support_below_prediction_floor"]
            + row["transition_rank_below_half_budget"]
            + row["cooccurrence_rank_below_quota"]
            + row["no_prediction_candidate"]
            + row["inside_returned_window"]
            + row["unclassified"])


def test_a_tampered_reason_total_is_reported():
    bad = copy.deepcopy(DOC)
    bad["summary"]["K_reasons"][1]["edges"] += 1

    assert sel.problems(bad), "reason totals must match the row set"


def test_page_is_current():
    assert sel.PAGE_PATH.read_text(encoding="utf-8") == sel.render(DOC)
    text = sel.PAGE_PATH.read_text(encoding="utf-8")
    assert "120-loop" in text
    assert "121" in text
    assert "254/338" in text
    assert "transition_rank_below_half_budget" in text
