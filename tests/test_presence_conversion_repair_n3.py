"""The pre-run N3 tables must be derivable from the observer's records and must not pretend to be results.

The artifact exists so the campaign's table shape is fixed before a cell runs. These tests hold it to
the record: every served row appears in the universe with its relation, the allocation counts agree
with the table, and the twelve design cells are still marked `not run`.
"""
LAYER = "synthetic"  # benchmarks/test_layers.py: the module runs the fixture observer

import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import presence_conversion_repair_n3 as n3  # noqa: E402
from benchmarks import presence_conversion_repair_observer as observer  # noqa: E402


def test_the_table_carries_every_served_row_with_its_relation():
    arms = observer.fixture()
    cell = n3.cell_table(arms["on"], seed=observer.FIXTURE_SEED, cap=observer.SHIPPED_CAP)

    assert cell["problems"] == []
    assert cell["cycles_recorded"] == observer.FIXTURE_CYCLES
    assert cell["unknown_relation_served"] == 0
    for cycle in cell["cycles"]:
        served = [row for row in cycle["rows"] if row["served"]]
        assert len(served) == cycle["allocation"]["served"]
        assert all(row["relation"] in n3.RELATIONS for row in served)
        assert all(row["rank"] >= 1 for row in cycle["rows"])
    assert cell["relations_served"]["transition"] + cell["relations_served"]["cooccurrence"] \
        == cell["served_rows"]


def test_the_allocation_counts_sum_to_the_window_every_cycle():
    arms = observer.fixture(seed=observer.SECOND_SEED, cap=112)
    cell = n3.cell_table(arms["on"], seed=observer.SECOND_SEED, cap=112)

    assert cell["problems"] == []
    for cycle in cell["cycles"]:
        allocation = cycle["allocation"]
        assert allocation["sum_matches"] is True
        assert allocation["transitions"] + allocation["cooccurrences"] \
            + allocation["unknown"] == allocation["served"] <= 112


def test_a_tampered_allocation_is_reported():
    arms = observer.fixture()
    cell = n3.cell_table(arms["on"], seed=observer.FIXTURE_SEED, cap=observer.SHIPPED_CAP)
    tampered = copy.deepcopy(cell)
    tampered["cycles"][0]["allocation"]["served"] += 1

    art = {"kind": n3.KIND, "not_a_result": True,
           "design_cells": n3._design_cells(), "fixture_cells": [tampered]}
    assert n3.problems(art), "a table that disagrees with its allocation must not pass"


def test_the_artifact_records_the_twelve_campaign_cells_as_run():
    art = json.loads(n3.ARTIFACT.read_text(encoding="utf-8"))
    run = json.loads(n3.RUN.read_text(encoding="utf-8"))

    assert art["not_a_result"] is True
    assert len(art["design_cells"]) == 12
    assert {cell["state"] for cell in art["design_cells"]} == {"run"}
    assert {(cell["seed"], cell["arm"]) for cell in art["design_cells"]} \
        == {(cell["seed"], cell["arm"]) for cell in run["cells"]}
    assert all(cell["served_fingerprint"] for cell in art["design_cells"])
    assert n3.problems(art) == []
    assert n3.PAGE.read_text(encoding="utf-8") == n3.render_page(art)


def test_a_design_cell_that_does_not_record_the_run_is_rejected():
    art = json.loads(n3.ARTIFACT.read_text(encoding="utf-8"))
    tampered = copy.deepcopy(art)
    tampered["design_cells"][0]["state"] = "not run"

    assert n3.problems(tampered), "a cell left at not run must be rejected once the run exists"


def test_the_band_breakdown_sums_to_the_served_relation_totals():
    art = json.loads(n3.ARTIFACT.read_text(encoding="utf-8"))

    for cell in art["fixture_cells"]:
        by_cycle = n3.band_breakdown(cell)
        totals = n3.band_totals(cell)
        assert sum(totals[b]["transition"] for b in totals) == cell["relations_served"]["transition"]
        assert sum(totals[b]["cooccurrence"] for b in totals) == cell["relations_served"]["cooccurrence"]
        for cycle in by_cycle:
            assert sum(b["transition"] + b["cooccurrence"] for b in cycle["bands"].values()) \
                == cell["cycles"][cycle["cycle"] - 1]["allocation"]["served"]
    for cell in art["campaign_cells"]:
        by_cycle = n3.band_breakdown(cell)
        totals = n3.band_totals(cell)
        assert sum(totals[b]["transition"] + totals[b]["cooccurrence"] for b in totals) \
            == cell["served_rows"]
        for cycle in by_cycle:
            assert sum(b["transition"] + b["cooccurrence"] for b in cycle["bands"].values()) \
                == len(cell["cycles"][cycle["cycle"] - 1]["served"])
    page = n3.PAGE.read_text(encoding="utf-8")
    assert "transitions/cooccurrences" in page
    assert page.count("### Campaign seed ") == len(art["campaign_cells"])


def test_the_campaign_cells_carry_their_own_universe_and_allocation():
    art = json.loads(n3.ARTIFACT.read_text(encoding="utf-8"))
    run = json.loads(n3.RUN.read_text(encoding="utf-8"))
    cells = art["campaign_cells"]

    assert [cell["seed"] for cell in cells] == [cell["seed"] for cell in art["design_cells"]
                                                if cell["arm"] == "on"]
    assert all(cell["cycles_recorded"] == 120 for cell in cells)
    first = cells[0]["cycles"][0]
    assert (len(first["universe"]["edges"]) == len(first["universe"]["relations"])
            == len(first["universe"]["strength"]))
    assert n3._campaign_problems(art, run) == []


def test_the_campaign_table_check_can_fail_on_a_tampered_served_edge():
    art = json.loads(n3.ARTIFACT.read_text(encoding="utf-8"))
    run = json.loads(n3.RUN.read_text(encoding="utf-8"))
    bad = json.loads(json.dumps(art))
    bad["campaign_cells"][0]["cycles"][0]["served"].append(["not", "an-edge"])

    assert n3._campaign_problems(bad, run)

    band_bad = copy.deepcopy(art)
    band_bad["campaign_cells"][0]["served_rows"] += 1
    assert any("band totals" in problem for problem in n3.problems(band_bad)), (
        "a band total that no longer equals the served count must fail")
