"""An unseen 16-tag block has fresh-16's candidate size but not its level."""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer
import copy
import json
from pathlib import Path

from benchmarks import a1_cap_response_seed_holdout as hd

DOC = json.loads(Path("docs/a1_cap_response_seed_holdout.json").read_text(encoding="utf-8"))


def test_record_is_clean_and_governed_off():
    assert hd.problems(DOC) == []
    assert hd.self_test() == []
    assert DOC["not_a_result"] is True
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }
    assert len(DOC["cells"]) == 4
    assert len(DOC["rows"]) == 24
    assert len(DOC["per_seed"]) == 6
    assert len(DOC["control"]) == 2
    assert DOC["constants"]["seeds"] == [
        20670101, 20670102, 20670103, 20670104, 20670105, 20670106]
    assert DOC["constants"]["caps"] == [20, 40, 80, 112]


def test_the_predictions_are_frozen_from_the_committed_size_model():
    assert DOC["constants"]["size_coefficients"] == [
        1.90290201, -0.35852459, 0.04698666]
    metrics = DOC["metrics"]
    assert metrics["log_candidates"] == 4.156258
    assert metrics["size_offset"] == 0.412781
    assert metrics["fresh16_log_candidates"] == 4.156258
    assert metrics["same_size_as_fresh16"] is True


def test_the_missed_level_is_the_finding():
    metrics = DOC["metrics"]
    assert (metrics["cell_rmse_size"], metrics["cell_max_size"],
            metrics["cell_mean_residual"]) == (0.03213, 0.043216, -0.031263)
    assert metrics["cell_rmse_size"] > metrics["reference_size_cell_loo"]
    assert metrics["cell_rmse_size"] > metrics["reference_shared_cell_loo_16tag"]
    assert (metrics["cell_rmse_current"], metrics["cell_rmse_fresh"]) == (
        0.039212, 0.026024)
    assert metrics["cell_rmse_fresh"] > metrics["reference_shared_cell_loo_16tag"]


def test_per_seed_scatter_is_no_worse_than_at_fitting_time():
    metrics = DOC["metrics"]
    assert (metrics["seed_rmse_size"], metrics["seed_max_size"]) == (
        0.059151, 0.11526)
    assert metrics["seed_rmse_size"] < metrics["reference_size_seed_loo_16tag"]


def test_the_block_sits_below_the_fresh_bracket_at_every_cap():
    residuals = [row["residual_fresh"] for row in DOC["cells"]]
    assert residuals == [-0.036899, -0.024732, -0.017077, -0.021077]
    assert all(value < 0 for value in residuals)
    assert DOC["metrics"]["fresh_bracket_residual_min"] == -0.036899
    assert DOC["metrics"]["fresh_bracket_residual_max"] == -0.017077


def test_the_cells_are_exact():
    cells = {row["cap"]: row for row in DOC["cells"]}
    assert (cells[20]["observed"], cells[20]["predicted_size"],
            cells[20]["residual_size"]) == (0.579696, 0.622912, -0.043216)
    assert (cells[112]["observed"], cells[112]["predicted_size"],
            cells[112]["residual_size"]) == (0.882647, 0.910041, -0.027394)
    assert [row["cap"] for row in DOC["cells"]] == [20, 40, 80, 112]


def test_candidate_streams_are_the_fixed_rule_size():
    counts = [row["candidate_edges"] for row in DOC["per_seed"]]
    assert counts == [63, 64, 64, 64, 64, 64]
    assert all(row["candidate_edges"] == 63 or row["candidate_edges"] == 64
               for row in DOC["rows"])


def test_control_reproduces_committed_counts():
    assert all(row["matches_committed"] for row in DOC["control"])
    assert [(row["seed"], row["A"], row["K"], row["A_and_K"])
            for row in DOC["control"]] == [
        (20630101, 51, 64, 51), (20650101, 56, 64, 56)]


def test_a_tampered_prediction_is_reported():
    bad = copy.deepcopy(DOC)
    bad["cells"][0]["predicted_size"] = 0.0

    assert hd.problems(bad)


def test_a_tampered_seed_row_is_reported():
    bad = copy.deepcopy(DOC)
    bad["rows"][0]["A_coverage"] = 0.0

    assert hd.problems(bad)


def test_the_page_is_current():
    assert hd.PAGE_PATH.read_text(encoding="utf-8") == hd.render(DOC)
    text = hd.PAGE_PATH.read_text(encoding="utf-8")
    assert "0.0321" in text
    assert "4.156258" in text
    assert "0.5797" in text
    assert "0.0171" in text
