"""
Organica Development Probe
==========================

Four measurements that decide what the research programme can and cannot
answer. Each one exists because a number in the repository looked like a
fact and turned out to be an artifact of the measurement.

  1. CAP CENSUS
     Does the Layer-4 hypothesis cap (MAX_HYPOTHESES) ever actually
     truncate anything? If it never binds, the retention POLICY cannot
     influence anything -- ranking a list that is never cut down changes
     nothing but its order, and Layer 5 re-sorts by support count anyway.

  2. BUDGET INSENSITIVITY
     If the census says "never binds", raising the cap must change
     nothing. This asserts that end to end rather than trusting it.

  3. PLATEAU ANALYSIS
     Did the 3,725-cycle live run keep developing, or did it converge
     and sit still? Convergence point, variance and trend over the tail
     of the run. Also re-derives the contradiction totals, which the
     original archive script lost (see the note on `contradiction_total`).

  4. VOCABULARY CONTAMINATION
     How much of the organism's tag vocabulary is its own storage
     schema rather than anything the world said?

Usage:
    python benchmarks/development_probe.py --cycles 600
    python benchmarks/development_probe.py --skip-budget

Writes docs/development_probe.json and prints a summary. Never touches
the live memory.db except to read it.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import sys
import time
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.memory import MemoryService          # noqa: E402
from organica.sleep import SleepService            # noqa: E402
from organica.streams import EVENTS_PER_CYCLE, STUDY_STREAM  # noqa: E402
from organica.paths import LIVE_DB, SCRATCH_DIR, temp_db  # noqa: E402

# Field names that occur in the stored candidate JSON schemas. A tag in
# this set is an artifact of how the organism stores itself, not
# something the world said.
SCHEMA_KEYS = {
    "type", "generation", "evidence", "strength", "confidence", "subject",
    "source", "target", "path", "members", "related", "candidates", "cycle",
    "anchor", "tag", "composites", "created", "sleep", "meta", "ran", "ran_at",
    "id", "ids", "parent", "parents", "expectation", "support", "contradiction",
    "investigation", "experiment", "dream", "theory", "question",
}


# ---------------------------------------------------------------------
# Instrumented service
# ---------------------------------------------------------------------
class ProbeSleep(SleepService):
    """Records the pre-truncation Layer-4 pool and both policy decisions."""

    def __init__(self, memory):
        super().__init__(memory)
        self.rows = []

    def _retain_hypotheses(self, beliefs, info, temporal):
        counts = Counter(h.subject for h in beliefs)

        # What each policy would KEEP (membership, not order).
        alpha = sorted(beliefs, key=lambda h: (h.subject, -h.confidence))
        alpha_set = {h.id for h in alpha[:self.MAX_HYPOTHESES]}

        scores = self._salience(beliefs, info, temporal)
        sal = sorted(beliefs, key=lambda h: (-scores[h.id], h.subject))
        sal_set = {h.id for h in sal[:self.MAX_HYPOTHESES]}

        kept = super()._retain_hypotheses(beliefs, info, temporal)

        self.rows.append({
            "pool_beliefs": len(beliefs),
            "cap": self.MAX_HYPOTHESES,
            "cap_binds": len(beliefs) > self.MAX_HYPOTHESES,
            "subjects": len(counts),
            "subjects_ge2": sum(1 for v in counts.values() if v >= 2),
            # MEMBERSHIP equality is the thing that matters.
            "policies_same_membership": alpha_set == sal_set,
            "policies_same_order": alpha_set == sal_set and
                                   [h.id for h in alpha[:self.MAX_HYPOTHESES]] ==
                                   [h.id for h in sal[:self.MAX_HYPOTHESES]],
            "kept_is_alpha": {h.id for h in kept} == alpha_set,
        })
        return kept

    def _retain_markers(self, markers, info):
        self.last_markers = len(markers)
        return super()._retain_markers(markers, info)


def _run_cold(cycles: int, budget: int) -> dict:
    """A cold colony: fresh DB, full study stream, the daemon's cadence."""
    db = temp_db("development_probe.db")
    memory = MemoryService(db_path=str(db))
    SleepService.MAX_HYPOTHESES = budget
    svc = ProbeSleep(memory)

    for text in STUDY_STREAM:
        memory.store(text, event_type="event", source="seed:bootstrap")

    t0 = time.time()
    beliefs, markers, subjects_ge2, theories, questions = [], [], [], [], []
    for i in range(cycles):
        start = (i * EVENTS_PER_CYCLE) % len(STUDY_STREAM)
        for text in STUDY_STREAM[start:start + EVENTS_PER_CYCLE]:
            memory.store(text, event_type="event", source=f"cycle:{i}")
        rep = svc.run_sleep_cycle()
        beliefs.append(svc.rows[-1]["pool_beliefs"])
        markers.append(getattr(svc, "last_markers", 0))
        subjects_ge2.append(svc.rows[-1]["subjects_ge2"])
        theories.append(len(rep.theories))
        questions.append(len(rep.questions))

    rows = svc.rows
    memory.close()
    db.unlink(missing_ok=True)
    return {
        "cycles": cycles,
        "budget": budget,
        "seconds": round(time.time() - t0, 1),
        "pool_max": max(beliefs) if beliefs else 0,
        "pool_mean": round(sum(beliefs) / len(beliefs), 2) if beliefs else 0,
        "pool_histogram": dict(sorted(Counter(beliefs).items())),
        "marker_mean": round(sum(markers) / len(markers), 2) if markers else 0,
        "cycles_cap_binds": sum(1 for r in rows if r["cap_binds"]),
        "cycles_policies_differ_membership": sum(
            1 for r in rows if not r["policies_same_membership"]),
        "cycles_policies_differ_order": sum(
            1 for r in rows if not r["policies_same_order"]),
        "max_subjects_ge2": max(subjects_ge2) if subjects_ge2 else 0,
        "mean_theories": round(sum(theories) / len(theories), 3) if theories else 0,
        "mean_questions": round(sum(questions) / len(questions), 3) if questions else 0,
        "max_theories": max(theories) if theories else 0,
        "max_questions": max(questions) if questions else 0,
    }


