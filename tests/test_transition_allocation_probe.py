"""The transition-allocation probe must stay tied to the band it claims to test."""
LAYER = "static"

import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import transition_allocation_probe as probe  # noqa: E402


def test_the_record_matches_the_source_band_and_its_own_arithmetic():
    assert probe.problems() == []
    art = json.loads(probe.ARTIFACT.read_text(encoding="utf-8"))
    assert art["not_a_result"] is True
    assert art["design"]["edges"] == probe.band_edges()
    assert [row["arm"] for row in art["arms"]] == list(probe.ARMS)


def test_a_dropped_band_edge_is_rejected():
    art = copy.deepcopy(json.loads(probe.ARTIFACT.read_text(encoding="utf-8")))
    art["design"]["edges"] = art["design"]["edges"][1:]

    assert probe.problems(art), "a record that no longer covers the source band must fail"


def test_the_relation_label_evidence_is_the_engine_construction():
    art = json.loads(probe.ARTIFACT.read_text(encoding="utf-8"))
    for arm in art["arms"]:
        evidence = arm["relation_evidence"]
        assert evidence["within_cycle_transition_in_cooc"] == 0
        assert evidence["rows"] > 0
        assert evidence["transition_rows"] + evidence["cooccurrence_rows"] == evidence["rows"]
        assert evidence["edges_labelled_both"] >= 0
    band = art["arms"][1]["relation_evidence"]["band"]
    assert [row["edge"] for row in band] == art["design"]["edges"]


def test_a_within_cycle_overlap_is_rejected():
    art = copy.deepcopy(json.loads(probe.ARTIFACT.read_text(encoding="utf-8")))
    art["arms"][0]["relation_evidence"]["within_cycle_transition_in_cooc"] = 1

    assert probe.problems(art), "a transition label inside the cooccurrence table must fail"


def test_a_served_count_that_contradicts_its_rows_is_rejected():
    art = copy.deepcopy(json.loads(probe.ARTIFACT.read_text(encoding="utf-8")))
    art["arms"][0]["band_served"] = art["arms"][0]["band_edges"] + 1

    assert probe.problems(art), "a summary that is not the per-edge sum must fail"
