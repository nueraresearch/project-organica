"""
Organica Continuous Runner
--------------------------
Runs the Organica sleep cycle in an infinite loop, accumulating experience
across cycles so the developmental ladder can grow organically.

Design:
  - A SINGLE MemoryService and SleepService are created once at startup
    (persistent across cycles within the same process).
  - Each cycle adds a fresh batch of synthetic domain events THEN sleeps.
  - After the first ~10 cycles the memory graph is dense enough for concepts,
    predictions, hypotheses, theories, questions, dreams, and investigations
    to begin emerging.
  - Every cycle is logged as a compact JSON summary to organica.log.

Stop conditions (checked after each cycle):
  - MAX_CYCLES (default: unlimited / 0 = run forever)
  - INTERVAL file next to this script overrides the sleep interval in seconds.

Usage:
  python run_continuous.py            # run forever, 30s interval
  python run_continuous.py 500        # run for 500 cycles then exit
"""

import json
import logging
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
log_file = Path(__file__).with_name("organica.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("organica.runner")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
INTERVAL_FILE = Path(__file__).with_name("INTERVAL")
DEFAULT_INTERVAL = 30  # seconds between cycles
MAX_CYCLES = int(sys.argv[1]) if len(sys.argv) > 1 else 0  # 0 = infinite

def get_interval():
    if INTERVAL_FILE.exists():
        try:
            return int(INTERVAL_FILE.read_text().strip())
        except ValueError:
            pass
    return DEFAULT_INTERVAL

# ---------------------------------------------------------------------------
# Organica imports
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent))
try:
    from organica.memory import MemoryService, TAG_COUNTS_SCOPE
    from organica.sleep import SleepService
except Exception as exc:
    log.error("Failed to import Organica modules: %s", exc)
    raise

# ---------------------------------------------------------------------------
# Domain event streams
# ---------------------------------------------------------------------------
# DESIGN NOTE (Phase G, 2026-10-21)
#
# The previous stream rotated through 30 unrelated events ("function called
# with arguments", "auth failure on login attempt", ...). A diagnostic
# (benchmarks/g5_gap_diagnostic.py) proved that stream can NEVER reach
# Generation 5: Layer 5 coalesces theories from hypotheses that share a
# subject and carry COMPETING expectations, and in a rotating stream every
# subject keeps exactly one successor. Measured result: 0 theories and 0
# questions across 670 logged cycles, with zero contradictions anywhere --
# so Shannon entropy stayed at 0 and the EIG attention economy (Law V)
# never engaged either. A 90-day study of that stream would have recorded
# a flat G4 line.
#
# The replacement stream below was selected empirically by
# benchmarks/stream_sweep.py, which scored four candidates on G5
# sustainment, question uncertainty, and experiment priority. The winner
# keeps the SAME branch point subject ("developer executed test suite" and
# "engineer committed patch") leading to BOTH a positive and a negative
# outcome, so support and contradiction both accumulate and uncertainty
# stays non-zero.
#
# Adding the ecology and robot domains made matters WORSE (G5 sustainment
# 0.70 -> 0.57): extra workflow structures crowd the hypothesis set, and
# Layer 4's 15-hypothesis cap then truncates away the competing
# expectation that Layer 5 needs. That crowding effect is documented in
# research-journal/phase_g_findings_20261021.md and is a candidate
# architecture amendment for the Phase A unfreeze.
#
# The stream itself lives in organica/streams.py so that the daemon and
# `build.py` share exactly one definition of it.
# ---------------------------------------------------------------------------
from organica.streams import EVENTS_PER_CYCLE, STUDY_STREAM  # noqa: E402


# ---------------------------------------------------------------------------
# Bootstrap: create persistent memory + service
# ---------------------------------------------------------------------------
memory = MemoryService()
sleep_service = SleepService(memory)

# Seed the memory once with ALL study events before the first cycle
for text in STUDY_STREAM:
    memory.store(text, event_type="event", source="seed:bootstrap")

log.info(
    "Organica continuous runner started. MAX_CYCLES=%s, interval=%ss",
    MAX_CYCLES if MAX_CYCLES else "unlimited",
    get_interval(),
)

