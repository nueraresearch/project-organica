"""The bottleneck map is a claim-status artifact, so it must use the repository's status
vocabulary, name the check behind every row, and never claim more than one row has an
experiment behind it.

The two corrected rows are checked in both directions: the corrected wording must be present,
and the superseded wording must not come back.
"""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import copy
import json
import re
from pathlib import Path

import pytest

from benchmarks import bottleneck_map as bm
from benchmarks import provenance as prov

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


def test_every_row_carries_one_provenance_tag_and_the_counts_are_derived():
    body = _body()
    assert prov.check_map(body, ROOT) == []
    per_tag = prov.counts(body)
    assert sum(per_tag.values()) == len(body["rows"])
    assert per_tag[prov.OWNER_READING] == 2
    owner = [r["candidate"] for r in body["rows"] if r["provenance"] == prov.OWNER_READING]
    assert owner == ["Pool-structure moderation", "Loop-redundancy moderation"]
    assert body["provenance"]["module"] == "benchmarks/provenance.py"
    assert set(body["provenance"]["tags"]) == set(prov.TAGS)
    # The boolean and the hand-maintained list of names are both gone, from the artifact as
    # text, not just from the rows a reader happens to walk.
    raw = ARTIFACT.read_text(encoding="utf-8")
    assert "read_for_this_record" not in raw
    assert "owner_reading_rows" not in raw
    assert "checked_rows" not in raw


def test_the_document_prints_each_rows_provenance_and_the_derived_counts():
    body = _body()
    table = bm.render_map_table(body).splitlines()[2:]
    for row, line in zip(body["rows"], table):
        assert line.endswith("| %s |" % row["provenance"]), row["candidate"]
    flat = _flat()
    per_tag = prov.counts(body)
    for tag in prov.TAGS:
        if per_tag[tag]:
            assert "`%s`" % tag in flat, tag
    for row in body["rows"]:
        if row["provenance"] == prov.OWNER_READING:
            assert row["candidate"] in flat, row["candidate"]
    assert "carry the owner's reading" not in flat, "the hand-maintained prose list came back"


def test_the_provenance_check_rejects_a_retagged_row_and_stops_the_render():
    body = copy.deepcopy(_body())
    row = next(r for r in body["rows"] if r["provenance"] == prov.OWNER_READING)
    row["check"] += " (precision 0.3438)"
    assert [f["code"] for f in prov.check_map(body, ROOT)] == ["figure-without-reading"]
    with pytest.raises(ValueError):
        bm.render_document(DOC.read_text(encoding="utf-8"), body)
    # Same row, same words, tagged as what it now claims to be: accepted.
    row["provenance"] = prov.ARTIFACT_READ
    assert prov.check_map(body, ROOT) == []


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


def _ledger():
    return _body()["constraint_ledger"]


def test_the_constraint_ledger_is_a_five_column_decision_ledger():
    ledger = _ledger()
    assert ledger["state_vocabulary"] == ["open", "in-test", "retired"]
    assert ledger["retirement_rule"].strip()
    assert "pass, fail or inconclusive" in ledger["retirement_rule"]
    assert "attempt_invalid" in ledger["retirement_rule"]
    assert "untested" in ledger["retirement_rule"]
    assert "one constraint" not in ledger["purpose"]
    assert "zero is valid before the first test" in ledger["policy"]
    rows = ledger["rows"]
    assert rows
    for row in rows:
        assert row["state"] in ledger["state_vocabulary"]
        for field in ("constraint", "evidence", "hypothesis", "intervention", "decision_rule"):
            assert row[field].strip(), (row["constraint"], field)
    table = bm.render_constraint_table(_body()).splitlines()
    assert table[0] == ("| Constraint (state) | Evidence | Hypothesis | Intervention | "
                        "Decision rule |")
    assert len(table) == len(rows) + 2


def test_at_most_one_row_is_in_test_and_the_slot_holds_the_successor():
    rows = _ledger()["rows"]
    in_test = [row for row in rows if row["state"] == "in-test"]
    assert len(in_test) <= 1
    assert [row["constraint"] for row in in_test] == [
        "K1S - support-gated co-occurrence admission"], \
        "the successor entered test on 2026-11-20 under the owner's grant"
    assert all(not row["constraint"].lower().startswith(("governance", "provenance"))
               for row in rows)


