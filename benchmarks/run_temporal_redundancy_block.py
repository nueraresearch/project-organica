"""Pre-registered runner for block 4 (docs/GATE13-TEMPORAL-REDUNDANCY-PREREGISTRATION.md).

Same arms, same cap, same world as blocks 2-3. Adds what the block-4 covariate needs: the control cell's asserted
temporal edges and loop edges as *sets*, so their overlap can be measured on the control cell before the ratio cell is
scored. Resumable JSONL, scratch databases only, engine untouched.
"""
from __future__ import annotations

import argparse
import hashlib
import json
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
from benchmarks.diagnose_structure_provenance import payloads_to_candidates, attribute

CAP = 20
MIN_DENOM = 3          # a share with fewer temporal edges than this is not measurable, not zero
OUT = REPO / ".scratch" / "temporal_redundancy_block.jsonl"


def _digest(edges) -> str:
    return hashlib.sha1("\n".join(sorted(f"{u}>{v}" for u, v in edges)).encode()).hexdigest()[:16]


def run_cell(arm: str, seed: int) -> dict:
    t0 = time.time()
    world = generate_compositional_world(seed=seed, cycles=300, events_per_cycle=EVENTS_PER_CYCLE)
    events, trainable = world["events"], world["trainable"]
    vocab = set(world["tag_to_cell"])
    world_edges = _world_compositional_edges(world)
    acq_lo, acq_hi = PHASE_ACQUISITION

    path = _make_scratch_db(f"trblock_{arm}_{seed}")
    mem = MemoryService(str(path))
    svc = make_arm(mem, arm, CAP)
    payloads = []
    orig_store = mem.store

    def store(content, *a, **kw):
        if kw.get("event_type", (a[0] if a else "observe")) == "sleep":
            payloads.append((kw.get("source"), content))
        return orig_store(content, *a, **kw)

    mem.store = store
    try:
        for ci in range(acq_hi):
            in_acq = acq_lo <= ci < acq_hi
            for i in range(ci * EVENTS_PER_CYCLE, (ci + 1) * EVENTS_PER_CYCLE):
                if in_acq and not trainable[i]:
                    continue
                mem.store(events[i], event_type="observe", source="env_acq" if in_acq else "env")
            svc.run_sleep_cycle()
        asserted = {(u, v) for u, tg in structure_edges(svc._load_prior_candidates()).items() for v in tg
                    if u in vocab and v in vocab and u not in NON_VOCAB_MARKERS and v not in NON_VOCAB_MARKERS}
        covered = asserted & world_edges
    finally:
        mem.close()
        try:
            path.unlink(missing_ok=True)
        except Exception:
            pass

    contrib = attribute(payloads_to_candidates(payloads))
    loop_edges = {e for e, t in contrib.items() if "loop_candidate" in t} & world_edges
    pred_edges = {e for e, t in contrib.items() if "prediction_candidate" in t} & world_edges
    overlap = loop_edges & pred_edges
    return {
        "arm": arm, "cap": CAP, "seed": seed,
        "asserted": len(asserted), "covered": len(covered), "asserted_hash": _digest(asserted),
        "coverage": round(len(covered) / len(world_edges), 4),
        "precision": round(len(covered) / len(asserted), 4) if asserted else None,
        "world_edges_total": len(world_edges),
        "loop_world": len(loop_edges), "loop_hash": _digest(loop_edges),
        "pred_world": len(pred_edges), "pred_hash": _digest(pred_edges),
        "overlap": len(overlap), "overlap_hash": _digest(overlap),
        # the covariate: share of the control's temporal structure its loops already imply
        "o": round(len(overlap) / len(pred_edges), 4) if len(pred_edges) >= MIN_DENOM else None,
        "runtime_s": round(time.time() - t0, 1),
    }


def done(path: Path) -> set:
    if not path.exists():
        return set()
    return {(r["arm"], r["cap"], r["seed"]) for r in
            (json.loads(x) for x in path.read_text().splitlines() if x.strip())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--block", type=str, default=None, help="START:END inclusive")
    ap.add_argument("--arm", type=str, default=None, choices=["C", "R"])
    ap.add_argument("--budget", type=int, default=1000)
    ap.add_argument("--jsonl", type=str, default=str(OUT))
    ap.add_argument("--self-test", type=int, default=None)
    args = ap.parse_args()

    if args.self_test is not None:
        idx = {(r["arm"], r["cap"], r["seed"]): r
               for r in json.loads((REPO / "docs/gate13_ratio_block2.json").read_text())["raw"]}
        for arm in ("C", "R"):
            got, want = run_cell(arm, args.self_test), idx[(arm, 20, args.self_test)]
            ok = (got["asserted"] == want["asserted"] and got["covered"] == want["covered"]
                  and got["asserted_hash"] == want["asserted_hash"])
            print(f"self-test {arm} {args.self_test}: asserted {got['asserted']}/{want['asserted']} "
                  f"covered {got['covered']}/{want['covered']} hash {got['asserted_hash']}=={want['asserted_hash']} "
                  f"| o={got['o']} loop={got['loop_world']} pred={got['pred_world']} -> {'PASS' if ok else 'FAIL'}",
                  flush=True)
            if not ok:
                raise SystemExit("self-test failed; the runner is not validated against block 2")
        print("self-test PASS")
        return

    lo, hi = (int(x) for x in args.block.split(":"))
    arms = (args.arm,) if args.arm else ("C", "R")
    out = Path(args.jsonl)
    have, ran = done(out), 0
    for seed in range(lo, hi + 1):
        for arm in arms:
            if (arm, CAP, seed) in have:
                continue
            if ran >= args.budget:
                print(f"budget reached: {ran} new cells, {len(have)} total done")
                return
            r = run_cell(arm, seed)
            out.parent.mkdir(parents=True, exist_ok=True)
            with out.open("a") as f:
                f.write(json.dumps(r) + "\n")
            have.add((arm, CAP, seed))
            ran += 1
            print(f"{arm} seed={seed} cov={r['coverage']} o={r['o']} overlap={r['overlap']} "
                  f"pred={r['pred_world']} loop={r['loop_world']} ({r['runtime_s']}s)", flush=True)
    print(f"complete: {len(have)} cells")


if __name__ == "__main__":
    main()
