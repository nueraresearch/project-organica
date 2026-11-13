"""PRESENCE-CAP-LADDER-1 is frozen, unrun and internally consistent."""
from __future__ import annotations

LAYER = "static"

from benchmarks import presence_cap_ladder_prereg as block
from benchmarks.presence_cap_experiment import seed_collisions


def test_record_is_frozen_and_unrun():
    doc = block.record()
    assert doc["prereg"] == "PRESENCE-CAP-LADDER-1"
    assert doc["status"] == "FROZEN, NOT RUN"
    assert doc["frozen_on"] == "2026-11-12"
    assert doc["no_cells_run"] is True
    assert doc["authorisation"]["granted"] is False
    assert doc["runner"]["built"] is True
    assert doc["runner"]["planned_module"] == "benchmarks.presence_cap_ladder_arm"
    assert doc["runner"]["cells_run"] == 0
    assert not block.RESULT.exists()


def test_ladder_design():
    design = block.record()["design"]
    assert design["caps"] == [40, 56, 80, 112]
    assert len(design["seeds"]) == 6
    assert design["cells"] == len(design["caps"]) * len(design["seeds"]) == 24
    assert design["cycles"] == 120
    assert design["primary_cap"] == 80
    assert [(r["cap"], r["transition_floor"], r["cooccurrence_cap"])
            for r in design["rungs"]] == [
                (40, 20, 20), (56, 28, 28), (80, 40, 40), (112, 56, 56)]


def test_false_admission_bar_is_not_fitted():
    rule = block.record()["false_admission"]
    assert rule["baseline_cap"] == 40
    assert rule["margin"] == 0.10
    assert "seed-cluster bootstrap" in rule["comparison"]
    assert "not in the seed's present world transitions" in rule["definition"]
    assert "collateral service" in rule["not_the_same_as"]


def test_all_declared_verdicts_have_a_row():
    verdicts = {row["verdict"] for row in block.record()["decision_table"]}
    assert set(block.VERDICTS) <= verdicts
    assert "RECOVERY WITH COST" in verdicts
    assert "RECOVERY AT 112 ONLY" in verdicts


def test_page_is_rendered_from_the_record():
    assert block.problems() == []
    assert "page stale" in block.problems(page="stale")


def test_seed_block_is_fresh():
    assert seed_collisions(list(block.SEEDS), allow=(block.RECORD, block.PAGE)) == {}


def test_record_is_engine_stamped():
    doc = block.record()
    for field in ("engine_version", "engine_commit", "engine_sha256", "runner"):
        assert doc.get(field)
