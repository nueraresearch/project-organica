"""A2's registration must be frozen, runnable and inconvenient, and its slope not a bar.

The guards here are the same shape as A1's, with A2's own condition: the judged criterion is
the sparse-end level, the interaction is descriptive because the dense end is pinned, the
bar has a provenance from unregistered seeds, the 16-seed grid runs through the shared
runner, and the frozen scorer reaches every pole of the decision table.
"""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import json
from pathlib import Path

import pytest

from benchmarks import run_density_interaction as runner
from benchmarks import score_density_interaction_a2 as scorer
from benchmarks import write_density_a2_prereg as writer
from benchmarks.density_worlds import designed_pool, identity_cell, is_intra_cell

ROOT = Path(__file__).resolve().parent.parent
PREREG = ROOT / "docs" / "density_interaction_a2_prereg.json"
DOC = ROOT / "docs" / "DENSITY-INTERACTION-A2-PREREGISTRATION.md"
PREREG_A1 = ROOT / "docs" / "density_interaction_prereg.json"


def _body():
    return json.loads(PREREG.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def designed_cells():
    """The whole A2 grid from the designed pools: no engine, no judged cell."""
    body = _body()
    cells = []
    for seed in body["design"]["seeds"]:
        for rho in body["design"]["densities"]:
            pool = designed_pool(int(seed), float(rho), body["design"]["filler"])
            for scheme in body["design"]["schemes"]:
                cells.extend(runner.cells_for(int(seed), float(rho), scheme, pool,
                                              body)["cells"])
    return {"cells": cells, "identity": runner.identity_audit(body)}


def test_a2_s_status_and_artifacts_agree():
    """A registration may not claim a run it does not have, in either direction."""
    body = _body()
    assert body["prereg"] == "DENSITY-INTERACTION-2"
    run_cells = ROOT / "docs" / "density_interaction_a2_run.json"
    result = ROOT / "docs" / "density_interaction_a2_result.json"
    assert body["status"].split()[0] == "RUN"
    assert run_cells.exists() and result.exists()
    payload = json.loads(run_cells.read_text(encoding="utf-8"))
    scored = json.loads(result.read_text(encoding="utf-8"))
    assert len(payload["cells"]) == body["design"]["cells"] \
        + body["design"]["sensitivity_cells"] == 640
    assert scored["cells"] == 640 and scored["gates"]["all_passed"] is True
    assert body["run"]["verdict"] == scored["decision"]["verdict"]
    assert body["held_predecessor"]["prereg"] == "DENSITY-INTERACTION-1"


def test_the_grid_is_the_declared_grid_and_the_runner_takes_sixteen_seeds():
    body = _body()
    design = body["design"]
    seeds = [int(s) for s in design["seeds"]]
    assert len(seeds) == 16 and len(set(seeds)) == 16
    assert seeds == list(range(seeds[0], seeds[0] + 16))
    planned = runner.plan(body)
    assert len(planned) == 640 == design["cells"] + design["sensitivity_cells"] == 320 + 320
    assert len({(c["seed"], c["rho_world"], c["scheme"], c["cap"], c["arm"])
                for c in planned}) == len(planned)
    runner.assert_grid(body)


def test_the_a2_filler_family_is_the_one_the_design_names():
    a2, a1 = _body(), json.loads(PREREG_A1.read_text(encoding="utf-8"))
    assert a2["design"]["filler"] == "constant"
    assert "filler" not in a1["design"], "A1's world must stay as it was registered"
    assert a1["status"].startswith("HELD")


def test_the_seed_block_is_fresh_anywhere_it_is_not_the_block():
    report = runner.freshness_audit(_body())
    assert report["passed"], report["collisions"]


def test_the_harness_passes_its_own_audits_before_any_cell():
    report = runner.self_test(_body())
    assert report["all_passed"], {
        name: check for name, check in report["checks"].items() if not check["passed"]}


def test_a1_is_still_refused_by_name():
    a1 = json.loads(PREREG_A1.read_text(encoding="utf-8"))
    with pytest.raises(SystemExit, match="held"):
        runner.run(ROOT / "docs" / "density_interaction_a2_should_not_exist.json", a1)


def test_the_judged_criterion_is_the_sparse_end_level_and_the_slope_is_descriptive():
    crit = _body()["criteria"]
    assert crit["primary_criterion"] == "sparse_level"
    assert crit["C1"].startswith("level at the sparse end")
    assert "precision at the primary cap" in crit["C1"]
    assert crit["C2"].startswith("the interaction")
    assert "NOT a criterion" in crit["C2"]
    assert "pinned" in crit["C2"]
    assert "C1 is the whole judged criterion" in crit["judged_whole"]
    assert "preconditions, not scores" in crit["judged_whole"]


def test_the_bar_is_calibrated_on_unregistered_seeds_and_not_the_run():
    crit = _body()["criteria"]
    assert crit["sparse_bar"] == 0.05
    assert "UNREGISTERED" in crit["bar_provenance"]
    assert "992001-992008" in crit["bar_provenance"]
    assert "rather than fitted to the judged run" in crit["bar_provenance"]


def test_the_pilot_supports_the_bar_and_the_pinned_dense_end():
    pilot = _body()["pilot"]
    primary, sensitivity = pilot["primary"], pilot["sensitivity"]
    for row in (primary, sensitivity):
        assert row["dense_delta_sd"] == 0.0, "the dense end is not pinned as described"
        assert abs(row["interaction_mean"]
                   - (row["dense_delta_mean"] - row["sparse_delta_mean"])) < 1e-3
        assert row["sparse_delta_mean"] > _body()["criteria"]["sparse_bar"]
        assert len(row["interaction_per_seed"]) == 8
    # power: the standard error the pilot implies at sixteen seeds
    assert abs(primary["sparse_delta_sd"] / (16 ** 0.5) - 0.0155) < 1e-9
    assert "0.8" in pilot["power"]


def test_every_verdict_in_the_table_is_reachable_and_named():
    table = _body()["decision_table"]
    verdicts = [row["verdict"] for row in table]
    assert len(set(verdicts)) == len(verdicts) == 7
    for wanted in ("EXCLUSION PAYS AT SPARSE DENSITY AND GROWS WITH DENSITY",
                   "EXCLUSION PAYS AT SPARSE DENSITY; DENSITY SLOPE NOT IDENTIFIED",
                   "EXCLUSION PAYS MORE AT SPARSE THAN DENSE",
                   "EXCLUSION DOES NOT PAY AT SPARSE DENSITY",
                   "EXPOSURE ARTIFACT", "UNDERPOWERED", "VOID"):
        assert wanted in verdicts, wanted
    for row in table:
        for key in ("condition", "reading", "decision"):
            assert row[key].strip(), (row["verdict"], key)


def test_the_frozen_scorer_reaches_exactly_the_table_s_verdicts(designed_cells):
    body = _body()
    result = scorer.score(designed_cells, body)
    assert result["cells"] == 640
    assert result["gates"]["all_passed"], {
        k: v for k, v in result["gates"].items() if isinstance(v, dict) and not v["passed"]}
    assert result["decision"]["verdict"] in {row["verdict"]
                                            for row in body["decision_table"]}
    assert result["criteria"]["descriptive_interaction"]["judged"] is False
    assert result["criteria"]["C1_sparse_level"]["bar"] == 0.05


def test_g0_requires_fourteen_of_sixteen():
    report = scorer.gates.__doc__
    assert report is not None
    body = _body()
    assert max(7, int(round(scorer.G0_SHARE * len(body["design"]["seeds"])))) == 14


@pytest.mark.parametrize("field,value,arm,gate", [
    ("presence", 0.99, "control", "G1_presence_ceiling"),
    ("coverage", 1.0, "control", "G6_treatment_does_not_lose_coverage"),
    ("precision", 0.999, "control", "G2_arithmetic"),
])
def test_each_gate_can_fail_and_voids_the_block(designed_cells, field, value, arm, gate):
    cells = json.loads(json.dumps(designed_cells["cells"]))
    next(c for c in cells if c["arm"] == arm)[field] = value
    report = scorer.score({"cells": cells, "identity": designed_cells["identity"]}, _body())
    assert report["gates"][gate]["passed"] is False, gate
    assert report["decision"]["verdict"] == "VOID"
    assert gate in report["decision"]["failed_gates"]


def test_the_identity_gate_fails_when_the_arms_are_not_identical(designed_cells):
    identity = dict(designed_cells["identity"], arms_identical=False, delta=0.25)
    report = scorer.score({"cells": designed_cells["cells"], "identity": identity}, _body())
    assert report["gates"]["G5_identity_where_it_must_hold"]["passed"] is False
    assert report["decision"]["verdict"] == "VOID"


def test_the_scorer_refuses_a_grid_with_a_cell_missing(designed_cells):
    with pytest.raises(ValueError, match="not the pre-registered grid"):
        scorer.score({"cells": designed_cells["cells"][1:],
                      "identity": designed_cells["identity"]}, _body())


def test_a_failed_criterion_with_a_narrow_interval_is_a_result_not_silence(designed_cells):
    """The DO-NOT-PAY pole must be reachable: a real null is a verdict."""
    cells = json.loads(json.dumps(designed_cells["cells"]))
    sparse = [c for c in cells if c["rho_world"] == 0.1 and c["cap"] == 20
              and c["scheme"] == "primary"]
    for cell in sparse:
        if cell["arm"] == "intra_cell_excluded":
            cell["precision"] = 0.0
            cell["covered"] = 0
    report = scorer.score({"cells": cells, "identity": designed_cells["identity"]}, _body())
    assert report["gates"]["all_passed"], "the edit left a gate failing"
    assert report["criteria"]["C1_sparse_level"]["passed"] is False
    assert report["decision"]["verdict"] in ("EXCLUSION DOES NOT PAY AT SPARSE DENSITY",
                                            "UNDERPOWERED")


def test_the_identity_fixture_is_not_decoration():
    fixture = identity_cell(_body()["design"]["seeds"][0])
    assert fixture["intra_cell_rows"] == 0
    assert fixture["cap"] < fixture["pool"]
    assert not any(is_intra_cell(a, b) for a, b in fixture["pool_edges"])
    assert fixture["passed"] and abs(fixture["delta"]) <= 1e-12


def test_the_document_is_the_artifact_rendered():
    text = DOC.read_text(encoding="utf-8")
    result = json.loads((ROOT / "docs" / "density_interaction_a2_result.json")
                        .read_text(encoding="utf-8"))
    assert writer.render_document(_body(), result) == text, (
        "the document differs from the artifact; regenerate with "
        "python -m benchmarks.write_density_a2_prereg")
    assert "## 9. Result (post-freeze)" in text
    assert _body()["run"]["verdict"] in text
    assert "{" not in text.replace("{%", "")
    assert "held" in text.lower() and "DENSITY-INTERACTION-1" in text


def test_the_document_states_the_pinned_dense_end_and_the_pilot():
    text = " ".join(DOC.read_text(encoding="utf-8").split())
    body = _body()
    assert "0.150 with sd 0.000" in text or "0.150 (sd 0.000)" in text
    assert body["criteria"]["bar_provenance"][:40] in text
    assert "not scored" in text
    low, high = body["seeds"]["block"]
    assert ("%d-%d" % (low, high)) in text or ("%d–%d" % (low, high)) in text


def test_the_registration_allocates_only_what_the_grid_pays_for():
    body = _body()
    allocation, design = body["allocation"], body["design"]
    assert allocation["seeds"] == len(design["seeds"]) == 16
    assert allocation["judged_cells"] == design["cells"] == 320
    assert allocation["sensitivity_cells"] == design["sensitivity_cells"] == 320
    assert allocation["bars"] == 1 and allocation["thresholds"] == 1
