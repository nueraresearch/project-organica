"""Relation-separation probe: can world relations be separated from
engine-generated relations WITHOUT modifying the frozen engine?

The question
------------
The acquisition-gate failure is not that the world's structure never entered
the organism.  It did: the `precedes` table holds the world's edges at
coverage 0.97-1.00.  The failure is that the world's edges do not survive
Layer-1 selection, because the table's top ranks are occupied by
`internal -> world` rows -- the engine's own sleep vocabulary pointing at
world tags.

The mechanism (already disclosed as D2 in docs/AUDIT-TRACE-SPEC.md)
--------------------------------------------------------------------
`organica/memory.py::store()` gates the *trigger*:

    if event_type != "sleep":
        self._record_cooccurrences(event.tags)
        self._record_temporal_edges(event.tags)

but `_record_temporal_edges` builds its window with an UNFILTERED query:

    SELECT tags FROM events ORDER BY time DESC LIMIT ?

so a world event's edges can take their `tag_from` from a SLEEP row that
happens to precede it.  The graph therefore mixes two relation families:
world co-occurrence / world transition, and the engine's own descriptive
vocabulary.

What this probe measures
-------------------------
It rebuilds the `precedes` table offline from the `events` table and asks
whether a provenance separation -- one that uses only `event_type`, which the
engine already records, and NO privileged knowledge of the world's tags --
recovers the world's edges at the FROZEN budget of 20.

Three tables, all rebuilt from the same engine run:

  raw          the engine's actual `precedes` table
  filtered_q   the same rule with the lookback window restricted to WORLD
               events (`event_type != 'sleep'`), LIMIT 3 -- the faithful
               one-line V2 fix
  filtered_q4  the same, but LIMIT 4 over world events -- the variant that
               restores the lookback DEPTH the constant asks for (the current
               rule's window includes the current event, so its effective
               depth is 2)

and one more, for attribution:

  self_only    the edges that the filtered rule removes -- i.e. the ones
               whose `tag_from` came from a sleep row

The probe carries its own proof-of-firing: it rebuilds the raw table from the
engine's own rule and requires it to MATCH the engine's table exactly.  If
the reconstruction does not reproduce the engine, the probe fails rather than
reporting a number it cannot stand behind.

No engine modification.  Scratch DBs only.  The frozen engine is untouched.

Usage:
    python benchmarks/probe_relation_separation.py
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.memory import MemoryService  # noqa: E402
from organica.paths import temp_db  # noqa: E402
from organica.sleep import SleepService  # noqa: E402
from benchmarks.acquisition_harness import (  # noqa: E402
    EVENTS_PER_CYCLE,
    PHASE_ACQUISITION,
    _world_compositional_edges,
    generate_compositional_world,
)

SEEDS = [20261101, 20261102, 20261103]
ENGINE_CAP = 20          # MAX_PREDICTIONS, the frozen budget
THRESHOLD = 0.50         # the Gate 13 sufficiency threshold
LOOKBACK = 3             # the engine's own lookback constant


# ---------------------------------------------------------------------------
# Offline reconstruction of the engine's `precedes` table
# ---------------------------------------------------------------------------

def _tags_of(row) -> list[str]:
    """The engine stores a comma-joined tag list; empty string means no tags."""
    tags_str = row["tags"] or ""
    return [t for t in tags_str.split(",") if t]


def rebuild_precedes(events, *, world_only_window: bool, limit: int) -> dict:
    """Rebuild the `precedes` table from the events table.

    Faithful to `MemoryService._record_temporal_edges`: for each event that
    TRIGGERS recording (any non-sleep event), take the `limit` most recent
    rows by time -- INCLUDING the current row, because `store()` inserts the
    event before it calls the recorder -- and connect every `tag_from` in
    those rows to every `tag_to` of the current event, skipping `tag_from ==
    tag_to`.

    With `world_only_window=True` the window is restricted to world events
    (`event_type != 'sleep'`).  That is the separation under test.
    """
    counts: dict[tuple[str, str], int] = defaultdict(int)
    for i, ev in enumerate(events):
        if ev["event_type"] == "sleep":
            continue          # sleep rows never TRIGGER recording
        window = events[max(0, i - limit + 1):i + 1]
        if world_only_window:
            window = [e for e in window if e["event_type"] != "sleep"]
        new_tags = _tags_of(ev)
        if not new_tags:
            continue
        for prior in window:
            for tag_from in _tags_of(prior):
                for tag_to in new_tags:
                    if tag_from != tag_to:
                        counts[(tag_from, tag_to)] += 1
    return dict(counts)


def engine_precedes(mem) -> dict[tuple[str, str], int]:
    """The engine's actual table, as a comparable dict."""
    rows = mem._conn.execute(
        "SELECT tag_from, tag_to, count FROM precedes"
    ).fetchall()
    return {(a, b): c for a, b, c in rows}


