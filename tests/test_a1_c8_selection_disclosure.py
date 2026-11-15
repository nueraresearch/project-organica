"""The S5 disclosure must be generated, and it must not describe a subtraction.

The page exists because `DECISION-A1-C8-SELECTION` S5 asks for the unfiltered selection beside the
filtered one. Its risk is not arithmetic: it is that a reader treats the two blocks as one block
minus rows. The data says they are different sets — the filtered block adds edges the unfiltered rule
never chose — so the page has to say so, and this test holds both the numbers and the sentence.
"""

from __future__ import annotations

import json
from pathlib import Path

from benchmarks import a1_c8_selection_disclosure as disclosure

ROOT = Path(__file__).resolve().parents[1]


def documents() -> tuple[dict, dict]:
    return (json.loads(disclosure.PARENT.read_text(encoding="utf-8")),
            json.loads(disclosure.FILTERED.read_text(encoding="utf-8")))


def test_the_page_is_its_render() -> None:
    assert disclosure.problems() == []
    assert disclosure.PAGE.read_text(encoding="utf-8") == disclosure.render()


def test_the_columns_reconcile() -> None:
    table = disclosure.rows(*documents())
    for row in table:
        assert row["filtered"] == row["shared"] + row["added"], row["seed"]
        assert row["unfiltered"] == row["shared"] + row["excluded_incompetent"] + row["excluded_not_chosen"]
    total = disclosure.totals(table)
    assert total["filtered"] == total["shared"] + total["added"]


def test_the_blocks_are_different_sets_so_the_page_says_so() -> None:
    """If `added` were zero the blocks would nest, and the warning would be wrong."""
    total = disclosure.totals(disclosure.rows(*documents()))
    assert total["added"] > 0
    assert total["excluded_not_chosen"] > 0
    text = disclosure.PAGE.read_text(encoding="utf-8")
    assert disclosure.READING in text
    assert "not a subtraction" in text


def test_the_timing_claim_has_grounds() -> None:
    """The sentence is only true while no cell has run; the checks say so instead of the prose."""
    assert disclosure.evidence() == []
    text = disclosure.PAGE.read_text(encoding="utf-8")
    assert "## Grounds for the timing claim" in text
    assert "✅ the freeze act reads" in text


def test_a_grant_record_breaks_the_claim(tmp_path: Path) -> None:
    (tmp_path / "A1-GRANT-EXAMPLE-1.md").write_text("a grant\n", encoding="utf-8")
    found = disclosure.evidence(docs=tmp_path)
    assert any("A1-GRANT-EXAMPLE-1.md" in problem for problem in found), found


def test_a_run_record_breaks_the_claim(tmp_path: Path) -> None:
    (tmp_path / "a1_run_cells.json").write_text("{}\n", encoding="utf-8")
    found = disclosure.evidence(docs=tmp_path)
    assert any("a1_run_cells.json" in problem for problem in found), found


def test_a_signed_act_breaks_the_claim(tmp_path: Path) -> None:
    signed = tmp_path / "act.md"
    signed.write_text(disclosure.ACT.read_text(encoding="utf-8")
                      .replace(disclosure.UNSIGNED, "SIGNED"), encoding="utf-8")
    found = disclosure.evidence(act=signed, docs=tmp_path)
    assert any("no longer says" in problem for problem in found), found


def test_the_page_records_when_the_filter_ran() -> None:
    text = disclosure.PAGE.read_text(encoding="utf-8")
    assert disclosure.TIMING in text
    assert "before any cell" in text
    assert "NOTHING FROZEN, NOTHING RUN" in text


def test_a_doctored_number_fails() -> None:
    text = disclosure.PAGE.read_text(encoding="utf-8")
    doctored = text.replace("| **total** | **120**", "| **total** | **121**", 1)
    assert doctored != text
    assert disclosure.problems(doctored)


def test_a_dropped_warning_fails() -> None:
    text = disclosure.PAGE.read_text(encoding="utf-8")
    doctored = text.replace(disclosure.READING, "", 1)
    assert any("not a subtraction" in problem for problem in disclosure.problems(doctored))
