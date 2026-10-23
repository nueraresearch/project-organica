"""
Diagnostic: why does the branch stimulus collapse at some repeat counts?

The first sweep found `neutral_n5_k2_r4` passing all four gates while
`r=6` and `r=10` collapsed to a near-empty belief pool. An unexplained
passing point is not a result, so this traces the funnel per cycle:

    predictions retained (top 20 by count)  ->  processes  ->  workflows
    ->  beliefs  ->  competing subjects  ->  theories

and reports, for each design, the per-cycle series plus the counts of the
Layer-1 prediction set, so the break point can be located rather than
guessed at.

Usage:
    python benchmarks/branch_diag.py --cycles 120
Writes docs/branch_diag.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.branch_streams import branch_stream   # noqa: E402
from organica.memory import MemoryService           # noqa: E402
from organica.sleep import SleepService             # noqa: E402
from organica.streams import EVENTS_PER_CYCLE, STUDY_STREAM  # noqa: E402
from organica.paths import temp_db                  # noqa: E402


class Traced(SleepService):
    """Records the funnel width at every layer, per cycle."""

    def __init__(self, memory):
        super().__init__(memory)
        self.rows = []
        self.pred_sources = set()

    def _build_predictions(self, temporal, freqs):
        preds = super()._build_predictions(temporal, freqs)
        self.pred_sources = {(p.source, p.target) for p in preds}
        return preds

    def _compose_processes(self, stable_prior):
        procs = super()._compose_processes(stable_prior)
        self._procs = procs
        return procs

    def _compose_workflows(self, meta_concepts, processes, stable_prior):
        wfs = super()._compose_workflows(meta_concepts, processes, stable_prior)
        self._wfs = wfs
        return wfs

    def _retain_hypotheses(self, beliefs, info, temporal):
        counts = Counter(h.subject for h in beliefs)
        self.rows.append({
            "beliefs": len(beliefs),
            "subjects": len(counts),
            "subjects_ge2": sum(1 for c in counts.values() if c >= 2),
            "predictions": len(self.pred_sources),
            "reciprocal_pairs": sum(
                1 for (a, b) in self.pred_sources if (b, a) in self.pred_sources),
            "processes": len(getattr(self, "_procs", [])),
            "workflows": len(getattr(self, "_wfs", [])),
        })
        return super()._retain_hypotheses(beliefs, info, temporal)


def trace(name, events, cycles):
    db = temp_db(f"bd_{name}.db")
    if db.exists():
        db.unlink()
    mem = MemoryService(db_path=str(db))
    svc = Traced(mem)
    for text in events:
        mem.store(text, event_type="event", source="seed:bootstrap")

    t0 = time.time()
    theories = []
    for i in range(cycles):
        start = (i * EVENTS_PER_CYCLE) % len(events)
        for text in events[start:start + EVENTS_PER_CYCLE]:
            mem.store(text, event_type="event", source=f"cycle:{i}")
        rep = svc.run_sleep_cycle()
        theories.append(len(rep.theories))
        svc.rows[-1]["theories"] = len(rep.theories)
    elapsed = time.time() - t0
    mem.close()
    db.unlink(missing_ok=True)
    return {"design": name, "events": len(events), "seconds": round(elapsed, 1),
            "rows": svc.rows, "theories": theories}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=120)
    ap.add_argument("--out", default=str(REPO / "docs" / "branch_diag.json"))
    args = ap.parse_args()

    designs = [("study_stream", list(STUDY_STREAM))]
    for r in (3, 4, 5, 6, 8):
        designs.append((f"n5_k2_r{r}", branch_stream(5, 2, r)))

    out_rows = []
    for name, events in designs:
        res = trace(name, events, args.cycles)
        rows = res["rows"]
        tail = rows[int(len(rows) * 0.5):]
        keys = ("predictions", "reciprocal_pairs", "processes", "workflows",
                "beliefs", "subjects_ge2", "theories")
        agg = {k: [r[k] for r in tail] for k in keys}
        res["tail_summary"] = {
            k: {"min": min(v), "max": max(v),
                "mean": round(sum(v) / len(v), 2),
                "distinct": sorted(set(v))[:10]}
            for k, v in agg.items()
        }
        out_rows.append(res)
        s = res["tail_summary"]
        print(f"{name:<14} ev={res['events']:<5} "
              + " ".join(f"{k}={s[k]['min']}-{s[k]['max']}" for k in keys))
        sys.stdout.flush()

    p = Path(args.out)
    p.write_text(json.dumps({
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cycles": args.cycles,
        "rows": out_rows,
    }, indent=2), encoding="utf-8")
    print(f"\nwrote {p}")


if __name__ == "__main__":
    main()
