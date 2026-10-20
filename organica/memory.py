"""
Memory Service — Version 0.

This is all that exists right now.

Store events. Retrieve them. That's it.
We will look at what actually accumulates before deciding what to build next.
"""

import re
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from collections import Counter


DB_PATH = Path(__file__).parent.parent / "memory.db"


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
        self._init_schema()

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
        self._conn.commit()
        return event

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
        rows = self._conn.execute("SELECT tags FROM events").fetchall()
        counter: Counter = Counter()
        for (tags_str,) in rows:
            for tag in (tags_str or "").split(","):
                if tag:
                    counter[tag] += 1
        return counter

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
