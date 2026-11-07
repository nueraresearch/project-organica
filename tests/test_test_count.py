"""The published test count must be measured, and it must not go stale."""

import pytest

from benchmarks import test_count as tc

# Before the first recording there is nothing to compare against. The skip is a
# bootstrap state only: the recorder writes the record and the documents from one
# real run, and from then on these checks run in full. A missing record is not
# silent at the gate -- `--check` fails on it rather than skipping.
# The record-versus-collection comparison lives in the gate, not here: as a suite test it
# deadlocks the recorder, because adding a test makes the record stale and the recorder
# refuses to publish a suite that is red for that reason alone.
needs_record = pytest.mark.skipif(
    not tc.ARTIFACT.exists(),
    reason="no recorded test count yet; run python -m benchmarks.test_count",
)


@needs_record
def test_the_documents_state_the_recorded_count():
    record = tc.load_record()
    fragment = tc.render_fragment(record)
    for path in tc.TARGETS:
        assert path.exists()
        assert tc.region_of(path.read_text(encoding="utf-8")) == fragment, (
            "%s does not state the recorded count; run python -m benchmarks.test_count" % path.name
        )


@needs_record
def test_the_old_hand_typed_count_is_gone():
    # The three statements that were stale. The manual may still quote the old
    # number as the history of this defect; what must not survive is a document
    # stating it as the current count.
    stale = ("# 250 tests", "(250 tests)", "250 tests, must be green")
    for path in tc.TARGETS:
        text = path.read_text(encoding="utf-8")
        for phrase in stale:
            assert phrase not in text, "%s still states the hand-typed count as current" % path.name


@needs_record
def test_a_tampered_region_is_reported(tmp_path, monkeypatch):
    record = tc.load_record()
    document = tmp_path / "AGENTS.md"
    document.write_text(
        "intro " + tc.MARK_START + " 1 passed of 1 " + tc.MARK_END + " tail\n", encoding="utf-8"
    )
    monkeypatch.setattr(tc, "TARGETS", (document,))
    found = tc.problems(record, live=record["collected"])
    assert any("AGENTS.md" in message for message in found), found


@needs_record
def test_a_missing_marker_is_reported(tmp_path, monkeypatch):
    record = tc.load_record()
    document = tmp_path / "AGENTS.md"
    document.write_text("no markers here\n", encoding="utf-8")
    monkeypatch.setattr(tc, "TARGETS", (document,))
    found = tc.problems(record, live=record["collected"])
    assert any("region" in message for message in found), found


@needs_record
def test_a_suite_that_grew_is_reported(tmp_path, monkeypatch):
    record = tc.load_record()
    document = tmp_path / "AGENTS.md"
    document.write_text(tc.MARK_START + tc.render_fragment(record) + tc.MARK_END, encoding="utf-8")
    monkeypatch.setattr(tc, "TARGETS", (document,))
    found = tc.problems(record, live=record["collected"] + 1)
    assert any("collects" in message for message in found), found


@needs_record
def test_check_writes_nothing():
    # The invariant is that the check never writes, whatever it returns: a stale
    # record makes it exit 1 by design, and a test that demanded 0 here would
    # deadlock the recorder on every run that adds a test.
    before = {path: path.read_bytes() for path in tc.TARGETS}
    record_before = tc.ARTIFACT.read_bytes()
    assert tc.main(["--check"]) in (0, 1)
    assert {path: path.read_bytes() for path in before} == before
    assert tc.ARTIFACT.read_bytes() == record_before


@needs_record
def test_the_writer_replaces_only_the_region(tmp_path, monkeypatch):
    record = tc.load_record()
    document = tmp_path / "AGENTS.md"
    document.write_text("before " + tc.MARK_START + "stale" + tc.MARK_END + " after\n", encoding="utf-8")
    monkeypatch.setattr(tc, "TARGETS", (document,))
    monkeypatch.setattr(tc, "ARTIFACT", tmp_path / "test_count.json")
    tc.write(record)
    assert document.read_text(encoding="utf-8") == (
        "before " + tc.MARK_START + tc.render_fragment(record) + tc.MARK_END + " after\n"
    )


def test_the_recorder_refuses_to_publish_a_red_suite(tmp_path, monkeypatch):
    monkeypatch.setattr(tc, "ARTIFACT", tmp_path / "test_count.json")
    monkeypatch.setattr(
        tc,
        "run_suite",
        lambda: {
            "command": "python -m pytest tests -q",
            "date": "2026-11-07",
            "exit_code": 1,
            "collected": 10,
            "passed": 7,
            "skipped": 0,
            "failed": 3,
        },
    )
    assert tc.main([]) == 1
    assert not (tmp_path / "test_count.json").exists(), "a red run must not be published"
