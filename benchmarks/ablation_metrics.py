"""
benchmarks/ablation_metrics.py
------------------------------------------------------------------
The measurement layer for the Organica ablation study.

Every function here is pure: it takes already-collected observations and
returns a number. Nothing in this module touches the substrate, the engine,
or the database. That separation matters for two reasons:

  1. The definitions below are the *pre-registration contract*. The
     experiment harness in ``ablation_study.py`` collects observations;
     this module decides what they mean. If you want to argue about a
     metric, you argue about this file, not about the harness.

  2. A metric that silently changed between conditions would be worse
     than no metric. Keeping the definitions in one place makes that
     auditable.

WHAT IS MEASURED, AND WHAT IS NOT
---------------------------------
Two of the metrics in the original specification are **structurally
unmeasurable** in this codebase, and one requires a human:

  CY    Curiosity Yield = Q_resolved / Q_generated.
        Nothing ever resolves a Question, because there is no experiment
        executor: Layer 8 emits experiment *candidates* and nothing runs
        them. So CY is identically 0 for every condition, including the
        full system. It cannot discriminate between conditions.

  EIG*  Experiment Information Gain = H_before - H_after.
        Same reason: no experiment is executed, so no belief ever moves.
        Identically 0 for every condition.

  DPF/DSI  Designer Prediction Failure / Designer Surprise Index.
        Requires the human designer to record, *before* a run, what they
        expect the organism to produce. It cannot be automated without
        circularity: an automated "surprise" predictor would be the same
        model that produced the output, so it would predict everything.

CY and EIG* are therefore EXCLUDED from the aggregate rather than zeroed.
Including them at their specified weights (0.15 each) would deflate every
ES score and every Impact score by roughly 30% and miscalibrate every
interpretation band. DPF/DSI is reported as pending a human protocol.

HONESTY NOTE ON THE AGGREGATE
------------------------------
``ES`` is a weighted convenience index. Its normalization constants
(``SCR_REF``, ``CD_CAP``) are conventions, not measurements. The primary
result of the ablation study is the **per-metric delta table**; ES is a
summary of it. Any claim of the form "layer X is foundational" should be
checkable in the raw metric columns, not only in the ES column.

Usage:
    from ablation_metrics import compute_all, ES_WEIGHTS
"""

from __future__ import annotations

import math
from typing import Iterable, Sequence

# ---------------------------------------------------------------------------
# Pre-registered normalisation constants
# ---------------------------------------------------------------------------
# SCR is unbounded (events per surviving structure). We saturate it at
# SCR_REF: 50 experience events represented by one surviving structure is
# "excellent compression" for this system. A condition that reaches it
# scores 1.0; beyond that we cannot distinguish, and we do not pretend to.
SCR_REF = 50.0

# CD is contradictions per 1000 active nodes. We saturate the penalty at
# CD_CAP: one unresolved contradiction per 10 active nodes is total
# epistemic deadlock, and nothing worse is distinguishable.
CD_CAP = 100.0

# A temporal edge must reach this count before the organism will predict it
# (``SleepService.PREDICTION_MIN_COUNT``). The same threshold is used for
# the substrate-level predictor so that PA and PA_substrate differ only in
# *which* pairs the organism chose, never in how confident the graph is.
PREDICTION_MIN_COUNT = 5

# ---------------------------------------------------------------------------
# The aggregate score
# ---------------------------------------------------------------------------
# Specified weights, with CY and EIG* removed and the remainder
# renormalised over the six computable terms.
#
#   spec: PA .20 | IP .15 | CY .15 | EIG* .15 | CDT .10 | NSR .10 | SS .10 | (1-CD) .05
#   kept: PA .20 | IP .15 |          |         | CDT .10 | NSR .10 | SS .10 | (1-CD) .05
#   sum of kept weights = 0.70, so each is divided by 0.70.
ES_WEIGHTS: dict[str, float] = {
    "pa": 0.20 / 0.70,
    "ip": 0.15 / 0.70,
    "cdt": 0.10 / 0.70,
    "nsr": 0.10 / 0.70,
    "ss": 0.10 / 0.70,
    "cd_term": 0.05 / 0.70,
}

# Interpretation bands for Impact(S) = ES_full - ES_without_S.
IMPACT_BANDS = (
    (5.0, "cosmetic"),
    (15.0, "supportive"),
    (30.0, "important"),
    (50.0, "foundational"),
    (float("inf"), "existential"),
)


