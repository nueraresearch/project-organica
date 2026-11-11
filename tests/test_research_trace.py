"""The trace layer must join the three records without inventing anything, and its drift rules must fire.

The registry, the ledger and the bottleneck map are each validated on their own. What this
suite covers is the join: a trace may only name rows that exist, and every drift rule must reject
the pair it exists to catch -- a contradiction that became evidence, support that was removed, a
gate that opened without the status moving, and a gate that can never open. A check that only
ever passes is decoration, so each rule is shown failing on a constructed record.
"""
LAYER = "dry-run"  # benchmarks/test_layers.py: the module's execution layer

import json
import re

import pytest

from benchmarks import decision_graph as dg
from benchmarks import research_trace as rt


@pytest.fixture(scope="module")
def records():
    return rt.load_records()


def question(qid, status="future", outcome=None, prereq=None):
    q = {"id": qid, "kind": "research", "status": status, "question": "%s?" % qid}
    if outcome is not None:
        q["outcome"] = outcome
    if prereq is not None:
        q["prerequisites"] = list(prereq)
        q["blocked_by"] = list(prereq)
    return q


def claim(cid, status="ACTIVE", classification="HYPOTHESIS", supporting=(), contradicting=()):
    return {
        "claim_id": cid,
        "claim": "%s statement" % cid,
        "classification": classification,
        "status": status,
        "supporting_questions": list(supporting),
        "contradicting_questions": list(contradicting),
        "supporting_evidence": [],
        "scope_limitations": ["a stated limit"],
        "superseded_by": None,
        "withdrawn_reason": "",
    }


def codes(findings):
    return [f["code"] for f in findings]


def test_the_committed_records_do_not_drift():
    assert rt.main(["--check"]) == 0


def test_every_claim_traces_only_to_questions_the_registry_holds(records):
    reg, ledger, mapdoc = records
    known = {q["id"] for q in reg["questions"]}
    for c in ledger["claims"]:
        text = rt.trace_claim(c["claim_id"], reg, ledger, mapdoc)
        assert c["claim"] in text, c["claim_id"]
        assert "NOT IN THE REGISTRY" not in text, c["claim_id"]
        assert set(re.findall(r"\b(Q\d{3})\b", text)) <= known, c["claim_id"]


def test_every_question_traces_only_to_records_the_other_files_hold(records):
    reg, ledger, mapdoc = records
    known = {q["id"] for q in reg["questions"]}
    for q in reg["questions"]:
        text = rt.trace_question(q["id"], reg, ledger, mapdoc)
        assert q["question"] in text, q["id"]
        assert "NOT IN THE REGISTRY" not in text, q["id"]
        assert "NOT IN THE MAP" not in text, q["id"]
        assert set(re.findall(r"\b(Q\d{3})\b", text)) <= known, q["id"]


def test_an_active_claim_contradicted_by_a_supported_question_is_reported():
    reg = {"questions": [question("Q001", "closed", "SUPPORTED")]}
    ledger = {"claims": [claim("C001", supporting=["Q001"], contradicting=["Q001"])]}
    findings = rt.drift(reg, ledger)
    assert "claim-contradicted" in codes(findings), findings
    assert findings[0]["subject"] == "C001"


def test_an_active_claim_whose_support_was_retired_is_reported():
    reg = {"questions": [question("Q001", "retired")]}
    ledger = {"claims": [claim("C001", supporting=["Q001"])]}
    findings = rt.drift(reg, ledger)
    assert "claim-support-gone" in codes(findings), findings


def test_an_active_claim_whose_support_was_withdrawn_is_reported():
    reg = {"questions": [question("Q001", "closed", "WITHDRAWN")]}
    ledger = {"claims": [claim("C001", supporting=["Q001"])]}
    findings = rt.drift(reg, ledger)
    assert "claim-support-gone" in codes(findings), findings


def test_a_withdrawn_claim_is_never_reported_as_drifting():
    reg = {"questions": [question("Q001", "retired")]}
    ledger = {"claims": [claim("C001", status="WITHDRAWN", supporting=["Q001"])]}
    assert rt.drift(reg, ledger) == []


def test_a_future_question_whose_blocker_closed_is_reported():
    reg = {
        "questions": [
            question("Q001", "closed", "SUPPORTED"),
            question("Q002", prereq=["Q001"]),
        ]
    }
    findings = rt.drift(reg, {"claims": []})
    assert "blocker-stale" in codes(findings), findings
    assert findings[0]["subject"] == "Q002"


