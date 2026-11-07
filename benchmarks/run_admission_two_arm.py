"""Run the two-arm admission comparison exactly as registered.

Both arms of a seed run through the Gate 13 harness on the same generated world
with the same budget and cycles; only ``service_cls`` differs.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from benchmarks.acquisition_harness import gate_acquisition_sufficiency
from organica.admission import DiversityFirstSleepService
from organica.sleep import SleepService

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "admission_two_arm_run.json"
PREREG = ROOT / "docs" / "admission_two_arm_prereg.json"

FROZEN = ("organica/sleep.py", "organica/memory.py", "organica/paths.py",
          "organica/streams.py", "organica/branch_streams.py",
          "organica/scale_streams.py", "organica/ground_truth_worlds.py")

ARMS = {"reference": SleepService, "adopted": DiversityFirstSleepService}


def prereg(path: Path = PREREG) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def boundary() -> dict:
    diff = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", *FROZEN],
                          cwd=str(ROOT), capture_output=True, text=True)
    status = subprocess.run(["git", "status", "--porcelain", "--", *FROZEN],
                            cwd=str(ROOT), capture_output=True, text=True)
    return {"frozen_files_clean": diff.returncode == 0 and not status.stdout.strip(),
            "checked": list(FROZEN)}


def run(out: Path = OUT, record: dict | None = None) -> dict:
    record = record or prereg()
    if not record["status"].startswith("FROZEN"):
        raise SystemExit("the registration is not frozen; no cell may run")
    cycles = int(record["design"]["cycles"])
    cells = []
    for seed in record["design"]["seeds"]:
        for arm in record["design"]["arms"]:
            stats = gate_acquisition_sufficiency(seed=int(seed), cycles=cycles,
                                                 service_cls=ARMS[arm])
            cells.append({
                "seed": int(seed), "arm": arm,
                "coverage": stats["asserted_coverage"],
                "covered": stats["covered_asserted_edges"],
                "asserted": stats["asserted_edges"],
                "precision": round(stats["covered_asserted_edges"]
                                   / stats["asserted_edges"], 6)
                if stats["asserted_edges"] else 0.0,
                "world_edges": stats["world_edges"],
                "raw_temporal_coverage": stats["raw_temporal_coverage"],
                "asserted_fingerprint": stats["asserted_fingerprint"],
                "service": stats["arm"],
            })
    first = int(record["design"]["seeds"][0])
    rerun = gate_acquisition_sufficiency(seed=first, cycles=cycles,
                                         service_cls=SleepService)
    reference_first = next(c for c in cells
                           if c["seed"] == first and c["arm"] == "reference")
    payload = {"prereg": record["prereg"], "cycles": cycles, "cells": cells,
               "determinism": {"seed": first,
                               "rerun_fingerprint": rerun["asserted_fingerprint"],
                               "matched": rerun["asserted_fingerprint"]
                                          == reference_first["asserted_fingerprint"]},
               "boundary": boundary(),
               "provenance": {"runner": "benchmarks/run_admission_two_arm.py",
                              "instrument": "benchmarks/acquisition_harness.py:gate_acquisition_sufficiency",
                              "arms": {a: ARMS[a].__name__ for a in record["design"]["arms"]},
                              "engine_runs": len(record["design"]["seeds"]) * 2 + 1}}
    out.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    print("wrote", out, "| cells:", len(cells))
    return payload


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--out", default=str(OUT))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
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
