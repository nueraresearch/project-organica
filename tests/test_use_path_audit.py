"""The reproduction audit's own checks.

The audit is post-hoc and these tests do not run a world.  They prove the
intervention fires, the classifier's labels are exhaustive, the analysis
refuses an incomplete artifact, and the result document is a rendering of the
committed artifact that can disagree with it.
"""
from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import use_path_audit as ua  # noqa: E402


JOURNAL = REPO / "research-journal" / "phase_g_findings_20261021.md"
MACHINE = re.compile(r"\*\*Machine-readable counts:\*\* `([^`]+)`")
JOURNAL_LINE = re.compile(
    r"\*\*Audit counts \(source: `docs/use_path_audit\.json`\):\*\* `([^`]+)`")
KEYS = (
    "seeds",
    "repeats",
    "runs",
    "no_tiebreak_stable",
    "tiebreak_stable",
    "arms_agree",
    "digests_agree",
    "campaign_no_match",
    "campaign_tie_match",
    "diagnostic_no_match",
    "diagnostic_tie_match",
    "layer3_entered",
)


def parse_machine(text: str) -> dict[str, int]:
    match = MACHINE.search(text)
    assert match, "the result document has no machine-readable counts line"
    return {key: int(value) for key, value in
            (item.split("=", 1) for item in match.group(1).split())}


def parse_counts(payload: str) -> dict[str, int]:
    return {key: int(value) for key, value in
            (item.split("=", 1) for item in payload.split())}


def compare_counts(got: dict, artifact: dict) -> list[str]:
    """Compare a parsed counts mapping with the artifact's; return problems."""
    c = artifact["summary"]["counts"]
    expected = {
        "seeds": c["seeds"],
        "repeats": artifact["repeats"],
        "runs": len(artifact["runs"]),
        "no_tiebreak_stable": c["no_tiebreak_stable"],
        "tiebreak_stable": c["tiebreak_stable"],
        "arms_agree": c["arms_agree"],
        "digests_agree": c["digests_agree"],
        "campaign_no_match": c["no_tiebreak_matches_campaign_table"],
        "campaign_tie_match": c["tiebreak_matches_campaign_table"],
        "diagnostic_no_match": c["no_tiebreak_matches_diagnostic"],
        "diagnostic_tie_match": c["tiebreak_matches_diagnostic"],
        "layer3_entered": c["layer3_entered"],
    }
    problems = [f"{key}: document {got.get(key)!r} != artifact {value!r}"
                for key, value in expected.items() if got.get(key) != value]
    missing = set(KEYS) - set(got)
    if missing:
        problems.append("missing counts: " + ", ".join(sorted(missing)))
    return problems


def check_doc(text: str, artifact: dict) -> list[str]:
    """Compare the result document's counts with the artifact's."""
    return compare_counts(parse_machine(text), artifact)


# ---------------------------------------------------------------------------
# The instrument
# ---------------------------------------------------------------------------

def test_self_test_fires_the_tiebreak(monkeypatch):
    monkeypatch.setenv("PYTHONHASHSEED", "0")
    assert ua.self_test() == 0


def test_classifier_labels_are_exhaustive():
    cases = [
        (True, True, True, True, "both_stable_both_reproduce"),
        (True, True, True, False, "both_stable_no_tiebreak_reproduces"),
        (True, True, False, True, "both_stable_tiebreak_reproduces"),
        (True, True, False, False, "both_stable_both_differ"),
        (False, True, False, False, "baseline_unstable_tiebreak_stable"),
        (True, False, False, False, "baseline_stable_tiebreak_unstable"),
        (False, False, False, False, "both_unstable"),
    ]
    labels = [ua.classify(*case[:4]) for case in cases]
    assert labels == [case[4] for case in cases]
    assert len(set(labels)) == 7, "a label is not reachable by the table"


def test_analysis_refuses_an_incomplete_artifact():
    with pytest.raises(ValueError, match="incomplete"):
        ua.analyse([], repeats=3)


def test_placeholder_guard_fires():
    with pytest.raises(ValueError, match="placeholder"):
        ua._assert_no_placeholder("a number {missing} here")


# ---------------------------------------------------------------------------
# The result document is a rendering of the artifact
# ---------------------------------------------------------------------------

def _artifact() -> dict:
    assert ua.AUDIT.exists(), (
        "docs/use_path_audit.json is missing; run the audit or restore the "
        "committed artifact")
    return json.loads(ua.AUDIT.read_text(encoding="utf-8"))


def test_result_document_is_generated_from_the_artifact():
    artifact = _artifact()
    text = ua.RESULT_MD.read_text(encoding="utf-8")
    assert check_doc(text, artifact) == []
    assert text == ua.render_markdown(artifact), (
        "docs/USE-PATH-AUDIT.md is stale; regenerate it with "
        "`python benchmarks/use_path_audit.py --render`")


def test_journal_counts_match_the_artifact():
    artifact = _artifact()
    text = JOURNAL.read_text(encoding="utf-8")
    match = JOURNAL_LINE.search(text)
    assert match, "the journal has no audit counts line"
    assert compare_counts(parse_counts(match.group(1)), artifact) == []


def test_journal_counts_can_fail():
    artifact = _artifact()
    text = JOURNAL.read_text(encoding="utf-8")
    match = JOURNAL_LINE.search(text)
    assert match
    drifted = parse_counts(match.group(1))
    drifted["arms_agree"] -= 1
    problems = compare_counts(drifted, artifact)
    assert problems, "the checker failed to notice a drifted journal count"
    assert any("arms_agree" in problem for problem in problems)


class TestTheCheckCanFail:
    """A check that cannot disagree with its subject is not a check."""

    def test_a_drifted_count_is_caught(self):
        artifact = _artifact()
        text = ua.RESULT_MD.read_text(encoding="utf-8")
        assert check_doc(text, artifact) == []

        drifted = copy.deepcopy(artifact)
        drifted["summary"]["counts"]["no_tiebreak_stable"] -= 1
        problems = check_doc(text, drifted)
        assert problems, "the checker failed to notice a drifted count"
        assert any("no_tiebreak_stable" in problem for problem in problems)

    def test_a_missing_line_is_caught(self):
        artifact = _artifact()
        text = ua.RESULT_MD.read_text(encoding="utf-8")
        stripped = MACHINE.sub("**Machine-readable counts:** absent", text)
        with pytest.raises(AssertionError):
            check_doc(stripped, artifact)
