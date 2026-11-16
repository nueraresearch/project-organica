"""The runner is built, and every path that could produce a result is exercised without a world."""
import copy
import json

import pytest

from benchmarks import v2_first_cell_report as report
from benchmarks import v2_first_cell_runner as runner


def test_check_passes_without_running_a_world():
    assert runner.main(["--check"]) == 0


def test_run_refuses_while_the_authorisation_is_pending(tmp_path):
    allowed, reason = runner.authorisation()
    if allowed:
        pytest.skip("the owner has signed; the pre-cell refusal no longer applies")
    out = tmp_path / "result.json"
    assert runner.main(["--run", "--out", str(out)]) == 1
    assert not out.exists()
    assert runner.AUTHORISATION in reason


def test_every_derived_label_assembles_into_the_report_shape():
    for label in ("PASS", "BOOKKEEPING", "REVERSAL"):
        fixture = report._fixture(label)
        result = runner.assemble(fixture["per_seed"], runner.synthetic_gates(), fixture["control"])
        assert result["outcome"] == label
        assert report.validate(result) == []
        assert f"**Outcome:** `{label}`" in report.render(result)


def test_a_failed_gate_voids_before_any_seed():
    result = runner.assemble(
        runner.unmeasured_rows("not run: gate A3 failed"),
        runner.synthetic_gates(failing=("A3",)),
        runner.no_control("the gate record did not pass"),
    )
    assert result["outcome"] == "VOID"
    assert result["interval"] is None
    assert "A3_MUTATION" in result["void"]["codes"]
    text = report.render(result)
    assert "**Outcome:** `VOID`" in text
    assert "No interval is reported" in text


def test_seven_measurable_seeds_assemble_as_a_measurable_void():
    rows = copy.deepcopy(report._fixture("PASS")["per_seed"])
    for row in rows[7:]:
        row["measurable"] = False
        row["exclusion"] = "no held-out positives"
        for field in ("d", "d_B", "beta"):
            row.pop(field)
    result = runner.assemble(rows, runner.synthetic_gates(), report._fixture("PASS")["control"])
    assert result["outcome"] == "VOID"
    assert "SEEDS_MEASURABLE" in result["void"]["codes"]
    assert "7 of 10" in result["void"]["detail"]


def test_a_missing_gate_record_is_refused(tmp_path):
    with pytest.raises(runner.GateError, match="A1-A5"):
        runner.load_gates(tmp_path / "no-gates.json")


def test_a_gate_record_needs_exactly_five_gates_and_evidence(tmp_path):
    record = tmp_path / "gates.json"
    record.write_text('{"gates": {"A1": {"status": "PASS", "evidence": "x"}}}', encoding="utf-8")
    with pytest.raises(runner.GateError, match="exactly A1-A5"):
        runner.load_gates(record)

    full = {"gates": {gate: {"status": "PASS", "evidence": ""} for gate in report.GATE_IDS}}
    record.write_text(__import__("json").dumps(full), encoding="utf-8")
    with pytest.raises(runner.GateError, match="needs its evidence"):
        runner.load_gates(record)


def test_the_pins_and_the_seed_block_are_the_declared_ones():
    assert runner.pins() == []
    assert report.declared_seeds() == list(range(20910101, 20910111))


def test_the_a1_cell_stream_accepts_a_clean_stream():
    stats = runner.a1_cell_stream(
        20910101,
        {"detections": [(1, ("alpha", "beta")), (2, ("beta", "alpha"))]},
    )
    assert stats["detections"] == 2
    assert stats["keys"] == 1
    assert stats["node_sets"] == 1
    assert stats["mixed"] == 0
    assert stats["flips"] == 0


def test_the_a1_cell_stream_rejects_a_key_that_mixes_node_sets(monkeypatch):
    monkeypatch.setattr(runner.readout, "canonical", lambda path: ("mixed",))
    with pytest.raises(runner.A1StreamError) as error:
        runner.a1_cell_stream(
            20910101,
            {"detections": [(1, ("alpha", "beta")), (2, ("gamma", "delta"))]},
        )
    assert "mixed" in str(error.value)


