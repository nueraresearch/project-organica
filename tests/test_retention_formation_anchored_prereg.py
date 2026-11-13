"""The formation-anchored retention follow-up is frozen, fresh and unrun."""
LAYER = "static"

import json

from benchmarks import retention_formation_anchored_prereg as block
from benchmarks.presence_cap_experiment import seed_collisions


def test_frozen_fresh_block_with_a_full_formation_window():
    art = json.loads(block.PREREG.read_text(encoding="utf-8"))
    assert art["prereg"] == "CONFIRMATORY-RETENTION-FORMATION-ANCHORED-1"
    assert art["status"] == "FROZEN, RUN"
    assert art["design"]["seeds"] == list(range(20619101, 20619113))
    assert art["design"]["cycles"] == 120
    assert art["design"]["cap"] == 40
    assert art["design"]["window_cycles"] == 20
    assert art["design"]["max_formation_cycle"] == 90
    assert art["design"]["late_formation_after"] == 60
    assert seed_collisions(block.SEEDS, allow=(block.PREREG, block.RESULT)) == {}


def test_population_admits_late_forming_loop_edges():
    art = json.loads(block.PREREG.read_text(encoding="utf-8"))
    assert "formation_cycle <= 90" in art["design"]["population"]
    assert "formation_cycle + 19" in art["design"]["population"]
    assert "formation_cycle > 60" in art["design"]["late_cohort"]
    assert "M9_late_representation" in art["gates"]
    assert "formation" not in art["design"]["primary_predictors"]
    assert "formation_descriptive" in art["design"]["primary_predictors"]
    assert "followup" in art["design"]["primary_predictors"]
    assert "b_formation" not in art["model"]["primary_formula"]
    assert "single horizon control" in art["model"]["identification"]
    assert art["amendments"][0]["before_grant"] is True


def test_grant_is_recorded_and_the_cells_have_run():
    art = json.loads(block.PREREG.read_text(encoding="utf-8"))
    assert art["authorisation"]["granted"] is True
    assert art["authorisation"]["granted_on"] == "2026-11-12"
    assert art["authorisation"]["document"] == "docs/AUTHORISATION-RETENTION-FORMATION-ANCHORED-1.md"
    assert art["authorisation"]["quote"] == (
        "Fix the post-landmark assertion cycle and rerun the twelve cells.")
    assert art["authorisation"]["quote_kind"] == "run-authorisation"
    assert art["authorisation"]["preparation_quote"] == (
        "Prepare the dated grant document for the formation-anchored block "
        "without running it.")
    assert (block.ROOT / art["authorisation"]["document"]).exists()
    assert art["runner"]["built"] is True
    assert art["runner"]["planned_module"] == "benchmarks.retention_formation_anchored"
    assert art["runner"]["cells_run"] == 12
    assert block.RESULT.exists()
    assert block.main(["--check"]) == 0


def test_page_is_current_and_explains_the_prior_void():
    art = json.loads(block.PREREG.read_text(encoding="utf-8"))
    page = block.PAGE.read_text(encoding="utf-8")
    assert page == block.render(art)
    assert "formation-anchored" in page
    assert "20-cycle" in page
    assert "all **16** late assertions" in page
    assert "`VOID`" in page
    assert "Run authorisation:" in page
    assert "> Fix the post-landmark assertion cycle and rerun the twelve cells." in page
    assert "runner is built behind the grant check" in page
    assert "single horizon control" in page
    assert "## Amendments" in page


def test_grant_document_is_dated_and_names_the_block():
    text = (block.ROOT / "docs/AUTHORISATION-RETENTION-FORMATION-ANCHORED-1.md").read_text(
        encoding="utf-8")
    assert "Dated 2026-11-12" in text
    assert "CONFIRMATORY-RETENTION-FORMATION-ANCHORED-1" in text
    assert "20619101–20619112" in text
    assert "The document was prepared under the instruction" in text
    assert "without running it" in text
    assert "The run itself was authorised by the later instruction" in text
    assert "> Fix the post-landmark assertion cycle and rerun the twelve cells." in text
    assert "not run a cell" in text
    assert "The twelve cells were rerun under the quoted run authorisation" in text


def test_check_refuses_an_incomplete_grant_or_a_broken_runner_state():
    art = json.loads(block.PREREG.read_text(encoding="utf-8"))
    art["authorisation"]["granted_on"] = None
    assert "grant is incomplete" in block.problems(art)
    art = json.loads(block.PREREG.read_text(encoding="utf-8"))
    art["runner"]["built"] = False
    assert "runner state" in block.problems(art)
    art = json.loads(block.PREREG.read_text(encoding="utf-8"))
    art["runner"]["planned_module"] = "benchmarks.wrong"
    assert "runner state" in block.problems(art)
