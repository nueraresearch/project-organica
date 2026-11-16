"""The gate suite writes a record the runner accepts, and it does not pass gates it cannot test."""
from pathlib import Path

from benchmarks import v2_first_cell_gates as gates
from benchmarks import v2_first_cell_report as report
from benchmarks import v2_first_cell_runner as runner

ROOT = Path(__file__).resolve().parents[1]


def test_check_passes_and_writes_nothing():
    before_record = gates.OUT.read_bytes()
    before_page = gates.PAGE.read_bytes()
    assert gates.main(["--check"]) == 0
    assert gates.OUT.read_bytes() == before_record
    assert gates.PAGE.read_bytes() == before_page


def test_the_record_is_the_one_the_runner_accepts():
    record = gates._load(gates.OUT)
    loaded = runner.load_gates(gates.OUT)
    assert loaded == record["gates"]
    assert [loaded[gate]["status"] for gate in report.GATE_IDS] == [
        "PASS", "NOT RUN", "NOT RUN", "NOT RUN", "NOT RUN"
    ]
    assert "NOT RUN" in record["status"]


def test_a1_reproduces_both_committed_regressions():
    result = gates.a1_regressions()
    assert result["177"] == [177, 158, 139, 19]
    assert result["138"] == [138, 125]
    assert "177->158" in result["checks"] and "138->125" in result["checks"]


def test_a1_rule_is_total_on_paths():
    result = gates.a1_rule()
    assert result["mixed"] == 0
    assert result["paths"] == 5
    assert result["keys"] == 3


def test_a1_uses_the_spent_smoke_seed_not_a_reserved_one():
    assert gates.SMOKE == 20911101
    assert gates.SMOKE not in report.declared_seeds()


def test_the_primitive_gates_say_why_they_were_not_run():
    record = gates._load(gates.OUT)
    assert "no stored composite id" in record["gates"]["A2"]["evidence"]
    assert "no mutation API" in record["gates"]["A3"]["evidence"]
    assert "no rebuilt primitive store" in record["gates"]["A4"]["evidence"]
    assert "no ids, versions or retirements" in record["gates"]["A5"]["evidence"]


def test_not_run_gates_assemble_as_void():
    record = gates._load(gates.OUT)
    result = runner.assemble(
        runner.unmeasured_rows("not run: the gate record did not pass"),
        record["gates"],
        runner.no_control("the gate record did not pass"),
    )
    assert result["outcome"] == "VOID"
    assert "GATES_NOT_RUN" in result["void"]["codes"]
    assert "SEEDS_MEASURABLE" in result["void"]["codes"]
    assert report.validate(result) == []


def test_run_still_refuses_with_the_gate_record_present(tmp_path):
    allowed, _reason = runner.authorisation()
    if allowed:
        assert True  # the owner has signed; the pre-cell refusal is no longer the state
        return
    out = tmp_path / "result.json"
    assert runner.main(["--run", "--gates", str(gates.OUT), "--out", str(out)]) == 1
    assert not out.exists()