def test_zero_in_test_rows_are_valid_before_the_first_test():
    body = copy.deepcopy(_body())
    rows = body["constraint_ledger"]["rows"]
    rows[:] = [row for row in rows if row["state"] != "in-test"]
    assert not [r for r in rows if r["state"] == "in-test"]
    assert bm.constraint_rows(body) == rows


def test_the_constraint_ledger_refuses_a_second_in_test_row():
    body = copy.deepcopy(_body())
    rows = body["constraint_ledger"]["rows"]
    rows.extend([copy.deepcopy(_in_test()), copy.deepcopy(_in_test())])
    with pytest.raises(ValueError, match="at most one in-test"):
        bm.constraint_rows(body)


def test_the_constraint_ledger_refuses_a_row_without_a_decision_rule():
    body = copy.deepcopy(_body())
    body["constraint_ledger"]["rows"][0]["decision_rule"] = ""
    with pytest.raises(ValueError, match="decision_rule"):
        bm.constraint_rows(body)


def test_the_constraint_table_is_generated_from_the_artifact():
    body = _body()
    text = DOC.read_text(encoding="utf-8")
    assert bm.CONSTRAINT_BEGIN in text and bm.CONSTRAINT_END in text
    assert bm.render_document(text, body) == text, (
        "the constraint ledger differs from the artifact; regenerate with "
        "python -m benchmarks.bottleneck_map --write"
    )
    assert "at most one row may be `in-test`" in _flat()
    assert "zero is valid before the first test" in _flat()
    assert "Retired rows remain in the ledger as history" in _flat()
    assert "attempt_invalid" in _flat()
    assert "untested, not refuted" in _flat()


def _k2():
    return next(r for r in _ledger()["rows"] if r["constraint"].startswith("K2"))


K1_REGISTRATION = "docs/constraint_registrations/K1-served-path.json"


def _in_test():
    """A synthetic in-test row.

    The artifact's one in-test row is the successor, so the refusal tests
    below need a row that is valid in shape independent of it.  It names the
    real K1 registration so the registration checks it exercises remain the
    committed ones.
    """
    return {
        "constraint": _in_test_registration()["constraint"],
        "evidence": "synthetic row for the refusal tests; not a ledger entry",
        "hypothesis": "synthetic",
        "intervention": "synthetic",
        "decision_rule": "synthetic",
        "state": "in-test",
        "registration": K1_REGISTRATION,
        "history": [{
            "from": "open",
            "to": "in-test",
            "date": "2026-11-19",
            "registration": "CONSTRAINT-K1-1",
        }],
    }


def _k2_registration():
    return json.loads((ROOT / _k2()["registration"]).read_text(encoding="utf-8"))


def _in_test_registration():
    return json.loads((ROOT / K1_REGISTRATION).read_text(encoding="utf-8"))


def test_k2_is_retired_as_an_invalid_attempt_not_a_failed_intervention():
    row = _k2()
    assert row["state"] == "retired"
    assert row["registration"] == "docs/constraint_registrations/K2-belief-revision.json"
    assert row["history"][-1] == {
        "from": "in-test",
        "to": "retired",
        "date": "2026-11-19",
        "registration": "CONSTRAINT-K2-1",
    }
    result = json.loads((ROOT / row["result"]).read_text(encoding="utf-8"))
    decision = json.loads((ROOT / row["decision"]).read_text(encoding="utf-8"))
    assert result["outcome"] == "attempt_invalid"
    assert result["hypothesis_status"] == "untested"
    assert result["criteria_read"] is False
    assert "untested" in decision["decision"].lower()
    assert result["registration"] == "CONSTRAINT-K2-1"
    assert decision["result"] == result["id"]
    registration = _k2_registration()
    assert registration["id"] == "CONSTRAINT-K2-1"
    assert registration["constraint"] == row["constraint"]
    assert bm.validate_constraint_row(row) == registration