# ---------------------------------------------------------------------------
# Selection and scoring
# ---------------------------------------------------------------------------

def select_global_top_k(table: dict[tuple[str, str], int], k: int) -> set:
    """The engine's own Layer-1 rule: global top-K by count.

    `_build_predictions` sorts candidates by raw temporal count and truncates
    at MAX_PREDICTIONS, across all sources.
    """
    ordered = sorted(table.items(), key=lambda kv: -kv[1])
    return {edge for edge, _c in ordered[:k]}


def measure(edges: set, world_edges: set, tag_to_cell: dict) -> dict:
    """Score a selected edge set against the world's edges.

    THREE categories, not two.  An edge with an endpoint that is NOT a world
    tag is neither intra-cell nor inter-cell: it is the organism's own
    vocabulary reaching into the world relation table.  Collapsing it into
    "inter" -- because the internal tag has no cell, so `None != cell` --
    mislabels exactly the rows the separation exists to expose, and makes a
    selection of engine vocabulary look like a selection of cross-cell world
    relations.
    """
    covered = edges & world_edges
    cov = len(covered) / len(world_edges) if world_edges else 0.0
    prec = len(covered) / len(edges) if edges else 0.0
    intra = inter = mixed = 0
    for a, b in edges:
        ca, cb = tag_to_cell.get(a), tag_to_cell.get(b)
        if ca is None or cb is None:
            mixed += 1
        elif ca == cb:
            intra += 1
        else:
            inter += 1
    return {
        "edges": len(edges),
        "covered": len(covered),
        "coverage": round(cov, 4),
        "precision": round(prec, 4),
        "intra_cell": intra,
        "inter_cell": inter,
        "mixed_vocabulary": mixed,
        "passes_gate13": cov >= THRESHOLD,
    }


def first_world_edge_rank(table: dict[tuple[str, str], int], world_edges: set) -> int | None:
    ordered = sorted(table.items(), key=lambda kv: -kv[1])
    for rank, (edge, _c) in enumerate(ordered, 1):
        if edge in world_edges:
            return rank
    return None


# ---------------------------------------------------------------------------
# One seed
# ---------------------------------------------------------------------------

