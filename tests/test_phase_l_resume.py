"""Tests for the Phase L campaign's resume reconstruction.

The preregistration (Section 8.2) promises that "--resume rebuilds from the
recording if the results file is missing".  The harness originally read only
the results file, so that promise was unkept.  These tests cover the
reconstruction path directly, and are deliberately cheap: no engine cell is
run, so they do not compete with a live campaign for CPU.

Control discipline: each test asserts an exact record count, so a
reconstruction that silently dropped or duplicated cells fails rather than
passing quietly.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_harness():
    path = REPO_ROOT / "benchmarks" / "phase_l_campaign.py"
    spec = importlib.util.spec_from_file_location("_phase_l_campaign", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["_phase_l_campaign"] = module
    spec.loader.exec_module(module)
    return module


HARNESS = _load_harness()


def _rec(arm: str, label: str, seed: int) -> dict:
    return {"arm": arm, "label": label, "seed": seed, "params": {}, "results": {}}


def _write_results(path: Path, records: list) -> None:
    path.write_text(
        json.dumps({"protocol": {}, "records": records}),
        encoding="utf-8",
    )


def _write_ndjson(path: Path, records: list, raw_tail: str = "") -> None:
    with open(path, "w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec) + "\n")
        if raw_tail:
            fh.write(raw_tail)


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
