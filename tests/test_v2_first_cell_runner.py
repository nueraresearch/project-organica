"""The runner is built, and every path that could produce a result is exercised without a world."""
import copy

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
