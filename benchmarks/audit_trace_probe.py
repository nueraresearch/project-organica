"""Feasibility probe for the development audit trace (docs/AUDIT-TRACE-SPEC.md).

The specification claims that the **selection contest** — the candidates that
died, the candidates that lost, and the ones that survived — can be
reconstructed *from outside* the engine, using only what the engine already
reports and what the substrate already persists.  That claim is the load-bearing
one, and it was read out of the source.  This probe tests it.

It is an instrument probe, not an experiment about the organism: it produces no
claim about what Organica does, only about whether an outside auditor can
reproduce what the engine did.

Two checks, the two load-bearing acceptance criteria from the spec:

  A1  evidence replay exactness   — for every reported belief, the auditor's
      recomputed support / contradiction / confidence equal the engine's.
  A2  selection reconstruction    — the auditor's reconstructed retained set
      equals the engine's reported retained set, cycle by cycle.

The engine is not modified and is not instrumented.  The auditor reads the
report and the substrate, and re-derives the decision from the documented
rules.  Nothing in `organica/` is touched.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.ground_truth_worlds import generate_cause_world  # noqa: E402
from organica.memory import MemoryService  # noqa: E402
from organica.paths import temp_db  # noqa: E402
from organica.sleep import SleepService, _make_id  # noqa: E402

CYCLES = 120
EVENTS_PER_CYCLE = 8
SEED = 20261025


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

    # Normalise the report's candidate objects to plain dicts so that the
    # cycle's own candidates and the persisted priors are the same shape.
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


def run(cycles: int = CYCLES, seed: int = SEED, max_hypotheses: int | None = None) -> dict:
    world = generate_cause_world(cycles=cycles, events_per_cycle=EVENTS_PER_CYCLE, seed=seed)
    events = world["events"]

    db = temp_db("audit_trace_probe.db")
    db.unlink(missing_ok=True)
    mem = MemoryService(db_path=str(db))
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
    a1_fail = a2_fail = 0
    a1_checked = a2_checked = 0
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

            # --- A1: evidence replay exactness -----------------------------
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

            cycle_reports.append({
                "cycle": cycle + 1,
                "reported_beliefs": len(reported_beliefs),
                "reported_markers": len(reported_markers),
                "pool": len(rec["beliefs"]) + len(rec["died_ids"]),
                "died": len(rec["died_ids"]),
                "lost": len(rec["lost"]),
                "a1_errors": a1_errors,
                "a2_match": a2_ok,
                "kept_detail": rec["kept_detail"],
                "lost_detail": rec["lost"][:5],
            })
    finally:
        mem.close()
        db.unlink(missing_ok=True)

    cycles_with_beliefs = [c for c in cycle_reports if c["reported_beliefs"]]
    return {
        "purpose": "Feasibility probe for docs/AUDIT-TRACE-SPEC.md — can the "
                   "selection contest be reconstructed from outside the engine?",
        "instrument_note": "Instrument probe, not an experiment about the organism. "
                           "It makes no claim about what Organica does; it checks "
                           "whether an outside auditor can reproduce what the engine did. "
                           "No engine file was modified or instrumented.",
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
        },
        "A1_evidence_replay": {
            "beliefs_checked": a1_checked, "cycles_failing": a1_fail,
            "pass": a1_fail == 0,
        },
        "A2_selection_reconstruction": {
            "cycles_checked": a2_checked, "cycles_failing": a2_fail,
            "pass": a2_fail == 0,
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
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "cycles"}, indent=2))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
