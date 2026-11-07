"""The bottleneck map is a claim-status artifact, so it must use the repository's status
vocabulary, name the check behind every row, and never claim more than one row has an
experiment behind it.

The two corrected rows are checked in both directions: the corrected wording must be present,
and the superseded wording must not come back.
"""

import json
import re
from pathlib import Path

from benchmarks import bottleneck_map as bm

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


def test_exactly_one_row_is_a_specified_experiment_and_it_allocates_a_registered_grid():
    body = _body()
    specified = [r for r in body["rows"] if r["study_specified"]]
    assert len(specified) == 1
    only = specified[0]
    assert only["candidate"] == "Density interaction"
    block = body["specified_experiment"]
    assert block["row"] == "Density interaction"
    assert block["registration"] == "docs/density_interaction_a2_prereg.json"
    results = ROOT / "docs" / "density_interaction_a2_result.json"
    assert block["run"] is results.exists(), (
        "the map's run flag must match the artifacts: no claim without a result, no "
        "result without the claim")
    registration = json.loads(
        (ROOT / block["registration"]).read_text(encoding="utf-8"))
    allocation = registration["allocation"]
    assert only["allocation"] == {"seeds": allocation["seeds"],
                                  "cells": allocation["judged_cells"],
                                  "thresholds": allocation["thresholds"],
                                  "bars": allocation["bars"]}
    assert all(r["allocation"] is None for r in body["rows"] if r is not only)
    design = json.loads(DENSITY.read_text(encoding="utf-8"))
    assert design["allocation"]["seeds"] == 0, (
        "the design record must still allocate nothing; the allocation is the registration's")
    # The design record's pre-run amendment is registered in A1; the map now points at A2,
    # whose registration names A1 as its held predecessor. The link is checked, not dropped.
    amendment = design["amendments"][0]
    assert amendment["registered_in"] == "docs/density_interaction_prereg.json"
    assert registration["held_predecessor"]["prereg"] == "DENSITY-INTERACTION-1"


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


def test_availability_and_generation_strategy_are_separate_rows():
    availability = _row("World-edge candidate availability")
    strategy = _row("Candidate-generation strategy (broader)")
    assert availability["status"] == ["Supported within the tested scope"]
    assert "112" in availability["check"] and "in memory" in availability["check"]
    assert strategy["status"] == ["Not established / not measured"]
    assert strategy["label"] == "unresolved"
    assert "generator" in strategy["does_not_say"]


def test_the_split_rule_is_stated():
    body = _body()
    assert "a row splits when the claim differs" in body["split_rule"]
    assert body["split_rule"] in _flat()


def _validate_labels(rows, defined, closed):
    """The guard the closed set exists for: a row outside the defined set is an error."""
    if closed:
        undefined = sorted({r["label"] for r in rows} - set(defined))
        if undefined:
            raise ValueError("undefined map label(s): " + ", ".join(undefined))
    return {r["label"] for r in rows}


def test_every_label_comes_from_the_closed_set():
    body = _body()
    vocabulary = body["vocabulary"]
    assert vocabulary["labels_are_closed"] is True
    defined = list(vocabulary["labels"])
    assert len(defined) == len(set(defined))
    assert set(defined) == set(body["label_meanings"])
    assert vocabulary["label_rule"].strip()
    used = _validate_labels(body["rows"], defined, vocabulary["labels_are_closed"])
    assert used <= set(defined)


def test_the_closed_set_rejects_a_label_it_does_not_define():
    body = _body()
    invented = [dict(body["rows"][0], label="probably fine")]
    try:
        _validate_labels(invented, body["vocabulary"]["labels"], True)
    except ValueError as exc:
        assert "probably fine" in str(exc)
    else:
        raise AssertionError("an undefined label was accepted")
    assert _validate_labels(invented, body["vocabulary"]["labels"], False) == {"probably fine"}


def test_the_document_says_the_label_set_is_closed():
    flat = _flat()
    assert "The label vocabulary is closed" in flat
    for label in _body()["vocabulary"]["labels"]:
        assert label in flat, label



def _mapping_statuses(sentence):
    return {part.strip() for part in sentence.split("+") if part.strip()}


def _statuses_used_by_rows(body, label):
    return {s for r in body["rows"] if r["label"] == label for s in r["status"]}


