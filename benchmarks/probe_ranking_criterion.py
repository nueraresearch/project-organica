"""Ranking-criterion probe: can the frozen budget of 20 reach the world's
relations if candidates are NOT ranked by raw count?

The question
------------
The relation-separation probe found that removing every engine-generated row
from the relation table is real, oracle-free, and NOT sufficient: at the
frozen budget of 20 the world's edges still do not make the cut, because
intra-cell co-occurrence pairs out-count the law's transitions.  The
remaining requirement was "a ranking that is not raw frequency" — and the
causal account had called it the hard one, with no precedent in the engine.

But there IS a precedent, and it is in the engine's own code.
``SleepService._build_predictions`` (``organica/sleep.py:1139-1160``):

    ratio = count / max(source_freq, 1)
    ...
    strength=min(1.0, ratio),
    evidence={
        "temporal_count": count,
        "source_frequency": source_freq,
        "target_frequency": freqs.get(tag_to, 0),
        "ratio": round(ratio, 3),
    },
    ...
    candidates.sort(key=lambda p: p["evidence"]["temporal_count"], reverse=True)

The engine computes a frequency-normalised criterion, stores it in every
candidate's evidence, uses it for SURVIVAL (via ``stable_prior``) -- and then
sorts by RAW COUNT for ADMISSION.  The normalised quantity is already there.

This probe asks whether any of those already-computed quantities, used as the
admission ranking, recovers the world's edges at the frozen budget of 20.

The rankings tested
-------------------
All five use ONLY fields the engine already stores on every candidate, so
each is a ZERO-NEW-INFORMATION selection rule:

    count              the engine's current ranking (baseline)
    ratio              count / source_freq        -- the engine's own `strength`
    target_ratio       count / target_freq        -- engine stores target_freq
    cosine             count / sqrt(src*dst)      -- from the same two fields
    pmi                count / (src*dst / N)      -- pointwise mutual info

The grid
--------
Each ranking is applied to TWO tables:

    raw        the engine's own relation table (engine-generated rows included)
    filtered   the same table with the lookback window restricted to world
               events -- the oracle-free provenance separation

so the probe separates the two requirements instead of confounding them:
a ranking that works only on the filtered table needs BOTH changes; one that
works on the raw table needs only the ranking.

Proof-of-firing
---------------
As in the relation-separation probe, the offline reconstruction of the raw
table must MATCH the engine's table exactly, or the probe refuses to report.

No engine modification.  Scratch DBs only.  The frozen engine is untouched.

Usage:
    python benchmarks/probe_ranking_criterion.py
"""
from __future__ import annotations

import json
import math
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
    measure,
    rebuild_precedes,
)

SEEDS = [20261101, 20261102, 20261103]
ENGINE_CAP = 20
THRESHOLD = 0.50


# ---------------------------------------------------------------------------
# Rankings -- every one uses only fields the engine already stores
# ---------------------------------------------------------------------------

def _rankings(table: dict, freqs: dict) -> dict:
    """Return {name: sorted edges, best first} for each candidate criterion."""
    total = sum(table.values()) or 1

    def by(key):
        return sorted(table.items(), key=lambda kv: -key(kv[0], kv[1]))

    def src_freq(edge, _c):
        return max(freqs.get(edge[0], 1), 1)

    def dst_freq(edge, _c):
        return max(freqs.get(edge[1], 1), 1)

    return {
        "count": by(lambda e, c: c),
        "ratio": by(lambda e, c: c / src_freq(e, c)),
        "target_ratio": by(lambda e, c: c / dst_freq(e, c)),
        "cosine": by(lambda e, c: c / math.sqrt(src_freq(e, c) * dst_freq(e, c))),
        "pmi": by(lambda e, c: c / ((src_freq(e, c) * dst_freq(e, c)) / total)),
    }


