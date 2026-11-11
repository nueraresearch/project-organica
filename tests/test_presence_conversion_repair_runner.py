"""The conversion-2 harness must exist, plan fourteen runs, and refuse a tampered N1."""
LAYER = "synthetic"

import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import presence_conversion_repair_runner as runner  # noqa: E402


def test_the_plan_is_the_twelve_cells_the_witness_and_the_rerun():
    plan = runner.planned()

    assert len(plan) == 14
    seeds = runner.design()["seeds"]
    assert plan[:12] == [(seed, arm) for seed in seeds for arm in ("off", "on")]
    assert plan[12:] == [(20261100, "off"), (seeds[0], "on")]


def test_the_n1_comparison_is_served_window_identity_per_seed():
    parts = {}
    for seed in runner.design()["seeds"]:
        parts[seed] = {arm: runner.load(seed, arm) for arm in ("plain", "off", "on")}
    tampered = copy.deepcopy(parts)
    tampered[runner.design()["seeds"][0]]["on"]["windows"][0] = [["x", "y"]]

    def n1(cells):
        return [seed for seed in cells if cells[seed]["on"]["windows"] != cells[seed]["plain"]["windows"]]

    assert n1(parts) == []
    assert n1(tampered) == [runner.design()["seeds"][0]]


def test_the_result_and_page_are_current():
    art = json.loads(runner.ARTIFACT.read_text(encoding="utf-8"))

    assert art["kind"] == runner.KIND
    assert len(art["cells"]) == 12
    assert art["verdict"] in ("SERVED NOT ENGINE", "OBSERVATION LEAKS", "VOID",
                              "CONVERSION STAGE MEASURED")
    assert runner.page() == runner.PAGE.read_text(encoding="utf-8")


def test_the_stage_table_counts_candidates_from_the_recorded_universe():
    art = json.loads(runner.ARTIFACT.read_text(encoding="utf-8"))
    cap = int(runner.prereg()["engine"]["cap"])
    for row in art["stage_table"]:
        derived = runner.stage_row(runner.load(row["seed"], "on"), cap)
        for key in ("present", "constructed", "below_minimum", "served_ever", "never_served",
                    "never_served_within_transition_budget", "never_served_rank_half_to_cap",
                    "never_served_rank_above_cap", "asserted_final", "unexplained"):
            assert row[key] == derived[key], (row["seed"], key)
        assert row["constructed"] + row["below_minimum"] == row["present"]
        assert (row["never_served_within_transition_budget"] + row["never_served_rank_half_to_cap"]
                + row["never_served_rank_above_cap"]) == row["never_served"]
        assert row["never_served_relations"]["cooccurrence"] == 0


def test_the_construct_bucket_moves_when_the_recorded_universe_is_taken_away():
    art = json.loads(runner.ARTIFACT.read_text(encoding="utf-8"))
    cap = int(runner.prereg()["engine"]["cap"])
    cell = copy.deepcopy(runner.load(art["stage_table"][0]["seed"], "on"))
    before = runner.stage_row(cell, cap)

    cell["universe"] = []
    after = runner.stage_row(cell, cap)

    assert before["constructed"] > before["served_ever"]
    assert after["constructed"] == 0
    assert after["below_minimum"] == before["present"]


def test_the_recorded_universe_order_is_the_served_order_within_each_block():
    art = json.loads(runner.ARTIFACT.read_text(encoding="utf-8"))
    sem = art["rank_semantics"]

    assert sem["cycles"] == 720
    assert sem["served_is_order_subsequence"] == 720
    assert sem["served_transitions_are_prefix"] == 720
    assert sem["served_cooccurrences_are_prefix"] == 720
    assert sem["max_served_transition_rank"] <= sem["max_allocated_transitions"] == 20
    assert sem["max_served_cooccurrence_rank"] > sem["max_allocated_transitions"]
    assert sem["never_served_relations"] == ["transition"]
    assert sem["never_served_within_transition_budget"] == 0
    fresh = runner.rank_semantics(runner.design()["seeds"], runner.prereg()["engine"]["cap"])
    assert all(sem[key] == value for key, value in fresh.items())
    assert sem["in_cap_never_served"] == 62
    assert sem["in_cap_never_served_within_served_transitions"] == 0
    assert sem["in_cap_asserted_without_admission"] == 10
    assert sem["in_cap_asserted_without_admission_within_served_transitions"] == 0
    assert sem["closest_in_cap_miss_gap"] == 1
    assert sem["unlabelled_universe_rows"] == 0
    assert sem["cycles_with_contiguous_relation_blocks"] == 720
