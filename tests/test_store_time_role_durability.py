"""The durability probe must report each missing leg, and must reject a blind classifier."""

import json

from benchmarks import store_time_role_durability as probe


def _by_id():
    return {
        "schema_1": {"id": "schema_1", "source_role_id": "role_a", "target_role_id": "role_b"},
        "role_a": {"id": "role_a", "exemplars": ["willow", "teal"]},
        "role_b": {"id": "role_b", "exemplars": ["cedar", "maple"]},
    }


def _primed():
    return [{"id": "pred_1", "schema_prior": "schema_1"}]


def test_a_complete_record_is_recoverable():
    rows = probe.classify(_primed(), _by_id())
    assert [row["status"] for row in rows] == ["recoverable"]
    assert rows[0]["role_ids"] == ["role_a", "role_b"]


def test_each_missing_leg_has_its_own_status():
    no_schema = {k: v for k, v in _by_id().items() if k != "schema_1"}
    assert probe.classify(_primed(), no_schema)[0]["status"] == "R1_schema_absent"

    no_role = {k: v for k, v in _by_id().items() if k != "role_b"}
    assert probe.classify(_primed(), no_role)[0]["status"] == "R2_role_rows_absent"

    stripped = {k: v for k, v in _by_id().items() if k != "schema_1"}
    stripped["schema_1"] = {"id": "schema_1"}
    assert probe.classify(_primed(), stripped)[0]["status"] == "R3_schema_without_role_ids"


def test_the_decision_needs_every_leg_present():
    assert probe.decision_for([]) == "NOT_MEASURABLE"
    assert probe.decision_for(probe.classify(_primed(), _by_id())) == "NO_ENGINE_CHANGE"
    broken = {k: v for k, v in _by_id().items() if k != "role_a"}
    assert probe.decision_for(probe.classify(_primed(), broken)) == "ENGINE_CHANGE_NEEDED"


def test_a_zero_denominator_is_not_a_pass():
    summary = probe.summarise([])
    assert summary["measurable"] is False
    assert summary["share"] is None
    assert summary["decision"] == "NOT_MEASURABLE"


def test_the_controls_reject_a_classifier_that_can_never_fail():
    result = probe.self_test()
    assert result["all_passed"] is True
    blind = probe.run_controls(probe.always_recoverable)
    assert blind["all_passed"] is False
    assert sum(1 for row in blind["controls"].values() if not row["passed"]) >= 3


def test_the_artifact_passes_its_own_check():
    artifact = json.loads(probe.ARTIFACT.read_text(encoding="utf-8"))
    assert probe.problems(artifact) == []


def test_a_zero_denominator_scored_as_a_decision_is_rejected():
    artifact = json.loads(probe.ARTIFACT.read_text(encoding="utf-8"))
    empty = dict(artifact, measurement=dict(artifact["measurement"], denominator=0,
                                            measurable=False, decision="NO_ENGINE_CHANGE"),
                 traces=[])
    assert any("zero denominator" in message for message in probe.problems(empty))


def test_the_page_states_the_decision_without_placeholders():
    artifact = json.loads(probe.ARTIFACT.read_text(encoding="utf-8"))
    page = probe.render(artifact)
    assert artifact["measurement"]["decision"] in page
    assert "{" not in page and "}" not in page
