"""The formation-provenance instrument: retired on 0.16.0, with the reason measured.

The retirement is not a note in a JSON file. ``run_controls()`` is still executable, and on the
shipped build it raises ``no prediction was formed`` with an empty formed-pair list -- so the
disposition is a fact about the engine that the suite re-checks. The origin classifier itself is
still live and is proved here on recorded transitions, because it takes a recorder's state and
needs no engine path.
"""
from __future__ import annotations
LAYER = "synthetic"  # benchmarks/test_layers.py: the module's execution layer

import json
from pathlib import Path

import pytest

from benchmarks import formation_provenance as fp
from benchmarks import provenance_trace as pt

REPO = Path(__file__).resolve().parent.parent
PAIR = ("willow", "teal")


def _retirement() -> dict:
    path = REPO / "docs" / "formation_provenance_retirement.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_the_controls_cannot_form_a_prediction_on_the_shipped_build():
    """The retirement reason is a measured fact about the engine, not a sentence about it."""
    with pytest.raises(AssertionError, match="no prediction was formed"):
        fp.run_controls()
    record = _retirement()
    assert record["measurable_on_shipped_build"] is False
    assert record["not_a_result"] is True
    assert "zero times by construction" in record["disposition"]


def test_the_origin_classifier_still_separates_the_three_reachable_classes():
    """Only the engine path that fed the classifier is gone; the classifier is not."""
    recorder = fp.FormationRecorder()

    recorder.transitions[PAIR] = {(1, 2): "world"}
    world = recorder.origins(PAIR)
    assert (world["status"], world["world"], world["self"], world["transitions"]) == \
        ("pair_world_attributed", 1, 0, 1)

    recorder.transitions[PAIR] = {(1, 2): "self"}
    self_ = recorder.origins(PAIR)
    assert (self_["status"], self_["world"], self_["self"], self_["transitions"]) == \
        ("pair_self_sourced", 0, 1, 1)

    recorder.transitions[PAIR] = {(1, 2): "world", (3, 4): "self"}
    mixed = recorder.origins(PAIR)
    assert (mixed["status"], mixed["world"], mixed["self"], mixed["transitions"]) == \
        ("pair_mixed", 1, 1, 2)

    # The classifier's answer must change with its input, not merely exist.
    recorder.transitions[PAIR] = {key: kind for key, kind in
                                  recorder.transitions[PAIR].items() if kind == "self"}
    assert recorder.origins(PAIR)["status"] == "pair_self_sourced"


def test_the_instrument_cannot_be_mistaken_for_the_ancestry_tracer():
    """Different question, different vocabulary: names must not be reused."""
    assert set(fp.ORIGIN_STATUSES).isdisjoint(set(pt.STATUSES))


def test_an_unrecorded_pair_is_reported_not_scored():
    origin = fp.FormationRecorder().origins(("willow", "teal"))
    assert origin["status"] == "pair_unattributed"
    assert origin["world"] == 0 and origin["self"] == 0
    assert origin["transitions"] == 0


def test_the_retirement_record_names_the_instrument_it_retires():
    record = _retirement()
    assert (REPO / record["instrument"]).exists()
    assert record["build"]["version"] == "0.16.0"
    assert record["no_cell_run"] is True
    assert record["what_it_does_not_do"].strip()
