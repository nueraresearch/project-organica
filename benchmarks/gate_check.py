"""
Gate check — the official re-run of G-P1 and its siblings on the FIXED
substrate.

This is the artifact that closes (or refuses to close) the launch gates
for the Ablation Matrix V2. It runs against the real `MemoryService`,
with the tag-frequency counter scoped to world events the same way the
co-occurrence and temporal graphs are (research journal §21).

The gates, evaluated on the PRE-retention belief pool so that they do not
depend on the retention arm under test:

  G-CS   >= 3 subjects hold >= 2 beliefs, reaching 5-7
  G-P1   belief pool p95 > MAX_HYPOTHESES (15)   -- retention pressure > 1.0
  G-SUP  belief pool > 15
  G-EXP  max(theories) < MAX_THEORIES (8)       -- theory layer unsaturated
  G-SUS  all of the above hold simultaneously in >= 60% of the tail cycles

Usage:
    python benchmarks/gate_check.py --cycles 300
Writes docs/gate_check.json
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
    NEUTRAL_HUB, NEUTRAL_PETALS, branch_stream, lattice_designs, lattice_stream)
from organica.memory import MemoryService            # noqa: E402
from organica.sleep import SleepService              # noqa: E402
from organica.streams import EVENTS_PER_CYCLE, STUDY_STREAM  # noqa: E402
from organica.paths import temp_db                   # noqa: E402

MAX_THEORIES = SleepService.MAX_THEORIES
MAX_HYPOTHESES = SleepService.MAX_HYPOTHESES
SUSTAIN_FLOOR = 0.60


class Instrumented(SleepService):
    """Records the pre-retention and post-retention belief structure."""

    def __init__(self, memory):
        super().__init__(memory)
        self.rows = []

    def _retain_hypotheses(self, beliefs, info, temporal):
        pre = Counter(h.subject for h in beliefs)
        kept = super()._retain_hypotheses(beliefs, info, temporal)
        post = Counter(h.subject for h in kept)
        self.rows.append({
            "pre_beliefs": len(beliefs),
            "pre_subjects": len(pre),
            "pre_ge2": sum(1 for c in pre.values() if c >= 2),
            "post_beliefs": len(kept),
            "post_ge2": sum(1 for c in post.values() if c >= 2),
        })
        return kept


def evaluate(name: str, events: list[str], cycles: int, note: str) -> dict:
    db = temp_db(f"gate_{name}.db")
    if db.exists():
        db.unlink()
    mem = MemoryService(db_path=str(db))
    svc = Instrumented(mem)

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
    tail = rows[len(rows) // 2:] or rows

    def vals(key):
        return [r[key] for r in tail]

    beliefs = vals("pre_beliefs")
    ge2 = vals("pre_ge2")
    subjects = vals("pre_subjects")
    post_ge2 = vals("post_ge2")

    p95 = sorted(beliefs)[max(0, int(0.95 * len(beliefs)) - 1)] if beliefs else 0
    ge2_max = max(ge2) if ge2 else 0
    subjects_max = max(subjects) if subjects else 0
    theories_max = max(theory_counts) if theory_counts else 0

    # G-SUS: every gate holds SIMULTANEOUSLY in this cycle.
    # G-EXP is checked on the OBSERVED theory count, which is what the
    # pre-registration says -- not on the number of distinct belief
    # subjects. A subject holding a single belief never becomes a theory,
    # so a design may legitimately carry more subjects than MAX_THEORIES
    # while its theory population stays well under the cap. (An earlier
    # version of this harness used the subject count as the proxy and
    # wrongly failed a design whose theory population was only 6.)
    simultaneous = 0
    tail_theories = theory_counts[len(rows) // 2:] or theory_counts
    for r, t in zip(tail, tail_theories):
        if (r["pre_beliefs"] > MAX_HYPOTHESES
                and r["pre_ge2"] >= 3
                and t < MAX_THEORIES):
            simultaneous += 1
    sustained = simultaneous / len(tail) if tail else 0.0
    zero = sum(1 for b in beliefs if b == 0)

    gates = {
        "G_CS": ge2_max >= 3 and 5 <= ge2_max <= 7,
        "G_CS_min3": ge2_max >= 3,
        "G_P1": p95 > MAX_HYPOTHESES,
        "G_SUP": p95 > MAX_HYPOTHESES,
        "G_EXP": theories_max < MAX_THEORIES,
        "G_SUS": sustained >= SUSTAIN_FLOOR,
    }
    gates["ALL"] = all(gates.values())

    return {
        "design": name,
        "note": note,
        "events": len(events),
        "cycles": cycles,
        "seconds": round(elapsed, 1),
        "pre_beliefs_mean": round(statistics.fmean(beliefs), 3) if beliefs else 0,
        "pre_beliefs_p95": p95,
        "pre_beliefs_max": max(beliefs) if beliefs else 0,
        "pre_subjects_max": subjects_max,
        "pre_ge2_mean": round(statistics.fmean(ge2), 3) if ge2 else 0,
        "pre_ge2_max": ge2_max,
        "post_ge2_mean": round(statistics.fmean(post_ge2), 3) if post_ge2 else 0,
        "post_ge2_max": max(post_ge2) if post_ge2 else 0,
        "theories_mean": round(statistics.fmean(theory_counts), 3) if theory_counts else 0,
        "theories_max": theories_max,
        "pressure_mean": round((statistics.fmean(beliefs) if beliefs else 0) / MAX_HYPOTHESES, 3),
        "pressure_p95": round(p95 / MAX_HYPOTHESES, 3),
        "sustained_frac": round(sustained, 3),
        "zero_belief_frac": round(zero / len(tail), 3) if tail else 0,
        "gates": gates,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=300)
    ap.add_argument("--out", default=str(REPO / "docs" / "gate_check.json"))
    args = ap.parse_args()

    lattice = lattice_designs(NEUTRAL_HUB, NEUTRAL_PETALS)
    stimuli = [
        ("study_stream", list(STUDY_STREAM),
         "control: the stream the study has been running on"),
        ("branch_r4", branch_stream(n_subjects=5, successors_per_subject=2, repeats=4),
         "the first branch generator; measured as intermittent before the scope fix"),
        ("lattice_L1", lattice_stream(lattice["L1_hub1_t3_disjoint"]["triangles"]),
         "three disjoint triangles: 7 subjects x 2-3 beliefs, derived from the mechanism"),
        ("lattice_L3", lattice_stream(lattice["L3_hub1_t3_mixed"]["triangles"]),
         "three triangles with one shared petal: 6 subjects"),
    ]

    rows = []
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    for name, events, note in stimuli:
        r = evaluate(name, events, args.cycles, note)
        rows.append(r)
        out_path.write_text(json.dumps({
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "cycles": args.cycles,
            "sustain_floor": SUSTAIN_FLOOR,
            "gate_population": "PRE-retention belief pool (policy-independent)",
            "substrate": "tag-frequency counter scoped to world events",
            "rows": list(rows),
        }, indent=2), encoding="utf-8")
        g = r["gates"]
        print(f"{name:<14} bel={r['pre_beliefs_mean']:>6.2f}/{r['pre_beliefs_p95']:<3} "
              f"ge2={r['pre_ge2_mean']:>5.2f}/{r['pre_ge2_max']:<2} "
              f"post={r['post_ge2_max']:<2} T={r['theories_mean']:>5.2f}/{r['theories_max']:<2} "
              f"sus={r['sustained_frac']:>5.2f} zero={r['zero_belief_frac']:>5.2f} "
              f"CS:{'Y' if g['G_CS'] else 'n'} P1:{'Y' if g['G_P1'] else 'n'} "
              f"SUP:{'Y' if g['G_SUP'] else 'n'} EXP:{'Y' if g['G_EXP'] else 'n'} "
              f"SUS:{'Y' if g['G_SUS'] else 'n'} ALL:{'Y' if g['ALL'] else 'n'}")
        sys.stdout.flush()

    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
