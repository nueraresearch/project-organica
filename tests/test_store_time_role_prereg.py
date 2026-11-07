"""The scope guard must accept a scoped preregistration and reject each defect in it."""

from benchmarks import store_time_role_prereg as guard


def _record(**overrides):
    record = {
        "sections": list(guard.REQUIRED_SECTIONS),
        "scope": "engine",
        "applied": False,
        "bar_share": 0.90,
        "calibration_seed": 20261101,
        "confirmatory_block": (20272001, 20272024),
        "neutrality": ["1", "2", "3", "4"],
        "trace": ["1", "2", "3", "4"],
        "stop_condition": True,
        "buckets": {name: "decision %d" % index for index, name in enumerate(guard.BUCKETS)},
        "reserved_language": False,
    }
    record.update(overrides)
    return record


def test_a_scoped_unapplied_preregistration_passes():
    report = guard.validate(_record(), engine_applied=False)
    assert report["passed"], report["errors"]


def test_the_committed_document_parses_to_that_record():
    record = guard.parse(guard.DOC.read_text(encoding="utf-8"))
    assert record["scope"] == "engine"
    assert record["applied"] is False
    assert record["bar_share"] == 0.90
    assert record["calibration_seed"] == 20261101
    assert record["confirmatory_block"] == (20272001, 20272024)
    assert record["neutrality"] == ["1", "2", "3", "4"]
    assert record["trace"] == ["1", "2", "3", "4"]
    assert not record["reserved_language"]


def test_a_bar_this_document_chose_is_rejected():
    report = guard.validate(_record(bar_share=0.95), engine_applied=False)
    assert any("frozen P4 bar" in error for error in report["errors"]), report["errors"]


def test_a_calibration_seed_inside_the_confirmatory_block_is_rejected():
    report = guard.validate(_record(calibration_seed=20272010), engine_applied=False)
    assert any("inside CCRE-2's confirmatory block" in error for error in report["errors"])


def test_a_widened_confirmatory_block_is_rejected():
    report = guard.validate(_record(confirmatory_block=(20260000, 20280000)),
                            engine_applied=False)
    assert any("confirmatory block is" in error for error in report["errors"])


def test_losing_the_mutation_control_is_rejected():
    report = guard.validate(_record(neutrality=["1", "2", "3"]), engine_applied=False)
    assert any("mutation control" in error for error in report["errors"])


def test_losing_the_durability_leg_is_rejected():
    report = guard.validate(_record(trace=["1", "2", "3"]), engine_applied=False)
    assert any("durability leg" in error for error in report["errors"])


def test_a_missing_section_is_named():
    report = guard.validate(
        _record(sections=[s for s in guard.REQUIRED_SECTIONS
                          if s != "## 8. What this cannot establish"]),
        engine_applied=False,
    )
    assert any("missing sections" in error for error in report["errors"])


def test_two_buckets_with_one_decision_are_rejected():
    buckets = {name: "revert" for name in guard.BUCKETS}
    report = guard.validate(_record(buckets=buckets), engine_applied=False)
    assert any("same decision" in error for error in report["errors"])


def test_an_applied_engine_with_an_unapplied_scope_block_is_rejected():
    report = guard.validate(_record(), engine_applied=True)
    assert any("NOT APPLIED" in error for error in report["errors"])


def test_reserve_language_survives_as_a_failure():
    report = guard.validate(_record(reserved_language=True), engine_applied=False)
    assert any("held in reserve" in error for error in report["errors"])


def test_the_guard_can_fail_on_the_committed_document():
    record = guard.parse(guard.DOC.read_text(encoding="utf-8"))
    assert guard.main(["--check"]) == 0
    broken = dict(record, bar_share=0.99)
    assert not guard.validate(broken, engine_applied=False)["passed"]
