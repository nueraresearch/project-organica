"""Pruning's share of edge deaths must be a measurement, not a total over every generation.

The engine's `pruned` counter sums every surviving candidate type, so it could not answer what
the attribution record needed. This harness observes the retirement write, reconciles it against
that counter on every cycle, and follows each peak edge to a terminal category. The checks below
hold the split to the engine's own number, and hold the gate able to fail.
"""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import json
from pathlib import Path

import pytest

from benchmarks import pruning_by_type as pbt

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = ROOT / "docs" / "pruning_by_type.json"


@pytest.fixture(scope="module")
def artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_the_split_reconciles_with_the_engines_own_counter(artifact):
    for arm, row in artifact["arms"].items():
        assert row["reconciliation_mismatches"] == 0, arm
        assert row["seeds"], arm
    for path in sorted(pbt.PARTS.glob("cell_*.json")):
        cell = json.loads(path.read_text(encoding="utf-8"))
        assert cell["reconciliation_mismatches"] == [], path.name
        for row in cell["per_cycle"]:
            assert row["engine_pruned"] == row["observed_retired"], (path.name, row["cycle"])


def test_prediction_candidates_are_in_the_retired_type_table(artifact):
    engine = artifact["arms"]["engine"]
    assert engine["retired_by_type"].get("prediction_candidate", 0) > 0
    assert len(engine["retired_by_type"]) >= 2, (
        "a single type would mean the split says nothing the total did not")


def test_every_peak_edge_lands_in_exactly_one_terminal_category(artifact):
    for arm, row in artifact["arms"].items():
        counted = (row["terminal"].get("pruned", 0)
                   + row["terminal"].get("withdrawn_without_pruning", 0)
                   + row["terminal"].get("alive", 0))
        assert counted == row["peak_edges"], arm
        assert row["deaths"] == counted - row["terminal"].get("alive", 0), arm


def test_the_share_is_derived_from_the_counts(artifact):
    engine = artifact["arms"]["engine"]
    expected = round(engine["terminal"]["pruned"] / engine["deaths"], 4)
    assert engine["pruned_share_of_deaths"] == expected
    assert 0.0 < expected <= 1.0


def test_the_engine_arm_prunes_most_of_the_structures_that_die(artifact):
    """The finding: pruning is not a bystander in this collapse, it is the terminal event."""
    share = artifact["arms"]["engine"]["pruned_share_of_deaths"]
    assert share > 0.5, share
    assert artifact["label"] == "PRUNING_PARTIAL"


def test_the_gates_pass_and_the_label_is_not_the_instrument_failing(artifact):
    assert all(artifact["gates"].values()), artifact["gates"]
    assert artifact["label"] != "INSTRUMENT_INVALID"


def test_the_page_is_generated_from_the_artifact(artifact):
    page = (ROOT / "docs" / "PRUNING-BY-TYPE.md").read_text(encoding="utf-8")
    assert page == pbt.render(artifact)
    assert "{" not in page and "}" not in page


def test_the_check_refuses_a_label_the_measurement_does_not_support(tmp_path, monkeypatch):
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    bad = tmp_path / "pruning_by_type.json"
    bad.write_text(json.dumps(dict(stored, label="PRUNING_IS_TERMINAL"), indent=2),
                   encoding="utf-8")
    monkeypatch.setattr(pbt, "ARTIFACT", bad)
    assert pbt.check() != []


def test_the_check_passes_on_the_committed_artifact():
    assert pbt.check() == []
