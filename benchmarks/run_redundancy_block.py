"""Pre-registered runner for the loop-redundancy moderator block (docs/GATE13-RATIO-REDUNDANCY-PREREGISTRATION.md).

Two arms at one cap: the registered count control C and the registered ratio arm R, cap 20. Each cell records the
asserted set digest, coverage, precision, and the store-time loop attribution the covariate needs. Resumable JSONL,
scratch databases only, engine untouched.

Self-test (run before the block, on a seed the block excludes) replays a block-2 cell and asserts the runner reproduces
its recorded `asserted`, `covered` and digest.
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
OUT = REPO / ".scratch" / "redundancy_block.jsonl"


def run_cell(arm: str, seed: int) -> dict:
    t0 = time.time()
    world = generate_compositional_world(seed=seed, cycles=300, events_per_cycle=EVENTS_PER_CYCLE)
    events, trainable = world["events"], world["trainable"]
    vocab = set(world["tag_to_cell"])
    world_edges = _world_compositional_edges(world)
    acq_lo, acq_hi = PHASE_ACQUISITION

    path = _make_scratch_db(f"redblock_{arm}_{seed}")
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
        digest = hashlib.sha1("\n".join(sorted(f"{u}>{v}" for u, v in asserted)).encode()).hexdigest()[:16]
    finally:
        mem.close()
        try:
            path.unlink(missing_ok=True)
        except Exception:
            pass

    contrib = attribute(payloads_to_candidates(payloads))
    loop_edges = {e for e, types in contrib.items() if "loop_candidate" in types}
    loop_world = loop_edges & world_edges
    # G2 compares loop attribution ACROSS ARMS, so the count is not enough: record a set digest.
    loop_hash = hashlib.sha1("\n".join(sorted(f"{u}>{v}" for u, v in loop_world)).encode()).hexdigest()[:16]
    return {
        "arm": arm, "cap": CAP, "seed": seed,
        "asserted": len(asserted), "covered": len(covered), "asserted_hash": digest,
        "coverage": round(len(covered) / len(world_edges), 4),
        "precision": round(len(covered) / len(asserted), 4) if asserted else None,
        "world_edges_total": len(world_edges),
        "loop_world_edges": len(loop_world), "loop_hash": loop_hash,
        "r": round(len(loop_world) / len(world_edges), 4),
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
    ap.add_argument("--budget", type=int, default=1000)
    ap.add_argument("--jsonl", type=str, default=str(OUT))
    ap.add_argument("--self-test", type=int, default=None, help="replay one excluded seed and check it against block 2")
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
                  f"-> {'PASS' if ok else 'FAIL'}", flush=True)
            if not ok:
                raise SystemExit("self-test failed; the runner is not validated against block 2")
        print("self-test PASS")
        return

    lo, hi = (int(x) for x in args.block.split(":"))
    out = Path(args.jsonl)
    have, ran = done(out), 0
    for seed in range(lo, hi + 1):
        for arm in ("C", "R"):
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
            print(f"{arm} seed={seed} cov={r['coverage']} prec={r['precision']} r={r['r']} "
                  f"loop={r['loop_world_edges']} ({r['runtime_s']}s)", flush=True)
    print(f"complete: {len(have)} cells")


if __name__ == "__main__":
    main()
