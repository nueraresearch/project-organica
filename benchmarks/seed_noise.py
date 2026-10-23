"""
Seed-noise floor.

The pre-registration commits to one seed per colony and to the rule that
"per-metric deltas smaller than seed noise are reported as *not
interpretable*, not as findings". That rule is only usable if the noise
is measured rather than guessed.

This runs the SAME colony several times with different seeds and reports,
for every metric, the spread across seeds. A campaign delta smaller than
that spread is not a finding.

Usage:
    python benchmarks/seed_noise.py --cycles 300
Writes docs/seed_noise.json
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks.force_matrix import (                # noqa: E402
    COLONIES, compute_metrics, _series)

METRICS = [
    ("M1", "theory duty cycle", lambda m: m["M1_theory_duty_cycle"]["whole_run"]),
    ("M2", "question duty cycle", lambda m: m["M2_question_duty_cycle"]["whole_run"]),
    ("M3", "contradiction density", lambda m: m["M3_contradiction_density"]["mean"]),
    ("M4", "contradiction survival", lambda m: m["M4_contradiction_survival"]["rate"]),
    ("M5", "development velocity", lambda m: m["M5_development_velocity"]["new_per_100_cycles"]),
    ("M6", "lineage depth", lambda m: m["M6_lineage_depth"]["max_generation"]),
    ("M7", "mean belief lifetime", lambda m: m["M7_mean_hypothesis_lifetime"]["mean"]),
    ("M8", "population stability", lambda m: m["M8_population_stability"]["beliefs"]),
    ("M9", "cognitive revolutions", lambda m: m["M9_cognitive_revolutions"]["revolutions"]),
]

POPS = [
    ("theories", "theories_mean"),
    ("questions", "questions_mean"),
    ("dreams", "dreams_mean"),
    ("experiments", "experiments_mean"),
    ("pre_beliefs", "pre_beliefs_mean"),
    ("pre_ge2", "pre_ge2_mean"),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=300)
    ap.add_argument("--colony", default="FULL")
    ap.add_argument("--seeds", nargs="*", type=int,
                    default=[20261023, 20261024, 20261025])
    ap.add_argument("--out", default=str(REPO / "docs" / "seed_noise.json"))
    args = ap.parse_args()

    from organica.branch_streams import (            # noqa: E402
        NEUTRAL_HUB, NEUTRAL_PETALS, lattice_designs, lattice_stream)
    from organica.memory import MemoryService        # noqa: E402
    from organica.streams import EVENTS_PER_CYCLE    # noqa: E402
    from organica.paths import temp_db               # noqa: E402
    from benchmarks.force_matrix import (            # noqa: E402
        Instrumented, capture_cycle, colony_class)

    lattice = lattice_designs(NEUTRAL_HUB, NEUTRAL_PETALS)
    events = lattice_stream(lattice["L1_hub1_t3_disjoint"]["triangles"])

    per_seed = []
    for seed in args.seeds:
        db = temp_db(f"seednoise_{args.colony}_{seed}.db")
        if db.exists():
            db.unlink()
        mem = MemoryService(db_path=str(db))
        svc = colony_class(args.colony)(mem)
        if hasattr(svc, "_rng"):
            svc._rng.seed(seed)
        for text in events:
            mem.store(text, event_type="event", source="seed:bootstrap")
        for i in range(args.cycles):
            start = (i * EVENTS_PER_CYCLE) % len(events)
            for text in events[start:start + EVENTS_PER_CYCLE]:
                mem.store(text, event_type="event", source=f"cycle:{i}")
            svc.run_sleep_cycle()
            capture_cycle(svc)
        metrics = compute_metrics(svc.rows, svc)
        mem.close()
        db.unlink(missing_ok=True)
        per_seed.append({"seed": seed, "metrics": metrics})
        print(f"  seed {seed} done")

    table = []
    for code, name, get in METRICS:
        vals = []
        for ps in per_seed:
            v = get(ps["metrics"])
            vals.append(v if isinstance(v, (int, float)) else 0)
        lo, hi = min(vals), max(vals)
        mid = statistics.fmean(vals)
        rel = (hi - lo) / abs(mid) if mid else 0.0
        table.append({"metric": code, "name": name, "values": vals,
                      "spread": hi - lo, "relative_spread": round(rel, 5)})

    pop_table = []
    for name, key in POPS:
        vals = [ps["metrics"]["_populations"][key] for ps in per_seed]
        lo, hi = min(vals), max(vals)
        mid = statistics.fmean(vals)
        pop_table.append({"population": name, "values": vals, "spread": hi - lo,
                          "relative_spread": round((hi - lo) / abs(mid), 5) if mid else 0.0})

    print()
    print("=" * 78)
    print(f"SEED-NOISE FLOOR -- {args.colony}, {args.cycles} cycles, "
          f"seeds {args.seeds}")
    print("=" * 78)
    for t in table:
        print(f"  {t['metric']:<4} {t['name']:<26} values={t['values']} "
              f"spread={t['spread']:.6g} rel={t['relative_spread']}")
    print()
    print("  populations:")
    for t in pop_table:
        print(f"  {t['population']:<12} values={t['values']} "
              f"spread={t['spread']:.6g} rel={t['relative_spread']}")

    Path(args.out).write_text(json.dumps({
        "colony": args.colony,
        "cycles": args.cycles,
        "seeds": args.seeds,
        "metrics": table,
        "populations": pop_table,
    }, indent=2), encoding="utf-8")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