def test_k1_is_retired_as_superseded_before_any_cell():
    row = next(r for r in _ledger()["rows"] if r["constraint"].startswith("K1"))
    assert row["state"] == "retired"
    assert row["registration"] == K1_REGISTRATION
    assert row["history"] == [
        {"from": "open", "to": "in-test", "date": "2026-11-19",
         "registration": "CONSTRAINT-K1-1"},
        {"from": "in-test", "to": "retired", "date": "2026-11-19",
         "registration": "CONSTRAINT-K1-1"},
    ]
    assert row["retirement_reason"].strip()
    result = json.loads((ROOT / row["result"]).read_text(encoding="utf-8"))
    decision = json.loads((ROOT / row["decision"]).read_text(encoding="utf-8"))
    assert result["outcome"] == "attempt_invalid"
    assert result["hypothesis_status"] == "untested"
    assert result["criteria_read"] is False
    assert result["cells_started"] == 0
    assert result["registration"] == "CONSTRAINT-K1-1"
    assert "untested" in decision["decision"].lower()
    assert "not refuted" in decision["decision"].lower()
    assert decision["result"] == result["id"]
    registration = _in_test_registration()
    assert registration["id"] == "CONSTRAINT-K1-1"
    assert registration["threshold_values"]["baseline_gap"] == -0.623961
    assert set(registration["threshold_values"]) == set(bm.THRESHOLD_KEYS)
    assert bm.validate_constraint_row(row) == registration


def test_an_in_test_row_without_a_registration_is_refused():
    row = copy.deepcopy(_in_test())
    row.pop("registration")
    with pytest.raises(ValueError, match="names no registration"):
        bm.validate_constraint_row(row)


def test_an_in_test_row_with_a_missing_registration_file_is_refused():
    row = copy.deepcopy(_in_test())
    row["registration"] = "docs/constraint_registrations/MISSING.json"
    with pytest.raises(ValueError, match="registration record does not exist"):
        bm.validate_constraint_row(row)


def test_an_in_test_row_without_history_is_refused():
    row = copy.deepcopy(_in_test())
    row.pop("history")
    with pytest.raises(ValueError, match="carries no transition history"):
        bm.validate_constraint_row(row)


def test_an_open_row_cannot_carry_a_registration_or_result():
    row = copy.deepcopy(next(r for r in _ledger()["rows"] if r["state"] == "open"))
    row["result"] = "RESULT-K2-1"
    with pytest.raises(ValueError, match="open but carries"):
        bm.validate_constraint_row(row)


def test_a_retired_row_cannot_skip_the_chain_or_its_records():
    row = copy.deepcopy(_in_test())
    row["history"].append({
        "from": "in-test", "to": "retired", "date": "2026-11-19",
        "registration": "CONSTRAINT-K1-1",
    })
    row["state"] = "retired"
    row["retirement_reason"] = "the intervention completed"
    with pytest.raises(ValueError, match="result record"):
        bm.validate_constraint_row(row)


def test_a_direct_open_to_retired_transition_is_refused():
    row = copy.deepcopy(_in_test())
    row["state"] = "retired"
    row["history"] = [{"from": "open", "to": "retired", "date": "2026-11-16"}]
    with pytest.raises(ValueError, match="invalid transition"):
        bm.validate_constraint_row(row)


