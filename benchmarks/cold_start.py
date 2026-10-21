"""
benchmarks/cold_start.py
------------------------------------------------------------------
How much assistance does Organica actually need?

The long-horizon question for this project is:

    "Would Generation 1 have built out the generations above it, with no
     assistance and no code changes on our side?"

The 90-day study cannot answer that question, because the current setup
contains assistance at four levels that are easy to miss:

  1. **Pre-seeding.** The daemon loads 48 events into an empty substrate
     *before* the first sleep cycle. A newborn organism does not arrive
     with a populated graph.
  2. **An engineered branch point.** The study stream is hand-designed so
     that one subject is followed by both a positive and a negative
     outcome. That is precisely what Generation 5 needs. A real-world
     stream was never designed to cooperate.
  3. **Hand-coded domain knowledge.** `memory.py` excludes "test" and
     "file" as tags, with the comment "too generic for a dev env -- we'll
     revisit this". That is a domain decision baked into the substrate.
  4. **Fixed sampling.** Exactly 8 events per cycle, in a fixed rotation,
     with a 3-event temporal lookback.

This script removes those one at a time and measures what still emerges.
It never edits the engine: ablations are applied in-process by subclassing
or by rebinding module attributes.

The reference condition is a genuine, unengineered stream -- the commit
messages in this repository's own git history. Nobody designed those to
have branch points, and they are present in every clone, so the result is
reproducible for any reader.

Usage:
    python benchmarks/cold_start.py
    python benchmarks/cold_start.py --cycles 60 --out docs/cold_start.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import organica.memory as memory_module  # noqa: E402
from organica import MemoryService, SleepService  # noqa: E402
from organica.paths import REPO_ROOT, temp_db  # noqa: E402
from organica.streams import STUDY_STREAM  # noqa: E402


# ---------------------------------------------------------------------------
# Generations we care about, in ladder order
# ---------------------------------------------------------------------------
GENERATIONS = [
    ("G1 concepts", "concepts"),
    ("G1 loops", "loops"),
    ("G1 predictions", "predictions"),
    ("G2 meta-concepts", "meta_concepts"),
    ("G2 processes", "processes"),
    ("G3 workflows", "workflow_concepts"),
    ("G4 hypotheses", "hypotheses"),
    ("G5 theories", "theories"),
    ("G5 questions", "questions"),
    ("G6 dreams", "dreams"),
    ("G7 investigations", "investigations"),
    ("G8 experiments", "experiments"),
]


# ---------------------------------------------------------------------------
# An unengineered stream: this repository's own commit history
# ---------------------------------------------------------------------------
def git_commit_stream(limit: int = 400) -> list[str]:
    """Real developer activity, from the repository's own git history.

    Nobody designed these messages to produce competing expectations, so
    whatever Generation 5 does here, it does on its own.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "log", f"-{limit}", "--pretty=format:%s"],
            capture_output=True, text=True, timeout=60, check=True,
        ).stdout
    except Exception:
        return []
    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    return lines


# ---------------------------------------------------------------------------
# The unbranched stream: 30 unrelated events, the original study stream
# ---------------------------------------------------------------------------
UNBRANCHED_STREAM = [
    "function called with arguments", "test passed after code modification",
    "auth failure on login attempt", "session expired triggering re-auth",
    "build pipeline triggered on push", "tests passed all suites green",
    "deployment succeeded to staging", "auth session renewed successfully",
    "pull request merged into main branch", "code review approved by reviewer",
    "test failed due to assertion error", "hotfix branch created for critical bug",
    "issue reported in production system", "issue assigned to developer team",
    "fix committed to feature branch", "regression test added for fix",
    "issue closed after verification", "duplicate issue linked to original",
    "resource consumed by organism", "organism reproduced successfully",
    "resource depleted triggering migration", "predator prey interaction observed",
    "population stabilised after peak", "sensor reading acquired from environment",
    "action planned based on sensor data", "action executed by actuator",
    "collision detected requiring replanning", "goal reached after navigation sequence",
    "battery low triggering return to dock",
]


