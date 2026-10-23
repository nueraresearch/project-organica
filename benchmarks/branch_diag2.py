"""
Stimulus diagnostic: why does the prediction window hold what it holds?

The first lattice sweep measured a result that refuted the working
hypothesis. `MAX_PREDICTIONS` was raised 20 -> 48 and the surviving
prediction window barely moved (4.6 -> 8.0 edges for L2). So the window is
not limited by the cap; it is limited by which candidates *survive* into
`stable_prior`, and the top of the temporal graph is not the branch
structure.

This script prints the three layers that matter, per stimulus:

  1. the top temporal edges by count  (what Layer 1 ranks)
  2. the edges that survived into `stable_prior` (what Layer 2 sees)
  3. the processes, workflows and beliefs that resulted

Usage:
    python benchmarks/branch_diag2.py --design L2 --cycles 60
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.branch_streams import (                # noqa: E402
    NEUTRAL_HUB, NEUTRAL_PETALS, lattice_designs, lattice_stream)
from organica.memory import MemoryService            # noqa: E402
from organica.sleep import SleepService              # noqa: E402
from organica.streams import EVENTS_PER_CYCLE        # noqa: E402
from organica.paths import temp_db                   # noqa: E402


class Diag(SleepService):
    def __init__(self, memory):
        super().__init__(memory)
        self.window = []
        self.last_processes = []
        self.last_workflows = []
        self.last_beliefs = []
        self.temporal = {}

    def _load_temporal(self):
        t = super()._load_temporal()
        self.temporal = t
        return t

    def _compose_processes(self, stable_prior):
        edges = []
        for c in stable_prior:
            if c.get("type") == "prediction_candidate":
                s, t = c.get("source", ""), c.get("target", "")
                if s and t:
                    edges.append((s, t, round(c.get("strength", 0), 3),
                                  c.get("evidence", {}).get("temporal_count", 0)))
        self.window = edges
        procs = super()._compose_processes(stable_prior)
        self.last_processes = [(p.cycle, p.strength) for p in procs]
        return procs

    def _compose_workflows(self, meta_concepts, processes, stable_prior):
        wfs = super()._compose_workflows(meta_concepts, processes, stable_prior)
        self.last_workflows = [w.components for w in wfs]
        return wfs

    def _retain_hypotheses(self, beliefs, info, temporal):
        kept = super()._retain_hypotheses(beliefs, info, temporal)
        self.last_beliefs = [(h.subject, h.expectation) for h in beliefs]
        return kept


def run(name: str, events: list[str], cycles: int) -> dict:
    db = temp_db(f"diag2_{name}.db")
    if db.exists():
        db.unlink()
    mem = MemoryService(db_path=str(db))
    svc = Diag(mem)
    for text in events:
        mem.store(text, event_type="event", source="seed:bootstrap")
    for i in range(cycles):
        start = (i * EVENTS_PER_CYCLE) % len(events)
        for text in events[start:start + EVENTS_PER_CYCLE]:
            mem.store(text, event_type="event", source=f"cycle:{i}")
        svc.run_sleep_cycle()

    # Top temporal edges by count, the way Layer 1 ranks them.
    ranked = []
    for src, tgts in svc.temporal.items():
        for tgt, count in tgts.items():
            ranked.append((count, src, tgt))
    ranked.sort(reverse=True)

    # The survival filter: Layer 1 ranks by count, but a candidate only
    # reaches `stable_prior` if strength >= STABLE_THRESHOLD, and
    # strength = min(1, count / source_frequency). So the edge that dies
    # is the one whose SOURCE tag is common.
    freqs = dict(mem.tag_frequencies())
    survived = {(s, t) for s, t, _, _ in svc.window}
    edge_table = []
    for count, src, tgt in ranked[:40]:
        sf = max(freqs.get(src, 1), 1)
        edge_table.append({
            "count": count,
            "src": src,
            "tgt": tgt,
            "source_freq": sf,
            "ratio": round(min(1.0, count / sf), 3),
            "survived": (src, tgt) in survived,
        })

    mem.close()
    db.unlink(missing_ok=True)
    return {
        "design": name,
        "events": len(events),
        "edges_total": len(ranked),
        "edges_eligible": sum(1 for c, _, _ in ranked if c >= SleepService.PREDICTION_MIN_COUNT),
        "top_edges": ranked[:25],
        "edge_table": edge_table,
        "tag_freqs": {t: freqs.get(t, 0) for t in sorted(freqs)},
        "window": svc.window,
        "processes": svc.last_processes,
        "workflows": svc.last_workflows,
        "beliefs": svc.last_beliefs,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--design", default="L2_hub1_t3_shared")
    ap.add_argument("--cycles", type=int, default=60)
    ap.add_argument("--out", default=str(REPO / ".scratch" / "branch_diag2.json"))
    args = ap.parse_args()

    designs = lattice_designs(NEUTRAL_HUB, NEUTRAL_PETALS)
    if args.design == "study":
        from organica.streams import STUDY_STREAM
        events = list(STUDY_STREAM)
    else:
        spec = designs[args.design]
        events = lattice_stream(spec["triangles"])
    r = run(args.design, events, args.cycles)

    print(f"=== {r['design']} ===")
    print(f"events={r['events']} edges_total={r['edges_total']} "
          f"eligible={r['edges_eligible']} (cap={SleepService.MAX_PREDICTIONS})")
    print(f"\n-- top 25 temporal edges by count (what Layer 1 ranks) --")
    for count, src, tgt in r["top_edges"]:
        print(f"   {count:>5}  {src} -> {tgt}")
    print(f"\n-- surviving window ({len(r['window'])} edges) --")
    for s, t, strength, count in r["window"]:
        print(f"   count={count:>5} strength={strength:<6} {s} -> {t}")
    print(f"\n-- processes ({len(r['processes'])}) --")
    for cycle, strength in r["processes"]:
        print(f"   {cycle} strength={strength}")
    print(f"\n-- workflows ({len(r['workflows'])}) --")
    for comps in r["workflows"]:
        print(f"   {comps}")
    print(f"\n-- beliefs ({len(r['beliefs'])}) --")
    for s, e in r["beliefs"]:
        print(f"   {s} -> {e}")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(r, indent=2), encoding="utf-8")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
