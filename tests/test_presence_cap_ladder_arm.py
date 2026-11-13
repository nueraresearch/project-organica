"""The cap-ladder runner is gated by a dated grant and writes one part per cell."""
LAYER = "dry-run"

import json
import sqlite3

import pytest

from benchmarks import presence_cap_ladder_arm as arm
from benchmarks import presence_cap_ladder_prereg as block


def test_dry_run_prints_the_frozen_24_cells(capsys):
    assert arm.main(["--dry-run"]) == 0
    lines = capsys.readouterr().out.splitlines()
    expected = [
        "python -m benchmarks.presence_cap_ladder_arm --cell %d %d" % (seed, cap)
        for seed in block.SEEDS for cap in block.CAPS
    ]
    assert lines == expected
    assert len(lines) == 24


def test_dry_run_never_opens_a_database(monkeypatch, capsys):
    def refuse(*args, **kwargs):
        raise AssertionError("sqlite3.connect was called during --dry-run")

    monkeypatch.setattr(sqlite3, "connect", refuse)

    assert arm.main(["--dry-run"]) == 0
    assert len(capsys.readouterr().out.splitlines()) == 24


def test_cell_refuses_before_opening_a_database(monkeypatch, capsys):
    def refuse(*args, **kwargs):
        raise AssertionError("sqlite3.connect was called during --cell")

    monkeypatch.setattr(sqlite3, "connect", refuse)

    with pytest.raises(SystemExit) as exc:
        arm.main(["--cell", "20614101", "40"])
    assert exc.value.code == 2
    assert "REFUSED" in capsys.readouterr().err


def _grant(monkeypatch, tmp_path):
    doc = block.record()
    doc["authorisation"] = {
        "required": True,
        "granted": True,
        "granted_on": "2026-11-12",
        "document": "docs/OWNER-GRANT.md",
        "quote": "run the 24 planned cap-ladder cells",
        "note": "test grant",
    }
    doc["runner"]["built"] = True
    doc["runner"]["planned_module"] = arm.MODULE
    monkeypatch.setattr(block, "record", lambda: doc)
    monkeypatch.setattr(arm, "PARTS", tmp_path)
    return doc


def test_cell_runs_when_the_grant_is_present(monkeypatch, tmp_path):
    _grant(monkeypatch, tmp_path)
    monkeypatch.setattr(arm, "run_cell", lambda seed, cap: {
        "kind": "presence_cap_ladder_cell", "seed": seed, "cap": cap,
    })

    assert arm.main(["--cell", "20614101", "40"]) == 0
    path = tmp_path / "20614101-40.json"
    assert path.exists()
    assert json.loads(path.read_text(encoding="utf-8"))["cap"] == 40


def test_unplanned_cell_refuses_before_a_database(monkeypatch, tmp_path):
    _grant(monkeypatch, tmp_path)

    def refuse(*args, **kwargs):
        raise AssertionError("sqlite3.connect was called for an unplanned cell")

    monkeypatch.setattr(sqlite3, "connect", refuse)
    assert arm.main(["--cell", "20614101", "20"]) == 2


def test_existing_part_refuses_before_a_database(monkeypatch, tmp_path):
    _grant(monkeypatch, tmp_path)
    (tmp_path / "20614101-40.json").write_text("{}", encoding="utf-8")

    def refuse(*args, **kwargs):
        raise AssertionError("sqlite3.connect was called for an existing part")

    monkeypatch.setattr(sqlite3, "connect", refuse)
    assert arm.main(["--cell", "20614101", "40"]) == 2


def test_preflight_names_a_missing_grant_date(monkeypatch, tmp_path):
    doc = _grant(monkeypatch, tmp_path)
    doc["authorisation"]["granted_on"] = None
    reasons = arm.preflight()
    assert any("no date" in reason for reason in reasons)
    with pytest.raises(SystemExit) as exc:
        arm.refuse()
    assert exc.value.code == 2
