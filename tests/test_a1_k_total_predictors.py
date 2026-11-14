"""The absolute-K predictor join is descriptive and mostly negative."""
import json
from pathlib import Path

from benchmarks import a1_k_total_predictors as predictors

DOC = json.loads(Path("docs/a1_k_total_predictors.json").read_text(
    encoding="utf-8"))


def test_record_is_clean_and_governed_off():
    assert predictors.problems(DOC) == []
    assert predictors.self_test() == []
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }
    assert len(DOC["seed_rows"]) == 18
    assert {row["block"] for row in DOC["seed_rows"]} == {
        "current-16", "fresh-16", "larger-28",
    }


def test_absolute_k_is_seed_specific_not_edge_scaled():
    ks = {
        block: [row["K_available"] for row in DOC["seed_rows"]
                if row["block"] == block]
        for block in ("current-16", "fresh-16", "larger-28")
    }
    assert ks["current-16"] == [44, 31, 39, 35, 43, 36]
    assert ks["fresh-16"] == [40, 37, 46, 42, 39, 38]
    assert ks["larger-28"] == [23, 40, 42, 55, 47, 37]
    candidate = next(
        row for row in DOC["correlations"] if row["feature"] == "candidate_edges")
    assert candidate["pooled_rho"] == 0.318015
    assert {entry["block"]: entry["rho"] for entry in candidate["within_block"]}[
        "larger-28"] == 0.028989


def test_a_is_best_but_barely_beats_the_baseline():
    best = DOC["best_observed"]
    assert best["model"] == "A_available"
    assert best["mae"] == 4.653332
    assert best["mean_baseline_mae"] == 4.814815
    assert best["gain_vs_baseline"] == 0.161483
    assert best["pre_run_model"] == "median_U"
    assert best["pre_run_mae"] == 5.451914
    assert best["pre_run_gain_vs_baseline"] == -0.637099


def test_lofo_shows_the_edge_count_failure():
    rows = {row["feature"]: row for row in DOC["leave_one_world_out"]}
    assert rows[None]["mae"] == 4.814815
    assert rows["candidate_edges"]["mae"] == 177.210978
    assert rows["candidate_edges"]["by_block"]["larger-28"] == 524.518519
    assert rows["A_available"]["mae"] == 4.653332


def test_page_is_current_and_states_the_negative_result():
    assert predictors.render(DOC) + "\n" == Path(
        "docs/A1-K-TOTAL-PREDICTORS.md").read_text(encoding="utf-8")
    text = Path("docs/A1-K-TOTAL-PREDICTORS.md").read_text(encoding="utf-8")
    assert "absolute K is seed-specific under these structural summaries" in text
    assert "candidate_edges" in text and "177.21" in text
    assert "improves on the mean baseline by only **0.16**" in text
    assert "does not prove no predictor exists" in text
