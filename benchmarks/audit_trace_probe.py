"""Feasibility probe for the development audit trace (docs/AUDIT-TRACE-SPEC.md).

The specification claims that the **selection contest** — the candidates that
died, the candidates that lost, and the ones that survived — can be
reconstructed *from outside* the engine, using only what the engine already
reports and what the substrate already persists.  That claim is the load-bearing
one, and it was read out of the source.  This probe tests it.

It is an instrument probe, not an experiment about the organism: it produces no
claim about what Organica does, only about whether an outside auditor can
reproduce what the engine did.

Four checks:

  A1  evidence replay exactness   — for every reported belief, the auditor's
      recomputed support / contradiction / confidence equal the engine's.
      NOTE: this reconciles **aggregate** counts (the `precedes` table), not
      the individual observations behind them.
  A2  selection reconstruction    — the auditor's reconstructed retained set
      equals the engine's reported retained set, cycle by cycle.
  A7  event-level attribution     — every temporal edge resolves to the
      concrete events that produced it, the attributed total equals the
      aggregate count, and each belief's support resolves to event ids with a
      world/self split.  Requires a passive store-time observer.
  A4  behaviour invariance         — an observer that records the trace leaves
      the engine's outputs byte-identical.

The engine is not modified and is not instrumented.  The observer subclasses
MemoryService, calls the parent unchanged, and only *reads* the lookback
window the engine had just used.  Nothing in `organica/` is touched.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, fields
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.ground_truth_worlds import generate_cause_world  # noqa: E402
from organica.memory import MemoryService  # noqa: E402
from organica.paths import temp_db  # noqa: E402
from organica.sleep import SleepService, SleepReport, _make_id  # noqa: E402

CYCLES = 120
EVENTS_PER_CYCLE = 8
SEED = 20261025
INVARIANCE_CYCLES = 12


# ------------------------------------------------------------------
# The passive observer.
# ------------------------------------------------------------------

class ObservingMemoryService(MemoryService):
    """Records the engine's lookback window at store time.  Read-only.

    The engine's `_record_temporal_edges` looks back at the three most recent
    rows by `ORDER BY time DESC LIMIT 3` — a window that **includes the event
    being stored**, because `store()` inserts the row before recording edges.
    Re-running the same query immediately afterwards observes exactly the
    window the engine used, without changing anything.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # edge (from_tag, to_tag) -> list of (prior_event_id, prior_event_type,
        #                                  to_event_id)
        self.attribution: dict[tuple[str, str], list[tuple[str, str, str]]] = {}
        self.store_order: list[str] = []

    def store(self, content: str, event_type: str = "observe", source: str = "env"):
        event = super().store(content, event_type=event_type, source=source)
        self.store_order.append(event.id)
        # The engine records graph edges only for world events: `store()`
        # guards the call with `if event_type != "sleep"`.  The observer must
        # mirror that guard exactly, or it attributes transitions the engine
        # never made.
        if event_type == "sleep":
            return event
        rows = self._conn.execute(
            "SELECT id, time, event_type, tags, rowid FROM events "
            "ORDER BY time DESC LIMIT 3"
        ).fetchall()
        for prior_id, _t, prior_type, prior_tags, _rowid in rows:
            for tag_from in (prior_tags or "").split(","):
                if not tag_from:
                    continue
                for tag_to in event.tags:
                    if tag_from == tag_to:
                        continue
                    self.attribution.setdefault((tag_from, tag_to), []).append(
                        (prior_id, prior_type, event.id)
                    )
        return event


# ------------------------------------------------------------------
# The auditor.  Every rule below mirrors a line in organica/sleep.py.
# ------------------------------------------------------------------

def _temporal_graph(mem: MemoryService) -> dict[str, dict[str, int]]:
    """Mirror of SleepService._load_temporal (sleep.py:871-874)."""
    graph: dict[str, dict[str, int]] = {}
    for tag_from, tag_to, count in mem.temporal_edges(min_count=1):
        graph.setdefault(tag_from, {})[tag_to] = count
    return graph


def _stable_prior(prior: list[dict], stable_threshold: float) -> list[dict]:
    """Mirror of the stable_prior filter in SleepService.run (sleep.py:463-465)."""
    return [
        c for c in prior
        if c.get("type") not in ("_sleep_meta", "anomaly")
        and (c.get("confidence") or c.get("strength") or 0) >= stable_threshold
    ]


