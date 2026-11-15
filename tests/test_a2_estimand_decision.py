"""A2's fork is recorded, not decided: the draft must name both branches and choose neither."""
from __future__ import annotations

import json
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1] / "docs"


def _text() -> str:
    return (DOCS / "DECISION-A2-ESTIMAND.md").read_text(encoding="utf-8")


def test_the_record_is_pending_and_chooses_nothing() -> None:
    record = next(d for d in json.loads((DOCS / "decisions.json").read_text(encoding="utf-8"))["decisions"]
                  if d["decision_id"] == "DECISION-A2-ESTIMAND")
    assert record["status"] == "PENDING"
    text = _text()
    assert "DRAFT — AWAITING THE OWNER'S ESTIMAND CHOICE" in text
    assert "Until signed, this document records a fork and chooses nothing." in text


def test_both_branches_are_named_with_their_cost() -> None:
    text = _text()
    assert "A2c′" in text and "A2b" in text
    assert "Unit of inference" in text
    assert "Comparability with A1" in text
    assert "Does the study's next claim need to be about edges, or about carriers?" in text


def test_the_aggregate_criterion_is_never_a_rescue() -> None:
    text = _text()
    assert "has no witnessed construction" in text
    assert "does not establish that no such construction exists" in text
    assert "a different criterion, not a rescue criterion" in text
    assert "no document may describe it as the per-edge design succeeding" in text


def test_the_evidence_that_fixes_the_fork_is_carried() -> None:
    text = _text()
    for number in ("90.2%", "88.4%", "92.9%", "2.76", "8.1%", "30, 51 and 78"):
        assert number in text, number


def test_it_authorises_no_run_and_a_question_tallies_it() -> None:
    text = _text()
    assert "Neither branch is authorised to run by this record" in text
    registry = json.loads((DOCS / "research_question_registry.json").read_text(encoding="utf-8"))
    tallies = [q["id"] for q in registry["questions"]
               if "DECISION-A2-ESTIMAND.md" in q.get("decisions", [])]
    assert len(tallies) == 1
    assert next(q for q in registry["questions"] if q["id"] == tallies[0])["status"] == "open"
