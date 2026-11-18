"""Tests for the Phase L campaign's resume reconstruction.

The preregistration (Section 8.2) promises that "--resume rebuilds from the
recording if the results file is missing".  The harness originally read only
the results file, so that promise was unkept.  These tests cover the
reconstruction path directly, and are deliberately cheap: no engine cell is
run, so they do not compete with a live campaign for CPU.

The recording is read through the campaign's shared strict reader, with Phase
L's own key fields (arm, label, seed), so these tests cover what that reader
guarantees here: one record per cell, a torn final line truncated before the
resume appends past it, and an unreadable, non-cell or disagreeing row refused
rather than skipped.  The last test holds the resume and the shared reader to
the same refusal, so a future reader cannot quietly diverge again.

Control discipline: each test asserts an exact record count, so a
reconstruction that silently dropped or duplicated cells fails rather than
passing quietly.
"""

from __future__ import annotations
LAYER = "dry-run"  # benchmarks/test_layers.py: the harness's resume path, no cell

import importlib.util
import json
import sys
from pathlib import Path

import pytest

from benchmarks import phase_k_campaign as shared

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_harness():
    path = REPO_ROOT / "benchmarks" / "phase_l_campaign.py"
    spec = importlib.util.spec_from_file_location("_phase_l_campaign", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["_phase_l_campaign"] = module
    spec.loader.exec_module(module)
    return module


HARNESS = _load_harness()


def _rec(arm: str, label: str, seed: int, results: dict | None = None) -> dict:
    return {"arm": arm, "label": label, "seed": seed, "params": {},
            "results": {} if results is None else results}


def _write_results(path: Path, records: list) -> None:
    path.write_text(
        json.dumps({"protocol": {}, "records": records}),
        encoding="utf-8",
    )


def _write_lines(path: Path, lines: list[str], *, torn_tail: bool = False) -> Path:
    """Write one line per element; a torn tail is written without its newline."""
    path.write_text("\n".join(lines) + ("" if torn_tail else "\n"),
                    encoding="utf-8")
    return path


def _write_ndjson(path: Path, records: list, raw_tail: str = "") -> None:
    lines = [json.dumps(rec) for rec in records]
    if raw_tail:
        lines.append(raw_tail)
    _write_lines(path, lines, torn_tail=bool(raw_tail))


def test_results_file_is_the_primary_source(tmp_path):
    results = tmp_path / "results.json"
    ndjson = tmp_path / "results.ndjson"
    _write_results(results, [_rec("V1", "1:1", 1), _rec("V1", "1:2", 2)])
    _write_ndjson(ndjson, [_rec("V1", "1:1", 1)])

    records, source = HARNESS.load_resume_records(results, ndjson)

    assert source == "results file"
    assert len(records) == 2


def test_missing_results_file_rebuilds_from_ndjson(tmp_path):
    """The preregistered promise: resume from the recording."""
    results = tmp_path / "results.json"
    ndjson = tmp_path / "results.ndjson"
    _write_ndjson(ndjson, [_rec("V1", "1:1", 1), _rec("V1", "2:1", 2),
                           _rec("V1", "1:2", 3)])

    records, source = HARNESS.load_resume_records(results, ndjson)

    assert source == "NDJSON live recording"
    assert len(records) == 3
    assert {(r["arm"], r["label"], r["seed"]) for r in records} == {
        ("V1", "1:1", 1), ("V1", "2:1", 2), ("V1", "1:2", 3),
    }


def test_corrupt_results_file_falls_back_to_ndjson(tmp_path):
    """A truncated results file must not cost the whole run."""
    results = tmp_path / "results.json"
    ndjson = tmp_path / "results.ndjson"
    results.write_text('{"records": [{"arm": "V1", "lab', encoding="utf-8")
    _write_ndjson(ndjson, [_rec("V1", "1:1", 1), _rec("V1", "1:2", 2)])

    records, source = HARNESS.load_resume_records(results, ndjson)

    assert source == "NDJSON live recording"
    assert len(records) == 2


def test_torn_final_ndjson_line_keeps_the_good_records(tmp_path):
    """A hard kill can tear the last line; earlier cells survive."""
    results = tmp_path / "results.json"
    ndjson = tmp_path / "results.ndjson"
    _write_ndjson(
        ndjson,
        [_rec("V1", "1:1", 1), _rec("V1", "1:2", 2)],
        raw_tail='{"arm": "V1", "label": "2:1", "se',
    )

    records, source = HARNESS.load_resume_records(results, ndjson)

    assert source == "NDJSON live recording"
    assert len(records) == 2


def test_a_torn_tail_is_repaired_even_when_the_results_file_wins(tmp_path):
    """The run appends to the recording, so its tail must go in either case."""
    results = tmp_path / "results.json"
    ndjson = tmp_path / "results.ndjson"
    _write_results(results, [_rec("V1", "1:1", 1), _rec("V1", "1:2", 2)])
    torn = json.dumps(_rec("V1", "2:1", 3))[:60]
    _write_lines(ndjson, [json.dumps(_rec("V1", "1:1", 1)), torn],
                 torn_tail=True)

    records, source = HARNESS.load_resume_records(results, ndjson)

    assert source == "results file"
    assert len(records) == 2
    lines = ndjson.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1, "the torn tail must be cut back, not kept"
    json.loads(lines[0])


def test_corrupt_recording_refuses_even_when_the_results_file_wins(tmp_path):
    """A complete results file must not license appending to a corrupt trail."""
    results = tmp_path / "results.json"
    ndjson = tmp_path / "results.ndjson"
    _write_results(results, [_rec("V1", "1:1", 1), _rec("V1", "1:2", 2)])
    _write_lines(ndjson, [json.dumps(_rec("V1", "1:1", 1)), "{not json",
                          json.dumps(_rec("V1", "1:2", 2))])

    with pytest.raises(shared.CheckpointError) as caught:
        HARNESS.load_resume_records(results, ndjson)

    assert caught.value.code == "CHECKPOINT_CORRUPT"
    assert caught.value.evidence["line"] == 2
    assert len(ndjson.read_text(encoding="utf-8").splitlines()) == 3, (
        "a refused recording must not be rewritten")


def test_ndjson_may_hold_fewer_records_than_the_results_file(tmp_path):
    """The documented gap: a resumed run does not re-append to the NDJSON.

    The live recording can legitimately hold fewer cells than the results
    file.  That is expected, not lost work -- so the results file must still
    win, and the reconstruction must not treat the NDJSON as a truncation
    error.
    """
    results = tmp_path / "results.json"
    ndjson = tmp_path / "results.ndjson"
    _write_results(results, [_rec("V1", "1:1", 1), _rec("V1", "1:2", 2)])
    _write_ndjson(ndjson, [_rec("V1", "1:1", 1)])

    records, source = HARNESS.load_resume_records(results, ndjson)

    assert source == "results file"
    assert len(records) == 2


def test_no_sources_yields_no_records(tmp_path):
    records, source = HARNESS.load_resume_records(
        tmp_path / "absent.json", tmp_path / "absent.ndjson"
    )
    assert records == []
    assert source == "results file"


# ==================================================================
# The recording is read strictly, one record per cell
# ==================================================================

def test_a_repeated_cell_is_kept_once(tmp_path):
    """An agreeing repeat must not be counted as a second completed cell."""
    ndjson = tmp_path / "results.ndjson"
    _write_ndjson(ndjson, [_rec("V1", "1:1", 1), _rec("V1", "1:2", 2),
                           _rec("V1", "1:1", 1)])

    records, source = HARNESS.load_resume_records(tmp_path / "results.json", ndjson)

    assert source == "NDJSON live recording"
    assert [(r["arm"], r["label"], r["seed"]) for r in records] == [
        ("V1", "1:1", 1), ("V1", "1:2", 2)]


def test_an_unreadable_row_before_the_last_refuses_the_resume(tmp_path):
    """Skipping it would silently drop a completed cell from the result."""
    ndjson = tmp_path / "results.ndjson"
    _write_lines(ndjson, [json.dumps(_rec("V1", "1:1", 1)), "{not json",
                          json.dumps(_rec("V1", "1:2", 2))])

    with pytest.raises(shared.CheckpointError) as caught:
        HARNESS.load_resume_records(tmp_path / "results.json", ndjson)

    assert caught.value.code == "CHECKPOINT_CORRUPT"
    assert caught.value.evidence["line"] == 2
    assert len(ndjson.read_text(encoding="utf-8").splitlines()) == 3, (
        "a refused recording must not be rewritten")


def test_two_rows_that_disagree_about_one_cell_refuse_the_resume(tmp_path):
    """The later row wins only when the cell's measurement agrees."""
    ndjson = tmp_path / "results.ndjson"
    _write_ndjson(ndjson, [
        _rec("V1", "1:1", 1, results={"organica": {"displacement_index": 0.0}}),
        _rec("V1", "1:1", 1, results={"organica": {"displacement_index": 0.7}}),
    ])

    with pytest.raises(shared.CheckpointError) as caught:
        HARNESS.load_resume_records(tmp_path / "results.json", ndjson)

    assert caught.value.code == "CHECKPOINT_DUPLICATE_DISAGREES"
    assert caught.value.evidence["first_line"] == 1
    assert caught.value.evidence["second_line"] == 2
    assert caught.value.evidence["cell"] == {"arm": "V1", "label": "1:1", "seed": 1}
    assert "results" in caught.value.evidence["differing_fields"]


def test_a_torn_final_row_is_truncated_before_the_run_appends(tmp_path):
    """The tail must go before the next cell is appended past it."""
    ndjson = tmp_path / "results.ndjson"
    torn = json.dumps(_rec("V1", "2:1", 3))[:60]
    _write_lines(ndjson, [json.dumps(_rec("V1", "1:1", 1)),
                          json.dumps(_rec("V1", "1:2", 2)), torn],
                 torn_tail=True)

    records, source = HARNESS.load_resume_records(tmp_path / "results.json", ndjson)

    assert source == "NDJSON live recording"
    assert len(records) == 2
    lines = ndjson.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2, "the torn tail must be cut back, not kept"
    for line in lines:
        json.loads(line)

    # The next completed cell appends after the repair, and the recording must
    # still read as one record per cell -- a tail left in place would now be an
    # unreadable interior row.
    with open(ndjson, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(_rec("V1", "2:1", 3)) + "\n")
    report = shared.read_checkpoint_report(
        ndjson, key_fields=HARNESS.RESUME_KEY_FIELDS,
        cell_fields=HARNESS.RESUME_CELL_FIELDS)
    assert report["cells"] == 3
    assert report["partial_final_row"] is False


def test_a_complete_final_row_that_is_not_a_cell_is_corruption(tmp_path):
    """A torn write is a line that does not parse; a parseable bad row is not."""
    ndjson = tmp_path / "results.ndjson"
    _write_ndjson(ndjson, [_rec("V1", "1:1", 1),
                           {"arm": "V1", "seed": 2}])  # no label

    with pytest.raises(shared.CheckpointError) as caught:
        HARNESS.load_resume_records(tmp_path / "results.json", ndjson)

    assert caught.value.code == "CHECKPOINT_CORRUPT"
    assert caught.value.evidence["reason"] == "not_a_cell_row"


# --- the resume and the shared reader must not disagree ---------------------

@pytest.mark.parametrize("case, code", [
    ("unreadable", "CHECKPOINT_CORRUPT"),
    ("not_a_cell", "CHECKPOINT_CORRUPT"),
    ("disagreeing", "CHECKPOINT_DUPLICATE_DISAGREES"),
])
def test_the_resume_and_the_shared_reader_refuse_alike(tmp_path, case, code):
    middle = {
        "unreadable": "{not json",
        "not_a_cell": json.dumps({"arm": "V1", "label": "", "seed": 2}),
        "disagreeing": json.dumps(
            _rec("V1", "1:1", 1, results={"organica": {"displacement_index": 0.7}})),
    }[case]
    path = _write_lines(tmp_path / f"{case}.ndjson", [
        json.dumps(_rec("V1", "1:1", 1)), middle,
        json.dumps(_rec("V1", "1:2", 2))])

    with pytest.raises(shared.CheckpointError) as resume_caught:
        HARNESS.load_resume_records(tmp_path / "absent.json", path)
    with pytest.raises(shared.CheckpointError) as reader_caught:
        shared.read_checkpoint_report(path,
                                      key_fields=HARNESS.RESUME_KEY_FIELDS,
                                      cell_fields=HARNESS.RESUME_CELL_FIELDS)

    assert resume_caught.value.code == reader_caught.value.code == code
