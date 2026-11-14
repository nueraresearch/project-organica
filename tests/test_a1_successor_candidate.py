"""The fresh-seed successor candidate and its preflight result."""
import json
from pathlib import Path

from benchmarks import a1_successor_candidate as candidate
from benchmarks import a1_successor_preflight as preflight

LAYER = "static"  # reads committed no-arm rows; runs and selects nothing


def _artifact():
    return json.loads(
        Path("docs/a1_successor_candidate.json").read_text(encoding="utf-8")
    )


def test_candidate_is_predeclared_and_not_screened_on_k():
    doc = _artifact()
    assert candidate.problems(doc) == []
    assert doc["status"] == "CANDIDATE SPEC — NO ARM, NO TARGET, NOT FROZEN, NOT RUN"
    assert doc["seed_block"] == list(candidate.SEEDS)
    assert doc["selection"]["targets_selected"] == 0
    assert doc["selection"]["boundary_safe"] is True
    assert "fixed before K was measured" in doc["selection"]["screen"]
    assert doc["per_seed"].keys() == {str(seed) for seed in candidate.SEEDS}


def test_candidate_rows_and_preflight_are_exact():
    doc = _artifact()
    result = preflight.evaluate(doc)
    assert result["status"] == "FAIL"
    assert [row["independent_edges"] for row in result["per_seed"]] == [
        64, 64, 64, 64, 63, 64,
    ]
    assert [row["A_available"] for row in result["per_seed"]] == [
        49, 46, 54, 53, 31, 46,
    ]
    assert [row["K_available"] for row in result["per_seed"]] == [
        40, 37, 46, 42, 39, 38,
    ]
    assert [row["C1_ceiling"] for row in result["per_seed"]] == [
        40, 37, 46, 42, 31, 38,
    ]
    assert [row["gap_to_60"] for row in result["per_seed"]] == [
        20, 23, 14, 18, 29, 22,
    ]
    assert result["seeds_passed"] == 0


def test_candidate_result_is_not_a_freeze_or_run():
    doc = _artifact()
    assert doc["baseline"]["treatment"] == "none"
    assert doc["baseline"]["cycles"] == 120
    assert doc["selection"]["targets_selected"] == 0
    assert "not a successor design adopted" in candidate.render(doc)
    assert "No target is selected, frozen or run." in candidate.render(doc)


def test_candidate_page_and_self_test():
    doc = _artifact()
    page = Path("docs/A1-SUCCESSOR-CANDIDATE.md").read_text(encoding="utf-8")
    assert page == candidate.render(doc) + "\n"
    assert "20650101" in page
    assert "**`FAIL`** — 0/6 seeds pass." in page
    assert candidate.self_test() == []
