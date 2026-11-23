"""The machine-readable successor candidate schema and refusal validator."""
import json
from pathlib import Path

from benchmarks import a1_successor_schema as schema

LAYER = "static"  # reads the committed candidate and schema; runs nothing


def test_schema_artifact_and_page_are_current():
    assert json.loads(Path("docs/a1_successor_candidate.schema.json").read_text(
        encoding="utf-8")) == schema.schema()
    page = Path("docs/A1-SUCCESSOR-SCHEMA.md").read_text(encoding="utf-8")
    assert page == schema.page() + "\n"
    assert schema.self_test() == []


def test_live_candidate_is_schema_clean_but_gate_fails():
    doc = json.loads(Path("docs/a1_successor_candidate.json").read_text(
        encoding="utf-8"))
    result = schema.validate(doc)
    assert result["schema"] == []
    assert result["schema_ok"] is True
    assert result["gate"]["status"] == "FAIL"
    assert result["refusals"] == ["C1_BELOW_60"]


def test_validator_rejects_refusal_conditions():
    def codes(mutate):
        doc = schema._fixture()
        mutate(doc)
        return schema.schema_problems(doc)

    assert "REUSED_CONTROL_SEEDS" in codes(
        lambda doc: doc["seed_block"].__setitem__(0, schema.CONTROL_SEEDS[0]))
    assert "SEED_SCREENED_ON_K" in codes(
        lambda doc: doc["selection"].__setitem__("k_screened", True))
    assert "UNDISCLOSED_K_EXPOSURE" in codes(
        lambda doc: doc["selection"].__setitem__("prior_k_exposure", ""))
    assert "TARGETS_SELECTED_BEFORE_PREFLIGHT" in codes(
        lambda doc: doc["selection"].__setitem__("targets_selected", 1))
    assert "PASS_TREATED_AS_GRANT" in codes(
        lambda doc: doc["governance"].__setitem__("freeze", True))
    assert "UNIVERSE_INCONSISTENT" in codes(
        lambda doc: doc["universe"].__setitem__("digest", "0" * 64))

    def reverse(doc):
        first = doc["per_seed"]["1"][0]["edge"]
        a, b = first.split(">", 1)
        doc["per_seed"]["1"].append({"edge": b + ">" + a, "A": True, "K": True})

    assert "REVERSE_DUPLICATE" in codes(reverse)


def test_gate_refusals_are_separate_from_schema_validity():
    doc = schema._fixture()
    for rows in doc["per_seed"].values():
        for row in rows:
            row["K"] = False
    result = schema.validate(doc)
    assert result["schema"] == []
    assert result["schema_ok"] is True
    assert "C1_BELOW_60" in result["refusals"]
    assert "TARGET_POOL_BELOW_20" in result["refusals"]
