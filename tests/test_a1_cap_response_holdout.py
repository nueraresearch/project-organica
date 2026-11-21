"""The shared curve transfers to a held-out cap but not to a held-out block."""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer
import copy
import json
from pathlib import Path

from benchmarks import a1_cap_response_holdout as hd

DOC = json.loads(Path("docs/a1_cap_response_holdout.json").read_text(encoding="utf-8"))


def test_record_is_clean_and_governed_off():
    assert hd.problems(DOC) == []
    assert hd.self_test() == []
    assert DOC["not_a_result"] is True
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }
    assert len(DOC["cells"]) == 12
    assert len(DOC["per_cap"]) == 4
    assert len(DOC["block_holdout"]) == 3
    assert len(DOC["control"]) == 6


def test_predictions_are_frozen_from_the_committed_fit():
    constants = DOC["constants"]
    assert constants["curve_coefficients"] == [
        0.42002218, -0.0135582, -0.35118485, 0.04698666]
    assert constants["size_coefficients"] == [
        1.90290201, -0.35852459, 0.04698666]
    assert constants["fit_caps"] == [20, 40, 80, 112]
    assert constants["holdout_caps"] == [28, 64, 96, 128]
    assert constants["interpolation_caps"] == [28, 64, 96]
    assert constants["extrapolation_caps"] == [128]


def test_interpolation_stays_inside_the_fit_scale():
    metrics = DOC["metrics"]
    assert (metrics["interpolation_cells"], metrics["interpolation_rmse"],
            metrics["interpolation_max"]) == (9, 0.013911, 0.023666)
    assert metrics["interpolation_rmse"] < metrics["reference_cell_loo_rmse"]


def test_one_step_of_extrapolation_does_not_degrade():
    metrics = DOC["metrics"]
    assert (metrics["extrapolation_cells"], metrics["extrapolation_rmse"],
            metrics["extrapolation_max"]) == (3, 0.014226, 0.022342)
    assert metrics["extrapolation_rmse"] < metrics["reference_cell_loo_rmse"]
    assert abs(metrics["extrapolation_rmse"]
               - metrics["interpolation_rmse"]) < 0.001


def test_every_heldout_cell_is_within_the_reference_error():
    residuals = [abs(row["residual"]) for row in DOC["cells"]]
    assert max(residuals) == 0.023666
    assert all(value <= 0.03 for value in residuals)
    current = next(row for row in DOC["cells"]
                   if row["block"] == "current-16" and row["cap"] == 28)
    assert (current["observed"], current["predicted"], current["residual"]) == (
        0.685888, 0.668652, 0.017236)


def test_candidate_size_offset_behaves_the_same():
    metrics = DOC["metrics"]
    assert (metrics["size_interpolation_rmse"],
            metrics["size_extrapolation_rmse"]) == (0.0151, 0.013093)


def test_the_fit_is_not_admissible_past_its_saturation_cap():
    assert DOC["saturation_caps"] == {
        "current-16": 152, "fresh-16": 160, "larger-28": 393}


def test_block_holdout_interpolates_but_does_not_extrapolate():
    entries = {entry["block"]: entry for entry in DOC["block_holdout"]}
    assert entries["current-16"]["status"] == "estimated"
    assert entries["current-16"]["rmse"] == 0.021637
    assert entries["fresh-16"]["status"] == "estimated"
    assert entries["fresh-16"]["rmse"] == 0.019702
    larger = entries["larger-28"]
    assert larger["status"] == "not_identified"
    assert larger["training_log_spread"] == 0.002625
    assert larger["coefficients"] == [21.891103, -5.165568, 0.044981]
    assert larger["cells"][0]["predicted"] == -4.332909
    assert DOC["metrics"]["block_not_identified"] == ["larger-28"]
    assert DOC["metrics"]["block_estimated_rmse_max"] == 0.021637


def test_control_reproduces_the_committed_cap80_counts():
    assert all(row["matches_committed"] for row in DOC["control"])
    assert [(row["block"], row["A"], row["K"], row["A_and_K"])
            for row in DOC["control"]] == [
        ("current-16", 51, 64, 51),
        ("current-16", 53, 63, 53),
        ("fresh-16", 56, 64, 56),
        ("fresh-16", 49, 64, 49),
        ("larger-28", 86, 111, 68),
        ("larger-28", 75, 124, 56),
    ]


def test_a_tampered_prediction_is_reported():
    bad = copy.deepcopy(DOC)
    bad["cells"][0]["predicted"] = 0.0

    assert hd.problems(bad)


def test_an_unidentified_direction_cannot_be_called_estimated():
    bad = copy.deepcopy(DOC)
    bad["block_holdout"][2]["status"] = "estimated"

    assert hd.problems(bad)


def test_page_is_current():
    assert hd.PAGE_PATH.read_text(encoding="utf-8") == hd.render(DOC)
    text = hd.PAGE_PATH.read_text(encoding="utf-8")
    assert "0.0139" in text
    assert "0.0142" in text
    assert "not identified" in text
    assert "152" in text
