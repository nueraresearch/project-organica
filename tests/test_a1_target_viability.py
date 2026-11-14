"""N4 and N20 target viability against C2's K/A requirements."""
import json
from pathlib import Path

from benchmarks import a1_target_viability as viability
from benchmarks import a1_two_path

LAYER = "static"  # reads committed no-arm artifacts and synthetic rows; runs no cell


def _artifact():
    return json.loads(Path("docs/a1_target_viability.json").read_text(encoding="utf-8"))


def test_report_is_clean_and_flags_both_designs():
    doc = _artifact()
    assert viability.problems(doc) == []
    assert doc["status"] == "FLAGGED — C2 NOT PASSABLE UNDER EITHER TARGET SET"
    assert doc["designs"]["N4"]["totals"]["c2_viable_seeds"] == 0
    assert doc["designs"]["N20"]["totals"]["c2_viable_seeds"] == 0
    assert a1_two_path.manifest()["frozen"] is False


def test_n4_and_n20_missing_carrier_counts_are_exact():
    doc = _artifact()
    n4 = doc["designs"]["N4"]["totals"]
    n20 = doc["designs"]["N20"]["totals"]
    assert n4["target_rows"] == 24
    assert n4["carrier_missing"] == 10
    assert n4["carrier_missing_rate"] == 0.416667
    assert n4["c2_failing_cells"] == 38
    assert n4["fully_c2_viable"] == 12
    assert n20["target_rows"] == 120
    assert n20["carrier_missing"] == 52
    assert n20["carrier_missing_rate"] == 0.433333
    assert n20["c2_failing_cells"] == 202
    assert n20["fully_c2_viable"] == 54
    assert [row["carrier_missing"] for row in doc["designs"]["N4"]["per_seed"]] == [1, 1, 1, 2, 2, 3]
    assert [row["carrier_missing"] for row in doc["designs"]["N20"]["per_seed"]] == [5, 12, 8, 11, 7, 9]


def test_n20_adds_rows_without_repairing_c2():
    doc = _artifact()
    comparison = doc["comparison"]
    assert comparison["added_rows"] == 96
    assert comparison["added_missing_carriers"] == 42
    assert comparison["added_missing_rate"] == 0.4375
    assert comparison["retained_N4_missing_carriers"] == 10
    assert comparison["added_c2_failing_cells"] == 164
    assert comparison["C2_viable_seed_delta"] == 0


def test_every_seed_has_a_missing_carrier_in_both_designs():
    doc = _artifact()
    for design in ("N4", "N20"):
        assert doc["designs"][design]["totals"]["seeds_with_missing"] == 6
        assert all(not row["c2_seed_viable"]
                   for row in doc["designs"][design]["per_seed"])


def test_c2_cell_exposure_follows_the_gate_predicates():
    assert viability.c2_failing_cells(True, True) == 0
    assert viability.c2_failing_cells(True, False) == 3
    assert viability.c2_failing_cells(False, True) == 2
    assert viability.c2_failing_cells(False, False) == 4


def test_page_is_rendered_and_self_test_is_clean():
    doc = _artifact()
    page = Path("docs/A1-TARGET-VIABILITY.md").read_text(encoding="utf-8")
    assert page == viability.render(doc) + "\n"
    assert "N20 does not repair C2" in page
    assert "0/6" in page
    assert viability.self_test() == []
