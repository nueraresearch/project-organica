"""Gate 13 preflight for the 1-tag stimulus variant.

Tests whether Organica V1 (frozen, MAX_PREDICTIONS=20) clears Gate 13
(>= 0.50 asserted-structure coverage of world edges) when each event
carries exactly ONE tag instead of two.

The 1-tag world has the same 4-cell, 2-factor latent structure:
  - flip_p with prob 0.65, flip_q with prob 0.35 (regime 0)
  - One tag drawn uniformly from the 4-cell tags per event
  - No within-event co-occurrence signal

Ground truth: 16 tags x 8 successors per tag = 128 world edges (same as 2-tag).

Run:
    python benchmarks/probe_1tag_gate13.py
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.memory import MemoryService          # noqa: E402
from organica.sleep import SleepService            # noqa: E402
from organica.paths import temp_db                 # noqa: E402
from benchmarks.acquisition_compositional import (  # noqa: E402
    TAG_POOL, CELLS, TAGS_PER_CELL, flip_p, flip_q, LAW_R0, cell_name,
    PHASE_ACQUISITION,
)
from benchmarks.acquisition_runner import structure_edges  # noqa: E402

SUFFICIENCY_THRESHOLD = 0.50
SEEDS = [20261100, 20261101, 20261102, 20261103, 20261104, 20261105]
CYCLES_ACQ = 110          # warmup (20) + acquisition (90) = 110 cycles, then sleep
EVENTS_PER_CYCLE = 8


def build_world(seed: int) -> dict:
    """Generate 1-tag events for cycles 0-109 with the same compositional law."""
    rng = random.Random(seed)
    pool = list(TAG_POOL)
    rng.shuffle(pool)
    cell_tags: dict = {c: sorted(pool[i * TAGS_PER_CELL:(i + 1) * TAGS_PER_CELL])
                       for i, c in enumerate(CELLS)}

    # Choose held cell (same RNG call order as generate_compositional_world)
    held = CELLS[rng.randrange(len(CELLS))]
    held_flip_p = flip_p(held)

    events: list[str] = []
    trainable: list[bool] = []
    state = CELLS[rng.randrange(len(CELLS))]
    acq_lo, acq_hi = PHASE_ACQUISITION

    for cycle in range(CYCLES_ACQ):
        law = LAW_R0
        for _ in range(EVENTS_PER_CYCLE):
            kinds = ("flip_p", "flip_q")
            kind = rng.choices(kinds, weights=[law[k] for k in kinds], k=1)[0]
            nxt = flip_p(state) if kind == "flip_p" else flip_q(state)
            tag = rng.choice(cell_tags[nxt])         # 1 tag only
            events.append(tag)
            in_acq = (acq_lo * EVENTS_PER_CYCLE <= len(events) - 1
                      < acq_hi * EVENTS_PER_CYCLE)
            is_withheld = (state == held and nxt == held_flip_p and in_acq)
            trainable.append(not is_withheld)
            state = nxt

    # Ground truth: all (src, dst) pairs where src is in cell c and dst is in
    # a neighbour cell of c (flip_p or flip_q).
    world_edges: set[tuple[str, str]] = set()
    for c in CELLS:
        for succ in (flip_p(c), flip_q(c)):
            for src in cell_tags[c]:
                for dst in cell_tags[succ]:
                    world_edges.add((src, dst))

    return {
        "events": events,
        "trainable": trainable,
        "world_edges": world_edges,
        "cell_tags": {cell_name(c): v for c, v in cell_tags.items()},
        "held_cell": cell_name(held),
        "held_flip_p": cell_name(held_flip_p),
    }


def run_seed(seed: int) -> dict:
    world = build_world(seed)
    events = world["events"]
    trainable = world["trainable"]
    world_edges = world["world_edges"]

    db_path = temp_db(f"probe_1tag_{seed}")
    mem = MemoryService(db_path)
    try:
        svc = SleepService(mem)

        for cycle in range(CYCLES_ACQ):
            start = cycle * EVENTS_PER_CYCLE
            for i in range(start, start + EVENTS_PER_CYCLE):
                if trainable[i]:
                    mem.store(events[i])
            svc.run_sleep_cycle()

        # Read asserted structure edges via the same readout path as the runner
        frozen_cands = svc._load_prior_candidates()
        asserted_rows = structure_edges(frozen_cands)
        struct_edges: set[tuple[str, str]] = {
            (u, v) for u, targets in asserted_rows.items() for v in targets
        }

        covered = struct_edges & world_edges
        cov = len(covered) / len(world_edges) if world_edges else 0.0
        prec = len(covered) / len(struct_edges) if struct_edges else 0.0
        gate13_pass = cov >= SUFFICIENCY_THRESHOLD

        # Also check raw temporal edge coverage (diagnostic, not the gate)
        temporal_e = set((ft, tt) for ft, tt, _cnt in mem.temporal_edges(min_count=1))
        temporal_cov = len(temporal_e & world_edges) / len(world_edges) if world_edges else 0.0

        # Top 20 precedes for diagnostics (column names: tag_from, tag_to, count)
        top_prec = mem._conn.execute(
            "SELECT tag_from, tag_to, count FROM precedes ORDER BY count DESC LIMIT 20"
        ).fetchall()

        return {
            "seed": seed,
            "n_struct_edges": len(struct_edges),
            "n_world_edges": len(world_edges),
            "n_covered": len(covered),
            "coverage": round(cov, 4),
            "precision": round(prec, 4),
            "temporal_coverage": round(temporal_cov, 4),
            "gate13_pass": gate13_pass,
            "top_precedes": [(r[0], r[1], r[2]) for r in top_prec],
            "held_cell": world["held_cell"],
            "held_flip_p": world["held_flip_p"],
        }
    finally:
        mem.close()
        try:
            db_path.unlink(missing_ok=True)
        except Exception:
            pass


def main():
    print(f"1-tag Gate 13 preflight  (threshold={SUFFICIENCY_THRESHOLD})")
    print(f"Seeds: {SEEDS}")
    print("=" * 72)

    results = []
    for seed in SEEDS:
        r = run_seed(seed)
        results.append(r)
        status = "PASS" if r["gate13_pass"] else "FAIL"
        print(f"\nSeed {seed}  [{status}]")
        print(f"  held={r['held_cell']} -> {r['held_flip_p']}")
        print(f"  struct_edges : {r['n_struct_edges']}")
        print(f"  world edges  : {r['n_world_edges']}")
        print(f"  covered      : {r['n_covered']}  (coverage={r['coverage']:.4f}, precision={r['precision']:.4f})")
        print(f"  temporal_cov : {r['temporal_coverage']:.4f}")
        print("  top precedes (src -> dst, count):")
        for rank, (src, dst, cnt) in enumerate(r["top_precedes"][:10], 1):
            print(f"    {rank:2d}. {src} -> {dst}  ({cnt})")

    passes = sum(1 for r in results if r["gate13_pass"])
    print("\n" + "=" * 72)
    print(f"Gate 13: {passes}/{len(results)} seeds pass")
    if passes == len(results):
        print("-> ALL PASS: 1-tag stimulus clears the acquisition gate.")
    elif passes > 0:
        print("-> PARTIAL: some seeds pass.")
    else:
        print("-> ALL FAIL: 1-tag stimulus does NOT clear Gate 13 at frozen MAX_PREDICTIONS=20.")


if __name__ == "__main__":
    main()
