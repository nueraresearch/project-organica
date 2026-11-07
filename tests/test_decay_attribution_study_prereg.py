"""The decay-attribution replication must stay unexecuted and frozen."""

import json

from benchmarks import decay_attribution_study_prereg as g


def _text():
    return g.DOC.read_text(encoding="utf-8")


def _registry():
    return json.loads(g.REGISTRY.read_text(encoding="utf-8"))


def test_the_committed_protocol_is_frozen_and_unexecuted():
    assert g.validate(_text(), _registry()) == []


def test_a_recorded_execution_is_rejected():
    found = g.validate(_text().replace("executions: 0", "executions: 1"), _registry())
    assert any("cannot be written after the run" in m for m in found), found


def test_an_existing_artifact_is_rejected():
    found = g.validate(_text(), _registry(), artifact_exists=True)
    assert any("post-hoc" in m for m in found), found


def test_a_moved_seed_is_rejected():
    found = g.validate(_text().replace("20301201", "20301299"), _registry())
    assert any("seed block" in m for m in found), found


def test_a_missing_question_is_rejected():
    found = g.validate(_text().replace("questions: Q029, Q030, Q031, Q032, Q036",
                                       "questions: Q029, Q030, Q031, Q032"), _registry())
    assert any("questions in the protocol" in m for m in found), found


def test_an_unassigned_question_that_now_exists_is_rejected():
    registry = _registry()
    registry["questions"].append({"id": "Q033", "preregistrations": []})
    found = g.validate(_text(), registry)
    assert any("scope statement is stale" in m for m in found), found


def test_an_edit_to_the_frozen_text_is_caught_by_the_digest():
    found = g.validate(_text().replace("60 world edges; 300", "60 world edges; 301"), _registry())
    assert any("protocol text moved" in m for m in found), found


def test_a_question_that_does_not_carry_the_protocol_is_rejected():
    registry = _registry()
    for question in registry["questions"]:
        if question["id"] == "Q030":
            question["preregistrations"] = []
    found = g.validate(_text(), registry)
    assert any("Q030 does not carry this pre-registration" in m for m in found), found


def test_a_missing_decision_bucket_is_rejected():
    found = g.validate(_text().replace("`REPLICATED_WITH_SHIFT`", "`REPLICATED_MAYBE`"),
                       _registry())
    assert any("no row for REPLICATED_WITH_SHIFT" in m for m in found), found


def test_check_mode_passes_and_writes_nothing():
    doc_before = g.DOC.read_bytes()
    registry_before = g.REGISTRY.read_bytes()
    assert g.main(["--check"]) == 0
    assert g.DOC.read_bytes() == doc_before
    assert g.REGISTRY.read_bytes() == registry_before
