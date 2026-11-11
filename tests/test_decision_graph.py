"""The decision index must quote its documents, cover them completely, and be able to reject a paraphrase.

A hand-written index over prose documents is exactly the object rule 27 describes: a transcription
that can drift while looking like a sentence. The guard here is mechanical -- every prose claim in
``docs/decisions.json`` must appear verbatim in the document it is attributed to -- and every rule
below is exercised on input it exists to reject.
"""
LAYER = "dry-run"  # benchmarks/test_layers.py: the module's execution layer

import json
import shutil
from pathlib import Path

import pytest

from benchmarks import decision_graph as dg
from benchmarks import research_trace as rt

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "docs" / "research_question_registry.json"


@pytest.fixture(scope="module")
def records():
    return dg.load(), json.loads(REGISTRY.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ledger():
    return rt.load_records()[1]


def clone(data):
    return json.loads(json.dumps(data))


def test_the_index_validates_against_the_documents(records):
    data, reg = records
    report = dg.validate(data, reg)
    assert report["passed"], report["errors"]


def test_every_decision_document_is_indexed_exactly_once(records):
    data, _reg = records
    indexed = sorted("%s.md" % d["decision_id"] for d in data["decisions"])
    assert indexed == dg.decision_docs()


def test_the_page_is_current_and_check_writes_nothing():
    before = dg.DOC.read_bytes()
    assert dg.main(["--check"]) == 0
    assert dg.DOC.read_bytes() == before


def test_a_paraphrased_chosen_action_is_rejected(records):
    data, reg = records
    data = clone(data)
    data["decisions"][0]["chosen"] = ["We decided to stop using diversity-first admission."]
    report = dg.validate(data, reg)
    assert not report["passed"]
    assert any("verbatim" in e for e in report["errors"]), report["errors"]


def test_a_paraphrased_rejection_reason_is_rejected(records):
    data, reg = records
    data = clone(data)
    data["decisions"][0]["rejected"][0]["reason"] = "because it did not work"
    report = dg.validate(data, reg)
    assert not report["passed"]
    assert any("verbatim" in e for e in report["errors"]), report["errors"]


def test_an_empty_status_quote_is_rejected(records):
    data, reg = records
    data = clone(data)
    data["decisions"][0]["status_quote"] = ""
    report = dg.validate(data, reg)
    assert any("empty status_quote" in e for e in report["errors"]), report["errors"]


def test_a_missing_evidence_path_is_rejected(records):
    data, reg = records
    data = clone(data)
    data["decisions"][0]["evidence"].append("docs/no-such-artifact.json")
    report = dg.validate(data, reg)
    assert any("evidence path does not exist" in e for e in report["errors"]), report["errors"]


def test_an_unknown_status_is_rejected(records):
    data, reg = records
    data = clone(data)
    data["decisions"][0]["status"] = "MAYBE"
    report = dg.validate(data, reg)
    assert any("unknown status" in e for e in report["errors"]), report["errors"]


def test_an_index_entry_without_a_document_is_rejected(records):
    data, reg = records
    data = clone(data)
    data["decisions"][0]["decision_id"] = "DECISION-NOT-ON-DISK"
    report = dg.validate(data, reg)
    assert any("no such decision document" in e for e in report["errors"]), report["errors"]


def test_an_unindexed_document_is_rejected(records, tmp_path, monkeypatch):
    data, reg = records
    docs = tmp_path / "docs"
    docs.mkdir()
    for name in dg.decision_docs():
        shutil.copy(dg.DOCS / name, docs / name)
    (docs / "DECISION-UNINDEXED-TEST.md").write_text("# a decision nobody indexed\n", encoding="utf-8")
    monkeypatch.setattr(dg, "DOCS", docs)
    report = dg.validate(data, reg)
    assert any("DECISION-UNINDEXED-TEST" in e for e in report["errors"]), report["errors"]


def test_a_superseding_decision_that_does_not_exist_is_rejected(records):
    data, reg = records
    data = clone(data)
    data["decisions"][0]["superseded_by"] = "DECISION-GHOST"
    report = dg.validate(data, reg)
    assert any("superseded_by" in e for e in report["errors"]), report["errors"]


def test_an_adopted_decision_tallied_only_by_a_retired_question_is_reported(records):
    data, _reg = records
    reg = {
        "questions": [
            {"id": "Q001", "status": "retired", "question": "a retired question?", "decisions": ["DECISION-V2-SCOPE"]}
        ]
    }
    findings = dg.drift(data, reg)
    assert [f["code"] for f in findings] == ["decision-orphaned"], findings
    assert findings[0]["subject"] == "DECISION-V2-SCOPE"


def test_a_withdrawn_decision_is_never_reported_as_orphaned(records):
    data, _reg = records
    reg = {
        "questions": [
            {"id": "Q001", "status": "retired", "question": "a retired question?", "decisions": ["DECISION-ADMISSION-RULE"]}
        ]
    }
    assert dg.drift(data, reg) == []


def test_every_pending_decision_reaches_the_work_queue(records, ledger):
    """A decided-but-unlanded decision is work; the queue and the page must both carry it."""
    data, reg = records
    pending = dg.pending(data)
    assert pending, "no pending decision to check"
    assert rt.work_queue(reg, ledger, data)["pending_decisions"] == pending
    page = rt.render_next(reg, ledger, data)
    for decision_id in pending:
        assert decision_id in page, decision_id


def test_the_trace_quotes_the_decision_and_its_rejection(records):
    data, reg = records
    text = dg.trace("DECISION-STORE-TIME-ROLE-RECORD", data, reg)
    assert "B first. No engine change (A), and no withdrawal of Q028 (C)." in text
    assert "premature while B is untested and cheap" in text
    assert "Q028" in text


def test_an_unknown_decision_is_rejected(records):
    data, reg = records
    assert dg.trace("DECISION-GHOST", data, reg).startswith("no such decision")
    assert rt.main(["--decision", "DECISION-GHOST"]) == 1


def test_check_fails_on_a_stale_page(records, tmp_path, monkeypatch):
    data, reg = records
    stale = tmp_path / "DECISION-GRAPH.md"
    stale.write_text("an out-of-date page\n", encoding="utf-8")
    monkeypatch.setattr(dg, "DOC", stale)
    assert dg.main(["--check"]) == 1
    assert stale.read_text(encoding="utf-8") == "an out-of-date page\n"


def test_a_paraphrased_open_question_is_rejected(records):
    data, reg = records
    data = clone(data)
    entry = next(d for d in data["decisions"] if d["decision_id"] == "DECISION-ADMISSION-STEP")
    entry["open_question"] = "Does the band arm answer the question?"
    report = dg.validate(data, reg)
    assert not report["passed"]
    assert any("open_question" in error for error in report["errors"]), report["errors"]


def test_the_open_question_renders_with_the_status(records):
    data, reg = records
    page = dg.render(data, reg)
    assert "**Open question.**" in page
    assert "mechanism question" in page
    assert "unadjudicated" in page
