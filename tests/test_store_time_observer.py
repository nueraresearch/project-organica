"""Fast checks for the store-time observer's bookkeeping (no arm is run).

The observer's full self-test runs an entire arm in about 135 s, so it cannot be
a per-commit gate.  These tests cover the two things that can be wrong without a
run: the stage classification, and the reconciliation arithmetic that decides
whether a cycle may be reported as "no write explains it" or must be reported
indeterminate.
"""

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from benchmarks.store_time_observer import reconcile, stage_of, summarise  # noqa: E402


def test_stage_distinguishes_ingest_from_construction():
    assert stage_of("sleep:concept") == "construction"
    assert stage_of("sleep:meta") == "construction"
    assert stage_of("env") == "ingest"
    assert stage_of("stream") == "ingest"


def test_reconcile_accepts_a_balanced_cycle():
    r = reconcile([1, 1, 1])
    assert r["observed_writes"] == 3
    assert r["accepted_rows"] == 3
    assert r["reconciled"] is True


def test_reconcile_fires_when_a_call_stored_nothing():
    """A call the wrapper saw that stored no row must NOT reconcile."""
    r = reconcile([1, 0])
    assert r["observed_writes"] == 2
    assert r["accepted_rows"] == 1
    assert r["reconciled"] is False


def test_reconcile_fires_when_rows_were_removed():
    r = reconcile([1, -1])
    assert r["net_delta"] == 0
    assert r["reconciled"] is False


def test_reconcile_cannot_pass_on_an_empty_cycle():
    """No calls is not a reconciled cycle; it is an absent measurement."""
    r = reconcile([])
    assert r["observed_writes"] == 0
    assert r["reconciled"] is False


def test_summarise_names_markers_and_unreconciled_cycles():
    per = {
        "1": {"construction": 5, "ingest": 0, "reconciled": True},
        "2": {"construction": 7, "ingest": 0, "reconciled": False},
        "pre-2": {"construction": 0, "ingest": 8, "reconciled": True},
    }
    s = summarise(per)
    assert s["markers"] == 2
    assert s["first"] == 1 and s["last"] == 2
    assert s["unreconciled"] == ["2"]
    assert s["ingest_buckets"] == 1
    assert s["ingest_per_bucket"] == [8]


def test_load_trace_resolves_the_digest_table(tmp_path):
    """A saved trace must be readable without re-deriving its digest index."""
    import gzip
    import json

    from benchmarks.store_time_observer import load_trace

    path = tmp_path / "trace.jsonl.gz"
    header = {"kind": "store_time_observer_trace", "observer_version": 1,
              "fields": ["cycle", "accepted", "digest_index", "stage", "source"],
              "digests": [{"digest": "abc123", "id": "concept:1", "type": "concept"},
                          {"digest": "def456", "id": None, "type": None}]}
    with gzip.open(path, "wt", encoding="utf-8") as f:
        f.write(json.dumps(header) + "\n")
        f.write(json.dumps(["3", 1, 0, 1, "sleep:concept"]) + "\n")
        f.write(json.dumps(["pre-4", 1, 1, 0, "env"]) + "\n")

    got_header, rows = load_trace(path)
    rows = list(rows)
    assert got_header["observer_version"] == 1
    assert len(rows) == 2
    assert rows[0]["cycle"] == "3" and rows[0]["id"] == "concept:1"
    assert rows[0]["stage"] == "construction" and rows[0]["source"] == "sleep:concept"
    assert rows[1]["stage"] == "ingest" and rows[1]["id"] is None


def test_find_offered_uses_only_the_declared_window():
    """The brief fixes the search window: the cycle and the one before it."""
    from benchmarks.store_time_observer import find_offered

    part = {"per_cycle": {
        "5": {"candidates": {"d1": {"id": "c1", "stage": "construction",
                                    "type": "concept", "count": 1}}},
        "9": {"candidates": {"d2": {"id": "c9", "stage": "ingest",
                                    "type": None, "count": 1}}},
    }}
    assert find_offered(part, 6, "c1")["cycle"] == "5"
    assert find_offered(part, 5, "c1")["stage"] == "construction"
    assert find_offered(part, 12, "c9") is None


def test_f4_needs_reconciliation_before_attribution():
    """Both conditions, in order: an unreconciled cycle is fatal on its own."""
    from benchmarks.store_time_observer import f4_decision

    attributed = [{"cycle": 10, "candidate": "c1"}]
    ok = {"10": {"reconciled": True}, "11": {"reconciled": True}, "12": {"reconciled": True}}
    bad = {"10": {"reconciled": True}, "11": {"reconciled": False}, "12": {"reconciled": True}}

    passed, verdict = f4_decision(attributed, ok, (10, 11, 12))
    assert passed is True and verdict == "attributed"

    passed, verdict = f4_decision(attributed, bad, (10, 11, 12))
    assert passed is False and "did not reconcile" in verdict

    passed, verdict = f4_decision([], ok, (10, 11, 12))
    assert passed is False and "no membership difference" in verdict


def test_label_separates_pool_writes_from_survivor_restores():
    """Same source, same type: only the engine's call path tells them apart."""
    from benchmarks.store_time_observer import label_of

    assert label_of("sleep:concept_candidate", ("run", "_store_candidates")) == \
        "pool:concept_candidate"
    assert label_of("sleep:concept_candidate", ("run", "_prune")) == \
        "restore:concept_candidate"
    assert label_of("sleep:meta", ("run", "_store_candidates")) == "marker"
    assert label_of("env", ()) == "ingest"


def test_f5_refuses_a_degenerate_split():
    """One pool label everywhere measures nothing; the gate must be able to fire."""
    from benchmarks.store_time_observer import f5_decision

    ok_rec = {"10": {"reconciled": True}}
    attributed = [{"cycle": 10, "candidate": "c1", "label": "pool:dream"}]

    passed, verdict = f5_decision(
        attributed, ["pool:concept_candidate", "pool:dream"], ok_rec, (10,))
    assert passed is True and verdict == "labelled"

    passed, verdict = f5_decision(attributed, ["pool:dream"], ok_rec, (10,))
    assert passed is False and "degenerate" in verdict

    passed, verdict = f5_decision([{"cycle": 10, "candidate": "c1"}],
                                  ["pool:a", "pool:b"], ok_rec, (10,))
    assert passed is False and "no label" in verdict

    passed, verdict = f5_decision(attributed, ["pool:a", "pool:b"],
                                  {"10": {"reconciled": False}}, (10,))
    assert passed is False and "did not reconcile" in verdict


def test_classify_cell_has_no_fifth_bucket():
    """Every cell lands in the pre-registered space, and partial is not a bucket."""
    from benchmarks.store_time_observer import classify_cell

    assert classify_cell(True, 0, 0, []) == "no_difference_at_pair"
    assert classify_cell(True, 4, 4, ["ingest"] * 4) == "A"
    assert classify_cell(True, 4, 4, ["pool:phrase_candidate"] * 4) == "B_restated"
    assert classify_cell(True, 4, 4, ["pool:dream"] * 4) == \
        "construction_other:pool:dream"
    assert classify_cell(True, 4, 0, []) == "C_accounted"
    assert classify_cell(True, 4, 2, ["pool:dream"] * 2) == "indeterminate"
    assert classify_cell(False, 4, 4, ["pool:dream"] * 4) == "indeterminate"
