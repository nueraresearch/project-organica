"""The density interaction's registration must be frozen, runnable and inconvenient.

These are the guards a pre-registration needs before it is worth anything: the grid is the
declared grid, the seeds are fresh, the harness passes its own audits, the criterion is one
whole conjunction rather than a count, every gate can fire, and the document is the
artifact rendered rather than prose about it.
"""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import json
from pathlib import Path

import pytest

from benchmarks import run_density_interaction as runner
from benchmarks import score_density_interaction as scorer
from benchmarks import write_density_prereg as writer
from benchmarks.density_worlds import (designed_pool, identity_cell, is_intra_cell,
                                       world_edges)

ROOT = Path(__file__).resolve().parent.parent
PREREG = ROOT / "docs" / "density_interaction_prereg.json"
DOC = ROOT / "docs" / "DENSITY-INTERACTION-PREREGISTRATION.md"
DESIGN = ROOT / "docs" / "WORLD-DENSITY-DESIGN.md"
DESIGN_JSON = ROOT / "docs" / "world_density_design.json"


def _body():
    return json.loads(PREREG.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def designed_cells():
    """The whole grid, built from the designed pools: no engine, no judged cell."""
    body = _body()
    cells, identity = [], None
    for seed in body["design"]["seeds"]:
        for rho in body["design"]["densities"]:
            pool = designed_pool(int(seed), float(rho))
            for scheme in body["design"]["schemes"]:
                produced = runner.cells_for(int(seed), float(rho), scheme, pool, body)
                cells.extend(produced["cells"])
        identity = runner.identity_audit(body)
    return {"cells": cells, "identity": identity}


def test_the_registration_is_frozen_and_has_not_run():
    body = _body()
    assert body["status"].split(",")[0] in ("FROZEN", "HELD")
    assert "NOT RUN" in body["status"]
    if body["status"].startswith("HELD"):
        review = json.loads((ROOT / "docs" / "density_interaction_review.json")
                            .read_text(encoding="utf-8"))
        assert review["verdict"].startswith("HELD")
        assert body["review"]["review"] == review["review"]
        assert body["review"]["blocking"]
    if body.get("run"):
        assert (ROOT / "docs" / "density_interaction_result.json").exists()
    else:
        assert not (ROOT / "docs" / "density_interaction_run.json").exists()


def test_the_grid_is_the_declared_grid():
    body = _body()
    design = body["design"]
    planned = runner.plan(body)
    assert len(planned) == len(design["seeds"]) * len(design["densities"]) \
        * len(design["schemes"]) * len(design["caps"]) * len(design["arms"])
    assert len(planned) == design["cells"] + design["sensitivity_cells"] == 320
    assert len({(c["seed"], c["rho_world"], c["scheme"], c["cap"], c["arm"])
                for c in planned}) == len(planned), "the grid repeats a cell"
    runner.assert_grid(body)


def test_the_seed_block_is_fresh_anywhere_it_is_not_the_block():
    report = runner.freshness_audit(_body())
    assert report["passed"], report["collisions"]


def test_the_harness_passes_its_own_audits_before_any_cell():
    report = runner.self_test(_body())
    assert report["all_passed"], {name: check for name, check in report["checks"].items()
                                  if not check["passed"]}


def test_the_world_can_produce_the_registered_direction():
    """Amendment A1's condition: the advantage must be representable, and it is measured."""
    audit = _body()["leverage_audit"]
    assert audit["share_falls"] and audit["control_rises"] and audit["delta_rises"]
    assert audit["delta_cap_20" if "delta_cap_20" in audit
                 else "rows"][0] is not None
    rows = audit["rows"]
    assert rows[-1]["delta_cap_20"] > rows[0]["delta_cap_20"] > 0
    assert rows[-1]["intra_cell_share"] < rows[0]["intra_cell_share"]
    assert rows[-1]["control_cap_20"] > rows[0]["control_cap_20"]


def test_the_bars_are_policy_and_not_the_run_s_own_numbers():
    criteria = _body()["criteria"]
    assert criteria["interaction_bar"] == criteria["level_bar"] == 0.08
    assert "NOT calibrated" in criteria["bar_provenance"]
    assert "ordering block" in criteria["bar_provenance"]


def test_the_criterion_is_the_interaction_and_coverage_is_not_it():
    criteria = _body()["criteria"]
    assert "precision" in criteria["estimand"] and "cap" in criteria["estimand"]
    for key in ("C1", "C2"):
        assert "precision" in criteria[key]
        assert "coverage" not in criteria[key], key
    note = _body()["design"]["endpoint_cap_note"]
    assert "coverage" in note and "arithmetic" in note
    assert "conjunction" in criteria["judged_whole"]
    assert "not a score" in criteria["judged_whole"]


def test_the_direction_being_tested_is_the_amended_one():
    body = _body()
    assert body["amendment"]["pre_run"] is True
    assert "grows" in body["amendment"]["why"] or "rises" in body["amendment"]["why"]
    assert "retained" in body["amendment"]["what_changes"]
    criteria = body["criteria"]
    assert criteria["C1"].startswith("interaction")
    assert "0.8" in criteria["C1"] and "0.1" in criteria["C1"]


def test_every_verdict_in_the_table_is_reachable_and_named():
    verdicts = {row["verdict"] for row in _body()["decision_table"]}
    assert len(verdicts) == len(_body()["decision_table"]), "a verdict is listed twice"
    for wanted in ("DENSITY INTERACTION SUPPORTED", "FLAT - GEOMETRY NOT THE LEVER",
                   "ADVANTAGE FALLS WITH DENSITY", "EXPOSURE ARTIFACT",
                   "UNDERPOWERED", "VOID"):
        assert wanted in verdicts, wanted
    for row in _body()["decision_table"]:
        for key in ("condition", "reading", "decision"):
            assert row[key].strip(), (row["verdict"], key)


def test_the_frozen_scorer_reads_the_designed_grid(designed_cells):
    result = scorer.score(designed_cells, _body())
    assert result["gates"]["all_passed"], {
        k: v for k, v in result["gates"].items() if isinstance(v, dict) and not v["passed"]}
    assert result["decision"]["verdict"] in {row["verdict"]
                                             for row in _body()["decision_table"]}
    body = _body()
    assert result["cells"] == body["design"]["cells"] \
        + body["design"]["sensitivity_cells"] == 320


@pytest.mark.parametrize("field,value,arm,gate", [
    ("presence", 0.99, "control", "G1_presence_ceiling"),
    ("coverage", 1.0, "control", "G6_treatment_does_not_lose_coverage"),
    ("precision", 0.999, "control", "G2_arithmetic"),
])
def test_each_gate_can_fail_and_voids_the_block(designed_cells, field, value, arm, gate):
    body = _body()
    cells = json.loads(json.dumps(designed_cells["cells"]))
    target = next(c for c in cells if c["arm"] == arm)
    target[field] = value
    report = scorer.score({"cells": cells, "identity": designed_cells["identity"]}, body)
    assert report["gates"][gate]["passed"] is False, gate
    assert report["decision"]["verdict"] == "VOID"
    assert gate in report["decision"]["failed_gates"]


def test_the_identity_gate_fails_when_the_arms_are_not_identical(designed_cells):
    identity = dict(designed_cells["identity"], arms_identical=False, delta=0.25)
    report = scorer.score({"cells": designed_cells["cells"], "identity": identity},
                          _body())
    assert report["gates"]["G5_identity_where_it_must_hold"]["passed"] is False
    assert report["decision"]["verdict"] == "VOID"


def test_the_scorer_refuses_a_grid_with_a_cell_missing(designed_cells):
    cells = designed_cells["cells"][1:]
    with pytest.raises(ValueError, match="not the pre-registered grid"):
        scorer.score({"cells": cells, "identity": designed_cells["identity"]}, _body())


def test_the_identity_fixture_is_the_condition_it_claims():
    fixture = identity_cell(_body()["design"]["seeds"][0])
    assert fixture["intra_cell_rows"] == 0
    assert not any(is_intra_cell(a, b) for a, b in fixture["pool_edges"])
    assert fixture["passed"] and abs(fixture["delta"]) <= 1e-12


def test_the_document_is_the_artifact_rendered():
    text = DOC.read_text(encoding="utf-8")
    assert writer.render(_body()) == text, (
        "the document differs from the artifact; regenerate with "
        "python -m benchmarks.write_density_prereg")


def test_the_document_states_the_amendment_and_keeps_the_original_prediction():
    body = _body()
    flat = " ".join(DOC.read_text(encoding="utf-8").split())
    design_flat = " ".join(DESIGN.read_text(encoding="utf-8").split())
    rows = body["leverage_audit"]["rows"]
    assert "amendment a1" in design_flat.lower() and "superseded" in design_flat
    assert "Delta(rho) = treated − control declines as rho_world rises" in design_flat, (
        "the original prediction was deleted; an amendment must retain it")
    for row in (rows[0], rows[-1]):
        assert ("%.3f" % row["delta_cap_20"]) in design_flat
    assert body["amendment"]["id"] in flat
    assert "no placeholders" or "{" not in DOC.read_text(encoding="utf-8")


def test_the_design_record_still_allocates_nothing_of_its_own():
    design = json.loads(DESIGN_JSON.read_text(encoding="utf-8"))
    assert design["allocation"]["seeds"] == 0 and design["allocation"]["bars"] == 0
    amendment = design["amendments"][0]
    assert amendment["id"] == "A1" and amendment["pre_run"] is True
    assert amendment["registered_in"] == "docs/density_interaction_prereg.json"


def test_the_allocation_matches_the_grid_it_pays_for():
    allocation = _body()["allocation"]
    design = _body()["design"]
    assert allocation["seeds"] == len(design["seeds"]) == 8
    assert allocation["judged_cells"] == design["cells"]
    assert allocation["sensitivity_cells"] == design["sensitivity_cells"]
    assert allocation["bars"] == 2 and allocation["thresholds"] == 2


def test_the_world_reaches_the_dense_end_without_an_intra_cell_edge():
    body = _body()
    for seed in body["design"]["seeds"]:
        world = world_edges(int(seed), 0.8)
        assert len(world) == 192
        assert not any(is_intra_cell(a, b) for a, b in world)


def test_the_identity_fixture_is_not_decoration():
    """A fixture that selects the whole pool cannot fail; the cap must bite."""
    fixture = identity_cell(_body()["design"]["seeds"][0])
    assert fixture["cap"] == 20 and fixture["pool"] > fixture["cap"]
    assert fixture["passed"] and abs(fixture["delta"]) <= 1e-12


def test_g0_compares_sets_and_not_stored_order(designed_cells):
    """The same rows in a different order are not liveness."""
    body = _body()
    cells = json.loads(json.dumps(designed_cells["cells"]))
    sparse = [c for c in cells if c["rho_world"] == 0.1 and c["cap"] == 20
              and c["scheme"] == "primary"]
    pairs = {}
    for cell in sparse:
        pairs.setdefault(cell["seed"], {})[cell["arm"]] = cell
    for pair in pairs.values():
        # same rows, different stored order, on EVERY seed
        pair["intra_cell_excluded"]["selected"] = list(
            reversed(pair["control"]["selected"]))
    report = scorer.score({"cells": cells, "identity": designed_cells["identity"]}, body)
    assert report["gates"]["G0_liveness"]["seeds_where_arms_differ"] <= 1
    assert report["gates"]["G0_liveness"]["passed"] is False
    assert report["decision"]["verdict"] == "VOID"


def test_the_world_description_does_not_claim_a_share_it_does_not_have():
    """The filler's count is (1 - rho) times a budget; its share falls faster."""
    from benchmarks.density_worlds import FILLER_BUDGET, filler_events
    for rho in _body()["design"]["densities"]:
        assert filler_events(rho) == int(round((1.0 - rho) * FILLER_BUDGET))
    text = (PREREG.read_text(encoding="utf-8")
            + (ROOT / "benchmarks" / "density_worlds.py").read_text(encoding="utf-8"))
    assert "share of the event budget is" not in text
    assert "falls faster than" in text


def test_the_review_holds_the_block_with_evidence():
    """The hold must rest on measurement, and the measurement must hit both poles."""
    review = json.loads((ROOT / "docs" / "density_interaction_review.json")
                        .read_text(encoding="utf-8"))
    dense = [r for r in review["dry_run"]["rows"]
             if r["rho_world"] == 0.8 and r["scheme"] == "primary"][0]
    assert dense["delta"] == [0.0] * len(dense["delta"]), "the dense end is not saturated"
    assert review["dry_run"]["interaction_primary"] < 0
    assert review["dry_run"]["interaction_sensitivity"] > 0
    assert review["verdict"].startswith("HELD")
    assert "no judged cell" in " ".join(review["method"]).lower()
    assert review["not_a_result"].startswith("the dry-run figures")
    doc = (ROOT / "docs" / "DENSITY-INTERACTION-REVIEW.md").read_text(encoding="utf-8")
    assert "{" not in doc.replace("{%", "")
    assert review["verdict"] in doc
