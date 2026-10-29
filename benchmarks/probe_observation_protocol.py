"""Observation-protocol probe: world-tags-only filtered readout.

Tests whether Gate 13 passes when the precedes table is read through a
world-tag filter (tag_from AND tag_to must both be world tags) rather than
the raw unfiltered ranking the engine uses.

No engine modification. Same frozen V1. Same data. Different observation layer.

Runs both the 1-tag and 2-tag worlds across seeds 20261100-20261105.

For each world/seed:
  (A) Raw:     use precedes as-is, top-20 per source  (engine's actual view)
  (B) Filtered: filter to world-tag pairs only, then top-K per source

The filtered readout directly answers:
  "Is the contamination happening only in the way we read reality?"

If (B) passes Gate 13 and (A) fails -> World A+: readout contamination only.
If (B) also fails -> World B+: structural problem even after cleaning.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.memory import MemoryService       # noqa: E402
from organica.sleep import SleepService         # noqa: E402
from organica.paths import temp_db              # noqa: E402
from benchmarks.acquisition_compositional import (  # noqa: E402
    TAG_POOL, CELLS, TAGS_PER_CELL, flip_p, flip_q, LAW_R0, cell_name,
    PHASE_ACQUISITION,
)

WORLD_TAGS = set(TAG_POOL)
SUFFICIENCY_THRESHOLD = 0.50
SEEDS = [20261100, 20261101, 20261102, 20261103, 20261104, 20261105]
CYCLES_ACQ = 110
EVENTS_PER_CYCLE = 8

# How many top-K per source to allow in the filtered readout.
# For the 2-tag case, world edges sit at ranks 4-7; K=20 matches engine default.
# For the 1-tag case, with only 8 valid successors, K=10 is generous.
K_FILTERED = 20
MAX_PREDICTIONS = 20  # engine's actual cap (for raw readout)


# ---------------------------------------------------------------------------
# World builders
# ---------------------------------------------------------------------------

def _generate_events(seed: int, tags_per_event: int):
    """Generate (events, trainable, world_edges, cell_tags, held, held_flip_p)
    matching the exact RNG call order of generate_compositional_world."""
    rng = random.Random(seed)
    pool = list(TAG_POOL)
    rng.shuffle(pool)
    ct = {c: sorted(pool[i * TAGS_PER_CELL:(i + 1) * TAGS_PER_CELL])
          for i, c in enumerate(CELLS)}
    held = CELLS[rng.randrange(len(CELLS))]
    held_flip_p = flip_p(held)
    state = CELLS[rng.randrange(len(CELLS))]

    acq_lo, acq_hi = PHASE_ACQUISITION
    events, trainable = [], []

    for cycle in range(CYCLES_ACQ):
        for _ in range(EVENTS_PER_CYCLE):
            kind = rng.choices(("flip_p", "flip_q"),
                               weights=[LAW_R0[k] for k in ("flip_p", "flip_q")],
                               k=1)[0]
            nxt = flip_p(state) if kind == "flip_p" else flip_q(state)
            if tags_per_event == 1:
                event_text = rng.choice(ct[nxt])
            else:
                pair = sorted(rng.sample(ct[nxt], 2))
                event_text = " ".join(pair)
            in_acq = (acq_lo * EVENTS_PER_CYCLE <= len(events)
                      < acq_hi * EVENTS_PER_CYCLE)
            is_withheld = (state == held and nxt == held_flip_p and in_acq)
            trainable.append(not is_withheld)
            events.append(event_text)
            state = nxt

    world_edges: set[tuple[str, str]] = {
        (s, d)
        for c in CELLS
        for nc in (flip_p(c), flip_q(c))
        for s in ct[c]
        for d in ct[nc]
    }
    return events, trainable, world_edges, ct, held, held_flip_p


# ---------------------------------------------------------------------------
# Coverage helpers
# ---------------------------------------------------------------------------

def _raw_coverage(prec_rows, world_edges, k=MAX_PREDICTIONS):
    """Top-K per source (raw), check coverage of world_edges."""
    from collections import defaultdict
    per_src: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for src, dst, cnt in prec_rows:
        per_src[src].append((dst, cnt))
    edges: set[tuple[str, str]] = set()
    for src, items in per_src.items():
        items.sort(key=lambda x: -x[1])
        for dst, _ in items[:k]:
            edges.add((src, dst))
    covered = edges & world_edges
    cov = len(covered) / len(world_edges) if world_edges else 0.0
    prec = len(covered) / len(edges) if edges else 0.0
    return cov, prec, len(covered), len(edges)


def _filtered_coverage(prec_rows, world_edges, k=K_FILTERED):
    """Filter to world-tag pairs only, then top-K per source."""
    filtered = [(s, d, c) for s, d, c in prec_rows
                if s in WORLD_TAGS and d in WORLD_TAGS]
    return _raw_coverage(filtered, world_edges, k=k)


# ---------------------------------------------------------------------------
# Main run
# ---------------------------------------------------------------------------

def run_seed(seed: int, tags_per_event: int) -> dict:
    events, trainable, world_edges, ct, held, held_flip_p = \
        _generate_events(seed, tags_per_event)

    db_path = temp_db(f"obsprotocol_{tags_per_event}t_{seed}")
    mem = MemoryService(db_path)
    try:
        svc = SleepService(mem)
        for cycle in range(CYCLES_ACQ):
            start = cycle * EVENTS_PER_CYCLE
            for i in range(start, start + EVENTS_PER_CYCLE):
                if trainable[i]:
                    mem.store(events[i])
            svc.run_sleep_cycle()

        prec_rows = mem._conn.execute(
            "SELECT tag_from, tag_to, count FROM precedes ORDER BY count DESC"
        ).fetchall()

        raw_cov, raw_prec, raw_n, raw_edges = _raw_coverage(prec_rows, world_edges)
        filt_cov, filt_prec, filt_n, filt_edges = _filtered_coverage(prec_rows, world_edges)

        # Also check what fraction of prec_rows are world-tag pairs
        wt_pairs = sum(1 for s, d, _ in prec_rows if s in WORLD_TAGS and d in WORLD_TAGS)
        total_rows = len(prec_rows)

        return {
            "seed": seed,
            "tags_per_event": tags_per_event,
            "held": cell_name(held),
            "held_flip_p": cell_name(held_flip_p),
            "world_edges": len(world_edges),
            "total_prec_rows": total_rows,
            "world_tag_pair_rows": wt_pairs,
            "world_tag_pair_pct": round(wt_pairs / total_rows, 4) if total_rows else 0,
            "raw": {
                "edges": raw_edges, "covered": raw_n,
                "coverage": round(raw_cov, 4), "precision": round(raw_prec, 4),
                "gate13_pass": raw_cov >= SUFFICIENCY_THRESHOLD,
            },
            "filtered": {
                "edges": filt_edges, "covered": filt_n,
                "coverage": round(filt_cov, 4), "precision": round(filt_prec, 4),
                "gate13_pass": filt_cov >= SUFFICIENCY_THRESHOLD,
            },
        }
    finally:
        mem.close()
        try:
            db_path.unlink(missing_ok=True)
        except Exception:
            pass


def main():
    print("Observation-Protocol Probe: World-Tags-Only Filtered Readout")
    print(f"Sufficiency threshold: {SUFFICIENCY_THRESHOLD}")
    print(f"K_filtered={K_FILTERED}  MAX_PREDICTIONS(raw)={MAX_PREDICTIONS}")
    print("=" * 80)

    for tags_per_event in (1, 2):
        label = f"{tags_per_event}-tag world"
        print(f"\n{'='*80}")
        print(f"  {label.upper()}")
        print(f"{'='*80}")
        raw_passes = 0
        filt_passes = 0
        for seed in SEEDS:
            r = run_seed(seed, tags_per_event)
            raw_pass = "PASS" if r["raw"]["gate13_pass"] else "FAIL"
            filt_pass = "PASS" if r["filtered"]["gate13_pass"] else "FAIL"
            if r["raw"]["gate13_pass"]:
                raw_passes += 1
            if r["filtered"]["gate13_pass"]:
                filt_passes += 1
            print(f"\nSeed {seed}  held={r['held']}->{r['held_flip_p']}")
            print(f"  precedes rows: {r['total_prec_rows']}  "
                  f"world-tag pairs: {r['world_tag_pair_rows']} "
                  f"({r['world_tag_pair_pct']*100:.1f}%)")
            print(f"  RAW      [{raw_pass}]:  "
                  f"cov={r['raw']['coverage']:.4f}  "
                  f"prec={r['raw']['precision']:.4f}  "
                  f"edges={r['raw']['edges']}")
            print(f"  FILTERED [{filt_pass}]:  "
                  f"cov={r['filtered']['coverage']:.4f}  "
                  f"prec={r['filtered']['precision']:.4f}  "
                  f"edges={r['filtered']['edges']}")

        print(f"\n  {label} summary:")
        print(f"    Raw gate13:      {raw_passes}/{len(SEEDS)}")
        print(f"    Filtered gate13: {filt_passes}/{len(SEEDS)}")
        verdict = ""
        if filt_passes == len(SEEDS) and raw_passes < len(SEEDS):
            verdict = "-> World A+: contamination is ONLY in the readout layer."
        elif filt_passes == 0:
            verdict = "-> World B+: structural problem persists even after filtering."
        elif filt_passes > raw_passes:
            verdict = f"-> Partial: filtering helps ({filt_passes} vs {raw_passes} raw)."
        else:
            verdict = f"-> Filtering made no difference ({filt_passes} vs {raw_passes} raw)."
        print(f"    {verdict}")


if __name__ == "__main__":
    main()
