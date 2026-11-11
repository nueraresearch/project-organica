"""The unexplained-edge record must be derivable from committed data and must be able to fail.

The count (26) already lives in the run artifact. This record exists so the *edges* and their
ranks are reproducible on a clean clone, and so a later edit cannot quietly move a number that a
document quotes. Every test here is a control on that guard: tamper with the stored input, the
rows or the summary and the guard must name the disagreement.
"""
LAYER = "synthetic"  # benchmarks/test_layers.py: derives from committed artifacts and a world

import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import presence_unexplained_edges as unexplained  # noqa: E402
from benchmarks.acquisition_compositional import generate_compositional_world  # noqa: E402
from benchmarks.presence_construct_audit import _world_compositional_edges  # noqa: E402


def artifact() -> dict:
    return json.loads(unexplained.ARTIFACT.read_text(encoding="utf-8"))


def test_the_record_reproduces_from_committed_data():
    art = artifact()

    assert unexplained.problems(art) == []
    assert art["summary"]["unexplained"] == 26
    assert art["summary"]["in_cap"] == 10
    assert art["summary"]["within_served_transitions"] == 0
    assert art["summary"]["closest_miss_in_cap"] == 2
    assert art["not_a_result"] is True


def test_every_unexplained_edge_is_present_and_absent_from_every_served_window():
    art = artifact()
    tables = json.loads(unexplained.N3.read_text(encoding="utf-8"))
    cells = {cell["seed"]: cell for cell in tables["campaign_cells"]}

    for record in art["seeds"]:
        cell = cells[record["seed"]]
        windows = [{tuple(edge) for edge in cycle["served"]} for cycle in cell["cycles"]]
        world = _world_compositional_edges(
            generate_compositional_world(seed=record["seed"], cycles=cell["cycles_recorded"]))
        for row in record["edges"]:
            edge = tuple(row["edge"].split(">"))
            assert edge in world
            assert not any(edge in window for window in windows), row["edge"]
            assert row["rank"] >= 1
            assert row["in_cap"] == (row["rank"] <= art["cap"])


def test_a_removed_asserted_edge_is_reported():
    bad = copy.deepcopy(artifact())
    seed = bad["seeds"][0]
    seed["asserted_world_edges"].pop()

    assert unexplained.problems(bad), "a stored edge list that no longer matches the run must fail"


def test_a_tampered_rank_is_reported():
    bad = copy.deepcopy(artifact())
    bad["seeds"][0]["edges"][0]["rank"] += 1

    assert unexplained.problems(bad), "a rank that disagrees with the N3 universe must fail"


def test_a_tampered_summary_is_reported():
    bad = copy.deepcopy(artifact())
    bad["summary"]["unexplained"] += 1

    assert unexplained.problems(bad), "a summary count that disagrees with the rows must fail"


def test_the_page_is_current():
    art = artifact()

    assert unexplained.PAGE.read_text(encoding="utf-8") == unexplained.render(art)
    assert "26" in unexplained.PAGE.read_text(encoding="utf-8")


def test_the_interpretation_note_is_current_and_quotes_the_record():
    art = artifact()
    note = unexplained.NOTE.read_text(encoding="utf-8")

    assert note == unexplained.render_note(art)
    summary = art["summary"]
    assert "%d" % summary["unexplained"] in note
    assert "%d" % summary["asserted"] in note
    assert "%d" % summary["in_cap"] in note
    assert "What it licenses" in note
    assert "What it does not license" in note
    assert "What would change this note" in note