def test_an_a1_cell_stream_failure_voids_before_an_arm(monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "authorisation", lambda: (True, "authorised"))
    monkeypatch.setattr(runner, "pins", lambda: [])
    monkeypatch.setattr(runner, "load_gates", lambda path: runner.synthetic_gates())

    def fail_a1():
        raise runner.A1StreamError(20910101, ["one key mixed distinct node sets"])

    def arms_ran(*args, **kwargs):
        raise AssertionError("an arm was scored after the A1 cell-stream check failed")

    monkeypatch.setattr(runner, "cell_streams", fail_a1)
    monkeypatch.setattr(runner.readout, "arms_for", arms_ran)

    monkeypatch.setattr(runner, "RUN", tmp_path / "default-run.json")
    monkeypatch.setattr(runner, "OUT", tmp_path / "default-result.json")
    monkeypatch.setattr(runner, "MANIFEST", tmp_path / "default-manifest.json")
    monkeypatch.setattr(runner, "RAW_LOG", tmp_path / "default-log.json")
    out = tmp_path / "result.json"
    assert runner.run(control_path=tmp_path / "no-control.json", out=out,
                      marker_path=tmp_path / "run.json", manifest_path=tmp_path / "manifest.json",
                      log_path=tmp_path / "run-log.json") == 0
    result = json.loads(out.read_text(encoding="utf-8"))
    assert result["outcome"] == "VOID"
    assert result["gates"]["A1"]["status"] == "FAIL"
    assert "A1_CANONICALISATION" in result["void"]["codes"]
    assert result["interval"] is None
    assert all(row["measurable"] is False for row in result["per_seed"])
    assert "A1 failed on seed 20910101" in result["void"]["detail"]
    raw = json.loads((tmp_path / "run-log.json").read_text(encoding="utf-8"))
    assert raw["seeds"] and all(seed["arms"] is None for seed in raw["seeds"])


def test_a_clean_cell_stream_is_added_to_the_a1_evidence_before_scoring(monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "authorisation", lambda: (True, "authorised"))
    monkeypatch.setattr(runner, "pins", lambda: [])
    monkeypatch.setattr(runner, "load_gates", lambda path: runner.synthetic_gates())
    seeds = report.declared_seeds()
    streams = [
        {
            "seed": seed,
            "data": {"tags": [], "detections": []},
            "a1": {"seed": seed, "cycles": 120, "detections": 0, "keys": 0,
                   "node_sets": 0, "mixed": 0, "flips": 0},
        }
        for seed in seeds
    ]
    calls = []

    def fake_arms_for(tags, detections, cycles):
        calls.append(cycles)
        return {
            "arms": {
                "A": {"beta": None, "log_loss": 0.5, "scored": 10},
                "B": {"beta": 1, "log_loss": 0.5005, "scored": 10},
                "C": {"beta": 2, "log_loss": 0.4995, "scored": 10},
            }
        }

    def streams_after_manifest():
        initial = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
        assert initial["status"] == "STARTED"
        return streams

    monkeypatch.setattr(runner, "cell_streams", streams_after_manifest)
    monkeypatch.setattr(runner.readout, "arms_for", fake_arms_for)
    monkeypatch.setattr(runner, "RUN", tmp_path / "default-run.json")
    monkeypatch.setattr(runner, "OUT", tmp_path / "default-result.json")
    monkeypatch.setattr(runner, "MANIFEST", tmp_path / "default-manifest.json")
    monkeypatch.setattr(runner, "RAW_LOG", tmp_path / "default-log.json")

    out = tmp_path / "result.json"
    log = tmp_path / "run-log.json"
    assert runner.run(control_path=tmp_path / "no-control.json", out=out,
                      marker_path=tmp_path / "run.json", manifest_path=tmp_path / "manifest.json",
                      log_path=log) == 0
    result = json.loads(out.read_text(encoding="utf-8"))
    assert calls == [120] * 10
    assert result["gates"]["A1"]["status"] == "PASS"
    assert "Cell-stream check: 10 seeds replayed" in result["gates"]["A1"]["evidence"]
    assert report.validate(result) == []
    raw = json.loads(log.read_text(encoding="utf-8"))
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert raw["kind"] == "v2_first_cell_run_log"
    assert len(raw["seeds"]) == 10
    assert raw["seeds"][0]["arms"]["A"]["log_loss"] == 0.5
    assert raw["seeds"][0]["arms"]["B"]["log_loss"] == 0.5005
    assert raw["seeds"][0]["arms"]["C"]["log_loss"] == 0.4995
    assert result["per_seed"][0]["d"] == round(0.4995 - 0.5, 6)
    assert manifest["status"] == "COMPLETED"
    assert manifest["artifacts"]["raw_log"] == str(log)
    assert manifest["result_sha256"] == runner.hashlib.sha256(out.read_bytes()).hexdigest()
    assert manifest["raw_log_sha256"] == runner.hashlib.sha256(log.read_bytes()).hexdigest()
    assert manifest["inputs"]["runner"]["sha256"] == runner.hashlib.sha256(
        runner.Path(runner.__file__).read_bytes()).hexdigest()
    assert manifest["inputs"]["report"]["sha256"] == runner.hashlib.sha256(
        (runner.REPO / "benchmarks" / "v2_first_cell_report.py").read_bytes()).hexdigest()
    assert manifest["python"]["version_info"][:2] == list(runner.sys.version_info[:2])


