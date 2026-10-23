"""
The Tier-1 matrix launcher.

Six colonies, run in parallel as six processes, merged into one artifact.

**Why this exists instead of six shell commands.** CPython randomises string
hashing per process unless `PYTHONHASHSEED` is pinned, and the engine's
candidate construction walks collections whose iteration order depends on a
string hash. Six separate processes therefore get six *different* hash
orders, and that difference is pure measurement artifact: it is not a
property of any colony. Run six colonies in six processes without pinning
and the between-colony comparison carries hash noise.

Running all six colonies in ONE process instead would make the hash order
common-mode (it cancels in the comparison) but would serialise 6 x 20 minutes
into two hours.

This launcher gets both: parallel processes, **all pinned to the same
`PYTHONHASHSEED`**, so the hash order is common-mode across the colonies and
the comparison between them is clean, and the campaign still finishes in
about the time of one colony.

The floor this removes was measured, not assumed:
`benchmarks/process_noise.py --sweep` -> `docs/process_noise.json`.

Usage:
    python benchmarks/run_matrix.py --cycles 3000 --out docs/force_matrix.json
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks.force_matrix import COLONIES  # noqa: E402

PARTS_DIR = REPO / ".scratch" / "matrix_parts"


def git(*args: str) -> str | None:
    try:
        out = subprocess.run(["git", *args], cwd=str(REPO),
                             capture_output=True, text=True, timeout=30)
        if out.returncode != 0:
            return None
        return out.stdout.strip()
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=3000)
    ap.add_argument("--seed", type=int, default=20261023)
    ap.add_argument("--hash-seed", default="0",
                    help="PYTHONHASHSEED for every colony process. The same "
                         "value for all six, so the hash order is common-mode "
                         "across colonies.")
    ap.add_argument("--colonies", nargs="*", default=list(COLONIES))
    ap.add_argument("--out", default=str(REPO / "docs" / "force_matrix.json"))
    ap.add_argument("--parts-dir", default=str(PARTS_DIR))
    ap.add_argument("--no-verify", action="store_true")
    args = ap.parse_args()

    parts_dir = Path(args.parts_dir)
    parts_dir.mkdir(parents=True, exist_ok=True)

    # ---- G1: prove the six colonies are genuinely distinct code paths -------
    if not args.no_verify:
        from benchmarks.force_matrix import verify_colonies
        from organica.branch_streams import (
            NEUTRAL_HUB, NEUTRAL_PETALS, lattice_designs, lattice_stream)
        lattice = lattice_designs(NEUTRAL_HUB, NEUTRAL_PETALS)
        events = lattice_stream(lattice["L1_hub1_t3_disjoint"]["triangles"])
        print("G1 code-path verification:")
        checks = verify_colonies(events)
        by_name = {c["colony"]: c for c in checks}
        if len(by_name) < len(args.colonies):
            raise SystemExit("G1 did not verify every colony")
    else:
        checks = []

    env = dict(os.environ)
    env["PYTHONHASHSEED"] = str(args.hash_seed)

    started = time.time()
    procs = {}
    for name in args.colonies:
        part = parts_dir / f"{name}.json"
        cmd = [sys.executable, str(REPO / "benchmarks" / "force_matrix.py"),
               "--cycles", str(args.cycles), "--seed", str(args.seed),
               "--no-verify", "--colonies", name, "--out", str(part)]
        print(f"  launching {name} (PYTHONHASHSEED={args.hash_seed}) ...",
              flush=True)
        procs[name] = (subprocess.Popen(cmd, cwd=str(REPO), env=env,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        text=True), part)

    print(f"\n{len(procs)} colonies running in parallel "
          f"(~{args.cycles} cycles each). Waiting ...", flush=True)

    failures = []
    for name, (proc, part) in procs.items():
        out = proc.communicate()[0]
        if proc.returncode != 0:
            failures.append((name, out))
            print(f"  {name} FAILED (exit {proc.returncode})")
            if out:
                print(out[-3000:])
        else:
            for line in out.strip().splitlines():
                if line.strip():
                    print(f"  {line}", flush=True)

    if failures:
        raise SystemExit(f"{len(failures)} colonies failed: "
                         f"{[n for n, _ in failures]}")

    # ---- merge, with provenance -------------------------------------------
    rows = []
    for name in args.colonies:
        part = parts_dir / f"{name}.json"
        doc = json.loads(part.read_text(encoding="utf-8"))
        rows.extend(doc.get("rows", []))
    order = list(COLONIES)
    rows.sort(key=lambda r: order.index(r["colony"])
              if r["colony"] in order else 99)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cycles": args.cycles,
        "seed": args.seed,
        "stimulus": "lattice_L1 (three disjoint triangles)",
        "provenance": {
            "py_hash_seed": args.hash_seed,
            "py_hash_seed_note":
                "The same PYTHONHASHSEED in all six colony processes, so the "
                "hash order is common-mode across colonies and cannot "
                "contaminate the between-colony comparison. The unpinned "
                "floor was measured: docs/process_noise.json.",
            "git_commit": git("rev-parse", "HEAD"),
            "git_branch": git("rev-parse", "--abbrev-ref", "HEAD"),
            "git_describe": git("describe", "--tags", "--always"),
            "wall_clock_seconds": round(time.time() - started, 1),
            "parts_dir": str(parts_dir),
            "g1_verification": checks,
        },
        "rows": rows,
    }, indent=2), encoding="utf-8")

    print(f"\nmerged {len(rows)} colonies into {out_path} "
          f"({round(time.time() - started, 1)}s total)")


if __name__ == "__main__":
    main()
