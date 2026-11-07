"""The decay falsifier must publish what the series says, and be able to fail."""

import json

from benchmarks import decay_falsifier as df


def _record():
    return json.loads(df.ARTIFACT.read_text(encoding="utf-8"))


def _series():
    raw = json.loads(df.RAW.read_text(encoding="utf-8"))
    row = next(r for r in raw["rows"] if r["colony"] == "FULL")
    return row["series"]


def test_the_recorded_counts_match_the_raw_series():
    record = _record()
    series = _series()
    assert record["theories"] == df.series_facts(series["theories"])
    assert record["beliefs"] == df.series_facts(series["beliefs"])


def test_the_recorded_verdict_follows_from_the_series():
    record = _record()
    series = _series()
    expected = df.verdict_for(series["theories"], series["beliefs"], int(record["cycles"]))
    assert record["verdict"] == expected["verdict"]
    assert record["falsifier_fired"] == expected["falsifier_fired"]


def test_the_result_describes_the_pinned_engine():
    record = _record()
    assert record["engine_pin_current"] is True
    assert record["engine_version"] == json.loads(
        (df.ROOT / "docs" / "engine_pin.json").read_text(encoding="utf-8")
    )["version"]


def test_verdict_falsified_when_theories_stay_live():
    result = df.verdict_for([2, 1, 3, 2], [1, 1, 1, 1], 4)
    assert result["verdict"] == "FALSIFIED"
    assert result["falsifier_fired"] is True


def test_verdict_reproduces_when_theories_die():
    result = df.verdict_for([3, 2, 0, 0], [4, 2, 0, 0], 4)
    assert result["verdict"] == "REPRODUCES"
    assert result["falsifier_fired"] is False


def test_verdict_intermittent_when_theories_return():
    result = df.verdict_for([3, 0, 0, 2], [4, 1, 0, 1], 4)
    assert result["verdict"] == "INTERMITTENT"
    assert result["falsifier_fired"] is False


def test_series_facts_count_cycles_not_items():
    facts = df.series_facts([0, 0, 2, 3, 0])
    assert facts == {"cycles": 5, "cycles_with_any": 2, "last_nonzero_cycle": 4, "at_end": 0}


def test_the_document_matches_a_fresh_render():
    record = _record()
    assert df.DOC.exists()
    assert df.DOC.read_text(encoding="utf-8") == df.render(record)


def test_a_verdict_that_does_not_follow_is_caught():
    record = _record()
    wrong = "FALSIFIED" if record["verdict"] != "FALSIFIED" else "REPRODUCES"
    found = df.problems(dict(record, verdict=wrong))
    assert any("verdict does not follow" in message for message in found), found


def test_a_stale_document_is_caught():
    record = _record()
    found = df.problems(dict(record, seed=-1))
    assert any("stale" in message for message in found), found


def test_the_artifact_itself_passes_its_own_check():
    assert df.problems(_record()) == []


def test_check_writes_nothing():
    artifact_before = df.ARTIFACT.read_bytes()
    doc_before = df.DOC.read_bytes()
    assert df.main(["--check"]) == 0
    assert df.ARTIFACT.read_bytes() == artifact_before
    assert df.DOC.read_bytes() == doc_before


def test_the_runner_records_the_status_and_never_scans_the_text(monkeypatch, tmp_path):
    from types import SimpleNamespace

    raw = tmp_path / "parts" / "FULL.json"
    harness = tmp_path / "harness.json"
    monkeypatch.setattr(df, "RAW", raw)
    monkeypatch.setattr(df, "HARNESS", harness)

    outputs = {
        1: "",   # fails, but prints nothing that says why
        0: "!! FULL produced no theories -- the reference arm is broken",  # says it, exits 0
    }

    def fake_run(cmd, **kwargs):
        return SimpleNamespace(returncode=fake_run.code, stdout=outputs[fake_run.code], stderr="")

    monkeypatch.setattr(df.subprocess, "run", fake_run)

    fake_run.code = 1
    assert df.run() == 1
    report = json.loads(harness.read_text(encoding="utf-8"))
    assert report["reference_arm_failed"] is True
    assert report["mode"] == "pre-fail-closed"
    assert report["reference_arm_problems"] is None
    assert "reference_arm_warning" not in report

    fake_run.code = 0
    assert df.run() == 0
    report = json.loads(harness.read_text(encoding="utf-8"))
    assert report["reference_arm_failed"] is False
    assert report["tail"][-1] == outputs[0]
    assert "reference_arm_warning" not in report


def test_a_status_the_harness_explained_is_attributed_from_the_artifact(monkeypatch, tmp_path):
    from types import SimpleNamespace

    raw = tmp_path / "parts" / "FULL.json"
    harness = tmp_path / "harness.json"
    raw.parent.mkdir(parents=True)
    raw.write_text(json.dumps({
        "rows": [],
        "reference_arm": {
            "check": "row_reference_problems",
            "problems": ["FULL held no theory in its final tenth of cycles -- the reference arm is dead"],
        },
    }), encoding="utf-8")
    monkeypatch.setattr(df, "RAW", raw)
    monkeypatch.setattr(df, "HARNESS", harness)
    monkeypatch.setattr(
        df.subprocess, "run",
        lambda cmd, **kwargs: SimpleNamespace(returncode=1, stdout="", stderr=""),
    )

    assert df.run() == 1
    report = json.loads(harness.read_text(encoding="utf-8"))
    assert report["mode"] == "fail-closed"
    assert report["reference_arm_failed"] is True
    assert report["reference_arm_problems"] == [
        "FULL held no theory in its final tenth of cycles -- the reference arm is dead"
    ]
    assert df.arm_status(report) == (1, True)


def test_the_arm_flag_is_derived_from_the_status_alone():
    # Fails, and prints nothing that names the reason.
    assert df.arm_status({"exit_code": 1, "tail": ["no message of any kind"]}) == (1, True)
    # Prints the warning, but exits successfully: the status is what decides.
    assert df.arm_status({"exit_code": 0, "tail": ["!! FULL produced no theories"]}) == (0, False)
    # A legacy report with no flag falls back to its own status.
    assert df.arm_status({"exit_code": 2}) == (2, True)
    # No status at all is not success.
    assert df.arm_status({"tail": []}) == (None, None)


def test_an_unexplained_failure_is_rejected_by_the_artifact_check():
    record = _record()
    found = df.problems(dict(record, harness_exit_code=1, harness_reference_arm_failed=True,
                             harness_reference_arm_problems=None))
    assert any("without a recorded reference-arm reason" in message for message in found), found


def test_an_explained_failure_must_match_the_series_it_judges():
    record = _record()
    wrong = dict(record, harness_exit_code=1, harness_reference_arm_failed=True,
                 harness_reference_arm_problems=["reference arm is dead"],
                 theories=dict(record["theories"], at_end=2))
    found = df.problems(wrong)
    assert any("not the condition this falsifier measures" in message for message in found), found


def test_a_flag_that_disagrees_with_the_status_is_rejected():
    record = _record()
    found = df.problems(dict(record, harness_exit_code=0, harness_reference_arm_failed=True))
    assert any("disagrees" in message for message in found), found
