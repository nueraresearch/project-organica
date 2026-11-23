"""The persistence-mechanism follow-up is frozen, factorial and unrun.

T1b's result decision names the next question -- pursue the persistence mechanism (decay,
floor, denominator). This block separates the two mechanisms at cap 112 with a 2 x 2 design and
holds the denominator reading fixed. The checks below are static: they read the record and page,
never an engine, and they prove the guard fires on a changed arm, seed, gate, grant or page.
"""

from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import copy
import json
from pathlib import Path

import pytest

from benchmarks import persistence_mechanism_prereg as P
from benchmarks import presence_cap_experiment as cap

ROOT = Path(__file__).resolve().parents[1]


def test_the_record_is_frozen_unrun_and_has_no_runner_or_result():
    doc = P.record()
    assert doc["status"] == "FROZEN, NOT RUN"
    assert doc["frozen_on"] == "2026-11-11"
    assert doc["no_cells_run"] is True
    assert doc["runner"]["built"] is False
    assert doc["runner"]["cells_run"] == 0
    assert doc["authorisation"]["granted"] is False
    assert not P.ARM.exists(), "the arm module exists for an unbuilt runner"
    assert not P.RUN.exists(), "a result exists for a block with no cells"


def test_the_page_is_rendered_from_the_record():
    assert P.problems() == []
    assert P.PAGE.read_text(encoding="utf-8").strip() == P.render(P.record()).strip()


def test_t1b_decision_is_the_program_and_is_present_verbatim():
    result = " ".join(P.T1B_RESULT.read_text(encoding="utf-8").split())
    assert P.T1B_DECISION in result
    doc = P.record()
    assert doc["program"]["source"] == "T1B-PERSISTENCE-OFF"
    assert doc["program"]["decision_quote"] == P.T1B_DECISION
    assert "T1" in doc["program"]["relationship"]
    assert "does not re-read" in doc["program"]["relationship"]


def test_the_design_is_the_frozen_two_by_two():
    design = P.record()["design"]
    assert design["cap"] == 112
    assert design["cycles"] == 120
    assert design["cells"] == 24
    assert design["cells_arithmetic"] == "4 arms x 6 seeds = 24 cells"
    assert design["seeds"] == [20612301, 20612302, 20612303, 20612304, 20612305, 20612306]
    assert design["bootstrap"] == 20612307
    assert design["factors"] == {
        "decay_factor": {"shipped": 0.95, "no_decay": 1.0},
        "read_floor": {"shipped": 5, "one": 1},
    }
    arms = P.record()["arms"]
    assert set(arms) == {"shipped", "no_decay", "floor_one", "no_decay_floor_one"}
    assert (arms["shipped"]["decay_factor"], arms["shipped"]["read_floor"]) == (0.95, 5)
    assert (arms["no_decay"]["decay_factor"], arms["no_decay"]["read_floor"]) == (1.0, 5)
    assert (arms["floor_one"]["decay_factor"], arms["floor_one"]["read_floor"]) == (0.95, 1)
    assert (arms["no_decay_floor_one"]["decay_factor"],
            arms["no_decay_floor_one"]["read_floor"]) == (1.0, 1)


def test_the_seed_block_is_fresh():
    design = P.record()["design"]
    collisions = cap.seed_collisions(design["seeds"] + [design["bootstrap"]],
                                     allow=(P.RECORD, P.PAGE))
    assert collisions == {}


def test_the_engine_is_pinned_at_the_t1b_build_and_cap():
    engine = P.record()["engine"]
    assert engine["version"] == "0.15.0"
    assert engine["cap"] == 112
    assert engine["edit"] == "none"
    assert "landing_0_15_0" in engine["pin"]


def test_the_primary_endpoint_and_both_contrasts_are_defined():
    effects = P.record()["effects"]
    assert effects["primary_endpoint"] == "S_ever"
    assert "S_ever(no_decay, floor 5)" in effects["definitions"]["decay_effect"]
    assert "S_ever(floor_one" in effects["definitions"]["floor_effect"]
    assert "no_decay_floor_one" in effects["definitions"]["interaction"]
    bar = effects["bar"]
    assert (bar["margin"], bar["positive_seeds"], bar["seeds"]) == (10, 5, 6)
    assert "at least 10" in bar["rule"]
    assert bar["resamples"] == 10000


def test_the_denominator_is_a_gate_not_a_free_variable():
    gates = P.record()["gates"]
    assert set(gates) == set(P.GATES)
    assert "P is non-zero" in gates["G4_denominator"]
    assert "zero S_ever" in gates["G4_denominator"]
    assert "0.95/5" in gates["G3_treatments_live"]
    assert "1.0/1" in gates["G3_treatments_live"]


def test_the_decision_table_names_every_mechanism_outcome():
    rows = P.record()["decision_table"]
    verdicts = {row["verdict"] for row in rows}
    assert verdicts == set(P.VERDICTS)
    assert all(row["condition"] and row["reading"] and row["decision"] for row in rows)
    for row in rows:
        assert row["verdict"] in P.VERDICTS


@pytest.mark.parametrize("mutate", [
    lambda d: d.__setitem__("status", "FROZEN, RUN"),
    lambda d: d["authorisation"].__setitem__("granted", True),
    lambda d: d["runner"].__setitem__("cells_run", 1),
    lambda d: d["runner"].__setitem__("built", True),
    lambda d: d["design"].__setitem__("cells", 25),
    lambda d: d["design"].__setitem__("seeds", [20612201] + d["design"]["seeds"][1:]),
    lambda d: d["arms"].pop("no_decay"),
    lambda d: d["arms"]["floor_one"].__setitem__("read_floor", 2),
    lambda d: d["gates"].pop("G4_denominator"),
    lambda d: d["effects"].__setitem__("primary_endpoint", "A_W"),
    lambda d: d["decision_table"].pop(),
])
def test_a_changed_record_is_rejected(mutate):
    doc = copy.deepcopy(P.record())
    mutate(doc)
    page = P.render(doc)
    assert P.problems(doc, page), "the guard accepted a changed record"


def test_a_changed_page_is_rejected():
    page = P.PAGE.read_text(encoding="utf-8") + "\nchanged\n"
    assert P.problems(P.record(), page)
