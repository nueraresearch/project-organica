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
    from organica.memory import MemoryService
    from organica.sleep import SleepService
except Exception as exc:
    log.error("Failed to import Organica modules: %s", exc)
    raise

# ---------------------------------------------------------------------------
# Domain event streams (four realistic domains that grow richer over time)
# ---------------------------------------------------------------------------
DOMAIN_EVENTS = [
    # Developer workflow
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
    # Bug tracking
    ("issue reported in production system", "event"),
    ("issue assigned to developer team", "event"),
    ("fix committed to feature branch", "event"),
    ("regression test added for fix", "event"),
    ("issue closed after verification", "event"),
    ("duplicate issue linked to original", "event"),
    # Synthetic ecology
    ("resource consumed by organism", "event"),
    ("organism reproduced successfully", "event"),
    ("resource depleted triggering migration", "event"),
    ("predator prey interaction observed", "event"),
    ("population stabilised after peak", "event"),
    # Robot simulation
    ("sensor reading acquired from environment", "event"),
    ("action planned based on sensor data", "event"),
    ("action executed by actuator", "event"),
    ("collision detected requiring replanning", "event"),
    ("goal reached after navigation sequence", "event"),
    ("battery low triggering return to dock", "event"),
]

# ---------------------------------------------------------------------------
# Bootstrap: create persistent memory + service
# ---------------------------------------------------------------------------
memory = MemoryService()
sleep_service = SleepService(memory)

# Seed the memory once with ALL domain events before the first cycle
for text, etype in DOMAIN_EVENTS:
    memory.store(text, event_type=etype, source="seed:bootstrap")

log.info(
    "Organica continuous runner started. MAX_CYCLES=%s, interval=%ss",
    MAX_CYCLES if MAX_CYCLES else "unlimited",
    get_interval(),
)

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
cycle_count = 0
total_composites = 0

while True:
    cycle_start = time.time()

    # Inject a rotating slice of domain events each cycle to keep signal fresh
    slice_start = (cycle_count * 4) % len(DOMAIN_EVENTS)
    for text, etype in DOMAIN_EVENTS[slice_start:slice_start + 4]:
        memory.store(text, event_type=etype, source=f"cycle:{cycle_count}")

    try:
        report = sleep_service.run_sleep_cycle()

        total_composites += report.composites_created

        summary = {
            "cycle": cycle_count,
            "sleep_cycle": report.cycle,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "concepts": len(report.concepts),
            "predictions": len(report.predictions),
            "loops": len(report.loops),
            "hypotheses": len(report.hypotheses),
            "theories": len(report.theories),
            "questions": len(report.questions),
            "dreams": len(report.dreams),
            "investigations": len(report.investigations),
            "experiments": len(report.experiments),
            "composites_created": report.composites_created,
            "total_composites": total_composites,
            "candidates_strengthened": report.candidates_strengthened,
            "candidates_pruned": report.candidates_pruned,
        }
        log.info("Cycle %s: %s", cycle_count, json.dumps(summary))

    except Exception as exc:
        log.exception("Error during sleep cycle %s: %s", cycle_count, exc)

    cycle_count += 1

    # Stop condition
    if MAX_CYCLES and cycle_count >= MAX_CYCLES:
        log.info("Reached MAX_CYCLES=%s – exiting.", MAX_CYCLES)
        break

    # Sleep until next cycle (respects live edits to INTERVAL file)
    elapsed = time.time() - cycle_start
    sleep_time = max(0, get_interval() - elapsed)
    time.sleep(sleep_time)
