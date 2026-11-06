"""The pre-registered `ratio` admission arm (docs/GATE13-RATIO-ADMISSION-PREREGISTRATION.md).

Three conditions, identical in every respect except the admission ordering:

  C  count-sorted admission at the cap (the rule in `PairedDiagnosticSleepService`, under which the
     §5-§8 capacity record was measured) -- the registered control.
  R  the same construction and the same cap, sorted by `ratio = count / max(source_freq, 1)`
     (deterministic tiebreak: -ratio, -count, source, target) -- the registered treatment.
  E  the engine's own rule (`organica/sleep_extraction.py::_build_predictions`: target entropy
     ascending, transition probability, count, half-cap to transitions, remainder to co-occurrences)
     at the same cap -- a reference condition added by Amendment 1, not a registered comparison.

Resumable: one JSON line per (arm, cap, seed) in .scratch/ratio_arm.jsonl; `--budget N` exits after N
new cells.  Scratch DBs only; no frozen file is edited.  Run with PYTHONHASHSEED=0.
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
from organica.sleep import SleepService
from benchmarks.acquisition_harness import _make_scratch_db
from benchmarks.acquisition_compositional import generate_compositional_world, PHASE_ACQUISITION
from benchmarks.acquisition_runner import _world_compositional_edges, structure_edges, EVENTS_PER_CYCLE
from benchmarks.run_paired_capacity_test import PairedDiagnosticSleepService, NON_VOCAB_MARKERS

SEEDS = [20261101, 20261102, 20261103, 20261104, 20261105]  # development block
CAPS = (20, 100, 1000)            # registered
CAPS_EXTRA = (10, 20, 100, 1000)  # C/R only: cap 10 supplies P4's size-matched bracket
ARMS = ("C", "R", "E")
def plan_cells(seeds):
    """Arm-major cell plan: C/R at four caps, E at three.  The only block-dependent input is `seeds`."""
    return [(a, c, s) for a in ARMS
            for c in (CAPS_EXTRA if a in ("C", "R") else CAPS)
            for s in seeds]


CELLS = plan_cells(SEEDS)
KS = (20, 40, 80)
OUT = REPO / ".scratch" / "ratio_arm.jsonl"


class RatioAdmissionSleepService(PairedDiagnosticSleepService):
    """Identical construction and cap to arm C; only the sort key differs.

    The parent sorts and *then* truncates, so re-sorting its return value would be a no-op on
    membership. The parent's own budget is therefore lifted for the one call and the arm's real cap
    is applied here, to the ratio-ordered list. Candidate construction, evidence fields, thresholds
    and the cap value are the parent's, untouched.
    """

    def __init__(self, memory, max_predictions: int = 20):
        super().__init__(memory, max_predictions=max_predictions)
        self.admission_cap = max_predictions

    def _build_predictions(self, temporal, freqs):
        self.custom_max_predictions = 10 ** 9
        try:
            cands = super()._build_predictions(temporal, freqs)
        finally:
            self.custom_max_predictions = self.admission_cap

        def key(p):
            ev = p.evidence or {}
            count = ev.get("temporal_count", 0)
            src_freq = max(ev.get("source_frequency", 1) or 1, 1)
            return (-(count / src_freq), -count, p.source, p.target)

        return sorted(cands, key=key)[: self.admission_cap]


def make_arm(mem: MemoryService, arm: str, cap: int):
    if arm == "C":
        return PairedDiagnosticSleepService(mem, max_predictions=cap)
    if arm == "R":
        return RatioAdmissionSleepService(mem, max_predictions=cap)
    if arm == "E":
        svc = SleepService(mem)
        svc.MAX_PREDICTIONS = cap          # engine-native rule at the same budget
        return svc
    raise ValueError(arm)


def pool_diagnostics(mem, vocab, world_edges, arm):
    rows = [(s, d, c) for s, d, c in mem._conn.execute(
        "SELECT tag_from, tag_to, count FROM precedes") if s in vocab and d in vocab]
    if not rows:
        return {"pool_rows": 0}
    freqs = {t: c for t, c in mem._conn.execute("SELECT tag, count FROM tag_counts")}
    def score(_, __, c, s=None, d=None):
        return c
    def key_row(r):
        s, d, c = r
        if arm == "R":
            return -(c / max(freqs.get(s, 1) or 1, 1))
        return -c                                  # C and E are both count-scored in the pool
    if arm == "R":
        rows.sort(key=lambda r: (key_row(r), -r[2], r[0], r[1]))
    else:
        rows.sort(key=lambda r: (-r[2], r[0], r[1]))
    vals = [key_row(r) for r in rows]
    from collections import Counter
    modal = Counter(vals).most_common(1)[0]
    marks = [(s, d) in world_edges for s, d, _c in rows]
    n = len(rows)
    return {
        "pool_rows": n,
        "pool_world_edges": sum(marks),
        "base_rate": round(sum(marks) / n, 4),
        "distinct_values": len(set(vals)),
        "modal_tie_share": round(modal[1] / n, 4),
        "top_k": {str(k): round(sum(marks[:k]) / k, 4) for k in KS if k <= n},
    }


def run_cell(arm: str, cap: int, seed: int) -> dict:
    t0 = time.time()
    world = generate_compositional_world(seed=seed, cycles=300, events_per_cycle=EVENTS_PER_CYCLE)
    events, trainable = world["events"], world["trainable"]
    vocab = set(world["tag_to_cell"]); world_edges = _world_compositional_edges(world)
    acq_lo, acq_hi = PHASE_ACQUISITION

    path = _make_scratch_db(f"ratioarm_{arm}_{cap}_{seed}")
    mem = MemoryService(str(path)); svc = make_arm(mem, arm, cap)
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
        # C0 compares asserted SETS; the development block recorded only their size.
        asserted_hash = hashlib.sha1(
            "\n".join(sorted(f"{u}>{v}" for u, v in asserted)).encode()).hexdigest()[:16]
        diag = pool_diagnostics(mem, vocab, world_edges, arm)
        return {
            "arm": arm, "cap": cap, "seed": seed,
            "asserted": len(asserted), "covered": covered,
            "asserted_hash": asserted_hash,
            "coverage": round(covered / len(world_edges), 4),
            "precision": round(covered / len(asserted), 4) if asserted else None,
            "world_edges_total": len(world_edges),
            "runtime_s": round(time.time() - t0, 1),
            **diag,
        }
    finally:
        mem.close()
        try: path.unlink(missing_ok=True)
        except Exception: pass


def done(path: Path) -> set:
    if not path.exists():
        return set()
    out = set()
    for line in path.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            out.add((r["arm"], r["cap"], r["seed"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=1000)
    ap.add_argument("--block", type=str, default=None,
                    help="START:END inclusive, e.g. 20270602:20270626; overrides the development seeds")
    ap.add_argument("--jsonl", type=str, default=str(OUT))
    args = ap.parse_args()
    out_path = Path(args.jsonl)
    cells = CELLS
    if args.block:
        lo, hi = (int(x) for x in args.block.split(":"))
        cells = plan_cells(list(range(lo, hi + 1)))
    have = done(out_path); ran = 0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    for arm, cap, seed in cells:
                if (arm, cap, seed) in have:
                    continue
                if ran >= args.budget:
                    print(f"budget reached: {ran} new cells, {len(have)} total done")
                    return
                r = run_cell(arm, cap, seed)
                with out_path.open("a") as f:
                    f.write(json.dumps(r) + "\n")
                have.add((arm, cap, seed)); ran += 1
                print(f"{arm} cap={cap:<5} seed={seed}  cov={r['coverage']:.4f} "
                      f"prec={r['precision']} asserted={r['asserted']} "
                      f"pool={r.get('pool_rows')} base={r.get('base_rate')} ({r['runtime_s']}s)", flush=True)
    print(f"complete: {len(have)} cells")


if __name__ == "__main__":
    main()
