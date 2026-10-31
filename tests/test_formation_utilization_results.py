"""The formation-utilization result document is a claim about one artifact.

The campaign artifact is machine-written; the result document is prose with
numbers in it.  These tests re-render the document from the artifact and fail
if a single character has drifted, parse the eighteen decision cells and check
them against the artifact's analysis, and prove that the check can fire.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from benchmarks import formation_utilization_results as report

ARTIFACT = Path("docs/formation_utilization.json")
DOCUMENT = Path("docs/formation_utilization_results.md")


def _artifact() -> dict:
    with open(ARTIFACT, encoding="utf-8") as fh:
        return json.load(fh)


def _document() -> str:
    return DOCUMENT.read_text(encoding="utf-8")


def test_the_document_is_what_the_artifact_renders():
    report.check(_document(), _artifact())


def test_every_decision_cell_matches_the_artifact():
    pattern = re.compile(
        r"\| (T[12]) / ([ABC]) \| (retention|transfer|revision) "
        r"\| ([+-]\d+\.\d{4}) \| \[([+-]\d+\.\d{4}), ([+-]\d+\.\d{4})\] "
        r"\| (win|tie|loss) \|")
    rows = pattern.findall(_document())
    assert len(rows) == 18
    artifact = _artifact()
    for task, arm, limb, mean, lo, hi, verdict in rows:
        cell = artifact["analysis"]["tasks"][task]["cells"][arm][limb]
        assert mean == f"{cell['mean']:+.4f}"
        assert lo == f"{cell['lo']:+.4f}"
        assert hi == f"{cell['hi']:+.4f}"
        assert verdict == cell["verdict"]


def test_the_verdict_is_the_pre_committed_mapping():
    artifact = _artifact()
    text = _document()
    for task in ("T1", "T2"):
        analysis = artifact["analysis"]["tasks"][task]
        assert analysis["mapping"]["label"] == report.EXPECTED_MAPPING
        assert analysis["summary_claim"] == report.EXPECTED_SUMMARY
        assert analysis["cells"]["B"]["transfer"]["verdict"] == "loss"
        assert analysis["cells"]["C"]["transfer"]["verdict"] == "loss"
        assert report.EXPECTED_MAPPING in text
        assert f"Summary claim: {report.EXPECTED_SUMMARY}" in text


def test_all_units_are_ready_and_no_audit_failed():
    artifact = _artifact()
    assert artifact["status"] == "complete"
    assert len(artifact["results"]) == 60
    assert len(artifact["seeds"]) == 30
    assert all(r["campaign_ready"] for r in artifact["results"])
    for result in artifact["results"]:
        for audit in result["audits"].values():
            assert audit.get("passed") is not False


def test_the_not_applicable_audits_are_the_committed_two():
    artifact = _artifact()
    for result in artifact["results"]:
        not_applicable = {key for key, audit in result["audits"].items()
                          if audit.get("passed") is None}
        if result["task"] == "T1":
            assert not_applicable == {"A3", "A6"}
        else:
            assert not_applicable == set()


def test_the_document_has_no_placeholders():
    assert not re.search(r"\{[A-Za-z_]", _document())


def test_the_checker_can_fail_on_a_changed_number():
    artifact = _artifact()
    text = _document()
    mutated = text.replace("| T1 / C | transfer | -0.0262 |",
                           "| T1 / C | transfer | -0.0261 |", 1)
    assert mutated != text
    with pytest.raises(AssertionError):
        report.check(mutated, artifact)


def test_the_checker_can_fail_on_a_changed_verdict():
    artifact = _artifact()
    text = _document()
    mutated = text.replace(report.EXPECTED_MAPPING, "utilization works", 1)
    assert mutated != text
    with pytest.raises(AssertionError):
        report.check(mutated, artifact)


def test_the_artifact_carries_the_provenance_correction():
    artifact = _artifact()
    assert artifact["engine_version"] == "0.10.0"
    assert artifact["command"].endswith(
        "run_campaign_resumable.py --seeds 30 --workers 10")
    assert "assembly_note" in artifact
    assert artifact["assembled_utc"]
    assert "No unit failed or was re-run" in artifact["runner_note"]
