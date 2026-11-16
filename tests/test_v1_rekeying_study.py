"""The re-keying study is reproducible from its artifact, and both validations hold."""
from __future__ import annotations

import json
from pathlib import Path

from benchmarks import v1_rekeying_study as study

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "docs" / "v1_rekeying_study.json"
DOC = ROOT / "docs" / "V1-REKEYING-STUDY.md"
REPLICATION = ROOT / "docs" / "v1_rekeying_study_20900101.json"
TWO_SEEDS = ROOT / "docs" / "V1-REKEYING-TWO-SEEDS.md"


def _doc() -> dict:
    return json.loads(ART.read_text(encoding="utf-8"))


def test_the_page_is_rendered_from_the_artifact() -> None:
    assert DOC.read_text(encoding="utf-8") == study.render_doc(_doc())


def test_the_comparison_matches_the_two_simulations() -> None:
    doc = _doc()
    b, f, c = doc["direction_bearing"], doc["direction_free"], doc["comparison"]
    assert c["identities_saved"] == b["identities"] - f["identities"]
    assert c["deaths_bearing"] == b["deaths"] and c["deaths_free"] == f["deaths"]
    assert doc["observed"]["distinct_paths"] == b["identities"]
    assert doc["observed"]["distinct_node_sets"] == f["identities"]


def test_both_validations_hold_against_the_store() -> None:
    doc = _doc()
    assert doc["validation"]["identities_match"] is True
    assert doc["validation"]["deaths_match"] is True
    assert doc["validation"]["deaths_simulated"] == doc["validation"]["deaths_observed"]
    assert "186" in doc["validation"]["note"]
    assert "corrected" in doc["validation"]["note"] or "wrong" in doc["validation"]["note"]


def test_the_rules_distinguish_the_two_keys_on_a_flip() -> None:
    detections = [(1, ("a", "b", "c"), 0.5), (2, ("a", "c", "b"), 0.5)]
    bearing = study.simulate(detections, lambda path: path)
    free = study.simulate(detections, study._free)
    assert bearing["identities"] == 2 and free["identities"] == 1
    assert bearing["reinforcements"] == 0 and free["reinforcements"] == 1
    assert free["strengths"] == {"a/b/c": 0.55}


def test_reinforcement_adds_to_the_fresh_detection() -> None:
    detections = [(1, ("a", "b", "c"), 0.4), (2, ("a", "b", "c"), 0.2)]
    got = study.simulate(detections, lambda path: path)
    assert got["strengths"] == {"a/b/c": 0.25}


def test_the_replication_is_a_different_world_and_validates() -> None:
    first, second = _doc(), json.loads(REPLICATION.read_text(encoding="utf-8"))
    assert second["seed"] == 20900101
    assert second["observed"]["stored_identities"] != first["observed"]["stored_identities"]
    assert second["validation"]["identities_match"] is True
    assert second["validation"]["deaths_match"] is True


def test_the_direction_holds_on_both_seeds() -> None:
    for doc in (_doc(), json.loads(REPLICATION.read_text(encoding="utf-8"))):
        comparison = doc["comparison"]
        assert comparison["identities_saved"] > 0
        assert comparison["deaths_bearing"] > comparison["deaths_free"]
        assert comparison["flip_events"] > 0


def test_the_two_seed_page_is_rendered_from_both_artifacts() -> None:
    first = _doc()
    second = json.loads(REPLICATION.read_text(encoding="utf-8"))
    assert TWO_SEEDS.read_text(encoding="utf-8") == study.render_two_seed(first, second)


def test_the_free_key_is_the_sorted_tag_set() -> None:
    assert study._free(("c", "a", "b", "c")) == ("a", "b", "c")
    assert study._free(("a", "b", "a")) == ("a", "b")
