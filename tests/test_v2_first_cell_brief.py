"""The signature brief is one page, derived from the artifacts, and still asks for a signature."""
from __future__ import annotations

import json
from pathlib import Path

from benchmarks import v2_first_cell_brief as brief

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs" / "V2-FIRST-CELL-BRIEF.md"


def test_the_brief_is_one_page() -> None:
    text = PAGE.read_text(encoding="utf-8")
    assert 250 < len(text.split()) < 750


def test_every_headline_number_comes_from_its_artifact() -> None:
    page = PAGE.read_text(encoding="utf-8")
    null = json.loads((ROOT / "docs" / "v2_first_cell_null.json").read_text(encoding="utf-8"))
    power = json.loads((ROOT / "docs" / "v2_first_cell_power.json").read_text(encoding="utf-8"))
    handicap = json.loads((ROOT / "docs" / "v2_first_cell_handicap.json").read_text(encoding="utf-8"))
    planted = json.loads((ROOT / "docs" / "v2_first_cell_planted.json").read_text(encoding="utf-8"))
    assert "%.4f" % null["calibration"]["directional_false_pass_rate"] in page
    assert "%.6f" % power["mde"]["0.9"] in page
    assert ("−" + "%.6f" % abs(power["required_mean_d"]["0.9"])) in page
    assert "%.6f" % handicap["decomposition"]["beta_only_mean"] in page
    assert "%.6f" % handicap["decomposition"]["net_mean"] in page
    assert "%.2f×" % planted["comparison"]["gain_multiple_of_handicap"] in page


def test_the_brief_tracks_the_signature_state() -> None:
    page = PAGE.read_text(encoding="utf-8")
    decisions = json.loads((ROOT / "docs" / "decisions.json").read_text(encoding="utf-8"))
    entry = [row for row in decisions["decisions"] if row["decision_id"] == "DECISION-V2-FIRST-CELL"][0]
    if entry["status"] == "PENDING":
        assert "## The single remaining action" in page
        assert "Sign [`DECISION-V2-FIRST-CELL`](DECISION-V2-FIRST-CELL.md)" in page
    else:
        assert entry["status"] == "ADOPTED"
        assert "## The signature is recorded" in page
        assert "**Signed 2026-11-16.**" in page
        assert "single remaining action" not in page
        assert "10**, `20910101`–`20910110`, spent" in page


def test_the_check_entry_point_passes() -> None:
    brief.check()
