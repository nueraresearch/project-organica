"""No within-block candidate-space quantity tracks the equal-size 16-tag level."""
import json
from pathlib import Path

from benchmarks import a1_within_block_level as level

DOC = json.loads(Path("docs/a1_within_block_level.json").read_text(encoding="utf-8"))


def test_record_is_clean_and_governed_off():
    assert level.problems(DOC) == []
    assert level.self_test() == []
    assert DOC["not_a_result"] is True
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }
    assert len(DOC["blocks"]) == 3
    assert len(DOC["rows"]) == 18
    assert DOC["constants"]["caps"] == [20, 40, 80, 112]


def test_the_blocks_are_equal_size_and_complete():
    for row in DOC["rows"]:
        assert row["candidate_edges"] == row["committed_candidates"]
        assert row["candidate_edges"] in (63, 64)
        assert row["k_completeness"] == 1.0
        assert row["cell_pairs"] == 9


def test_the_level_gap_is_within_seed_noise():
    blocks = {row["label"]: row for row in DOC["blocks"]}
    assert [blocks[label]["offset_mean"] for label in
            ("current-16", "fresh-16", "seed-2067")] == [
                0.420022, 0.406464, 0.381518]
    gaps = {tuple(row["blocks"]): row for row in DOC["gap_tests"]}
    assert gaps[("current-16", "fresh-16")]["z"] == 0.392
    assert gaps[("current-16", "seed-2067")]["z"] == 1.677
    assert gaps[("fresh-16", "seed-2067")]["z"] == 0.753
    assert DOC["found"]["level_spread"] == 0.038504


def test_no_quantity_tracks_the_level():
    assert DOC["found"]["any_statistics_track"] == 0
    assert DOC["found"]["any_sign_consistent"] == 0
    ordered = [row["name"] for row in DOC["statistics"]
               if row["orders_like_level_all"]]
    assert set(ordered) == {"median_support", "tag_entropy", "frac_le_10"}
    for row in DOC["statistics"]:
        assert not row["tracks"]


def test_the_block_means_are_flat_where_the_level_is_not():
    stats = {row["name"]: row for row in DOC["statistics"]}
    assert stats["mean_support"]["block_means"] == [
        22.897156, 22.609499, 22.618469]
    assert stats["support_mass"]["block_means"] == [
        1457.833333, 1443.166667, 1443.833333]
    assert stats["tag_entropy"]["block_means"] == [
        3.905986, 3.902093, 3.895547]
    assert stats["cell_pairs"]["block_means"] == [9.0, 9.0, 9.0]
    assert stats["mean_support"]["relative_spread"] < 0.02


def test_the_support_account_fails_on_its_own_clearest_seed():
    row = next(item for item in DOC["rows"] if item["seed"] == 20650105)
    assert row["block"] == "fresh-16"
    assert row["offset"] == 0.258874
    assert row["mean_support"] == 23.047619
    assert row["offset"] == min(item["offset"] for item in DOC["rows"]
                                if item["block"] == "fresh-16")
    assert row["mean_support"] == max(item["mean_support"] for item in DOC["rows"]
                                      if item["block"] == "fresh-16")
