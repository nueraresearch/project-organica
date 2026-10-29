"""Why does the raw table's normalised ranking still prefer engine vocabulary
even when a self-inclusive frequency scope is used?

The ranking probe found: on the RAW table with the engine's world-scoped
frequency, `ratio`/`cosine`/`pmi` each select 20 MIXED edges (an engine word
pointing at a world tag) with coverage 0.0000, on every seed.  The stated
mechanism is that `tag_counts` is world-scoped, so the engine's own words have
no frequency entry, `freqs.get(tag_from, 1)` returns 1, and their ratio
equals their raw count -- the maximum possible for that count.

But with a SELF-INCLUSIVE frequency scope the raw table STILL selects mixed
edges (17-20).  The stated mechanism does not explain that, and this project
does not report a mechanism it has not measured.

This diagnostic prints, for one seed:
  - the mixed edges the raw table's `ratio` ranking selects
  - for each: its source tag, whether that source is in the world vocabulary,
    whether it is in the self-frequency map, its raw count, its world
    frequency, its self frequency, and the resulting ratio
  - the best world edges by the same criterion, for comparison

so the comparison is explicit: what does the ranking prefer, and on what
numbers?

Usage:
    python benchmarks/probe_ranking_mechanism.py
"""
from __future__ import annotations

import json
import sys
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
from benchmarks.probe_relation_separation import (  # noqa: E402
    LOOKBACK,
    engine_precedes,
    rebuild_precedes,
)

SEED = 20261101
ENGINE_CAP = 20


def main():
    world = generate_compositional_world(seed=SEED, cycles=110)
    events_text = world["events"]
    trainable = world["trainable"]
    acq_lo, acq_hi = PHASE_ACQUISITION
    acq_lo_e = acq_lo * EVENTS_PER_CYCLE
    acq_hi_e = acq_hi * EVENTS_PER_CYCLE

    db_path = temp_db(f"rankmech_{SEED}")
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
            "SELECT id, time, source, event_type, content, tags FROM events").fetchall()
        events = [{"id": r[0], "time": r[1], "source": r[2], "event_type": r[3],
                   "content": r[4], "tags": r[5]} for r in rows]

        world_freqs = {t: c for t, c in mem._conn.execute(
            "SELECT tag, count FROM tag_counts").fetchall()}
        self_freqs: dict[str, int] = {}
        for ev in events:
            if ev["event_type"] == "sleep":
                for t in (ev["tags"] or "").split(","):
                    if t:
                        self_freqs[t] = self_freqs.get(t, 0) + 1

        table = engine_precedes(mem)
        rebuilt = rebuild_precedes(events, world_only_window=False, limit=LOOKBACK)
        if rebuilt != table:
            raise AssertionError("reconstruction mismatch")

        world_edges = _world_compositional_edges(world)
        tag_to_cell = world["tag_to_cell"]
        world_tags = set(tag_to_cell)

        def ratio(edge, c, freqs):
            src = edge[0]
            return c / max(freqs.get(src, 1), 1)

        for scope_name, freqs in (("world_freq", world_freqs),
                                  ("world_plus_self_freq",
                                   {**world_freqs,
                                    **{t: world_freqs.get(t, 0) + c
                                       for t, c in self_freqs.items()}})):
            ordered = sorted(table.items(), key=lambda kv: -ratio(kv[0], kv[1], freqs))
            sel = ordered[:ENGINE_CAP]
            mixed = [(e, c) for e, c in sel
                     if e[0] not in world_tags or e[1] not in world_tags]
            world_sel = [(e, c) for e, c in sel if e in world_edges]
            print("=" * 96)
            print(f"scope={scope_name}   seed={SEED}   selected={len(sel)}   "
                  f"mixed={len(mixed)}   world edges selected={len(world_sel)}")
            print("=" * 96)
            print(f"{'src':<14} {'-> dst':<14} {'count':>6} {'w_freq':>7} "
                  f"{'s_freq':>7} {'ratio':>9}  {'src in world?':<13} "
                  f"{'src in self map?':<16} {'is world edge?'}")
            for e, c in sel[:12]:
                s, d = e
                wf = world_freqs.get(s, 0)
                sf = self_freqs.get(s, 0)
                print(f"{s:<14} {d:<14} {c:>6} {wf:>7} {sf:>7} "
                      f"{ratio(e, c, freqs):>9.4f}  {str(s in world_tags):<13} "
                      f"{str(s in self_freqs):<16} {str(e in world_edges)}")
            print()
            # The best world edges by the same criterion, for comparison.
            world_ranked = sorted(
                [(e, c) for e, c in table.items() if e in world_edges],
                key=lambda kv: -ratio(kv[0], kv[1], freqs))
            print("  best world edges by the SAME criterion (not selected):")
            for e, c in world_ranked[:5]:
                s, d = e
                print(f"    {s:<14} {d:<14} {c:>6} {world_freqs.get(s, 0):>7} "
                      f"{self_freqs.get(s, 0):>7} {ratio(e, c, freqs):>9.4f}")
            print()
    finally:
        mem.close()
        try:
            db_path.unlink(missing_ok=True)
        except Exception:
            pass


if __name__ == "__main__":
    main()
