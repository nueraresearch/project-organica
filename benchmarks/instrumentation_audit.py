"""
Organica Instrumentation Audit (Phase V1.5)
===========================================

A measurement study, not an ablation study.

The V1 ablation campaign produced byte-identical results for five very
different upstream threshold settings. That has two possible causes and
they demand opposite responses:

    (a) the parameter genuinely does not matter, or
    (b) the OBSERVATION CHANNEL is saturated -- the parameter changes the
        candidate pool, but the layer's output cap discards the change
        before it can be seen.

(b) is far more likely, and it would have made a whole matrix of
experiments measure bottlenecks instead of cognition. So before running
the Tier-1 matrix, this audit measures the machinery itself.

Three outputs
-------------
AUDIT 1 -- PARAMETER INFLUENCE MAP
    For every tunable parameter: was the code path executed, and was the
    value DECISIVE (changed the final outputs) or merely POOL-ONLY
    (changed the candidate pool, but the cap hid it) or INERT (changed
    nothing at any level)?

AUDIT 2 -- PRE-TRUNCATION CANDIDATE DISTRIBUTIONS
    For every capped layer: the candidate pool size BEFORE truncation, as
    mean / median / p95 / max over the run, plus

        retention_pressure = pool_size / cap

    < 1.0  no pressure -- the retention policy cannot matter
    1-2    weak pressure
    2-5    useful pressure
    > 5    strong pressure

    This is gate G-P1. A retention experiment (alphabetical vs salience)
    is only informative if pressure > 1.0 for the object being retained.

AUDIT 3 -- EFFECTIVE WORLD SIZE
    Unique tags, tag entropy and frequency concentration of the world the
    organism can actually perceive, per cycle. If the effective world is
    only a handful of tags deep, the organism cannot differentiate no
    matter how it is configured -- and the next experiment is world
    expansion, not retention.

Nothing here modifies the engine. The audit subclasses SleepService to
observe, exactly as the V1 ablation campaign did.

Usage:
    python benchmarks/instrumentation_audit.py --cycles 400
    python benchmarks/instrumentation_audit.py --part pools world
    python benchmarks/instrumentation_audit.py --param PREDICTION_MIN_COUNT=3

Writes docs/instrumentation_audit.json. Never writes to the live
memory.db.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.memory import MemoryService          # noqa: E402
from organica.sleep import SleepService            # noqa: E402
from organica.streams import (                     # noqa: E402
    DOMAINS, EVENTS_PER_CYCLE, STUDY_STREAM)
from organica.paths import temp_db                 # noqa: E402

INF = 10 ** 9

# Every layer whose output is capped, and the constant that caps it.
CAPPED_LAYERS = {
    "loops": "MAX_LOOPS",
    "predictions": "MAX_PREDICTIONS",
    "anomalies": "MAX_ANOMALIES",
    "meta_concepts": "MAX_META_CONCEPTS",
    "processes": "MAX_PROCESSES",
    "workflows": "MAX_WORKFLOWS",
    "theories": "MAX_THEORIES",
    "questions": "MAX_QUESTIONS",
    "dreams": "MAX_DREAMS",
    "investigations": "MAX_INVESTIGATIONS",
    "experiments": "MAX_EXPERIMENTS",
    # The belief pool is capped by the retention policy, not by a builder,
    # but it is a retained object type and its pressure is the whole
    # point of gate G-P1.
    "hypotheses": "MAX_HYPOTHESES",
}

# The parameters Audit 1 varies, with the alternative value to try.
PARAMETER_VARIANTS = {
    "PREDICTION_MIN_COUNT": 3,
    "META_CONCEPT_MIN_REFS": 2,
    "CONCEPT_MIN_DEGREE": 2,
    "CONCEPT_MIN_REACH": 2,
    "PHRASE_MIN_CLUSTERING": 0.5,
    "LOOP_MIN_STRENGTH": 2,
    "STABLE_THRESHOLD": 0.2,
    "DEATH_THRESHOLD": 0.25,
    "MAX_HYPOTHESES": 40,
    "MAX_WORKFLOWS": 25,
    "MAX_PROCESSES": 25,
    "MAX_META_CONCEPTS": 30,
    "MAX_PREDICTIONS": 40,
    "WORKFLOW_MIN_MATCHED_METAS": 1,
}

# The report attribute names differ from the layer names in a few places
# (the report says "workflow_concepts", the layer says "workflows"). Getting
# this wrong makes a working layer look dead, so the mapping is explicit.
POPULATION_FIELDS = (
    ("concepts", "concepts"),
    ("phrases", "phrases"),
    ("loops", "loops"),
    ("predictions", "predictions"),
    ("anomalies", "anomalies"),
    ("meta_concepts", "meta_concepts"),
    ("processes", "processes"),
    ("workflows", "workflow_concepts"),
    ("hypotheses", "hypotheses"),
    ("theories", "theories"),
    ("questions", "questions"),
    ("dreams", "dreams"),
    ("investigations", "investigations"),
    ("experiments", "experiments"),
)


# ---------------------------------------------------------------------
class AuditedSleep(SleepService):
    """Observes every capped layer's PRE-truncation candidate pool.

    The trick: temporarily lift the cap, let the layer build its full
    candidate list, then restore the cap and return exactly what the
    engine would have returned. The pre-cap size is therefore measured
    without changing the dynamics at all.
    """

    def __init__(self, memory):
        super().__init__(memory)
        self.pre_cap = {}
        self.rows = []
        self._world = {}
        self.composition_anchors = set()
        self.process_tags = set()
        self.workflow_tags = set()
        self.belief_pairs = set()

    def _capture(self, name, cap_attr, fn, *args, **kwargs):
        saved = getattr(self, cap_attr)
        setattr(self, cap_attr, INF)
        try:
            full = fn(*args, **kwargs)
        finally:
            setattr(self, cap_attr, saved)
        self.pre_cap[name] = len(full)
        return full[:saved]

    # -- Layer 1 ------------------------------------------------------
    def _build_loops(self, temporal):
        return self._capture("loops", "MAX_LOOPS",
                             super()._build_loops, temporal)

    def _build_predictions(self, temporal, freqs):
        return self._capture("predictions", "MAX_PREDICTIONS",
                             super()._build_predictions, temporal, freqs)

    def _build_anomalies(self, temporal, freqs):
        return self._capture("anomalies", "MAX_ANOMALIES",
                             super()._build_anomalies, temporal, freqs)

    # -- Layer 2 ------------------------------------------------------
    def _compose_meta_concepts(self, stable_prior):
        metas = self._capture("meta_concepts", "MAX_META_CONCEPTS",
                              super()._compose_meta_concepts, stable_prior)
        # The EFFECTIVE COMPOSITION WORLD: the tags the organism can
        # actually build structure out of. It is a subset of the temporal
        # world, because meta-concepts are composed only from the
        # candidates that survived the upstream caps.
        self.composition_anchors = {m.anchor_tag for m in metas}
        return metas

    def _compose_processes(self, stable_prior):
        procs = self._capture("processes", "MAX_PROCESSES",
                              super()._compose_processes, stable_prior)
        self.process_tags = {t for p in procs for t in (p.cycle or [])}
        return procs

    # -- Layer 3 ------------------------------------------------------
    def _compose_workflows(self, meta_concepts, processes, stable_prior):
        wfs = self._capture("workflows", "MAX_WORKFLOWS",
                            super()._compose_workflows, meta_concepts,
                            processes, stable_prior)
        self.workflow_tags = {t for w in wfs for t in (w.components or [])}
        return wfs

    # -- Layer 4 ------------------------------------------------------
    def _retain_hypotheses(self, beliefs, info, temporal):
        # The belief pool arrives here UNtruncated; the cap is applied
        # inside the policy. So this is the pre-cap belief pool.
        self.pre_cap["hypotheses"] = len(beliefs)
        self.belief_pairs = {(h.subject, h.expectation) for h in beliefs}
        return super()._retain_hypotheses(beliefs, info, temporal)

    def _retain_markers(self, markers, info):
        self.pre_cap["hypothesis_markers"] = len(markers)
        return super()._retain_markers(markers, info)

    # -- Layer 5 ------------------------------------------------------
    def _form_theories_and_questions(self, hypotheses, prior):
        saved_t, saved_q = self.MAX_THEORIES, self.MAX_QUESTIONS
        self.MAX_THEORIES = self.MAX_QUESTIONS = INF
        try:
            theories, questions = super()._form_theories_and_questions(
                hypotheses, prior)
        finally:
            self.MAX_THEORIES, self.MAX_QUESTIONS = saved_t, saved_q
        self.pre_cap["theories"] = len(theories)
        self.pre_cap["questions"] = len(questions)
        return theories[:saved_t], questions[:saved_q]

    # -- Layer 6 ------------------------------------------------------
    def _generate_categorized_dreams(self, *a, **kw):
        return self._capture("dreams", "MAX_DREAMS",
                             super()._generate_categorized_dreams, *a, **kw)

    # -- Layer 7/8 ----------------------------------------------------
    def _rank_investigations(self, *a, **kw):
        return self._capture("investigations", "MAX_INVESTIGATIONS",
                             super()._rank_investigations, *a, **kw)

    def _select_experiments(self, *a, **kw):
        return self._capture("experiments", "MAX_EXPERIMENTS",
                             super()._select_experiments, *a, **kw)


# ---------------------------------------------------------------------
def stimulus_events(name: str) -> list[str]:
    if name == "study":
        return list(STUDY_STREAM)
    if name == "domains_x2":
        out = list(STUDY_STREAM)
        for key in ("developer_workflow", "bug_tracking"):
            out += list(DOMAINS[key][1])
        return out
    if name == "domains_x4":
        out = list(STUDY_STREAM)
        for key in DOMAINS:
            out += list(DOMAINS[key][1])
        return out
    raise ValueError(name)


def run_colony(events, cycles, overrides=None, label="colony") -> dict:
    """Run one cold colony and return its full observation record."""
    db = temp_db(f"audit_{label}.db")
    memory = MemoryService(db_path=str(db))

    saved = {k: getattr(SleepService, k) for k in (overrides or {})}
    for k, v in (overrides or {}).items():
        setattr(SleepService, k, v)

    svc = AuditedSleep(memory)
    for text in events:
        memory.store(text, event_type="event", source="seed:bootstrap")

    t0 = time.time()
    rows = []
    for i in range(cycles):
        start = (i * EVENTS_PER_CYCLE) % len(events)
        for text in events[start:start + EVENTS_PER_CYCLE]:
            memory.store(text, event_type="event", source=f"cycle:{i}")
        rep = svc.run_sleep_cycle()

        # -- AUDIT 3: effective world size -------------------------
        temporal = svc._load_temporal()
        world_tags = set(temporal.keys())
        out_counts = Counter()
        for k, targets in temporal.items():
            out_counts[k] += sum(targets.values())
        total = sum(out_counts.values())
        ent = 0.0
        if total:
            for c in out_counts.values():
                q = c / total
                ent -= q * math.log2(q)
        top10 = (sum(c for _, c in out_counts.most_common(10)) / total
                 if total else 0.0)

        rows.append({
            "pre_cap": dict(svc.pre_cap),
            "pop": {name: len(getattr(rep, attr, []) or [])
                    for name, attr in POPULATION_FIELDS},
            "world_tags": len(world_tags),
            "world_edges": total,
            "world_entropy": round(ent, 4),
            "world_top10_share": round(top10, 4),
            # Funnel widths: how wide the world is at each composition
            # stage. These are the numbers that explain WHY the belief
            # pool is small.
            "composition_anchors": len(svc.composition_anchors),
            "process_tags": len(svc.process_tags),
            "workflow_tags": len(svc.workflow_tags),
            "belief_pairs": len(svc.belief_pairs),
        })

    for k, v in saved.items():
        setattr(SleepService, k, v)
    memory.close()
    db.unlink(missing_ok=True)

    return {"label": label, "cycles": cycles,
            "seconds": round(time.time() - t0, 1), "rows": rows}


# ---------------------------------------------------------------------
def _stats(vals):
    if not vals:
        return {"mean": 0, "median": 0, "p95": 0, "max": 0, "min": 0}
    s = sorted(vals)
    idx = max(0, math.ceil(0.95 * len(s)) - 1)
    return {
        "mean": round(statistics.fmean(s), 3),
        "median": round(statistics.median(s), 3),
        "p95": s[idx],
        "max": max(s),
        "min": min(s),
    }


def audit_pools(colony) -> dict:
    """AUDIT 2: pre-cap pools and retention pressure per capped layer."""
    rows = colony["rows"]
    out = {}
    for layer, cap_attr in CAPPED_LAYERS.items():
        cap = getattr(SleepService, cap_attr)
        vals = [r["pre_cap"].get(layer, 0) for r in rows]
        st = _stats(vals)
        st["cap"] = cap
        st["pressure_mean"] = round(st["mean"] / cap, 3) if cap else 0
        st["pressure_p95"] = round(st["p95"] / cap, 3) if cap else 0
        st["pressure_max"] = round(st["max"] / cap, 3) if cap else 0
        st["cap_binds_p95"] = st["p95"] > cap
        out[layer] = st
    # The belief pool has its own allowance for inert markers.
    if "hypothesis_markers" in rows[0]["pre_cap"]:
        mk = _stats([r["pre_cap"].get("hypothesis_markers", 0) for r in rows])
        mk["cap"] = SleepService.MAX_STRUCTURAL_MARKERS
        mk["note"] = ("inert structural markers; Layer 5 discards them, so "
                      "they are not beliefs and their pressure is not "
                      "selection pressure")
        out["hypothesis_markers"] = mk
    return out


def audit_world(colony) -> dict:
    """AUDIT 3: effective world size."""
    rows = colony["rows"]
    return {
        "world_tags": _stats([r["world_tags"] for r in rows]),
        "world_edges": _stats([r["world_edges"] for r in rows]),
        "world_entropy": _stats([r["world_entropy"] for r in rows]),
        "world_top10_share": _stats([r["world_top10_share"] for r in rows]),
    }


def fingerprint(colony) -> dict:
    """A compact, comparable signature of a colony's behaviour."""
    rows = colony["rows"]
    tail = rows[int(len(rows) * 0.75):] or rows
    pop = {name: round(statistics.fmean([r["pop"].get(name, 0) for r in tail]), 3)
           for name, _ in POPULATION_FIELDS}
    pre = {k: round(statistics.fmean([r["pre_cap"].get(k, 0) for r in tail]), 3)
           for k in sorted({k for r in rows for k in r["pre_cap"]})}
    world = round(statistics.fmean([r["world_tags"] for r in tail]), 3)
    return {"pop": pop, "pre_cap": pre, "world_tags": world}