# ---------------------------------------------------------------------
def probe_budget_insensitivity(cycles: int) -> list:
    """Raising the cap must change nothing if the cap never binds."""
    out = []
    for budget in (15, 30, 60):
        work = SCRATCH_DIR / f"budget_probe_{budget}.db"
        SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
        if work.exists():
            work.unlink()
        shutil.copy2(LIVE_DB, work)
        memory = MemoryService(db_path=str(work))
        SleepService.MAX_HYPOTHESES = budget
        svc = ProbeSleep(memory)
        for text in STUDY_STREAM:
            memory.store(text, event_type="event", source="seed:bootstrap")
        for i in range(cycles):
            start = (i * EVENTS_PER_CYCLE) % len(STUDY_STREAM)
            for text in STUDY_STREAM[start:start + EVENTS_PER_CYCLE]:
                memory.store(text, event_type="event", source=f"cycle:{i}")
            svc.run_sleep_cycle()
        last = svc.rows[-1]
        out.append({
            "budget": budget,
            "pool_beliefs": last["pool_beliefs"],
            "subjects": last["subjects"],
            "subjects_ge2": last["subjects_ge2"],
        })
        memory.close()
        work.unlink(missing_ok=True)
    identical = len({json.dumps(r, sort_keys=True) for r in
                     [{k: v for k, v in r.items() if k != "budget"} for r in out]}) == 1
    return {"arms": out, "identical_apart_from_budget": identical}


def _slope(xs, ys):
    n = len(xs)
    if n < 2:
        return 0.0
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    return num / den if den else 0.0


def _sd(v):
    n = len(v)
    if n < 2:
        return 0.0
    m = sum(v) / n
    return (sum((x - m) ** 2 for x in v) / n) ** 0.5


