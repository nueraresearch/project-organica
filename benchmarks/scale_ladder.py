"""
The H24 ladder: does the inventory grow with the world's information content?

H24: *Organica's apparent developmental plateau is primarily constrained by
environmental information content rather than by architectural inability to
reorganise.*

The 300-cycle pilot (Rungs 0-2, uniform frequency) produced an inversion:
more world, less development (91 -> 66 -> 56 inventory). The mechanism
hypothesis (FACTS-SHEET S.LM1): frequency dilution starves the prediction
window of complete 3-cycles.

This script now supports two rung families:

  Uniform rungs  (0, 1, 2, 3)  -- the pilot design; all triangles at equal
                                   frequency. Preserved for the dilution-
                                   mechanism test (raise MAX_PREDICTIONS to
                                   40, does Rung-1 recover?).

  Scaffold rungs (1s, 2s, 3s)  -- the revised design: a 3-triangle core
                                   repeating at high frequency, plus one fresh
                                   triangle introduced every N cycles. Tests
                                   whether Organica can assimilate novelty
                                   without losing its developmental scaffold.

The decision rule is pre-registered in docs/WORLD-SCALE-PREREGISTRATION.md:

  inventory grows with rung      -> H24 supported
  inventory flat across rungs    -> H24 falsified (the ceiling is architectural)

Usage:
    # Pilot (uniform frequency, already measured):
    python benchmarks/scale_ladder.py --cycles 300 --rungs 0 1 2

    # Scaffold experiment (revised H24 test):
    python benchmarks/scale_ladder.py --cycles 300 --rungs 0 1s 2s 3s \
        --out docs/scale_ladder_scaffold.json

    # Full run:
    python benchmarks/scale_ladder.py --cycles 3000 --rungs 0 1s 2s 3s \
        --out docs/scale_ladder_scaffold_full.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.scale_streams import (  # noqa: E402
    rung_for_run, scale_designs, scale_stream, scaffold_stream,
    burst_stream, triangle_events)


def run_rung(rung: str, cycles: int, seed: int, colony: str = "FULL") -> dict:
    from benchmarks.force_matrix import (
        _series, capture_cycle, colony_class, compute_metrics)
    from organica.memory import MemoryService
    from organica.paths import temp_db
    from organica.streams import EVENTS_PER_CYCLE

    designs = scale_designs()
    design  = designs[f"rung{rung}"]
    mode    = design["mode"]

    db = temp_db(f"ladder_rung{rung}_{colony}.db")
    if db.exists():
        db.unlink()
    mem = MemoryService(db_path=str(db))
    svc = colony_class(colony)(mem)
    if hasattr(svc, "_rng"):
        svc._rng.seed(seed)

    if mode == "burst":
        core_triangles = design["core_triangles"]
        burst_every = design.get("burst_every", 30)
        burst_len = design.get("burst_len", 8)
        core_evs = triangle_events(core_triangles)
        for text in core_evs:
            mem.store(text, event_type="event", source="seed:bootstrap")
        full_stream = burst_stream(core_triangles, cycles, burst_every, burst_len, EVENTS_PER_CYCLE)
        for i in range(cycles):
            cycle_evs = full_stream[i * EVENTS_PER_CYCLE : (i + 1) * EVENTS_PER_CYCLE]
            for text in cycle_evs:
                mem.store(text, event_type="event", source=f"cycle:{i}")
            svc.run_sleep_cycle()
            capture_cycle(svc)
        # The stream introduces at positive cycle indices (every, 2*every, ...).
        # A horizon ending exactly on a multiple does not include that cycle.
        n_novel = (cycles - 1) // burst_every if cycles > 0 else 0
        stimulus_info = {
            "core_triangles": len(core_triangles),
            "burst_every_cycles": burst_every,
            "burst_len_cycles": burst_len,
            "novelties_introduced": n_novel,
            "total_distinct_triangles": len(core_triangles) + n_novel,
            "distinct_event_strings": len(set(full_stream)),
            "distinct_words": len({w for e in full_stream for w in e.split()}),
            "experience_period_cycles": None,
            "never_repeats": True,
        }
    elif mode == "scaffold":
        # Bootstrap with the repeating core only (not the whole stream).
        # Events are then delivered cycle-by-cycle from the pre-built stream.
        core_triangles = design["core_triangles"]
        novelty_every  = design["novelty_every"]
        core_evs       = triangle_events(core_triangles)

        for text in core_evs:
            mem.store(text, event_type="event", source="seed:bootstrap")

        full_stream = scaffold_stream(
            core_triangles, cycles, EVENTS_PER_CYCLE, novelty_every)

        for i in range(cycles):
            cycle_evs = full_stream[i * EVENTS_PER_CYCLE:
                                    (i + 1) * EVENTS_PER_CYCLE]
            for text in cycle_evs:
                mem.store(text, event_type="event", source=f"cycle:{i}")
            svc.run_sleep_cycle()
            capture_cycle(svc)

        # The first novelty arrives at novelty_every, not cycle zero.
        n_novel = (cycles - 1) // novelty_every if cycles > 0 else 0
        stimulus_info = {
            "core_triangles": len(core_triangles),
            "novelty_every_cycles": novelty_every,
            "novelties_introduced": n_novel,
            "total_distinct_triangles": len(core_triangles) + n_novel,
            "distinct_event_strings": len(set(full_stream)),
            "distinct_words": len({w for e in full_stream for w in e.split()}),
            "experience_period_cycles": None,
            "never_repeats": True,
        }

    else:
        # Block / open mode (uniform frequency, original pilot)
        triangles = rung_for_run(design, cycles, EVENTS_PER_CYCLE)
        events    = scale_stream(triangles, mode, design.get("block_repeat", 1))

        for text in events:
            mem.store(text, event_type="event", source="seed:bootstrap")

        for i in range(cycles):
            start = (i * EVENTS_PER_CYCLE) % len(events)
            for text in events[start:start + EVENTS_PER_CYCLE]:
                mem.store(text, event_type="event", source=f"cycle:{i}")
            svc.run_sleep_cycle()
            capture_cycle(svc)

        consumed = []
        for i in range(400):
            start = (i * EVENTS_PER_CYCLE) % len(events)
            consumed.append(tuple(events[start:start + EVENTS_PER_CYCLE]))
        period = None
        for p in range(1, 200):
            if all(consumed[i] == consumed[i + p]
                   for i in range(len(consumed) - p)):
                period = p
                break

        stimulus_info = {
            "triangles": len(triangles),
            "distinct_event_strings": len(set(events)),
            "distinct_words": len({w for e in events for w in e.split()}),
            "experience_period_cycles": period,
            "never_repeats": period is None or period >= 200,
        }

    metrics = compute_metrics(svc.rows, svc)
    series  = _series(svc.rows)
    mem.close()
    db.unlink(missing_ok=True)

    disc  = series.get("discovery", {})
    cum   = disc.get("m5_cycle_cumulative_total") or []
    m5    = metrics["M5_development_velocity"]
    total = cum[-1] if cum else 0
    pops  = metrics.get("_populations", {})
    inv   = m5.get("inventory_total")

    n_tri = (stimulus_info.get("total_distinct_triangles")
             or stimulus_info.get("triangles") or 1)
    efficiency = round(inv / n_tri, 2) if inv and n_tri else None

    return {
        "rung": rung,
        "name": design["name"],
        "description": design["description"],
        "mode": mode,
        "cycles": cycles,
        "colony": colony,
        "seed": seed,
        "stimulus": stimulus_info,
        "inventory": {
            "m5_total": inv,
            "per_category": m5.get("inventory_per_category"),
            "rate_per_100_cycles": m5.get("new_per_100_cycles"),
            "new_in_last_100_cycles": m5.get("last_100_new_total"),
            "inventory_per_triangle": efficiency,
        },
        "discovery_curve": {
            "cumulative": cum,
            "cycle_95pct": next((i for i, v in enumerate(cum)
                                 if v >= 0.95 * total), None) if total else None,
            "cycle_99pct": next((i for i, v in enumerate(cum)
                                 if v >= 0.99 * total), None) if total else None,
        },
        "populations": {
            "theories_mean":    pops.get("theories_mean"),
            "questions_mean":   pops.get("questions_mean"),
            "dreams_mean":      pops.get("dreams_mean"),
            "experiments_mean": pops.get("experiments_mean"),
            "pre_beliefs_mean": pops.get("pre_beliefs_mean"),
            "pre_ge2_mean":     pops.get("pre_ge2_mean"),
        },
        "metrics": {
            "M1_theory_duty_cycle":        metrics["M1_theory_duty_cycle"]["whole_run"],
            "M2_question_duty_cycle":      metrics["M2_question_duty_cycle"]["whole_run"],
            "M3_contradiction_density":    metrics["M3_contradiction_density"]["mean"],
            "M4_contradiction_survival":   metrics["M4_contradiction_survival"]["rate"],
            "M5_development_velocity":     m5["new_per_100_cycles"],
            "M6_lineage_depth":            metrics["M6_lineage_depth"]["max_generation"],
            "M7_mean_hypothesis_lifetime": metrics["M7_mean_hypothesis_lifetime"]["mean"],
            "M8_population_stability":     metrics["M8_population_stability"]["beliefs"],
            "M9_cognitive_revolutions":    metrics["M9_cognitive_revolutions"]["revolutions"],
        },
        "gates": {
            "G-CS competing subjects": pops.get("pre_ge2_mean"),
            "G-SUP belief supply":     pops.get("pre_beliefs_mean"),
            "G-EXP theories":          pops.get("theories_mean"),
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=3000)
    ap.add_argument("--seed",   type=int, default=20261023)
    ap.add_argument("--rungs",  nargs="*", default=["0", "1s", "2s", "3s"])
    ap.add_argument("--colony", default="FULL")
    ap.add_argument("--out",
                    default=str(REPO / "docs" / "scale_ladder.json"))
    args = ap.parse_args()

    results = []
    for rung in args.rungs:
        rung = str(rung)
        print(f"rung {rung} ...", flush=True)
        r = run_rung(rung, args.cycles, args.seed, args.colony)
        results.append(r)
        inv  = r["inventory"]
        pops = r["populations"]
        print(f"  inventory={inv['m5_total']} "
              f"(inv/tri={inv.get('inventory_per_triangle','?')}) "
              f"pre_ge2={pops['pre_ge2_mean']} "
              f"theories={pops['theories_mean']} "
              f"last100={inv['new_in_last_100_cycles']}", flush=True)

    print()
    print("=" * 100)
    print(f"H24 LADDER -- {args.cycles} cycles/colony, colony {args.colony}")
    print("=" * 100)
    print(f"{'rung':<7}{'mode':<12}{'inv':<8}{'inv/tri':<10}{'last100':<9}"
          f"{'pre_ge2':<9}{'theories':<10}{'questions':<11}{'rev':<5}")
    for r in results:
        inv  = r["inventory"]
        pops = r["populations"]
        print(f"{r['rung']:<7}{r['mode']:<12}"
              f"{inv['m5_total']:<8}"
              f"{str(inv.get('inventory_per_triangle','?')):<10}"
              f"{inv['new_in_last_100_cycles']:<9}"
              f"{pops['pre_ge2_mean']:<9}{pops['theories_mean']:<10}"
              f"{pops['questions_mean']:<11}"
              f"{r['metrics']['M9_cognitive_revolutions']:<5}")

    inventories = [r["inventory"]["m5_total"] for r in results]
    grows = len(inventories) > 1 and inventories[-1] > inventories[0]
    flat  = len(inventories) > 1 and inventories[-1] == inventories[0]
    print()
    if grows:
        print(f"  INVENTORY GROWS: {inventories[0]} -> {inventories[-1]}. "
              f"H24 CONSISTENT: the plateau was an environmental artefact.")
    elif flat:
        print(f"  INVENTORY IS FLAT: {inventories}. H24 FALSIFIED: "
              f"the ceiling is architectural.")
    else:
        print(f"  INVENTORY: {inventories}. Mixed -- read the curve, "
              f"not the endpoint.")

    Path(args.out).write_text(json.dumps({
        "cycles":      args.cycles,
        "seed":        args.seed,
        "colony":      args.colony,
        "results":     results,
        "inventories": inventories,
        "h24_reading": ("consistent" if grows else
                        "falsified"  if flat  else "mixed"),
    }, indent=2), encoding="utf-8")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
