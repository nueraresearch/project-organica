"""The gate runner must summarize a failure and return a failing exit code."""

from benchmarks import gate_runner


def _result(gate, passed):
    return {
        "name": gate[0],
        "module": gate[1],
        "args": gate[2],
        "passed": passed,
        "returncode": 0 if passed else 7,
        "seconds": 0.01,
        "stdout": "",
        "stderr": "",
        "error": None,
    }


def test_main_prints_one_fail_summary_and_exits_one(monkeypatch, capsys):
    gates = (("passing gate", "unused.pass", ()), ("failing gate", "unused.fail", ()))
    monkeypatch.setattr(gate_runner, "GATES", gates)
    monkeypatch.setattr(
        gate_runner,
        "run_gate",
        lambda gate, timeout=180.0: _result(gate, gate[0] == "passing gate"),
    )

    status = gate_runner.main([])
    output = capsys.readouterr().out

    assert status == 1
    assert output.count("GATE SUMMARY") == 1
    summary = output.split("GATE SUMMARY", 1)[1]
    assert summary.count("\n  FAIL ") == 1
    assert "failing gate (exit 7)" in summary
    assert "1 of 2 gates passed." in summary
    assert summary.count("RESULT: FAIL") == 1
    assert "RESULT: PASS" not in summary
