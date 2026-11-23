"""The within-cycle distribution ledger must be reproducible and able to fail.

These are static controls over the committed ledger. They do not replay a cell.
"""
LAYER = "static"

import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import within_cycle_distribution as distribution  # noqa: E402


def artifact() -> dict:
    return json.loads(distribution.ARTIFACT.read_text(encoding="utf-8"))


def test_the_distribution_is_reproducible():
    art = artifact()

    assert distribution.problems(art) == []
    assert art["not_a_result"] is True
    assert art["summary"]["zero_cells"] == 5
    assert art["summary"]["control_cells"] == 7
    assert art["summary"]["zero"]["groups"] == 600
    assert art["summary"]["zero"]["max_count_histogram"] == {"0": 8, "1": 78,
                                                             "2": 429, "3": 82, "4": 3}
    assert art["summary"]["zero"]["edge_count_histogram"] == {"1": 12278, "2": 1861,
                                                              "3": 136, "4": 4}
    assert art["summary"]["zero"]["strict"]["max_count_histogram"] == {
        "0": 11, "1": 107, "2": 425, "3": 55, "4": 2}
    assert art["summary"]["zero"]["strict"]["edge_count_histogram"] == {
        "1": 10852, "2": 1408, "3": 80, "4": 2}
    assert art["summary"]["zero_long_groups"] == 0
    assert art["summary"]["control_long_groups"] > 0
    assert art["summary"]["short_engine_max"] == 4
    assert art["summary"]["short_strict_max"] == 4
    assert art["summary"]["long_engine_max"] >= 5
    assert art["summary"]["long_strict_max"] >= 5
    assert art["summary"]["zero_edge_rows"] == 14279
    assert art["summary"]["zero_count1_share"] == 12278 / 14279
    assert art["summary"]["zero_lag0_share"] == 0
    assert art["summary"]["zero_lag1_share"] > 0.8
    assert art["summary"]["zero_count_ge5"] == 0
    assert art["summary"]["control_count_ge5"] > 0
    assert art["summary"]["control_count_ge5_in_short"] == 0
    assert art["summary"]["control_strict_count_ge5_in_short"] == 0


def test_the_positive_control_can_exceed_four():
    control = artifact()["controls"][0]

    assert control["name"] == "repeated_pair_control"
    assert control["passes"] is True
    assert control["max_count"] > 4
    assert control["lag0"] + control["lag1"] + control["lag2"] == control["max_count"]


def test_a_tampered_histogram_is_reported():
    bad = copy.deepcopy(artifact())
    bad["summary"]["zero"]["edge_count_histogram"]["1"] += 1

    assert distribution.problems(bad), "a histogram that disagrees with the cells must fail"


def test_a_short_group_with_a_five_is_reported():
    bad = copy.deepcopy(artifact())
    group = next(group for cell in bad["cells"] if cell["role"] == "control"
                 for group in cell["groups"] if group["events"] <= 8)
    group["max_count"] = 5
    group["count_histogram"]["5"] = 1
    group["edge_observations"] += 1
    group["lag1"] += 1

    assert distribution.problems(bad), "a count 5+ in a short group must fail"


def test_a_stale_page_is_reported():
    art = artifact()

    assert distribution.PAGE.read_text(encoding="utf-8") == distribution.render(art)
    assert "600" in distribution.PAGE.read_text(encoding="utf-8")
    assert "Positive control" in distribution.PAGE.read_text(encoding="utf-8")
