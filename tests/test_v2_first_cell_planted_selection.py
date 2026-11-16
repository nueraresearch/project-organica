"""On a world with signal, selection beats random where on the null it lost."""
from __future__ import annotations

import json
from pathlib import Path

from benchmarks import v2_first_cell_planted_selection as ps

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "v2_first_cell_planted_selection.json"
PAGE = ROOT / "docs" / "V2-FIRST-CELL-PLANTED-SELECTION.md"


def _record() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_the_artifact_covers_the_planted_block_and_reproduces_it() -> None:
    record = _record()
    planted = json.loads((ROOT / "docs" / "v2_first_cell_planted.json").read_text(encoding="utf-8"))
    assert record["seeds"] == planted["seeds"]
    for row, reference in zip(record["per_seed"], planted["per_seed"]):
        assert abs(row["d_maintained"] - reference["d"]) < 1e-6


def test_the_controls_hold_mass_and_key_count() -> None:
    for row in _record()["per_seed"]:
        assert row["mass"]["mass"]["edges"] == row["mass"]["maintained"]["edges"]
        assert row["mass"]["keys"]["edges"] <= row["mass"]["maintained"]["edges"]
        assert row["mass"]["keys"]["nonempty"] <= row["mass"]["maintained"]["nonempty"]


def test_selection_beats_random_at_equal_mass_and_key_count() -> None:
    record = _record()
    assert record["intervals"]["keys"]["lo"] > 0
    assert record["summary"]["mean_delta_keys"] > 0
    assert record["verdict"]["keys"].startswith("MAINTAINED SELECTION CAPTURES SIGNAL")


def test_the_sign_reverses_against_the_null_control() -> None:
    record = _record()
    null = json.loads((ROOT / "docs" / "v2_first_cell_mass_match.json").read_text(encoding="utf-8"))
    assert null["summary"]["mean_delta_keys"] < 0
    assert record["comparison"]["planted_mean_delta_keys"] > 0
    assert record["intervals"]["mass"]["includes_zero"] is True


def test_the_page_restates_the_reversal_and_its_scope() -> None:
    page = PAGE.read_text(encoding="utf-8")
    record = _record()
    assert "%.9f" % record["summary"]["mean_delta_keys"] in page
    assert "%.9f" % record["comparison"]["null_mean_delta_keys"] in page
    assert "deliberately the readout's best case" in page


def test_the_check_entry_point_passes() -> None:
    ps.check()
