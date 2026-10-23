"""
Branch-stimulus sweep: which design clears all four campaign gates?

The gates (docs/FORCE-MATRIX-PREREGISTRATION.md §1):

  G-CS   competing-subject count >= 3, reaching 5-7
  G-P1   belief pool > MAX_HYPOTHESES (15)  -> retention pressure > 1.0
  G-SUP  belief pool > 15, spread across subjects
  G-EXP  the theory population never reaches MAX_THEORIES (8)

This sweeps a grid of stimulus designs, runs each cold, and reports the
measured gates. Nothing here asserts a design is good; the sweep is the
measurement that decides.

Usage:
    python benchmarks/branch_sweep.py --cycles 300
Writes docs/branch_sweep.json
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.branch_streams import (                # noqa: E402
    NEUTRAL_SUBJECTS, NEUTRAL_SUCCESSORS, SEMANTIC_SUBJECTS,
    SEMANTIC_SUCCESSORS, branch_stream, describe)
from organica.memory import MemoryService            # noqa: E402
from organica.sleep import SleepService              # noqa: E402
from organica.streams import EVENTS_PER_CYCLE, STUDY_STREAM  # noqa: E402
from organica.paths import temp_db                   # noqa: E402

MAX_THEORIES = SleepService.MAX_THEORIES
MAX_HYPOTHESES = SleepService.MAX_HYPOTHESES


class Gated(SleepService):
    """Records the quantities the gates are defined on."""

    def __init__(self, memory):
        super().__init__(memory)
        self.rows = []

    def _retain_hypotheses(self, beliefs, info, temporal):
        counts = Counter(h.subject for h in beliefs)
        self.rows.append({
            "beliefs": len(beliefs),
            "subjects": len(counts),
            "subjects_ge2": sum(1 for c in counts.values() if c >= 2),
        })
        return super()._retain_hypotheses(beliefs, info, temporal)


def evaluate(name: str, events: list[str], cycles: int) -> dict:
    db = temp_db(f"branch_{name}.db")
    if db.exists():
        db.unlink()
    mem = MemoryService(db_path=str(db))
    svc = Gated(mem)

    for text in events:
        mem.store(text, event_type="event", source="seed:bootstrap")

    t0 = time.time()
    theory_counts = []
    for i in range(cycles):
        start = (i * EVENTS_PER_CYCLE) % len(events)
        for text in events[start:start + EVENTS_PER_CYCLE]:
            mem.store(text, event_type="event", source=f"cycle:{i}")
        rep = svc.run_sleep_cycle()
        theory_counts.append(len(rep.theories))
    elapsed = time.time() - t0
    mem.close()
    db.unlink(missing_ok=True)

    rows = svc.rows
    tail = rows[int(len(rows) * 0.75):] or rows
    subj = [r["subjects"] for r in tail]
    ge2 = [r["subjects_ge2"] for r in tail]
    beliefs = [r["beliefs"] for r in tail]

    # G-P1 wants SUSTAINED pressure, so measure the tail of the run, not
    # a single lucky cycle.
    p95 = sorted(beliefs)[max(0, int(0.95 * len(beliefs)) - 1)] if beliefs else 0
    mean_pressure = (statistics.fmean(beliefs) / MAX_HYPOTHESES) if beliefs else 0
    p95_pressure = p95 / MAX_HYPOTHESES
    # Fraction of the tail in which pressure exceeded 1.0.
    sustained = (sum(1 for b in beliefs if b > MAX_HYPOTHESES) / len(beliefs)
                 if beliefs else 0.0)

    mean_ge2 = statistics.fmean(ge2) if ge2 else 0
    max_ge2 = max(ge2) if ge2 else 0
    max_theories = max(theory_counts) if theory_counts else 0
    mean_theories = statistics.fmean(theory_counts) if theory_counts else 0

    d = describe(events)
    return {
        "design": name,
        "events": len(events),
        "distinct_tags": d["distinct_tags"],
        "seconds": round(elapsed, 1),
        "belief_pool_mean": round(statistics.fmean(beliefs), 2) if beliefs else 0,
        "belief_pool_p95": p95,
        "belief_pool_max": max(beliefs) if beliefs else 0,
        "subjects_mean": round(statistics.fmean(subj), 2) if subj else 0,
        "subjects_max": max(subj) if subj else 0,
        "competing_subjects_mean": round(mean_ge2, 2),
        "competing_subjects_max": max_ge2,
        "pressure_mean": round(mean_pressure, 3),
        "pressure_p95": round(p95_pressure, 3),
        "pressure_sustained_frac": round(sustained, 3),
        "theories_mean": round(mean_theories, 3),
        "theories_max": max_theories,
        "questions_max": 0,
        "gates": {
            "G_CS": max_ge2 >= 3 and 5 <= max_ge2 <= 7,
            "G_CS_min3": max_ge2 >= 3,
            "G_P1": p95_pressure > 1.0,
            "G_SUP": p95 > MAX_HYPOTHESES,
            "G_EXP": max_theories < MAX_THEORIES,
        },
        "all_gates_pass": False,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=300)
    ap.add_argument("--out", default=str(REPO / "docs" / "branch_sweep.json"))
    args = ap.parse_args()

    designs = []
    # The current study stream, as the reference point.
    designs.append(("study_stream", list(STUDY_STREAM)))
    # Neutral pseudo-word branch stimuli across the design grid.
    for n in (5, 6, 7):
        for k in (2, 3):
            for reps in (4, 6, 10):
                designs.append((
                    f"neutral_n{n}_k{k}_r{reps}",
                    branch_stream(n_subjects=n, successors_per_subject=k,
                                  repeats=reps),
                ))
    # Shared-successor variant at the derived target.
    designs.append((
        "neutral_n6_k2_r6_shared",
        branch_stream(n_subjects=6, successors_per_subject=2, repeats=6,
                      shared_successors=True),
    ))
    # Semantic vocabulary at the derived target.
    designs.append((
        "semantic_n6_k2_r6",
        branch_stream(n_subjects=6, successors_per_subject=2, repeats=6,
                      subjects=SEMANTIC_SUBJECTS,
                      successors=SEMANTIC_SUCCESSORS),
    ))

    rows = []
    out_path = Path(args.out)

    def flush(rows):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps({
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "cycles": args.cycles,
            "gates": {
                "G_CS": "competing subjects >= 3, reaching 5-7",
                "G_P1": "belief pool p95 > MAX_HYPOTHESES (retention pressure > 1.0)",
                "G_SUP": "belief pool > 15",
                "G_EXP": "theory population never reaches MAX_THEORIES (8)",
            },
            "rows": list(rows),
        }, indent=2), encoding="utf-8")

    for name, events in designs:
        r = evaluate(name, events, args.cycles)
        r["all_gates_pass"] = all(r["gates"].values())
        rows.append(r)
        flush(rows)
        g = r["gates"]
        print(f"{name:<26} ev={r['events']:<5} tags={r['distinct_tags']:<4} "
              f"beliefs={r['belief_pool_mean']:>6.2f}/{r['belief_pool_p95']:<3} "
              f"comp={r['competing_subjects_mean']:>5.2f}/{r['competing_subjects_max']:<3} "
              f"press={r['pressure_p95']:>5.2f} "
              f"T={r['theories_mean']:>5.2f}/{r['theories_max']:<2} "
              f"CS:{'Y' if g['G_CS'] else 'n'} P1:{'Y' if g['G_P1'] else 'n'} "
              f"SUP:{'Y' if g['G_SUP'] else 'n'} EXP:{'Y' if g['G_EXP'] else 'n'}")
        sys.stdout.flush()

    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
