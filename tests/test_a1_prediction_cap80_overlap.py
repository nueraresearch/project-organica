"""The two cap-80 larger-28 joint failures are selective K-coverage losses."""
import copy
import json
from pathlib import Path

from benchmarks import a1_prediction_cap80_overlap as ol

DOC = json.loads(Path("docs/a1_prediction_cap80_overlap.json").read_text(encoding="utf-8"))


def test_record_is_clean_and_governed_off():
    assert ol.problems(DOC) == []
    assert ol.self_test() == []
    assert DOC["not_a_result"] is True
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }
    assert len(DOC["seed_rows"]) == 6


def test_block_totals_and_overlap_split():
    s = DOC["summary"]
    assert (s["A_total"], s["K_total"], s["A_and_K_total"]) == (498, 732, 394)
    assert (s["A_only_total"], s["K_only_total"]) == (104, 338)
    assert (s["C1_marginal_pass"], s["C1_joint_pass"]) == (6, 4)
    assert s["A_total"] - s["A_only_total"] == s["A_and_K_total"]
    assert s["K_total"] - s["K_only_total"] == s["A_and_K_total"]


def test_per_seed_overlap_counts():
    rows = {row["seed"]: row for row in DOC["seed_rows"]}
    assert {seed: (row["A"], row["K"], row["A_and_K"], row["A_only"],
                   row["K_only"])
            for seed, row in rows.items()} == {
        20660101: (86, 111, 68, 18, 43),
        20660102: (75, 124, 56, 19, 68),
        20660103: (83, 105, 51, 32, 54),
        20660104: (88, 138, 77, 11, 61),
        20660105: (91, 121, 72, 19, 49),
        20660106: (75, 133, 70, 5, 63),
    }


def test_both_joint_failures_clear_a_marginally():
    rows = {row["seed"]: row for row in DOC["seed_rows"]}
    assert all(row["C1_marginal_pass"] for row in rows.values())
    for seed in (20660102, 20660103):
        assert not rows[seed]["C1_joint_pass"]
        assert rows[seed]["A"] >= 60
        assert rows[seed]["K"] >= 60
        assert rows[seed]["full_K_coverage_joint"] == rows[seed]["A"]


def test_k_coverage_explains_the_failures():
    rows = {row["seed"]: row for row in DOC["seed_rows"]}
    assert (rows[20660102]["A_and_K"], rows[20660102]["A_only"],
            rows[20660102]["min_K_repair"]) == (56, 19, 4)
    assert (rows[20660103]["A_and_K"], rows[20660103]["A_only"],
            rows[20660103]["min_K_repair"]) == (51, 32, 9)
    assert rows[20660102]["K_coverage_of_A"] == 0.746667
    assert rows[20660103]["K_coverage_of_A"] == 0.614458
    passes = [row for row in rows.values() if row["C1_joint_pass"]]
    assert min(row["K_coverage_of_A"] for row in passes) == 0.790698
    assert DOC["summary"]["joint_failures"] == [20660102, 20660103]
    assert DOC["summary"]["joint_failure_A_only"] == [19, 32]
    assert DOC["summary"]["joint_failure_min_K_repair"] == [4, 9]


def test_support_composition_sums_to_the_split():
    s = DOC["summary"]
    a_only = {row["label"]: row["edges"] for row in s["A_only_by_support"]}
    k_only = {row["label"]: row["edges"] for row in s["K_only_by_support"]}
    assert a_only == {"0": 0, "1": 0, "2-3": 7, "4-7": 35, "8-15": 59, "16+": 3}
    assert k_only == {"0": 0, "1": 2, "2-3": 30, "4-7": 168, "8-15": 136, "16+": 2}
    assert sum(a_only.values()) == s["A_only_total"]
    assert sum(k_only.values()) == s["K_only_total"]


def test_exact_failure_edges_include_top_ranked_omissions():
    rows = {row["seed"]: row for row in DOC["seed_rows"]}
    edges = {(edge["edge"], edge["A_rank"])
             for row in rows.values() if not row["C1_joint_pass"]
             for edge in row["A_only_edges"]}
    assert ("cedar>tagii", 1) in edges
    assert ("taghh>fern", 1) in edges
    assert ("yarrow>crimson", 1) in edges
    assert len(edges) == 51


def test_a_tampered_split_is_reported():
    bad = copy.deepcopy(DOC)
    bad["seed_rows"][1]["A_only"] += 1

    assert ol.problems(bad), "A-only must equal A - A∩K"


def test_page_is_current():
    assert ol.PAGE_PATH.read_text(encoding="utf-8") == ol.render(DOC)
    text = ol.PAGE_PATH.read_text(encoding="utf-8")
    assert "20660102" in text
    assert "20660103" in text
    assert "4" in text and "9" in text
    assert "A\\K" in text
