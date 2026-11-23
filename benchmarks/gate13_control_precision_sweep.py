"""Diagnostic sweep: how does the count-sorted control's cap-20 precision vary across seeds?

**This is not a confirmatory test and tests no hypothesis.** The `ratio` admission question was settled
by `docs/GATE13-RATIO-CONFIRMATORY-PREREGISTRATION.md`, whose C1 criterion failed; this harness exists
to characterise *that failure*, and no threshold in it is pre-registered, so nothing it returns may be
read as a verdict on the admission rule.

The quantity measured is arm C's asserted precision at cap 20, computed by
`benchmarks.run_ratio_admission_arm.run_cell` -- imported, not reimplemented, so it is the same
world generation, ingestion, sleep cycles, asserted-set construction and precision as the registered
block. Only the seed set and the cell plan (C at cap 20, one cell per seed) differ.

Why the pool base rate is not the thing being estimated: `pool_diagnostics` reports the same 240 rows
containing the same 112 world edges on every seed, so the base rate is 112/240 = 0.4667 by
construction, exactly, on every cell. What varies across seeds is where those 112 edges sit in the
count ordering -- i.e. the top-20 density of a fixed candidate space. The sweep therefore measures the
distributions of `precision` and of the top-20 density around that constant, and reports them as a
characterisation.

Every row also records the pool diagnostics, so the base rate is verified per seed rather than assumed.

Resumable: one JSON line per seed. Scratch DBs only; no frozen file is read or edited.
Run with PYTHONHASHSEED=0.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks.run_ratio_admission_arm import run_cell  # noqa: E402  the registered computation

ARM = "C"
CAP = 20
OUT = REPO / ".scratch" / "control_precision_sweep.jsonl"


def head_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True,
                              text=True, timeout=20).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def done(path: Path) -> set:
    if not path.exists():
        return set()
    return {json.loads(l)["seed"] for l in path.read_text().splitlines() if l.strip()}


def main() -> None:
    ap = argparse.ArgumentParser(description="diagnostic sweep, not a confirmatory test")
    ap.add_argument("--block", required=True, help="START:END inclusive, e.g. 20270627:20270825")
    ap.add_argument("--jsonl", default=str(OUT))
    ap.add_argument("--budget", type=int, default=1000, help="stop after this many new cells")
    args = ap.parse_args()

    lo, hi = (int(x) for x in args.block.split(":"))
    out_path = Path(args.jsonl)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    have, ran = done(out_path), 0
    commit = head_commit()
    for seed in range(lo, hi + 1):
        if seed in have:
            continue
        if ran >= args.budget:
            print(f"budget reached: {ran} new cells, {len(have)} total done")
            return
        r = run_cell(ARM, CAP, seed)
        row = {"seed": seed, "arm": ARM, "cap": CAP, "commit": commit, **r}
        with out_path.open("a") as f:
            f.write(json.dumps(row) + "\n")
        have.add(seed)
        ran += 1
        print(f"seed={seed} prec={r['precision']} asserted={r['asserted']} cov={r['coverage']} "
              f"pool={r.get('pool_rows')} base={r.get('base_rate')} top20={r.get('top_k', {}).get('20')} "
              f"dmin={r.get('distinct_values')} modal={r.get('modal_tie_share')} ({r['runtime_s']}s)",
              flush=True)
    print(f"complete: {len(have)} cells")


if __name__ == "__main__":
    main()
