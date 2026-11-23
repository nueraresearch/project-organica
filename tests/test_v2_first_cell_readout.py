"""The readout adapter runs the signed protocol on a smoke seed; its pins match the files it hashes."""
from __future__ import annotations
LAYER = "synthetic"  # benchmarks/test_layers.py: the module's execution layer

import json
from pathlib import Path

from benchmarks import v2_first_cell_readout as readout

ROOT = Path(__file__).resolve().parents[1]
PIN = ROOT / "docs" / "v2_first_cell_scorer_pin.json"
DRY = ROOT / "docs" / "v2_first_cell_dry_run.json"


def test_the_treatment_arm_cannot_select_itself_into_the_null() -> None:
    assert readout.BETA_GRID == (1, 2, 4, 8)
    assert 0 not in readout.BETA_GRID


def test_every_pin_matches_the_file_on_disk() -> None:
    pin = json.loads(PIN.read_text(encoding="utf-8"))
    for module, digest in pin["modules"].items():
        import hashlib
        assert hashlib.sha256((ROOT / module).read_bytes()).hexdigest() == digest, module
    assert pin["adapter"]["sha256"] == readout.adapter_sha256()
    assert "PINNED" in pin["status"]


def test_the_dry_run_record_is_a_dry_run_and_the_arms_separate() -> None:
    record = json.loads(DRY.read_text(encoding="utf-8"))
    assert "DRY RUN" in record["status"] and "NOT A CELL" in record["status"]
    assert record["seed"] == readout.DRY_SEED == 20911101
    assert record["m"] == 2 and record["window"] == 20
    assert record["train_blocks"] == 96
    assert record["calibration"] == [80, 96] and record["holdout"] == [96, 120]
    assert record["beta_grid"] == [1, 2, 4, 8]
    arms = record["arms"]
    assert arms["A"]["composites"] == 0
    assert arms["B"]["composites"] > 0 and arms["C"]["composites"] > 0
    assert arms["B"]["beta"] in readout.BETA_GRID and arms["C"]["beta"] in readout.BETA_GRID
    assert arms["C"]["mutations"] > 0
    losses = [arms[arm]["log_loss"] for arm in "ABC"]
    assert all(isinstance(loss, float) for loss in losses)
    assert len(set(losses)) == 3
    assert abs(arms["C"]["log_loss"] - arms["A"]["log_loss"] - record["difference_c_minus_a"]) < 1e-6
    assert record["engine_version"] and record["engine_sha256"]


def test_the_smoke_seed_is_reserved_and_marked_spent() -> None:
    registry = json.loads((ROOT / "docs" / "a1_seed_reservations.json").read_text(encoding="utf-8"))
    held = [row for row in registry["reservations"]
            if row["owner"] == "docs/v2_first_cell_dry_run.json"]
    assert len(held) == 1
    assert held[0]["seeds"] == [20911101]
    assert held[0]["spent"] is True


def test_the_check_entry_point_runs_the_pipeline_twice_and_passes() -> None:
    readout.check()