def _subject_entropy(subject: str, temporal: dict[str, dict[str, int]]) -> float:
    """Mirror of SleepService._subject_entropy (sleep.py:1559-1576)."""
    counts = [c for c in temporal.get(subject, {}).values() if c > 0]
    if len(counts) < 2:
        return 0.0
    total = sum(counts)
    h = 0.0
    for c in counts:
        q = c / total
        h -= q * math.log2(q)
    return h / math.log2(len(counts))


def reconstruct(report, prior: list[dict], temporal: dict[str, dict[str, int]],
                svc: SleepService) -> dict:
    """Rebuild the belief contest from the report and the substrate.

    Mirrors SleepService._form_and_test_hypotheses (sleep.py:1406-1528),
    _belief_info (1534-1557), _salience (1578-1602) and _retain_hypotheses
    (1614-1647) under the default "salience" policy.
    """
    stable = _stable_prior(prior, svc.STABLE_THRESHOLD)

    cur_workflows = [asdict(w) for w in report.workflow_concepts]
    cur_processes = [asdict(p) for p in report.processes]
    cur_metas = [asdict(m) for m in report.meta_concepts]

    # --- all_workflows / all_processes / all_metas (sleep.py:473-509) --------
    all_workflows = list(cur_workflows)
    have = {w["id"] for w in all_workflows}
    for c in stable:
        if c.get("type") == "workflow_concept" and c.get("id") not in have:
            all_workflows.append({
                "id": c.get("id"), "components": c.get("components", []),
                "confidence": c.get("confidence", 1.0),
            })
    all_processes = list(cur_processes)
    have = {p["id"] for p in all_processes}
    for c in stable:
        if c.get("type") == "process_candidate" and c.get("id") not in have:
            all_processes.append({
                "id": c.get("id"), "cycle": c.get("cycle", []),
                "strength": c.get("strength", 1.0),
            })
    all_metas = list(cur_metas)
    have = {m["id"] for m in all_metas}
    for c in stable:
        if c.get("type") == "meta_concept" and c.get("id") not in have:
            all_metas.append({
                "id": c.get("id"), "anchor_tag": c.get("anchor_tag", ""),
                "related_candidates": c.get("related_candidates", 0),
                "confidence": c.get("confidence", 0.0),
            })

    # --- the candidate pool (sleep.py:1418-1469) ---------------------------
    pool: dict[str, dict] = {}
    for w in all_workflows:
        comps = list(w["components"])
        for i in range(len(comps)):
            for j in range(len(comps)):
                if i != j:
                    hid = _make_id("hyp", comps[i], comps[j])
                    pool.setdefault(hid, {"id": hid, "subject": comps[i], "expectation": comps[j]})
    for p in all_processes:
        cyc = list(p["cycle"])
        for i in range(len(cyc)):
            sub, exp = cyc[i], cyc[(i + 1) % len(cyc)]
            hid = _make_id("hyp", sub, exp)
            pool.setdefault(hid, {"id": hid, "subject": sub, "expectation": exp})
    markers = []
    for m in all_metas:
        if m["related_candidates"] >= 5:
            hid = _make_id("hyp", m["anchor_tag"], "high_structural_significance")
            markers.append({
                "id": hid, "subject": m["anchor_tag"],
                "expectation": "high_structural_significance",
                "confidence": m["confidence"], "support_count": m["related_candidates"],
                "contradiction_count": 0,
            })

    # --- counts, confidence, death rule (sleep.py:1480-1500) ---------------
    prior_hyps = {h.get("id"): h for h in prior if h.get("type") == "hypothesis"}
    beliefs: dict[str, dict] = {}
    died: list[str] = []
    for hid, cand in pool.items():
        sub, exp = cand["subject"], cand["expectation"]
        targets = temporal.get(sub, {})
        support = targets.get(exp, 0)
        total_flow = sum(targets.values())
        raw_contradiction = max(0, total_flow - support)
        contradiction = raw_contradiction * svc.CONTRADICTION_SCALE
        conf = round(support / (support + contradiction), 4) if (support + contradiction) > 0 else 0.0
        if conf < svc.DEATH_THRESHOLD and (support + contradiction) >= 3:
            died.append(hid)
            continue
        prior_h = prior_hyps.get(hid)
        prior_conf = prior_h.get("confidence") if prior_h else None
        cand.update({
            "support_count": support, "contradiction_count": contradiction,
            "raw_contradiction_count": raw_contradiction,
            "total_flow": total_flow, "confidence": conf,
            "prior_confidence": prior_conf,
            "revision_delta": round(conf - prior_conf, 4) if prior_conf is not None else 0.0,
        })
        beliefs[hid] = cand

    # --- salience (sleep.py:1534-1602) -------------------------------------
    info = {}
    for hid, c in beliefs.items():
        raw = c["raw_contradiction_count"]
        total = c["support_count"] + raw
        prior_h = prior_hyps.get(hid)
        prior_conf = prior_h.get("confidence") if prior_h else None
        info[hid] = {
            "tension": (raw / total) if total > 0 else 0.0,
            "curiosity": _subject_entropy(c["subject"], temporal),
            "novelty": 0.0 if prior_h else 1.0,
            "revision": abs(c["confidence"] - prior_conf) if prior_conf is not None else 0.0,
        }
    w_t, w_c, w_n, w_r = svc.SALIENCE_WEIGHTS
    for hid, c in beliefs.items():
        i = info[hid]
        c["salience"] = (w_t * i["tension"] + w_c * i["curiosity"]
                         + w_n * i["novelty"] + w_r * i["revision"])
        c["components"] = i

    # --- retention (sleep.py:1641-1643) ------------------------------------
    ranked = sorted(beliefs.values(), key=lambda h: (-h["salience"], h["subject"]))
    kept = ranked[:svc.MAX_HYPOTHESES]
    kept_ids = {h["id"] for h in kept}
    lost = [h for h in ranked[svc.MAX_HYPOTHESES:]]

    kept_markers = sorted(markers, key=lambda h: (-h["confidence"], h["subject"]))[:svc.MAX_STRUCTURAL_MARKERS]
    kept_marker_ids = {m["id"] for m in kept_markers}

    return {
        "kept_ids": kept_ids,
        "kept_marker_ids": kept_marker_ids,
        "beliefs": beliefs,
        "died_ids": set(died),
        "lost": [{"id": h["id"], "subject": h["subject"], "expectation": h["expectation"],
                   "salience": round(h["salience"], 6),
                   "components": {k: round(v, 6) for k, v in h["components"].items()}}
                  for h in lost],
        "kept_detail": [{"id": h["id"], "subject": h["subject"], "expectation": h["expectation"],
                         "salience": round(h["salience"], 6),
                         "support_count": h["support_count"],
                         "contradiction_count": h["contradiction_count"],
                         "confidence": h["confidence"],
                         "components": {k: round(v, 6) for k, v in h["components"].items()}}
                        for h in kept],
    }


