"""The gate runner must summarize both outcomes, return the matching exit code, and list without running."""
LAYER = "dry-run"  # benchmarks/test_layers.py: the module's execution layer

import sys

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


def test_main_prints_one_pass_summary_and_exits_zero(monkeypatch, capsys):
    """The other direction: every gate passing must say PASS once and exit 0."""
    gates = (("first gate", "unused.one", ("--check",)), ("second gate", "unused.two", ()))
    monkeypatch.setattr(gate_runner, "GATES", gates)
    calls = []

    def fake_run_gate(gate, timeout=180.0):
        calls.append((gate[0], timeout))
        return _result(gate, True)

    monkeypatch.setattr(gate_runner, "run_gate", fake_run_gate)

    status = gate_runner.main(["--timeout", "12.5"])
    output = capsys.readouterr().out

    assert status == 0
    assert output.count("GATE SUMMARY") == 1
    summary = output.split("GATE SUMMARY", 1)[1]
    assert summary.count("\n  PASS ") == 2
    assert "\n  FAIL " not in summary
    assert "2 of 2 gates passed." in summary
    assert summary.count("RESULT: PASS") == 1
    assert "RESULT: FAIL" not in summary
    # Each gate's own banner is printed even when it writes no stdout.
    assert "PASS  first gate  (0.01s)" in output
    assert "PASS  second gate  (0.01s)" in output
    # --timeout reaches every gate.
    assert calls == [("first gate", 12.5), ("second gate", 12.5)]


def test_list_prints_every_gate_command_and_runs_none(monkeypatch, capsys):
    """--list must describe the registered commands without invoking any of them."""
    def refuse(*args, **kwargs):
        raise AssertionError("--list must not run a gate")

    monkeypatch.setattr(gate_runner, "run_gate", refuse)

    status = gate_runner.main(["--list"])
    output = capsys.readouterr().out
    lines = [line for line in output.splitlines() if line.strip()]

    assert status == 0
    assert len(lines) == len(gate_runner.GATES)
    for name, module, gate_args in gate_runner.GATES:
        expected = "%-30s %s" % (
            name, " ".join([sys.executable, "-m", module, *gate_args]))
        assert expected in output
    assert "GATE SUMMARY" not in output
    assert "RESULT:" not in output