def run_seed(seed: int) -> dict:
    world = generate_compositional_world(seed=seed, cycles=110)
    events_text = world["events"]
    trainable = world["trainable"]

    acq_lo, acq_hi = PHASE_ACQUISITION
    acq_lo_e = acq_lo * EVENTS_PER_CYCLE
    acq_hi_e = acq_hi * EVENTS_PER_CYCLE

    db_path = temp_db(f"rankcrit_{seed}")
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
        freqs = {tag: cnt for tag, cnt in mem._conn.execute(
            "SELECT tag, count FROM tag_counts").fetchall()}

        # The engine records NO frequency statistic for its own vocabulary:
        # `_record_tag_counts` is inside the `if event_type != "sleep":` block
        # in `store()`, so `tag_counts` is world-scoped and the engine's own
        # words are absent from it.  The engine nevertheless has those words in
        # the substrate -- every sleep event stores its tags -- so a
        # self-inclusive frequency can be recovered from the events table
        # without touching the engine.
        self_freqs: dict[str, int] = {}
        for ev in events:
            if ev["event_type"] == "sleep":
                for t in (ev["tags"] or "").split(","):
                    if t:
                        self_freqs[t] = self_freqs.get(t, 0) + 1
        freqs_total = dict(freqs)
        for t, c in self_freqs.items():
            freqs_total[t] = freqs_total.get(t, 0) + c

        engine_table = engine_precedes(mem)
        rebuilt = rebuild_precedes(events, world_only_window=False, limit=LOOKBACK)
        if rebuilt != engine_table:
            raise AssertionError(
                "RECONSTRUCTION DOES NOT MATCH THE ENGINE -- the probe refuses to "
                "report numbers it cannot stand behind.")
        filtered = rebuild_precedes(events, world_only_window=True, limit=LOOKBACK)

        world_edges = _world_compositional_edges(world)
        tag_to_cell = world["tag_to_cell"]

        out = {"seed": seed, "reconstruction_matches_engine": True,
               "world_edges": len(world_edges),
               "self_vocabulary_terms": len(self_freqs),
               "self_events": sum(1 for e in events if e["event_type"] == "sleep"),
               "tables": {}}

        for table_name, table in (("raw", engine_table), ("filtered", filtered)):
            per_scope = {}
            for scope_name, scope_freqs in (("world_freq", freqs),
                                            ("world_plus_self_freq", freqs_total)):
                per_ranking = {}
                for name, ordered in _rankings(table, scope_freqs).items():
                    sel = {edge for edge, _c in ordered[:ENGINE_CAP]}
                    per_ranking[name] = measure(sel, world_edges, tag_to_cell)
                per_scope[scope_name] = per_ranking
            out["tables"][table_name] = per_scope

        return out
    finally:
        mem.close()
        try:
            db_path.unlink(missing_ok=True)
        except Exception:
            pass


def main():
    print(f"Ranking-criterion probe  |  seeds={SEEDS}  cap={ENGINE_CAP}  "
          f"threshold={THRESHOLD}")
    print("=" * 104)
    print("All criteria below use ONLY fields the engine already stores on every "
          "candidate.")
    results = []
    for seed in SEEDS:
        r = run_seed(seed)
        results.append(r)
        print(f"\nSeed {seed}   world edges={r['world_edges']}   "
              f"self-vocabulary terms={r['self_vocabulary_terms']}   "
              f"self events={r['self_events']}")
        print(f"  {'table':<10} {'freq scope':<21} {'ranking':<13} {'cov':>8} "
              f"{'prec':>8} {'intra':>6} {'inter':>6} {'mixed':>6}  gate13")
        for table_name in ("raw", "filtered"):
            for scope_name, per_ranking in r["tables"][table_name].items():
                for name, s in per_ranking.items():
                    verdict = "PASS" if s["passes_gate13"] else "FAIL"
                    print(f"  {table_name:<10} {scope_name:<21} {name:<13} "
                          f"{s['coverage']:>8.4f} {s['precision']:>8.4f} "
                          f"{s['intra_cell']:>6} {s['inter_cell']:>6} "
                          f"{s['mixed_vocabulary']:>6}  {verdict}")
        print(flush=True)

    out = REPO / "docs" / "gate13_ranking_criterion.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
