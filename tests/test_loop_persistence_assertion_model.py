"""The loop retention/strength extension stays post hoc and internally current."""
LAYER = "static"

from benchmarks import loop_persistence_assertion_model as block


def test_artifact_is_posthoc_and_current():
    assert block.main(["--check"]) == 0
    art = block._load(block.ARTIFACT)
    assert art["posthoc"] is True
    assert art["prereg"] is None
    assert art["summary"]["confirmatory_verdict"] is None
    assert all(art["summary"]["integrity"].values())


def test_formation_control_is_present_and_derived_from_loop_onset():
    art = block._load(block.ARTIFACT)
    assert all(row["formation_cycle"] == min(row["loop_cycles"])
               for row in art["rows"])
    assert all(abs(row["formation_fraction"]
                   - row["formation_cycle"] / float(block.CYCLES)) < 1e-15
               for row in art["rows"])
    assert art["summary"]["integrity"]["formation_finite"] is True
    assert art["summary"]["integrity"]["controlled_converged"] is True
    assert art["summary"]["controlled"]["n"] == 177
    assert art["summary"]["controlled"]["events"] == 77
    assert "formation" in art["summary"]["controlled"]["coefficients"]
    assert art["summary"]["formation_control_readout"]
    assert "Formation-control readout" in block.render(art)


def test_strength_quartiles_cover_every_row():
    art = block._load(block.ARTIFACT)
    groups = art["summary"]["strength_quartiles"]
    assert sum(group["n"] for group in groups) == len(art["rows"])
    assert sum(group["events"] for group in groups) == art["summary"]["events"]


def test_check_refuses_a_confirmatory_verdict():
    art = block._load(block.ARTIFACT)
    art["confirmatory_verdict"] = "CONFIRMED"
    assert "confirmatory verdict present" in block.problems(art)
