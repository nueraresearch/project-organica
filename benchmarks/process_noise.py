"""
Cross-process noise floor.

`benchmarks/seed_noise.py` runs several seeds inside ONE process and found a
spread of exactly 0. That result is real, but it does not bound the noise of
the campaign, because the campaign runs each colony in its OWN process
(`force_matrix.py --merge` spawns one process per colony). A quantity that is
invariant to the seed *within* a process can still vary *between* processes,
because CPython randomises string hashing per process (PYTHONHASHSEED) unless
it is pinned. Any set or dict whose iteration order depends on a string hash
then yields a different order in a different process, and the engine's
candidate construction walks such collections.

This script runs ONE (colony, seed) and prints a compact metric record as
JSON on stdout. The driver runs it several times with different PYTHONHASHSEED
values and compares the results. That is the noise floor a campaign delta has
to beat.

Usage:
    python benchmarks/process_noise.py --cycles 300 --seed 20261023
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# METRICS as flat scalars so two records can be compared field by field.
SCALARS = [
    ("M1_theory_duty_cycle", "whole_run"),
    ("M2_question_duty_cycle", "whole_run"),
    ("M3_contradiction_density", "mean"),
    ("M3_contradiction_density", "median"),
    ("M3_contradiction_density", "p95"),
    ("M4_contradiction_survival", "rate"),
    ("M5_development_velocity", "new_per_100_cycles"),
    ("M6_lineage_depth", "max_generation"),
    ("M7_mean_hypothesis_lifetime", "mean"),
    ("M8_population_stability", "beliefs"),
    ("M9_cognitive_revolutions", "revolutions"),
]

POPULATIONS = [
    "theories_mean",
    "questions_mean",
    "dreams_mean",
    "experiments_mean",
    "pre_beliefs_mean",
    "pre_ge2_mean",
]


def run_once(colony: str, cycles: int, seed: int) -> dict:
    from organica.branch_streams import (
        NEUTRAL_HUB, NEUTRAL_PETALS, lattice_designs, lattice_stream)
    from organica.memory import MemoryService
    from organica.paths import temp_db
    from organica.streams import EVENTS_PER_CYCLE
    from benchmarks.force_matrix import (
        _series, capture_cycle, colony_class, compute_metrics)

    lattice = lattice_designs(NEUTRAL_HUB, NEUTRAL_PETALS)
    events = lattice_stream(lattice["L1_hub1_t3_disjoint"]["triangles"])

    db = temp_db(f"procnoise_{colony}_{seed}.db")
    if db.exists():
        db.unlink()
    mem = MemoryService(db_path=str(db))
    svc = colony_class(colony)(mem)
    if hasattr(svc, "_rng"):
        svc._rng.seed(seed)
    for text in events:
        mem.store(text, event_type="event", source="seed:bootstrap")
    for i in range(cycles):
        start = (i * EVENTS_PER_CYCLE) % len(events)
        for text in events[start:start + EVENTS_PER_CYCLE]:
            mem.store(text, event_type="event", source=f"cycle:{i}")
        svc.run_sleep_cycle()
        capture_cycle(svc)
    metrics = compute_metrics(svc.rows, svc)
    mem.close()
    db.unlink(missing_ok=True)

    record = {"py_hash_seed": os.environ.get("PYTHONHASHSEED", "<unset>")}
    for key, sub in SCALARS:
        try:
            record[f"{key}.{sub}"] = metrics[key][sub]
        except Exception:
            record[f"{key}.{sub}"] = None
    for key in POPULATIONS:
        try:
            record[f"pop.{key}"] = metrics["_populations"][key]
        except Exception:
            record[f"pop.{key}"] = None

    # The discovery curve, so the floor can be read against the shape of the
    # curve and not only its endpoint.
    try:
        disc = _series(svc.rows).get("discovery", {})
        record["m5_inventory_total"] = metrics[
            "M5_development_velocity"]["inventory_total"]
        record["m5_inventory_per_category"] = metrics[
            "M5_development_velocity"]["inventory_per_category"]
        record["discovery_cumulative_m5"] = disc.get(
            "m5_cycle_cumulative_total", [])
    except Exception:
        pass
    return record


def sweep(cycles: int, colony: str, seed: int, hash_seeds: list[str],
          out: Path, parallel: bool = True) -> None:
    """Run the SAME (colony, seed) in separate processes, each with a
    different PYTHONHASHSEED, and report the spread of every field."""
    import subprocess

    def one(hs: str) -> dict:
        env = dict(os.environ)
        env["PYTHONHASHSEED"] = hs
        cmd = [sys.executable, str(REPO / "benchmarks" / "process_noise.py"),
               "--cycles", str(cycles), "--colony", colony, "--seed", str(seed)]
        proc = subprocess.run(cmd, cwd=str(REPO), env=env,
                              capture_output=True, text=True)
        if proc.returncode != 0:
            print(proc.stdout[-2000:])
            print(proc.stderr[-4000:])
            raise SystemExit(f"run failed for PYTHONHASHSEED={hs}")
        return json.loads(proc.stdout.strip().splitlines()[-1])

    records = []
    if parallel and len(hash_seeds) > 1:
        from concurrent.futures import ThreadPoolExecutor
        print(f"  {len(hash_seeds)} processes in parallel "
              f"({cycles} cycles each) ...", flush=True)
        with ThreadPoolExecutor(max_workers=len(hash_seeds)) as pool:
            for rec in pool.map(one, hash_seeds):
                records.append(rec)
                print(f"  PYTHONHASHSEED={rec['py_hash_seed']} done", flush=True)
    else:
        for hs in hash_seeds:
            print(f"  running with PYTHONHASHSEED={hs} ...", flush=True)
            records.append(one(hs))

    fields = [k for k in records[0] if k != "py_hash_seed"]
    table = []
    for f in fields:
        vals = [r.get(f) for r in records]
        nums = [v for v in vals if isinstance(v, (int, float))]
        if len(nums) != len(vals):
            table.append({"field": f, "values": vals, "spread": None,
                          "relative_spread": None, "varies": False})
            continue
        lo, hi = min(nums), max(nums)
        mid = sum(nums) / len(nums)
        rel = (hi - lo) / abs(mid) if mid else 0.0
        table.append({"field": f, "values": vals, "spread": hi - lo,
                      "relative_spread": round(rel, 6), "varies": hi != lo})

    varying = [t for t in table if t["varies"]]
    print()
    print("=" * 78)
    print(f"PROCESS-LEVEL NOISE FLOOR -- {colony}, {cycles} cycles, "
          f"seed {seed}, {len(records)} processes")
    print("=" * 78)
    for t in table:
        flag = "VARIES" if t["varies"] else "  same"
        sp = t["spread"]
        sp_s = f"{sp:.6g}" if isinstance(sp, (int, float)) else "-"
        rel_s = (f"{t['relative_spread']:.6g}"
                 if isinstance(t["relative_spread"], (int, float)) else "-")
        print(f"  {flag}  {t['field']:<42} spread={sp_s:<12} rel={rel_s:<10} "
              f"values={t['values']}")
    print()
    print(f"  {len(varying)} of {len(table)} fields vary between processes.")

    # The scale-invariant form of the floor. M5 is a RATE (new items per
    # 100 cycles), so its numeric spread shrinks as the run gets longer even
    # when the underlying count does not. The count is the honest bound, and
    # it is what a delta must be compared against at any run length.
    m5 = next((t for t in table
               if t["field"] == "M5_development_velocity.new_per_100_cycles"),
              None)
    items = None
    if m5 and m5["varies"]:
        counts = [v * cycles / 100.0 for v in m5["values"]]
        items = {
            "new_items_per_run": [round(c, 4) for c in counts],
            "item_spread": round(max(counts) - min(counts), 4),
            "rate_spread": m5["spread"],
            "note": ("M5 is a rate. The item count is the scale-invariant "
                     "form of the floor and is the number a delta must beat."),
        }
        print()
        print("  M5 in WHOLE NEW ITEMS over the run (scale-invariant):")
        print(f"    {items['new_items_per_run']}  item spread = "
              f"{items['item_spread']}")

    out.write_text(json.dumps({
        "colony": colony,
        "cycles": cycles,
        "seed": seed,
        "hash_seeds": hash_seeds,
        "records": records,
        "table": table,
        "varying_fields": [t["field"] for t in varying],
        "m5_in_items": items,
    }, indent=2), encoding="utf-8")
    print(f"\nwrote {out}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=300)
    ap.add_argument("--colony", default="FULL")
    ap.add_argument("--seed", type=int, default=20261023)
    ap.add_argument("--sweep", action="store_true",
                    help="run the same seed in several processes with "
                         "different PYTHONHASHSEED and report the spread")
    ap.add_argument("--hash-seeds", nargs="*",
                    default=["0", "1", "2", "3", "4", "5"])
    ap.add_argument("--no-parallel", action="store_true",
                    help="run the processes one at a time")
    ap.add_argument("--out", default=str(REPO / "docs" / "process_noise.json"))
    args = ap.parse_args()
    if args.sweep:
        sweep(args.cycles, args.colony, args.seed, args.hash_seeds,
              Path(args.out), parallel=not args.no_parallel)
    else:
        print(json.dumps(run_once(args.colony, args.cycles, args.seed)))


if __name__ == "__main__":
    main()