def test_a_complete_retirement_chain_is_accepted(tmp_path):
    registration = copy.deepcopy(_in_test_registration())
    result = {
        "id": "RESULT-K2-1",
        "registration": "CONSTRAINT-K1-1",
        "outcome": "pass",
    }
    decision = {
        "id": "DECISION-K2-1",
        "result": "RESULT-K2-1",
        "decision": "RETIRE THE RETENTION-PRIORITY HYPOTHESIS",
    }
    (tmp_path / "registration.json").write_text(json.dumps(registration), encoding="utf-8")
    (tmp_path / "result.json").write_text(json.dumps(result), encoding="utf-8")
    (tmp_path / "decision.json").write_text(json.dumps(decision), encoding="utf-8")
    row = copy.deepcopy(_in_test())
    row.update({
        "state": "retired",
        "registration": "registration.json",
        "result": "result.json",
        "decision": "decision.json",
        "retirement_reason": "the intervention completed",
    })
    row["history"].append({
        "from": "in-test", "to": "retired", "date": "2026-11-19",
        "registration": "CONSTRAINT-K1-1",
    })
    assert bm.validate_constraint_row(row, tmp_path)["id"] == "CONSTRAINT-K1-1"
    body = copy.deepcopy(_body())
    body["constraint_ledger"]["rows"] = [row] + [
        other for other in body["constraint_ledger"]["rows"]
        if not other["constraint"].startswith(("K1", "K2"))]
    assert bm.constraint_rows(body, tmp_path)[0]["state"] == "retired"
    assert not [other for other in body["constraint_ledger"]["rows"]
                if other["state"] == "in-test"]
    result["registration"] = "CONSTRAINT-OTHER"
    (tmp_path / "result.json").write_text(json.dumps(result), encoding="utf-8")
    with pytest.raises(ValueError, match="result does not reference"):
        bm.validate_constraint_row(row, tmp_path)
    result["registration"] = "CONSTRAINT-K1-1"
    result["outcome"] = "pass"
    (tmp_path / "result.json").write_text(json.dumps(result), encoding="utf-8")
    decision["result"] = "RESULT-OTHER"
    (tmp_path / "decision.json").write_text(json.dumps(decision), encoding="utf-8")
    with pytest.raises(ValueError, match="decision does not reference"):
        bm.validate_constraint_row(row, tmp_path)
    decision["result"] = "RESULT-K2-1"
    (tmp_path / "decision.json").write_text(json.dumps(decision), encoding="utf-8")
    result["outcome"] = "VOID"
    (tmp_path / "result.json").write_text(json.dumps(result), encoding="utf-8")
    with pytest.raises(ValueError, match="outcome must be one of"):
        bm.validate_constraint_row(row, tmp_path)


def test_an_invalid_attempt_requires_untested_status_and_no_criterion(tmp_path):
    registration = copy.deepcopy(_in_test_registration())
    (tmp_path / "registration.json").write_text(json.dumps(registration), encoding="utf-8")
    result = {
        "id": "RESULT-K1-INVALID",
        "registration": "CONSTRAINT-K1-1",
        "outcome": "attempt_invalid",
        "hypothesis_status": "refuted",
        "criteria_read": False,
        "cells_started": 20,
    }
    decision = {
        "id": "DECISION-K1-INVALID",
        "result": "RESULT-K1-INVALID",
        "decision": "RETIRE AS UNTESTED",
    }
    row = copy.deepcopy(_in_test())
    row.update({
        "state": "retired",
        "registration": "registration.json",
        "result": "result.json",
        "decision": "decision.json",
        "retirement_reason": "the attempt was invalid",
    })
    row["history"].append({
        "from": "in-test", "to": "retired", "date": "2026-11-19",
        "registration": "CONSTRAINT-K1-1",
    })

    def write():
        (tmp_path / "result.json").write_text(json.dumps(result), encoding="utf-8")
        (tmp_path / "decision.json").write_text(json.dumps(decision), encoding="utf-8")

    write()
    with pytest.raises(ValueError, match="hypothesis_status"):
        bm.validate_constraint_row(row, tmp_path)
    result["hypothesis_status"] = "untested"
    result["criteria_read"] = True
    write()
    with pytest.raises(ValueError, match="criteria_read"):
        bm.validate_constraint_row(row, tmp_path)
    result["criteria_read"] = False
    decision["decision"] = "RETIRE AS REFUTED"
    write()
    with pytest.raises(ValueError, match="untested"):
        bm.validate_constraint_row(row, tmp_path)
    decision["decision"] = "RETIRE AS UNTESTED"
    write()
    assert bm.validate_constraint_row(row, tmp_path)["id"] == "CONSTRAINT-K1-1"


