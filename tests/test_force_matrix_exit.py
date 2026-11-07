"""The force-matrix harness must fail when its reference arm is dead.

`docs/RERUN-0.12.0.md` records the defect these tests close: the harness
printed `FULL produced no theories -- the reference arm is broken` and exited
0, so a caller reading the status saw success.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import force_matrix  # noqa: E402


def _check(theories, colony="FULL"):
    return {"colony": colony, "theories": theories,
            "retention_policy": "alphabetical"}


def _row(colony, counts):
    return {"colony": colony, "series": {"theories": counts}, "seconds": 0.0,
            "metrics": {
                "M1_theory_duty_cycle": {"whole_run": 0.0},
                "M2_question_duty_cycle": {"whole_run": 0.0},
                "M3_contradiction_density": {"mean": 0.0},
                "M4_contradiction_survival": {"rate": 0.0},
                "M5_development_velocity": {"new_per_100_cycles": 0.0},
                "M6_lineage_depth": {"max_generation": 0},
                "M7_mean_hypothesis_lifetime": {"mean": 0.0},
                "M8_population_stability": {"beliefs": 0},
                "M9_cognitive_revolutions": {"revolutions": 0},
            }}


def test_a_dead_reference_arm_is_a_problem():
    problems = force_matrix.reference_arm_problems([_check(0)])
    assert problems
    assert "no theories" in problems[0]


def test_a_live_reference_arm_is_not_a_problem():
    assert force_matrix.reference_arm_problems([_check(5)]) == []


def test_a_missing_reference_arm_is_a_problem():
    problems = force_matrix.reference_arm_problems([_check(4, colony="SALIENCE")])
    assert problems and "missing" in problems[0]


def test_a_reference_trace_that_ends_empty_is_a_problem():
    problems = force_matrix.row_reference_problems([_row("FULL", [6] * 90 + [0] * 10)])
    assert problems
    assert "final tenth" in problems[0]


def test_a_reference_trace_that_never_forms_is_a_problem():
    problems = force_matrix.row_reference_problems([_row("FULL", [0] * 100)])
    assert problems and "no theories" in problems[0]


def test_a_live_reference_trace_is_not_a_problem():
    assert force_matrix.row_reference_problems([_row("FULL", [3] * 100)]) == []


def test_verify_only_exits_non_zero_when_the_arm_is_dead(monkeypatch):
    dead = [_check(0)]
    monkeypatch.setattr(force_matrix, "verify_colonies",
                        lambda events: (dead, force_matrix.reference_arm_problems(dead)))
    monkeypatch.setattr(sys, "argv", ["force_matrix.py", "--verify-only"])
    with pytest.raises(SystemExit) as excinfo:
        force_matrix.main()
    assert excinfo.value.code == 1


def test_verify_only_returns_cleanly_when_the_arm_is_live(monkeypatch):
    monkeypatch.setattr(force_matrix, "verify_colonies",
                        lambda events: ([_check(5)], []))
    monkeypatch.setattr(sys, "argv", ["force_matrix.py", "--verify-only"])
    assert force_matrix.main() is None


def test_the_campaign_exits_non_zero_when_its_own_trace_is_dead(monkeypatch, tmp_path):
    monkeypatch.setattr(force_matrix, "run_colony",
                        lambda name, events, cycles, seed: _row(name, [0] * 20))
    out = tmp_path / "dead.json"
    monkeypatch.setattr(sys, "argv",
                        ["force_matrix.py", "--no-verify", "--colonies", "FULL",
                         "--cycles", "20", "--out", str(out)])
    with pytest.raises(SystemExit) as excinfo:
        force_matrix.main()
    assert excinfo.value.code == 1
    assert json.loads(out.read_text(encoding="utf-8"))["rows"]


def test_the_campaign_returns_cleanly_when_the_arm_is_live(monkeypatch, tmp_path):
    monkeypatch.setattr(force_matrix, "run_colony",
                        lambda name, events, cycles, seed: _row(name, [4] * 20))
    out = tmp_path / "live.json"
    monkeypatch.setattr(sys, "argv",
                        ["force_matrix.py", "--no-verify", "--colonies", "FULL",
                         "--cycles", "20", "--out", str(out)])
    assert force_matrix.main() is None
    assert json.loads(out.read_text(encoding="utf-8"))["rows"]
