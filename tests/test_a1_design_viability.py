"""A1 design viability: C1 ceiling and conditional C2/C8 target competence."""
import json
from pathlib import Path

from benchmarks import a1_design_viability as viability

LAYER = "static"  # reads committed no-arm artifacts; runs no cell


def _artifact():
    return json.loads(Path("docs/a1_design_viability.json").read_text(encoding="utf-8"))


def test_report_is_clean_and_flags_the_design():
    doc = _artifact()
    assert viability.problems(doc) == []
    assert doc["status"].startswith("FLAGGED — C1 CEILING")
    assert doc["c1_ceiling"]["candidate_stream"]["seeds_reaching_floor"] == 0
    assert doc["c2_c8_competence"]["status"].startswith("CONDITIONAL")


def test_candidate_stream_ceiling_is_below_floor_on_every_seed():
    stream = _artifact()["c1_ceiling"]["candidate_stream"]
    assert [row["max_attainable"] for row in stream["per_seed"]] == [
        44, 31, 39, 35, 43, 36,
    ]
    assert [row["rows"] for row in stream["per_seed"]] == [64, 63, 64, 64, 64, 63]
    assert all(row["shortfall"] > 0 for row in stream["per_seed"])
    assert all(not row["reaches_floor"] for row in stream["per_seed"])
    assert stream["min_attainable"] == 31
    assert stream["max_attainable"] == 44


def test_cell_stream_still_falls_short_on_two_seeds():
    stream = _artifact()["c1_ceiling"]["cell_stream"]
    assert [row["max_attainable"] for row in stream["per_seed"]] == [
        70, 59, 69, 58, 72, 72,
    ]
    assert stream["seeds_reaching_floor"] == 4
    assert [row["seed"] for row in stream["per_seed"] if not row["reaches_floor"]] == [
        20630102, 20630104,
    ]


def test_cell_stream_is_candidate_plus_reverse_orientations():
    comp = _artifact()["c1_ceiling"]["stream_composition"]
    assert comp["candidate_rows"] == 382
    assert comp["reverse_orientations"] == 286
    assert comp["extra_orientations"] == 4
    assert comp["cell_rows"] == 672
    assert comp["unique_undirected"] == 384
    assert comp["unique_c1_min"] == 31
    assert comp["unique_c1_max"] == 44
    assert [row["unique_undirected"] for row in comp["per_seed"]] == [64] * 6
    assert [row["extra_orientations"] for row in comp["per_seed"]] == [
        0, 2, 0, 0, 0, 2,
    ]
    assert all(row["all_candidate_edges_present"] for row in comp["per_seed"])


def test_candidate_pool_can_supply_a_twenty_row_competent_block():
    pool = _artifact()["c2_c8_competence"]["target_pool"]
    assert pool["c8_rows_required"] == 20
    assert pool["min_A_and_K_available"] == 23
    assert pool["max_A_and_K_available"] == 36
    assert pool["seeds_sufficient"] == 6
    assert [row["A_and_K_available"] for row in pool["per_seed"]] == [
        32, 23, 36, 27, 35, 33,
    ]
    assert all(row["pool_sufficient"] for row in pool["per_seed"])


def test_c2_c8_competence_is_conditional_and_short():
    comp = _artifact()["c2_c8_competence"]
    assert "not a proof" in comp["status"].lower()
    assert "treatment gate" in comp["induction_caveat"]
    n4 = comp["designs"]["N4"]
    n20 = comp["designs"]["N20"]
    assert n4["c8_rows_required"] == 4
    assert n20["c8_rows_required"] == 20
    assert n4["total_clean_rows"] == 12
    assert n20["total_clean_rows"] == 54
    assert n4["max_clean_rows"] == 3
    assert n20["max_clean_rows"] == 12
    assert n4["seeds_clean_block_possible"] == 0
    assert n20["seeds_clean_block_possible"] == 0
    assert [row["fully_c2_viable"] for row in n4["per_seed"]] == [2, 3, 3, 1, 2, 1]
    assert [row["fully_c2_viable"] for row in n20["per_seed"]] == [10, 5, 12, 7, 10, 10]


def test_ceiling_and_competence_fixtures_are_checked():
    assert viability.self_test() == []
    row = viability._ceiling_row(
        1, {"candidate_rows": 64, "A_available": 70, "K_available": 82})
    assert row["max_attainable"] == 70
    assert row["shortfall"] == 0
    assert row["surplus"] == 10
    assert row["reaches_floor"] is True


def test_page_is_rendered_from_the_artifact():
    doc = _artifact()
    page = Path("docs/A1-DESIGN-VIABILITY.md").read_text(encoding="utf-8")
    assert page == viability.render(doc) + "\n"
    assert "C1 ceiling — proof for the current stream" in page
    assert "CONDITIONAL — NOT A PROOF OF C2 OR C8 FAILURE" in page
    assert "Cell-stream composition and dedupe" in page
    assert "Competent target pool" in page
    assert "0/6" in page
