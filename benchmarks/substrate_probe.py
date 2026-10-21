"""
benchmarks/substrate_probe.py
------------------------------------------------------------------
Phase G diagnostic: read the REAL substrate and measure what it costs.

The daemon's own log cannot answer the endurance question because it spans
multiple daemon runs and only the newest harness records `duration_ms`.
The database, however, is the actual substrate: it holds every experience
event, every persisted sleep candidate, and the co-occurrence / temporal
graphs.

This probe measures, against the live `memory.db`:

  * table row counts and the experience/sleep split
  * SQLite page accounting -> is the file growing because live data grows,
    or because deleted rows are never reclaimed?
  * the cost of each per-cycle substrate read, separated out, so the O(n)
    behaviour can be attributed to a specific query rather than guessed at
  * orphan accounting: are pruned candidates actually deleted?

Usage:
    python benchmarks/substrate_probe.py
    python benchmarks/substrate_probe.py --db memory.db
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def timeit(fn, repeats=1):
    t0 = time.perf_counter()
    result = None
    for _ in range(repeats):
        result = fn()
    return (time.perf_counter() - t0) / repeats, result


def probe(db_path: Path) -> dict:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    out: dict = {"db_path": str(db_path), "size_bytes": db_path.stat().st_size}

    # ---- table counts -------------------------------------------------
    counts = {}
    for table in ("events", "cooccurrences", "precedes"):
        try:
            counts[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        except sqlite3.Error as exc:
            counts[table] = f"error: {exc}"
    out["row_counts"] = counts

    # ---- event split --------------------------------------------------
    try:
        out["event_split"] = dict(
            conn.execute("SELECT event_type, COUNT(*) FROM events GROUP BY event_type").fetchall()
        )
    except sqlite3.Error as exc:
        out["event_split"] = f"error: {exc}"

    # ---- page accounting: is the file reclaimable? --------------------
    try:
        page_count = conn.execute("PRAGMA page_count").fetchone()[0]
        freelist = conn.execute("PRAGMA freelist_count").fetchone()[0]
        page_size = conn.execute("PRAGMA page_size").fetchone()[0]
        out["page_accounting"] = {
            "page_size": page_size,
            "page_count": page_count,
            "freelist_count": freelist,
            "live_bytes": (page_count - freelist) * page_size,
            "free_bytes": freelist * page_size,
            "free_pct_of_file": round(100 * freelist / page_count, 2) if page_count else 0.0,
        }
    except sqlite3.Error as exc:
        out["page_accounting"] = f"error: {exc}"

    # ---- per-cycle substrate read costs --------------------------------
    # These mirror the calls SleepService.run() makes every cycle.
    timings = {}

    def q_tagfreq():
        return conn.execute("SELECT tags FROM events").fetchall()

    def q_recent_sleep():
        return conn.execute(
            "SELECT * FROM events WHERE event_type='sleep' ORDER BY time DESC LIMIT 4000"
        ).fetchall()

    def q_recent_all():
        return conn.execute(
            "SELECT * FROM events ORDER BY time DESC LIMIT 4000"
        ).fetchall()

    def q_cooc():
        return conn.execute(
            "SELECT tag_a, tag_b, count FROM cooccurrences WHERE count >= 2 ORDER BY count DESC"
        ).fetchall()

    def q_temporal():
        return conn.execute(
            "SELECT tag_from, tag_to, count FROM precedes WHERE count >= 2 ORDER BY count DESC"
        ).fetchall()

    for name, fn in (
        ("tag_frequencies__FULL_TABLE_SCAN", q_tagfreq),
        ("recent_4000_sleep", q_recent_sleep),
        ("recent_4000_any", q_recent_all),
        ("load_cooccurrences", q_cooc),
        ("load_temporal", q_temporal),
    ):
        secs, _ = timeit(fn)
        timings[name] = round(secs * 1000, 2)

    out["read_cost_ms"] = timings
    out["total_per_cycle_read_ms"] = round(sum(timings.values()), 2)

    # ---- orphan accounting: are pruned candidates deleted? -------------
    # Sleep candidates are stored as JSON payloads in events.content.
    # If pruning removes them from the active set but never deletes the
    # underlying rows, the table grows without bound.
    try:
        total_sleep = out["event_split"].get("sleep", 0)
        rows = conn.execute(
            "SELECT content FROM events WHERE event_type='sleep' AND source LIKE 'sleep:%' LIMIT 20000"
        ).fetchall()
        types: dict[str, int] = {}
        for (content,) in rows:
            try:
                obj = json.loads(content)
                t = obj.get("type", "?")
            except (json.JSONDecodeError, TypeError):
                t = "<non-json>"
            types[t] = types.get(t, 0) + 1
        out["candidate_type_sample"] = types
        out["candidate_rows_sampled"] = len(rows)
        out["total_sleep_rows"] = total_sleep
    except sqlite3.Error as exc:
        out["candidate_type_sample"] = f"error: {exc}"

    # ---- index inventory ----------------------------------------------
    try:
        out["indexes"] = [
            {"name": r[0], "table": r[1], "sql": r[2]}
            for r in conn.execute(
                "SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index'"
            ).fetchall()
        ]
    except sqlite3.Error as exc:
        out["indexes"] = f"error: {exc}"

    conn.close()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Probe the live Organica substrate.")
    ap.add_argument("--db", default="memory.db")
    ap.add_argument("--out", default="docs/substrate_probe.json")
    args = ap.parse_args()

    db_path = Path(__file__).parent.parent / args.db
    if not db_path.exists():
        print(f"ERROR: {db_path} not found")
        return 1

    result = probe(db_path)

    print("=" * 74)
    print("PROJECT ORGANICA -- LIVE SUBSTRATE PROBE")
    print("=" * 74)
    print(f"  db                : {result['db_path']}")
    print(f"  size              : {result['size_bytes']/1e6:.1f} MB")
    print(f"  row counts        : {result['row_counts']}")
    print(f"  event split       : {result['event_split']}")

    pa = result.get("page_accounting")
    if isinstance(pa, dict):
        print(f"  live bytes        : {pa['live_bytes']/1e6:.1f} MB")
        print(f"  free (unreclaimed): {pa['free_bytes']/1e6:.1f} MB  "
              f"({pa['free_pct_of_file']}% of file)")

    print("\n  per-cycle substrate read costs (ms):")
    for k, v in result["read_cost_ms"].items():
        print(f"    {k:<38} {v:>10.2f}")
    print(f"    {'TOTAL per cycle':<38} {result['total_per_cycle_read_ms']:>10.2f}")

    if isinstance(result.get("candidate_type_sample"), dict):
        print(f"\n  candidate rows by type (sample of "
              f"{result['candidate_rows_sampled']} of {result.get('total_sleep_rows')} sleep rows):")
        for t, n in sorted(result["candidate_type_sample"].items(), key=lambda kv: -kv[1]):
            print(f"    {t:<28} {n:>8}")

    out = Path(__file__).parent.parent / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))
    print(f"\n  Full report written to: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
