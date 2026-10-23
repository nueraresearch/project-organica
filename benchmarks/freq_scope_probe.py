"""
Milestone M0.5 - mechanism closure probe.

Two questions, one run.

QUESTION 1 - the scope defect
------------------------------
`MemoryService.store()` builds co-occurrence and temporal edges only from
world events:

    if event_type != "sleep":
        self._record_cooccurrences(event.tags)
        self._record_temporal_edges(event.tags)

but the tag-frequency counter is maintained for *every* event, sleep
payloads included:

    self._record_tag_counts(event.tags)

and `tag_frequencies()` reads that counter. That counter is the
**denominator of the Layer-1 edge strength**:

    ratio   = count / max(source_freq, 1)
    strength = min(1.0, ratio)

so the numerator is world-only and the denominator includes the
organism's own output. A candidate only reaches `stable_prior` when
strength >= STABLE_THRESHOLD (0.3), so the scope mismatch decides which
edges the organism is even allowed to build structure from.

This probe re-runs the same stimuli with the counter restricted to world
events, and reports the difference.

QUESTION 2 - the r=4 / r=6 / r=10 boundary
-----------------------------------------
The first branch generator passed every gate at r=4 and collapsed at r=6
and r=10. "It works at 4" is not an explanation. This probe records the
per-cycle series (window size, beliefs, competing subjects) for all three
so the boundary can be read as a mechanism rather than a lucky point.

Usage:
    python benchmarks/freq_scope_probe.py --cycles 120
Writes docs/freq_scope_probe.json
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.branch_streams import (                # noqa: E402
    NEUTRAL_HUB, NEUTRAL_PETALS, branch_stream, lattice_designs, lattice_stream)
from organica.memory import MemoryService            # noqa: E402
from organica.sleep import SleepService              # noqa: E402
from organica.streams import EVENTS_PER_CYCLE, STUDY_STREAM  # noqa: E402
from organica.paths import temp_db                   # noqa: E402

MAX_THEORIES = SleepService.MAX_THEORIES
MAX_HYPOTHESES = SleepService.MAX_HYPOTHESES


class WorldFreqMemory(MemoryService):
    """Tag frequencies scoped to the world graph, matching edge scope.

    The stock `tag_frequencies()` counts tags from every stored event,
    including the organism's own sleep payloads. The temporal graph is
    built only from world events, so the frequency that normalises an
    edge count should be scoped the same way.
    """

    def tag_frequencies(self) -> Counter:
        rows = self._conn.execute(
            "SELECT tags FROM events WHERE event_type != 'sleep'").fetchall()
        counts = Counter()
        for (tags,) in rows:
            for tag in (tags or "").split(","):
                if tag:
                    counts[tag] += 1
        return counts


class Instrumented(SleepService):
    def __init__(self, memory):
        super().__init__(memory)
        self.rows = []

    def _compose_processes(self, stable_prior):
        edges = set()
        for c in stable_prior:
            if c.get("type") == "prediction_candidate":
                s, t = c.get("source", ""), c.get("target", "")
                if s and t:
                    edges.add((s, t))
        self._window = len(edges)
        return super()._compose_processes(stable_prior)

    def _retain_hypotheses(self, beliefs, info, temporal):
        pre = Counter(h.subject for h in beliefs)
        kept = super()._retain_hypotheses(beliefs, info, temporal)
        post = Counter(h.subject for h in kept)
        self.rows.append({
            "window": getattr(self, "_window", 0),
            "pre_beliefs": len(beliefs),
            "pre_ge2": sum(1 for c in pre.values() if c >= 2),
            "post_ge2": sum(1 for c in post.values() if c >= 2),
        })
        return kept


def evaluate(name: str, events: list[str], cycles: int, scope: str) -> dict:
    db = temp_db(f"probe_{name}_{scope}.db")
    if db.exists():
        db.unlink()
    mem_cls = WorldFreqMemory if scope == "world" else MemoryService
    mem = mem_cls(db_path=str(db))
    svc = Instrumented(mem)

    for text in events:
        mem.store(text, event_type="event", source="seed:bootstrap")
    t0 = time.time()
    theory_counts = []
    for i in range(cycles):
        start = (i * EVENTS_PER_CYCLE) % len(events)
        for text in events[start:start + EVENTS_PER_CYCLE]:
            mem.store(text, event_type="event", source=f"cycle:{i}")
        rep = svc.run_sleep_cycle()
        theory_counts.append(len(rep.theories))
    elapsed = time.time() - t0
    mem.close()
    db.unlink(missing_ok=True)

    rows = svc.rows
    tail = rows[len(rows) // 2:] or rows

    def tail_stat(key):
        vals = [r[key] for r in tail]
        if not vals:
            return 0.0, 0
        return round(statistics.fmean(vals), 3), max(vals)

    win_mean, win_max = tail_stat("window")
    bel_mean, bel_max = tail_stat("pre_beliefs")
    ge2_mean, ge2_max = tail_stat("pre_ge2")
    post_mean, post_max = tail_stat("post_ge2")

    gate_hits = sum(1 for r in tail
                    if r["pre_beliefs"] > MAX_HYPOTHESES
                    and r["pre_ge2"] >= 3
                    and r["pre_beliefs"] > 0)
    sustained = gate_hits / len(tail) if tail else 0.0
    zero = sum(1 for r in tail if r["pre_beliefs"] == 0)

    return {
        "design": name,
        "freq_scope": scope,
        "events": len(events),
        "seconds": round(elapsed, 1),
        "window_mean": win_mean,
        "window_max": win_max,
        "beliefs_mean": bel_mean,
        "beliefs_max": bel_max,
        "ge2_mean": ge2_mean,
        "ge2_max": ge2_max,
        "post_ge2_max": post_max,
        "theories_mean": round(statistics.fmean(theory_counts), 3) if theory_counts else 0,
        "theories_max": max(theory_counts) if theory_counts else 0,
        "pressure_mean": round(bel_mean / MAX_HYPOTHESES, 3),
        "sustained_frac": round(sustained, 3),
        "zero_belief_frac": round(zero / len(tail), 3) if tail else 0,
        "series": [r["window"] for r in rows],
        "series_beliefs": [r["pre_beliefs"] for r in rows],
        "gates": {
            "G_CS": ge2_max >= 3 and 5 <= ge2_max <= 7,
            "G_P1": bel_max > MAX_HYPOTHESES,
            "G_SUP": bel_max > MAX_HYPOTHESES,
            "G_EXP": max(theory_counts) < MAX_THEORIES if theory_counts else False,
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=120)
    ap.add_argument("--out", default=str(REPO / "docs" / "freq_scope_probe.json"))
    args = ap.parse_args()

    designs = []
    designs.append(("study", list(STUDY_STREAM)))
    for r in (4, 6, 10):
        designs.append((f"branch_r{r}",
                        branch_stream(n_subjects=5, successors_per_subject=2, repeats=r)))
    lattice = lattice_designs(NEUTRAL_HUB, NEUTRAL_PETALS)
    for name, spec in lattice.items():
        designs.append((name, lattice_stream(spec["triangles"])))

    rows = []
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    def flush():
        out_path.write_text(json.dumps({
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "cycles": args.cycles,
            "purpose": "M0.5 - is the tag-frequency scope the collapse mechanism?",
            "rows": list(rows),
        }, indent=2), encoding="utf-8")

    for name, events in designs:
        for scope in ("all", "world"):
            r = evaluate(name, events, args.cycles, scope)
            rows.append(r)
            flush()
            g = r["gates"]
            print(f"{name:<22} scope={scope:<6} win={r['window_mean']:>6.2f}/{r['window_max']:<3} "
                  f"bel={r['beliefs_mean']:>6.2f}/{r['beliefs_max']:<3} "
                  f"ge2={r['ge2_mean']:>5.2f}/{r['ge2_max']:<3} "
                  f"T={r['theories_mean']:>5.2f}/{r['theories_max']:<2} "
                  f"sus={r['sustained_frac']:>5.2f} zero={r['zero_belief_frac']:>5.2f} "
                  f"CS:{'Y' if g['G_CS'] else 'n'} P1:{'Y' if g['G_P1'] else 'n'} "
                  f"SUP:{'Y' if g['G_SUP'] else 'n'} EXP:{'Y' if g['G_EXP'] else 'n'}")
            sys.stdout.flush()

    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