# BUILD MARKER.
#
# The log is append-only and can span several builds. Without a marker
# there is no way to tell which cycles came from which configuration --
# and on 2026-10-22 that was exactly the problem: the run was stopped so
# the retention-policy change could land, and a reader had no way to see
# where the old build ended. Every startup now records the configuration
# that produced the cycles that follow it.
log.info(
    "BUILD retention=%s caps(hyp=%s,pred=%s,proc=%s,meta=%s,wf=%s) "
    "contradiction_scale=%s markers=%s freq_scope=%s",
    SleepService.HYPOTHESIS_RETENTION,
    SleepService.MAX_HYPOTHESES,
    SleepService.MAX_PREDICTIONS,
    SleepService.MAX_PROCESSES,
    SleepService.MAX_META_CONCEPTS,
    SleepService.MAX_WORKFLOWS,
    SleepService.CONTRADICTION_SCALE,
    SleepService.MAX_STRUCTURAL_MARKERS,
    TAG_COUNTS_SCOPE,
)

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
cycle_count = 0
total_composites = 0
consecutive_errors = 0

while True:
    cycle_start = time.time()

    # Inject a rotating slice of experience events each cycle so the graph
    # keeps evolving. The slice size and stride are the validated
    # parameters from benchmarks/stream_sweep.py.
    slice_start = (cycle_count * EVENTS_PER_CYCLE) % len(STUDY_STREAM)
    for text in STUDY_STREAM[slice_start:slice_start + EVENTS_PER_CYCLE]:
        memory.store(text, event_type="event", source=f"cycle:{cycle_count}")

    status = "success"
    error_msg = None

    try:
        report = sleep_service.run_sleep_cycle()

        total_composites += report.composites_created
        consecutive_errors = 0

        cycle_duration_ms = int((time.time() - cycle_start) * 1000)

        # Bound the substrate. The organism's working memory is the newest
        # 4,000 sleep events and the retention window (20,000 candidates) is
        # comfortably larger, so this changes no cognition -- it only stops
        # the candidate table growing without limit. Measured: 942MB after
        # ~500 cycles, projecting to ~210GB over a 90-day run at a 30s
        # interval.
        pruned_rows = memory.prune_sleep_candidates()

        # Snapshot hypothesis details for lifecycle tracking
        hypothesis_snapshot = [
            {
                "id": getattr(h, "id", None),
                "subject": getattr(h, "subject", None),
                "confidence": round(getattr(h, "confidence", 0), 4),
                "support_count": getattr(h, "support_count", 0),
                "contradiction_count": getattr(h, "contradiction_count", 0),
                "generation": getattr(h, "generation", 0),
            }
            for h in report.hypotheses
        ]

        # Tally dream categories for richer observation
        dream_categories: dict = {}
        for d in report.dreams:
            cat = getattr(d, "dream_category", "unknown")
            dream_categories[cat] = dream_categories.get(cat, 0) + 1

        summary = {
            "cycle": cycle_count,
            "sleep_cycle": report.cycle,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": status,
            "duration_ms": cycle_duration_ms,
            "consecutive_errors": consecutive_errors,
            "concepts": len(report.concepts),
            "predictions": len(report.predictions),
            "loops": len(report.loops),
            "hypotheses": len(report.hypotheses),
            "hypothesis_snapshot": hypothesis_snapshot,
            "theories": len(report.theories),
            "questions": len(report.questions),
            "dreams": len(report.dreams),
            "dream_categories": dream_categories,
            "investigations": len(report.investigations),
            "experiments": len(report.experiments),
            "composites_created": report.composites_created,
            "total_composites": total_composites,
            "candidates_strengthened": report.candidates_strengthened,
            "candidates_pruned": report.candidates_pruned,
            "substrate_rows_pruned": pruned_rows,
        }
        log.info("Cycle %s: %s", cycle_count, json.dumps(summary))

    except Exception as exc:
        consecutive_errors += 1
        error_msg = str(exc)
        cycle_duration_ms = int((time.time() - cycle_start) * 1000)
        error_summary = {
            "cycle": cycle_count,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": "failed",
            "duration_ms": cycle_duration_ms,
            "consecutive_errors": consecutive_errors,
            "error": error_msg,
        }
        log.error("Cycle %s FAILED: %s", cycle_count, json.dumps(error_summary))
        log.exception("Traceback for cycle %s:", cycle_count)

    cycle_count += 1

    # Stop condition
    if MAX_CYCLES and cycle_count >= MAX_CYCLES:
        log.info("Reached MAX_CYCLES=%s – exiting.", MAX_CYCLES)
        break

    # Sleep until next cycle (respects live edits to INTERVAL file)
    elapsed = time.time() - cycle_start
    sleep_time = max(0, get_interval() - elapsed)
    time.sleep(sleep_time)
