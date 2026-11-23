"""Density ties with candidate size; three blocks cannot separate them."""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer
import copy
import json
from pathlib import Path

from benchmarks import a1_offset_density as od

DOC = json.loads(Path("docs/a1_offset_density.json").read_text(encoding="utf-8"))


def test_record_is_clean_and_governed_off():
    assert od.problems(DOC) == []
    assert od.self_test() == []
    assert DOC["not_a_result"] is True
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }
    assert len(DOC["comparisons"]) == 7
    assert len(DOC["cells"]) == 12
    assert len(DOC["seed_rows"]) == 72
    assert DOC["constants"]["density"] == "candidate_edges / tags"


def test_density_is_candidate_edges_per_tag():
    assert DOC["constants"]["tags"] == {
        "current-16": 16, "fresh-16": 16, "larger-28": 28}
    pairs = {row["block"]: row for row in DOC["block_pairs"]}
    assert (pairs["current-16"]["log_candidates"],
            pairs["current-16"]["density"]) == (4.153634, 3.979167)
    assert (pairs["fresh-16"]["log_candidates"],
            pairs["fresh-16"]["density"]) == (4.156258, 3.989583)
    assert (pairs["larger-28"]["log_candidates"],
            pairs["larger-28"]["density"]) == (5.115638, 5.952381)


def test_density_and_size_are_indistinguishable():
    models = {row["model"]: row for row in DOC["comparisons"]}
    density = models["candidate_density"]
    size = models["candidate_size"]
    free = models["free_block_offset"]
    assert (density["cell_loo_rmse"], density["seed_loo_rmse"]) == (
        0.018203, 0.068913)
    assert (size["cell_loo_rmse"], size["seed_loo_rmse"]) == (
        0.018372, 0.066656)
    assert (free["cell_loo_rmse"], free["seed_loo_rmse"]) == (
        0.019283, 0.066839)
    assert density["cell_loo_rmse"] < size["cell_loo_rmse"]
    assert size["cell_loo_rmse"] - density["cell_loo_rmse"] < 0.001
    assert density["seed_loo_rmse"] > size["seed_loo_rmse"]
    assert density["seed_loo_rmse"] - size["seed_loo_rmse"] < 0.005


def test_k_completeness_is_the_only_clearly_worse_summary():
    models = {row["model"]: row for row in DOC["comparisons"]}
    kc = models["k_completeness"]
    assert (kc["cell_loo_rmse"], kc["seed_loo_rmse"]) == (0.018921, 0.086542)
    assert kc["seed_loo_rmse"] > models["candidate_density"]["seed_loo_rmse"]
    assert kc["seed_loo_rmse"] > models["candidate_size"]["seed_loo_rmse"]


def test_adding_density_to_size_does_not_help():
    models = {row["model"]: row for row in DOC["comparisons"]}
    both = models["size_plus_density"]
    size = models["candidate_size"]
    assert (both["cell_loo_rmse"], both["seed_loo_rmse"]) == (
        0.019283, 0.066314)
    assert both["cell_loo_rmse"] > size["cell_loo_rmse"]
    assert both["cell_coefficients"] == [
        -9.42916961, 4.76918983, -2.5031062, 0.04698668]


def test_within_larger_the_two_predictors_are_collinear():
    correlations = DOC["correlations"]
    assert correlations == {
        "A_vs_log_candidates_larger": -0.011536,
        "A_vs_density_larger": -0.012892,
        "A_vs_k_completeness_larger": 0.078573,
        "density_vs_log_candidates_larger": 0.999912,
        "density_vs_k_completeness_larger": -0.870729,
    }
    assert correlations["density_vs_log_candidates_larger"] > 0.999
    larger = [row for row in DOC["seed_rows"] if row["block"] == "larger-28"]
    assert len(larger) == 24
    assert all(row["density"] == round(row["candidate_edges"] / 28, 6)
               for row in larger)


def test_a_tampered_seed_density_is_reported():
    bad = copy.deepcopy(DOC)
    bad["seed_rows"][0]["density"] = 99.0

    assert od.problems(bad)


def test_missing_models_are_reported():
    bad = copy.deepcopy(DOC)
    bad["comparisons"].pop()

    assert od.problems(bad)


def test_page_is_current():
    assert od.PAGE_PATH.read_text(encoding="utf-8") == od.render(DOC)
    text = od.PAGE_PATH.read_text(encoding="utf-8")
    assert "0.0182" in text
    assert "0.0689" in text
    assert "3.9792" in text
    assert "5.9524" in text
    assert "cannot distinguish" in text
