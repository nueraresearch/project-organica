"""
build.py
------------------------------------------------------------------
Build a Project Organica organism from nothing and watch it construct
its own cognition.

This is the entry point for someone who has never seen the project. It
needs no setup beyond Python 3.11+, it writes only into `.scratch/`, and
it leaves the live study database alone.

    python build.py

What it does, in order:

  1. Creates an empty substrate.
  2. Feeds it raw text events -- no schema, no labels, no categories.
  3. Runs sleep cycles, printing what emerges at each layer.
  4. Reports the developmental ladder, the integrity of the lineage, and
     whether the epistemic (curiosity) economy is actually running.

Other modes:

    python build.py --domain robot_simulation   # build in one world
    python build.py --all                       # all four reproduction domains
    python build.py --cycles 12                 # longer build, more depth
    python build.py --keep                      # keep the scratch database
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from organica import MemoryService, SleepService  # noqa: E402
from organica.paths import scratch_db  # noqa: E402
from organica.streams import DOMAINS, EVENTS_PER_CYCLE, STUDY_STREAM  # noqa: E402

RULE = "=" * 78


def _counts(report) -> dict:
    """Population counts per layer for one sleep report."""
    return {
        "concepts": len(report.concepts),
        "predictions": len(report.predictions),
        "loops": len(report.loops),
        "meta_concepts": len(report.meta_concepts),
        "processes": len(report.processes),
        "workflows": len(report.workflow_concepts),
        "hypotheses": len(report.hypotheses),
        "theories": len(report.theories),
        "questions": len(report.questions),
        "dreams": len(report.dreams),
        "investigations": len(report.investigations),
        "experiments": len(report.experiments),
    }


def _grounded_pct(memory: MemoryService) -> float:
    """Fraction of candidates whose lineage reaches a Generation 0 event."""
    import sqlite3
    conn = memory._conn
    g0_tags = set()
    for (tags_str,) in conn.execute(
            "SELECT tags FROM events WHERE event_type != 'sleep'").fetchall():
        for tag in (tags_str or "").split(","):
            if tag:
                g0_tags.add(tag)

    by_id = {}
    for (content,) in conn.execute(
            "SELECT content FROM events WHERE event_type='sleep' AND source != 'sleep:meta'"
    ).fetchall():
        try:
            obj = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(obj, dict) and "id" in obj:
            by_id[obj["id"]] = obj

    grounding = {
        "concept_candidate": ("members",),
        "phrase_candidate": ("members",),
        "loop_candidate": ("path",),
        "prediction_candidate": ("source", "target"),
        "anomaly": ("expected", "observed"),
    }

    def resolve(cid, seen=frozenset()):
        node = by_id.get(cid)
        if node is None:
            return False
        if node.get("type") in grounding:
            tags = []
            for field in grounding[node["type"]]:
                value = node.get(field)
                if isinstance(value, str) and value:
                    tags.append(value)
                elif isinstance(value, list):
                    tags.extend(str(v) for v in value if v)
            return any(t in g0_tags for t in tags)
        if cid in seen:
            return False
        seen = seen | {cid}
        parents = node.get("parent_ids") or []
        return any(resolve(p, seen) for p in parents)

    needing = [c for c in by_id.values() if c.get("generation", 1) > 1]
    if not needing:
        return 100.0
    grounded = sum(1 for c in needing if resolve(c["id"]))
    return round(100 * grounded / len(needing), 2)


def build(name: str, description: str, events: list[str], cycles: int,
          keep: bool, quiet: bool = False) -> dict:
    """Grow an organism in one world and report what emerged."""
    db_path = scratch_db(f"build_{name}.db")

    def say(*args):
        if not quiet:
            print(*args)

    say(f"\n{RULE}")
    say(f"  BUILDING: {name}")
    say(f"  {description}")
    say(RULE)
    say(f"  substrate : {db_path}  (empty)")
    say(f"  events    : {len(events)} raw strings, no schema, no labels")
    say(f"  cycles    : {cycles}")
    say("")

    mem = MemoryService(db_path)
    sleep = SleepService(mem)

    # ---- 1. Ingest raw experience -------------------------------------
    t0 = time.time()
    for text in events:
        mem.store(text, event_type="event", source="build:raw")
    say(f"  [1] ingested {mem.count()} experience events "
        f"({time.time() - t0:.2f}s)")

    # ---- 2. Sleep, layer by layer -------------------------------------
    history = []
    dream_categories = set()
    max_uncertainty = 0.0
    max_priority = 0.0
    for cycle in range(cycles):
        # Keep the stream moving so the graph keeps evolving, exactly as
        # the live daemon does.
        start = (cycle * EVENTS_PER_CYCLE) % len(events)
        for text in events[start:start + EVENTS_PER_CYCLE]:
            mem.store(text, event_type="event", source=f"build:cycle:{cycle}")

        t1 = time.time()
        report = sleep.run_sleep_cycle()
        counts = _counts(report)
        history.append(counts)

        grouped = defaultdict(list)
        for h in report.hypotheses:
            if h.expectation != "high_structural_significance":
                grouped[h.subject].append(h)
        competing = sum(1 for v in grouped.values() if len(v) >= 2)
        contradictions = sum(h.contradiction_count for h in report.hypotheses)
        uncertainty = max((q.uncertainty for q in report.questions), default=0.0)
        priority = max((e.priority for e in report.experiments), default=0.0)
        max_uncertainty = max(max_uncertainty, uncertainty)
        max_priority = max(max_priority, priority)
        dream_categories.update(
            getattr(d, "dream_category", "?") for d in report.dreams)

        say(f"  [2] cycle {cycle + 1:>2} ({time.time() - t1:>5.2f}s)  "
            f"concepts {counts['concepts']:>2}  loops {counts['loops']:>2}  "
            f"workflows {counts['workflows']:>2}  hyps {counts['hypotheses']:>2}  "
            f"theories {counts['theories']}  questions {counts['questions']}  "
            f"dreams {counts['dreams']:>2}  exps {counts['experiments']}")
        say(f"          competing subjects: {competing}   "
            f"contradictions: {contradictions}   "
            f"max uncertainty: {uncertainty:.3f}   top priority: {priority:.3f}")

    # ---- 3. The ladder -------------------------------------------------
    final = history[-1]
    say("")
    say(f"  [3] DEVELOPMENTAL LADDER")
    ladder = [
        ("Gen 0", "Experience events", mem.count()),
        ("Gen 1", "Concepts", final["concepts"]),
        ("Gen 1", "Predictions", final["predictions"]),
        ("Gen 1", "Loops", final["loops"]),
        ("Gen 2", "Meta-concepts", final["meta_concepts"]),
        ("Gen 2", "Processes", final["processes"]),
        ("Gen 3", "Workflow concepts", final["workflows"]),
        ("Gen 4", "Hypotheses", final["hypotheses"]),
        ("Gen 5", "Theories", final["theories"]),
        ("Gen 5", "Questions", final["questions"]),
        ("Gen 6", "Dreams", final["dreams"]),
        ("Gen 7", "Investigations", final["investigations"]),
        ("Gen 8", "Experiments", final["experiments"]),
    ]
    for gen, label, value in ladder:
        bar = "#" * min(value, 40)
        say(f"        {gen}  {label:<22} {value:>4}  {bar}")

    # ---- 4. Integrity --------------------------------------------------
    grounded = _grounded_pct(mem)
    say("")
    say(f"  [4] INTEGRITY (Law II)")
    say(f"        candidates resolving to a Generation 0 experience event: {grounded}%")
    say(f"        experience events retained (never evicted):             {mem.count()}")

    # ---- 5. Epistemic activity ----------------------------------------
    say("")
    say(f"  [5] EPISTEMIC ACTIVITY (Law V)")
    if final["theories"] > 0 and final["questions"] > 0:
        say("        Generation 5 REACHED: competing hypotheses coalesced into")
        say("        theories, and the uncertainty between them is non-zero.")
    else:
        say("        Generation 5 NOT reached in this build. The stream does not")
        say("        give any subject two competing expectations, so Layer 5 had")
        say("        nothing to coalesce. This is a property of the stream, not")
        say("        a failure of the engine -- see benchmarks/g5_gap_diagnostic.py")
    say(f"        dream categories seen : {', '.join(sorted(dream_categories)) or 'none'}")
    say(f"        top experiment priority (EIG / cost): {max_priority:.3f}")
    say(f"        max question uncertainty            : {max_uncertainty:.3f}")

    mem.close()
    if not keep:
        try:
            db_path.unlink()
        except OSError:
            pass

    return {
        "domain": name,
        "description": description,
        "events": len(events),
        "cycles": cycles,
        "final_populations": final,
        "lineage_grounded_pct": grounded,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a Project Organica organism from scratch.")
    parser.add_argument("--domain", default="study",
                        choices=["study", *DOMAINS.keys()],
                        help="which world to build in (default: the study stream)")
    parser.add_argument("--all", action="store_true",
                        help="build in all four reproduction domains")
    parser.add_argument("--cycles", type=int, default=8,
                        help="sleep cycles per build (default: 8)")
    parser.add_argument("--keep", action="store_true",
                        help="keep the scratch database for inspection")
    args = parser.parse_args()

    print(RULE)
    print("  PROJECT ORGANICA -- BUILD FROM SCRATCH")
    print(f"  Python {sys.version.split()[0]}")
    print(RULE)
    print("  Starting from an empty substrate. No pre-trained weights, no")
    print("  hard-coded concepts, no schema. Everything below emerges from")
    print("  the structure of the raw text.")

    results = []
    if args.all:
        for name, (desc, events) in DOMAINS.items():
            results.append(build(name, desc, events, args.cycles, args.keep))
    elif args.domain == "study":
        results.append(build(
            "study_stream",
            "The 90-day longitudinal study stream (branch-structured, so "
            "Generation 5 is reachable)",
            STUDY_STREAM, args.cycles, args.keep))
    else:
        desc, events = DOMAINS[args.domain]
        results.append(build(args.domain, desc, events, args.cycles, args.keep))

    print(f"\n{RULE}")
    print("  SUMMARY")
    print(RULE)
    for r in results:
        f = r["final_populations"]
        print(f"  {r['domain']:<22} lineage {r['lineage_grounded_pct']:>6}%   "
              f"hyps {f['hypotheses']:>3}   theories {f['theories']:>2}   "
              f"questions {f['questions']:>2}   dreams {f['dreams']:>2}   "
              f"experiments {f['experiments']:>2}")
    print()
    print("  Next steps:")
    print("    GETTING-STARTED.md   -- the full guide for a first-time reader")
    print("    docs/USER-MANUAL.md  -- operating the 90-day study")
    print("    python benchmarks/study_health.py  -- health of a running study")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