def impact_band(impact: float) -> str:
    """Classify an Impact score using the pre-registered bands."""
    for threshold, name in IMPACT_BANDS:
        if impact < threshold:
            return name
    return "existential"


# ---------------------------------------------------------------------------
# Primitive metrics
# ---------------------------------------------------------------------------
def f1(tp: float, fp: float, fn: float) -> float:
    """F1 = 2TP / (2TP + FP + FN). 0.0 when there is nothing to score."""
    denom = 2 * tp + fp + fn
    if denom <= 0:
        return 0.0
    return (2 * tp) / denom


def set_f1(predicted: Iterable, truth: Iterable) -> float:
    """F1 over two sets of pairs."""
    p, t = set(predicted), set(truth)
    tp = len(p & t)
    fp = len(p - t)
    fn = len(t - p)
    return f1(tp, fp, fn)


def prediction_counts(edge_map: dict[str, set[str]],
                      contexts: Sequence[Sequence[str]],
                      observed: Sequence[Sequence[str]]) -> tuple[float, float, float]:
    """TP / FP / FN for next-tag prediction over a replayed event sequence.

    ``edge_map`` maps a context tag to the set of tags predicted to follow
    it. For each (context_event, next_event) pair in the replayed sequence:

        TP += |predicted(context) & observed(next)|
        FP += |predicted(context) - observed(next)|
        FN += |observed(next) - predicted(context)|

    This is the standard set-prediction formulation of "did the organism
    predict what actually happened, and did it miss what did happen".

    Counts are returned rather than a score so that several held-out
    blocks can be pooled before the F1 is taken.
    """
    tp = fp = fn = 0.0
    for ctx_tags, obs_tags in zip(contexts, observed):
        for a in ctx_tags:
            predicted = edge_map.get(a, set())
            obs = set(obs_tags)
            tp += len(predicted & obs)
            fp += len(predicted - obs)
            fn += len(obs - predicted)
    return tp, fp, fn


def predictive_f1(edge_map: dict[str, set[str]],
                  contexts: Sequence[Sequence[str]],
                  observed: Sequence[Sequence[str]]) -> float:
    """F1 of next-tag prediction over one replayed sequence."""
    tp, fp, fn = prediction_counts(edge_map, contexts, observed)
    return f1(tp, fp, fn)


def ip_score(pa_full: float | None, pa_compressed: float | None) -> float | None:
    """Information Preservation = PA_compressed / PA_full.

    Undefined when there is no full model to compare against, or when the
    full model makes no predictions at all.
    """
    if pa_full is None or pa_compressed is None:
        return None
    if pa_full <= 0:
        return None
    return max(0.0, min(1.0, pa_compressed / pa_full))


def scr_score(covered_events: int, n_surviving_structures: int) -> float | None:
    """Structural Compression Ratio = covered experience events / surviving structures.

    The numerator is **experience coverage** -- the number of experience
    events represented by the surviving structures -- not the raw event
    count. This matters: with a raw event count, a system that destroys
    its own structures scores a *better* compression ratio, because fewer
    structures always means a bigger ratio. Coverage removes that
    incentive, because structures that do not represent anything score
    nothing.

    Undefined when nothing survived: there is no representation to
    compare the event stream against, and reporting "infinite" would
    flatter an ablated system for the wrong reason.
    """
    if n_surviving_structures <= 0:
        return None
    return covered_events / n_surviving_structures


def ss_score(created: int, survived: int) -> float | None:
    """Survival Selectivity = 1 - survived/created, in [0, 1].

    High = most candidates died (real selection pressure). Low = graph
    bloat. Undefined when nothing was created.
    """
    if created <= 0:
        return None
    return max(0.0, min(1.0, 1.0 - (survived / created)))


def lc_score(grounded: int, resolvable: int) -> float | None:
    """Lineage Completeness = fully traceable nodes / nodes requiring lineage."""
    if resolvable <= 0:
        return None
    return max(0.0, min(1.0, grounded / resolvable))


def cd_score(contradictions: int, active_nodes: int) -> float | None:
    """Contradiction Density = unresolved contradictions per 1000 active nodes.

    Undefined when there are no active nodes. This matters: a system that
    has collapsed to zero structures has no contradiction *density* to
    report, and scoring it as a clean 0.0 would hand a collapsed system a
    perfect contradiction-hygiene mark. Undefined is the honest answer.
    """
    if active_nodes <= 0:
        return None
    return (contradictions / active_nodes) * 1000.0


