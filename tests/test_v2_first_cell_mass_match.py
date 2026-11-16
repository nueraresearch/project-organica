"""The matched controls hold mass and key count, and both put maintained behind random."""
from __future__ import annotations

import json
from pathlib import Path

from benchmarks import v2_first_cell_mass_match as mm

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "v2_first_cell_mass_match.json"
PAGE = ROOT / "docs" / "V2-FIRST-CELL-MASS-MATCH.md"


def _record() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_the_artifact_covers_the_null_worlds_and_reproduces_them() -> None:
    record = _record()
    null = json.loads((ROOT / "docs" / "v2_first_cell_null.json").read_text(encoding="utf-8"))
    assert record["seeds"] == null["null_world"]["seeds"]
    assert [row["seed"] for row in record["per_seed"]] == record["seeds"]
    for row, reference in zip(record["per_seed"], null["per_seed"]):
        assert abs(row["d_maintained"] - reference["d"]) < 1e-6


def test_the_controls_hold_mass_and_key_count() -> None:
    for row in _record()["per_seed"]:
        assert row["mass"]["mass"]["edges"] == row["mass"]["maintained"]["edges"]
        assert row["mass"]["keys"]["edges"] <= row["mass"]["maintained"]["edges"]
        assert row["mass"]["keys"]["nonempty"] <= row["mass"]["maintained"]["nonempty"]


def test_both_readings_put_maintained_behind_random() -> None:
    record = _record()
    for mode in mm.MODES:
        assert record["intervals"][mode]["hi"] < 0, mode
        assert record["summary"]["mean_delta_" + mode] < 0, mode
    assert record["verdict"]["mass"].startswith("A MASS-MATCHED RANDOM ALLOCATION BEATS")
    assert record["verdict"]["keys"].startswith("MAINTAINED SELECTION IS WORSE THAN RANDOM")


def test_the_page_restates_the_result_and_the_shortfall() -> None:
    page = PAGE.read_text(encoding="utf-8")
    record = _record()
    assert "%.9f" % record["summary"]["mean_delta_mass"] in page
    assert "%.9f" % record["summary"]["mean_delta_keys"] in page
    assert "%.2f" % (record["summary"]["shortfall"] / record["summary"]["n"]) in page


def test_the_check_entry_point_passes() -> None:
    mm.check()
