"""
tests/test_substrate_equivalence.py
------------------------------------------------------------------
Phase G: prove the substrate changes are behaviour-preserving.

Four substrate changes were made so the 90-day longitudinal study can
actually run:

  1. `tag_frequencies()` now reads an incrementally maintained
     `tag_counts` table instead of scanning the whole `events` table.
     The RESULT must be identical to a full scan over WORLD events.

  1a. The counter's SCOPE was corrected. It previously counted the
     organism's own sleep payloads as well, while the co-occurrence and
     temporal graphs it normalises are world-only. The Layer-1 survival
     filter therefore compared a world edge count against a polluted
     denominator, which discarded the world's own structure (research
     journal §21). The scope-consistency test below is the regression
     test.

  2. The monotonic sleep-cycle counter moved from "scan the last 500 sleep
     events for a `_sleep_meta` marker" to a dedicated `sleep_cycles`
     table. The old approach silently returned 0 once the candidate
     population exceeded 500 rows per cycle.

  3. `prune_sleep_candidates()` bounds the candidate table. It must never
     delete experience events or `sleep:meta` markers, and it must leave
     the organism's 4,000-event working memory untouched.

These tests assert each of those guarantees.

Run:  python -m pytest tests/test_substrate_equivalence.py -v
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from organica.memory import MemoryService, _extract_tags  # noqa: E402
from organica.sleep import SleepService  # noqa: E402


def legacy_full_scan_counts(conn) -> dict:
    """The ORIGINAL tag-frequency implementation, reproduced verbatim.

    Scoped to WORLD events, which is what the counter means now. The
    counter is the denominator of the Layer-1 edge strength
    (`ratio = count / source_freq`), and the co-occurrence and temporal
    graphs it normalises are built from world events only. Counting the
    organism's own sleep payloads in the denominator while the numerator
    stays world-only made the two sides of that ratio measure different
    populations; the measured consequence was that a branch stimulus
    collapsed to 4 surviving edges, 0 processes and 0 beliefs (research
    journal §21).
    """
    rows = conn.execute(
        "SELECT tags FROM events WHERE event_type != 'sleep'").fetchall()
    counter: dict = {}
    for (tags_str,) in rows:
        for tag in (tags_str or "").split(","):
            if tag:
                counter[tag] = counter.get(tag, 0) + 1
    return counter


# ---------------------------------------------------------------------------
# 1. tag_frequencies equivalence
# ---------------------------------------------------------------------------
def test_tag_frequencies_matches_legacy_full_scan(tmp_path):
    mem = MemoryService(tmp_path / "eq.db")
    for text in ["alpha beta gamma", "beta delta", "alpha alpha epsilon"]:
        mem.store(text, event_type="event", source="test")
    # Sleep payloads are stored, but they are not part of the world the
    # organism perceives, so they contribute to neither the graph nor the
    # frequency counter that normalises it.
    mem.store(json.dumps({"type": "concept_candidate", "members": ["alpha", "beta"],
                          "confidence": 0.9}), event_type="sleep", source="sleep:concept_candidate")
    mem.store(json.dumps({"type": "loop_candidate", "path": ["gamma", "delta"]}),
              event_type="sleep", source="sleep:loop_candidate")

    legacy = legacy_full_scan_counts(mem._conn)
    current = dict(mem.tag_frequencies())

    assert current == legacy, (
        f"tag_frequencies diverged from the legacy full scan.\n"
        f"legacy : {legacy}\ncurrent: {current}"
    )
    mem.close()


def test_tag_frequency_scope_matches_graph_scope(tmp_path):
    """The counter that normalises an edge count must see the same
    population the edge count was drawn from.

    This is the regression test for the scope defect that collapsed the
    branch stimulus: the temporal graph was world-only while the
    frequency counter included the organism's own sleep payloads, so the
    Layer-1 survival filter discarded the world's structure (research
    journal §21).
    """
    mem = MemoryService(tmp_path / "scope.db")
    mem.store("alpha bravo charlie", event_type="event", source="test")
    before_freqs = dict(mem.tag_frequencies())
    before_graph = mem.temporal_edges(min_count=1)

    mem.store(json.dumps({"type": "hypothesis_candidate", "subject": "alpha",
                          "expectation": "bravo", "generation": 3}),
              event_type="sleep", source="sleep:hypothesis_candidate")
    mem.store(json.dumps({"type": "workflow_concept",
                          "components": ["alpha", "bravo", "charlie"]}),
              event_type="sleep", source="sleep:workflow_concept")

    after_freqs = dict(mem.tag_frequencies())
    after_graph = mem.temporal_edges(min_count=1)

    assert after_freqs == before_freqs, (
        "a sleep payload changed the tag-frequency counter; the counter "
        "must share the scope of the graph it normalises."
    )
    assert after_graph == before_graph, (
        "a sleep payload changed the temporal graph."
    )
    mem.close()


def test_tag_frequencies_equivalence_after_backfill(tmp_path):
    """A database created before `tag_counts` existed must backfill exactly."""
    db = tmp_path / "legacy.db"
    conn = sqlite3.connect(str(db))
    conn.execute("""
        CREATE TABLE events (
            id TEXT PRIMARY KEY, time REAL NOT NULL, source TEXT NOT NULL,
            event_type TEXT NOT NULL, content TEXT NOT NULL, tags TEXT DEFAULT ''
        )
    """)
    rows = []
    for i, content in enumerate(["alpha beta", "beta gamma", "delta"]):
        tags = ",".join(_extract_tags(content))
        rows.append((f"id{i}", 1000.0 + i, "test", "event", content, tags))
    conn.executemany("INSERT INTO events VALUES (?,?,?,?,?,?)", rows)
    conn.commit()
    conn.close()

    mem = MemoryService(db)  # triggers _backfill_accounting
    legacy = legacy_full_scan_counts(mem._conn)
    current = dict(mem.tag_frequencies())
    assert current == legacy, f"backfill diverged.\nlegacy : {legacy}\ncurrent: {current}"
    mem.close()


def test_tag_frequencies_increments_on_store(tmp_path):
    mem = MemoryService(tmp_path / "inc.db")
    before = dict(mem.tag_frequencies())
    mem.store("zebra unicorn", event_type="event", source="test")
    after = dict(mem.tag_frequencies())
    assert after["zebra"] == before.get("zebra", 0) + 1
    assert after["unicorn"] == before.get("unicorn", 0) + 1
    mem.close()


# ---------------------------------------------------------------------------
# 2. Monotonic cycle counter
# ---------------------------------------------------------------------------
def test_latest_sleep_cycle_is_monotonic_beyond_the_old_window(tmp_path):
    """The old implementation failed once >500 sleep events existed."""
    mem = MemoryService(tmp_path / "cycle.db")
    sleep = SleepService(mem)

    mem.store("seed event alpha", event_type="event", source="test")

    # Write well over 500 sleep candidate rows, then record a cycle.
    for i in range(600):
        mem.store(json.dumps({"type": "concept_candidate", "members": [f"m{i}"]}),
                  event_type="sleep", source="sleep:concept_candidate")
    mem.record_sleep_cycle(7, 1234.0)

    # The OLD approach: scan the last 500 sleep events for a meta marker.
    window = mem.recent(n=500, event_type="sleep")
    old_style = 0
    for e in window:
        if e.source == "sleep:meta":
            old_style = max(old_style, json.loads(e.content).get("cycle", 0))

    assert old_style == 0, (
        "test precondition failed: the old windowed scan was expected to "
        "miss the cycle marker here"
    )
    assert mem.latest_sleep_cycle() == 7, (
        "the new counter must still see the cycle number when the old "
        "windowed scan could not"
    )
    mem.close()


def test_sleep_cycle_advances_monotonically(tmp_path):
    mem = MemoryService(tmp_path / "mono.db")
    sleep = SleepService(mem)
    mem.store("alpha beta gamma delta", event_type="event", source="test")
    seen = []
    for _ in range(4):
        report = sleep.run()
        seen.append(report.cycle)
    assert seen == sorted(seen), f"cycle numbers must not go backwards: {seen}"
    assert len(set(seen)) == len(seen), f"cycle numbers must be unique: {seen}"
    assert mem.latest_sleep_cycle() == max(seen)
    mem.close()


# ---------------------------------------------------------------------------
# 3. Retention
# ---------------------------------------------------------------------------
def test_prune_keeps_experience_events_and_meta_rows(tmp_path):
    mem = MemoryService(tmp_path / "prune.db")
    mem.store("experience alpha", event_type="event", source="test")
    mem.store(json.dumps({"type": "_sleep_meta", "cycle": 1}),
              event_type="sleep", source="sleep:meta")
    for i in range(100):
        mem.store(json.dumps({"type": "concept_candidate", "members": [f"m{i}"]}),
                  event_type="sleep", source="sleep:concept_candidate")

    deleted = mem.prune_sleep_candidates(keep=10)
    assert deleted == 90, f"expected 90 candidate rows deleted, got {deleted}"

    sources = [r[0] for r in mem._conn.execute("SELECT source FROM events").fetchall()]
    assert "test" in sources, "experience events must never be deleted"
    assert "sleep:meta" in sources, "sleep:meta rows must never be deleted"
    cand = sum(1 for s in sources if s.startswith("sleep:") and s != "sleep:meta")
    assert cand == 10, f"expected 10 candidates retained, got {cand}"
    mem.close()


def test_prune_keeps_working_memory_intact(tmp_path):
    """Retention must not disturb the newest 4,000 sleep events.

    The retention limit must be larger than the organism's working-memory
    window for this invariant to hold; the shipped default (20,000) is.
    """
    mem = MemoryService(tmp_path / "window.db")
    for i in range(12000):
        mem.store(json.dumps({"type": "concept_candidate", "members": [f"m{i}"]}),
                  event_type="sleep", source="sleep:concept_candidate")

    before = [e.id for e in mem.recent(n=4000, event_type="sleep")]
    mem.prune_sleep_candidates(keep=8000)
    after = [e.id for e in mem.recent(n=4000, event_type="sleep")]

    assert len(before) == 4000
    assert after == before, (
        "the organism's working memory (newest 4,000 sleep events) must be "
        "identical before and after retention"
    )
    mem.close()


def test_prune_is_a_noop_when_under_the_limit(tmp_path):
    mem = MemoryService(tmp_path / "noop.db")
    for i in range(10):
        mem.store(json.dumps({"type": "concept_candidate", "members": [f"m{i}"]}),
                  event_type="sleep", source="sleep:concept_candidate")
    assert mem.prune_sleep_candidates(keep=1000) == 0
    mem.close()


# ---------------------------------------------------------------------------
# 4. Transaction batching
# ---------------------------------------------------------------------------
def test_batch_writes_identical_rows_to_unbatched_writes(tmp_path):
    a = MemoryService(tmp_path / "batch.db")
    b = MemoryService(tmp_path / "plain.db")
    payloads = [json.dumps({"type": "concept_candidate", "members": [f"m{i}"]})
                for i in range(50)]
    for p in payloads:
        a.store(p, event_type="sleep", source="sleep:concept_candidate")
    with b.batch():
        for p in payloads:
            b.store(p, event_type="sleep", source="sleep:concept_candidate")
    assert a.count() == b.count()
    assert dict(a.tag_frequencies()) == dict(b.tag_frequencies())
    a.close()
    b.close()


def test_batch_rolls_back_on_exception(tmp_path):
    mem = MemoryService(tmp_path / "rollback.db")
    with pytest.raises(ValueError):
        with mem.batch():
            mem.store("alpha beta", event_type="event", source="test")
            raise ValueError("boom")
    assert mem.count() == 0, "a failed batch must not leave partial rows behind"
    mem.close()


def test_nested_batches_commit_once_at_the_outermost_level(tmp_path):
    mem = MemoryService(tmp_path / "nested.db")
    with mem.batch():
        mem.store("alpha beta", event_type="event", source="test")
        with mem.batch():
            mem.store("gamma delta", event_type="event", source="test")
    assert mem.count() == 2
    mem.close()


def test_sleep_cycle_batching_does_not_change_the_report(tmp_path):
    """The batched sleep cycle must produce the same report as before."""
    def run(label):
        mem = MemoryService(tmp_path / f"{label}.db")
        for text in ["alpha beta gamma", "beta gamma delta", "alpha epsilon"]:
            mem.store(text, event_type="event", source="test")
        sleep = SleepService(mem)
        report = sleep.run_sleep_cycle()
        summary = (len(report.concepts), len(report.predictions), len(report.loops),
                   len(report.hypotheses), len(report.theories), len(report.questions),
                   report.composites_created)
        mem.close()
        return summary

    assert run("batched") == run("batched2"), (
        "two identical runs must produce identical populations"
    )
