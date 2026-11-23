"""A1 competence filter draft — the rule, its witnesses, and the seed it cannot cover."""
import json
from pathlib import Path

from benchmarks import a1_competence_filter_draft as draft

LAYER = "static"  # reads committed no-arm artifacts; runs no cell


def _record() -> dict:
    return json.loads(Path("docs/a1_competence_filter_draft.json").read_text(
        encoding="utf-8"))


def test_draft_is_clean_and_current():
    doc = _record()
    assert draft.problems(doc) == []
    assert doc == draft.build()
    assert doc["block"] == 2074
    assert doc["integrity"]["unfiltered_reproduces_recorded"] is True


def test_the_unfiltered_pass_reproduces_both_published_selections():
    doc = _record()
    for design in ("N4", "N20"):
        rows = doc["designs"][design]["rows"]
        assert len(rows) == 6
        assert all(row["reproduces_recorded"] for row in rows)


def test_n4_takes_a_competent_block_on_every_seed():
    n4 = _record()["designs"]["N4"]
    assert n4["seeds_formed"] == 6
    assert n4["removed"] == 14
    assert n4["kept"] + n4["removed"] == 24
    assert all(row["all_competent"] for row in n4["rows"])


def test_n20_does_not_take_a_block_on_every_seed_and_says_why():
    n20 = _record()["designs"]["N20"]
    assert n20["seeds_formed"] == 4
    assert n20["seeds_greedy_formed"] == 3
    assert n20["seeds_impossible"] == 1
    assert n20["seeds_undecided"] == 1

    impossible = [row for row in n20["rows"]
                  if row["verdict"].startswith("IMPOSSIBLE")]
    assert [row["seed"] for row in impossible] == [20740102]
    # The impossibility must be exhaustive, not a search that gave up.
    assert impossible[0]["exhaustive"] is False
    assert impossible[0]["best_found_rows"] < 20

    undecided = [row for row in n20["rows"]
                 if row["verdict"].startswith("UNDECIDED")]
    assert undecided[0]["exhaustive"] is None
    assert undecided[0]["best_found_rows"] < 20


def test_every_recorded_witness_respects_the_endpoint_cap():
    doc = _record()
    for design, limit in (("N4", 1), ("N20", 3)):
        for row in doc["designs"][design]["rows"]:
            degree: dict[str, int] = {}
            for edge in row["best_found"]:
                a, b = edge.split(">", 1)
                degree[a] = degree.get(a, 0) + 1
                degree[b] = degree.get(b, 0) + 1
            assert max(degree.values()) <= limit
            assert len(row["best_found"]) == len(set(row["best_found"]))
            assert row["best_found_rows"] == len(row["best_found"])


def test_the_estimand_section_separates_what_moves_from_what_does_not():
    doc = _record()
    joined = " ".join(doc["estimand"]["what_does_not_move"])
    assert "C1's denominator" in joined
    assert "C4's exposure" in joined
    assert "treatment gate" in joined
    assert "pre-treatment" in " ".join(doc["estimand"]["what_moves"])


def test_the_page_states_the_impossibility_rather_than_hiding_it():
    page = Path("docs/A1-COMPETENCE-FILTER-DRAFT.md").read_text(encoding="utf-8")
    assert "20740102" in page
    assert "IMPOSSIBLE — EXHAUSTIVE" in page
    assert "necessary" in page and "not sufficient" in page


def test_self_test_fires_on_each_inconsistency():
    assert draft.self_test() == []
