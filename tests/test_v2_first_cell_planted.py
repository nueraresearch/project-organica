"""The planted composite gain clears the null handicap, and the gain is the composite term's."""
from __future__ import annotations

import json
from pathlib import Path

from benchmarks import v2_first_cell_planted as planted

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "v2_first_cell_planted.json"
PAGE = ROOT / "docs" / "V2-FIRST-CELL-PLANTED.md"
HANDICAP = ROOT / "docs" / "v2_first_cell_handicap.json"


def _record() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_the_artifact_covers_the_declared_block() -> None:
    record = _record()
    declared = json.loads((ROOT / "docs" / "v2_first_cell_planted_seeds.json").read_text(encoding="utf-8"))
    assert record["seeds"] == declared["seed_block"]["seeds"]
    assert record["smoke_seed"] == declared["smoke_seed"]
    assert len(record["per_seed"]) == declared["n"]


def test_every_seed_gains_and_the_interval_clears_the_handicap() -> None:
    record = _record()
    handicap = json.loads(HANDICAP.read_text(encoding="utf-8"))["decomposition"]["net_mean"]
    assert all(row["d"] < 0 for row in record["per_seed"])
    assert record["interval"]["hi"] < -handicap
    assert record["comparison"]["clears_handicap"] is True
    assert record["comparison"]["gain_multiple_of_handicap"] > 10


def test_the_gain_is_the_composite_term_not_revision() -> None:
    record = _record()
    assert record["summary"]["mean_d_beta_only"] < 0
    assert abs(record["summary"]["mean_d_revision_only"]) < 0.01 * abs(record["summary"]["mean_d"])
    assert record["comparison"]["revision_share_of_gain"] < 0.05


def test_the_page_restates_the_result_and_its_scope() -> None:
    page = PAGE.read_text(encoding="utf-8")
    record = _record()
    assert "%.6f" % record["summary"]["mean_d"] in page
    assert "%.2f×" % record["comparison"]["gain_multiple_of_handicap"] in page
    assert "tag-to-role mapping" in page
    assert "does not establish that the first cell's world contains such a motif" in page


def test_the_check_entry_point_passes() -> None:
    planted.check()