# ---------------------------------------------------------------------------
# Memory variants used by the ablations
# ---------------------------------------------------------------------------
class WideLookbackMemory(MemoryService):
    """MemoryService with a much wider temporal lookback (3 -> 30)."""

    def _record_temporal_edges(self, new_tags, lookback: int = 30):
        return super()._record_temporal_edges(new_tags, lookback=lookback)


def _patched_extract_tags_factory(stopword_overrides: dict[str, set[str]]):
    """Build a tag extractor with a different stopword set.

    `_extract_tags` is looked up on the module at call time inside
    `MemoryService.store`, so rebinding it here changes the behaviour
    without touching the engine source.
    """
    original = memory_module._extract_tags
    base_stop = original.__globals__["stopwords"] if "stopwords" in original.__globals__ else None

    def _extract_tags(content: str) -> list[str]:
        words = memory_module.re.findall(r"\b[a-zA-Z]{4,}\b", content.lower())
        stop = set(base_stop or set())
        for word, extra in stopword_overrides.items():
            if word in stop:
                stop.discard(word)
        seen, tags = set(), []
        for w in words:
            if w not in stop and w not in seen:
                seen.add(w)
                tags.append(w)
        return tags[:8]

    return _extract_tags


# ---------------------------------------------------------------------------
# One experimental condition
# ---------------------------------------------------------------------------
def run_condition(name: str, description: str, events: list[str], cycles: int,
                  seed: bool, per_cycle: int, memory_cls=MemoryService,
                  stopword_overrides: dict | None = None,
                  max_hypotheses: int | None = None) -> dict:
    """Run one condition and record when each generation first appeared."""
    original_extract = memory_module._extract_tags
    original_max = SleepService.MAX_HYPOTHESES

    if stopword_overrides is not None:
        memory_module._extract_tags = _patched_extract_tags_factory(stopword_overrides)
    if max_hypotheses is not None:
        SleepService.MAX_HYPOTHESES = max_hypotheses

    db_path = temp_db(f"{name}.db")
    mem = memory_cls(db_path)
    try:
        if seed:
            for text in events:
                mem.store(text, event_type="event", source="seed:bootstrap")

        sleep = SleepService(mem)
        first_seen: dict[str, int] = {}
        n = len(events)
        for cycle in range(cycles):
            if not seed:
                # Unassisted: the world arrives one event at a time.
                for k in range(per_cycle):
                    text = events[(cycle * per_cycle + k) % n]
                    mem.store(text, event_type="event", source=f"cycle:{cycle}")
            else:
                start = (cycle * per_cycle) % n
                for text in events[start:start + per_cycle]:
                    mem.store(text, event_type="event", source=f"cycle:{cycle}")

            report = sleep.run_sleep_cycle()
            for label, attr in GENERATIONS:
                if label not in first_seen and len(getattr(report, attr)) > 0:
                    first_seen[label] = cycle + 1

        last = report
        final = {label: len(getattr(last, attr)) for label, attr in GENERATIONS}
        competing = defaultdict(int)
        for h in last.hypotheses:
            if h.expectation != "high_structural_significance":
                competing[h.subject] += 1
        n_competing = sum(1 for v in competing.values() if v >= 2)

        deepest = 0
        for idx, (label, _) in enumerate(GENERATIONS):
            if label in first_seen:
                deepest = idx + 1

        return {
            "condition": name,
            "description": description,
            "seeded": seed,
            "events_in_stream": len(events),
            "events_per_cycle": per_cycle,
            "cycles": cycles,
            "cycles_to_first_emergence": first_seen,
            "final_populations": final,
            "deepest_generation_reached": deepest,
            "competing_subjects_final": n_competing,
            "experience_events": mem.count(),
        }
    finally:
        mem.close()
        memory_module._extract_tags = original_extract
        SleepService.MAX_HYPOTHESES = original_max
        try:
            db_path.unlink()
        except OSError:
            pass


# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="Cold-start / ablation study.")
    ap.add_argument("--cycles", type=int, default=40,
                    help="sleep cycles per condition (default: 40)")
    ap.add_argument("--out", default="docs/cold_start.json")
    args = ap.parse_args()

    git_stream = git_commit_stream()
    print(f"  unengineered stream: {len(git_stream)} real commit messages from git history")

    conditions = [
        dict(name="baseline",
             description="As the 90-day study runs it: seeded, engineered branch "
                         "stream, 8 events/cycle, default stopwords and truncation.",
             events=STUDY_STREAM, seed=True, per_cycle=8),
        dict(name="no_branch",
             description="The ORIGINAL study stream: 30 unrelated events, no "
                         "engineered branch point. Seeded, 8 events/cycle.",
             events=UNBRANCHED_STREAM, seed=True, per_cycle=8),
        dict(name="cold_start",
             description="NO pre-seeding, 1 event per cycle, engineered stream. "
                         "The world arrives one observation at a time.",
             events=STUDY_STREAM, seed=False, per_cycle=1),
        dict(name="cold_start_unbranched",
             description="NO pre-seeding, 1 event per cycle, unbranched stream. "
                         "The most unassisted condition possible.",
             events=UNBRANCHED_STREAM, seed=False, per_cycle=1),
        dict(name="real_git_history",
             description="NO pre-seeding, 1 event per cycle, and the stream is this "
                         "repository's own commit messages -- genuinely unengineered.",
             events=git_stream, seed=False, per_cycle=1),
        dict(name="no_truncation",
             description="Baseline, but the 15-hypothesis cap raised to 200, to test "
                         "whether the alphabetical truncation is what blocks G5.",
             events=STUDY_STREAM, seed=True, per_cycle=8, max_hypotheses=200),
        dict(name="no_dev_stopwords",
             description="Baseline, but the hand-coded 'test' and 'file' stopwords "
                         "removed, to measure the cost of that domain decision.",
             events=STUDY_STREAM, seed=True, per_cycle=8,
             stopword_overrides={"test": set(), "file": set()}),
        dict(name="wide_lookback",
             description="Baseline, but the temporal lookback widened from 3 to 30 "
                         "events, so the organism can see further back.",
             events=STUDY_STREAM, seed=True, per_cycle=8, memory_cls=WideLookbackMemory),
    ]

    results = []
    for cond in conditions:
        if not cond["events"]:
            print(f"  skipping {cond['name']} (no events available)")
            continue
        t0 = time.time()
        res = run_condition(cycles=args.cycles, **cond)
        res["wall_seconds"] = round(time.time() - t0, 1)
        results.append(res)
        reached = res["deepest_generation_reached"]
        print(f"  {res['condition']:<24} deepest: {reached}/{len(GENERATIONS)}"
              f"   G5 theories: {res['final_populations']['G5 theories']}"
              f"   competing subjects: {res['competing_subjects_final']}"
              f"   ({res['wall_seconds']}s)")

    # ---- report -------------------------------------------------------
    print()
    print("=" * 104)
    print("COLD START / ABLATION -- how much assistance does the architecture need?")
    print("=" * 104)
    labels = [g[0] for g in GENERATIONS]
    header = f"{'condition':<24}" + "".join(f"{l.split()[0]:>4}" for l in labels)
    print(header)
    print("-" * 104)
    for res in results:
        row = f"{res['condition']:<24}"
        for label in labels:
            c = res["cycles_to_first_emergence"].get(label)
            row += f"{c if c else '-':>4}"
        print(row)
    print("-" * 104)
    print("  numbers = sleep cycles until that generation first appeared ('-' = never)")
    print()
    for res in results:
        g5 = res["cycles_to_first_emergence"].get("G5 theories")
        verdict = (f"reached G5 at cycle {g5}" if g5
                   else f"never reached G5 (deepest: {res['deepest_generation_reached']}/{len(GENERATIONS)})")
        print(f"  {res['condition']:<24} {verdict}")

    out = REPO_ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "phase": "G",
        "title": "Cold Start / Ablation Study",
        "method": "Each condition removes one layer of assistance (pre-seeding, the "
                  "engineered branch point, hand-coded stopwords, the temporal "
                  "lookback, the hypothesis cap) and records when each generation "
                  "first emerges. Abridged: the stream is this repository's own git "
                  "commit history, which nobody designed to cooperate.",
        "unengineered_stream_size": len(git_stream),
        "conditions": results,
    }, indent=2))
    print(f"\n  Full report written to: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