def _attribution_for(observer: ObservingMemoryService, subject: str,
                      expectation: str) -> list[dict]:
    """The concrete transitions behind one belief's support."""
    out = []
    for prior_id, prior_type, to_id in observer.attribution.get((subject, expectation), []):
        out.append({
            "from_event": prior_id,
            "from_event_type": prior_type,
            "to_event": to_id,
            "source": "self" if prior_type == "sleep" else "world",
        })
    return out


def run(cycles: int = CYCLES, seed: int = SEED, max_hypotheses: int | None = None) -> dict:
    world = generate_cause_world(cycles=cycles, events_per_cycle=EVENTS_PER_CYCLE, seed=seed)
    events = world["events"]

    db = temp_db("audit_trace_probe.db")
    db.unlink(missing_ok=True)
    mem = ObservingMemoryService(db_path=str(db))
    svc = SleepService(mem)
    if hasattr(svc, "_rng"):
        svc._rng.seed(seed)
    if max_hypotheses is not None:
        # STRESS ARM ONLY.  The belief budget is tightened so that the pool
        # exceeds the cap and the "lost on rank" branch is exercised.  This is
        # a stress test of the *auditor*, not a claim about the organism: the
        # auditor reads the same budget, and the engine's files are untouched.
        svc.MAX_HYPOTHESES = max_hypotheses

    cycle_reports = []
    a1_fail = a2_fail = a7_fail = 0
    a1_checked = a2_checked = a7_checked = 0
    self_sourced_total = world_sourced_total = 0
    try:
        for cycle in range(cycles):
            chunk = events[cycle * EVENTS_PER_CYCLE:(cycle + 1) * EVENTS_PER_CYCLE]
            for event in chunk:
                mem.store(event, event_type="event", source=f"cycle:{cycle}")

            # Snapshots taken at exactly the moment the engine reads them.
            temporal = _temporal_graph(mem)
            prior = svc._load_prior_candidates()

            report = svc.run_sleep_cycle()

            rec = reconstruct(report, prior, temporal, svc)

            reported = {h.id: h for h in report.hypotheses}
            reported_beliefs = {i: h for i, h in reported.items()
                                if h.expectation != "high_structural_significance"}
            reported_markers = {i: h for i, h in reported.items()
                                if h.expectation == "high_structural_significance"}

            # --- A1: evidence replay exactness (aggregate counts) ----------
            a1_errors = []
            for hid, h in reported_beliefs.items():
                mine = rec["beliefs"].get(hid)
                if mine is None:
                    a1_errors.append({"id": hid, "error": "not in reconstructed pool"})
                    continue
                for field in ("support_count", "contradiction_count", "confidence"):
                    if abs(float(getattr(h, field)) - float(mine[field])) > 1e-9:
                        a1_errors.append({"id": hid, "field": field,
                                          "engine": getattr(h, field), "auditor": mine[field]})
                a1_checked += 1
            if a1_errors:
                a1_fail += 1

            # --- A2: selection reconstruction ------------------------------
            a2_ok = (set(reported_beliefs) == rec["kept_ids"]
                     and set(reported_markers) == rec["kept_marker_ids"])
            a2_checked += 1
            if not a2_ok:
                a2_fail += 1

            # --- A7: event-level attribution -------------------------------
            a7_errors = []
            for hid, h in reported_beliefs.items():
                transitions = _attribution_for(mem, h.subject, h.expectation)
                if len(transitions) != h.support_count:
                    a7_errors.append({"id": hid, "error": "attribution count mismatch",
                                       "attributed": len(transitions),
                                       "support_count": h.support_count})
                    continue
                world_n = sum(1 for t in transitions if t["source"] == "world")
                self_n = len(transitions) - world_n
                world_sourced_total += world_n
                self_sourced_total += self_n
                a7_checked += 1
            if a7_errors:
                a7_fail += 1

            cycle_reports.append({
                "cycle": cycle + 1,
                "reported_beliefs": len(reported_beliefs),
                "reported_markers": len(reported_markers),
                "pool": len(rec["beliefs"]) + len(rec["died_ids"]),
                "died": len(rec["died_ids"]),
                "lost": len(rec["lost"]),
                "a1_errors": a1_errors,
                "a2_match": a2_ok,
                "a7_errors": a7_errors,
                "kept_detail": rec["kept_detail"],
                "lost_detail": rec["lost"][:5],
            })

        # --- A7 aggregate: every edge's attributed total == its count -----
        # The cross-check between two independent paths: the per-event
        # attribution, and the `precedes` aggregate table the engine builds.
        edge_mismatches = []
        edges_checked = 0
        aggregate_edges = set()
        for tag_from, tag_to, count in mem.temporal_edges(min_count=1):
            edges_checked += 1
            aggregate_edges.add((tag_from, tag_to))
            attributed = len(mem.attribution.get((tag_from, tag_to), []))
            if attributed != count:
                edge_mismatches.append({
                    "from": tag_from, "to": tag_to,
                    "aggregate_count": count, "attributed": attributed,
                })
        attributed_only = [f"{f}->{t}" for (f, t) in mem.attribution
                           if (f, t) not in aggregate_edges]
    finally:
        mem.close()
        db.unlink(missing_ok=True)

    cycles_with_beliefs = [c for c in cycle_reports if c["reported_beliefs"]]
    total_attributed = world_sourced_total + self_sourced_total
    return {
        "purpose": "Feasibility probe for docs/AUDIT-TRACE-SPEC.md — can the "
                   "selection contest be reconstructed from outside the engine, "
                   "and can evidence be resolved to event ids?",
        "instrument_note": "Instrument probe, not an experiment about the organism. "
                           "It makes no claim about what Organica does; it checks "
                           "whether an outside auditor can reproduce what the engine did. "
                           "No engine file was modified or instrumented. The observer "
                           "subclasses MemoryService, calls the parent unchanged, and "
                           "only reads the lookback window the engine had just used.",
        "protocol": {
            "world": "organica/ground_truth_worlds.generate_cause_world",
            "cycles": cycles, "events_per_cycle": EVENTS_PER_CYCLE, "seed": seed,
            "retention_policy": SleepService.HYPOTHESIS_RETENTION,
            "max_hypotheses": svc.MAX_HYPOTHESES,
            "default_max_hypotheses": SleepService.MAX_HYPOTHESES,
            "stress_arm": max_hypotheses is not None,
            "salience_weights": list(SleepService.SALIENCE_WEIGHTS),
            "death_threshold": SleepService.DEATH_THRESHOLD,
            "contradiction_scale": SleepService.CONTRADICTION_SCALE,
            "report_candidate_lists": len([f.name for f in fields(SleepReport)
                                           if f.name not in ("cycle", "ran_at",
                                                             "prior_candidates_loaded",
                                                             "candidates_strengthened",
                                                             "candidates_decayed",
                                                             "candidates_pruned",
                                                             "composites_created")]),
        },
        "A1_evidence_replay_aggregate": {
            "beliefs_checked": a1_checked, "cycles_failing": a1_fail,
            "pass": a1_fail == 0,
            "scope": "aggregate counts only — the `precedes` table, not the "
                     "individual observations behind them",
        },
        "A2_selection_reconstruction": {
            "cycles_checked": a2_checked, "cycles_failing": a2_fail,
            "pass": a2_fail == 0,
        },
        "A7_event_level_attribution": {
            "beliefs_checked": a7_checked, "cycles_failing": a7_fail,
            "pass": a7_fail == 0 and not edge_mismatches and not attributed_only,
            "attributed_transitions_total": total_attributed,
            "world_sourced": world_sourced_total,
            "self_sourced": self_sourced_total,
            "self_sourced_share": (round(self_sourced_total / total_attributed, 6)
                                    if total_attributed else 0.0),
            "aggregate_edges_checked": edges_checked,
            "edge_mismatches": edge_mismatches[:10],
            "attributed_but_absent_from_aggregate": attributed_only[:10],
            "note": "Every temporal edge must resolve to the concrete events "
                    "that produced it, and the attributed total must equal the "
                    "aggregate count. The world/self split is the D2 quantity: "
                    "a supporting transition whose prior event is the "
                    "organism's own sleep payload is self-sourced.",
        },
        "summary": {
            "cycles_run": len(cycle_reports),
            "cycles_with_beliefs": len(cycles_with_beliefs),
            "max_pool": max((c["pool"] for c in cycle_reports), default=0),
            "max_died": max((c["died"] for c in cycle_reports), default=0),
            "max_lost": max((c["lost"] for c in cycle_reports), default=0),
            "total_died": sum(c["died"] for c in cycle_reports),
            "total_lost": sum(c["lost"] for c in cycle_reports),
        },
        "cycles": cycle_reports,
    }


