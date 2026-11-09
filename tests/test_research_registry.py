"""The question registry and the outreach note are generated under test.

The registry is the project's memory of what it has settled. A stale tally there is
worse than no tally, because it reads as a claim. These tests keep the rendered
document tied to its data and keep the outreach note tied to artifacts on disk.

The registry's `--check` mode is wired in here, so a decision record or a bottleneck
map row that nothing tallies fails on commit rather than on the next time someone
remembers to run the renderer. Two of the tests prove the check can fire; a check that
only ever passes is decoration.
"""
import json
import os
import re
import subprocess
import sys
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


def test_check_mode_passes_on_the_committed_tree() -> None:
    """The suite runs the real entry point, not only its functions."""
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    proc = subprocess.run(
        [sys.executable, "-m", "benchmarks.research_registry", "--check"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "FAIL" not in proc.stdout, proc.stdout


def test_check_mode_does_not_rewrite_the_document(capsys) -> None:
    before = DOC.read_bytes()
    assert rr.main(["--check"]) == 0
    capsys.readouterr()
    assert DOC.read_bytes() == before


def test_check_mode_fails_when_a_decision_record_is_untallied(tmp_path, monkeypatch, capsys) -> None:
    """A new docs/DECISION-*.md that no question claims fails the check and names itself."""
    docs = tmp_path / "docs"
    docs.mkdir()
    for name in rr.decision_files():
        (docs / name).write_text("# tallied\n", encoding="utf-8")
    stray = "DECISION-UNREGISTERED-TEST.md"
    (docs / stray).write_text("# nothing tallies this\n", encoding="utf-8")
    monkeypatch.setattr(rr, "ROOT", tmp_path)
    assert rr.main(["--check"]) == 1
    output = capsys.readouterr().out
    assert stray in output, output
    assert "not tallied" in output, output


def test_check_mode_fails_when_a_bottleneck_row_is_unclaimed(tmp_path, monkeypatch, capsys) -> None:
    """A row added to the bottleneck map that no question claims fails the check."""
    data = json.loads(rr.MAP.read_text(encoding="utf-8"))
    row = json.loads(json.dumps(data["rows"][-1]))
    row["candidate"] = "A row no question claims"
    data["rows"].append(row)
    stray_map = tmp_path / "bottleneck_map.json"
    stray_map.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(rr, "MAP", stray_map)
    assert rr.main(["--check"]) == 1
    output = capsys.readouterr().out
    assert "A row no question claims" in output, output


def test_check_passes_when_the_rendered_document_is_current():
    from benchmarks import research_registry as rr

    assert rr.main(["--check"]) == 0


def test_check_fails_when_the_rendered_document_is_stale(tmp_path, monkeypatch):
    from benchmarks import research_registry as rr

    document = tmp_path / "RESEARCH-QUESTION-REGISTRY.md"
    document.write_text("an out-of-date render\n", encoding="utf-8")
    monkeypatch.setattr(rr, "DOC", document)
    assert rr.main(["--check"]) == 1
    assert document.read_text(encoding="utf-8") == "an out-of-date render\n", (
        "--check must report a stale document, never repair it"
    )


def test_reopened_questions_rest_on_no_artifact_that_names_the_pinned_build() -> None:
    """The reopening criterion is a property of the data, not a sentence about it.

    A question is reopened because the artifacts behind its answer do not name the build
    pinned now. If an evidence artifact does name that release, the reopening is wrong and
    this fails.
    """
    reg = registry()
    pinned = reg["reopening"]["engine_version"]
    reopened = [q for q in reg["questions"] if q.get("reopened")]
    assert reopened, "no question carries a reopening record"
    for question in reopened:
        assert question["status"] == "open", question["id"]
        assert question.get("outcome") is None, question["id"]
        for path in question.get("evidence", []):
            artifact = ROOT / path
            if artifact.suffix != ".json":
                continue
            try:
                data = json.loads(artifact.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if isinstance(data, dict):
                assert data.get("engine_version") != pinned, (
                    "%s was reopened but %s names the pinned build %s"
                    % (question["id"], path, pinned))


def test_the_reopening_record_names_every_row_and_every_exception() -> None:
    reg = registry()
    opening = reg["reopening"]
    rows = sorted(q["id"] for q in reg["questions"] if q.get("reopened"))
    assert sorted(opening["reopened"]) == rows, (opening["reopened"], rows)
    kept = [exception["id"] for exception in opening["kept_closed"]]
    assert not set(kept) & set(rows), "a question cannot be reopened and kept closed"
    assert all(exception["reason"].strip() for exception in opening["kept_closed"])
    from benchmarks import engine_stamp

    assert opening["engine_sha256"] == engine_stamp.engine_sha256(), (
        "the reopening must name the engine bytes it was made against")


def test_a_reopening_without_the_build_it_was_measured_on_fails_validation() -> None:
    """Proof the new check can fire: a reopening that cannot say what it replaces."""
    reg = json.loads(json.dumps(registry()))
    target = next(q for q in reg["questions"] if q.get("reopened"))
    del target["reopened"]["measured_on"]
    problems = rr.validate(reg)["errors"]
    assert any(target["id"] in problem and "measured_on" in problem for problem in problems), problems


def _unclassified_closures(reg: dict) -> list[str]:
    """Closed or retired questions the reopening record never classified."""
    kept = {exception["id"] for exception in reg["reopening"]["kept_closed"]}
    reopened = set(reg["reopening"]["reopened"])
    closed = {q["id"] for q in reg["questions"] if q["status"] in ("closed", "retired")}
    return sorted(closed - kept - reopened)


def test_every_closed_or_retired_question_is_classified_in_the_reopening_record() -> None:
    """A closure the pass never classified is an unaccounted row, not an exception.

    Q052 was closed before the 2026-11-08 reopening pass and was omitted from both
    lists, so the record named 26 of the 27 closed or retired answers. The partition
    is now checked rather than tallied by hand: every closed or retired question must
    appear in `reopened` or `kept_closed`.
    """
    missing = _unclassified_closures(registry())
    assert not missing, missing


def test_the_reopening_partition_sums_to_the_registry() -> None:
    reg = registry()
    status = {q["id"]: q["status"] for q in reg["questions"]}
    reopened = reg["reopening"]["reopened"]
    kept = [exception["id"] for exception in reg["reopening"]["kept_closed"]]
    never = [question_id for question_id in status
             if question_id not in set(reopened) and question_id not in set(kept)]
    assert len(reopened) + len(kept) + len(never) == len(reg["questions"])
    assert len(set(reopened) | set(kept) | set(never)) == len(reg["questions"])
    assert {status[question_id] for question_id in reopened} == {"open"}
    assert {status[question_id] for question_id in never} <= {"open", "future"}


def test_the_closure_check_fires_when_a_closed_question_is_omitted() -> None:
    reg = json.loads(json.dumps(registry()))
    reg["reopening"]["kept_closed"] = [exception for exception in reg["reopening"]["kept_closed"]
                                       if exception["id"] != "Q052"]
    assert _unclassified_closures(reg) == ["Q052"]
