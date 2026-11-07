"""The question registry and the outreach note are generated under test.

The registry is the project's memory of what it has settled. A stale tally there is
worse than no tally, because it reads as a claim. These tests keep the rendered
document tied to its data and keep the outreach note tied to artifacts on disk.
"""
import json
import re
from pathlib import Path

from benchmarks import research_registry as rr

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "RESEARCH-QUESTION-REGISTRY.md"
OUTREACH = ROOT / "docs" / "OUTREACH.md"


def registry() -> dict:
    return json.loads((ROOT / "docs" / "research_question_registry.json").read_text(encoding="utf-8"))


def test_registry_validates() -> None:
    result = rr.validate(rr.load())
    assert result["passed"], result["errors"]


def test_rendered_document_matches_its_data() -> None:
    assert DOC.exists(), "run python -m benchmarks.research_registry"
    reg = rr.load()
    assert DOC.read_text(encoding="utf-8") == rr.render(reg, rr.validate(reg))


def test_every_decision_record_is_tallied() -> None:
    tallied = {name for q in registry()["questions"] for name in q.get("decisions", [])}
    missing = [name for name in rr.decision_files() if name not in tallied]
    assert not missing, missing


def test_every_bottleneck_row_is_claimed() -> None:
    claimed = {name for q in registry()["questions"] for name in q.get("bottleneck_rows", [])}
    missing = [name for name in rr.map_rows() if name not in claimed]
    assert not missing, missing


def test_future_questions_name_existing_prerequisites() -> None:
    data = registry()
    known = {q["id"] for q in data["questions"]}
    future = [q for q in data["questions"] if q["status"] == "future"]
    assert future
    for q in future:
        assert q["blocked_by"], q["id"]
        assert set(q["blocked_by"]) <= known, q["id"]


def test_outreach_cites_the_earned_result_and_says_agi_is_not_demonstrated() -> None:
    text = OUTREACH.read_text(encoding="utf-8")
    assert "STRUCTURAL_PRIOR_PRESENT_NO_ACQUISITION_ADVANTAGE" in text
    assert "not demonstrated" in text.lower()
    for path in sorted(set(re.findall(r"`((?:docs|papers)/[^`]+)`", text))):
        assert (ROOT / path).exists(), path


def test_outreach_never_quotes_a_withdrawn_number_bare() -> None:
    for line in OUTREACH.read_text(encoding="utf-8").splitlines():
        if "3.2" in line:
            assert any(word in line.lower() for word in ("v1", "withdrawn", "do not")), line
