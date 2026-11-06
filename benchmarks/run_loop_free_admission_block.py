"""Runner for the loop-free preference arm (block 6).

Arms, all at cap 20 on the same world:

  C  count-sorted admission -- the registered control of blocks 2-5.
  R  ratio-sorted admission -- the registered treatment of blocks 2-5.
  X  **the intervention at soft dose**: identical to R except that a candidate whose edge a loop
     candidate asserts *this cycle* sorts after one that no loop asserts. This is the arm §10 of the
     block-5 pre-registration names as the decisive test: it manipulates admission instead of hoping
     the covariate varies between seeds. Calibrated on ten seeds it displaces ~6 admitted edges per
     cycle yet moves final coverage by a median of +0.004 (sd 0.021) -- a dose too weak to test at 100
     seeds, recorded in `docs/gate13_loop_free_admission_calibration.json`.
  Y  **the intervention at full dose**: the same preference, applied by reserving the cap for edges no
     loop asserts and backfilling with loop-asserted edges only when fewer than the cap qualify. Same
     mechanism, no reordering dilution: ~30% of R's admission budget is spent on edges loops already
     assert, and this arm spends it elsewhere.

The loop set is the one the engine itself forms for the cycle: `SleepService.run` calls
`_build_loops(temporal)` at line 166 and `_build_predictions(temporal, freqs)` at line 175, so the arm
recomputes the same deterministic function on the same `temporal` dict before sorting. Nothing in the
engine is edited; the arm is a subclass, as `benchmarks/ablation_study.py` is.

Edges are compared undirected because the readout (`structure_edges`) counts a loop's path edges in
both directions. A candidate edge (u, v) is "loop-asserted" when (u, v) or (v, u) is a loop path edge.

Resumable JSONL, scratch databases only, PYTHONHASHSEED=0. `--self-test SEED` re-derives the C and R
cells of a block-2 seed and refuses to run if they differ from `docs/gate13_ratio_block2.json`.
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
from benchmarks.run_ratio_admission_arm import make_arm, RatioAdmissionSleepService
from benchmarks.run_paired_capacity_test import PairedDiagnosticSleepService, NON_VOCAB_MARKERS
from benchmarks.diagnose_structure_provenance import payloads_to_candidates, attribute

CAP = 20
ARMS = ("C", "R", "Y")  # X is calibration-only: on this world family it is the same function as Y
OUT = REPO / ".scratch" / "loop_free_admission_block.jsonl"


def _digest(edges) -> str:
    return hashlib.sha1("\n".join(sorted(f"{u}>{v}" for u, v in edges)).encode()).hexdigest()[:16]


def _loop_edges(loops) -> set[tuple[str, str]]:
    """Undirected edges of the loop candidates' paths, matching how `structure_edges` reads them."""
    edges: set[tuple[str, str]] = set()
    for loop in loops:
        path = list(getattr(loop, "path", []) or [])
        for a, b in zip(path, path[1:]):
            edges.add((a, b))
            edges.add((b, a))
    return edges


class LoopFreePreferenceSleepService(RatioAdmissionSleepService):
    """R, with loop-asserted edges sorted last.

    The parent lifts the engine's own cap, builds every admissible candidate, and re-sorts by ratio.
    This arm does the same and then applies one extra key: a candidate whose edge a loop asserts sorts
    after one that no loop asserts; within each group the parent's ratio order is preserved. The cap is
    the parent's, unchanged, and the candidate construction is the engine's, unchanged.

    `self.displacements` records, per cycle, how many edges the preference pushed out of the top-cap
    ratio set -- the size of the perturbation. An intervention that displaces nothing has not run.
    """

    def __init__(self, memory, max_predictions: int = 20):
        super().__init__(memory, max_predictions=max_predictions)
        self.displacements: list[int] = []

    def _build_predictions(self, temporal, freqs):
        self.custom_max_predictions = 10 ** 9
        try:
            cands = PairedDiagnosticSleepService._build_predictions(self, temporal, freqs)
        finally:
            self.custom_max_predictions = self.admission_cap

        loop_edges = _loop_edges(self._build_loops(temporal))

        def ratio_key(p):
            ev = p.evidence or {}
            count = ev.get("temporal_count", 0)
            src_freq = max(ev.get("source_frequency", 1) or 1, 1)
            return (-(count / src_freq), -count, p.source, p.target)

        def preference_key(p):
            edge = (p.source, p.target)
            loop_asserted = edge in loop_edges or (edge[1], edge[0]) in loop_edges
            return (1 if loop_asserted else 0, *ratio_key(p))

        by_ratio = sorted(cands, key=ratio_key)[: self.admission_cap]
        chosen = sorted(cands, key=preference_key)[: self.admission_cap]
        ratio_edges = {(p.source, p.target) for p in by_ratio}
        chosen_edges = {(p.source, p.target) for p in chosen}
        self.displacements.append(len(ratio_edges - chosen_edges))
        return chosen


