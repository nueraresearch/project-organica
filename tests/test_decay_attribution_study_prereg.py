"""The decay-attribution replication must stay unexecuted and frozen."""

import json

from benchmarks import decay_attribution_study_prereg as g


def _text():
    return g.DOC.read_text(encoding="utf-8")


def _registry():
    return json.loads(g.REGISTRY.read_text(encoding="utf-8"))


def test_the_committed_protocol_is_frozen_and_executed():
    artifact = {"protocol_digest": g.FROZEN_DIGEST, "label": "REPLICATED", "seeds": list(g.SEEDS)}
    assert g.validate(_text(), _registry(), artifact=artifact) == []
    unexecuted = _text().replace("executions: 1", "executions: 0", 1)
    found = g.validate(unexecuted, _registry())
    assert any("outcome is written" in m or "executions" in m for m in found), found


def test_a_recorded_execution_is_rejected():
    found = g.validate(_text().replace("executions: 0", "executions: 1"), _registry())
    assert any("cannot be written after the run" in m for m in found), found


def _artifact(label="REPLICATED"):
    return {"protocol_digest": g.FROZEN_DIGEST, "label": label, "seeds": list(g.SEEDS)}


def test_an_artifact_under_an_unexecuted_protocol_is_rejected():
    unexecuted = _text().replace("executions: 1", "executions: 0", 1)
    found = g.validate(unexecuted, _registry(), artifact=_artifact())
    assert any("executions" in m for m in found), found


def test_an_artifact_with_the_pinned_digest_and_label_is_accepted():
    text = _text().replace("executions: 0", "executions: 1", 1)
    text = text.replace("**Not yet written.**", "**REPLICATED**", 1)
    assert g.validate(text, _registry(), artifact=_artifact()) == []


def test_an_artifact_with_a_moved_digest_is_rejected():
    text = _text().replace("executions: 0", "executions: 1", 1)
    text = text.replace("**Not yet written.**", "**REPLICATED**", 1)
    found = g.validate(text, _registry(), artifact={
        "protocol_digest": "0" * 64, "label": "REPLICATED", "seeds": list(g.SEEDS)})
    assert any("digest" in m for m in found), found


def test_a_moved_seed_is_rejected():
    found = g.validate(_text().replace("20301201", "20301299"), _registry())
    assert any("seed block" in m for m in found), found


def test_a_missing_question_is_rejected():
    found = g.validate(_text().replace("questions: Q029, Q030, Q031, Q032, Q036",
                                       "questions: Q029, Q030, Q031, Q032"), _registry())
    assert any("questions in the protocol" in m for m in found), found


def test_an_amended_question_must_be_registered():
    registry = _registry()
    registry["questions"] = [x for x in registry["questions"] if x["id"] != "Q033"]
    found = g.validate(_text(), registry)
    assert any("Q033 was brought into scope but is not registered" in m for m in found), found


def test_an_amended_question_must_carry_the_protocol():
    registry = _registry()
    for x in registry["questions"]:
        if x["id"] == "Q034":
            x["preregistrations"] = []
    found = g.validate(_text(), registry)
    assert any("Q034 does not carry this pre-registration" in m for m in found), found


def test_an_out_of_scope_question_must_not_carry_the_protocol():
    registry = _registry()
    for x in registry["questions"]:
        if x["id"] == "Q035":
            x["preregistrations"] = [g.DOC.name]
    found = g.validate(_text(), registry)
    assert any("Q035 is out of this run's scope" in m for m in found), found


def test_an_edit_to_the_amendment_is_caught_by_its_own_digest():
    found = g.validate(_text().replace("at most 2 cycles", "at most 3 cycles"), _registry())
    assert any("amendment text moved" in m for m in found), found


def test_a_missing_amendment_is_rejected():
    found = g.validate(_text()[: _text().index("\n## 11.")], _registry())
    assert any("section 11" in m for m in found), found


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