def cdt_score(pa_with_transfer: float | None, pa_without_transfer: float | None) -> float | None:
    """Cross-Domain Transfer = accuracy with transfer - accuracy without.

    Negative means transferring *hurt*: the donor domain supplied edges
    that were wrong on the target. That is a real result, not a bug, and
    it is floored at 0 for the aggregate only (the raw delta is kept).
    """
    if pa_with_transfer is None or pa_without_transfer is None:
        return None
    return pa_with_transfer - pa_without_transfer


def nsr_score(novel_nodes: int, all_new_nodes: int) -> float | None:
    """Novel Structure Rate = nodes with an unseen topology / all new nodes."""
    if all_new_nodes <= 0:
        return None
    return max(0.0, min(1.0, novel_nodes / all_new_nodes))


# ---------------------------------------------------------------------------
# Canonical topology signatures (for NSR)
# ---------------------------------------------------------------------------
def canonical_signature(candidate: dict) -> str:
    """A stable signature of a candidate's exact topology.

    "Novel" means: this exact topology has never existed in the graph
    before. Two concepts with the same member set are the same topology.
    A concept and a hypothesis with the same tags are different
    topologies, because the type is part of the structure.
    """
    ctype = candidate.get("type", "unknown")

    def joined(seq) -> str:
        return "|".join(str(s) for s in (seq or []))

    if ctype == "concept_candidate":
        return f"concept:{joined(sorted(candidate.get('members') or []))}"
    if ctype == "phrase_candidate":
        return f"phrase:{joined(sorted(candidate.get('members') or []))}"
    if ctype == "loop_candidate":
        return f"loop:{joined(candidate.get('path') or [])}"
    if ctype == "prediction_candidate":
        return f"prediction:{candidate.get('source', '')}|{candidate.get('target', '')}"
    if ctype == "anomaly":
        return f"anomaly:{candidate.get('expected', '')}|{candidate.get('observed', '')}"
    if ctype == "meta_concept":
        return f"meta:{candidate.get('anchor_tag', '')}"
    if ctype == "process_candidate":
        return f"process:{joined(candidate.get('cycle') or [])}"
    if ctype == "workflow_concept":
        return f"workflow:{candidate.get('name', '')}:{joined(candidate.get('components') or [])}"
    if ctype == "hypothesis":
        return f"hypothesis:{candidate.get('subject', '')}|{candidate.get('expectation', '')}"
    if ctype == "theory":
        return f"theory:{candidate.get('subject', '')}:{joined(sorted(candidate.get('evidence', {}).get('expectations') or []))}"
    if ctype == "question":
        return f"question:{candidate.get('subject', '')}:{joined(sorted(candidate.get('competing_expectations') or []))}"
    if ctype == "dream":
        return f"dream:{candidate.get('dream_category', '')}:{candidate.get('subject', '')}:{joined(candidate.get('path_or_context') or [])}"
    if ctype == "investigation":
        return f"investigation:{candidate.get('target_type', '')}|{candidate.get('target_id', '')}"
    if ctype == "experiment":
        return f"experiment:{candidate.get('action_type', '')}|{candidate.get('target_id', '')}"
    return f"{ctype}:{candidate.get('id', '')}"


def edges_implied_by_structures(candidates: Iterable[dict]) -> dict[str, set[str]]:
    """The compressed graph: every tag pair asserted by a surviving structure.

    This is what the organism would have to work with if it kept only its
    own abstractions and threw the raw event stream away. Comparing its
    predictive power against the raw graph gives Information Preservation.
    """
    edges: dict[str, set[str]] = {}

    def add(a: str, b: str) -> None:
        if a and b and a != b:
            edges.setdefault(a, set()).add(b)

    for c in candidates:
        ctype = c.get("type", "")
        if ctype in ("concept_candidate", "phrase_candidate"):
            members = list(c.get("members") or [])
            for i, a in enumerate(members):
                for b in members[i + 1:]:
                    add(a, b)
        elif ctype == "loop_candidate":
            path = list(c.get("path") or [])
            for a, b in zip(path, path[1:]):
                add(a, b)
        elif ctype == "prediction_candidate":
            add(c.get("source", ""), c.get("target", ""))
        elif ctype == "hypothesis":
            add(c.get("subject", ""), c.get("expectation", ""))
        elif ctype == "process_candidate":
            cyc = list(c.get("cycle") or [])
            for i, a in enumerate(cyc):
                add(a, cyc[(i + 1) % len(cyc)] if cyc else "")
        elif ctype == "workflow_concept":
            comps = list(c.get("components") or [])
            for a, b in zip(comps, comps[1:]):
                add(a, b)
        elif ctype == "dream":
            path = list(c.get("path_or_context") or [])
            for a, b in zip(path, path[1:]):
                add(a, b)
    return edges


