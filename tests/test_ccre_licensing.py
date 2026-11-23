"""The licensing record must bound the run, and the bound must be able to fire."""
LAYER = "dry-run"  # benchmarks/test_layers.py: the module's execution layer

import copy
import json

from benchmarks import ccre_licensing as cl


def _record():
    return cl.load()


def test_the_record_validates():
    report = cl.validate(_record())
    assert report["passed"], report["errors"]


def test_every_licensed_question_is_in_the_registry():
    questions = cl.registry_questions()
    for row in _record()["licensed"]:
        assert row["id"] in questions, row["id"]


def test_at_least_one_question_may_be_answered_and_one_is_trace_derived():
    report = cl.validate(_record())
    assert report["tally"]["answers"] >= 1
    assert report["trace_derived"] >= 1


def test_the_page_matches_a_fresh_render():
    record = _record()
    report = cl.validate(record)
    assert cl.DOC.exists()
    assert cl.DOC.read_text(encoding="utf-8") == cl.render(record, report)


def test_a_settled_question_cannot_be_licensed_as_unsettled():
    record = copy.deepcopy(_record())
    row = next(r for r in record["licensed"] if r["tier"] in cl.SETTLING)
    closed = next(q for q in cl.registry_questions().values() if q["status"] in ("closed", "retired"))
    row["id"] = closed["id"]
    report = cl.validate(record)
    assert any("already answers" in message for message in report["errors"]), report["errors"]


def test_an_answer_with_one_decision_is_rejected():
    record = copy.deepcopy(_record())
    row = next(r for r in record["licensed"] if r["tier"] == "answers")
    row["decision_if_negative"] = row["decision_if_positive"]
    report = cl.validate(record)
    assert any(row["id"] in message and "same" in message for message in report["errors"]), report[
        "errors"
    ]


def test_a_record_without_a_trace_derived_question_is_rejected():
    record = copy.deepcopy(_record())
    for row in record["licensed"]:
        row.pop("trace_derived", None)
    report = cl.validate(record)
    assert any("trace-derived" in message for message in report["errors"]), report["errors"]


def test_nothing_refused_is_rejected():
    record = copy.deepcopy(_record())
    record["not_licensed"] = []
    report = cl.validate(record)
    assert any("refused" in message for message in report["errors"]), report["errors"]


def test_a_refused_question_that_is_also_licensed_is_rejected():
    record = copy.deepcopy(_record())
    licensed_id = record["licensed"][0]["id"]
    question = cl.registry_questions()[licensed_id]["question"]
    record["not_licensed"].append(
        {"question": question, "reason": "This reason is long enough to pass the thinness check."}
    )
    report = cl.validate(record)
    assert any("both licensed and refused" in message for message in report["errors"]), report["errors"]


def test_a_missing_prior_artifact_is_rejected():
    record = copy.deepcopy(_record())
    row = next(r for r in record["licensed"] if r.get("prior_artifact"))
    row["prior_artifact"] = "docs/does-not-exist.json"
    report = cl.validate(record)
    assert any("prior artifact does not exist" in message for message in report["errors"]), report[
        "errors"
    ]


def test_check_writes_nothing():
    record_before = cl.RECORD.read_bytes()
    doc_before = cl.DOC.read_bytes()
    assert cl.main(["--check"]) == 0
    assert cl.RECORD.read_bytes() == record_before
    assert cl.DOC.read_bytes() == doc_before


def test_the_registry_carries_the_new_questions():
    questions = cl.registry_questions()
    for qid in ("Q025", "Q026", "Q027", "Q028"):
        assert qid in questions, qid
        assert questions[qid]["status"] in ("open", "future"), qid
        assert questions[qid].get("outcome") is None, qid