def probe_plateau() -> dict:
    """Convergence and trend of the archived live run."""
    series_path = REPO / "docs" / "prefix_run_series.json"
    if not series_path.exists():
        return {"error": "docs/prefix_run_series.json not present"}
    data = json.loads(series_path.read_text(encoding="utf-8"))
    rows = data["series"]
    n = len(rows)
    xs = [r.get("cycle", i) for i, r in enumerate(rows)]

    out = {"cycles": n, "series": {}}
    for key in ("hypotheses", "theories", "questions", "dreams",
                "investigations", "experiments"):
        if key not in rows[0]:
            continue
        vals = [r.get(key) or 0 for r in rows]
        final = vals[-1]
        last_change = 0
        for i, v in enumerate(vals):
            if v != final:
                last_change = i + 1
        entry = {"final": final, "converged_at_cycle": last_change}
        for wname, a in (("last_50pct", n // 2), ("last_25pct", int(n * 0.75)),
                         ("last_10pct", int(n * 0.90))):
            seg, sx = vals[a:], xs[a:]
            entry[wname] = {
                "mean": round(sum(seg) / len(seg), 3),
                "stdev": round(_sd(seg), 6),
                "slope_per_1000_cycles": round(_slope(sx, seg) * 1000, 6),
                "distinct_values": len(set(seg)),
            }
        out["series"][key] = entry

    # Re-derive contradiction totals from the hypothesis snapshot. The
    # original archive script copied a log key the daemon never wrote, so
    # every archived value was null -- which reads as "zero contradiction".
    ct, sup = [], []
    for r in rows:
        det = r.get("hypotheses_detail") or []
        ct.append(sum(h.get("contradiction") or 0 for h in det))
        sup.append(sum(h.get("support") or 0 for h in det))
    out["contradiction"] = {
        "archived_key_present_but_null": all(
            r.get("contradiction_total") is None for r in rows),
        "rederived_final": ct[-1],
        "rederived_max": max(ct),
        "rederived_at_cycles": {str(c): ct[c] for c in
                                (100, 500, 1000, 2000, 3000, n - 1) if c < n},
        "support_final": sup[-1],
        "last_25pct_distinct": len(set(ct[int(n * 0.75):])),
    }
    return out


def probe_vocabulary() -> dict:
    """How much of the tag vocabulary is the organism's own schema?"""
    if not LIVE_DB.exists():
        return {"error": "live memory.db not present"}
    conn = sqlite3.connect(str(LIVE_DB))
    cur = conn.cursor()
    cur.execute("SELECT tag, count FROM tag_counts ORDER BY count DESC")
    tags = cur.fetchall()
    total = sum(c for _, c in tags)
    schema_c = sum(c for t, c in tags if t in SCHEMA_KEYS)
    conn.close()
    return {
        "distinct_tags": len(tags),
        "total_tag_occurrences": total,
        "schema_artefact_occurrences": schema_c,
        "schema_artefact_pct": round(100 * schema_c / total, 1) if total else 0,
        "top_tags": [{"tag": t, "count": c,
                      "kind": "schema" if t in SCHEMA_KEYS else "world"}
                     for t, c in tags[:20]],
    }


# ---------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=600)
    ap.add_argument("--budget-cycles", type=int, default=30)
    ap.add_argument("--skip-budget", action="store_true")
    args = ap.parse_args()

    results = {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "note": "Organica development probe: cap census, budget "
                       "insensitivity, plateau analysis, vocabulary audit."}

    print("1/4 cap census ...")
    results["cap_census"] = _run_cold(args.cycles, SleepService.MAX_HYPOTHESES)
    print(json.dumps(results["cap_census"], indent=2))

    if not args.skip_budget:
        print("2/4 budget insensitivity ...")
        results["budget_insensitivity"] = probe_budget_insensitivity(
            args.budget_cycles)
        print(json.dumps(results["budget_insensitivity"], indent=2))
    else:
        results["budget_insensitivity"] = {"skipped": True}

    print("3/4 plateau analysis ...")
    results["plateau"] = probe_plateau()
    print(json.dumps(results["plateau"], indent=2))

    print("4/4 vocabulary audit ...")
    results["vocabulary"] = probe_vocabulary()
    print(json.dumps(results["vocabulary"], indent=2))

    out = REPO / "docs" / "development_probe.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
