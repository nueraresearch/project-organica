"""A2's estimand decision is adopted: it closes the line, and says why in design terms."""
from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import json
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1] / "docs"


def _text() -> str:
    return (DOCS / "DECISION-A2-ESTIMAND.md").read_text(encoding="utf-8")


def _record() -> dict:
    return next(d for d in json.loads((DOCS / "decisions.json").read_text(encoding="utf-8"))["decisions"]
                if d["decision_id"] == "DECISION-A2-ESTIMAND")


def test_the_decision_is_adopted_and_closes_the_line() -> None:
    record = _record()
    assert record["status"] == "ADOPTED"
    text = _text()
    assert "ADOPTED — A2 IS CLOSED AND NO A2 ARM RUNS" in text
    assert "A2 is closed: the edge-level question A1 asked is not testable with this intervention" in text


def test_it_gives_a_design_reason_not_a_taste_reason() -> None:
    text = _text()
    assert "controls the total, not the distribution" in text
    assert "A2b's criterion cannot fail" in text
    assert "cannot fire as a check" in text


def test_it_does_not_overclaim_impossibility_or_authorise_work() -> None:
    text = _text()
    assert "does not establish that no such construction exists" in text
    assert "It does **not** assert that no A2 design exists" in text
    assert "authorises **no code, no cells, no engine change and no spending**" in text


def test_the_two_closures_are_distinguished_and_scoped() -> None:
    text = _text()
    assert "The two closures are not the same kind" in text
    assert "its **control failed**" in text
    assert "**control can only be obtained by changing the question**" in text
    assert "within this engine, world family and" in text
    assert "not about every design a" in text
    assert "not rejected as science, only as A1's continuation" in text


def test_a1_is_untouched() -> None:
    text = _text()
    assert "A1 remains `VOID`, frozen and un-rescored" in text
    assert "does not reopen A1" in text


def test_the_question_is_answered_and_tallies_the_decision() -> None:
    registry = json.loads((DOCS / "research_question_registry.json").read_text(encoding="utf-8"))
    tallies = [q for q in registry["questions"] if "DECISION-A2-ESTIMAND.md" in q.get("decisions", [])]
    assert len(tallies) == 1
    question = tallies[0]
    assert question["status"] == "closed"
    assert question["outcome"] == "SUPPORTED"
    assert "A2 is closed" in question["answer"]