def diff_fingerprints(base: dict, other: dict) -> dict:
    changed_pop = {k: (base["pop"][k], other["pop"][k])
                   for k in base["pop"] if base["pop"][k] != other["pop"][k]}
    changed_pre = {k: (base["pre_cap"].get(k, 0), other["pre_cap"].get(k, 0))
                   for k in set(base["pre_cap"]) | set(other["pre_cap"])
                   if base["pre_cap"].get(k, 0) != other["pre_cap"].get(k, 0)}
    return {"changed_population": changed_pop,
            "changed_pre_cap_pool": changed_pre,
            "world_tags": (base["world_tags"], other["world_tags"])}


def classify(base_fp, other_fp) -> str:
    d = diff_fingerprints(base_fp, other_fp)
    if d["changed_population"] or d["world_tags"][0] != d["world_tags"][1]:
        return "DECISIVE"
    if d["changed_pre_cap_pool"]:
        return "POOL_ONLY"
    return "INERT"


# ---------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=400)
    ap.add_argument("--part", nargs="+", default=["pools", "params", "world"],
                    choices=["pools", "params", "world", "funnel"])
    ap.add_argument("--param", action="append", default=[],
                    help="NAME=VALUE override, repeatable")
    ap.add_argument("--out", default=str(REPO / "docs" / "instrumentation_audit.json"))
    args = ap.parse_args()

    overrides = {}
    for spec in args.param:
        name, _, val = spec.partition("=")
        current = getattr(SleepService, name)
        overrides[name] = type(current)(val) if not isinstance(current, str) \
            else val

    results = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cycles": args.cycles,
        "overrides": {k: str(v) for k, v in overrides.items()},
        "note": "Phase V1.5 instrumentation audit. Observation only; the "
                "engine is not modified.",
    }

    events = stimulus_events("study")

    if "funnel" in args.part:
        # THE DECISIVE SWEEP.
        #
        # The audit showed Layer 1 is over-truncated (hundreds of
        # candidates for 10-20 slots) while Layer 4 is input-starved
        # (5-8 beliefs for 15 slots). If the Layer-1 caps are what starve
        # the belief layer, then widening Layer 1 must widen the belief
        # pool, and at some point the hypothesis cap must start to bind
        # -- which is the precondition (gate G-P1) for the retention
        # experiment P1 to mean anything.
        print(f"funnel sweep ({args.cycles} cycles per arm) ...")
        funnel = {}
        for cap in (20, 40, 80, 160, 320):
            print(f"  MAX_PREDICTIONS = {cap} ...", flush=True)
            col = run_colony(events, args.cycles,
                             {**overrides, "MAX_PREDICTIONS": cap},
                             f"funnel_{cap}")
            rows = col["rows"]
            tail = rows[int(len(rows) * 0.75):] or rows
            pools = audit_pools(col)
            fp = fingerprint(col)
            funnel[str(cap)] = {
                "layer1_candidates": {
                    "loops_pool_mean": pools["loops"]["mean"],
                    "predictions_pool_mean": pools["predictions"]["mean"],
                    "anomalies_pool_mean": pools["anomalies"]["mean"],
                },
                "layer1_pressure": {
                    "loops": pools["loops"]["pressure_mean"],
                    "predictions": pools["predictions"]["pressure_mean"],
                    "anomalies": pools["anomalies"]["pressure_mean"],
                },
                "funnel_widths": {
                    "meta_anchors": round(statistics.fmean(
                        [r["composition_anchors"] for r in tail]), 2),
                    "process_tags": round(statistics.fmean(
                        [r["process_tags"] for r in tail]), 2),
                    "workflow_tags": round(statistics.fmean(
                        [r["workflow_tags"] for r in tail]), 2),
                    "belief_pairs": round(statistics.fmean(
                        [r["belief_pairs"] for r in tail]), 2),
                },
                "belief_pool_mean": pools["hypotheses"]["mean"]
                    if "hypotheses" in pools else None,
                "hypothesis_pressure_mean": round(
                    (pools["hypotheses"]["mean"] / 15), 3)
                if "hypotheses" in pools else None,
                "hypothesis_pressure_p95": round(
                    (pools["hypotheses"]["p95"] / 15), 3)
                if "hypotheses" in pools else None,
                "hypothesis_cap_binds_p95": pools["hypotheses"]["cap_binds_p95"]
                    if "hypotheses" in pools else None,
                "population_means": fp["pop"],
            }
            print(f"    belief pool={funnel[str(cap)]['belief_pool_mean']} "
                  f"pressure={funnel[str(cap)]['hypothesis_pressure_mean']} "
                  f"pairs={funnel[str(cap)]['funnel_widths']['belief_pairs']} "
                  f"theories={fp['pop']['theories']}")
        results["funnel_sweep_MAX_PREDICTIONS"] = funnel
        print(json.dumps(funnel, indent=2))

    if "pools" in args.part or "params" in args.part:
        print(f"baseline colony ({args.cycles} cycles) ...")
        base = run_colony(events, args.cycles, overrides, "baseline")
        base_fp = fingerprint(base)
        results["baseline_fingerprint"] = base_fp
        if "pools" in args.part:
            print("AUDIT 2 -- pre-cap pools and retention pressure ...")
            results["audit2_pre_cap_pools"] = audit_pools(base)
            results["audit2_pre_cap_pools"]["_population_means"] = base_fp["pop"]
            print(json.dumps(results["audit2_pre_cap_pools"], indent=2))
        if "world" in args.part:
            print("AUDIT 3 -- effective world size ...")
            results["audit3_world_size_study"] = audit_world(base)
            print(json.dumps(results["audit3_world_size_study"], indent=2))

        if "params" in args.part:
            print("AUDIT 1 -- parameter influence map ...")
            influence = {}
            for name, alt in PARAMETER_VARIANTS.items():
                print(f"  {name} = {alt} ...", flush=True)
                arm = run_colony(events, args.cycles, {**overrides, name: alt},
                                 f"param_{name}")
                fp = fingerprint(arm)
                verdict = classify(base_fp, fp)
                influence[name] = {
                    "baseline_value": getattr(SleepService, name),
                    "variant_value": alt,
                    "verdict": verdict,
                    "diff": diff_fingerprints(base_fp, fp),
                    "fingerprint": fp,
                }
                print(f"    -> {verdict}")
            results["audit1_parameter_influence"] = influence

    if "world" in args.part:
        print("AUDIT 3 -- stimulus sweep (world expansion) ...")
        stimulus = {}
        for name in ("study", "domains_x2", "domains_x4"):
            ev = stimulus_events(name)
            print(f"  stimulus {name} ({len(ev)} events) ...", flush=True)
            col = run_colony(ev, args.cycles, overrides, f"stim_{name}")
            fp = fingerprint(col)
            stimulus[name] = {
                "events": len(ev),
                "world_size": audit_world(col),
                "retention_pressure": {
                    layer: {
                        "cap": s["cap"],
                        "pool_mean": s["mean"],
                        "pool_p95": s["p95"],
                        "pool_max": s["max"],
                        "pressure_mean": s["pressure_mean"],
                        "pressure_p95": s["pressure_p95"],
                        "pressure_max": s["pressure_max"],
                    }
                    for layer, s in audit_pools(col).items()
                    if isinstance(s, dict) and "pressure_mean" in s
                },
                "population_means": fp["pop"],
            }
            print(json.dumps(stimulus[name]["retention_pressure"].get(
                "hypotheses", {}), indent=2))
        results["audit3_stimulus_sweep"] = stimulus

    out = Path(args.out)
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
