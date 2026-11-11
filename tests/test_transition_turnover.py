"""The turnover table must derive from the committed campaign tables and must be able to fail.

The table is a view of records the campaign already wrote: each cycle's served transition prefix
and the served window. These tests hold the view to those records and prove the guard rejects a
tampered row, a tampered association and a stale page.
"""
LAYER = "synthetic"  # benchmarks/test_layers.py: derives from committed artifacts only

import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import transition_turnover as turnover  # noqa: E402


def artifact() -> dict:
    return json.loads(turnover.ARTIFACT.read_text(encoding="utf-8"))


def tables() -> dict:
    return json.loads(turnover.N3.read_text(encoding="utf-8"))


def test_the_record_reproduces_from_committed_data():
    art = artifact()

    assert turnover.problems(art) == []
    assert art["not_a_result"] is True
    assert len(art["seeds"]) == 6
    assert [record["cycles"] for record in art["seeds"]] == [120] * 6
    for record in art["seeds"]:
        assert record["transition_slots"] == (
            record["top20_union"] + record["carried"] + record["returned"])
        assert record["top20_union"] == (record["top20_union_world"]
                                          + record["top20_union_outside_world"])
        assert record["top20_union_world"] == record["s_ever"]
        assert sum(row["first_seen_world"] for row in record["turnover"]) \
            == record["s_ever"]
        assert 0 < record["mean_new_world_per_cycle"] < record["mean_new_per_cycle"]


def test_the_top_set_is_every_cycles_served_transition_prefix():
    for cell in tables()["campaign_cells"]:
        series = turnover.cycle_sets(cell)
        assert len(series) == len(cell["cycles"])
        for (cycle_no, top), cycle in zip(series, cell["cycles"]):
            if cycle_no != cycle["cycle"]:
                raise AssertionError("cycle order")
            edges = [tuple(edge.split(">")) for edge in cycle["universe"]["edges"]]
            relations = cycle["universe"]["relations"]
            prefix = [edge for edge, name in zip(edges, relations) if name == "t"][
                :turnover.TOP]
            served = {tuple(edge) for edge in cycle["served"]}
            assert top == prefix, (cell["seed"], cycle_no)
            assert set(top) <= served, (cell["seed"], cycle_no)
            assert len(top) == min(turnover.TOP,
                                   sum(1 for name in relations if name == "t"))


def test_a_tampered_turnover_row_is_reported():
    bad = copy.deepcopy(artifact())
    bad["seeds"][0]["turnover"][5]["new"] += 1

    assert turnover.problems(bad), "a row that disagrees with the campaign tables must fail"


def test_a_tampered_association_is_reported():
    bad = copy.deepcopy(artifact())
    bad["associations"]["mean_new_vs_s_ever"]["spearman"] = 0.5

    assert turnover.problems(bad), "a correlation that is not recomputed must fail"


def test_the_page_is_current():
    art = artifact()

    assert turnover.PAGE.read_text(encoding="utf-8") == turnover.render(art)
    assert "Not a result artifact" in turnover.PAGE.read_text(encoding="utf-8")
