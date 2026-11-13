"""The entry-transition preregistration is frozen, fresh and unrun."""
LAYER = "static"

import json

from benchmarks import retention_entry_transition_prereg as block
from benchmarks.presence_cap_experiment import seed_collisions


def test_frozen_block_has_the_twenty_four_fresh_seeds():
    art = json.loads(block.PREREG.read_text(encoding="utf-8"))
    assert art["prereg"] == "CONFIRMATORY-RETENTION-ENTRY-TRANSITION-1"
    assert art["kind"] == "retention_entry_transition_prereg"
    assert art["status"] == "FROZEN, NOT RUN"
    assert art["design"]["seeds"] == list(range(20620101, 20620125))
    assert art["design"]["cells"] == 24
    assert art["design"]["cycles"] == 120
    assert art["design"]["cap"] == 40
    assert art["design"]["max_formation_cycle"] == 60
    assert art["design"]["structure_free_through_offset"] == 39
    assert art["design"]["outcome_start_offset"] == 40
    assert art["design"]["entry_run_cycles"] == 2
    assert seed_collisions(block.SEEDS, allow=(block.PREREG,)) == {}


def test_gates_are_exactly_d1_to_d10_and_the_late_cohort_is_absent():
    art = json.loads(block.PREREG.read_text(encoding="utf-8"))
    assert list(art["gates"]) == [
        "D1_population", "D2_structure_free", "D3_rank_coverage",
        "D4_seed_levels", "D5_convergence", "D6_complete",
        "D7_entry_validity", "D8_no_collision", "D9_separation",
        "D10_exposure",
    ]
    assert art["design"]["late_cohort"] is None
    assert "structure-free" in art["design"]["late_cohort_note"]
    assert "b_early" in art["model"]["primary_formula"]
    assert "b_proximal" in art["model"]["primary_formula"]
    assert "b_formation" not in art["model"]["primary_formula"]
    assert [row["id"] for row in art["criteria"]] == [
        "P1", "P2", "P3", "P4"]


def test_block_has_a_built_runner_but_no_grant_cell_or_result():
    art = json.loads(block.PREREG.read_text(encoding="utf-8"))
    assert art["authorisation"]["granted"] is False
    assert art["authorisation"]["document"] is None
    assert art["authorisation"]["quote"] is None
    assert art["runner"]["built"] is True
    assert art["runner"]["planned_module"] == "benchmarks.retention_entry_transition"
    assert art["runner"]["cells_run"] == 0
    assert not block.RESULT.exists()
    assert "No grant is recorded" in art["authorisation"]["note"]


def test_page_is_current_and_names_the_transition():
    art = json.loads(block.PREREG.read_text(encoding="utf-8"))
    page = block.PAGE.read_text(encoding="utf-8")
    assert page == block.render(art)
    assert "**Status: `FROZEN, NOT RUN`.**" in page
    assert "structure-free through f+39" in page
    assert "first **two-cycle** structure entry" in page
    assert "`D1_population`" in page
    assert "`D10_exposure`" in page
    assert "No grant is recorded" in page


def test_check_passes_and_refuses_a_grant_or_a_cell():
    assert block.main(["--check"]) == 0
    art = json.loads(block.PREREG.read_text(encoding="utf-8"))
    art["authorisation"]["granted"] = True
    assert "grant" in block.problems(art)
    art = json.loads(block.PREREG.read_text(encoding="utf-8"))
    art["runner"]["cells_run"] = 1
    assert "cells run" in block.problems(art)
    art = json.loads(block.PREREG.read_text(encoding="utf-8"))
    art["status"] = "GRANTED, NOT RUN"
    assert "status" in block.problems(art)
