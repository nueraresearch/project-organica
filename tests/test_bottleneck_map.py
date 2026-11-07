"""The bottleneck map is a claim-status artifact, so it must use the repository's status
vocabulary, name the check behind every row, and never claim more than one row has an
experiment behind it.

The two corrected rows are checked in both directions: the corrected wording must be present,
and the superseded wording must not come back.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = ROOT / "docs" / "bottleneck_map.json"
DOC = ROOT / "docs" / "BOTTLENECK-MAP.md"
DENSITY = ROOT / "docs" / "world_density_design.json"

VOCAB = {
    "Supported within the tested scope",
    "Mixed / context-limited",
    "Reversed",
    "Not established / not measured",
}


def _body():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _flat():
    return " ".join(DOC.read_text(encoding="utf-8").split())


def _row(name):
    return next(r for r in _body()["rows"] if r["candidate"] == name)


def test_the_vocabulary_is_the_repositorys_four_statuses():
    body = _body()
    assert set(body["vocabulary"]["statuses"]) == VOCAB
    assert body["vocabulary"]["source"] == "papers/README.md"
    for row in body["rows"]:
        assert row["status"], row["candidate"]
        for status in row["status"]:
            assert status in VOCAB, (row["candidate"], status)


def test_no_row_claims_reversal_it_does_not_have():
    for row in _body()["rows"]:
        assert "Reversed" not in row["status"], row["candidate"]


def test_every_row_names_a_check_that_exists():
    for row in _body()["rows"]:
        assert row["check"].strip(), row["candidate"]
        assert row["evidence"], row["candidate"]
        for path in row["evidence"]:
            assert (ROOT / path).exists(), (row["candidate"], path)


def test_every_row_says_what_its_status_does_not_mean():
    for row in _body()["rows"]:
        assert row["does_not_say"].strip(), row["candidate"]
        assert row["would_change"].strip(), row["candidate"]


def test_the_unmeasured_rows_refuse_refutation():
    for name in ("Pool-structure moderation", "Loop-redundancy moderation"):
        row = _row(name)
        assert "not evidence of absence" in row["does_not_say"] or "refuted" in row["does_not_say"]


def test_decay_necessity_is_unresolved_not_not_supported():
    row = _row("Decay necessity for liveness")
    assert row["label"] == "unresolved"
    assert row["status"] == ["Not established / not measured"]
    assert "Neither direction was tested" in row["does_not_say"]
    assert 'Decay necessity: "not supported" became "unresolved"' in _flat()
    corrections = {c["row"]: c for c in _body()["corrections"]}
    assert corrections["Decay necessity for liveness"]["was"] == "not supported"


def test_selection_is_a_constraint_on_coverage_not_a_contributor():
    row = _row("Selection / allocation")
    assert "contributor" not in row["label"]
    assert "coverage" in row["label"] and "behavior untested" in row["label"]
    assert set(row["status"]) == {"Supported within the tested scope",
                                  "Not established / not measured"}
    assert "No cell has shown" in row["does_not_say"]
    corrections = {c["row"]: c for c in _body()["corrections"]}
    assert corrections["Selection / allocation"]["was"] == "demonstrated contributor"


def test_exactly_one_row_is_a_specified_experiment_and_it_allocates_nothing():
    body = _body()
    specified = [r for r in body["rows"] if r["study_specified"]]
    assert len(specified) == 1
    only = specified[0]
    assert only["candidate"] == "Density interaction"
    assert body["specified_experiment"]["row"] == "Density interaction"
    assert only["allocation"] == {"seeds": 0, "cells": 0, "thresholds": 0, "bars": 0}
    assert all(r["allocation"] is None for r in body["rows"] if r is not only)
    design = json.loads(DENSITY.read_text(encoding="utf-8"))
    assert {k: design["allocation"][k] for k in only["allocation"]} == only["allocation"]


def test_the_map_allocates_no_seeds_of_its_own():
    raw = ARTIFACT.read_text(encoding="utf-8")
    assert not re.search(r"\b20\d{6}\b", raw)
    assert not any("seed" in key for key in _body())


def test_the_document_quotes_the_artifact_and_has_no_placeholders():
    body = _body()
    flat = _flat()
    assert "a reading of the record, not new evidence" in flat
    for row in body["rows"]:
        assert row["candidate"] in flat, row["candidate"]
        assert row["label"] in flat, (row["candidate"], row["label"])
    assert f"Of the {len(body['rows'])} rows" in flat
    assert body["specified_experiment"]["row"] in flat
    assert not re.search(r"\{[a-z_]+\}", DOC.read_text(encoding="utf-8"))


def test_the_two_unread_rows_say_so():
    body = _body()
    prov = body["provenance"]
    assert prov["checked_rows"] == sum(1 for r in body["rows"] if r["read_for_this_record"])
    assert prov["owner_reading_rows"] == ["Pool-structure moderation",
                                          "Loop-redundancy moderation"]
    assert "carry the owner's reading" in _flat()


def test_every_label_is_defined_and_mapped():
    body = _body()
    labels = {r["label"] for r in body["rows"]}
    assert labels <= set(body["label_meanings"])
    for label, meaning in body["label_meanings"].items():
        assert meaning["means"].strip(), label
        assert meaning["status"].strip(), label


def test_the_label_status_split_is_documented():
    flat = _flat()
    assert "Labels are not statuses" in flat
    assert "a **map label** that is not a status" in flat
    for label in _body()["label_meanings"]:
        assert label in flat, label


def test_the_vocabulary_gap_is_named_rather_than_absorbed():
    gap = _body()["label_meanings"]["not supported"]["gap"]
    assert "no separate" in gap
    flat = _flat()
    assert 'no exact home for "not supported"' in flat
    assert "belongs to the owner" in flat


def test_candidate_generation_splits_presence_from_strategy():
    row = _row("Candidate generation")
    assert set(row["status"]) == {"Supported within the tested scope",
                                  "Not established / not measured"}
    assert "in memory" in row["check"]
    assert "generation strategy" in row["does_not_say"]
