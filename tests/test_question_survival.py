"""The question-survival page is derived, complete, and its classifier can fail."""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer
import json

from benchmarks import question_survival as qs


def _registry():
    return json.loads(qs.REGISTRY.read_text(encoding="utf-8"))


def test_the_page_and_the_artifact_match_a_rebuild():
    problem = qs.stale()
    assert problem is None, problem


def test_every_open_and_future_question_is_reviewed_once():
    reg = _registry()
    expected = [q["id"] for q in reg["questions"] if q["status"] in ("open", "future")]
    record = json.loads(qs.ARTIFACT.read_text(encoding="utf-8"))
    reviewed = [row["id"] for row in record["questions"]]
    assert reviewed == expected
    assert record["populations"]["reviewed"] == len(expected)


def test_no_reviewed_question_names_a_path_that_does_not_exist():
    record = json.loads(qs.ARTIFACT.read_text(encoding="utf-8"))
    assert record["evidence"]["missing_paths"] == []
    assert sum(row["evidence"] for row in record["questions"]) > 0


def test_the_classifier_separates_every_case_it_claims_to():
    """Each branch must be reachable, or a state is decoration rather than a report."""
    pinned = qs.pin()
    other = "0.9.0"
    base = {"status": "open", "evidence": ["docs/V1-SYNTHESIS.md"]}
    cases = [
        ({**base, "answer": "yes"}, [pinned], [], [], "answered-at-pin"),
        ({**base, "answer": "yes"}, [other], [], [], "answered-older-build"),
        ({**base, "answer": "yes"}, [], [], [], "answered-no-build"),
        ({**base, "answer": "yes", "why_open": "Reopened 2026-11-08: predates 0.12.0"},
         [pinned], [], [], "answered-older-build"),
        (base, [], [], [], "open-with-evidence"),
        ({"status": "future", "evidence": []}, [], [], [], "open-no-evidence"),
        ({**base, "blocked_by": ["Q012"]}, [], [], [], "prerequisite"),
        ({**base, "answer": "yes"}, [pinned], [], ["DECISION-X"], "governance-held"),
        ({**base, "answer": "yes"}, [pinned], ["docs/gone.json"], [], "broken-evidence"),
    ]
    for question, builds, missing, pending, expected in cases:
        assert qs.classify(question, builds, missing, pending) == expected, (question, expected)


def test_an_unnamed_build_is_not_reported_as_an_older_one():
    """The defect the page exists to keep separate: silence is not staleness."""
    record = json.loads(qs.ARTIFACT.read_text(encoding="utf-8"))
    unnamed = [row for row in record["questions"] if row["state"] == "answered-no-build"]
    for row in unnamed:
        assert row["builds"] == []
        assert not row["reopened_in_prose"]
    older = [row for row in record["questions"] if row["state"] == "answered-older-build"]
    for row in older:
        assert row["reopened_in_prose"] or record["pinned_version"] not in row["builds"]
    at_pin = [row for row in record["questions"] if row["state"] == "answered-at-pin"]
    for row in at_pin:
        assert record["pinned_version"] in row["builds"]
        assert not row["reopened_in_prose"]
