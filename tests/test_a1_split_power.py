"""Seeds per split block the offset discriminator needs at a stated error rate."""
import json
from pathlib import Path

from benchmarks import a1_split_power as power

DOC = json.loads(Path("docs/a1_split_power.json").read_text(encoding="utf-8"))


def test_record_is_clean_and_governed_off():
    assert power.problems(DOC) == []
    assert power.self_test() == []
    assert DOC["not_a_result"] is True
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }


def test_the_estimand_is_the_committed_differential():
    found = DOC["found"]
    assert found["gap"] == -0.11638
    assert found["size_gap"] == 0.0
    assert DOC["constants"]["floor"] == 0.05
    assert DOC["constants"]["ceiling"] == 0.09


def test_the_primary_design_number():
    found = DOC["found"]
    assert found["primary_sigma"] == 0.066656
    assert found["seeds_size_at_primary"] == 6
    assert found["seeds_density_at_primary"] == 9
    assert found["seeds_both_at_primary"] == 9
    assert found["range_across_sigma"] == [2, 11]


def test_six_seeds_per_block_miss_the_convention():
    found = DOC["found"]
    assert found["committed_seeds_per_block"] == 6
    assert found["committed_se"] == 0.038484
    assert 0.80 < found["committed_power_size"] < 0.85
    assert 0.74 < found["committed_power_density"] < 0.79
    assert found["committed_power_density"] < 0.80


def test_the_band_edges_drive_the_cost_not_the_model_gap():
    found = DOC["found"]
    margin = abs(found["gap"]) - 0.09
    assert abs(margin - 0.02638) < 1e-9
    assert margin < abs(found["gap"]) / 4


def test_pairing_and_the_level_alternative_are_consistent():
    pairing = [row["seeds_both_branches"] for row in DOC["pairing"]]
    assert pairing == sorted(pairing, reverse=True)
    assert pairing[0] == 9
    assert pairing[-1] == 4
    for row in DOC["level_alternative"]:
        assert row["seeds_at_half_gap"] == 2
        assert row["model_gap"] > 0.3


def test_a_stricter_rate_never_asks_for_fewer_seeds():
    for sigma in DOC["constants"]["sigma_grid"]:
        seeds = [row["seeds_both_branches"] for row in DOC["rows"]
                 if row["sigma"] == sigma]
        assert seeds == sorted(seeds)