def structure_tags(candidates: Iterable[dict]) -> set[str]:
    """Every tag mentioned by a surviving structure.

    Used to measure how much of the experience stream the organism's own
    abstractions actually represent.
    """
    tags: set[str] = set()

    def add_all(seq) -> None:
        for v in (seq or []):
            if v:
                tags.add(str(v))

    for c in candidates:
        ctype = c.get("type", "")
        if ctype in ("concept_candidate", "phrase_candidate"):
            add_all(c.get("members"))
        elif ctype == "loop_candidate":
            add_all(c.get("path"))
        elif ctype == "prediction_candidate":
            add_all([c.get("source"), c.get("target")])
        elif ctype == "hypothesis":
            add_all([c.get("subject"), c.get("expectation")])
        elif ctype == "process_candidate":
            add_all(c.get("cycle"))
        elif ctype == "workflow_concept":
            add_all(c.get("components"))
        elif ctype == "dream":
            add_all(c.get("path_or_context"))
        elif ctype == "meta_concept":
            add_all([c.get("anchor_tag")])
        elif ctype == "theory":
            add_all([c.get("subject")])
            add_all(c.get("evidence", {}).get("expectations"))
        elif ctype == "question":
            add_all([c.get("subject")])
            add_all(c.get("competing_expectations"))
    return tags


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------
def _norm_scr(scr: float | None) -> float | None:
    if scr is None:
        return None
    return max(0.0, min(1.0, scr / SCR_REF))


def _norm_cd(cd: float | None) -> float | None:
    if cd is None:
        return None
    penalty = min(1.0, max(0.0, cd / CD_CAP))
    return 1.0 - penalty


def compute_es(metrics: dict) -> tuple[float | None, list[str], dict]:
    """Compute the Emergence Score from a metric dict.

    Returns ``(score, excluded_metrics, contributions)``.

    A metric that is unavailable (``None``) is excluded and the remaining
    weights are renormalised *within this condition*. The excluded list is
    returned so that every ES in the results table can be read with its
    denominator in view.
    """
    raw = {
        "pa": metrics.get("pa"),
        "ip": metrics.get("ip"),
        "cdt": metrics.get("cdt"),
        "nsr": metrics.get("nsr"),
        "ss": metrics.get("ss"),
        "cd_term": _norm_cd(metrics.get("cd")),
    }
    available = {k: v for k, v in raw.items() if v is not None}
    excluded = sorted(k for k, v in raw.items() if v is None)
    if not available:
        # Every metric depends on the organism having produced something.
        # Zero, not undefined: a system that produced nothing scores zero.
        return 0.0, excluded, {}

    weight_sum = sum(ES_WEIGHTS[k] for k in available)
    contributions = {
        k: (ES_WEIGHTS[k] / weight_sum) * v for k, v in available.items()
    }
    score = sum(contributions.values()) * 100.0
    return score, excluded, contributions


