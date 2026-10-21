"""
Memory Service — Version 0.

This is all that exists right now.

Store events. Retrieve them. That's it.
We will look at what actually accumulates before deciding what to build next.
"""

import json
import re
import sqlite3
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from collections import Counter


DB_PATH = Path(__file__).parent.parent / "memory.db"

# How many persisted sleep candidates to retain. The organism's working
# memory is the most recent 4,000 sleep events (SleepService._load_prior_candidates),
# so anything above that window is invisible to cognition. Retaining a
# generous multiple keeps behaviour identical while bounding disk growth:
# the candidate table is otherwise the single largest consumer of space
# (measured: 1.65M rows / 942MB after ~500 cycles, growing ~3,300 rows per
# cycle -> roughly 210GB over a 90-day run at a 30s interval).
DEFAULT_SLEEP_RETENTION = 20000


@dataclass
class Event:
    id: str
    time: float
    source: str
    event_type: str
    content: str
    tags: list[str] = field(default_factory=list)

    @staticmethod
    def from_row(row: tuple) -> "Event":
        id_, time_, source, event_type, content, tags_str = row
        return Event(
            id=id_,
            time=time_,
            source=source,
            event_type=event_type,
            content=content,
            tags=[t for t in tags_str.split(",") if t] if tags_str else [],
        )


