"""The review brief must hand the reviewer files that exist, and outcomes that can reject."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs/INDEPENDENT-METHODS-REVIEW.md"


def _doc():
    if not DOC.exists():
        import pytest
        pytest.skip("the review brief has not been written yet")
    return DOC.read_text(encoding="utf-8")


def test_the_three_outcomes_and_the_rejection_rule():
    text = _doc()
    assert "Approved with conditions" in text
    assert "Rejected" in text
    assert "recorded verbatim" in text
    assert "cannot be argued into an approval" in text


def test_the_five_questions_are_mapped_not_listed():
    text = _doc()
    for q in ("genuinely testable", "measurements independent",
              "held-out design valid", "statistical criteria defensible",
              "falsify the hypothesis"):
        assert q.lower() in text.lower(), q
    assert "what counts as a defect" in text.lower()


def test_the_author_is_excluded_by_rule():
    text = _doc()
    assert "cannot be conducted by the author" in text
    assert "cannot be me" in text or "cannot stand in for it" in text


def test_the_reviewer_sees_no_result_from_this_design():
    text = _doc()
    assert "before any new experimental result exists" in text
    assert "design-block" in text


def test_every_artifact_in_the_package_exists():
    text = _doc()
    paths = set(re.findall(r"`((?:docs|benchmarks|tests|research-journal)/[^`]+)`", text))
    assert paths, "the package table names no artifacts"
    missing = sorted(p for p in paths if not (ROOT / p).exists())
    assert not missing, missing


def test_the_manual_and_journal_record_the_review():
    manual = (ROOT / "docs/USER-MANUAL.md").read_text(encoding="utf-8")
    row = [l for l in manual.split("\n") if l.startswith("| 14 | **Obtain the independent methods review")]
    assert len(row) == 1
    assert "INDEPENDENT-METHODS-REVIEW.md" in row[0]
    assert "cannot be me" in row[0]
    journal = (ROOT / "research-journal/phase_g_findings_20261021.md").read_text(encoding="utf-8")
    assert "## \u00a7141" in journal


def test_the_machine_pass_is_offered_and_cannot_take_the_record():
    root = Path(__file__).resolve().parent.parent
    prompt = (root / "docs/AI-REVIEW-PROMPT.md").read_text(encoding="utf-8")
    brief = (root / "docs/INDEPENDENT-METHODS-REVIEW.md").read_text(encoding="utf-8")
    # the prompt must demand artifact checks and forbid both approval and the record
    assert "Check artifacts, not prose" in prompt
    assert "Do not output an approval or a rejection" in prompt
    assert "Do not fill in the report form" in prompt
    assert "It cannot discharge the review gate" in prompt
    # and the brief must not let it be upgraded later
    assert "## 9. Machine review is a pre-pass" in brief
    assert "never the record" in brief
    assert "fabricated provenance" in brief
    # the form stays empty: no model may have signed it
    assert "*(to be completed)*" in brief