def _reports_signature(reports: list[dict]) -> str:
    """A stable signature of the engine's outputs.

    `ran_at` is a wall-clock timestamp and differs between any two runs; it
    is not part of the engine's behavioural output, so it is excluded.  Every
    other field — every candidate, every counter — must match exactly.
    """
    stripped = []
    for r in reports:
        r = dict(r)
        r.pop("ran_at", None)
        stripped.append(r)
    return json.dumps(stripped, sort_keys=True)


def run_invariance(cycles: int = INVARIANCE_CYCLES, seed: int = SEED) -> dict:
    """A4 — does the observer change the engine's outputs?  It must not."""
    def once(observing: bool) -> list[dict]:
        world = generate_cause_world(cycles=cycles, events_per_cycle=EVENTS_PER_CYCLE, seed=seed)
        db = temp_db(f"audit_trace_invariance_{'obs' if observing else 'plain'}.db")
        db.unlink(missing_ok=True)
        mem = (ObservingMemoryService if observing else MemoryService)(db_path=str(db))
        svc = SleepService(mem)
        if hasattr(svc, "_rng"):
            svc._rng.seed(seed)
        out = []
        try:
            for cycle in range(cycles):
                for event in world["events"][cycle * EVENTS_PER_CYCLE:(cycle + 1) * EVENTS_PER_CYCLE]:
                    mem.store(event, event_type="event", source=f"cycle:{cycle}")
                report = svc.run_sleep_cycle()
                out.append(asdict(report))
        finally:
            mem.close()
            db.unlink(missing_ok=True)
        return out

    plain = _reports_signature(once(False))
    observed = _reports_signature(once(True))
    return {
        "A4_behaviour_invariance": {
            "cycles": cycles, "seed": seed,
            "observer_on_equals_observer_off": plain == observed,
            "pass": plain == observed,
            "note": "The observer subclasses MemoryService, calls the parent "
                    "unchanged, and only reads. It must not change a single "
                    "reported field.",
        }
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycles", type=int, default=CYCLES)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--max-hypotheses", type=int, default=None,
                        help="stress arm: tighten the belief budget so the "
                             "'lost on rank' branch is exercised")
    parser.add_argument("--out", default=str(REPO / "docs" / "audit_trace_probe.json"))
    args = parser.parse_args()
    result = run(args.cycles, args.seed, args.max_hypotheses)
    result.update(run_invariance())
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "cycles"}, indent=2))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
