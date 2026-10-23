"""
MBSD census: the full table, with the exact density denominator.

`benchmarks/gate_validation.py` reads the V1 artifact and shows that the
within-cycle relationship is an IDENTITY -- the theory count equals the
number of subjects holding >= 2 beliefs, capped at MAX_THEORIES -- in
100% of cycles for 9 of the 11 conditions. The one designed exception is
F (No Hypothesis Layer), which bypasses Layer 4 and builds theories
straight from workflow components: 6 theories, 0 competing subjects.

The artifact does not record how many DISTINCT SUBJECTS hold beliefs, so
the density's denominator is missing. This re-runs the 11 conditions with
an instrumented service that records it, and produces the full table:

    Condition | Subjects >=2 Beliefs | MBSD | Theory Count

The V1 condition classes are imported and reused verbatim, so this is the
same experiment, not a re-implementation.

Usage: python benchmarks/mbsd_census.py --cycles 300
Writes docs/mbsd_census.json
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "benchmarks"))

from ablation_study import (                     # noqa: E402
    CONDITIONS, NoStructureMemory, RandomCuriosityService, RandomSleepService)
from organica.memory import MemoryService         # noqa: E402
from organica.sleep import SleepService           # noqa: E402
from organica.streams import EVENTS_PER_CYCLE, STUDY_STREAM  # noqa: E402
from organica.paths import temp_db                # noqa: E402

MAX_THEORIES = SleepService.MAX_THEORIES


class Instrumented(SleepService):
    """Records how many belief subjects exist and how many compete."""

    def __init__(self, memory, **kwargs):
        super().__init__(memory, **kwargs)
        self.records = []

    def _retain_hypotheses(self, beliefs, info, temporal):
        counts = Counter(h.subject for h in beliefs)
        self.records.append({
            "beliefs": len(beliefs),
            "subjects": len(counts),
            "subjects_ge2": sum(1 for c in counts.values() if c >= 2),
            "subjects_ge3": sum(1 for c in counts.values() if c >= 3),
        })
        return super()._retain_hypotheses(beliefs, info, temporal)


def make_instrumented(base_cls):
    """Build an instrumented version of a V1 condition class.

    The mixin is placed FIRST so its _retain_hypotheses records and then
    delegates to the condition's own implementation. For NoHypothesisLayer
    the hypothesis layer is bypassed entirely, so the mixin never fires --
    which is itself the finding.
    """
    return type(f"Instr{base_cls.__name__}", (Instrumented, base_cls), {})


def run(code, name, sleep_cls, mem_cls, cycles, seed, stream):
    rng = random.Random(seed)
    db = temp_db(f"mbsd_{code}.db")
    if db.exists():
        db.unlink()
    mem = mem_cls(db)
    cls = make_instrumented(sleep_cls)
    if sleep_cls in (RandomSleepService, RandomCuriosityService):
        sleep = cls(mem, rng=rng)
    else:
        sleep = cls(mem)

    t0 = time.time()
    try:
        for cycle in range(cycles):
            start = (cycle * EVENTS_PER_CYCLE) % len(stream)
            chunk = [stream[(start + k) % len(stream)] for k in range(EVENTS_PER_CYCLE)]
            for text in chunk:
                mem.store(text, event_type="event", source=f"cycle:{cycle}")
            sleep.run_sleep_cycle()
    finally:
        elapsed = time.time() - t0
        mem.close()
        db.unlink(missing_ok=True)

    recs = sleep.records
    if not recs:
        return {
            "condition": code, "name": name, "seconds": round(elapsed, 1),
            "hypothesis_layer_engaged": False,
            "note": "Layer 4 is bypassed by design in this condition; there "
                    "is no belief pool, so MBSD is undefined and the theory "
                    "count comes from a different route.",
        }

    tail = recs[int(len(recs) * 0.75):] or recs
    subj = [r["subjects"] for r in tail]
    ge2 = [r["subjects_ge2"] for r in tail]
    beliefs = [r["beliefs"] for r in tail]
    density = (sum(ge2) / sum(subj)) if sum(subj) else 0.0
    return {
        "condition": code,
        "name": name,
        "seconds": round(elapsed, 1),
        "hypothesis_layer_engaged": True,
        "subjects_mean": round(statistics.fmean(subj), 2),
        "subjects_max": max(subj),
        "subjects_ge2_mean": round(statistics.fmean(ge2), 2),
        "subjects_ge2_max": max(ge2),
        "subjects_ge3_max": max(r["subjects_ge3"] for r in tail),
        "mbsd_density": round(density, 3),
        "belief_pool_mean": round(statistics.fmean(beliefs), 2),
        "belief_pool_max": max(beliefs),
        "retention_pressure_mean": round(
            statistics.fmean(beliefs) / SleepService.MAX_HYPOTHESES, 3),
        "retention_pressure_max": round(
            max(beliefs) / SleepService.MAX_HYPOTHESES, 3),
        "passes_mbsd_absolute_ge3": max(ge2) >= 3,
        "passes_mbsd_density_ge050": density >= 0.50,
        "passes_g_p1": max(beliefs) > SleepService.MAX_HYPOTHESES,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=300)
    ap.add_argument("--out", default=str(REPO / "docs" / "mbsd_census.json"))
    args = ap.parse_args()

    stream = list(STUDY_STREAM)
    rows = []
    out_path = Path(args.out)

    def flush(rows):
        out = {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "cycles": args.cycles,
            "purpose": "Exact MBSD density (with denominator) for the 11 V1 "
                       "conditions, using the V1 condition classes verbatim.",
            "rows": list(rows),
        }
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")

    for idx, (code, name, desc, sleep_cls, mem_cls) in enumerate(CONDITIONS):
        seed = 1000 + idx
        r = run(code, name, sleep_cls, mem_cls, args.cycles, seed, stream)
        rows.append(r)
        flush(rows)          # write after every condition: a crash must not
                             # lose completed work
        if r["hypothesis_layer_engaged"]:
            print(f"{code:<8}{name:<26} subj={r['subjects_mean']:>5.2f}/"
                  f"{r['subjects_max']:<3} ge2={r['subjects_ge2_mean']:>5.2f}/"
                  f"{r['subjects_ge2_max']:<3} MBSD={r['mbsd_density']:>5.3f} "
                  f"pool={r['belief_pool_mean']:>5.2f}/{r['belief_pool_max']:<3}"
                  f" press={r['retention_pressure_mean']:>5.3f}"
                  f"  G-MBD:{'Y' if r['passes_mbsd_absolute_ge3'] else 'n'}"
                  f"  G-P1:{'Y' if r['passes_g_p1'] else 'n'}")
        else:
            print(f"{code:<8}{name:<26} Layer-4 bypassed -- MBSD undefined")
        sys.stdout.flush()

    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
