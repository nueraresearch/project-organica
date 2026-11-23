"""The cap-112 runners must be built, gated, and unable to run on the shipped build.

The grant covers the cells; the build does not. These tests hold the runner to that: the
preflight names the cap and the version, `--measure` raises before a cell, and every gate the
records promise has a control that fires on a hand-built row set. No engine is started here.
"""
LAYER = "dry-run"  # benchmarks/test_layers.py: refusal paths and pure gate functions only

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import presence_cap112_runners as runners  # noqa: E402


def test_the_landed_build_satisfies_the_preflight_and_the_gate_still_fires():
    assert runners.preflight() == []
    assert runners.refuse() is None

    # The level has landed, so the refusal is proved on an injected condition rather than by
    # the build: the same path a real unmet prerequisite would take.
    message = runners.refusal_message(["the shipped Layer-1 cap is 40, not 112"])
    assert message.startswith("REFUSED") and "cap is 40" in message

    original = runners.preflight
    try:
        runners.preflight = lambda: ["the shipped Layer-1 cap is 40, not 112"]
        with pytest.raises(SystemExit) as refused:
            runners.main(["--measure", "--block", "comparator"])
        assert "REFUSED" in str(refused.value)
    finally:
        runners.preflight = original


def test_no_cell_function_runs_before_the_refusal(monkeypatch):
    def opened(*args, **kwargs):
        raise AssertionError("a cell was opened on a build that is not the level")

    monkeypatch.setattr(runners, "run_one", opened)
    monkeypatch.setattr(runners, "preflight",
                        lambda: ["the shipped Layer-1 cap is 40, not 112"])
    with pytest.raises(SystemExit):
        runners.measure("Q1")


def test_the_three_blocks_are_wired_to_their_records():
    assert sorted(runners.RECORDS) == ["Q1", "Q2", "comparator"]

    for block, name in runners.RECORDS.items():
        body = runners.record(block)
        assert body["cap"] == 112
        if block in ("comparator", "Q2"):
            assert body["status"] == "FROZEN, RUN"
            assert body["no_cells_run"] is False
            expected = ("PRESENCE NOT ASSERTION" if block == "comparator"
                        else "CAP LIMITING")
            assert body["result"]["verdict"] == expected
        else:
            assert body["status"] == "FROZEN, NOT RUN"
            assert body["no_cells_run"] is True
        assert body["runner"]["module"] == "benchmarks/presence_cap112_runners.py"
        assert runners.ARTIFACTS[block].name.endswith("_run.json")
        assert runners.PAGES[block].name.endswith("-RESULT.md")


def test_every_declared_verdict_is_reachable_and_the_controls_fire():
    assert runners.self_test() == []
    assert set(runners.COMPARATOR_VERDICTS) == {
        "PRESENCE NOT FULL", "PRESENCE NOT ASSERTION", "PRESENCE AND ASSERTION COINCIDE"}
    assert set(runners.Q1_VERDICTS) == {
        "CONSTRUCT VALID", "OBJECT MISMATCH", "NOT MEASURABLE", "VOID"}
    assert set(runners.Q2_VERDICTS) == {
        "VOID", "CAP NOT BINDING", "ADMISSION-ONLY BOTTLENECK", "CAP LIMITING",
        "CAP LIMITING BELOW BAR", "CAP NOT LIMITING", "MIXED"}


def test_check_passes_and_would_fail_without_the_refusal_proof(monkeypatch):
    assert runners.main(["--check"]) == 0

    monkeypatch.setattr(runners, "refusal_message", lambda problems: "")
    assert runners.main(["--check"]) == 1, "a check that does not name the refusal must fail"


def test_dry_run_prints_every_planned_cell_without_writing(capsys):
    before = sorted(path.name for path in runners.PARTS.glob("*")) \
        if runners.PARTS.exists() else None

    assert runners.main(["--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "no cell opened" in out
    assert "planned cells: 39" in out
    for seed in runners.record("Q2")["design"]["seeds"]:
        for cap in runners.record("Q2")["design"]["levels"]:
            path = runners.part_path("Q2", seed, cap).relative_to(runners.ROOT)
            assert str(path) in out
    witness = runners.record("Q2")["design"]["witness_cell"]
    assert str(runners.part_path("Q2", witness["seed"], witness["cap"], "-witness")
               .relative_to(runners.ROOT)) in out

    after = sorted(path.name for path in runners.PARTS.glob("*")) \
        if runners.PARTS.exists() else None
    assert before == after, "a dry run must not write a part"


def test_dry_run_opens_no_cell(monkeypatch, capsys):
    def opened(*args, **kwargs):
        raise AssertionError("a dry run opened a cell")

    monkeypatch.setattr(runners, "run_one", opened)
    assert runners.main(["--dry-run", "--block", "Q1"]) == 0
    out = capsys.readouterr().out
    assert out.count("part=") == 7  # six seeds plus the control
    assert "Q1: PRESENCE-CONSTRUCT-1-112" in out


def test_the_self_test_reports_a_missing_gate(monkeypatch):
    def quiet(*args, **kwargs):
        return []

    monkeypatch.setattr(runners, "comparator_failures", quiet)
    assert runners.self_test(), "a gate that never fires must be reported"
