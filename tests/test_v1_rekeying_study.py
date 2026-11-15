"""The re-keying study is reproducible from its artifact, and it discloses where its validation stops."""
from __future__ import annotations

import json
from pathlib import Path

from benchmarks import v1_rekeying_study as study

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "docs" / "v1_rekeying_study.json"
DOC = ROOT / "docs" / "V1-REKEYING-STUDY.md"


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


def test_the_validation_gap_is_disclosed_not_hidden() -> None:
    doc = _doc()
    assert doc["validation"]["identities_match"] is True
    assert doc["validation"]["deaths_match"] is False
    assert "forgotten" in doc["validation"]["note"]
    assert "lower bound" in DOC.read_text(encoding="utf-8")


def test_the_rules_distinguish_the_two_keys_on_a_flip() -> None:
    detections = [(1, ("a", "b", "c"), 0.5), (2, ("a", "c", "b"), 0.5)]
    bearing = study.simulate(detections, lambda path: path)
    free = study.simulate(detections, study._free)
    assert bearing["identities"] == 2 and free["identities"] == 1
    assert bearing["reinforcements"] == 0 and free["reinforcements"] == 1
    assert free["strengths"] == {"a/b/c": 0.55}


def test_the_free_key_is_the_sorted_tag_set() -> None:
    assert study._free(("c", "a", "b", "c")) == ("a", "b", "c")
    assert study._free(("a", "b", "a")) == ("a", "b")