def test_a_run_with_no_marker_or_artifact_is_unrun(tmp_path):
    state = runner.run_status(
        marker_path=tmp_path / "run.json", out=tmp_path / "result.json",
        manifest_path=tmp_path / "manifest.json", log_path=tmp_path / "log.json",
    )
    assert state["status"] == "UNRUN"
    assert state["started"] is False
    assert state["retry_allowed"] is False
    assert state["policy"] == runner.RUNTIME_POLICY


def test_a_started_marker_is_void_and_is_never_retried(tmp_path):
    marker = tmp_path / "run.json"
    marker.write_text('{"status": "STARTED"}', encoding="utf-8")
    state = runner.run_status(
        marker_path=marker, out=tmp_path / "result.json",
        manifest_path=tmp_path / "manifest.json", log_path=tmp_path / "log.json",
    )
    assert state["status"] == "VOID"
    assert state["started"] is True
    assert state["retry_allowed"] is False
    assert "STARTED" in state["detail"]
    assert "never retried" in state["detail"]
    with pytest.raises(runner.RunGuardError, match="never retried"):
        runner.run_guard(marker_path=marker, out=tmp_path / "result.json",
                         manifest_path=tmp_path / "manifest.json", log_path=tmp_path / "log.json")


def test_a_completed_attempt_is_audit_only(tmp_path):
    marker = tmp_path / "run.json"
    marker.write_text('{"status": "COMPLETED"}', encoding="utf-8")
    out = tmp_path / "result.json"
    manifest = tmp_path / "manifest.json"
    log = tmp_path / "log.json"
    for path in (out, manifest, log):
        path.write_text("{}", encoding="utf-8")
    state = runner.run_status(marker_path=marker, out=out, manifest_path=manifest, log_path=log)
    assert state["status"] == "COMPLETED"
    assert state["started"] is True
    assert state["retry_allowed"] is False
    assert "audit-only" in state["detail"]


def test_a_completed_marker_without_its_artifacts_is_void(tmp_path):
    marker = tmp_path / "run.json"
    marker.write_text('{"status": "COMPLETED"}', encoding="utf-8")
    state = runner.run_status(
        marker_path=marker, out=tmp_path / "result.json",
        manifest_path=tmp_path / "manifest.json", log_path=tmp_path / "log.json",
    )
    assert state["status"] == "VOID"
    assert state["retry_allowed"] is False
    assert "unfinished" in state["detail"]


def test_artifacts_without_a_marker_are_void_and_unfinished(tmp_path):
    out = tmp_path / "result.json"
    out.write_text("{}", encoding="utf-8")
    state = runner.run_status(
        marker_path=tmp_path / "run.json", out=out,
        manifest_path=tmp_path / "manifest.json", log_path=tmp_path / "log.json",
    )
    assert state["status"] == "VOID"
    assert state["started"] is True
    assert state["retry_allowed"] is False
    assert "without the run marker" in state["detail"]


def test_status_is_read_only_and_names_the_policy(monkeypatch, tmp_path, capsys):
    marker = tmp_path / "run.json"
    marker.write_text('{"status": "STARTED"}', encoding="utf-8")
    before = marker.read_bytes()
    out = tmp_path / "result.json"
    monkeypatch.setattr(runner, "RUN", marker)
    monkeypatch.setattr(runner, "OUT", out)
    monkeypatch.setattr(runner, "MANIFEST", tmp_path / "manifest.json")
    monkeypatch.setattr(runner, "RAW_LOG", tmp_path / "log.json")
    assert runner.main(["--status"]) == 0
    text = capsys.readouterr().out
    assert "run status: VOID" in text
    assert "never retried" in text
    assert "retry: refused" in text
    assert marker.read_bytes() == before
    assert not out.exists()


