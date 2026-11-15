"""The sham-feasibility record must keep both verdicts, and not let one stand for the other."""
from __future__ import annotations

import json
from pathlib import Path

from benchmarks import a2_sham_feasibility as feasibility

DOCS = Path(__file__).resolve().parents[1] / "docs"


def _artifact() -> dict:
    return json.loads((DOCS / "a2_sham_feasibility.json").read_text(encoding="utf-8"))


def test_the_record_is_internally_consistent() -> None:
    doc = _artifact()
    assert doc["kind"] == "a2_sham_feasibility"
    assert doc["tolerance_cycles"] == 6
    assert doc["selection_artifact"].endswith("a1_c8_target_selection_competent.json")
    assert len(doc["rows"]) == 6
    for row in doc["rows"]:
        assert len(row["sham_edges"]) == row["targets"]
        assert row["sham_disjoint"] is True
        assert row["sham_degree_ok"] is True
    assert feasibility.problems() == []


def test_the_per_edge_verdict_is_not_rescued_by_the_aggregate_one() -> None:
    doc = _artifact()
    assert doc["status"].startswith("NOT FEASIBLE PER EDGE")
    per_edge_failures = [row for row in doc["rows"]
                         if row["distance"]["share_within_tolerance"] < 0.95]
    assert len(per_edge_failures) == 3
    # The aggregate reading is a different C4', and the record says so rather than presenting it as a pass.
    assert doc["aggregate"]["status"].startswith("FEASIBLE ON ALL SEEDS")
    assert "not a rescue" in doc["aggregate"]["note"]
    assert doc["totals"]["aggregate"]["feasible"] is True


def test_the_page_states_both_verdicts() -> None:
    page = (DOCS / "A2-SHAM-FEASIBILITY.md").read_text(encoding="utf-8")
    assert "Per edge: no construction found" in page
    assert "does not establish that none exists" in page
    assert "95%%" not in page, "a doubled percent sign is a formatting defect, not a figure"
    assert "different design" in page
    assert "not evidence about the organism" in page
