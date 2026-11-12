"""The carrier trace must cover the 26 rows and its controls must be able to fail.

Static controls: these read the committed trace and exercise its pure path
classifier. They do not replay a cell.
"""
LAYER = "static"

import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import assertion_carrier_trace as carrier  # noqa: E402


def artifact() -> dict:
    return json.loads(carrier.ARTIFACT.read_text(encoding="utf-8"))


def test_the_trace_reproduces_and_covers_all_26_edges():
    art = artifact()

    assert carrier.problems(art) == []
    assert art["not_a_result"] is True
    assert art["summary"]["edges"] == 26
    assert art["summary"]["loop_carrier_rows"] == 26
    assert art["summary"]["dream_carrier_rows"] == 1
    assert art["summary"]["loop_carriers"] == 61
    assert art["summary"]["dream_carriers"] == 1
    assert art["summary"]["two_cycle_loops"] == 3
    assert art["summary"]["three_cycle_loops"] == 58


def test_every_row_is_carried_by_a_loop_and_the_direct_edge_clears_the_floor():
    art = artifact()

    for row in art["rows"]:
        assert row["loop_carriers"] >= 1, row["edge"]
        assert row["direct_temporal_count"] >= carrier.PREDICTION_FLOOR, row["edge"]
        assert row["reverse_temporal_count"] >= carrier.PREDICTION_FLOOR, row["edge"]
        assert row["prediction_source"] is False, row["edge"]
        for item in row["carriers"]:
            assert item["formation_cycle"] is not None
            assert item["hit_edges"]
            assert item["path"]


def test_the_loop_symmetry_and_missing_controls_are_not_vacuous():
    controls = {item["name"]: item for item in artifact()["controls"]}

    assert controls["loop_symmetry_control"]["hits"] == ["direct", "reverse"]
    assert controls["dream_direct_control"]["hits"] == ["direct"]
    assert controls["loop_missing_control"]["hits"] == []
    assert controls["dream_missing_control"]["hits"] == []


def test_a_tampered_carrier_path_is_reported():
    bad = copy.deepcopy(artifact())
    bad["rows"][0]["carriers"][0]["path"] = ["amber", "birch", "amber"]

    assert carrier.problems(bad), "a path that no longer contains the edge must fail"


def test_a_tampered_summary_is_reported():
    bad = copy.deepcopy(artifact())
    bad["summary"]["loop_carriers"] += 1

    assert carrier.problems(bad), "a summary that disagrees with the rows must fail"


def test_the_page_is_current():
    art = artifact()

    assert carrier.PAGE.read_text(encoding="utf-8") == carrier.render(art)
    assert "26" in carrier.PAGE.read_text(encoding="utf-8")
    assert "not a result artifact" in carrier.PAGE.read_text(encoding="utf-8").lower()
