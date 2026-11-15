"""Entropy gates the cap-112 window but cannot choose flip_q inside a source."""
import json
from pathlib import Path

from benchmarks import a1_cap112_ordering_term as term

DOC = json.loads(Path("docs/a1_cap112_ordering_term.json").read_text(encoding="utf-8"))


def test_record_is_clean_and_governed_off():
    assert term.problems(DOC) == []
    assert term.self_test() == []
    assert DOC["not_a_result"] is True
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }
    assert DOC["found"]["seeds"] == 12
    assert DOC["found"]["candidates"] == 764
    assert DOC["found"]["unserved"] == 73


def test_entropy_is_one_number_per_source():
    within = DOC["found"]["within_source"]
    assert within["source_cycles"] == 11232
    assert within["entropy_identical"] == within["source_cycles"]


def test_unserved_edges_come_from_higher_entropy_sources():
    found = DOC["found"]
    assert found["served_mean_entropy"] == 3.147455
    assert found["unserved_mean_entropy"] == 3.678359
    assert found["unserved_mean_entropy"] > found["served_mean_entropy"]
    assert found["unserved_mean_probability"] < found["served_mean_probability"]


def test_the_family_split_is_a_probability_split():
    families = {row["family"]: row for row in DOC["per_family"]}
    assert (families["flip_p"]["serve_rate"],
            families["flip_q"]["serve_rate"]) == (0.979112, 0.829396)
    assert families["flip_q"]["mean_entropy"] > families["flip_p"]["mean_entropy"]
    assert families["flip_q"]["mean_probability"] < families["flip_p"]["mean_probability"]
    assert (families["flip_p"]["candidates"],
            families["flip_q"]["candidates"]) == (383, 381)


def test_within_a_source_flip_p_wins_on_probability():
    within = DOC["found"]["within_source"]
    assert within["flip_p_higher_probability"] == 8343
    assert within["flip_p_ranks_first"] == 8491
    assert within["flip_p_higher_probability"] / within["source_cycles"] > 0.7


def test_removing_entropy_does_not_recover_the_window():
    recovered = DOC["found"]["recovered"]
    assert recovered == {"engine": 0, "count_only": 20, "probability_only": 17}
    assert recovered["probability_only"] < DOC["found"]["unserved"] / 2
    assert recovered["count_only"] < DOC["found"]["unserved"] / 2


def test_the_engine_order_reproduces_every_served_set():
    assert DOC["found"]["served"] == sum(
        row["served_ranked"] for row in DOC["per_seed"])
    for row in DOC["per_seed"]:
        assert row["recovered"]["engine"] == 0
        ranked = row["served_ranked"] + row["unserved"]
        assert row["candidates"] - 1 <= ranked <= row["candidates"]
