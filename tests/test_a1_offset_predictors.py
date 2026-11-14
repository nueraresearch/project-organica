"""Candidate size replaces the free block offset; K completeness does not add."""
import copy
import json
from pathlib import Path

from benchmarks import a1_offset_predictors as op

DOC = json.loads(Path("docs/a1_offset_predictors.json").read_text(encoding="utf-8"))


def test_record_is_clean_and_governed_off():
    assert op.problems(DOC) == []
    assert op.self_test() == []
    assert DOC["not_a_result"] is True
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }
    assert len(DOC["cells"]) == 12
    assert len(DOC["seed_rows"]) == 72
    assert len(DOC["comparisons"]) == 4


def test_candidate_size_matches_or_beats_the_free_offset():
    models = {row["model"]: row for row in DOC["comparisons"]}
    free = models["free_block_offset"]
    size = models["candidate_size"]
    assert (free["cell_loo_rmse"], free["seed_loo_rmse"]) == (
        0.019283, 0.066839)
    assert (size["cell_loo_rmse"], size["seed_loo_rmse"]) == (
        0.018372, 0.066656)
    assert size["cell_loo_rmse"] < free["cell_loo_rmse"]
    assert size["seed_loo_rmse"] < free["seed_loo_rmse"]
    assert size["cell_coefficients"] == [1.90290201, -0.35852459, 0.04698666]


def test_candidate_size_reproduces_the_larger_offset():
    assert DOC["free_block_offsets"] == {
        "current-16": 0.42002218,
        "fresh-16": 0.40646398,
        "larger-28": 0.06883733,
    }
    assert DOC["size_offsets_at_cap0"] == {
        "current-16": 0.413722,
        "fresh-16": 0.412781,
        "larger-28": 0.06882,
    }
    assert abs(DOC["size_offsets_at_cap0"]["larger-28"]
               - DOC["free_block_offsets"]["larger-28"]) < 0.0001


def test_k_completeness_does_not_add_seed_signal():
    models = {row["model"]: row for row in DOC["comparisons"]}
    kc = models["k_completeness"]
    joint = models["candidate_plus_k"]
    size = models["candidate_size"]
    assert (kc["cell_loo_rmse"], kc["seed_loo_rmse"]) == (
        0.018921, 0.086542)
    assert kc["seed_loo_rmse"] > models["free_block_offset"]["seed_loo_rmse"]
    assert joint["seed_loo_rmse"] >= size["seed_loo_rmse"]
    assert abs(joint["seed_loo_rmse"] - size["seed_loo_rmse"]) < 0.0003
    assert joint["cell_loo_rmse"] < size["cell_loo_rmse"]


def test_joint_coefficients_are_collinear_and_unstable():
    joint = next(row for row in DOC["comparisons"]
                 if row["model"] == "candidate_plus_k")
    coef = joint["cell_coefficients"]
    assert abs(coef[0]) > 30
    assert abs(coef[1]) > 4
    assert abs(coef[2]) > 15


def test_within_larger_relationships_are_weak_and_collinear():
    assert DOC["correlations"] == {
        "A_vs_k_completeness_larger": 0.078572,
        "A_vs_log_candidates_larger": -0.011536,
        "k_completeness_vs_log_candidates_larger": -0.865568,
    }
    per_cap = {row["cap"]: row for row in DOC["larger_by_cap"]}
    assert per_cap[20]["A_vs_k_completeness"] == 0.4045
    assert per_cap[80]["A_vs_k_completeness"] == 0.062465
    assert per_cap[112]["A_vs_log_candidates"] == -0.165989


def test_a_tampered_comparison_is_reported():
    bad = copy.deepcopy(DOC)
    bad["comparisons"][1]["cell_loo_rmse"] = 0.0

    assert op.problems(bad)


def test_page_is_current():
    assert op.PAGE_PATH.read_text(encoding="utf-8") == op.render(DOC)
    text = op.PAGE_PATH.read_text(encoding="utf-8")
    assert "Candidate size can replace" in text
    assert "0.0865" in text
    assert "0.079" in text
    assert "-0.866" in text
