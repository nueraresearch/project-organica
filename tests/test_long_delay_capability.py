"""Tests for the online long-delay capability instrument."""
from __future__ import annotations

import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks.long_delay_capability import (  # noqa: E402
    _chunk,
    _logloss,
    _window,
    seeded_triangles,
    stream_digest,
    stream_for,
)


def test_seeded_triangles_are_deterministic():
    assert seeded_triangles(20302801) == seeded_triangles(20302801)


def test_seeded_triangles_vary_the_block_order():
    a = seeded_triangles(20302801)
    b = seeded_triangles(20302802)
    assert sorted(a) == sorted(b)
    assert a != b


def test_stream_digest_depends_on_the_seed():
    assert stream_for(20302801) != stream_for(20302802)
    assert stream_digest(20302801) != stream_digest(20302802)


def test_chunk_wraps_the_stream():
    events = [str(i) for i in range(100)]
    assert _chunk(events, 0) == events[:8]
    assert _chunk(events, 12) == events[96:100] + events[:4]


def test_logloss_scores_the_next_cycle_before_it_is_ingested():
    vocabulary = {"alpha", "bravo"}
    predictions = {("alpha", "bravo"): 1.0, ("bravo", "alpha"): 1.0}
    chunk = ["alpha", "bravo"]
    loss, labels, hits = _logloss(predictions, "alpha", chunk, vocabulary)
    # Every source-target pair over the vocabulary is scored, so a confident
    # prediction of the false pair is punished as well as the true one.
    assert labels > 0
    assert loss is not None and loss > 0.0
    assert hits >= 1


def test_logloss_reports_not_measurable_without_labels():
    loss, labels, _ = _logloss({}, "alpha", [], set())
    assert loss is None
    assert labels == 0


def test_window_excludes_cycles_without_a_score():
    rows = [
        {"cycle": 39, "log_loss": 0.5, "labels": 10, "predictions": 1},
        {"cycle": 40, "log_loss": None, "labels": 0, "predictions": 0},
        {"cycle": 41, "log_loss": 0.25, "labels": 10, "predictions": 2},
    ]
    window = _window(rows, (40, 90))
    assert window["mean_log_loss"] == 0.25
    assert window["cycles"] == 1
    assert window["labels"] == 10
    assert window["predictions"] == 2


def test_window_reports_not_measurable_for_an_empty_window():
    window = _window([], (40, 90))
    assert window["mean_log_loss"] is None
    assert window["labels"] == 0
    assert window["cycles"] == 0