class MemoryService:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._batching = 0
        self._init_schema()

    @contextmanager
    def batch(self):
        """Group many writes into a single transaction.

        Storing sleep candidates one at a time costs one disk sync per
        candidate. Profiling a single sleep cycle against the live
        substrate showed 1,023 commits consuming 3.0s of a 4.5s cycle --
        two thirds of the time spent fsyncing, once per candidate. Under
        a batch, the writes are committed together at the end of the
        block, and the block is atomic: an exception rolls it back rather
        than leaving half a cycle persisted.
        """
        self._batching += 1
        try:
            yield self
        except Exception:
            self._batching -= 1
            if self._batching == 0:
                self._conn.rollback()
            raise
        else:
            self._batching -= 1
            if self._batching == 0:
                self._conn.commit()


    def _init_schema(self):
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id          TEXT PRIMARY KEY,
                time        REAL NOT NULL,
                source      TEXT NOT NULL,
                event_type  TEXT NOT NULL,
                content     TEXT NOT NULL,
                tags        TEXT DEFAULT ''
            )
        """)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS cooccurrences (
                tag_a   TEXT NOT NULL,
                tag_b   TEXT NOT NULL,
                count   INTEGER DEFAULT 1,
                PRIMARY KEY (tag_a, tag_b)
            )
        """)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS precedes (
                tag_from    TEXT NOT NULL,
                tag_to      TEXT NOT NULL,
                count       INTEGER DEFAULT 1,
                PRIMARY KEY (tag_from, tag_to)
            )
        """)
        self._conn.execute("CREATE INDEX IF NOT EXISTS idx_time ON events(time)")

        # --- Substrate accounting tables (Phase G endurance) -------------
        # `tag_counts` replaces a full-table scan of `events` with an
        # O(1) read. The scan it replaces cost 4.8s per sleep cycle at
        # 1.65M rows and grew linearly, which alone made a 90-day run
        # impossible.
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS tag_counts (
                tag   TEXT PRIMARY KEY,
                count INTEGER NOT NULL DEFAULT 0
            )
        """)
        # `sleep_cycles` is the authoritative monotonic sleep-cycle counter.
        # It previously had to be recovered by scanning the most recent 500
        # sleep events for a `_sleep_meta` marker, which silently returned 0
        # once the candidate population exceeded 500 rows per cycle -- the
        # cycle counter then reset to 1 mid-run, corrupting the time axis of
        # every longitudinal measurement.
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS sleep_cycles (
                cycle   INTEGER PRIMARY KEY,
                ran_at  REAL
            )
        """)
        # Composite index for `recent(n, event_type)`: filters on
        # event_type and orders by time without scanning the whole table.
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_type_time ON events(event_type, time DESC)"
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_source ON events(source)"
        )

        self._conn.commit()
        self._backfill_accounting()

    def _backfill_accounting(self):
        """Rebuild `tag_counts` and `sleep_cycles` from an existing database.

        Only runs when the accounting tables are empty but `events` is not,
        i.e. exactly once for a database created before these tables
        existed. Afterwards both tables are maintained incrementally.
        """
        has_events = self._conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        if not has_events:
            return

        if self._conn.execute("SELECT COUNT(*) FROM tag_counts").fetchone()[0] == 0:
            rows = self._conn.execute("SELECT tags FROM events").fetchall()
            counts: Counter = Counter()
            for (tags_str,) in rows:
                for tag in (tags_str or "").split(","):
                    if tag:
                        counts[tag] += 1
            self._conn.executemany(
                "INSERT INTO tag_counts (tag, count) VALUES (?, ?)",
                [(t, c) for t, c in counts.items()],
            )

        if self._conn.execute("SELECT COUNT(*) FROM sleep_cycles").fetchone()[0] == 0:
            rows = self._conn.execute(
                "SELECT content FROM events WHERE source = 'sleep:meta'"
            ).fetchall()
            recovered = []
            for (content,) in rows:
                try:
                    payload = json.loads(content)
                    if payload.get("type") == "_sleep_meta":
                        recovered.append((int(payload.get("cycle", 0)), payload.get("ran_at")))
                except (json.JSONDecodeError, ValueError, TypeError):
                    continue
            # A cycle number can repeat across restarts, so keep the
            # highest observed value per cycle number.
            best: dict[int, float] = {}
            for cycle, ran_at in recovered:
                if cycle > best.get(cycle, -1):
                    best[cycle] = ran_at
            self._conn.executemany(
                "INSERT OR REPLACE INTO sleep_cycles (cycle, ran_at) VALUES (?, ?)",
                [(c, best[c]) for c in sorted(best)],
            )

        self._conn.commit()


    def store(self, content: str, event_type: str = "observe", source: str = "env") -> Event:
        event = Event(
            id=str(uuid.uuid4()),
            time=time.time(),
            source=source,
            event_type=event_type,
            content=content,
            tags=_extract_tags(content),
        )
        self._conn.execute(
            "INSERT INTO events VALUES (?, ?, ?, ?, ?, ?)",
            (event.id, event.time, event.source, event.event_type,
             event.content, ",".join(event.tags)),
        )
        # Only build graph edges from external experience, not internal
        # sleep output.  Sleep candidates are stored but don't pollute
        # the co-occurrence / temporal graphs.
        if event_type != "sleep":
            self._record_cooccurrences(event.tags)
            self._record_temporal_edges(event.tags)
        # Maintain the incremental tag-frequency counter. This mirrors
        # exactly what a full `SELECT tags FROM events` scan would count
        # (including tags contributed by sleep payloads), but in O(1)
        # amortised time instead of O(total rows) per sleep cycle.
        self._record_tag_counts(event.tags)
        if not self._batching:
            self._conn.commit()
        return event

    def _record_tag_counts(self, tags: list[str]):
        """Increment the persistent tag-frequency counters."""
        if not tags:
            return
        self._conn.executemany(
            """
            INSERT INTO tag_counts (tag, count) VALUES (?, 1)
            ON CONFLICT(tag) DO UPDATE SET count = count + 1
            """,
            [(t,) for t in tags],
        )

    def _record_cooccurrences(self, tags: list[str]):
        """
        For every pair of tags in this event, increment their co-occurrence count.
        Tags that appear together repeatedly form edges. Those edges are the
        raw material for later discovering phrases, clusters, and noise.
        Order-normalised: (auth, failure) and (failure, auth) are the same edge.
        """
        for i in range(len(tags)):
            for j in range(i + 1, len(tags)):
                a, b = sorted([tags[i], tags[j]])
                self._conn.execute("""
                    INSERT INTO cooccurrences (tag_a, tag_b, count) VALUES (?, ?, 1)
                    ON CONFLICT(tag_a, tag_b) DO UPDATE SET count = count + 1
                """, (a, b))

    def _record_temporal_edges(self, new_tags: list[str], lookback: int = 3):
        """
        Connect tags from the previous N events to tags from this event.
        This records what tends to *precede* what — the organism's first
        approximation of causality.

        lookback=3 means: "anything in the last 3 events may predict this."
        We weight all lookback positions equally for now. Decay can come later.
        """
        if not new_tags:
            return
        rows = self._conn.execute(
            "SELECT tags FROM events ORDER BY time DESC LIMIT ?", (lookback,)
        ).fetchall()
        for (tags_str,) in rows:
            prior_tags = [t for t in (tags_str or "").split(",") if t]
            for tag_from in prior_tags:
                for tag_to in new_tags:
                    if tag_from != tag_to:
                        self._conn.execute("""
                            INSERT INTO precedes (tag_from, tag_to, count) VALUES (?, ?, 1)
                            ON CONFLICT(tag_from, tag_to) DO UPDATE SET count = count + 1
                        """, (tag_from, tag_to))

    def cooccurrences(self, min_count: int = 1) -> list[tuple[str, str, int]]:
        """Return all co-occurrence edges with count >= min_count, sorted by count."""
        rows = self._conn.execute(
            "SELECT tag_a, tag_b, count FROM cooccurrences WHERE count >= ? ORDER BY count DESC",
            (min_count,)
        ).fetchall()
        return [(a, b, c) for a, b, c in rows]

    def neighbors(self, tag: str) -> list[tuple[str, int]]:
        """Return all tags that co-occur with this one, with counts."""
        rows = self._conn.execute("""
            SELECT tag_b, count FROM cooccurrences WHERE tag_a = ?
            UNION
            SELECT tag_a, count FROM cooccurrences WHERE tag_b = ?
            ORDER BY count DESC
        """, (tag, tag)).fetchall()
        return [(t, c) for t, c in rows]

    def what_follows(self, tag: str) -> list[tuple[str, int]]:
        """What tags tend to appear shortly AFTER this tag? (temporal)"""
        rows = self._conn.execute(
            "SELECT tag_to, count FROM precedes WHERE tag_from = ? ORDER BY count DESC",
            (tag,)
        ).fetchall()
        return [(t, c) for t, c in rows]

    def what_precedes(self, tag: str) -> list[tuple[str, int]]:
        """What tags tend to appear shortly BEFORE this tag? (temporal)"""
        rows = self._conn.execute(
            "SELECT tag_from, count FROM precedes WHERE tag_to = ? ORDER BY count DESC",
            (tag,)
        ).fetchall()
        return [(t, c) for t, c in rows]

    def temporal_edges(self, min_count: int = 2) -> list[tuple[str, str, int]]:
        """Return all temporal edges with count >= min_count, sorted by count."""
        rows = self._conn.execute(
            "SELECT tag_from, tag_to, count FROM precedes WHERE count >= ? ORDER BY count DESC",
            (min_count,)
        ).fetchall()
        return [(f, t, c) for f, t, c in rows]

    def recent(self, n: int = 50, event_type: Optional[str] = None) -> list[Event]:
        if event_type:
            rows = self._conn.execute(
                "SELECT * FROM events WHERE event_type=? ORDER BY time DESC LIMIT ?",
                (event_type, n),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM events ORDER BY time DESC LIMIT ?", (n,)
            ).fetchall()
        return [Event.from_row(r) for r in rows]

    def since(self, timestamp: float) -> list[Event]:
        rows = self._conn.execute(
            "SELECT * FROM events WHERE time > ? ORDER BY time ASC", (timestamp,)
        ).fetchall()
        return [Event.from_row(r) for r in rows]

    def search(self, query: str, limit: int = 20) -> list[Event]:
        pattern = f"%{query}%"
        rows = self._conn.execute(
            "SELECT * FROM events WHERE content LIKE ? OR tags LIKE ? ORDER BY time DESC LIMIT ?",
            (pattern, pattern, limit),
        ).fetchall()
        return [Event.from_row(r) for r in rows]

    def tag_frequencies(self) -> Counter:
        """Return tag frequencies.

        Reads the incrementally maintained `tag_counts` table instead of
        scanning the whole `events` table. The result is identical to the
        historical full scan (verified in tests/test_substrate_equivalence.py);
        only the cost profile changed, from O(total rows) to O(distinct tags).
        """
        rows = self._conn.execute("SELECT tag, count FROM tag_counts").fetchall()
        return Counter({tag: count for tag, count in rows})

    def latest_sleep_cycle(self) -> int:
        """Return the highest sleep-cycle number ever recorded.

        This is the authoritative monotonic cycle counter. It used to be
        recovered by scanning the most recent 500 sleep events for a
        `_sleep_meta` marker, which returned 0 as soon as the candidate
        population exceeded 500 rows per cycle -- silently resetting the
        cycle counter mid-run.
        """
        row = self._conn.execute("SELECT MAX(cycle) FROM sleep_cycles").fetchone()
        return int(row[0]) if row and row[0] is not None else 0

    def record_sleep_cycle(self, cycle: int, ran_at=None):
        """Record that a sleep cycle with *cycle* has completed."""
        self._conn.execute(
            "INSERT OR REPLACE INTO sleep_cycles (cycle, ran_at) VALUES (?, ?)",
            (int(cycle), ran_at),
        )
        if not self._batching:
            self._conn.commit()

    def prune_sleep_candidates(self, keep: int = DEFAULT_SLEEP_RETENTION) -> int:
        """Delete sleep-candidate rows beyond the newest *keep* rows.

        Experience events (`event_type != 'sleep'`) and `sleep:meta` markers
        are never deleted: they are the empirical record and the cycle
        history. The candidate rows are re-emitted every cycle, so retaining
        a window comfortably larger than the organism's 4,000-event working
        memory leaves cognition untouched while bounding disk growth.

        Returns the number of rows deleted.
        """
        if keep <= 0:
            return 0
        # Order by rowid as well as time: rowid is monotonic for append-only
        # inserts, so it is a stable tie-breaker when two rows share a
        # timestamp. The cutoff is the rowid of the keep-th newest candidate,
        # so exactly `keep` candidates survive.
        cutoff = self._conn.execute(
            """
            SELECT rowid FROM events
            WHERE event_type = 'sleep' AND source != 'sleep:meta'
            ORDER BY time DESC, rowid DESC
            LIMIT 1 OFFSET ?
            """,
            (keep - 1,),
        ).fetchone()
        if not cutoff:
            return 0
        cur = self._conn.execute(
            """
            DELETE FROM events
            WHERE event_type = 'sleep' AND source != 'sleep:meta' AND rowid < ?
            """,
            (cutoff[0],),
        )
        deleted = cur.rowcount if cur.rowcount and cur.rowcount > 0 else 0
        if not self._batching:
            self._conn.commit()
        return deleted

    def count(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]

    def dump(self) -> list[dict]:
        """Return everything — used for inspection."""
        events = self.recent(9999)
        return [
            {
                "time": e.time,
                "type": e.event_type,
                "source": e.source,
                "content": e.content,
                "tags": e.tags,
            }
            for e in reversed(events)
        ]

    def close(self):
        self._conn.close()


def _extract_tags(content: str) -> list[str]:
    words = re.findall(r"\b[a-zA-Z]{4,}\b", content.lower())
    stopwords = {
        "this", "that", "with", "from", "have", "been", "will", "were",
        "they", "them", "then", "than", "when", "what", "which", "there",
        "their", "would", "could", "should", "about", "some", "more",
        "also", "just", "like", "into", "over", "after", "before",
        "test", "file",  # too generic for a dev env — we'll revisit this
    }
    seen = set()
    tags = []
    for w in words:
        if w not in stopwords and w not in seen:
            seen.add(w)
            tags.append(w)
    return tags[:8]
