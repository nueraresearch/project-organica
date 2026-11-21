"""Engine-side quantities against the per-seed 16-tag level."""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer
import json
from pathlib import Path

from benchmarks import a1_engine_side_join as join

DOC = json.loads(Path("docs/a1_engine_side_join.json").read_text(encoding="utf-8"))


def test_record_is_clean_and_governed_off():
    assert join.problems(DOC) == []
    assert join.self_test() == []
    assert DOC["not_a_result"] is True
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }
    assert DOC["found"]["seeds"] == 12
    assert DOC["found"]["blocks"] == {"current-16": 6, "fresh-16": 6}


def test_the_join_passes_its_controls():
    found = DOC["found"]
    assert found["served_control_r"] == 0.8322
    assert found["candidate_control_r"] == 0.4209
    assert found["candidate_control_p"] == 0.18104


def test_the_loop_window_does_not_track_the_level():
    found = DOC["found"]
    assert found["loop_window_tracks"] == 0
    loop = [row for row in DOC["results"]
            if row["key"] in (join.QUANTITIES[i][0] for i in range(len(join.QUANTITIES)))
            and row["family"] == "loop window"]
    assert len(loop) == 9
    assert all(abs(row["pooled_r"]) < 0.35 for row in loop)


def test_the_ordering_terms_do_not_track_the_level():
    found = DOC["found"]
    assert found["ordering_tracks"] == 1
    terms = {row["key"]: row for row in DOC["results"]}
    for key in ("mean_entropy_served", "mean_probability_served",
                "mean_count_served", "probability_mass_served",
                "mass_fraction_served"):
        assert terms[key]["tracks"] is False


def test_the_one_tracker_is_the_selection_itself():
    found = DOC["found"]
    assert found["tracks"] == ["mean_rank_fraction_served"]
    assert found["best_pooled_r"] == -0.8743
    assert found["best_block_r"] == {"current-16": -0.9012, "fresh-16": -0.8701}
    row = next(item for item in DOC["results"]
               if item["key"] == "mean_rank_fraction_served")
    assert row["permutation_p"] == 0.0026
    assert row["partial_r_given_served"] == -0.9628
    assert row["permutation_p"] <= found["bonferroni_threshold"]


def test_the_rank_fraction_is_not_the_served_prefix_restated():
    found = DOC["found"]
    assert found["rank_fraction_vs_prefix_r"] == -0.460592
    assert found["rank_fraction_vs_prefix_max_gap"] == 0.353549


def test_the_rule_is_a_threshold_over_registered_quantities():
    found = DOC["found"]
    assert found["quantities"] == 20
    assert found["tested"] == 17
    assert abs(found["bonferroni_threshold"] - 0.05 / 17) < 1e-6
    assert found["min_abs_r"] == 0.6
    keys = [row["key"] for row in DOC["results"]]
    assert len(set(keys)) == len(keys)
