"""Descriptive K-availability decomposition over the six no-arm seeds."""
import json
from pathlib import Path

from benchmarks import a1_k_decomposition as report

LAYER = "static"  # reads committed no-arm artifacts; runs and selects nothing


def _artifact():
    return json.loads(
        Path("docs/a1_k_decomposition.json").read_text(encoding="utf-8")
    )


def test_totals_and_k_specific_gap():
    doc = _artifact()
    assert report.problems(doc) == []
    totals = doc["totals"]
    assert totals["candidate_edges"] == 382
    assert totals["A_available"] == 281
    assert totals["K_available"] == 228
    assert totals["A_and_K"] == 186
    assert totals["K_only_missing"] == 95
    assert totals["A_only_missing"] == 42
    assert totals["both_missing"] == 59
    assert totals["K_rate"] == 0.596859
    assert totals["A_rate"] == 0.735602


def test_per_seed_path_counts_are_exact():
    rows = {row["seed"]: row for row in _artifact()["per_seed"]}
    assert [rows[seed]["A_available"] for seed in report.SEEDS] == [
        44, 44, 52, 43, 49, 49,
    ]
    assert [rows[seed]["K_available"] for seed in report.SEEDS] == [
        44, 31, 39, 35, 43, 36,
    ]
    assert [rows[seed]["A_and_K"] for seed in report.SEEDS] == [
        32, 23, 36, 27, 35, 33,
    ]
    assert [rows[seed]["K_only_missing"] for seed in report.SEEDS] == [
        12, 21, 16, 16, 14, 16,
    ]
    assert [rows[seed]["A_only_missing"] for seed in report.SEEDS] == [
        12, 8, 3, 8, 8, 3,
    ]
    assert [rows[seed]["both_missing"] for seed in report.SEEDS] == [
        8, 11, 9, 13, 7, 11,
    ]
    assert [rows[seed]["required_K_rate_for_60"] for seed in report.SEEDS] == [
        0.9375, 0.952381, 0.9375, 0.9375, 0.9375, 0.952381,
    ]


def test_u_strength_quartiles_and_halves():
    doc = _artifact()
    quartiles = doc["u_quartiles"]["rows"]
    assert [row["edges"] for row in quartiles] == [107, 107, 104, 64]
    assert [row["K_available"] for row in quartiles] == [34, 53, 84, 57]
    assert [row["K_rate"] for row in quartiles] == [
        0.317757, 0.495327, 0.807692, 0.890625,
    ]
    assert all(row["high_half_K_rate"] > row["low_half_K_rate"]
               for row in doc["per_seed"])
    assert [row["high_half_rows"] for row in doc["per_seed"]] == [
        29, 31, 30, 28, 29, 31,
    ]


def test_first_k_timing_and_orientation():
    doc = _artifact()
    timing = {row["label"]: row["edges"]
              for row in doc["first_k_timing"]["rows"]}
    assert timing == {"1–30": 138, "31–60": 62, "61–90": 19,
                      "91–120": 9, "never": 154}
    assert sum(timing.values()) == 382
    assert timing["61–90"] + timing["91–120"] == 28
    orientation = doc["orientation"]
    assert orientation["pairs_with_reverse"] == 286
    assert orientation["both"] == 177
    assert orientation["neither"] == 101
    assert orientation["candidate_only"] == 3
    assert orientation["reverse_only"] == 5
    assert orientation["concordant"] == 278
    assert orientation["concordant_rate"] == 0.972028


def test_tag_rows_do_not_support_a_single_missing_tag():
    doc = _artifact()
    rows = {row["tag"]: row for row in doc["tag_rows"]}
    assert len(rows) == 16
    assert sum(row["incidences"] for row in rows.values()) == 764
    assert rows["amber"]["K_rate"] == 0.446809
    assert rows["slate"]["K_rate"] == 0.770833
    assert all(row["seeds_below_half"] < 6 for row in rows.values())
    assert all(row["min_seed_rate"] < row["max_seed_rate"] for row in rows.values())


def test_topology_and_page_are_recorded():
    doc = _artifact()
    assert doc["topology"]["max_endpoint_degree_distribution"] == {"8": 382}
    page = Path("docs/A1-K-DECOMPOSITION.md").read_text(encoding="utf-8")
    assert page == report.render(doc) + "\n"
    assert "K-specific gap" in page
    assert "97.2%" in page
    assert "no identified direction" in page
    assert report.self_test() == []
