"""Band position, error budget and seeds per split block."""
import json
from pathlib import Path

from benchmarks import a1_band_frontier as band

DOC = json.loads(Path("docs/a1_band_frontier.json").read_text(encoding="utf-8"))
ROWS = {(row["floor"], row["ceiling"]): row for row in DOC["rows"]}


def test_record_is_clean_and_governed_off():
    assert band.problems(DOC) == []
    assert band.self_test() == []
    assert DOC["not_a_result"] is True
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }


def test_the_committed_bands_need_nine_seeds():
    committed = ROWS[(0.05, 0.09)]
    assert committed["seeds"] == {"0.05": 9, "0.10": 9}
    six = committed["at_six"]
    assert six["size_if_size"] == 0.81794
    assert six["density_if_density"] == 0.767202
    assert six["density_if_size"] == 0.01268


def test_the_ceiling_is_the_slack_and_the_floor_is_not():
    found = DOC["found"]
    assert found["ceiling_can_drop_to"] == 0.0633
    assert found["floor_can_rise_to"] == 0.05308
    assert found["bounds"][0]["n"] == 6
    assert found["bounds"][1]["floor_max"] == 0.064696


def test_a_wider_ceiling_buys_three_seeds():
    found = DOC["found"]
    cheapest = ROWS[(0.05, 0.07)]
    assert cheapest["seeds"]["0.05"] == 6
    assert found["seeds_cheapest_at_5pct"] == 6
    assert found["seeds_saved_at_5pct"] == 3
    assert (found["cheapest_floor"], found["cheapest_ceiling"]) == (0.05, 0.07)


def test_raising_the_floor_costs_seeds():
    assert ROWS[(0.07, 0.09)]["seeds"]["0.05"] == 12
    assert ROWS[(0.07, 0.09)]["seeds"]["0.05"] > ROWS[(0.05, 0.09)]["seeds"]["0.05"]


def test_tightening_both_edges_costs_more():
    assert ROWS[(0.04, 0.10)]["seeds"]["0.05"] == 23


def test_the_single_threshold_is_cheaper_only_at_a_loose_budget():
    found = DOC["found"]
    assert found["single_threshold_seeds"] == 8
    assert found["single_threshold_seeds"] > found["seeds_cheapest_at_5pct"]
    assert found["seeds_floor_at_5pct"] == 6
    assert found["seeds_floor_at_10pct"] == 4
    assert found["seeds_floor_at_10pct_bands"] == [0.0582, 0.0582]


def test_the_outcome_distributions_are_complete():
    for row in DOC["rows"]:
        for truth in ("if_size", "if_density"):
            total = sum(row["at_six"]["%s_%s" % (branch, truth)]
                        for branch in ("size", "density", "undecided"))
            assert abs(total - 1.0) < 1e-5
