"""Seed-exchangeability audit for the Phase L primary axis.

WHY THIS EXISTS

The raise-n run (n=30) did not merely add precision to the n=10 curve. The
twenty added seeds moved it: at 6:1 the original ten seeds gave
DI = 0.750 and the added twenty gave DI = 0.697, and at 2:1 the split was
0.283 vs 0.164. A resampling test over the thirty seeds puts both gaps
outside the spread that pure resampling produces (p = 0.002 and p = 0.010).

The protocol's bootstrap over seeds assumes the seeds are exchangeable
draws. The seed enters the world only through random.Random(seed) and the
entity set does not depend on it, so it SHOULD be exchangeable. But the
campaign's seeds are CONSECUTIVE INTEGERS, and a gap between "the first ten
consecutive seeds" and "the next twenty consecutive seeds" is exactly the
pattern that non-exchangeability would produce -- and also exactly what an
unlucky draw would produce.

This audit separates the two. It runs one sweep point with a fresh,
non-consecutive, pre-declared seed set and asks the same question of it:
does the first half of the list differ from the second half?

WHAT IT IS NOT

This is an INSTRUMENT AUDIT. It produces no experimental claim about the
organism, it changes no criterion, no verdict and no prediction, and it
cannot turn the raise-n result into a boundary claim. Whatever it finds is
reported alongside the raise-n result, whichever way it comes out.

Usage:
    python benchmarks/phase_l_seed_audit.py [--label 6:1] [--workers 12]
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import random
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import benchmarks.phase_l_campaign as P

#: The fresh seeds are drawn ONCE, from a fixed random draw over a wide
#: range, so they are not consecutive and carry no block structure. The draw
#: is fixed here in the source so the audit is reproducible.
FRESH_SEED_DRAW = 20261025
FRESH_SEED_RANGE = 1_000_000_000

#: The sweep point with the largest observed seed-set gap.
DEFAULT_LABEL = "6:1"


def fresh_seeds(n: int) -> list[int]:
    rng = random.Random(FRESH_SEED_DRAW)
    return sorted(rng.sample(range(FRESH_SEED_RANGE), n))


def _job(seed: int, lw: int, ew: int, cycles: int) -> dict:
    return {"arm": "V1", "label": f"{lw}:{ew}",
            "params": {"support_ratio": (lw, ew), "cycles": cycles},
            "seed": seed}


def _run(job: dict) -> dict:
    return P.run_cell(job)


def _load_checkpoint(path: Path) -> dict[int, dict]:
    """Cells already done, so a killed audit resumes instead of redoing them."""
    done: dict[int, dict] = {}
    if not path.exists():
        return done
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue  # a torn final line from a hard kill
                done[rec["seed"]] = rec
    except OSError:
        pass
    return done


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default=DEFAULT_LABEL)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--out", default="docs/phase_l_seed_audit.json")
    ap.add_argument("--checkpoint", default="docs/phase_l_seed_audit.ndjson")
    args = ap.parse_args()

    lw, ew = (int(x) for x in args.label.split(":"))
    seeds = fresh_seeds(args.seeds)
    out_path = REPO / args.out
    ckpt_path = REPO / args.checkpoint

    print("=" * 78)
    print("SEED-EXCHANGEABILITY AUDIT (instrument audit; no experimental claim)")
    print("=" * 78)
    print(f"  sweep point : {args.label}")
    print(f"  fresh seeds : {len(seeds)} (non-consecutive, fixed draw "
          f"{FRESH_SEED_DRAW} over range {FRESH_SEED_RANGE})")
    print(f"  first three : {seeds[:3]} ... last three: {seeds[-3:]}")

    done = _load_checkpoint(ckpt_path)
    if done:
        print(f"  resuming: {len(done)} cell(s) already done")
    todo = [s for s in seeds if s not in done]
    print(f"  running {len(todo)} cells on {args.workers} workers ...")

    results = list(done.values())
    if todo:
        with open(ckpt_path, "a", encoding="utf-8") as ckpt:
            with mp.Pool(processes=args.workers) as pool:
                for rec in pool.imap_unordered(
                        _run, [_job(s, lw, ew, P.CYCLES) for s in todo]):
                    results.append(rec)
                    ckpt.write(json.dumps(rec) + "\n")
                    ckpt.flush()
                    print(f"    seed {rec['seed']}: "
                          f"DI={rec['results']['organica']['displacement_index']} "
                          f"PI={rec['results']['organica']['preservation_index']}",
                          flush=True)

    results.sort(key=lambda r: r["seed"])
    out_path.write_text(json.dumps({
        "audit": "seed_exchangeability",
        "note": "Instrument audit. Produces no experimental claim.",
        "label": args.label,
        "fresh_seed_draw": FRESH_SEED_DRAW,
        "fresh_seeds": seeds,
        "records": results,
    }, indent=1), encoding="utf-8")

    fresh_di = [r["results"]["organica"]["displacement_index"] for r in results]
    fresh_pi = [r["results"]["organica"]["preservation_index"] for r in results]

    # The campaign's own subsets at this label, for comparison.
    campaign = json.loads((REPO / "docs" / "phase_l_results.json").read_text(encoding="utf-8"))
    old_seeds = set(range(20261023, 20261033))
    new_seeds = set(range(20261033, 20261053))
    by_seed = {r["seed"]: (r["results"]["organica"]["displacement_index"],
                           r["results"]["organica"]["preservation_index"])
               for r in campaign["records"]
               if r["arm"] == "V1" and r["label"] == args.label}
    old_di = [by_seed[s][0] for s in sorted(old_seeds) if s in by_seed]
    new_di = [by_seed[s][0] for s in sorted(new_seeds) if s in by_seed]

    half = len(seeds) // 2
    first_di = fresh_di[:half]
    second_di = fresh_di[half:]

    print()
    print("=" * 78)
    print("COMPARISON AT THIS SWEEP POINT")
    print("=" * 78)
    print(f"  campaign, original 10 seeds   : DI mean {statistics.mean(old_di):.4f} "
          f"(n={len(old_di)})")
    print(f"  campaign, added 20 seeds       : DI mean {statistics.mean(new_di):.4f} "
          f"(n={len(new_di)})")
    print(f"  campaign, all 30              : DI mean "
          f"{statistics.mean(old_di + new_di):.4f}")
    print(f"  AUDIT, fresh {len(seeds)} non-consecutive   : DI mean "
          f"{statistics.mean(fresh_di):.4f}")
    print()
    print(f"  fresh seeds, first {half}          : DI mean "
          f"{statistics.mean(first_di):.4f}")
    print(f"  fresh seeds, second {len(seeds)-half}         : DI mean "
          f"{statistics.mean(second_di):.4f}")
    print(f"  fresh first-half minus second-half: "
          f"{statistics.mean(first_di) - statistics.mean(second_di):+.4f}")
    print()
    print(f"  campaign old-10 minus new-20 gap  : "
          f"{statistics.mean(old_di) - statistics.mean(new_di):+.4f}")
    print()
    print("  wrote", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
