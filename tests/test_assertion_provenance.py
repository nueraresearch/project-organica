"""The provenance ledger must be reproducible and its classifier must be able to fail.

These are static controls: they read the committed ledger and exercise the pure classifier.
They do not replay a cell.
"""
LAYER = "static"

import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import assertion_provenance as provenance  # noqa: E402


def artifact() -> dict:
    return json.loads(provenance.ARTIFACT.read_text(encoding="utf-8"))


def test_the_ledger_reproduces_and_covers_all_26_edges():
    art = artifact()

    assert provenance.problems(art) == []
    assert art["not_a_result"] is True
    assert art["summary"]["edges"] == 26
    assert sum(art["summary"]["categories"].values()) == 26
    assert art["summary"]["recording_gap_windows"] == 0
    assert art["summary"]["categories"]["recording_gap"] == 0
    assert art["summary"]["categories"]["assertion_without_service"] == 0
    assert art["summary"]["alternate_source"] == 26
    assert art["summary"]["prediction_source"] == 0


def test_every_edge_has_a_source_and_a_consistent_category():
    art = artifact()

    for row in art["rows"]:
        assert row["assertion_sources"], row["edge"]
        assert row["category"] in provenance.CATEGORIES
        expected = provenance.classify(
            row["direct_replay_windows"],
            row["direct_committed_windows"],
            row["reverse_committed_windows"],
            row["assertion_sources"],
        )
        assert row["category"] == expected
        if row["category"] == "identity_mismatch":
            assert row["reverse_committed_windows"] > 0
        if row["category"] == "alternate_assertion_path":
            assert row["reverse_committed_windows"] == 0
            assert row["alternate_source"] is True


def test_all_four_classifier_buckets_can_fire():
    controls = {row["name"]: row for row in artifact()["controls"]}

    assert controls["recording_gap_control"]["category"] == "recording_gap"
    assert controls["identity_mismatch_control"]["category"] == "identity_mismatch"
    assert controls["alternate_path_control"]["category"] == "alternate_assertion_path"
    assert controls["prediction_residual_control"]["category"] == "assertion_without_service"


def test_a_tampered_category_is_reported():
    bad = copy.deepcopy(artifact())
    row = bad["rows"][0]
    row["category"] = ("alternate_assertion_path"
                       if row["category"] != "alternate_assertion_path"
                       else "identity_mismatch")

    assert provenance.problems(bad), "a category that disagrees with its fields must fail"


def test_a_tampered_summary_is_reported():
    bad = copy.deepcopy(artifact())
    bad["summary"]["categories"]["recording_gap"] += 1

    assert provenance.problems(bad), "a summary that disagrees with the rows must fail"


def test_a_removed_source_is_reported():
    bad = copy.deepcopy(artifact())
    bad["rows"][0]["assertion_sources"] = {}

    assert provenance.problems(bad), "an asserted edge with no source must fail"


def test_the_page_is_current():
    art = artifact()

    assert provenance.PAGE.read_text(encoding="utf-8") == provenance.render(art)
    assert "26" in provenance.PAGE.read_text(encoding="utf-8")
    assert "No recording gaps" in provenance.PAGE.read_text(encoding="utf-8")