class LoopFreeReserveSleepService(RatioAdmissionSleepService):
    """R with the cap reserved for edges no loop asserts -- the same preference at full dose.

    Candidates are the engine's, the cap is the parent's. The only change is which candidates the cap
    is spent on: non-loop edges first in ratio order, loop-asserted edges only as backfill when fewer
    than `cap` non-loop candidates exist. `self.displacements` records how many loop-asserted edges the
    reservation pushed out of the cap each cycle.
    """

    def __init__(self, memory, max_predictions: int = 20):
        super().__init__(memory, max_predictions=max_predictions)
        self.displacements: list[int] = []

    def _build_predictions(self, temporal, freqs):
        self.custom_max_predictions = 10 ** 9
        try:
            cands = PairedDiagnosticSleepService._build_predictions(self, temporal, freqs)
        finally:
            self.custom_max_predictions = self.admission_cap

        loop_edges = _loop_edges(self._build_loops(temporal))

        def ratio_key(p):
            ev = p.evidence or {}
            count = ev.get("temporal_count", 0)
            src_freq = max(ev.get("source_frequency", 1) or 1, 1)
            return (-(count / src_freq), -count, p.source, p.target)

        def loop_asserted(p):
            edge = (p.source, p.target)
            return edge in loop_edges or (edge[1], edge[0]) in loop_edges

        novel = sorted((p for p in cands if not loop_asserted(p)), key=ratio_key)
        redundant = sorted((p for p in cands if loop_asserted(p)), key=ratio_key)
        chosen = novel[: self.admission_cap]
        if len(chosen) < self.admission_cap:
            chosen += redundant[: self.admission_cap - len(chosen)]

        by_ratio = sorted(cands, key=ratio_key)[: self.admission_cap]
        ratio_edges = {(p.source, p.target) for p in by_ratio}
        chosen_edges = {(p.source, p.target) for p in chosen}
        self.displacements.append(len(ratio_edges - chosen_edges))
        return chosen


def make_block_arm(mem: MemoryService, arm: str, cap: int):
    if arm == "X":
        return LoopFreePreferenceSleepService(mem, max_predictions=cap)
    if arm == "Y":
        return LoopFreeReserveSleepService(mem, max_predictions=cap)
    return make_arm(mem, arm, cap)


