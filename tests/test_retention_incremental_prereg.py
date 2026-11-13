"""The retention preregistration is frozen, prospective and unrun."""
LAYER = "static"

import json

from benchmarks import retention_incremental_prereg as block
from benchmarks.presence_cap_experiment import seed_collisions


def test_prereg_is_frozen_with_a_fresh_twelve_seed_block():
    art = json.loads(block.PREREG.read_text(encoding="utf-8"))
    assert art["prereg"] == "CONFIRMATORY-RETENTION-INCREMENTAL-1"
    assert art["status"] == "FROZEN, RUN"
    assert art["design"]["seeds"] == list(range(20618101, 20618113))
    assert art["design"]["cells"] == 12
    assert art["design"]["cycles"] == 120
    assert art["design"]["cap"] == 40
    assert art["design"]["landmark_cycle"] == 60
    assert seed_collisions(block.SEEDS, allow=(block.PREREG, block.RESULT)) == {}


def test_primary_and_reverse_predictors_are_named():
    art = json.loads(block.PREREG.read_text(encoding="utf-8"))
    assert "early_retention" in art["design"]["primary_predictors"]
    assert "late_retention" in art["design"]["reverse_time"]
    assert "assertion_cycle" in art["design"]["reverse_time"]
    assert "early_retention" in art["model"]["primary_formula"]
    assert "late_retention" in art["model"]["reverse_formula"]
    assert [row["id"] for row in art["criteria"]] == ["P1", "P2", "P3", "R1"]


def test_grant_and_run_are_recorded_with_a_result():
    art = json.loads(block.PREREG.read_text(encoding="utf-8"))
    assert art["authorisation"]["granted"] is True
    assert art["authorisation"]["document"] == "docs/AUTHORISATION-RETENTION-INCREMENTAL-1.md"
    assert art["runner"]["built"] is True
    assert art["runner"]["planned_module"] == "benchmarks.retention_incremental"
    assert art["runner"]["cells_run"] == 12
    assert block.RESULT.exists()
    assert block.main(["--check"]) == 0


def test_page_is_current_and_names_the_landmark():
    art = json.loads(block.PREREG.read_text(encoding="utf-8"))
    page = block.PAGE.read_text(encoding="utf-8")
    assert page == block.render(art)
    assert "Landmark:** cycle **60**" in page
    assert "Reverse-time control" in page
    assert "Granted on **2026-11-12**" in page
    assert "The twelve cells have run" in page


def test_check_refuses_an_incomplete_grant_or_wrong_cell_count():
    art = json.loads(block.PREREG.read_text(encoding="utf-8"))
    art["authorisation"]["granted"] = True
    art["authorisation"]["document"] = None
    assert "grant is incomplete" in block.problems(art)
    art = json.loads(block.PREREG.read_text(encoding="utf-8"))
    art["runner"]["cells_run"] = 11
    assert "cells run" in block.problems(art)
    art = json.loads(block.PREREG.read_text(encoding="utf-8"))
    art["status"] = "GRANTED, NOT RUN"
    assert "result exists before run" in block.problems(art)


if __name__ == "__main__":
    raise SystemExit(__import__("pytest").main([__file__, "-q"]))
