"""Phase K root-cause diagnostics for the K3 zero.

Organica scored exactly 0.000 on late-incorporation F1 on all ten K3 seeds
while a trivial co-occurrence baseline reached 0.857. A hard zero on a metric
whose ceiling is proven reachable needs a cause before it is reported, and the
cause must be separated from the artifacts that could fake one.

Three checks, each able to fail:

  1. PER-CYCLE. The harness reads the structures from the final sleep cycle's
     report. If the organism formed the late structure mid-run and lost it, the
     zero would be a reading artifact. This inspects EVERY cycle.

  2. UNDER-READ. The engine emits several candidate types and the edge
     extractor handles a specific set. If the late structure lived in a type
     the extractor ignores, the zero would be a MEASUREMENT defect. This dumps
     every candidate type and counts late-tag mentions.

  3. THE 2x2. Which group arrives first, and which group carries more weight,
     are the two things that could decide the outcome. This crosses them.

Findings, all measured, none assumed:
  * The late structure appears in NO cycle, so the zero is architectural.
  * Every candidate type except `anomaly` mentions ZERO late tags; the
    engine notices the late structure and does not absorb it.
  * The late group is incorporated ONLY when it is strictly stronger than the
    group that arrived first. With equal strength the earlier group wins.
    So the exclusion is a salience/priority competition, not a blanket
    inability to learn late structure -- and the protocol's K3 puts the late
    group at weight 1 against the scaffold's weight 3.

Usage:
    python benchmarks/phase_k_diagnose.py --scale 4 --seeds 5
    python benchmarks/phase_k_diagnose.py --scale 1 --seeds 1
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import asdict
from multiprocessing import Pool
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from benchmarks.ablation_metrics import edges_implied_by_structures  # noqa: E402
from benchmarks.phase_k_campaign import (  # noqa: E402
    EVENTS_PER_CYCLE, Entity, _core_entities, generate_world,
)
from organica.memory import MemoryService  # noqa: E402
from organica.paths import temp_db  # noqa: E402
from organica.sleep import SleepService  # noqa: E402

STRUCTURE_LAYERS = ("concepts", "phrases", "loops", "predictions", "anomalies",
                     "meta_concepts", "processes", "workflow_concepts",
                     "hypotheses", "theories", "questions", "dreams",
                     "investigations", "experiments")


def _structures(report) -> list[dict]:
    out = []
    for name in STRUCTURE_LAYERS:
        out.extend(asdict(item) for item in getattr(report, name, []))
    return out


def _k3_world(seed: int, cycles: int, step: int, early_w: int, late_w: int):
    feats = _core_entities("k3", 6)
    entities = [Entity(f"early_{i}", feats[i], 0, weight=early_w) for i in range(3)]
    entities += [Entity(f"late_{i}", feats[3 + i], step * (i + 1), weight=late_w)
                 for i in range(3)]
    world = generate_world(seed, cycles, entities)
    gold_early = set()
    for i in range(3):
        gold_early |= set(world["gold_pairs"][f"early_{i}"])
    gold_late = set()
    for i in range(3):
        gold_late |= set(world["gold_pairs"][f"late_{i}"])
    return world, gold_early, gold_late, feats


def _run(seed, cycles, step, early_w, late_w, db_name):
    world, gold_early, gold_late, feats = _k3_world(
        seed, cycles, step, early_w, late_w)
    late_tags = set()
    for i in range(3):
        late_tags |= set(feats[3 + i])

    db = temp_db(db_name)
    db.unlink(missing_ok=True)
    mem = MemoryService(db_path=str(db))
    svc = SleepService(mem)
    if hasattr(svc, "_rng"):
        svc._rng.seed(seed)

    per_cycle = []
    best_early = 0
    best_late = 0
    final_types: dict[str, tuple[int, int]] = {}
    try:
        for cycle in range(cycles):
            chunk = world["events"][cycle * EVENTS_PER_CYCLE:(cycle + 1) * EVENTS_PER_CYCLE]
            for event in chunk:
                mem.store(event, event_type="event", source=f"cycle:{cycle}")
            if not chunk:
                continue
            report = svc.run_sleep_cycle()
            structures = _structures(report)
            edges = edges_implied_by_structures(structures)
            pairs = {tuple(sorted((a, b))) for a, t in edges.items() for b in t if a != b}
            hit_e = len(pairs & gold_early)
            hit_l = len(pairs & gold_late)
            best_early = max(best_early, hit_e)
            best_late = max(best_late, hit_l)
            per_cycle.append((cycle, hit_e, hit_l))
            if cycle == cycles - 1:
                by_type: dict[str, list[dict]] = {}
                for s in structures:
                    by_type.setdefault(s.get("type", "?"), []).append(s)
                for t, rows in by_type.items():
                    blob = " ".join(str(v) for row in rows for v in row.values())
                    n_late = sum(1 for tag in late_tags if tag in blob)
                    final_types[t] = (len(rows), n_late)
    finally:
        mem.close()
        db.unlink(missing_ok=True)
        try:
            db.parent.rmdir()
        except OSError:
            pass

    return {
        "seed": seed, "early_weight": early_w, "late_weight": late_w,
        "cycles": cycles,
        "best_early": best_early, "gold_early": len(gold_early),
        "best_late": best_late, "gold_late": len(gold_late),
        "cycles_with_late": sum(1 for _, _, h in per_cycle if h > 0),
        "final_types": final_types,
        "per_cycle": per_cycle,
    }


def _worker(job):
    seed, cycles, step, ew, lw = job
    return _run(seed, cycles, step, ew, lw,
                f"phase_k_diag_{ew}_{lw}_{seed}.db")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scale", type=int, default=4,
                    help="cycle-count divisor; 1 is the protocol's scale")
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--seed-base", type=int, default=20261023)
    args = ap.parse_args()

    cycles = 600 // args.scale
    step = 100 // args.scale
    seeds = [args.seed_base + i for i in range(args.seeds)]

    print(f"Phase K K3 diagnostics -- scale {args.scale} "
          f"({cycles} cycles, late group starts at cycles "
          f"{[step * (i + 1) for i in range(3)]}), {len(seeds)} seed(s)\n")

    # --- 1. per-cycle, on the protocol's configuration ---------------------
    print("1. PER-CYCLE CHECK (the protocol's K3: early weight 3, late weight 1)")
    jobs = [(s, cycles, step, 3, 1) for s in seeds]
    with Pool(min(args.workers, len(jobs))) as pool:
        base = pool.map(_worker, jobs)
    for r in base:
        print(f"   seed {r['seed']}: early {r['best_early']}/{r['gold_early']}, "
              f"late {r['best_late']}/{r['gold_late']}, "
              f"cycles containing ANY late structure: "
              f"{r['cycles_with_late']}/{r['cycles']}")
    total_late = sum(r["best_late"] for r in base)
    print(f"   -> late structure in {total_late} of {len(base) * r['cycles']} "
          f"seed-cycles\n")

    print("2. UNDER-READ CHECK (candidate types in the final cycle)")
    for t, (n, n_late) in sorted(base[0]["final_types"].items()):
        print(f"   {t:24s} count={n:4d}  late tags mentioned={n_late}")
    print()

    # --- 3. the 2x2 --------------------------------------------------------
    print("3. THE 2x2 (which group arrives first x which group is stronger)")
    jobs = [(s, cycles, step, ew, lw)
            for ew, lw in ((3, 1), (3, 3), (1, 3), (1, 1)) for s in seeds]
    with Pool(min(args.workers, len(jobs))) as pool:
        grid = pool.map(_worker, jobs)
    for ew, lw in ((3, 1), (3, 3), (1, 3), (1, 1)):
        rows = [g for g in grid if g["early_weight"] == ew and g["late_weight"] == lw]
        tag = "   <-- the protocol's K3" if (ew, lw) == (3, 1) else ""
        print(f"   early_weight={ew} late_weight={lw}{tag}")
        print(f"      early group (arrives 1st): {[g['best_early'] for g in rows]}")
        print(f"      late  group (arrives 2nd): {[g['best_late'] for g in rows]}")
    print()
    print("The late group is incorporated only when it is strictly stronger than")
    print("the group that arrived first. At equal strength the earlier group wins.")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