def compute_all(observations: dict) -> dict:
    """Turn raw observations into the full metric set plus the aggregate.

    ``observations`` keys expected (all optional except where noted):

        n_experience_events      int
        n_surviving_structures   int
        created / survived       dict[label, int]
        predictions              set[(src, tgt)]     the organism's Layer-1 predictions
        graph_edges              dict[src, set[tgt]] the substrate graph at threshold
        structures               list[dict]          surviving candidates
        pa                       float|None          already-computed organism F1
        pa_substrate             float|None
        pa_compressed            float|None
        contradictions           int
        active_nodes             int
        pa_with_transfer         float|None
        pa_without_transfer      float|None
        novel_nodes              int
        all_new_nodes            int
        grounded / resolvable    int
    """
    metrics: dict = {}

    # --- PA -------------------------------------------------------------
    metrics["pa"] = observations.get("pa")
    metrics["pa_substrate"] = observations.get("pa_substrate")

    # --- IP -------------------------------------------------------------
    metrics["ip"] = ip_score(
        observations.get("pa_substrate"),
        observations.get("pa_compressed"),
    )

    # --- SCR ------------------------------------------------------------
    metrics["scr"] = scr_score(
        observations.get("covered_events", 0),
        observations.get("n_surviving_structures", 0),
    )
    metrics["coverage_ratio"] = (
        observations.get("covered_events", 0) / observations["n_experience_events"]
        if observations.get("n_experience_events") else None
    )

    # --- SS -------------------------------------------------------------
    created = observations.get("created", {})
    survived = observations.get("survived", {})
    per_gen = {}
    for label, n_created in created.items():
        if n_created <= 0:
            continue
        n_surv = survived.get(label, 0)
        s = ss_score(n_created, n_surv)
        if s is not None:
            per_gen[label] = round(s, 4)
    metrics["ss"] = (sum(per_gen.values()) / len(per_gen)) if per_gen else None
    metrics["ss_per_generation"] = per_gen

    # --- LC -------------------------------------------------------------
    metrics["lc"] = lc_score(
        observations.get("grounded", 0),
        observations.get("resolvable", 0),
    )

    # --- CD -------------------------------------------------------------
    # Measured over the whole run, not read off the final cycle. Generation
    # 5 oscillates (journal finding 6), so a single-cycle snapshot of
    # contradictions is a sample of a fluctuating quantity rather than a
    # property of the system.
    cd_mean = observations.get("cd_mean_density")
    if cd_mean is None:
        metrics["cd"] = cd_score(
            observations.get("contradictions", 0),
            observations.get("active_nodes", 0),
        )
    else:
        metrics["cd"] = cd_mean
    metrics["cd_duty_cycle"] = observations.get("cd_duty_cycle")
    metrics["cd_mean_competing_subjects"] = observations.get("cd_mean_competing_subjects")

    # --- CDT ------------------------------------------------------------
    metrics["cdt"] = cdt_score(
        observations.get("pa_with_transfer"),
        observations.get("pa_without_transfer"),
    )

    # --- NSR ------------------------------------------------------------
    metrics["nsr"] = nsr_score(
        observations.get("novel_nodes", 0),
        observations.get("all_new_nodes", 0),
    )

    # --- Not measurable, by construction --------------------------------
    metrics["cy"] = None
    metrics["cy_note"] = ("not measurable: no experiment executor exists, so no "
                          "Question is ever resolved")
    metrics["eig_star"] = None
    metrics["eig_star_note"] = ("not measurable: experiments are generated but never "
                                "executed, so no belief entropy ever changes")
    metrics["dpf"] = None
    metrics["dpf_note"] = ("pending: requires the human designer to record predictions "
                           "before a run; cannot be automated without circularity")

    # --- Aggregate ------------------------------------------------------
    score, excluded, contributions = compute_es(metrics)
    metrics["es"] = score
    metrics["es_excluded"] = excluded
    metrics["es_contributions"] = {k: round(v * 100.0, 3) for k, v in contributions.items()}
    return metrics


def compare(full: dict, ablated: dict) -> dict:
    """Per-metric deltas plus the Impact score for one ablation.

    The deltas are the primary result. The Impact score is a summary of
    them and inherits every weakness of the aggregate's normalisation.
    """
    keys = ["pa", "pa_substrate", "ip", "scr", "ss", "lc", "cd", "cdt", "nsr"]
    deltas = {}
    for k in keys:
        f, a = full.get(k), ablated.get(k)
        if f is None or a is None:
            deltas[k] = None
        else:
            deltas[k] = round(f - a, 4)

    es_full, es_abl = full.get("es"), ablated.get("es")
    impact = None
    if es_full is not None and es_abl is not None:
        impact = es_full - es_abl

    return {
        "deltas": deltas,
        "es_full": es_full,
        "es_ablated": es_abl,
        "impact": None if impact is None else round(impact, 3),
        "impact_band": None if impact is None else impact_band(impact),
        "metrics_excluded_full": full.get("es_excluded", []),
        "metrics_excluded_ablated": ablated.get("es_excluded", []),
    }


def shannon_entropy(pairs: Sequence[float]) -> float:
    """Shannon entropy in bits of a small discrete distribution."""
    total = sum(pairs)
    if total <= 0:
        return 0.0
    h = 0.0
    for p in pairs:
        if p > 0:
            q = p / total
            h -= q * math.log2(q)
    return h