def test_a_finalization_failure_is_void_and_returns_failure(monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "authorisation", lambda: (True, "authorised"))
    monkeypatch.setattr(runner, "pins", lambda: [])
    monkeypatch.setattr(runner, "load_gates", lambda path: runner.synthetic_gates(failing=("A3",)))
    monkeypatch.setattr(runner, "RUN", tmp_path / "default-run.json")
    monkeypatch.setattr(runner, "OUT", tmp_path / "default-result.json")
    monkeypatch.setattr(runner, "MANIFEST", tmp_path / "default-manifest.json")
    monkeypatch.setattr(runner, "RAW_LOG", tmp_path / "default-log.json")
    monkeypatch.setattr(runner, "_finish_run",
                        lambda *args: (_ for _ in ()).throw(OSError("simulated finalization failure")))
    marker = tmp_path / "run.json"
    out = tmp_path / "result.json"
    manifest = tmp_path / "manifest.json"
    log = tmp_path / "run-log.json"
    assert runner.run(control_path=tmp_path / "no-control.json", out=out, marker_path=marker,
                      manifest_path=manifest, log_path=log) == 1
    assert json.loads(marker.read_text(encoding="utf-8"))["status"] == "STARTED"
    state = runner.run_status(marker_path=marker, out=out, manifest_path=manifest, log_path=log)
    assert state["status"] == "VOID"
    assert state["retry_allowed"] is False
    before = out.read_bytes()
    assert runner.run(control_path=tmp_path / "no-control.json", out=out, marker_path=marker,
                      manifest_path=manifest, log_path=log) == 1
    assert out.read_bytes() == before


def test_a_run_marker_refuses_a_second_attempt_before_any_gate_read(monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "authorisation", lambda: (True, "authorised"))
    monkeypatch.setattr(runner, "pins", lambda: [])
    monkeypatch.setattr(runner, "RUN", tmp_path / "default-run.json")
    monkeypatch.setattr(runner, "OUT", tmp_path / "default-result.json")
    monkeypatch.setattr(runner, "MANIFEST", tmp_path / "default-manifest.json")
    monkeypatch.setattr(runner, "RAW_LOG", tmp_path / "default-log.json")
    monkeypatch.setattr(runner, "load_gates", lambda path: (_ for _ in ()).throw(
        AssertionError("gates were read after the run marker refused")))
    marker = tmp_path / "run.json"
    marker.write_text("{}", encoding="utf-8")
    out = tmp_path / "result.json"

    assert runner.run(control_path=tmp_path / "no-control.json", out=out, marker_path=marker,
                      manifest_path=tmp_path / "manifest.json", log_path=tmp_path / "log.json") == 1
    assert not out.exists()
    assert json.loads(marker.read_text(encoding="utf-8")) == {}


def test_an_existing_result_is_never_overwritten(monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "authorisation", lambda: (True, "authorised"))
    monkeypatch.setattr(runner, "pins", lambda: [])
    monkeypatch.setattr(runner, "RUN", tmp_path / "default-run.json")
    monkeypatch.setattr(runner, "OUT", tmp_path / "default-result.json")
    monkeypatch.setattr(runner, "MANIFEST", tmp_path / "default-manifest.json")
    monkeypatch.setattr(runner, "RAW_LOG", tmp_path / "default-log.json")
    out = tmp_path / "result.json"
    out.write_text("the one report\n", encoding="utf-8")
    marker = tmp_path / "run.json"

    assert runner.run(control_path=tmp_path / "no-control.json", out=out, marker_path=marker,
                      manifest_path=tmp_path / "manifest.json", log_path=tmp_path / "log.json") == 1
    assert out.read_text(encoding="utf-8") == "the one report\n"
    assert not marker.exists()


def test_the_canonical_paths_block_even_a_custom_attempt(monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "authorisation", lambda: (True, "authorised"))
    monkeypatch.setattr(runner, "pins", lambda: [])
    monkeypatch.setattr(runner, "RUN", tmp_path / "default-run.json")
    monkeypatch.setattr(runner, "OUT", tmp_path / "default-result.json")
    monkeypatch.setattr(runner, "MANIFEST", tmp_path / "default-manifest.json")
    monkeypatch.setattr(runner, "RAW_LOG", tmp_path / "default-log.json")
    monkeypatch.setattr(runner, "load_gates", lambda path: (_ for _ in ()).throw(
        AssertionError("gates were read after the canonical guard refused")))
    custom_marker = tmp_path / "custom-run.json"
    custom_out = tmp_path / "custom-result.json"

    (tmp_path / "default-run.json").write_text("{}", encoding="utf-8")
    assert runner.run(control_path=tmp_path / "no-control.json", out=custom_out,
                      marker_path=custom_marker, manifest_path=tmp_path / "custom-manifest.json",
                      log_path=tmp_path / "custom-log.json") == 1
    assert not custom_out.exists()

    (tmp_path / "default-run.json").unlink()
    (tmp_path / "default-result.json").write_text("the one report\n", encoding="utf-8")
    assert runner.run(control_path=tmp_path / "no-control.json", out=custom_out,
                      marker_path=custom_marker, manifest_path=tmp_path / "custom-manifest.json",
                      log_path=tmp_path / "custom-log.json") == 1
    assert not custom_marker.exists()


