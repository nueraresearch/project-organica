"""A run the harness will not certify is void; the policy must be able to fail."""

import json

from benchmarks import decay_falsifier as df
from benchmarks import verdict_policy as vp


def _certified():
    decided = vp.decide("FALSIFIED", vp.certificate(False, []), "VOID_REFERENCE_DEAD")
    return decided


def _void():
    problems = ["FULL held no theory in its final tenth of cycles"]
    decided = vp.decide("REPRODUCES", vp.certificate(True, problems), "VOID_REFERENCE_DEAD")
    return decided


def test_a_certified_run_keeps_its_scientific_verdict():
    record = _certified()
    assert record["verdict"] == "FALSIFIED"
    assert record["certified"] is True
    assert record["observation"] is None
    assert record["gate"] is None
    assert vp.check(record, "VOID_REFERENCE_DEAD") == []


def test_an_uncertified_run_is_void_and_keeps_the_reading_as_an_observation():
    record = _void()
    assert record["verdict"] == "VOID_REFERENCE_DEAD"
    assert record["certified"] is False
    assert record["observation"] == "REPRODUCES"
    assert record["gate"]["problems"]
    assert vp.check(record, "VOID_REFERENCE_DEAD") == []


def test_a_verdict_on_an_uncertified_run_is_rejected():
    found = vp.check(dict(_void(), verdict="REPRODUCES"), "VOID_REFERENCE_DEAD")
    assert any("not VOID_REFERENCE_DEAD" in message for message in found), found


def test_a_void_without_a_recorded_reason_is_rejected():
    found = vp.check(dict(_void(), gate=None), "VOID_REFERENCE_DEAD")
    assert any("no reason" in message for message in found), found


def test_a_void_whose_observation_repeats_the_label_is_rejected():
    found = vp.check(dict(_void(), observation="VOID_REFERENCE_DEAD"),
                     "VOID_REFERENCE_DEAD")
    assert any("repeats the void label" in message for message in found), found


def test_a_certified_run_carrying_a_void_label_is_rejected():
    found = vp.check(dict(_certified(), verdict="VOID_REFERENCE_DEAD"),
                     "VOID_REFERENCE_DEAD")
    assert any("certified but the verdict is void" in message for message in found), found


def test_a_certified_run_carrying_a_gate_is_rejected():
    found = vp.check(dict(_certified(), gate={"problems": ["stale"]}), "VOID_REFERENCE_DEAD")
    assert any("carries a gate failure" in message for message in found), found


def test_a_record_with_no_certificate_is_rejected():
    found = vp.check({"verdict": "FALSIFIED"}, "VOID_REFERENCE_DEAD")
    assert any("no certificate" in message for message in found), found


def test_an_observation_on_a_certified_run_is_rejected():
    found = vp.check(dict(_certified(), observation="REPRODUCES"), "VOID_REFERENCE_DEAD")
    assert any("certified run" in message for message in found), found


def test_a_void_is_excluded_from_the_countable_verdicts():
    assert vp.scientific([_certified(), _void()]) == ["FALSIFIED"]


def test_the_falsifier_artifact_is_read_through_the_policy():
    record = json.loads(df.ARTIFACT.read_text(encoding="utf-8"))
    assert record["certified"] is False
    assert record["verdict"] == "VOID_REFERENCE_DEAD"
    assert record["observation"] == record["series_verdict"]
    assert vp.check(record, "VOID_REFERENCE_DEAD") == []


def test_the_certificate_must_agree_with_the_harness_flag():
    record = json.loads(df.ARTIFACT.read_text(encoding="utf-8"))
    broken = dict(record, certified=True, verdict="REPRODUCES", observation=None, gate=None)
    found = df.problems(broken)
    assert any("disagrees with the harness" in message for message in found), found
