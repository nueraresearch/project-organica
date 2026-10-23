"""
Lattice-stimulus sweep: which design clears all four campaign gates, and
does it clear them *sustained*?

The gates (docs/FORCE-MATRIX-PREREGISTRATION.md §1), evaluated on the
PRE-retention belief pool so that they measure the *stimulus* rather than
the retention policy:

  G-CS   >= 3 subjects hold >= 2 beliefs, reaching 5-7
  G-P1   belief pool / MAX_HYPOTHESES > 1.0   (retention pressure)
  G-SUP  belief pool > MAX_HYPOTHESES (15)
  G-EXP  the number of distinct belief subjects stays below MAX_THEORIES (8)

WHY "PRE-RETENTION"
-------------------
Layer 5 forms theories from the *retained* belief set, so the retained
count is what determines the theory population -- but it is also a
function of `HYPOTHESIS_RETENTION`, which is one of the six arms under
test. A gate that depends on the arm under test is not a gate. The
supply-side quantities are policy-independent, so the gate is stated on
the pre-retention pool and the retained count is reported alongside it as
a campaign outcome.

The sweep also measures the thing the first generator got wrong: the
**prediction window**. `edges_eligible` is the number of distinct
temporal edges that clear `PREDICTION_MIN_COUNT`; `window_edges` is how
many of them survive the top-`MAX_PREDICTIONS` selection. When
`window_edges` is close to `MAX_PREDICTIONS`, the window is a tie-break
lottery and the belief supply oscillates -- that is the mechanism for
the intermittency measured in the first sweep.

Usage:
    python benchmarks/branch_sweep2.py --cycles 300
Writes docs/branch_sweep2.json
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
    NEUTRAL_HUB, NEUTRAL_PETALS, lattice_designs, lattice_stream, describe)
from organica.memory import MemoryService            # noqa: E402
from organica.sleep import SleepService              # noqa: E402
from organica.streams import EVENTS_PER_CYCLE, STUDY_STREAM  # noqa: E402
from organica.paths import temp_db                   # noqa: E402

MAX_THEORIES = SleepService.MAX_THEORIES
MAX_HYPOTHESES = SleepService.MAX_HYPOTHESES


class Instrumented(SleepService):
    """Records the quantities the gates and the mechanism check need."""

    def __init__(self, memory):
        super().__init__(memory)
        self.rows = []
        self._pending = {}

    # -- how many edges could enter the prediction window, and how many did
    def _load_temporal(self):
        temporal = super()._load_temporal()
        self._edges_all = sum(
            len(tgts) for tgts in temporal.values())
        self._edges_eligible = sum(
            1 for tgts in temporal.values() for c in tgts.values()
            if c >= self.PREDICTION_MIN_COUNT)
        return temporal

    def _compose_processes(self, stable_prior):
        edges = set()
        for c in stable_prior:
            if c.get("type") == "prediction_candidate":
                s, t = c.get("source", ""), c.get("target", "")
                if s and t:
                    edges.add((s, t))
        self._pending = {
            "window_edges": len(edges),
            "edges_eligible": getattr(self, "_edges_eligible", 0),
            "edges_all": getattr(self, "_edges_all", 0),
        }
        return super()._compose_processes(stable_prior)

    # -- the belief pool, before and after retention
    def _retain_hypotheses(self, beliefs, info, temporal):
        pre = Counter(h.subject for h in beliefs)
        kept = super()._retain_hypotheses(beliefs, info, temporal)
        post = Counter(h.subject for h in kept)
        row = dict(self._pending)
        row.update({
            "pre_beliefs": len(beliefs),
            "pre_subjects": len(pre),
            "pre_subjects_ge2": sum(1 for c in pre.values() if c >= 2),
            "post_beliefs": len(kept),
            "post_subjects": len(post),
            "post_subjects_ge2": sum(1 for c in post.values() if c >= 2),
        })
        self.rows.append(row)
        return kept


def make_service(max_predictions: int, policy: str):
    """A service subclass with a specific prediction window and policy."""

    class S(Instrumented):
        MAX_PREDICTIONS = max_predictions
        HYPOTHESIS_RETENTION = policy

    S.__name__ = f"Instrumented_p{max_predictions}_{policy}"
    return S


def evaluate(name: str, events: list[str], cycles: int,
             max_predictions: int, policy: str) -> dict:
    db = temp_db(f"lattice_{name}.db")
    if db.exists():
        db.unlink()
    mem = MemoryService(db_path=str(db))
    svc = make_service(max_predictions, policy)(mem)

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
    tail = rows[int(len(rows) * 0.5):] or rows

    def stats(key, src=tail):
        vals = [r[key] for r in src]
        if not vals:
            return 0.0, 0, 0
        vals_sorted = sorted(vals)
        p95 = vals_sorted[max(0, int(0.95 * len(vals_sorted)) - 1)]
        return round(statistics.fmean(vals), 3), p95, max(vals)

    pre_mean, pre_p95, pre_max = stats("pre_beliefs")
    pre2_mean, pre2_p95, pre2_max = stats("pre_subjects_ge2")
    post2_mean, post2_p95, post2_max = stats("post_subjects_ge2")
    win_mean, win_p95, win_max = stats("window_edges")
    elig_mean, _, elig_max = stats("edges_eligible")

    # Sustainment: the fraction of the tail in which ALL FOUR gates hold
    # at the same time. This is the number that decides whether the
    # campaign can run: a gate that passes on peaks is not a gate.
    gate_hits = 0
    for r in tail:
        if (r["pre_beliefs"] > MAX_HYPOTHESES
                and r["pre_subjects_ge2"] >= 3
                and r["pre_subjects"] < MAX_THEORIES):
            gate_hits += 1
    sustained = gate_hits / len(tail) if tail else 0.0

    # Intermittency: how often the supply is completely absent.
    zero = sum(1 for r in tail if r["pre_beliefs"] == 0)
    intermittency = zero / len(tail) if tail else 0.0

    d = describe(events)
    return {
        "design": name,
        "events": len(events),
        "distinct_tags": d["distinct_tags"],
        "max_predictions": max_predictions,
        "policy": policy,
        "seconds": round(elapsed, 1),
        "pre_beliefs_mean": pre_mean,
        "pre_beliefs_p95": pre_p95,
        "pre_beliefs_max": pre_max,
        "pre_subjects_ge2_mean": pre2_mean,
        "pre_subjects_ge2_p95": pre2_p95,
        "pre_subjects_ge2_max": pre2_max,
        "post_subjects_ge2_mean": post2_mean,
        "post_subjects_ge2_max": post2_max,
        "theories_mean": round(statistics.fmean(theory_counts), 3) if theory_counts else 0,
        "theories_max": max(theory_counts) if theory_counts else 0,
        "pressure_mean": round(pre_mean / MAX_HYPOTHESES, 3),
        "pressure_p95": round(pre_p95 / MAX_HYPOTHESES, 3),
        "window_edges_mean": win_mean,
        "window_edges_max": win_max,
        "edges_eligible_mean": elig_mean,
        "edges_eligible_max": elig_max,
        "window_is_full": bool(win_max >= max_predictions),
        "sustained_frac": round(sustained, 3),
        "intermittency": round(intermittency, 3),
        "gates": {
            "G_CS": pre2_max >= 3 and 5 <= pre2_max <= 7,
            "G_CS_min3": pre2_max >= 3,
            "G_P1": pre_p95 > MAX_HYPOTHESES,
            "G_SUP": pre_p95 > MAX_HYPOTHESES,
            "G_EXP": (max(r["pre_subjects"] for r in tail) if tail else 0) < MAX_THEORIES,
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=300)
    ap.add_argument("--policy", default="salience")
    ap.add_argument("--out", default=str(REPO / "docs" / "branch_sweep2.json"))
    args = ap.parse_args()

    designs = []
    # The current study stream, as the reference point.
    designs.append(("study_stream", list(STUDY_STREAM), None))
    for name, spec in lattice_designs(NEUTRAL_HUB, NEUTRAL_PETALS).items():
        designs.append((name, lattice_stream(spec["triangles"]), spec["predict"]))

    rows = []
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    def flush():
        out_path.write_text(json.dumps({
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "cycles": args.cycles,
            "policy": args.policy,
            "gate_definition": "evaluated on the PRE-retention belief pool",
            "rows": list(rows),
        }, indent=2), encoding="utf-8")

    caps = [20, 32, 48]
    for name, events, predict in designs:
        caps_for_design = [SleepService.MAX_PREDICTIONS] if predict is None else caps
        for cap in caps_for_design:
            label = name if predict is None else f"{name}_p{cap}"
            r = evaluate(label, events, args.cycles, cap, args.policy)
            r["predicted"] = predict
            rows.append(r)
            flush()
            g = r["gates"]
            print(f"{label:<28} bel={r['pre_beliefs_mean']:>6.2f}/{r['pre_beliefs_p95']:<3} "
                  f"comp={r['pre_subjects_ge2_mean']:>5.2f}/{r['pre_subjects_ge2_max']:<3} "
                  f"post={r['post_subjects_ge2_max']:<2} "
                  f"T={r['theories_mean']:>5.2f}/{r['theories_max']:<2} "
                  f"win={r['window_edges_mean']:>6.1f}/{r['window_edges_max']:<3} "
                  f"elig={r['edges_eligible_max']:<3} "
                  f"sus={r['sustained_frac']:>5.2f} int={r['intermittency']:>5.2f} "
                  f"CS:{'Y' if g['G_CS'] else 'n'} P1:{'Y' if g['G_P1'] else 'n'} "
                  f"SUP:{'Y' if g['G_SUP'] else 'n'} EXP:{'Y' if g['G_EXP'] else 'n'}")
            sys.stdout.flush()

    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
