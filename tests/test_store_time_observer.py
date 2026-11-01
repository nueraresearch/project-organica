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
