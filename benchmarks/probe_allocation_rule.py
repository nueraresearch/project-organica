"""Allocation-rule probe: is the binding constraint the BUDGET or the ALLOCATION?

The capacity sweep showed that the engine's asserted-structure coverage of the
world's edges is a monotone dose-response in `MAX_PREDICTIONS`, and that a
budget of 80 is not enough (coverage 0.13-0.18) while removing the cap is
(coverage 0.99-1.00).  That leaves two candidate fixes open:

  (A) a bigger global budget  — "raise MAX_PREDICTIONS"
  (B) a different allocation rule — "keep the top-K per SOURCE instead of the
      top-K globally"

(B) is attractive because it needs no additional budget to begin with: the
engine already keeps 20 candidates, it just keeps the 20 highest-count rows
across the whole table, which are dominated by internal-vocabulary edges
(`type -> olive`, `generation -> olive`, ...) rather than by the law-bearing
cross-cell edges.

This probe measures both curves on the same `precedes` table, from the same
engine run, so the comparison is paired:

  global curve   — top-K by count across the whole table, K in
                   (5, 10, 20, 40, 80, 160, 320)
  per-source curve — top-K per source tag, K in (1, 2, 3, 5, 10)

and, for each point, the number of edges RETAINED as well as the coverage of
the world's edges, so a fix that merely spends more budget is visible as such.

No engine modification.  Scratch DBs only.  The frozen engine is untouched.

Usage:
    python benchmarks/probe_allocation_rule.py
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
GLOBAL_KS = (5, 10, 20, 40, 80, 160, 320)
PER_SOURCE_KS = (1, 2, 3, 5, 10)
THRESHOLD = 0.50


def _global_top_k(prec_rows, k):
    """The engine's own rule: top-K by count across the whole table."""
    rows = sorted(prec_rows, key=lambda r: -r[2])
    return {(s, d) for s, d, _c in rows[:k]}


def _per_source_top_k(prec_rows, k):
    """Top-K per source, each source sorted by count."""
    per_src: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for s, d, c in prec_rows:
        per_src[s].append((d, c))
    edges = set()
    for src, items in per_src.items():
        items.sort(key=lambda x: -x[1])
        for dst, _c in items[:k]:
            edges.add((src, dst))
    return edges


def _measure(edges, world_edges):
    covered = edges & world_edges
    cov = len(covered) / len(world_edges) if world_edges else 0.0
    prec = len(covered) / len(edges) if edges else 0.0
    return {
        "edges_retained": len(edges),
        "covered": len(covered),
        "coverage": round(cov, 4),
        "precision": round(prec, 4),
        "passes_gate13": cov >= THRESHOLD,
    }


def run_seed(seed: int) -> dict:
    world = generate_compositional_world(seed=seed, cycles=110)
    events_text = world["events"]
    trainable = world["trainable"]

    acq_lo, acq_hi = PHASE_ACQUISITION
    acq_lo_e = acq_lo * EVENTS_PER_CYCLE
    acq_hi_e = acq_hi * EVENTS_PER_CYCLE

    db_path = temp_db(f"allocrule_{seed}")
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

        prec_rows = mem._conn.execute(
            "SELECT tag_from, tag_to, count FROM precedes"
        ).fetchall()

        world_edges = _world_compositional_edges(world)
        sources = {s for s, _d, _c in prec_rows}

        global_curve = {
            str(k): _measure(_global_top_k(prec_rows, k), world_edges)
            for k in GLOBAL_KS
        }
        per_source_curve = {
            str(k): _measure(_per_source_top_k(prec_rows, k), world_edges)
            for k in PER_SOURCE_KS
        }
        return {
            "seed": seed,
            "precedes_rows": len(prec_rows),
            "distinct_sources": len(sources),
            "world_edges": len(world_edges),
            "global_top_k": global_curve,
            "per_source_top_k": per_source_curve,
        }
    finally:
        mem.close()
        try:
            db_path.unlink(missing_ok=True)
        except Exception:
            pass


def main():
    print(f"Allocation-rule probe  |  seeds={SEEDS}  threshold={THRESHOLD}")
    print("=" * 78)
    results = []
    for seed in SEEDS:
        r = run_seed(seed)
        results.append(r)
        print(f"\nSeed {seed}: precedes rows={r['precedes_rows']} "
              f"distinct sources={r['distinct_sources']} "
              f"world edges={r['world_edges']}")
        print(f"  {'rule':<16} {'K':>4} {'retained':>9} {'covered':>8} "
              f"{'coverage':>9} {'precision':>10}  gate13")
        for k, v in r["global_top_k"].items():
            print(f"  {'global':<16} {k:>4} {v['edges_retained']:>9} "
                  f"{v['covered']:>8} {v['coverage']:>9.4f} "
                  f"{v['precision']:>10.4f}  "
                  f"{'PASS' if v['passes_gate13'] else 'FAIL'}")
        for k, v in r["per_source_top_k"].items():
            print(f"  {'per-source':<16} {k:>4} {v['edges_retained']:>9} "
                  f"{v['covered']:>8} {v['coverage']:>9.4f} "
                  f"{v['precision']:>10.4f}  "
                  f"{'PASS' if v['passes_gate13'] else 'FAIL'}")
        print(flush=True)

    out = REPO / "docs" / "gate13_allocation_rule.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
