"""The N=20 competent target-selection rule, without selecting targets."""
import json
from pathlib import Path

from benchmarks import a1_n20_competent_selection as rule

LAYER = "static"  # reads committed no-arm artifacts; selects and runs nothing


def _artifact():
    return json.loads(
        Path("docs/a1_n20_competent_selection_prereg.json").read_text(encoding="utf-8")
    )


def test_rule_record_is_clean_and_draft_only():
    doc = _artifact()
    assert rule.problems(doc) == []
    assert doc["status"].startswith("DRAFT — RULE PRE-REGISTERED")
    assert doc["rule"]["selection_performed"] is False
    assert doc["rule"]["targets_selected"] == 0
    assert doc["rule"]["frozen"] is False
    assert doc["rule"]["granted"] is False
    assert doc["rule"]["run"] is False


def test_feasibility_counts_are_exact():
    feasibility = _artifact()["feasibility"]
    assert [row["competent_candidates"] for row in feasibility["per_seed"]] == [
        32, 23, 36, 27, 35, 33,
    ]
    assert [row["current_n4_competent"] for row in feasibility["per_seed"]] == [
        2, 3, 3, 1, 2, 1,
    ]
    assert [row["current_n4_dropped"] for row in feasibility["per_seed"]] == [
        2, 1, 1, 3, 2, 3,
    ]
    assert [row["new_rows_needed"] for row in feasibility["per_seed"]] == [
        18, 17, 17, 19, 18, 19,
    ]
    assert [row["max_cap_matching"] for row in feasibility["per_seed"]] == [
        32, 23, 36, 27, 35, 33,
    ]
    assert feasibility["min_competent_candidates"] == 23
    assert feasibility["max_competent_candidates"] == 36
    assert feasibility["min_max_cap_matching"] == 23
    assert feasibility["max_max_cap_matching"] == 36
    assert feasibility["seeds_feasible"] == 6
    assert feasibility["current_n4_competent"] == 12
    assert feasibility["current_n4_dropped"] == 12
    assert feasibility["expected_new_rows"] == 108


def test_matching_respects_the_endpoint_cap():
    edges = [("a", "b"), ("a", "c"), ("a", "d"), ("a", "e")]
    assert rule._max_flow(edges, {"a": 1}) == 1
    assert rule._max_flow(edges, {"a": 2, "e": 1}) == 3


def test_rule_does_not_preserve_the_carrier_missing_n4_rows():
    doc = _artifact()
    rule_text = doc["rule"]["preserves_current_n4"]
    assert "carrier-missing" in rule_text
    assert "not a superset" in rule_text
    assert doc["consequences"]["estimand"].startswith("Changes the target population")
    assert "31-44" in doc["consequences"]["c1"]


def test_no_target_selection_artifact_exists():
    assert not Path("docs/a1_n20_competent_target_selection.json").exists()
    assert not Path("docs/a1_n20_competent_targets.json").exists()


def test_page_is_rendered_and_self_test_is_clean():
    doc = _artifact()
    page = Path("docs/A1-N20-COMPETENT-SELECTION.md").read_text(encoding="utf-8")
    assert page == rule.render(doc) + "\n"
    assert "pre-treatment but not future-blind" in page
    assert "6/6" in page
    assert rule.self_test() == []
