"""
benchmarks/g5_gap_diagnostic.py
------------------------------------------------------------------
Phase G diagnostic: *why does the organism never reach G5?*

The continuous daemon (`run_continuous.py`) has logged hundreds of sleep
cycles in which `theories == 0` and `questions == 0`, while the Phase F
cross-domain validation reported `theories == 1` for one of four domains.
CHALLENGE.md lists G5 (Epistemic Tension -> Theories + Questions) as one of
the nine required emergence targets, so this discrepancy matters.

This script isolates the cause instead of guessing at it. It instruments the
G5 precondition directly:

  Layer 5 (`_form_theories_and_questions`) groups hypotheses by `subject`
  and skips any subject with fewer than two hypotheses:

      for subject, hyps in by_subject.items():
          if len(hyps) < 2:
              continue

  So a Theory is possible only for subjects that carry >= 2 competing
  expectations. This script computes that **ceiling** for every cycle and
  compares it against what was actually produced. If actual == ceiling, the
  gate is fully explained and no other blocker exists.

It also measures substrate scaling (cycle latency vs. cumulative event
count), because an unbounded O(n) substrate cannot support the 90-day
longitudinal study regardless of the cognitive findings.

Usage:
    python benchmarks/g5_gap_diagnostic.py
    python benchmarks/g5_gap_diagnostic.py --cycles 12 --out docs/g5_gap_diagnostic.json

Writes a JSON report to docs/g5_gap_diagnostic.json and prints a summary.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from organica import MemoryService, SleepService  # noqa: E402


# ---------------------------------------------------------------------------
# Stream A -- the exact stream the 90-day longitudinal study runs.
# Copied verbatim from run_continuous.py (DOMAIN_EVENTS + rotating slice).
# ---------------------------------------------------------------------------
RUNNER_EVENTS = [
    ("function called with arguments", "event"),
    ("test passed after code modification", "event"),
    ("auth failure on login attempt", "event"),
    ("session expired triggering re-auth", "event"),
    ("build pipeline triggered on push", "event"),
    ("tests passed all suites green", "event"),
    ("deployment succeeded to staging", "event"),
    ("auth session renewed successfully", "event"),
    ("pull request merged into main branch", "event"),
    ("code review approved by reviewer", "event"),
    ("test failed due to assertion error", "event"),
    ("hotfix branch created for critical bug", "event"),
    ("issue reported in production system", "event"),
    ("issue assigned to developer team", "event"),
    ("fix committed to feature branch", "event"),
    ("regression test added for fix", "event"),
    ("issue closed after verification", "event"),
    ("duplicate issue linked to original", "event"),
    ("resource consumed by organism", "event"),
    ("organism reproduced successfully", "event"),
    ("resource depleted triggering migration", "event"),
    ("predator prey interaction observed", "event"),
    ("population stabilised after peak", "event"),
    ("sensor reading acquired from environment", "event"),
    ("action planned based on sensor data", "event"),
    ("action executed by actuator", "event"),
    ("collision detected requiring replanning", "event"),
    ("goal reached after navigation sequence", "event"),
    ("battery low triggering return to dock", "event"),
]


# ---------------------------------------------------------------------------
# Stream B -- the Phase F "Developer Workflow" domain, the only domain that
# has ever produced a theory. Used as the positive control.
# ---------------------------------------------------------------------------
DEVELOPER_WORKFLOW = [
    "developer modified auth login session",
    "developer executed test suite",
    "test suite report: failures detected session",
    "failure detected in login module",
    "developer modified auth session handler",
    "developer executed test suite",
    "test suite report: passed validation clean",
    "developer modified api router endpoint",
    "developer executed test suite",
    "test suite report: failures detected router",
    "failure detected in router endpoint",
    "developer modified api router handler",
    "developer executed test suite",
    "test suite report: passed validation clean",
] * 4


# ---------------------------------------------------------------------------
# Stream C -- CANDIDATE replacement for the longitudinal study.
#
# Design goals, derived from the two failures measured in streams A and B:
#
#   * G5 needs a subject that carries >= 2 competing expectations. That
#     requires the SAME tag to be followed by DIFFERENT tags. The original
#     study stream rotated through 30 unrelated events, so every tag kept
#     exactly one successor and no subject ever had a competitor.
#   * Law V needs non-zero uncertainty. With no branching, support saturates,
#     confidence pins at 1.0, entropy is 0, and EIG is 0 -- the attention
#     economy never engages.
#
# So each domain is a TIGHT repeating loop, and the branch point ("pipeline
# executed tests verified passed" vs "... failed") is shared across domains
# so that one subject accumulates both a positive and a negative successor.
# ---------------------------------------------------------------------------
LONGITUDINAL_CANDIDATE = (
    # --- Domain 1: developer workflow (branching outcome) ---
    [
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
    + [
        # --- Domain 2: defect triage (branching outcome) ---
        "reporter filed issue ticket defect",
        "engineer reproduced defect stacktrace",
        "engineer committed patch defect",
        "pipeline executed tests failed",
        "reporter filed issue ticket regression",
        "engineer reproduced regression stacktrace",
        "engineer committed patch regression",
        "pipeline executed tests passed",
    ] * 4
    + [
        # --- Domain 3: foraging ecology ---
        "organism foraged resource depleted",
        "organism consumed resource energy restored",
        "organism reproduced offspring colony",
        "biome replenished resource vegetation growth",
    ] * 5
    + [
        # --- Domain 4: mobile robot ---
        "robot navigated corridor obstacle detected",
        "robot steered actuator turned left",
        "robot navigated corridor path clear",
        "battery drained robot returned dock",
    ] * 5
)


# ---------------------------------------------------------------------------
# G5 precondition instrumentation
# ---------------------------------------------------------------------------
def analyze_cycle(report) -> dict:
    """Compute the G5 ceiling for one sleep cycle and compare to reality."""
    by_subject: dict[str, list] = defaultdict(list)
    for h in report.hypotheses:
        by_subject[h.subject].append(h)

    # Layer 5 EXCLUDES "high_structural_significance" hypotheses before
    # grouping (they are meta-centrality markers, not directional claims).
    # The ceiling must therefore be computed on the same population the
    # engine actually groups, otherwise the ceiling over-counts.
    engine_by_subject: dict[str, list] = defaultdict(list)
    for h in report.hypotheses:
        if h.expectation != "high_structural_significance":
            engine_by_subject[h.subject].append(h)

    # Layer 5 skips any subject with < 2 hypotheses -> those subjects can
    # never yield a theory or a question.
    eligible = {s: hs for s, hs in engine_by_subject.items() if len(hs) >= 2}

    theory_ceiling = min(SleepService.MAX_THEORIES, len(eligible))
    question_ceiling = min(SleepService.MAX_QUESTIONS, len(eligible))

    return {
        "cycle": report.cycle,
        "hypotheses": len(report.hypotheses),
        "distinct_subjects": len(by_subject),
        "engine_grouped_subjects": len(engine_by_subject),
        "structural_only_subjects": len(by_subject) - len(engine_by_subject),
        "g5_eligible_subjects": len(eligible),
        "theory_ceiling": theory_ceiling,
        "question_ceiling": question_ceiling,
        "theories_actual": len(report.theories),
        "questions_actual": len(report.questions),
        "ceiling_saturated": (
            len(report.theories) == theory_ceiling
            and len(report.questions) == question_ceiling
        ),
        "subject_detail": {
            subject: [
                {
                    "expectation": h.expectation,
                    "support": h.support_count,
                    "contradiction": h.contradiction_count,
                    "confidence": round(h.confidence, 4),
                }
                for h in hyps
            ]
            for subject, hyps in by_subject.items()
        },
        "eligible_subject_detail": {
            subject: {
                "hypothesis_count": len(hyps),
                "expectations": [h.expectation for h in hyps],
                "produced_theory": any(
                    subject in getattr(t, "subject", None) for t in report.theories
                ),
            }
            for subject, hyps in eligible.items()
        },
        "downstream": {
            "dreams": len(report.dreams),
            "investigations": len(report.investigations),
            "experiments": len(report.experiments),
        },
        # Law V (EIG) only has fuel when uncertainty is non-zero, which
        # requires at least one hypothesis to carry contradictions.
        "contradiction_total": sum(
            h.contradiction_count for h in report.hypotheses
        ),
        "hypotheses_with_contradictions": sum(
            1 for h in report.hypotheses if h.contradiction_count > 0
        ),
        "mean_hypothesis_confidence": (
            round(sum(h.confidence for h in report.hypotheses) / len(report.hypotheses), 4)
            if report.hypotheses else 0.0
        ),
        "peak_question_uncertainty": round(
            max((q.uncertainty for q in report.questions), default=0.0), 4
        ),
        "peak_experiment_priority": round(
            max((e.priority for e in report.experiments), default=0.0), 4
        ),
    }


# ---------------------------------------------------------------------------
# Stream runners
# ---------------------------------------------------------------------------
def run_runner_stream(cycles: int) -> dict:
    """Replicates run_continuous.py exactly: seed all 30 events, then inject a
    rotating 4-event slice per cycle."""
    return _run(
        label="continuous_runner_stream",
        description="The exact event stream used by the 90-day longitudinal study (run_continuous.py).",
        seed=[text for text, _ in RUNNER_EVENTS],
        per_cycle=lambda cycle: [
            text for text, _ in RUNNER_EVENTS[(cycle * 4) % len(RUNNER_EVENTS):(cycle * 4) % len(RUNNER_EVENTS) + 4]
        ],
        cycles=cycles,
    )


def run_developer_workflow(cycles: int) -> dict:
    """Positive control: the one Phase F domain that produced a theory."""
    return _run(
        label="cross_domain_developer_workflow",
        description="Phase F 'Developer Workflow' domain (known to produce theories == 1).",
        seed=DEVELOPER_WORKFLOW,
        per_cycle=lambda cycle: [],
        cycles=cycles,
    )


def run_longitudinal_candidate(cycles: int) -> dict:
    """Candidate replacement stream for the 90-day study."""
    return _run(
        label="candidate_longitudinal_stream",
        description="CANDIDATE study stream: tight per-domain loops with a shared "
                    "branching outcome, designed so a subject accumulates two "
                    "competing expectations (G5) and non-zero uncertainty (Law V).",
        seed=LONGITUDINAL_CANDIDATE,
        per_cycle=lambda cycle: [],
        cycles=cycles,
    )


def _run(label, description, seed, per_cycle, cycles) -> dict:
    tmpdir = tempfile.mkdtemp(prefix="organica_diag_")
    db_path = Path(tmpdir) / "diag.db"

    mem = MemoryService(db_path)
    for text in seed:
        mem.store(text, event_type="event", source="diag:seed")
    sleep = SleepService(mem)

    per_cycle_records = []
    for cycle in range(cycles):
        for text in per_cycle(cycle):
            mem.store(text, event_type="event", source=f"diag:cycle:{cycle}")

        t0 = time.time()
        report = sleep.run_sleep_cycle()
        elapsed_ms = (time.time() - t0) * 1000

        record = analyze_cycle(report)
        record["cycle_ms"] = round(elapsed_ms, 1)
        record["total_events"] = mem.count()
        per_cycle_records.append(record)

    # ---- aggregate ----
    eligible_cycles = [r for r in per_cycle_records if r["g5_eligible_subjects"] > 0]
    saturated_cycles = [r for r in per_cycle_records if r["ceiling_saturated"]]
    ever_theory = any(r["theories_actual"] > 0 for r in per_cycle_records)
    ever_question = any(r["questions_actual"] > 0 for r in per_cycle_records)

    # substrate scaling: latency growth per 1000 additional events
    scaling = []
    if len(per_cycle_records) >= 2:
        first, last = per_cycle_records[0], per_cycle_records[-1]
        d_events = last["total_events"] - first["total_events"]
        d_ms = last["cycle_ms"] - first["cycle_ms"]
        scaling = {
            "events_first": first["total_events"],
            "events_last": last["total_events"],
            "cycle_ms_first": first["cycle_ms"],
            "cycle_ms_last": last["cycle_ms"],
            "ms_per_1000_events": round(d_ms / d_events * 1000, 4) if d_events else None,
            "final_total_events": last["total_events"],
        }

    result = {
        "label": label,
        "description": description,
        "cycles": cycles,
        "ever_produced_theory": ever_theory,
        "ever_produced_question": ever_question,
        "cycles_with_g5_eligible_subjects": len(eligible_cycles),
        "cycles_where_ceiling_saturated": len(saturated_cycles),
        "gate_is_binding_constraint": (
            len(eligible_cycles) == 0 and not ever_theory
        ),
        "peak_hypotheses": max((r["hypotheses"] for r in per_cycle_records), default=0),
        "peak_distinct_subjects": max((r["distinct_subjects"] for r in per_cycle_records), default=0),
        "peak_g5_eligible_subjects": max((r["g5_eligible_subjects"] for r in per_cycle_records), default=0),
        "peak_theories": max((r["theories_actual"] for r in per_cycle_records), default=0),
        "peak_questions": max((r["questions_actual"] for r in per_cycle_records), default=0),
        "peak_contradiction_total": max((r["contradiction_total"] for r in per_cycle_records), default=0),
        "peak_hypotheses_with_contradictions": max(
            (r["hypotheses_with_contradictions"] for r in per_cycle_records), default=0),
        "peak_question_uncertainty": max((r["peak_question_uncertainty"] for r in per_cycle_records), default=0),
        "peak_experiment_priority": max((r["peak_experiment_priority"] for r in per_cycle_records), default=0),
        "mean_hypothesis_confidence": (
            round(sum(r["mean_hypothesis_confidence"] for r in per_cycle_records) / len(per_cycle_records), 4)
            if per_cycle_records else 0.0
        ),
        "scaling": scaling,
        "per_cycle": per_cycle_records,
    }

    mem.close()
    try:
        db_path.unlink()
        os.rmdir(tmpdir)
    except OSError:
        pass
    return result


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
def print_summary(results: list[dict]):
    print("=" * 78)
    print("PROJECT ORGANICA -- PHASE G DIAGNOSTIC: THE G5 GAP")
    print("=" * 78)

    for res in results:
        print(f"\n  Stream: {res['label']}")
        print(f"    {res['description']}")
        print(f"    cycles run                      : {res['cycles']}")
        print(f"    peak hypotheses                 : {res['peak_hypotheses']}")
        print(f"    peak distinct subjects          : {res['peak_distinct_subjects']}")
        print(f"    peak subjects with >=2 hyps     : {res['peak_g5_eligible_subjects']}"
              f"   <-- G5 precondition")
        print(f"    peak theories / questions       : {res['peak_theories']} / {res['peak_questions']}")
        print(f"    peak contradictions (Law V fuel) : {res['peak_contradiction_total']}"
              f"  across {res['peak_hypotheses_with_contradictions']} hypothesis(es)")
        print(f"    peak question uncertainty        : {res['peak_question_uncertainty']}")
        print(f"    peak experiment priority (EIG)   : {res['peak_experiment_priority']}")
        print(f"    mean hypothesis confidence       : {res['mean_hypothesis_confidence']}")
        print(f"    ever produced a theory          : {res['ever_produced_theory']}")
        print(f"    ever produced a question        : {res['ever_produced_question']}")
        print(f"    cycles where ceiling saturated  : {res['cycles_where_ceiling_saturated']}"
              f" / {res['cycles']}")
        if res["gate_is_binding_constraint"]:
            print("    => GATE IS BINDING: no subject ever carried two competing")
            print("       hypotheses, so Layer 5 never had anything to coalesce.")
        if res["scaling"]:
            s = res["scaling"]
            print(f"    substrate scaling               : {s['cycle_ms_first']}ms -> {s['cycle_ms_last']}ms"
                  f" over {s['events_last']} events")
            if s.get("ms_per_1000_events") is not None:
                print(f"      marginal cost                 : {s['ms_per_1000_events']} ms per 1000 events")

    print("\n" + "=" * 78)
    print("CONCLUSION")
    print("=" * 78)
    runner = next((r for r in results if r["label"] == "continuous_runner_stream"), None)
    control = next((r for r in results if r["label"] == "cross_domain_developer_workflow"), None)
    if runner and control:
        print(f"  Study stream  G5 eligible subjects (peak): {runner['peak_g5_eligible_subjects']}")
        print(f"  Control      G5 eligible subjects (peak): {control['peak_g5_eligible_subjects']}")
        print(f"  Study stream  theories (peak)             : {runner['peak_theories']}")
        print(f"  Control      theories (peak)             : {control['peak_theories']}")
        if runner["gate_is_binding_constraint"] and control["ever_produced_theory"]:
            print("\n  FINDING: the G5 gate is a property of the STUDY EVENT STREAM, not")
            print("  of the engine. The control stream -- which reuses the same event")
            print("  vocabulary but in tight repeating loops -- produces competing")
            print("  expectations on the same subject and therefore coalesces into")
            print("  theories. The study stream rotates through 30 unrelated events,")
            print("  so every subject keeps exactly one expectation and G5 can never fire.")
            print("\n  CONSEQUENCE: the 90-day longitudinal study as currently configured")
            print("  would record a flat G4 line. Running it for 90 days would produce")
            print("  no data about theories, questions, or the EIG curiosity economy.")
        else:
            print("\n  FINDING: inconclusive -- see per-cycle detail in the JSON report.")


def main() -> int:
    ap = argparse.ArgumentParser(description="Diagnose the Organica G5 gap.")
    ap.add_argument("--cycles", type=int, default=10,
                    help="sleep cycles per stream (default: 10)")
    ap.add_argument("--out", type=str, default="docs/g5_gap_diagnostic.json",
                    help="path for the JSON report")
    args = ap.parse_args()

    results = [run_runner_stream(args.cycles),
               run_developer_workflow(args.cycles),
               run_longitudinal_candidate(args.cycles)]
    print_summary(results)

    out = Path(__file__).parent.parent / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "phase": "G",
        "title": "G5 Gap Diagnostic (Theories/Questions never emerge)",
        "method": "Instrumented the Layer 5 precondition (>=2 hypotheses per subject) and "
                  "compared the resulting ceiling against actual production, across the "
                  "longitudinal-study stream and the Phase F positive control.",
        "streams": results,
    }, indent=2))
    print(f"\n  Full report written to: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
