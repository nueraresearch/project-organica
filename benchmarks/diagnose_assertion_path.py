"""Replay the block-2 cap-20 cells and trace what each arm's admission window actually did.

The stored artifact holds aggregates only (`asserted`, `covered`, `asserted_hash`), and the recorded `top_k` density is
measured on the *final* pool -- after the treatment has already acted. This replays the same deterministic cells, records
every per-cycle admission window, and refuses to interpret any cell whose replay disagrees with the stored aggregate.
Writes `docs/gate13_assertion_path.json`.

**Replay, not a new experiment**: same seeds, same harness, same caps, read-only with respect to `organica/` and the
artifacts. Recording is an instance-level wrapper that returns the unmodified list, and the hash check is what proves it.
"""
from __future__ import annotations

import hashlib
import json
import statistics as st
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.memory import MemoryService
from benchmarks.acquisition_harness import _make_scratch_db
from benchmarks.acquisition_compositional import generate_compositional_world, PHASE_ACQUISITION
from benchmarks.acquisition_runner import _world_compositional_edges, structure_edges, EVENTS_PER_CYCLE
from benchmarks.run_ratio_admission_arm import make_arm
from benchmarks.run_paired_capacity_test import NON_VOCAB_MARKERS
from benchmarks import engine_stamp

BLOCK = json.loads((REPO / "docs/gate13_ratio_block2.json").read_text())


def cells():
    return {(r["arm"], r["cap"], r["seed"]): r for r in BLOCK["raw"]}


def replay(arm, cap, seed):
    """Same construction and loop as run_cell, plus a per-cycle trace of the admission window."""
    world = generate_compositional_world(seed=seed, cycles=300, events_per_cycle=EVENTS_PER_CYCLE)
    events, trainable = world["events"], world["trainable"]
    vocab = set(world["tag_to_cell"])
    world_edges = _world_compositional_edges(world)
    acq_lo, acq_hi = PHASE_ACQUISITION

    path = _make_scratch_db(f"assertpath_{arm}_{cap}_{seed}")
    mem = MemoryService(str(path))
    svc = make_arm(mem, arm, cap)
    trace = []
    orig = svc._build_predictions

    def wrapped(temporal, freqs):
        out = orig(temporal, freqs)
        trace.append([(p.source, p.target, (p.source, p.target) in world_edges,
                       (p.evidence or {}).get("temporal_count", 0),
                       (p.evidence or {}).get("source_frequency", 0)) for p in out])
        return out

    svc._build_predictions = wrapped
    try:
        for ci in range(acq_hi):
            in_acq = acq_lo <= ci < acq_hi
            for i in range(ci * EVENTS_PER_CYCLE, (ci + 1) * EVENTS_PER_CYCLE):
                if in_acq and not trainable[i]:
                    continue
                mem.store(events[i], event_type="observe", source="env_acq" if in_acq else "env")
            svc.run_sleep_cycle()

        asserted = {(u, v) for u, targets in structure_edges(svc._load_prior_candidates()).items()
                    for v in targets
                    if u in vocab and v in vocab and u not in NON_VOCAB_MARKERS and v not in NON_VOCAB_MARKERS}
        covered = len(asserted & world_edges)
        digest = hashlib.sha1("\n".join(sorted(f"{u}>{v}" for u, v in asserted)).encode()).hexdigest()[:16]
    finally:
        mem.close()
        try:
            path.unlink(missing_ok=True)
        except Exception:
            pass

    admitted, cycles_used, per_cycle_hits, per_cycle_new = set(), 0, [], []
    first_hit = {}
    for ci, window in enumerate(trace):
        kept = [(u, v) for u, v, _w, _c, _f in window]
        if not kept:
            continue
        cycles_used += 1
        hits = sum(1 for _u, _v, w, _c, _f in window if w)
        per_cycle_hits.append(hits)
        fresh = 0
        for u, v, w, _c, _f in window:
            if not w:
                continue
            if (u, v) not in first_hit:
                first_hit[(u, v)] = ci
                fresh += 1
            admitted.add((u, v))
        per_cycle_new.append(fresh)
    ever = set(first_hit)
    return {
        "arm": arm, "cap": cap, "seed": seed,
        "verified": {"asserted": len(asserted), "covered": covered, "hash": digest},
        "admitted_rows": len(admitted),
        "cycles_with_admissions": cycles_used,
        "window_size_median": st.median([len(w) for w in trace if w]) if any(trace) else 0,
        "per_cycle_hits": per_cycle_hits,
        "per_cycle_new": per_cycle_new,
        "ever_world_edges": len(ever),
        "never_asserted": sorted(f"{u}>{v}" for u, v in (ever - asserted)),
        "lost_edges": sorted(f"{u}>{v}" for u, v in (asserted & world_edges) - ever),
        "first_hit": {"%s>%s" % k: v for k, v in first_hit.items()},
        "covered_set": sorted("%s>%s" % e for e in (asserted & world_edges)),
        "asserted_set": sorted("%s>%s" % e for e in asserted),
    }


