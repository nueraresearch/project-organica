"""The null-world calibration is reproducible, directional and checks itself against its artifact."""
from __future__ import annotations

import json
from pathlib import Path

from benchmarks import v2_first_cell_null as null
from benchmarks import v2_first_cell_readout as readout

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "v2_first_cell_null.json"
PAGE = ROOT / "docs" / "V2-FIRST-CELL-NULL.md"


def _record() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_the_interval_can_fail_and_can_pass() -> None:
    assert readout.paired_interval([0.0] * 10)["includes_zero"] is True
    below = readout.paired_interval([-0.01] * 10)
    assert below["hi"] < 0 and below["includes_zero"] is False
    above = readout.paired_interval([0.01] * 10)
    assert above["lo"] > 0 and above["includes_zero"] is False


def test_the_null_world_has_no_temporal_law_but_keeps_the_shape() -> None:
    first = null.null_stream(20920101, 12)
    second = null.null_stream(20920101, 12)
    assert first == second
    assert len(first["events"]) == 12 * 8
    assert all(len(event.split()) == 2 for event in first["events"])
    assert all(set(event.split()) <= set(null.TAG_POOL) for event in first["events"])


def test_the_artifact_covers_the_declared_worlds_and_its_differences_match() -> None:
    record = _record()
    assert record["kind"] == "v2_first_cell_null"
    assert "NOT A CELL" in record["status"] and "NOT A VERDICT" in record["status"]
    assert [row["seed"] for row in record["per_seed"]] == null.NULL_SEEDS
    for row in record["per_seed"]:
        assert abs(row["arms"]["C"]["log_loss"] - row["arms"]["A"]["log_loss"] - row["d"]) < 1e-6


def test_the_calibration_is_the_directional_false_pass_rate() -> None:
    cal = _record()["calibration"]
    assert cal["cells"] == 1000 and cal["cell_size"] == 10
    assert cal["includes_zero_rate"] + cal["excludes_zero_rate"] == 1.0
    assert cal["excludes_above_zero"] + cal["excludes_below_zero"] == round(cal["excludes_zero_rate"] * cal["cells"])
    assert cal["directional_false_pass_rate"] == round(cal["excludes_below_zero"] / cal["cells"], 4)
    assert cal["directional_false_pass_rate"] <= 0.01
    assert 0.9 <= cal["coverage_of_pool_mean"] <= 1.0
    assert cal["median_width"] > 0


def test_the_page_restates_the_artifact() -> None:
    record = _record()
    page = PAGE.read_text(encoding="utf-8")
    cal = record["calibration"]
    assert "%.4f" % cal["includes_zero_rate"] in page
    assert "%d" % cal["excludes_above_zero"] in page
    assert "%.6f" % record["summary"]["mean_d"] in page
    assert "%.6f" % record["summary"]["sd_d"] in page
    assert "Amendment 2" in page


def test_the_null_seeds_are_reserved_and_spent() -> None:
    registry = json.loads((ROOT / "docs" / "a1_seed_reservations.json").read_text(encoding="utf-8"))
    rows = [row for row in registry["reservations"] if row["owner"] == "docs/v2_first_cell_null.json"]
    assert len(rows) == 1
    assert rows[0]["seeds"] == null.NULL_SEEDS
    assert rows[0]["spent"] is True


def test_the_check_entry_point_passes() -> None:
    null.check()