def run_seed(seed: int) -> dict:
    world = generate_compositional_world(seed=seed, cycles=110)
    events_text = world["events"]
    trainable = world["trainable"]

    acq_lo, acq_hi = PHASE_ACQUISITION
    acq_lo_e = acq_lo * EVENTS_PER_CYCLE
    acq_hi_e = acq_hi * EVENTS_PER_CYCLE

    db_path = temp_db(f"relsep_{seed}")
    mem = MemoryService(str(db_path))
    try:
        svc = SleepService(mem)
        for i, (text, train_flag) in enumerate(zip(events_text, trainable)):
            in_acq = acq_lo_e <= i < acq_hi_e
            if in_acq and not train_flag:
                continue
            source = "env_acq" if in_acq else "env"
            mem.store(text, event_type="observe", source=source)
            if (i + 1) % EVENTS_PER_CYCLE == 0:
                svc.run_sleep_cycle()

        rows = mem._conn.execute(
            "SELECT id, time, source, event_type, content, tags FROM events"
        ).fetchall()
        events = [
            {"id": r[0], "time": r[1], "source": r[2], "event_type": r[3],
             "content": r[4], "tags": r[5]}
            for r in rows
        ]

        engine_table = engine_precedes(mem)
        rebuilt_raw = rebuild_precedes(events, world_only_window=False, limit=LOOKBACK)

        # --- the probe's own proof-of-firing -------------------------------
        # The reconstruction must reproduce the engine's table EXACTLY.  If it
        # does not, every number below would be built on a model of the engine
        # rather than on the engine.
        raw_matches = rebuilt_raw == engine_table
        if not raw_matches:
            missing = set(engine_table) - set(rebuilt_raw)
            extra = set(rebuilt_raw) - set(engine_table)
            differing = {
                k: (engine_table[k], rebuilt_raw[k])
                for k in set(engine_table) & set(rebuilt_raw)
                if engine_table[k] != rebuilt_raw[k]
            }
            raise AssertionError(
                "RECONSTRUCTION DOES NOT MATCH THE ENGINE -- the probe refuses to "
                f"report numbers it cannot stand behind. "
                f"missing={len(missing)} extra={len(extra)} "
                f"count_mismatch={len(differing)} "
                f"sample_missing={sorted(missing)[:5]} "
                f"sample_extra={sorted(extra)[:5]}"
            )

        world_edges = _world_compositional_edges(world)
        tag_to_cell = world["tag_to_cell"]

        raw_sel = select_global_top_k(engine_table, ENGINE_CAP)
        filt3 = rebuild_precedes(events, world_only_window=True, limit=LOOKBACK)
        filt4 = rebuild_precedes(events, world_only_window=True, limit=LOOKBACK + 1)
        filt3_sel = select_global_top_k(filt3, ENGINE_CAP)
        filt4_sel = select_global_top_k(filt4, ENGINE_CAP)

        # Which raw rows were removed by the separation?
        removed = {e: c for e, c in engine_table.items() if e not in filt3}

        sleep_tags = set()
        for e in events:
            if e["event_type"] == "sleep":
                sleep_tags.update(_tags_of(e))

        return {
            "seed": seed,
            "reconstruction_matches_engine": raw_matches,
            "events_total": len(events),
            "events_world": sum(1 for e in events if e["event_type"] != "sleep"),
            "events_sleep": sum(1 for e in events if e["event_type"] == "sleep"),
            "engine_table_rows": len(engine_table),
            "rows_removed_by_separation": len(removed),
            "sleep_vocabulary_terms": len(sleep_tags),
            "world_edges": len(world_edges),
            "raw": {
                "table_rows": len(engine_table),
                "selected": measure(raw_sel, world_edges, tag_to_cell),
                "first_world_edge_rank": first_world_edge_rank(engine_table, world_edges),
            },
            "filtered_limit3": {
                "table_rows": len(filt3),
                "selected": measure(filt3_sel, world_edges, tag_to_cell),
                "first_world_edge_rank": first_world_edge_rank(filt3, world_edges),
            },
            "filtered_limit4": {
                "table_rows": len(filt4),
                "selected": measure(filt4_sel, world_edges, tag_to_cell),
                "first_world_edge_rank": first_world_edge_rank(filt4, world_edges),
            },
            "self_only_removed": {
                "table_rows": len(removed),
                "share_of_engine_rows": round(len(removed) / len(engine_table), 4)
                if engine_table else 0.0,
                "share_with_sleep_source": round(
                    sum(1 for a, _b in removed if a in sleep_tags) / len(removed), 4
                ) if removed else 0.0,
            },
        }
    finally:
        mem.close()
        try:
            db_path.unlink(missing_ok=True)
        except Exception:
            pass


def main():
    print(f"Relation-separation probe  |  seeds={SEEDS}  "
          f"engine cap={ENGINE_CAP}  threshold={THRESHOLD}")
    print("=" * 100)
    results = []
    for seed in SEEDS:
        r = run_seed(seed)
        results.append(r)
        print(f"\nSeed {seed}")
        print(f"  events: {r['events_world']} world + {r['events_sleep']} sleep"
              f"   |   engine precedes rows: {r['engine_table_rows']}"
              f"   |   reconstruction matches engine: "
              f"{r['reconstruction_matches_engine']}")
        print(f"  world edges: {r['world_edges']}   |   rows removed by the "
              f"separation: {r['rows_removed_by_separation']} "
              f"({r['self_only_removed']['share_of_engine_rows'] * 100:.1f}% of the table; "
              f"{r['self_only_removed']['share_with_sleep_source'] * 100:.1f}% of those have a "
              f"sleep-sourced tag_from)")
        print(f"  {'table':<18} {'rows':>6} {'sel':>5} {'cov':>8} {'prec':>8} "
              f"{'intra':>6} {'inter':>6} {'1st world edge':>15}")
        for key, label in (("raw", "raw (engine)"),
                           ("filtered_limit3", "filtered LIMIT 3"),
                           ("filtered_limit4", "filtered LIMIT 4")):
            blk = r[key]
            s = blk["selected"]
            rank = blk["first_world_edge_rank"]
            print(f"  {label:<18} {blk['table_rows']:>6} {s['edges']:>5} "
                  f"{s['coverage']:>8.4f} {s['precision']:>8.4f} "
                  f"{s['intra_cell']:>6} {s['inter_cell']:>6} "
                  f"{(rank if rank is not None else 'none'):>15}")
        print(flush=True)

    out = REPO / "docs" / "gate13_relation_separation.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
