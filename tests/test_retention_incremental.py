"""The retention runner is built, but refuses before any database without a grant."""
LAYER = "static"

import json
import random

import pytest

from benchmarks import retention_incremental as runner
from benchmarks import retention_incremental_prereg as block


def test_dry_run_prints_twelve_cell_commands_without_opening_a_database(monkeypatch, capsys):
    def forbidden():
        raise AssertionError("dry-run opened a database")

    monkeypatch.setattr(runner, "_make_scratch_db", forbidden)
    assert runner.main(["--dry-run"]) == 0
    lines = capsys.readouterr().out.strip().splitlines()
    assert lines == [runner.command(seed) for seed in block.SEEDS]


def _ungranted(monkeypatch):
    doc = block.record()
    doc["status"] = "FROZEN, NOT RUN"
    doc["authorisation"] = {"required": True, "granted": False,
                            "document": None, "quote": None}
    monkeypatch.setattr(block, "record", lambda: doc)
    return doc


def test_ungranted_cell_refuses_before_a_database_is_opened(monkeypatch):
    _ungranted(monkeypatch)

    def forbidden():
        raise AssertionError("ungranted cell opened a database")

    monkeypatch.setattr(runner, "_make_scratch_db", forbidden)
    with pytest.raises(SystemExit) as exc:
        runner.cell(block.SEEDS[0])
    assert exc.value.code == 2
    assert runner.preflight()


def test_ungranted_measure_refuses_before_a_database_is_opened(monkeypatch):
    _ungranted(monkeypatch)

    def forbidden():
        raise AssertionError("ungranted measure opened a database")

    monkeypatch.setattr(runner, "_make_scratch_db", forbidden)
    with pytest.raises(SystemExit) as exc:
        runner.measure()
    assert exc.value.code == 2


def _granted(monkeypatch):
    doc = block.record()
    doc["status"] = "GRANTED, NOT RUN"
    doc["runner"]["cells_run"] = 0
    doc["authorisation"] = {
        "required": True,
        "granted": True,
        "granted_on": "2026-11-12",
        "document": "docs/USER-MANUAL.md",
        "quote": "synthetic grant for a runner test",
    }
    monkeypatch.setattr(block, "record", lambda: doc)
    return doc


def test_complete_grant_passes_preflight(monkeypatch):
    _granted(monkeypatch)
    assert runner.preflight() == []


def test_granted_cell_uses_the_collection_hook_only(monkeypatch, tmp_path):
    _granted(monkeypatch)
    monkeypatch.setattr(runner, "PARTS", tmp_path)
    called = []

    def fake_run(seed):
        called.append(seed)
        return {"seed": seed, "rows": []}

    monkeypatch.setattr(runner, "run_cell", fake_run)
    assert runner.cell(block.SEEDS[0]) == 0
    assert called == [block.SEEDS[0]]
    assert runner.part_path(block.SEEDS[0]).exists()


def test_cell_outside_the_seed_block_is_refused_after_the_grant(monkeypatch):
    _granted(monkeypatch)
    assert runner.cell(20618999) == 2


def test_finish_requires_every_part(monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "PARTS", tmp_path)
    with pytest.raises(SystemExit) as exc:
        runner.finish()
    assert "missing parts" in str(exc.value)


def test_adjudicator_reads_synthetic_rows_without_a_seed_replay():
    rng = random.Random(13)
    rows = []
    for si, seed in enumerate(block.SEEDS):
        for j in range(20):
            asserted = rng.random() < 0.3
            early = rng.random()
            late = rng.random()
            rows.append({
                "seed": seed,
                "edge": "a%d-%d>b%d-%d" % (si, j, si, j),
                "asserted": asserted,
                "assertion_cycle": 61 + rng.randrange(40) if asserted else None,
                "served_windows": 0,
                "ever_loop": True,
                "formation_cycle": 1 + (j % 50),
                "loop_cycles": list(range(1 + (j % 50), 120, 7)),
                "early_retention": early,
                "late_retention": late,
                "rank60": 1 + rng.randrange(40),
                "count60": rng.randrange(20),
                "strength60": 0.1 + rng.random(),
                "late_strength": 0.1 + rng.random(),
                "direct_count_final": rng.randrange(20),
            })
    summary = runner._adjudicate(rows)
    assert summary["n_eligible"] == len(rows)
    assert summary["n_events"] == sum(1 for row in rows if row["asserted"])
    assert summary["verdict"] in block.build_prereg()["verdicts"]
    assert summary["verdict"] != "VOID"
    assert list(summary["criteria"]) == ["P1", "P2", "P3", "R1"]
    assert len(summary["gates"]) == 8


def test_run_wrote_the_result_and_page_and_check_passes():
    assert block.RESULT.exists()
    assert runner.ARTIFACT.exists()
    assert runner.PAGE.exists()
    assert runner.main(["--check"]) == 0
    result = json.loads(runner.ARTIFACT.read_text())
    assert result["summary"]["verdict"] == "VOID"
    assert result["summary"]["gates"]["M1_population"] is False
