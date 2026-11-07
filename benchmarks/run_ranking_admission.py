"""Run the confirmatory admission block with the same instrument as the ordering block.

    ./.venv/bin/python -m benchmarks.run_ranking_admission --run

The pools, the world family, the two orderings and the cell construction are imported from
`benchmarks.run_rank_ordering`, so the confirmatory block differs from the completed one in
its seeds its bar and its decision rule, and in nothing else. No judged cell runs unless the
audit passes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks import run_rank_ordering as base

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "ranking_admission_run.json"


def prereg(path: Path | None = None) -> dict:
    return json.loads((path or (ROOT / "docs" / "ranking_admission_prereg.json"))
                      .read_text(encoding="utf-8"))


def audit(record: dict) -> dict:
    design = record["design"]
    seeds = list(design["seeds"])
    problems = []
    if len(seeds) != 8 or len(set(seeds)) != 8:
        problems.append("the grid does not carry eight distinct seeds")
    if seeds != list(range(seeds[0], seeds[0] + 8)):
        problems.append("the seed block is not contiguous")
    if len(design["arms"]) != 2 or len(design["caps"]) != 2:
        problems.append("the grid is not two arms by two caps")
    if len(design["densities"]) != 5:
        problems.append("the grid is not five densities")
    if design["cells"] != 2 * 2 * 5 * 8:
        problems.append("the grid is not 160 cells")
    if record["status"].split("(")[0].split(",")[0].strip() != "FROZEN":
        problems.append("the pre-registration is not frozen")
    return {"passed": not problems, "problems": problems}


def run(out: Path = OUT, record: dict | None = None) -> dict:
    record = record or prereg()
    report = audit(record)
    if not report["passed"]:
        raise SystemExit("the pre-registration failed its audit; no cell may run: %r"
                         % report["problems"])
    blocked = (record.get("pre_run") or {}).get("blocked")
    if blocked:
        raise SystemExit("the block is blocked by a recorded finding: %s" % blocked)
    identity = base.identity_audit()
    cells: list[dict] = []
    for seed in record["design"]["seeds"]:
        for rho in record["design"]["densities"]:
            pool = base.run_pool(seed, rho)
            world = base.world_edges(seed, rho)
            cells.extend(base.cells_for(seed, rho, pool, world, record))
    payload = {"prereg": record["prereg"], "cells": cells, "identity": identity,
               "provenance": {"runner": "benchmarks/run_ranking_admission.py",
                              "instrument": "benchmarks/run_rank_ordering.py",
                              "engine_runs": len(record["design"]["seeds"])
                              * len(record["design"]["densities"]),
                              "cells": len(cells)}}
    out.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    print("wrote", out, "| cells:", len(cells))
    return payload


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="execute the block")
    parser.add_argument("--audit", action="store_true", help="audit only; no engine, no world")
    parser.add_argument("--out", default=str(OUT))
    parser.add_argument("--force", action="store_true",
                        help="overwrite an existing run artifact")
    args = parser.parse_args(argv)
    if args.audit:
        report = audit(prereg())
        print(json.dumps(report, indent=1))
        return 0 if report["passed"] else 1
    if not args.run:
        parser.print_help()
        return 0
    target = Path(args.out)
    if target.exists() and not args.force:
        print("refusing to overwrite %s without --force" % target)
        return 1
    run(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
