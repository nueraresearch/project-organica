"""The formation-provenance instrument, proven on synthetic controls only."""
from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

from benchmarks import formation_provenance as fp
from benchmarks import provenance_trace as pt


def test_every_control_matches_its_known_origin():
    result = fp.run_controls()
    assert result["all_passed"], result["controls"]
    for name, row in result["controls"].items():
        assert row["passed"], (name, row)


def test_the_origin_classes_can_all_be_reached():
    """A category no control reaches is a category that has not been tested."""
    result = fp.run_controls()["controls"]
    reached = {row["status"] for row in result.values()}
    for status in fp.ORIGIN_STATUSES:
        assert status in reached, f"{status} was never reached by a control"


def test_the_instrument_cannot_be_mistaken_for_the_ancestry_tracer():
    """Different question, different vocabulary: names must not be reused."""
    assert set(fp.ORIGIN_STATUSES).isdisjoint(set(pt.STATUSES))


def test_an_unrecorded_pair_is_reported_not_scored():
    origin = fp.FormationRecorder().origins(("willow", "teal"))
    assert origin["status"] == "pair_unattributed"
    assert origin["world"] == 0 and origin["self"] == 0
    assert origin["transitions"] == 0