def _check_label_mappings(body):
    """A label's recorded mapping must be the mapping its rows actually carry."""
    for label, meaning in body["label_meanings"].items():
        recorded = _mapping_statuses(meaning["status"])
        assert recorded <= VOCAB, (label, recorded - VOCAB)
        observed = _statuses_used_by_rows(body, label)
        if recorded != observed:
            raise AssertionError(
                "label %r is recorded as mapping to %s but its rows carry %s"
                % (label, sorted(recorded), sorted(observed))
            )


def test_each_labels_recorded_mapping_is_the_mapping_its_rows_use():
    body = _body()
    _check_label_mappings(body)
    for label in body["label_meanings"]:
        assert _statuses_used_by_rows(body, label), "no row uses label %r" % label


def test_the_mapping_check_rejects_a_drifted_label():
    body = json.loads(json.dumps(_body()))
    body["label_meanings"]["weakened"]["status"] = (
        "Supported within the tested scope + Not established / not measured"
    )
    try:
        _check_label_mappings(body)
    except AssertionError as exc:
        assert "weakened" in str(exc)
    else:
        raise AssertionError("a drifted label mapping was accepted")
    _check_label_mappings(_body())


def test_the_document_says_the_mapping_is_asserted():
    flat = _flat()
    assert "A label's mapping is asserted, not just described." in flat
    assert "each label must map to exactly the set of statuses its rows carry" in flat


def test_the_label_table_is_generated_from_the_artifact():
    body = _body()
    text = DOC.read_text(encoding="utf-8")
    assert bm.BEGIN in text and bm.END in text
    assert bm.render_document(text, body) == text, (
        "the label table differs from the artifact; regenerate with "
        "python -m benchmarks.bottleneck_map --write"
    )


def test_the_generated_table_has_one_row_per_label():
    body = _body()
    rows = bm.render_table(body).splitlines()[2:]
    assert len(rows) == len(body["label_meanings"])
    for label in body["label_meanings"]:
        assert sum(1 for row in rows if row.startswith("| %s |" % label)) == 1, label


def test_the_generation_check_rejects_a_hand_edited_cell():
    body = _body()
    text = DOC.read_text(encoding="utf-8")
    drifted = text.replace("| weakened | evidence bears against",
                           "| weakened | evidence favours", 1)
    assert drifted != text, "the edit the check is supposed to notice did not happen"
    assert bm.render_document(drifted, body) != drifted
    stripped = text.replace(bm.BEGIN, "", 1).replace(bm.END, "", 1)
    try:
        bm.render_document(stripped, body)
    except ValueError as exc:
        assert "markers" in str(exc)
    else:
        raise AssertionError("a document with no markers was accepted")


def test_the_map_table_is_generated_from_the_artifact():
    body = _body()
    text = DOC.read_text(encoding="utf-8")
    assert bm.MAP_BEGIN in text and bm.MAP_END in text
    assert bm.render_document(text, body) == text, (
        "a table differs from the artifact; regenerate with "
        "python -m benchmarks.bottleneck_map --write"
    )


def test_the_map_table_has_one_row_per_candidate_and_exact_statuses():
    body = _body()
    rows = bm.render_map_table(body).splitlines()[2:]
    assert len(rows) == len(body["rows"])
    for row, line in zip(body["rows"], rows):
        assert line.startswith("| %s | %s |" % (row["candidate"], row["label"]))
        assert "| %s |" % " + ".join(row["status"]) in line
    assert "| Supported within the tested scope + Not established |" not in bm.render_map_table(body)


def test_the_check_column_is_kept_to_one_readable_sentence():
    for row in _body()["rows"]:
        assert len(row["check"]) <= bm.MAX_CHECK_CHARS, row["candidate"]
        assert "\n" not in row["check"], row["candidate"]
        assert "|" not in row["check"], row["candidate"]


def test_the_map_table_check_rejects_a_hand_edited_check():
    body = _body()
    text = DOC.read_text(encoding="utf-8")
    drifted = text.replace("all 112 true world edges were present in memory",
                           "all 112 true world edges were present in the graph", 1)
    assert drifted != text, "the edit the check is supposed to notice did not happen"
    assert bm.render_document(drifted, body) != drifted
