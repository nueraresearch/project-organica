"""At cap 112 the unserved 16-tag edges are flip_q transitions past the window."""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer
import json
from collections import Counter
from pathlib import Path

from benchmarks import a1_prediction_cap112_unserved as unserved

DOC = json.loads(Path("docs/a1_prediction_cap112_unserved.json").read_text(encoding="utf-8"))


def test_record_is_clean_and_governed_off():
    assert unserved.problems(DOC) == []
    assert unserved.self_test() == []
    assert DOC["not_a_result"] is True
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }
    assert len(DOC["seed_rows"]) == 12
    assert len(DOC["unserved_rows"]) == 74
    assert DOC["constants"]["prediction_cap"] == 112
    assert DOC["constants"]["loop_cap"] == 120
    assert DOC["constants"]["support_floor"] == 5


def test_the_window_is_the_binding_constraint():
    found = DOC["found"]
    assert (found["candidate_edges"], found["served"], found["unserved"]) == (
        765, 691, 74)
    assert found["unserved_support_ge_5"] == 74
    assert found["unserved_transitions"] == 73
    assert found["unserved_cooccurrences"] == 0
    assert found["unserved_no_candidate"] == 1


def test_unserved_edges_are_ranked_past_the_transition_share():
    found = DOC["found"]
    assert (found["rank_min"], found["rank_median"], found["rank_max"]) == (
        65, 100, 189)
    bands = {row["band"]: row["unserved"] for row in DOC["by_rank_band"]}
    assert bands == {"1-56": 0, "57-112": 47, "113-224": 26, "225+": 0}
    for row in DOC["unserved_rows"]:
        assert row["served"] is False
        if row["rank"] is not None:
            assert row["rank"] >= 57


def test_the_shortfall_is_a_flip_q_shortfall():
    assert DOC["found"]["families"] == {"flip_q": 66, "flip_p": 8}
    rates = {row["family"]: row["A_rate"] for row in DOC["by_family"]}
    assert (rates["flip_p"], rates["flip_q"]) == (0.979112, 0.827225)
    assert rates["flip_q"] < rates["flip_p"]
    assert Counter(row["family"] for row in DOC["unserved_rows"]) == {
        "flip_q": 66, "flip_p": 8}


def test_every_unserved_edge_is_already_carried():
    assert DOC["found"]["unserved_in_K"] == 74
    assert all(row["K112"] for row in DOC["unserved_rows"])


def test_the_single_non_candidate_is_named():
    rows = [row for row in DOC["unserved_rows"] if row["kind"] == "none"]
    assert len(rows) == 1
    assert rows[0]["edge"] == "slate>willow"
    assert rows[0]["seed"] == 20630103
    assert rows[0]["support"] == 16
    assert rows[0]["reason"] == "no_prediction_candidate"


def test_seed_totals_match_the_edge_rows():
    assert sum(row["unserved"] for row in DOC["seed_rows"]) == 74
    assert sum(row["candidate_edges"] for row in DOC["seed_rows"]) == 765
    assert sum(row["A"] for row in DOC["seed_rows"]) == 691
