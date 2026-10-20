"""
Phase G: Long-Term Endurance Soak Daemon
=========================================
Runs Organica continuously, simulating a realistic mixed environment stream.
Measures memory growth, candidate survival, theory turnover, dream generation,
and experiment prioritization over extended periods.

Usage:
    python benchmarks/endurance_soak.py           # runs for 10 cycles (quick test)
    python benchmarks/endurance_soak.py --hours 1  # runs for 1 hour
    python benchmarks/endurance_soak.py --hours 24  # full 24-hour soak

Output:
    docs/soak_report_<timestamp>.json
"""

import argparse
import json
import time
import signal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from organica import MemoryService, SleepService

# Mixed-domain stream simulating a running developer environment
STREAM_TEMPLATES = [
    "developer modified {module} source code",
    "developer executed test suite validation",
    "test suite report: {n} failures {m} passed",
    "failure detected in {module} handler",
    "developer modified {module} handler fixed",
    "test suite report: passed validation clean",
    "system monitor cpu usage {pct} percent",
    "system monitor memory allocation {mb} megabytes",
    "scheduler task {task} dispatched queue",
    "scheduler task {task} completed success",
    "user session login authenticated",
    "user session logout timeout expired",
    "api request endpoint {endpoint} received",
    "api response status {code} delivered",
    "database query executed records fetched",
    "cache miss lookup storage retrieved",
]

MODULES   = ["auth", "router", "session", "payment", "notify", "search"]
TASKS     = ["backup", "cleanup", "report", "sync", "audit"]
ENDPOINTS = ["login", "logout", "profile", "search", "checkout"]

import random
random.seed(42)

def make_event(i: int) -> str:
    tmpl = STREAM_TEMPLATES[i % len(STREAM_TEMPLATES)]
    return tmpl.format(
        module=MODULES[i % len(MODULES)],
        n=random.randint(0, 5),
        m=random.randint(45, 50),
        pct=random.randint(10, 90),
        mb=random.randint(256, 4096),
        task=TASKS[i % len(TASKS)],
        endpoint=ENDPOINTS[i % len(ENDPOINTS)],
        code=random.choice([200, 201, 400, 404, 500]),
    )


_shutdown = False

def _handle_signal(sig, frame):
    global _shutdown
    print("\n[SOAK] Shutdown signal received. Finishing current cycle...")
    _shutdown = True

signal.signal(signal.SIGINT, _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)


def run_soak(duration_seconds: float, events_per_cycle: int = 20):
    db = Path("organica_soak.db")
    mem = MemoryService(db)
    sleep = SleepService(mem)

    start_time = time.time()
    deadline = start_time + duration_seconds
    cycle = 0
    event_counter = 0
    telemetry = []

    print(f"[SOAK] Starting endurance soak. Duration: {duration_seconds:.0f}s | DB: {db}")
    print(f"[SOAK] Events per cycle: {events_per_cycle}")
    print(f"[SOAK] {'Cycle':>6}  {'Events':>8}  {'Concepts':>8}  {'Procs':>6}  "
          f"{'Hyps':>5}  {'Qs':>4}  {'EXPs':>5}  {'Candidates':>10}  {'Cycle_ms':>9}")
    print("-" * 85)

    while time.time() < deadline and not _shutdown:
        cycle += 1

        # Ingest a batch of mixed-domain events
        for j in range(events_per_cycle):
            mem.store(make_event(event_counter), event_type="observe", source="soak")
            event_counter += 1

        # Run one sleep consolidation
        t0 = time.time()
        report = sleep.run()
        cycle_ms = round((time.time() - t0) * 1000, 1)

        # Lineage check (lightweight: sample up to 20 candidates)
        priors = sleep._load_prior_candidates()
        id_set = {c.get("id") for c in priors if "id" in c}
        non_g1 = [c for c in priors if c.get("generation", 1) > 1 and "parent_ids" in c][:20]
        total_links = sum(len(c.get("parent_ids", [])) for c in non_g1)
        verified = sum(1 for c in non_g1 for pid in c.get("parent_ids", []) if pid in id_set)
        lineage_ok = (verified == total_links)

        snapshot = {
            "cycle": cycle,
            "elapsed_s": round(time.time() - start_time, 1),
            "total_events": event_counter,
            "total_candidates": len(priors),
            "concepts": len(report.concepts),
            "processes": len(report.processes),
            "workflow_concepts": len(report.workflow_concepts),
            "hypotheses": len(report.hypotheses),
            "theories": len(report.theories),
            "questions": len(report.questions),
            "dreams": len(report.dreams),
            "investigations": len(report.investigations),
            "experiments": len(report.experiments),
            "candidates_strengthened": report.candidates_strengthened,
            "candidates_decayed": report.candidates_decayed,
            "candidates_pruned": report.candidates_pruned,
            "lineage_sample_ok": lineage_ok,
            "cycle_ms": cycle_ms,
        }
        telemetry.append(snapshot)

        print(f"  {cycle:>6}  {event_counter:>8}  {snapshot['concepts']:>8}  "
              f"{snapshot['processes']:>6}  {snapshot['hypotheses']:>5}  "
              f"{snapshot['questions']:>4}  {snapshot['experiments']:>5}  "
              f"{snapshot['total_candidates']:>10}  {cycle_ms:>8.1f}ms  "
              f"{'OK' if lineage_ok else 'LINEAGE-WARN'}")

        # Brief pause so we don't burn 100% CPU in a tight loop
        time.sleep(0.1)

    elapsed = round(time.time() - start_time, 1)
    mem.close()

    # Write soak report
    ts = time.strftime("%Y%m%dT%H%M%S", time.gmtime())
    report_path = Path(__file__).parent.parent / "docs" / f"soak_report_{ts}.json"
    soak_report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "phase": "G",
        "title": "Long-Term Endurance Soak",
        "duration_target_s": duration_seconds,
        "duration_actual_s": elapsed,
        "total_cycles": cycle,
        "total_events": event_counter,
        "final_candidate_pool_size": telemetry[-1]["total_candidates"] if telemetry else 0,
        "all_lineage_checks_passed": all(s["lineage_sample_ok"] for s in telemetry),
        "telemetry": telemetry,
    }
    report_path.write_text(json.dumps(soak_report, indent=2))

    print("\n" + "=" * 85)
    print(f"[SOAK] COMPLETE: {cycle} cycles | {event_counter} events | {elapsed}s elapsed")
    print(f"[SOAK] Final candidate pool: {soak_report['final_candidate_pool_size']}")
    print(f"[SOAK] All lineage checks passed: {soak_report['all_lineage_checks_passed']}")
    print(f"[SOAK] Report: {report_path}")
    return soak_report


def main():
    parser = argparse.ArgumentParser(description="Organica Endurance Soak Daemon")
    parser.add_argument("--hours", type=float, default=None, help="Duration in hours")
    parser.add_argument("--minutes", type=float, default=None, help="Duration in minutes")
    parser.add_argument("--cycles", type=int, default=10, help="Number of cycles (if no time given)")
    parser.add_argument("--events-per-cycle", type=int, default=20, help="Events per sleep cycle")
    args = parser.parse_args()

    if args.hours:
        duration = args.hours * 3600
    elif args.minutes:
        duration = args.minutes * 60
    else:
        # Quick finite run: estimate duration from cycles * ~0.5s/cycle
        duration = args.cycles * 0.5

    run_soak(duration_seconds=duration, events_per_cycle=args.events_per_cycle)


if __name__ == "__main__":
    main()
