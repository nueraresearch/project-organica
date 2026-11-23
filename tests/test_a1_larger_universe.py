"""The predeclared 28-tag larger-universe candidate and its preflight."""
import json
from pathlib import Path

from benchmarks import a1_larger_universe as larger
from benchmarks import a1_successor_preflight as preflight
from benchmarks import a1_successor_schema as schema

LAYER = "static"  # reads committed no-arm rows; runs and selects nothing


def _candidate():
    return json.loads(Path("docs/a1_larger_universe_candidate.json").read_text(
        encoding="utf-8"))


def test_construction_is_predeclared_at_28_tags():
    assert larger.TAGS_PER_CELL == 7
    assert len(larger.TAGS) == 28
    assert len(set(larger.TAGS)) == 28
    assert larger.self_test() == []


def test_candidate_has_at_least_144_independent_edges():
    doc = _candidate()
    assert schema.schema_problems(doc) == []
    assert doc["seed_block"] == list(larger.SEEDS)
    assert [row["independent_edges"] for row in doc["summaries"]] == [
        169, 167, 172, 165, 169, 158,
    ]
    assert all(row["independent_edges"] >= 144 for row in doc["summaries"])


def test_larger_universe_fails_the_preflight():
    doc = _candidate()
    result = preflight.evaluate(doc)
    assert result["status"] == "FAIL"
    assert result["seeds_passed"] == 0
    assert [row["C1_ceiling"] for row in result["per_seed"]] == [
        23, 40, 42, 55, 47, 37,
    ]
    assert [row["K_available"] for row in result["per_seed"]] == [
        23, 40, 42, 55, 47, 37,
    ]
    assert [row["target_matching"] for row in result["per_seed"]] == [
        18, 15, 16, 26, 26, 18,
    ]
    assert "TARGET_POOL_BELOW_20" in result["per_seed"][0]["reasons"]


def test_schema_valid_but_gate_fail_is_explicit():
    doc = _candidate()
    result = schema.validate(doc)
    assert result["schema"] == []
    assert result["schema_ok"] is True
    assert result["gate"]["status"] == "FAIL"
    assert "C1_BELOW_60" in result["refusals"]


def test_pages_and_preflight_record_are_current():
    doc = _candidate()
    candidate_page = Path("docs/A1-LARGER-UNIVERSE-CANDIDATE.md").read_text(
        encoding="utf-8")
    assert larger._render(doc, preflight.evaluate(doc)) + "\n" == candidate_page
    record = json.loads(Path("docs/a1_larger_universe_preflight.json").read_text(
        encoding="utf-8"))
    assert record == preflight.build(doc)
    assert Path("docs/A1-LARGER-UNIVERSE-PREFLIGHT.md").read_text(
        encoding="utf-8") == preflight.render(record) + "\n"
    assert "No target is selected, frozen or run." in candidate_page
