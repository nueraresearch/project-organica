"""
benchmarks/stream_sweep.py
------------------------------------------------------------------
Phase G: choose the experience stream for the 90-day longitudinal study.

The original study stream (30 unrelated events rotated) provably cannot
exercise Generation 5: no subject ever carries two competing expectations,
so Layer 5 has nothing to coalesce. `g5_gap_diagnostic.py` established
that. This script picks the replacement empirically.

Every candidate is scored the same way, over the same number of cycles,
with the same rotating-slice injection the daemon uses:

  g5_sustainment   -- fraction of cycles with at least one Theory
  mean_uncertainty -- mean peak Shannon uncertainty of Questions (Law V)
  mean_priority    -- mean peak EIG of Experiments (Law V)
  mean_contras     -- mean total hypothesis contradictions
  g1_g4_stable     -- fraction of cycles that still hold hypotheses
                      (the organism must not simply decay to nothing)

Usage:
    python benchmarks/stream_sweep.py
    python benchmarks/stream_sweep.py --cycles 24
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from organica import MemoryService, SleepService  # noqa: E402


# ---------------------------------------------------------------------------
# Candidates
# ---------------------------------------------------------------------------
PHASE_F_DEVELOPER = [
    "developer modified auth login session",
    "developer executed test suite",
    "test suite report failures detected session",
    "failure detected in login module",
    "developer modified auth session handler",
    "developer executed test suite",
    "test suite report passed validation clean",
    "developer modified api router endpoint",
    "developer executed test suite",
    "test suite report failures detected router",
    "failure detected in router endpoint",
    "developer modified api router handler",
    "developer executed test suite",
    "test suite report passed validation clean",
] * 4

PHASE_F_DEFECT = [
    "user reported issue ticket assigned",
    "triage assigned issue engineer review",
    "engineer reproduce issue commit patch",
    "pipeline executed tests verified passed",
    "support agent closed issue resolved",
    "user reported issue ticket assigned",
    "triage assigned issue engineer review",
    "engineer reproduce commit patch failed",
    "engineer reproduce commit patch retry",
    "pipeline executed tests verified passed",
    "support agent closed issue resolved",
] * 4

PHASE_F_ECOLOGY = [
    "organism search energy level depleted",
    "organism locate resource food available",
    "organism consume food energy restored",
    "biome replenish vegetation growth season",
    "organism rest metabolism stable recovered",
    "organism search energy level depleted",
    "organism locate resource food available",
    "organism consume food energy restored",
    "biome replenish vegetation growth season",
] * 5

PHASE_F_ROBOT = [
    "robot drive forward velocity motion",
    "sonar detect obstacle distance near",
    "actuator steer pivot turn left",
    "sonar sense clear corridor open",
    "robot drive forward velocity motion",
    "sonar detect obstacle distance near",
    "actuator steer pivot turn right",
    "sonar sense clear corridor open",
    "robot drive forward velocity motion",
] * 5

# Branch-heavy variants: the SAME subject must be followed by BOTH a
# positive and a negative outcome, so that support and contradiction both
# accumulate and Shannon entropy stays non-zero.
BRANCH_DEVELOPER = [
    "developer modified auth login session",
    "developer executed test suite",
    "test suite report failures detected session",
    "developer modified api router endpoint",
    "developer executed test suite",
    "test suite report passed validation clean",
    "developer modified auth login session",
    "developer executed test suite",
    "test suite report failures detected session",
    "developer modified api router endpoint",
    "developer executed test suite",
    "test suite report passed validation clean",
] * 2

BRANCH_DEFECT = [
    "reporter filed issue ticket defect",
    "engineer reproduced defect stacktrace",
    "engineer committed patch defect",
    "pipeline executed tests failed",
    "reporter filed issue ticket regression",
    "engineer reproduced regression stacktrace",
    "engineer committed patch regression",
    "pipeline executed tests passed",
] * 3

CANDIDATES = {
    "phase_f_pack_all": PHASE_F_DEVELOPER + PHASE_F_DEFECT + PHASE_F_ECOLOGY + PHASE_F_ROBOT,
    "branch_developer_only": BRANCH_DEVELOPER,
    "branch_developer_and_defect": BRANCH_DEVELOPER + BRANCH_DEFECT,
    "branch_four_domains": (
        BRANCH_DEVELOPER
        + BRANCH_DEFECT
        + PHASE_F_ECOLOGY
        + PHASE_F_ROBOT
    ),
}


# ---------------------------------------------------------------------------
def score(stream: list[str], cycles: int, slice_size: int) -> dict:
    tmpdir = tempfile.mkdtemp(prefix="organica_sweep_")
    mem = MemoryService(Path(tmpdir) / "sweep.db")
    for text in stream:
        mem.store(text, event_type="event", source="sweep:seed")
    sleep = SleepService(mem)

    n = len(stream)
    rows = []
    for cycle in range(cycles):
        start = (cycle * slice_size) % n
        for text in stream[start:start + slice_size]:
            mem.store(text, event_type="event", source=f"sweep:cycle:{cycle}")

        report = sleep.run_sleep_cycle()
        grouped = defaultdict(list)
        for h in report.hypotheses:
            if h.expectation != "high_structural_significance":
                grouped[h.subject].append(h)
        rows.append({
            "cycle": report.cycle,
            "hypotheses": len(report.hypotheses),
            "eligible_subjects": sum(1 for v in grouped.values() if len(v) >= 2),
            "theories": len(report.theories),
            "questions": len(report.questions),
            "uncertainty": max((q.uncertainty for q in report.questions), default=0.0),
            "priority": max((e.priority for e in report.experiments), default=0.0),
            "contradictions": sum(h.contradiction_count for h in report.hypotheses),
            "dreams": len(report.dreams),
            "investigations": len(report.investigations),
            "experiments": len(report.experiments),
        })

    mem.close()
    try:
        (Path(tmpdir) / "sweep.db").unlink()
        Path(tmpdir).rmdir()
    except OSError:
        pass

    scored = [r for r in rows if r["hypotheses"] > 0] or rows
    return {
        "cycles": cycles,
        "slice_size": slice_size,
        "g5_sustainment": round(
            sum(1 for r in scored if r["theories"] > 0) / len(scored), 4) if scored else 0.0,
        "question_sustainment": round(
            sum(1 for r in scored if r["questions"] > 0) / len(scored), 4) if scored else 0.0,
        "mean_uncertainty": round(sum(r["uncertainty"] for r in scored) / len(scored), 4) if scored else 0.0,
        "mean_priority": round(sum(r["priority"] for r in scored) / len(scored), 4) if scored else 0.0,
        "mean_contradictions": round(sum(r["contradictions"] for r in scored) / len(scored), 1) if scored else 0.0,
        "mean_hypotheses": round(sum(r["hypotheses"] for r in scored) / len(scored), 2) if scored else 0.0,
        "mean_eligible_subjects": round(sum(r["eligible_subjects"] for r in scored) / len(scored), 3) if scored else 0.0,
        "mean_dreams": round(sum(r["dreams"] for r in scored) / len(scored), 2) if scored else 0.0,
        "per_cycle": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Sweep candidate study streams.")
    ap.add_argument("--cycles", type=int, default=24)
    ap.add_argument("--slice", type=int, default=8)
    ap.add_argument("--out", default="docs/stream_sweep.json")
    args = ap.parse_args()

    results = {}
    for name, stream in CANDIDATES.items():
        print(f"  running {name} ({len(stream)} events)...", flush=True)
        results[name] = score(stream, args.cycles, args.slice)

    print()
    print("=" * 92)
    print("PROJECT ORGANICA -- STUDY STREAM SWEEP")
    print("=" * 92)
    hdr = f"{'candidate':<28}{'G5 sust':>9}{'Q sust':>9}{'uncert':>9}{'EIG':>8}{'contra':>10}{'hyps':>7}{'elig':>7}{'dreams':>8}"
    print(hdr)
    print("-" * 92)
    ranked = sorted(results.items(), key=lambda kv: -kv[1]["g5_sustainment"])
    for name, r in ranked:
        print(f"{name:<28}{r['g5_sustainment']:>9.2f}{r['question_sustainment']:>9.2f}"
              f"{r['mean_uncertainty']:>9.3f}{r['mean_priority']:>8.3f}{r['mean_contradictions']:>10.1f}"
              f"{r['mean_hypotheses']:>7.2f}{r['mean_eligible_subjects']:>7.2f}{r['mean_dreams']:>8.2f}")
    print("-" * 92)
    best = ranked[0][0]
    print(f"  BEST: {best}")

    out = Path(__file__).parent.parent / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "phase": "G",
        "title": "Study Stream Sweep",
        "method": f"Each candidate scored over {args.cycles} cycles with a rotating "
                  f"{args.slice}-event slice per cycle, identical to the daemon's injection.",
        "best": best,
        "candidates": results,
    }, indent=2))
    print(f"  Full report written to: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