def main():
    idx = cells()
    seeds = BLOCK["seeds"]
    rows = {}
    for s in seeds:
        c, r = idx[("C", 20, s)], idx[("R", 20, s)]
        rows[s] = {"delta": round(r["coverage"] - c["coverage"], 4),
                   "uplift": round(r["top_k"]["20"] - c["top_k"]["20"], 4)}
    failing = [s for s in seeds if rows[s]["delta"] <= 0]
    improved = [s for s in seeds if rows[s]["delta"] > 0]
    match, pool = {}, list(improved)
    for f in sorted(failing, key=lambda s: rows[s]["uplift"]):
        best = min(pool, key=lambda s: abs(rows[s]["uplift"] - rows[f]["uplift"]))
        match[f] = best
        pool.remove(best)

    cells_run, mismatches = {}, []
    for group, pairs in (("fail", [(f, f) for f in failing]), ("match", [(f, m) for f, m in match.items()])):
        for _, seed in pairs:
            for arm in ("C", "R"):
                got = replay(arm, 20, seed)
                want = idx[(arm, 20, seed)]
                ok = (got["verified"]["asserted"] == want["asserted"]
                      and got["verified"]["covered"] == want["covered"]
                      and got["verified"]["hash"] == want["asserted_hash"])
                got["matched_to"] = seed if group == "match" else None
                got["group"] = group
                got["replay_matches_artifact"] = ok
                if not ok:
                    mismatches.append({"seed": seed, "arm": arm, "got": got["verified"],
                                       "want": {"asserted": want["asserted"], "covered": want["covered"],
                                                "hash": want["asserted_hash"]}})
                cells_run[f"{seed}_{arm}"] = got
                print(f"{group} {seed} {arm}: asserted {got['verified']['asserted']} "
                      f"covered {got['verified']['covered']} ever {got['ever_world_edges']} "
                      f"windows {got['cycles_with_admissions']} match={ok}", flush=True)

    art = {
        "what": "per-cycle admission trace for the failing seeds and uplift-matched improving seeds, block 2 cap 20",
        "status": "EXPLORATORY replay. Same seeds and harness; recording is behaviour-neutral, proven by the hash check.",
        "seeds_failing": failing, "matched": match, "per_seed_uplift_delta": rows,
        "replay_mismatches": mismatches, "cells": cells_run,
    }
    (REPO / "docs/gate13_assertion_path.json").write_text(json.dumps(engine_stamp.stamp(art), indent=2) + "\n")

    print("\nmismatches:", len(mismatches))
    for k, v in cells_run.items():
        print(f"  {k}: ever-admitted world edges {v['ever_world_edges']}, final covered {v['verified']['covered']}, "
              f"admitted-then-absent {len(v['never_asserted'])}, covered-without-admission {len(v['lost_edges'])}")


if __name__ == "__main__":
    t0 = time.time()
    main()
    print(f"elapsed {time.time() - t0:.0f}s")
