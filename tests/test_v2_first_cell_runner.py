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

    out = tmp_path / "result.json"
    assert runner.run(control_path=tmp_path / "no-control.json", out=out) == 0
    result = json.loads(out.read_text(encoding="utf-8"))
    assert result["outcome"] == "VOID"
    assert result["gates"]["A1"]["status"] == "FAIL"
    assert "A1_CANONICALISATION" in result["void"]["codes"]
    assert result["interval"] is None
    assert all(row["measurable"] is False for row in result["per_seed"])
    assert "A1 failed on seed 20910101" in result["void"]["detail"]


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

    monkeypatch.setattr(runner, "cell_streams", lambda: streams)
    monkeypatch.setattr(runner.readout, "arms_for", fake_arms_for)

    out = tmp_path / "result.json"
    assert runner.run(control_path=tmp_path / "no-control.json", out=out) == 0
    result = json.loads(out.read_text(encoding="utf-8"))
    assert calls == [120] * 10
    assert result["gates"]["A1"]["status"] == "PASS"
    assert "Cell-stream check: 10 seeds replayed" in result["gates"]["A1"]["evidence"]
    assert report.validate(result) == []
