"""The ten 16-tag failures are transition-only, flip_q-heavy cap truncations."""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer
import copy
import json
from pathlib import Path

from benchmarks import a1_prediction_cap112_decompose as dec

DOC = json.loads(Path("docs/a1_prediction_cap112_decompose.json").read_text(encoding="utf-8"))


def test_record_is_clean_and_governed_off():
    assert dec.problems(DOC) == []
    assert dec.self_test() == []
    assert DOC["not_a_result"] is True
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }
    assert len(DOC["seed_rows"]) == 10


def test_all_missing_edges_are_support_eligible_transitions():
    assert DOC["missing_total"] == 69
    assert DOC["missing_support_ge_5"] == 69
    assert DOC["missing_cap_bound"] == 69
    assert DOC["missing_never"] == 0
    assert DOC["missing_cooccurrence"] == 0
    assert (DOC["missing_rank_min"], DOC["missing_rank_max"]) == (65, 189)
    kinds = {row["label"]: row for row in DOC["kinds"]}
    assert kinds["transition"]["candidate_edges"] == 637
    assert kinds["transition"]["missing"] == 69
    assert "cooccurrence" not in kinds


def test_flip_q_is_the_stable_family_split():
    families = {row["label"]: row for row in DOC["families"]}
    assert (families["flip_p"]["candidate_edges"],
            families["flip_p"]["A112"],
            families["flip_p"]["missing"]) == (319, 312, 7)
    assert (families["flip_q"]["candidate_edges"],
            families["flip_q"]["A112"],
            families["flip_q"]["missing"]) == (318, 256, 62)
    assert families["flip_p"]["missing_never"] == 0
    assert families["flip_q"]["missing_never"] == 0


def test_family_gap_survives_matched_support():
    rows = {(row["family"], row["support_bin"]): row
            for row in DOC["family_support"]}
    assert (rows[("flip_p", "16+")]["candidate_edges"],
            rows[("flip_p", "16+")]["A112"],
            rows[("flip_p", "16+")]["missing"]) == (318, 311, 7)
    assert (rows[("flip_q", "16+")]["candidate_edges"],
            rows[("flip_q", "16+")]["A112"],
            rows[("flip_q", "16+")]["missing"]) == (182, 149, 33)
    assert (rows[("flip_q", "8-15")]["candidate_edges"],
            rows[("flip_q", "8-15")]["A112"],
            rows[("flip_q", "8-15")]["missing"]) == (133, 105, 28)


def test_support_is_not_the_floor():
    support = {row["label"]: row for row in DOC["support_bins"]}
    assert (support["4-7"]["candidate_edges"],
            support["4-7"]["A112"],
            support["4-7"]["missing"]) == (3, 2, 1)
    assert (support["8-15"]["candidate_edges"],
            support["8-15"]["A112"],
            support["8-15"]["missing"]) == (134, 106, 28)
    assert (support["16+"]["candidate_edges"],
            support["16+"]["A112"],
            support["16+"]["missing"]) == (500, 460, 40)


def test_per_seed_counts_and_gaps():
    rows = {(row["block"], row["seed"]): row for row in DOC["seed_rows"]}
    assert rows[("current-16", 20630101)]["A112"] == 57
    assert rows[("current-16", 20630105)]["A112"] == 59
    assert rows[("fresh-16", 20650105)]["A112"] == 52
    assert rows[("fresh-16", 20650106)]["A112"] == 57
    assert all(row["A1000"] == row["candidate_edges"]
               for row in DOC["seed_rows"])
    assert all(row["gap_to_60"] == 60 - row["A112"]
               for row in DOC["seed_rows"])
    assert all(row["missing_cap_bound"] == row["missing"]
               for row in DOC["seed_rows"])


def test_rank_distributions():
    ranks = {row["label"]: row["edges"] for row in DOC["rank_bands"]}
    assert ranks == {"1-20": 455, "21-40": 62, "41-56": 37, "57-112": 14}
    missing = {row["label"]: row["edges"] for row in DOC["missing_rank_bands"]}
    assert missing == {"57-112": 44, "113-1000": 25}


def test_a_tampered_missing_count_is_reported():
    bad = copy.deepcopy(DOC)
    bad["seed_rows"][0]["missing"] += 1

    assert dec.problems(bad), "a missing count inconsistent with the seed total must fail"


def test_page_is_current():
    assert dec.PAGE_PATH.read_text(encoding="utf-8") == dec.render(DOC)
    text = dec.PAGE_PATH.read_text(encoding="utf-8")
    assert "62/69" in text
    assert "transition" in text
    assert "flip_q" in text
