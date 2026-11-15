"""A1 adopted-block target competence — the record the C2/C8 rule decision rests on."""
import json
from pathlib import Path

from benchmarks import a1_competence_adopted as competence

LAYER = "static"  # reads committed no-arm artifacts; runs no cell


def _record() -> dict:
    return json.loads(Path("docs/a1_competence_adopted.json").read_text(
        encoding="utf-8"))


def test_record_is_clean_and_derived_from_its_sources():
    doc = _record()
    assert competence.problems(doc) == []
    assert doc["block"] == 2074
    assert doc["seed_block"] == [20740101, 20740102, 20740103,
                                 20740104, 20740105, 20740106]
    # The guard's whole point: a stale record must not pass.
    assert doc == competence.build()


def test_no_seed_supplies_a_clean_block_under_the_current_selection():
    doc = _record()
    assert doc["N4"]["competent"] == 12
    assert doc["N4"]["rows"] == 24
    assert doc["N4"]["per_seed_min"] == 0
    assert doc["N4"]["per_seed_max"] == 3
    assert doc["N4"]["seeds_with_clean_block"] == 0

    assert doc["N20"]["competent"] == 58
    assert doc["N20"]["rows"] == 120
    assert doc["N20"]["per_seed_min"] == 7
    assert doc["N20"]["per_seed_max"] == 13
    assert doc["N20"]["seeds_with_clean_block"] == 0

    assert [row["N4"]["competent"] for row in doc["per_seed"]] == [
        3, 0, 3, 2, 2, 2]
    assert [row["N20"]["competent"] for row in doc["per_seed"]] == [
        10, 7, 11, 13, 10, 7]


def test_the_pool_is_sufficient_where_the_selection_is_not():
    doc = _record()
    assert doc["competent_pool"]["per_seed_min"] == 27
    assert doc["competent_pool"]["per_seed_max"] == 40
    assert doc["competent_pool"]["required_for_N20"] == 20
    assert doc["competent_pool"]["sufficient_on_every_seed"] is True
    assert all(row["pool_sufficient_for_N20"] for row in doc["per_seed"])
    assert all(row["competent_pool"] >= 20 for row in doc["per_seed"])


def test_every_selected_row_is_recorded_so_the_counts_are_exact():
    doc = _record()
    assert doc["integrity"]["unrecorded_selected_rows"] == 0
    assert doc["integrity"]["n20_rows_off_the_universe"] == 0
    for row in doc["per_seed"]:
        assert row["N4"]["unrecorded"] == []
        assert row["N20"]["unrecorded"] == []
        assert len(row["N4"]["non_competent"]) == 4 - row["N4"]["competent"]
        assert len(row["N20"]["non_competent"]) == 20 - row["N20"]["competent"]


def test_the_competence_reading_carries_its_own_limit():
    doc = _record()
    assert "treatment gate" in doc["reading"]["induction_caveat"]
    assert "not a proof" in doc["reading"]["induction_caveat"]
    assert "VOID" in doc["finding"]["consequence_for_the_rule"]
    assert "runs no a1 cell" in doc["not_evidence"].lower()
    assert "measures no treatment effect" in doc["not_evidence"].lower()


def test_page_carries_the_numbers_and_the_verdict():
    page = Path("docs/A1-COMPETENCE-ADOPTED.md").read_text(encoding="utf-8")
    assert "| 20740101 | 64 | **3 of 4** | **10 of 20** |" in page
    assert "**12**" in page and "**58**" in page
    assert "**0 of 6**" in page
    assert "sufficient on every seed: **True**" in page


def test_self_test_fires_on_each_inconsistency():
    assert competence.self_test() == []
