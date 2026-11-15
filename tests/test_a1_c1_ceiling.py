"""The C1 ceiling decision's numbers and quoted clauses are re-derived, not transcribed.

Three things are checked, each because this corpus has already been bitten by its absence:

* the per-seed minima in the decision are the baseline artifact's, recomputed here;
* the premise of the conflict is real — five of six seeds exceed 64 on the operative row;
* the index quotes (status, chosen clauses, rejected reasons) appear in the document, so the
  record cannot drift away from the index that summarises it.
"""

from __future__ import annotations

import json
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1] / "docs"
DECISION = DOCS / "DECISION-A1-C1-CEILING.md"
BASELINE = DOCS / "a1_baseline_availability_adopted.json"

LAYER = "static"


def _doc() -> str:
    return DECISION.read_text(encoding="utf-8")


def _flat(text: str) -> str:
    """Prose wraps; the index quotes are single lines. Compare on one line."""
    return " ".join(text.split())


def _table_row(label: str) -> list[int]:
    """The integer cells of a table row whose first cell starts with ``label``."""
    for line in _doc().splitlines():
        if line.startswith("|") and line.lstrip("| ").startswith(label):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            return [int(cell.replace("*", "").replace(",", "")) for cell in cells[1:]
                    if cell.replace("*", "").replace(",", "").isdigit()]
    raise AssertionError("no table row labelled %r" % label)


def _minima() -> list[int]:
    data = json.loads(BASELINE.read_text(encoding="utf-8"))
    return [record["c1_min_denominator"] for record in data["per_seed"]]


def test_the_ceiling_decision_reports_the_baseline_minima() -> None:
    """The five bolded minima and the one plain 64 are the artifact's own numbers."""
    minima = _minima()
    assert len(minima) == 6
    assert _table_row("Observed minimum") == minima
    assert [m > 64 for m in minima] == [True, False, True, True, True, True]


def test_the_conflict_premise_holds_on_the_operative_row() -> None:
    """Five of six seeds are above the ceiling, and the sixth sits exactly on it."""
    minima = _minima()
    assert sum(m > 64 for m in minima) == 5
    assert min(minima) == 64, "the boundary seed is exactly at the ceiling, not below it"


def test_the_decision_names_the_quantity_the_clause_was_written_against() -> None:
    doc = _doc()
    assert "candidate count" in doc
    assert "Not the candidate count" in doc, "the denominator record's own wording is quoted"
    for record in ("A1-PATH-A-C1-RULE-1", "DECISION-A1-C1-DENOMINATOR-1", "A1-C1-CEILING-CONFLICT"):
        assert record in doc


def test_the_decision_quotes_are_the_index_quotes() -> None:
    """The index stores verbatim quotes; a paraphrase here would fail validation."""
    index = json.loads((DOCS / "decisions.json").read_text(encoding="utf-8"))
    entry = next(d for d in index["decisions"]
                 if d["decision_id"] == "DECISION-A1-C1-CEILING")
    doc = _flat(_doc())
    # Adopted 2026-11-15; the quote moves with the status line and must still be verbatim.
    assert entry["status"] == "ADOPTED"
    assert _flat(entry["status_quote"]) in doc
    for phrase in entry["chosen"]:
        assert _flat(phrase) in doc, phrase
    for rejected in entry["rejected"]:
        assert _flat(rejected["reason"]) in doc, rejected["reason"]


def test_the_decision_leaves_every_threshold_alone() -> None:
    """An amendment to one clause must say what it does not touch, and say it in those terms."""
    doc = _doc()
    for untouched in ("0.95", "60-row floor", "three-loss band", "C4 ceiling"):
        assert untouched in doc
    assert "79 / 64 / 79 / 74 / 72 / 74" in doc
