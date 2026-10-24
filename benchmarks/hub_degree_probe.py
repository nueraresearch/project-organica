"""
Why do the larger ladder rungs produce nothing?

The Tier-1 stimulus shares ONE hub tag across its three triangles. The
Ladder's larger rungs share one hub across 24 or 144 triangles -- and they
produce **zero** beliefs, zero competing subjects, zero theories.

Hypothesis: the Layer-1 survival filter is
``strength = min(1, count / source_frequency) >= STABLE_THRESHOLD (0.3)``.
For a hub of degree N, each hub edge has count k (the block repeat) and the
hub's source frequency is N*k, so the ratio is exactly **1/N**. The Tier-1
design sits at N = 3, where the ratio is 1/3 = 0.333 -- just above the
threshold. N = 4 puts it at 0.25 and every hub edge dies.

If that is right, the ladder must scale by the number of HUBS, never by the
degree of one hub. This probe measures it rather than assuming it.

Usage:
    python benchmarks/hub_degree_probe.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks.force_matrix import Instrumented  # noqa: E402


class Diag(Instrumented):
    """Captures the surviving Layer-1 window and the temporal graph.

    `self.window` is the list of edges that reached `stable_prior`, i.e. the
    edges whose `strength = min(1, count / source_frequency)` cleared
    STABLE_THRESHOLD. `self.temporal` is the raw temporal graph.
    """

    def __init__(self, memory):
        super().__init__(memory)
        self.window = []
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
        return super()._compose_processes(stable_prior)


def probe(degree: int, cycles: int, seed: int = 20261023) -> dict:
    from organica.memory import MemoryService
    from organica.paths import temp_db
    from organica.scale_streams import expanding_triangles, scale_stream
    from organica.sleep import SleepService
    from organica.streams import EVENTS_PER_CYCLE

    hub = "alpha"
    triangles = expanding_triangles(degree, hub=hub)
    events = scale_stream(triangles, mode="block", block_repeat=4)

    db = temp_db(f"hubdeg_{degree}.db")
    if db.exists():
        db.unlink()
    mem = MemoryService(db_path=str(db))
    svc = Diag(mem)
    if hasattr(svc, "_rng"):
        svc._rng.seed(seed)
    for text in events:
        mem.store(text, event_type="event", source="seed:bootstrap")
    for i in range(cycles):
        start = (i * EVENTS_PER_CYCLE) % len(events)
        for text in events[start:start + EVENTS_PER_CYCLE]:
            mem.store(text, event_type="event", source=f"cycle:{i}")
        svc.run_sleep_cycle()

    freqs = dict(mem.tag_frequencies())
    survived = {(s, t) for s, t, _, _ in svc.window}
    ranked = []
    for src, tgts in svc.temporal.items():
        for tgt, count in tgts.items():
            ranked.append((count, src, tgt))
    ranked.sort(reverse=True)

    hub_edges = [(c, s, t) for (c, s, t) in ranked if s == hub]
    ratios = []
    for count, src, tgt in hub_edges:
        sf = max(freqs.get(src, 1), 1)
        ratios.append(min(1.0, count / sf))
    alive = [(s, t) for (s, t, _, _) in svc.window]
    alive_hub = [(s, t) for (s, t) in alive if s == hub]

    # the belief-level outcome
    beliefs = set()
    for r in svc.rows:
        for b in r.get("beliefs", []):
            beliefs.add(b.get("id"))
    last = svc.rows[-1] if svc.rows else {}
    belief_count = len(last.get("beliefs", []))
    pre = last.get("pre_beliefs")
    ge2 = last.get("pre_ge2")

    mem.close()
    db.unlink(missing_ok=True)
    return {
        "degree": degree,
        "hub_edges": len(hub_edges),
        "hub_edge_ratio": round(max(ratios), 4) if ratios else None,
        "hub_edge_ratio_min": round(min(ratios), 4) if ratios else None,
        "threshold": SleepService.STABLE_THRESHOLD,
        "hub_edges_survived": len(alive_hub),
        "edges_total": len(ranked),
        "edges_survived_total": len(alive),
        "beliefs_final": belief_count,
        "pre_beliefs_final": pre,
        "competing_subjects_final": ge2,
        "distinct_beliefs_ever": len(beliefs),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=200)
    ap.add_argument("--degrees", nargs="*", type=int,
                    default=[1, 2, 3, 4, 5, 6, 8, 12])
    ap.add_argument("--out",
                    default=str(REPO / "docs" / "hub_degree_probe.json"))
    args = ap.parse_args()

    results = []
    for d in args.degrees:
        r = probe(d, args.cycles)
        results.append(r)
        print(f"  degree {d:<3} hub ratio={str(r['hub_edge_ratio']):<7} "
              f"hub edges alive={r['hub_edges_survived']:<3}/{r['hub_edges']:<3} "
              f"beliefs={r['beliefs_final']:<3} "
              f"pre_beliefs={r['pre_beliefs_final']} "
              f"competing={r['competing_subjects_final']}")

    print()
    print("=" * 100)
    print(f"HUB-DEGREE PROBE -- {args.cycles} cycles, threshold "
          f"{results[0]['threshold']}")
    print("=" * 100)
    print(f"{'degree':<8}{'hub ratio':<12}{'hub alive':<12}"
          f"{'beliefs':<10}{'pre_beliefs':<13}{'competing':<11}")
    for r in results:
        print(f"{r['degree']:<8}{str(r['hub_edge_ratio']):<12}"
              f"{str(r['hub_edges_survived']) + '/' + str(r['hub_edges']):<12}"
              f"{r['beliefs_final']:<10}{str(r['pre_beliefs_final']):<13}"
              f"{str(r['competing_subjects_final']):<11}")

    Path(args.out).write_text(json.dumps({
        "cycles": args.cycles,
        "threshold": results[0]["threshold"],
        "results": results,
    }, indent=2), encoding="utf-8")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