def test_an_existing_manifest_or_log_refuses_a_second_attempt(monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "authorisation", lambda: (True, "authorised"))
    monkeypatch.setattr(runner, "pins", lambda: [])
    monkeypatch.setattr(runner, "RUN", tmp_path / "default-run.json")
    monkeypatch.setattr(runner, "OUT", tmp_path / "default-result.json")
    monkeypatch.setattr(runner, "MANIFEST", tmp_path / "default-manifest.json")
    monkeypatch.setattr(runner, "RAW_LOG", tmp_path / "default-log.json")
    monkeypatch.setattr(runner, "load_gates", lambda path: (_ for _ in ()).throw(
        AssertionError("gates were read after a provenance artifact refused")))
    marker = tmp_path / "run.json"
    out = tmp_path / "result.json"
    manifest = tmp_path / "manifest.json"
    log = tmp_path / "run-log.json"

    manifest.write_text("{}", encoding="utf-8")
    assert runner.run(control_path=tmp_path / "no-control.json", out=out, marker_path=marker,
                      manifest_path=manifest, log_path=log) == 1
    assert not marker.exists() and not out.exists()

    manifest.unlink()
    log.write_text("{}", encoding="utf-8")
    assert runner.run(control_path=tmp_path / "no-control.json", out=out, marker_path=marker,
                      manifest_path=manifest, log_path=log) == 1
    assert not marker.exists() and not out.exists()


def test_a_gate_failure_writes_a_marker_and_void_once(monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "authorisation", lambda: (True, "authorised"))
    monkeypatch.setattr(runner, "pins", lambda: [])
    monkeypatch.setattr(runner, "load_gates", lambda path: runner.synthetic_gates(failing=("A3",)))
    monkeypatch.setattr(runner, "RUN", tmp_path / "default-run.json")
    monkeypatch.setattr(runner, "OUT", tmp_path / "default-result.json")
    monkeypatch.setattr(runner, "MANIFEST", tmp_path / "default-manifest.json")
    monkeypatch.setattr(runner, "RAW_LOG", tmp_path / "default-log.json")
    marker = tmp_path / "run.json"
    out = tmp_path / "result.json"
    manifest = tmp_path / "manifest.json"
    log = tmp_path / "run-log.json"

    assert runner.run(control_path=tmp_path / "no-control.json", out=out, marker_path=marker,
                      manifest_path=manifest, log_path=log) == 0
    result = json.loads(out.read_text(encoding="utf-8"))
    completed = json.loads(marker.read_text(encoding="utf-8"))
    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
    raw = json.loads(log.read_text(encoding="utf-8"))
    assert result["outcome"] == "VOID"
    assert "A3_MUTATION" in result["void"]["codes"]
    assert completed["status"] == "COMPLETED"
    assert completed["result_sha256"] == runner.hashlib.sha256(out.read_bytes()).hexdigest()
    assert completed["manifest_sha256"] == runner.hashlib.sha256(manifest.read_bytes()).hexdigest()
    assert completed["run_log_sha256"] == runner.hashlib.sha256(log.read_bytes()).hexdigest()
    assert manifest_data["status"] == "COMPLETED"
    assert manifest_data["inputs"]["gate_record"]["sha256"] == runner.hashlib.sha256(
        runner.GATES.read_bytes()).hexdigest()
    assert manifest_data["inputs"]["seed_declaration"]["sha256"] == runner.hashlib.sha256(
        (runner.REPO / "docs" / "v2_first_cell_seeds.json").read_bytes()).hexdigest()
    assert raw["seeds"] and all(seed["arms"] is None for seed in raw["seeds"])
    assert not list(tmp_path.glob(".*.tmp-*"))

    before = out.read_bytes()
    assert runner.run(control_path=tmp_path / "no-control.json", out=out, marker_path=marker,
                      manifest_path=manifest, log_path=log) == 1
    assert out.read_bytes() == before