def test_an_unrun_retirement_must_say_the_hypothesis_is_not_refuted(tmp_path):
    """cells_started 0 is a withdrawal, so the wording cannot be a null result."""
    registration = copy.deepcopy(_in_test_registration())
    (tmp_path / "registration.json").write_text(json.dumps(registration), encoding="utf-8")
    result = {
        "id": "RESULT-K1-UNRUN",
        "registration": "CONSTRAINT-K1-1",
        "outcome": "attempt_invalid",
        "hypothesis_status": "untested",
        "criteria_read": False,
        "cells_started": 0,
    }
    decision = {
        "id": "DECISION-K1-UNRUN",
        "result": "RESULT-K1-UNRUN",
        "decision": "RETIRE AS UNTESTED",
    }
    row = copy.deepcopy(_in_test())
    row.update({
        "state": "retired",
        "registration": "registration.json",
        "result": "result.json",
        "decision": "decision.json",
        "retirement_reason": "withdrawn before a grant",
    })
    row["history"].append({
        "from": "in-test", "to": "retired", "date": "2026-11-19",
        "registration": "CONSTRAINT-K1-1",
    })

    def write():
        (tmp_path / "result.json").write_text(json.dumps(result), encoding="utf-8")
        (tmp_path / "decision.json").write_text(json.dumps(decision), encoding="utf-8")

    write()
    with pytest.raises(ValueError, match="not refuted"):
        bm.validate_constraint_row(row, tmp_path)
    decision["decision"] = "RETIRE AS UNTESTED AND NOT REFUTED"
    write()
    assert bm.validate_constraint_row(row, tmp_path)["id"] == "CONSTRAINT-K1-1"
    result["cells_started"] = -1
    write()
    with pytest.raises(ValueError, match="cells_started"):
        bm.validate_constraint_row(row, tmp_path)


def test_an_invalid_attempt_must_record_cells_started(tmp_path):
    """The field is required, so an unrun retirement cannot dodge the wording check."""
    registration = copy.deepcopy(_in_test_registration())
    (tmp_path / "registration.json").write_text(json.dumps(registration), encoding="utf-8")
    result = {
        "id": "RESULT-K1-NOFIELD",
        "registration": "CONSTRAINT-K1-1",
        "outcome": "attempt_invalid",
        "hypothesis_status": "untested",
        "criteria_read": False,
    }
    decision = {
        "id": "DECISION-K1-NOFIELD",
        "result": "RESULT-K1-NOFIELD",
        "decision": "RETIRE AS UNTESTED",
    }
    row = copy.deepcopy(_in_test())
    row.update({
        "state": "retired",
        "registration": "registration.json",
        "result": "result.json",
        "decision": "decision.json",
        "retirement_reason": "withdrawn before a grant",
    })
    row["history"].append({
        "from": "in-test", "to": "retired", "date": "2026-11-19",
        "registration": "CONSTRAINT-K1-1",
    })
    (tmp_path / "result.json").write_text(json.dumps(result), encoding="utf-8")
    (tmp_path / "decision.json").write_text(json.dumps(decision), encoding="utf-8")
    with pytest.raises(ValueError, match="cells_started"):
        bm.validate_constraint_row(row, tmp_path)


SUCCESSOR_DRAFT = "docs/constraint_registrations/assertion-provenance.json"


def test_the_successor_draft_carries_the_ledger_keys_and_both_gates():
    draft = json.loads((ROOT / SUCCESSOR_DRAFT).read_text(encoding="utf-8"))
    assert draft["id"] == "CONSTRAINT-ASSERTION-PROVENANCE-1"
    assert "NOT REGISTERED" in draft["status"]
    values = draft["threshold_values"]
    assert set(values) == set(bm.THRESHOLD_KEYS)
    assert (values["fail_below_improvement"] <= values["inconclusive_min_improvement"]
            <= values["inconclusive_max_improvement"] <= values["pass_min_improvement"])
    # The two gates the draft exists to carry.
    assert "0.95" in draft["recall_guard"]
    assert "returned-edge-set" in draft["liveness_gate"] and "VOID" in draft["liveness_gate"]
    # The controls that stop it passing by deletion or by peeking at the answer.
    rules = " ".join(control["rule"] for control in draft["controls"])
    assert "truncation" in rules.lower() and "gold" in rules
    # Its pressure test withdrew it, and a withdrawn draft still owns no ledger row.
    assert draft["pressure_test"]["outcome"].startswith("withdrawn")
    assert draft["pressure_test"]["cells"] == 0
    assert not [row for row in _ledger()["rows"]
                if "ASSERTION-PROVENANCE" in str(row.get("registration"))]


def test_k2_records_the_cells_its_block_started():
    """The backfilled count is the artifact's own record count, not a typed 20."""
    row = _k2()
    result = json.loads((ROOT / row["result"]).read_text(encoding="utf-8"))
    artifact = json.loads((ROOT / "docs" / "phase_k_k2_results.json").read_text(encoding="utf-8"))
    assert result["cells_started"] == len(artifact["records"]) == 20