def test_a_settled_negative_does_not_unblock_a_future_question():
    """Closed-UNSUPPORTED settles the question against; it is not a gate that opened."""
    reg = {
        "questions": [
            question("Q001", "closed", "UNSUPPORTED"),
            question("Q002", prereq=["Q001"]),
        ]
    }
    assert rt.drift(reg, {"claims": []}) == []


def test_a_future_question_blocked_by_a_retired_question_is_reported():
    reg = {"questions": [question("Q001", "retired"), question("Q002", prereq=["Q001"])]}
    findings = rt.drift(reg, {"claims": []})
    assert "blocker-dead" in codes(findings), findings


def test_a_partially_met_gate_is_not_reported_as_open():
    reg = {
        "questions": [
            question("Q001", "closed", "SUPPORTED"),
            question("Q002", "open"),
            question("Q003", prereq=["Q001", "Q002"]),
        ]
    }
    assert rt.drift(reg, {"claims": []}) == []


def test_the_work_queue_separates_uncovered_questions_from_unblocked_ones():
    reg = {
        "questions": [
            question("Q001", "closed", "SUPPORTED"),
            question("Q002", "open"),
            question("Q003", "open"),
            question("Q004", prereq=["Q001"]),
            question("Q005", prereq=["Q002"]),
        ]
    }
    reg["questions"][2]["preregistrations"] = ["docs/PREREG.md"]
    reg["questions"][2]["evidence"] = ["docs/artifact.json"]
    queue = rt.work_queue(reg, {"claims": [claim("C001", contradicting=["Q002"])]})
    assert queue["unblocked"] == ["Q004"]
    assert queue["uncovered"] == ["Q002"]
    assert queue["contested"] == ["C001"]


def test_the_next_view_carries_the_pending_open_question(records):
    reg, ledger, _mapdoc = records
    page = rt.render_next(reg, ledger, dg.load())
    assert "DECISION-ADMISSION-STEP" in page
    assert "mechanism question" in page


def test_a_pending_decision_without_an_open_question_is_not_in_the_next_view(records):
    reg, ledger, _mapdoc = records
    decisions = json.loads(json.dumps(dg.load()))
    for decision in decisions["decisions"]:
        decision.pop("open_question", None)
    page = rt.render_next(reg, ledger, decisions)
    assert "mechanism question" not in page


def test_the_rendered_queue_names_the_question_and_its_gate():
    reg = {"questions": [question("Q001", "closed", "SUPPORTED"), question("Q002", prereq=["Q001"])]}
    text = rt.render_next(reg, {"claims": []})
    assert "Q002" in text and "Q001" in text


def test_an_unknown_identifier_is_rejected():
    assert rt.main(["--claim", "C999"]) == 1
    assert rt.main(["--question", "Q999"]) == 1


def test_check_writes_nothing():
    paths = [
        rt.REGISTRY,
        rt.LEDGER,
        rt.MAP,
        rt.ROOT / "docs" / "RESEARCH-QUESTION-REGISTRY.md",
        rt.ROOT / "docs" / "CLAIM-LEDGER.md",
        rt.ROOT / "docs" / "RESEARCH-DASHBOARD.md",
        rt.ROOT / "docs" / "RESEARCH-FINDINGS.md",
    ]
    before = {p: p.read_bytes() for p in paths}
    assert rt.main(["--check"]) == 0
    assert {p: p.read_bytes() for p in paths} == before


def test_check_mode_fails_on_a_drifting_record(tmp_path, monkeypatch):
    """The entry point reports the finding and exits 1, rather than only the pure function."""
    reg = json.loads(rt.REGISTRY.read_text(encoding="utf-8"))
    ledger = json.loads(rt.LEDGER.read_text(encoding="utf-8"))
    for q in reg["questions"]:
        if q["id"] == "Q016":
            q["status"], q["outcome"] = "closed", "SUPPORTED"
            q["answer"] = "closed for this test"
    reg_path = tmp_path / "registry.json"
    reg_path.write_text(json.dumps(reg), encoding="utf-8")
    monkeypatch.setattr(rt, "REGISTRY", reg_path)
    assert rt.main(["--check"]) == 1
