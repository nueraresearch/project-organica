"""One shared sqrt cap curve plus a block offset beats block-specific shapes."""
import copy
import json
from pathlib import Path

from benchmarks import a1_cap_response_curve as rc

DOC = json.loads(Path("docs/a1_cap_response_curve.json").read_text(encoding="utf-8"))


def test_record_is_clean_and_governed_off():
    assert rc.problems(DOC) == []
    assert rc.self_test() == []
    assert DOC["not_a_result"] is True
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }
    assert DOC["constants"]["cells"] == 12
    assert DOC["constants"]["seeds"] == 72
    assert len(DOC["cells"]) == 12


def test_selected_model_is_shared_sqrt_plus_offset():
    selected = DOC["selected_model"]
    assert selected["model"] == "common_sqrt_offset"
    assert selected["parameters"] == 4
    assert selected["in_rmse"] == 0.013061
    assert selected["in_max"] == 0.02421
    assert selected["loo_rmse"] == 0.019283
    assert selected["loo_max"] == 0.033338
    assert selected["coefficients"] == [
        0.42002218, -0.0135582, -0.35118485, 0.04698666,
    ]
    assert DOC["sqrt_coefficient"] == 0.04698666


def test_block_offsets_are_the_baseline_difference():
    assert DOC["block_offsets"] == {
        "current-16": 0.42002218,
        "fresh-16": 0.40646398,
        "larger-28": 0.06883733,
    }
    assert DOC["relative_offsets"] == {
        "fresh-16": -0.0135582,
        "larger-28": -0.35118485,
    }


def test_cell_residuals_are_small_and_bounded():
    assert max(abs(row["residual"]) for row in DOC["cells"]) == 0.02421
    rows = {(row["block"], row["cap"]): row for row in DOC["cells"]}
    assert rows[("current-16", 20)]["observed"] == 0.636243
    assert rows[("fresh-16", 40)]["observed"] == 0.727844
    assert rows[("larger-28", 112)]["observed"] == 0.578149
    assert all(abs(row["residual"]) < 0.025 for row in DOC["cells"])


def test_shared_curve_beats_extra_block_shapes():
    models = {row["model"]: row for row in DOC["comparisons"]}
    assert models["common_sqrt_offset"]["loo_rmse"] == 0.019283
    assert models["block_sqrt"]["loo_rmse"] == 0.020933
    assert models["additive_cap_effects"]["loo_rmse"] == 0.023193
    assert models["block_linear"]["loo_rmse"] == 0.039759
    assert models["block_sqrt"]["in_rmse"] < models["common_sqrt_offset"]["in_rmse"]
    assert models["block_sqrt"]["loo_rmse"] > models["common_sqrt_offset"]["loo_rmse"]
    assert DOC["best_loo_model"] == "common_sqrt_offset"


def test_saturated_model_has_no_heldout_prediction():
    full = next(row for row in DOC["comparisons"]
                if row["model"] == "full_interaction")
    assert full["parameters"] == 12
    assert full["in_rmse"] == 0.0
    assert full["loo_rmse"] is None
    assert full["loo_max"] is None


def test_a_tampered_selected_model_is_reported():
    bad = copy.deepcopy(DOC)
    bad["selected_model"]["model"] = "block_sqrt"

    assert rc.problems(bad), "the selected model is part of the committed test"


def test_page_is_current():
    assert rc.PAGE_PATH.read_text(encoding="utf-8") == rc.render(DOC)
    text = rc.PAGE_PATH.read_text(encoding="utf-8")
    assert "square-root cap curve" in text
    assert "0.04699" in text
    assert "0.0193" in text
    assert "larger-28 | 0.0688" in text
