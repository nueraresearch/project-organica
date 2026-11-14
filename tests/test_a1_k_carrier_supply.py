"""The carrier-supply trace must expose the top-15 loop window and fail closed."""
import copy
import json
from pathlib import Path

import pytest

from benchmarks import a1_k_carrier_supply as supply

DOC = json.loads(Path("docs/a1_k_carrier_supply.json").read_text(encoding="utf-8"))


def test_record_is_clean_and_governed_off():
    assert supply.problems(DOC) == []
    assert supply.self_test() == []
    assert DOC["not_a_result"] is True
    assert DOC["governance"] == {
        "freeze": False, "grant": False, "run": False, "authorization": "none",
    }
    assert len(DOC["seeds"]) == 18


def test_totals_are_exact():
    totals = DOC["totals"]
    assert totals["candidate_edges"] == 1765
    assert totals["candidate_K"] == 714
    assert totals["candidate_K_loop"] == 653
    assert totals["candidate_K_dream_only"] == 61
    assert totals["all_K_directed"] == 3548
    assert totals["candidate_never_eligible"] == 48
    assert totals["candidate_eligible_never_K"] == 1004
    assert totals["possible_loops"] == 1421231
    assert totals["selected_loops"] == 26932
    assert totals["loop_slot_share"] == 0.01895
    assert totals["cap_cycles"] == 1753


def test_blocks_show_a_fixed_k_total_as_candidates_grow():
    by_label = {block["label"]: block for block in DOC["blocks"]}
    assert (
        by_label["current-16"]["candidate_edges_total"],
        by_label["current-16"]["candidate_K_total"],
        by_label["current-16"]["all_K_directed_total"],
    ) == (382, 228, 980)
    assert (
        by_label["fresh-16"]["candidate_edges_total"],
        by_label["fresh-16"]["candidate_K_total"],
        by_label["fresh-16"]["all_K_directed_total"],
    ) == (383, 242, 1031)
    assert (
        by_label["larger-28"]["candidate_edges_total"],
        by_label["larger-28"]["candidate_K_total"],
        by_label["larger-28"]["all_K_directed_total"],
    ) == (1000, 244, 1537)
    assert by_label["larger-28"]["candidate_coverage_total"] == 0.244
    assert by_label["current-16"]["candidate_coverage_total"] == 0.596859
    assert by_label["fresh-16"]["candidate_coverage_total"] == 0.631854


def test_candidate_k_matches_the_predictor_join_exactly():
    assert [row["summary"]["candidate_K"] for row in DOC["seeds"]] == [
        44, 31, 39, 35, 43, 36,
        40, 37, 46, 42, 39, 38,
        23, 40, 42, 55, 47, 37,
    ]


def test_the_rank_boundary_is_exact():
    loop_k = []
    eligible_not_k = []
    for seed in DOC["seeds"]:
        for row in seed["edges"]:
            if row["loop_K_cycles"]:
                loop_k.append(row)
            if row["eligible"] and not row["K"]:
                eligible_not_k.append(row)
    assert len(loop_k) == 653
    assert len(eligible_not_k) == 1004
    assert all(1 <= row["best_loop_rank"] <= 15 for row in loop_k)
    assert all(row["best_loop_rank"] >= 16 for row in eligible_not_k)
    assert sum(
        row["K"] and not row["eligible"]
        for seed in DOC["seeds"] for row in seed["edges"]) == 1
    assert min(row["best_loop_rank"] for row in eligible_not_k) == 16
    assert max(row["best_loop_rank"] for row in eligible_not_k) == 1217


def test_a_tampered_rank_is_reported():
    bad = copy.deepcopy(DOC)
    target = next(
        row for seed in bad["seeds"] for row in seed["edges"]
        if row["eligible"] and not row["K"])
    target["best_loop_rank"] = 1

    assert supply.problems(bad), "a top-ranked non-K edge must fail"


def test_a_tampered_total_is_reported():
    bad = copy.deepcopy(DOC)
    bad["totals"]["candidate_K"] += 1

    assert supply.problems(bad), "a total that disagrees with the rows must fail"


def test_page_is_current_and_has_no_template_placeholder():
    assert supply.PAGE_PATH.read_text(encoding="utf-8") == supply.render(DOC)
    text = supply.PAGE_PATH.read_text(encoding="utf-8")
    assert "15-loop output window" in text
    assert "median **49**" in text
    assert "%%" not in text
    assert "not a result artifact" in text.lower()