def run_cell(arm: str, seed: int, cap: int = CAP) -> dict:
    t0 = time.time()
    world = generate_compositional_world(seed=seed, cycles=300, events_per_cycle=EVENTS_PER_CYCLE)
    events, trainable = world["events"], world["trainable"]
    vocab = set(world["tag_to_cell"])
    world_edges = _world_compositional_edges(world)
    acq_lo, acq_hi = PHASE_ACQUISITION

    path = _make_scratch_db(f"loopfree_{arm}_{cap}_{seed}")
    mem = MemoryService(str(path))
    svc = make_block_arm(mem, arm, cap)
    payloads = []
    orig_store = mem.store

    def store(content, *a, **kw):
        if kw.get("event_type", (a[0] if a else "observe")) == "sleep":
            payloads.append((kw.get("source"), content))
        return orig_store(content, *a, **kw)

    mem.store = store
    disp = []
    try:
        for ci in range(acq_hi):
            in_acq = acq_lo <= ci < acq_hi
            for i in range(ci * EVENTS_PER_CYCLE, (ci + 1) * EVENTS_PER_CYCLE):
                if in_acq and not trainable[i]:
                    continue
                mem.store(events[i], event_type="observe", source="env_acq" if in_acq else "env")
            svc.run_sleep_cycle()
            disp = list(getattr(svc, "displacements", []) or [])

        asserted = {(u, v) for u, tg in structure_edges(svc._load_prior_candidates()).items() for v in tg
                    if u in vocab and v in vocab and u not in NON_VOCAB_MARKERS and v not in NON_VOCAB_MARKERS}
        covered = asserted & world_edges
        # The engine clears `_current_tag_events` at the end of a cycle; `_build_loops` reads it only for
        # parent ids, never for the path edges, so an empty map is enough to rebuild the same loop set.
        svc._current_tag_events = {}
        final_loops = _loop_edges(svc._build_loops(svc._load_temporal()))
        final_loops = {(u, v) for (u, v) in final_loops if u in vocab and v in vocab}
    finally:
        mem.close()
        try:
            path.unlink(missing_ok=True)
        except Exception:
            pass

    contrib = attribute(payloads_to_candidates(payloads))
    loop_pred = {e for e, t in contrib.items() if "loop_candidate" in t} & world_edges
    pred_edges = {e for e, t in contrib.items() if "prediction_candidate" in t} & world_edges

    row = {
        "arm": arm, "cap": cap, "seed": seed,
        "asserted": len(asserted), "covered": len(covered),
        "asserted_hash": _digest(asserted),
        "coverage": round(len(covered) / len(world_edges), 4),
        "precision": round(len(covered) / len(asserted), 4) if asserted else None,
        "world_edges_total": len(world_edges),
        "loop_edges": len(final_loops),
        "asserted_loop": len(asserted & final_loops),
        "covered_loop": len(covered & final_loops),
        "covered_novel": len(covered - final_loops),
        "loop_world": len(loop_pred), "pred_world": len(pred_edges),
        "overlap": len(loop_pred & pred_edges),
        "runtime_s": round(time.time() - t0, 1),
    }
    if disp:
        row["disp_total"] = sum(disp)
        row["disp_cycles"] = sum(1 for d in disp if d > 0)
        row["disp_max"] = max(disp)
        row["disp_mean"] = round(sum(disp) / len(disp), 3)
    return row


def done(path: Path) -> set:
    if not path.exists():
        return set()
    return {(r["arm"], r["cap"], r["seed"]) for r in
            (json.loads(x) for x in path.read_text().splitlines() if x.strip())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--block", type=str, default=None, help="START:END inclusive")
    ap.add_argument("--arm", type=str, default=None, choices=ARMS)
    ap.add_argument("--budget", type=int, default=1000)
    ap.add_argument("--jsonl", type=str, default=str(OUT))
    ap.add_argument("--caps", type=str, default=None, help="comma-separated caps, e.g. 40,100")
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
                  f"-> {'PASS' if ok else 'FAIL'}", flush=True)
            if not ok:
                raise SystemExit("self-test failed; the C/R path is not validated against block 2")
        print("self-test PASS", flush=True)
        return

    lo, hi = (int(x) for x in args.block.split(":"))
    arms = (args.arm,) if args.arm else ARMS
    caps = tuple(int(x) for x in args.caps.split(",")) if args.caps else (CAP,)
    out = Path(args.jsonl)
    have, ran = done(out), 0
    for seed in range(lo, hi + 1):
        for cap in caps:
            for arm in arms:
                if (arm, cap, seed) in have:
                    continue
                if ran >= args.budget:
                    print(f"budget reached: {ran} new cells, {len(have)} total done")
                    return
                r = run_cell(arm, seed, cap)
                out.parent.mkdir(parents=True, exist_ok=True)
                with out.open("a") as f:
                    f.write(json.dumps(r) + "\n")
                have.add((arm, cap, seed))
                ran += 1
                extra = f" disp={r.get('disp_total', 0)}" if arm == "Y" else ""
                print(f"{arm} cap={cap} seed={seed} cov={r['coverage']} prec={r['precision']} "
                      f"loopE={r['loop_edges']} assertedLoop={r['asserted_loop']} novel={r['covered_novel']}"
                      f"{extra} ({r['runtime_s']}s)", flush=True)
    print(f"complete: {len(have)} cells")


if __name__ == "__main__":
    main()
