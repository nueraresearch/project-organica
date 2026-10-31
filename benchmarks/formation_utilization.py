"""Formation versus utilization — the harness for the pre-registered experiment.

    docs/FORMATION-UTILIZATION-PREREGISTRATION.md        (committed at 8536d9a)

THE QUESTION
------------
Given that the world's relation CAN be held at all, does holding it predict
better than the strongest data-only learner — on retention, on transfer, and on
revision?  Gate 13 showed formation failing at the frozen cap of 20; the paired
capacity test showed it succeeding at 1,000.  Neither was scored downstream.
This harness runs the three arms that turn that pair of formation results into a
utilization measurement.

THE ARMS (§4)
-------------
    A  cap 20     no filter       the published failure
    B  cap 1,000  no filter       formation at the measured precision ceiling
    C  cap 1,000  support filter  utilization GIVEN correct structure

The filter is harness-side.  ``organica/`` is never edited: each arm is an
in-process subclass, the same instrument ``run_paired_capacity_test.py`` used.
The filter rewrites the ``temporal`` mapping BEFORE candidate construction, so
the engine's cap applies after the filter and ``freqs`` — and therefore every
candidate's evidence — is the engine's own.  Turning the filter off must leave
the substrate byte-identical to the unfiltered arm; ``tests/
test_formation_utilization.py`` proves it.

Arm C is a CEILING, not a learner.  It receives the world's law at admission,
which no data-only learner does.  A result from it may never be headlined as
"the organism learned the law".

THE ORACLE SET (§3.1)
---------------------
The generator's full non-zero transition support, materialized from the
generator's own parameters before any arm runs.  It is not derived from the
organism, from observed data, or from any scoring window.  It is computed per
regime and the harness REFUSES to run if the two regimes disagree, because one
frozen filter has to serve the revision limb; silently handing revision a
filter built from the old law would be a handicapped arm, not a test.

THREE DISCLOSURES, FIXED BEFORE THE TIMING RUN
----------------------------------------------
1. A6's committed wording asks that shuffling the oracle make C "collapse to
   B's coverage".  That cannot happen: B's coverage is 98–100 %, and a shuffled
   filter can only lower C's coverage.  The audit is implemented as the
   comparison that can discriminate — shuffled precision back in B's measured
   band, shuffled coverage under A1's own 0.50 gate, and the shuffled transfer
   score not matching C's — and this document says the original wording is
   superseded.  Nothing was relaxed: the substituted checks are stricter on
   the quantity that matters (the score) and use thresholds already committed
   elsewhere in the same protocol.
2. §3.4 says "four scored windows"; §4.4's table lists revision 200–249 AND a
   held-out 250–299, while the pinned runner scores three limbs.  Three limbs
   is what §7's Bonferroni-over-three assumes.  This harness implements three:
   retention 110–149, transfer 150–199, revision 250–299.  The learning window
   200–249 is where the revision is acquired, not where it is scored.
3. T1's generator switches law at cycle 150 by default, which would put the
   switch inside the transfer window §4.4 says is under the OLD law.  The
   harness passes ``regime_cycles=200`` and verifies the recorded regime at the
   boundary.  The module default and §4.4 disagree; the report says so.

A6 is gated only where a size-matched wrong filter exists — that is, where the
shuffle retains none of the true pairs.  On T2 it retains none.  On T1 the
support covers 12 of 16 targets per source, so any size-matched filter is
partly true by construction; A6 is reported there, marked not applicable, and
the retained share is printed.  The campaign's gate is the primary task, T2.
Calling a control "passed" where it could not discriminate would be the exact
failure AGENTS rule 25(c) records.

TWO AUDIT-SCOPE CORRECTIONS, MADE BEFORE THE CAMPAIGN
-----------------------------------------------------
A2 is implemented on the arm's OWN stream, which is what the committed text
says: C's admitted set equals the engine's count-threshold-eligible pairs
restricted to the support.  A stronger comparison (C against B's permitted
subset) was implemented first and failed; it is not the committed audit, and
folding it in would have been a stronger criterion wearing A2's name.  Under
Amendment 1 the stronger comparison is audit A8, which gates the run.

A3's 0.3443 band was measured on T2.  It is applied on T2 and reported, not
gated, on T1, which has no committed band; applying a T2 constant to a
different world is the wrong-metric defect of AGENTS rule 23(a).

AMENDMENT 1, AND THE FEEDBACK LOOP IT CLOSES
--------------------------------------------
The timing pass measured a confound the committed protocol did not anticipate.
`_record_temporal_edges` is called only for world events, but its window is the
last three ROWS of `events`, and sleep rows are rows: the last sleep rows of
cycle k occupy window slots for the first world events of cycle k+1, and their
tags become `tag_from` values.  Arms that admit different candidate sets store
different sleep rows and are therefore given a different temporal graph on the
next cycle.  D1 measured it — on T2 32 edges differ and 59 of 131 permitted
streams differ; on T1 21 edges and 107 of 160 — and the pre-amendment artifact
is preserved as `docs/formation_utilization_timing_pre_amendment.json`.

Amendment 1 (`docs/FORMATION-UTILIZATION-PREREGISTRATION.md` §12) fixes the
temporal basis at arm B's.  B is run first and its `_load_temporal()` graph is
recorded at the start of each sleep cycle.  C and S are then run with
`_load_temporal()` returning that recorded graph for the same cycle index, and
each asserts it consumed exactly as many graphs as B produced.  A and B are
unchanged, and `organica/` is not edited.  A8 (`audit_temporal_input`) gates
the result: at every cycle the graph each admission arm read, its eligible
candidate set and the evidence on shared pairs must equal B's.

What it fixes: C's admission can no longer change C's temporal input.  What it
does not fix: B's graph still contains B's own sleep rows (the shipped engine
is not sleep-blind), C's own payload and prior still differ (that is the
treatment), and C is a counterfactual trajectory on B's evidence, not an
independent organism.  A C result is therefore "admission filtering at fixed
temporal evidence", never "the engine with this filter installed".

Usage
-----
    python benchmarks/formation_utilization.py --timing
    python benchmarks/formation_utilization.py --campaign --seeds 30 --workers 8

The timing pass writes ``docs/formation_utilization_timing.json`` / ``.md``.
Only a full campaign writes ``docs/formation_utilization.json`` / ``.md``.
Standard library only.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import re
import statistics
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica import __version__ as ENGINE_VERSION  # noqa: E402
from organica.memory import MemoryService  # noqa: E402
from organica.paths import LIVE_DB, scratch_db  # noqa: E402

from benchmarks.acquisition_baselines import (  # noqa: E402
    fit_bigram,
    fit_cell_counter,
    score as house_score,
)
from benchmarks.acquisition_compositional import (  # noqa: E402
    CYCLES,
    EVENTS_PER_CYCLE,
    PHASE_ACQUISITION,
    PHASE_RETENTION,
    PHASE_REVISION_LEARN,
    PHASE_REVISION_TEST,
    PHASE_TRANSFER,
    PHASE_WARMUP,
    cell_conditional,
    generate_compositional_world,
    make_ceiling,
)
from benchmarks.acquisition_harness import (  # noqa: E402
    _CapOverrideSleepService,
    _world_compositional_edges,
)
from benchmarks.acquisition_runner import (  # noqa: E402
    candidate_summary,
    evaluate_shapes,
    fit_replay_learner,
    make_organica_backoff,
    structure_edges,
)
from benchmarks.acquisition_world import (  # noqa: E402
    GROUPS,
    NOISE_STATE,
    NOISE_TAGS,
    generate_rule_world,
    group_of,
    next_event_distribution,
)

# ---------------------------------------------------------------------------
# Constants — every one of them committed before the timing run
# ---------------------------------------------------------------------------

TASK_T1 = "T1"          # calibration / control (acquisition §4.1)
TASK_T2 = "T2"          # primary
TASKS = (TASK_T2, TASK_T1)
LIMBS = ("retention", "transfer", "revision")

ALPHA = 256.0
REPLAY_CFG = {"window": 1, "half_life": None, "alpha": 0.5}
STAT_CFG = (0.1, None, None)

CAP_A = 20
CAP_B = 1_000

COVERAGE_GATE = 0.50            # Gate 13 / A1
PRECISION_CEILING = 0.3443      # GATE13-RANKING-CRITERION
PRECISION_TOL = 0.01            # A3's band
ATTRIBUTION_MIN = 0.50          # A7
A6_SCORE_TOL = 0.01             # nats; A6's "not as good as C"

DECISION_ALPHA = 0.9833         # Bonferroni over three limbs
BOOTSTRAP_REPS = 10_000
BOOTSTRAP_SEED = 0

CALIBRATION_SEED = 20261099     # the seed every hyperparameter is frozen from
TIMING_SEED = 20261100          # exploratory; already spent by Gate 13
CAMPAIGN_SEED_START = 20261101
CAMPAIGN_SEED_COUNT = 30

T1_REGIME_CYCLES = 200          # see disclosure 3
SYNTHETIC_ALPHA = 1.0           # A5 audits the construct, not the calibration

TIMING_OUT = "docs/formation_utilization_timing.json"
TIMING_MD = "docs/formation_utilization_timing.md"
CAMPAIGN_OUT = "docs/formation_utilization.json"
CAMPAIGN_MD = "docs/formation_utilization.md"


# ---------------------------------------------------------------------------
# The oracle set (§3.1) and the no-leakage control
# ---------------------------------------------------------------------------

def build_world(task: str, seed: int, cycles: int = CYCLES,
                epc: int = EVENTS_PER_CYCLE) -> dict:
    """Generate the task's world.  T1 is generated with a switch at cycle 200."""
    if task == TASK_T2:
        return generate_compositional_world(seed=seed, cycles=cycles,
                                            events_per_cycle=epc)
    return generate_rule_world(seed=seed, cycles=cycles, events_per_cycle=epc,
                               regime_cycles=T1_REGIME_CYCLES)


def build_support(task: str, world: dict, regime: int = 0) -> set[tuple[str, str]]:
    """The generator's full non-zero transition support, from its parameters."""
    if task == TASK_T2:
        cond = cell_conditional(regime, world["cell_tags"])
        tag_to_cell = world["tag_to_cell"]
        return {(u, v)
                for u in tag_to_cell
                for v, p in cond[tag_to_cell[u]].items() if p > 0.0}

    dist = next_event_distribution(regime)
    tags = [t for members in GROUPS.values() for t in members] + list(NOISE_TAGS)
    support: set[tuple[str, str]] = set()
    for u in tags:
        for v, p in dist.get(group_of([u]), {}).items():
            if p > 0.0:
                support.add((u, v))
    return support


def shuffled_support(support: set[tuple[str, str]], seed: int = 0
                     ) -> tuple[set[tuple[str, str]], dict[str, Any]]:
    """A size-matched wrong filter: same sources, same out-degree, wrong pairs.

    Per source, targets are drawn from the tags that the generator does NOT
    permit from that source.  Where the complement is smaller than the row
    (T1: 12 permitted targets out of a 16-tag vocabulary), the remainder is
    filled from the permitted row and the retained share is reported.  A6 is
    gated only where that share is zero — see the module docstring.
    """
    by_source: dict[str, list[str]] = defaultdict(list)
    for u, v in sorted(support):
        by_source[u].append(v)
    vocab = sorted({u for u, _ in support} | {v for _, v in support})
    rng = random.Random(seed)
    out: set[tuple[str, str]] = set()
    filled = 0
    retained = 0
    for u in sorted(by_source):
        want = len(by_source[u])
        forbidden = [v for v in vocab if (u, v) not in support]
        rng.shuffle(forbidden)
        take = forbidden[:want]
        if len(take) < want:
            permitted = [v for v in vocab if (u, v) in support and v not in take]
            rng.shuffle(permitted)
            pad = permitted[: want - len(take)]
            take = take + pad
            filled += len(pad)
        retained += sum(1 for v in take if (u, v) in support)
        out.update((u, v) for v in take)
    meta = {
        "size": len(out),
        "support_size": len(support),
        "retained_permitted": retained,
        "retained_share": round(retained / max(len(support), 1), 4),
        "filled_from_permitted": filled,
    }
    return out, meta


# ---------------------------------------------------------------------------
# Windows, vocabulary, and the prepared world (shared by every arm of a seed)
# ---------------------------------------------------------------------------

def _window_pairs(events: list[str], lo: int, hi: int, epc: int
                  ) -> tuple[list[list[str]], list[list[str]]]:
    idx = list(range(lo * epc, hi * epc))
    ctx = [sorted(events[idx[k]].split()) for k in range(len(idx) - 1)]
    obs = [sorted(events[idx[k + 1]].split()) for k in range(len(idx) - 1)]
    return ctx, obs


def world_edges_from_training(world: dict, task: str) -> set[tuple[str, str]]:
    """Edges the organism was exposed to in acquisition (Gate 13's numerator).

    T2 reuses the pinned harness function, which honours the withheld mask.
    T1 has no withheld combination, so the same pairwise rule is applied to the
    acquisition window directly.
    """
    if task == TASK_T2:
        return _world_compositional_edges(world)
    events = world["events"]
    epc = EVENTS_PER_CYCLE
    lo, hi = PHASE_ACQUISITION
    prev: list[str] = []
    edges: set[tuple[str, str]] = set()
    for i, text in enumerate(events):
        cur = text.split()
        if lo * epc <= i < hi * epc:
            for a in prev:
                for b in cur:
                    if a != b:
                        edges.add((a, b))
        prev = cur
    return edges


def _latent_map(task: str, world: dict) -> dict[str, str]:
    """The comparison learner's granted latent state (scoring-side only)."""
    if task == TASK_T2:
        return dict(world["tag_to_cell"])
    out = {t: g for g, members in GROUPS.items() for t in members}
    for t in NOISE_TAGS:
        out[t] = NOISE_STATE
    return out


def prepare_world(task: str, seed: int) -> dict:
    """Everything a seed needs that does not depend on the arm."""
    t0 = time.perf_counter()
    world = build_world(task, seed)
    events = world["events"]
    epc = EVENTS_PER_CYCLE
    trainable = world["trainable"] if "trainable" in world else [True] * len(events)

    warm_lo, _ = PHASE_WARMUP
    acq_lo, acq_hi = PHASE_ACQUISITION
    exposure = [i for i in range(warm_lo * epc, acq_hi * epc)
                if not (acq_lo * epc <= i < acq_hi * epc) or trainable[i]]
    rows = [events[i] for i in exposure]
    vocab = {t for r in rows for t in r.split()}

    counts: dict[str, int] = defaultdict(int)
    for r in rows:
        for t in r.split():
            counts[t] += 1
    total = sum(counts.values()) or 1
    base_rate = {t: n / total for t, n in counts.items()}

    ret_ctx, ret_obs = _window_pairs(events, *PHASE_RETENTION, epc)
    tr_ctx, tr_obs = _window_pairs(events, *PHASE_TRANSFER, epc)
    rev_ctx, rev_obs = _window_pairs(events, *PHASE_REVISION_TEST, epc)

    limbs = {
        "retention": (ret_ctx, ret_obs),
        "transfer": (tr_ctx, tr_obs),
        "revision": (rev_ctx, rev_obs),
    }
    limb_counts = {
        name: {
            "events": len(ctx),
            "cells": sum(len(c) for c in ctx) * len(vocab),
            "excluded_observation_tokens": sum(
                1 for obs in obs for t in obs if t not in vocab),
        }
        for name, (ctx, obs) in limbs.items()
    }

    switch = T1_REGIME_CYCLES if task == TASK_T1 else 200
    if len(events) > switch * epc:
        if task == TASK_T1:
            observed = world["hidden_regimes"][switch * epc]
        else:
            observed = world["regimes"][switch * epc]
        if observed != 1:
            raise AssertionError(
                f"{task} seed {seed}: regime at cycle {switch} is {observed}, "
                "expected the new law — the limb windows would be wrong")

    prep = {
        "task": task,
        "seed": seed,
        "events": events,
        "trainable": trainable,
        "epc": epc,
        "vocab": vocab,
        "rows": rows,
        "base_rate": base_rate,
        "windows": limbs,
        "limb_counts": limb_counts,
        "world": world,
        "world_edges": world_edges_from_training(world, task),
        "tag_to_latent": _latent_map(task, world),
        "regime_switch_cycle": switch,
        "prepare_seconds": round(time.perf_counter() - t0, 3),
    }
    return prep


def reference_ceiling(task: str, world: dict, regime: int) -> Callable[[str, str], float]:
    if task == TASK_T2:
        return make_ceiling(world, regime)
    dist = next_event_distribution(regime)

    def prob(u: str, v: str) -> float:
        return dist.get(group_of([u]), {}).get(v, 0.0)

    return prob


def evaluate_limbs(prob: Callable[[str, str], float], prep: dict,
                   limbs: tuple[str, ...] = LIMBS) -> dict[str, Any]:
    out = {}
    for name in limbs:
        ctx, obs = prep["windows"][name]
        out[name] = evaluate_shapes(prob, ctx, obs, prep["vocab"])
    return out


# ---------------------------------------------------------------------------
# The arms
# ---------------------------------------------------------------------------

class _AdmissionSleepService(_CapOverrideSleepService):
    """Recording subclass: filter, then the engine's cap, in that order.

    ``_CapOverrideSleepService`` builds the candidate list exactly as the frozen
    engine does and truncates at ``diagnostic_max_predictions``.  This subclass
    raises that bound while it asks the parent for the full list, records the
    list, and then applies the SAME slice the engine applies.  Nothing about
    candidate construction, the count filter, the sort key or the evidence
    fields changes, and recording is proven behavior-neutral by a test that
    compares every substrate table against a run without it.

    Under Amendment 1, ``fixed_temporal`` supplies the graph the sleep service
    reads for each cycle.  It is arm B's recorded graph, captured at the start
    of its sleep cycle; the admission arms read it instead of their own so that
    what they admit cannot change what they are given next.  The graph returned
    by ``_load_temporal`` is recorded in ``temporal_reads`` either way, so A8
    checks what the service actually read rather than what the harness meant to
    pass.  A fixed list that is not consumed exactly once per cycle raises.
    """

    def __init__(self, memory: MemoryService, max_predictions: int,
                 admission: set[tuple[str, str]] | None = None,
                 fixed_temporal: list[dict[str, dict[str, int]]] | None = None
                 ) -> None:
        super().__init__(memory, max_predictions)
        self._arm_cap = max_predictions
        self.admission = None if admission is None else frozenset(admission)
        self.fixed_temporal = fixed_temporal
        self.fixed_cursor = 0
        self.temporal_reads: list[dict[str, dict[str, int]]] = []
        self.pre_cap: list[list[tuple[str, str]]] = []
        self.pre_cap_evidence: list[dict[tuple[str, str], dict]] = []
        self.admitted: list[list[tuple[str, str]]] = []
        self.admitted_evidence: list[dict[tuple[str, str], dict]] = []
        self.eligible: list[list[tuple[str, str]]] = []

    def _load_temporal(self) -> dict[str, dict[str, int]]:
        if self.fixed_temporal is None:
            graph = super()._load_temporal()
        else:
            if self.fixed_cursor >= len(self.fixed_temporal):
                raise AssertionError(
                    "the fixed temporal basis is exhausted before the run ended")
            graph = self.fixed_temporal[self.fixed_cursor]
            self.fixed_cursor += 1
        copied = {source: dict(targets) for source, targets in graph.items()}
        self.temporal_reads.append(copied)
        return copied

    def _build_predictions(self, temporal, freqs):
        # The engine's own count threshold, applied to the UNFILTERED temporal
        # graph.  This is the denominator A2's "no missing pair above the count
        # threshold" names, and it must be recorded before the filter runs.
        self.eligible.append(
            [(u, v) for u, targets in temporal.items()
             for v, count in targets.items()
             if count >= self.PREDICTION_MIN_COUNT])
        if self.admission is not None:
            filtered = {
                u: {v: c for v, c in targets.items() if (u, v) in self.admission}
                for u, targets in temporal.items()
            }
            temporal = {u: t for u, t in filtered.items() if t}
        self.diagnostic_max_predictions = 10 ** 9
        try:
            candidates = super()._build_predictions(temporal, freqs)
        finally:
            self.diagnostic_max_predictions = self._arm_cap
        self.pre_cap.append([(c.source, c.target) for c in candidates])
        self.pre_cap_evidence.append(
            {(c.source, c.target): dict(c.evidence) for c in candidates})
        admitted = candidates[: self._arm_cap]
        self.admitted.append([(c.source, c.target) for c in admitted])
        self.admitted_evidence.append(
            {(c.source, c.target): dict(c.evidence) for c in admitted})
        return admitted


def _fresh_db(name: str) -> Path:
    path = scratch_db(name)
    path.unlink(missing_ok=True)
    if path.resolve() == LIVE_DB.resolve():
        raise AssertionError(f"refusing to write to the live DB: {path}")
    return path


def _unique_candidates(candidates: list[dict]) -> list[dict]:
    by_id: dict = {}
    for c in candidates:
        key = c.get("id")
        if key is None:
            key = id(c)
        by_id.setdefault(key, c)
    return list(by_id.values())


def layer1_pairs(candidates: list[dict]) -> set[tuple[str, str]]:
    return {(c["source"], c["target"])
            for c in _unique_candidates(candidates)
            if c.get("type") == "prediction_candidate"
            and c.get("source") and c.get("target")}


def run_arm(prep: dict, label: str, cap: int,
            admission: set[tuple[str, str]] | None = None,
            fixed_temporal: list[dict[str, dict[str, int]]] | None = None
            ) -> dict[str, Any]:
    """One engine run, scored on all three limbs, with the admission recorded.

    ``fixed_temporal`` is arm B's per-cycle graph under Amendment 1.  When it
    is supplied, every sleep cycle reads the next graph in the list and the run
    asserts the list was consumed exactly once per cycle; a short list stops
    the run rather than silently falling back to the arm's own graph.
    """
    task, seed = prep["task"], prep["seed"]
    events, epc = prep["events"], prep["epc"]
    acq_lo, acq_hi = PHASE_ACQUISITION
    rev_lo, rev_hi = PHASE_REVISION_LEARN
    db = _fresh_db(f"fu_{task}_{label}_{seed}.db")
    mem = MemoryService(str(db))
    svc = _AdmissionSleepService(mem, cap, admission, fixed_temporal)
    timings: dict[str, float] = {}
    try:
        t0 = time.perf_counter()
        for i in range(acq_hi * epc):
            in_acq = acq_lo * epc <= i < acq_hi * epc
            if in_acq and not prep["trainable"][i]:
                continue
            source = "env_acq" if in_acq else "env"
            mem.store(events[i], event_type="observe", source=source)
            if (i + 1) % epc == 0:
                svc.run_sleep_cycle()
                # The live daemon prunes every cycle (run_continuous.py).  The
                # retention window is 20,000 rows, five times the 4,000-row
                # cognition window, so this only bounds disk: the newest 4,000
                # sleep rows — the only ones `_load_prior_candidates` reads —
                # are never touched.
                mem.prune_sleep_candidates()
        timings["acquisition"] = round(time.perf_counter() - t0, 3)

        t0 = time.perf_counter()
        frozen = svc._load_prior_candidates()
        # The engine's OWN graph at the end of acquisition.  This is the point
        # D1 measured and A8's footnote compares; it is not read by Layer 1 for
        # the admission arms under Amendment 1.
        temporal_pairs = {(u, v) for u, v, _n in mem.temporal_edges(min_count=1)}
        asserted_rows = structure_edges(frozen)
        asserted = {(u, v) for u, targets in asserted_rows.items() for v in targets}
        triggered = layer1_pairs(frozen)
        world_edges = prep["world_edges"]

        # Gate 13's basis: every structure type the readout aggregates.
        covered = asserted & world_edges
        coverage = len(covered) / len(world_edges) if world_edges else 0.0
        readout_precision = len(covered) / len(asserted) if asserted else 0.0

        # Layer 1 alone — the layer the oracle controls, and the basis on which
        # the 0.3443 precision ceiling was measured (GATE13-RANKING-CRITERION).
        layer1_covered = triggered & world_edges
        layer1_coverage = (len(layer1_covered) / len(world_edges)
                           if world_edges else 0.0)
        layer1_precision_world = (len(layer1_covered) / len(triggered)
                                  if triggered else None)
        layer1_precision_support = (len(triggered & prep["support"]) / len(triggered)
                                    if prep.get("support") and triggered else None)
        summary = candidate_summary(frozen)
        prob = make_organica_backoff(asserted_rows, prep["base_rate"], ALPHA)
        scores = evaluate_limbs(prob, prep, ("retention", "transfer"))
        timings["scoring"] = round(time.perf_counter() - t0, 3)

        t0 = time.perf_counter()
        for cyc in range(rev_lo, rev_hi):
            for ev in events[cyc * epc:(cyc + 1) * epc]:
                mem.store(ev, event_type="observe", source="env_rev")
            svc.run_sleep_cycle()
            mem.prune_sleep_candidates()
        timings["revision_learning"] = round(time.perf_counter() - t0, 3)

        t0 = time.perf_counter()
        post = svc._load_prior_candidates()
        post_asserted = structure_edges(post)
        prob_rev = make_organica_backoff(post_asserted, prep["base_rate"], ALPHA)
        scores.update(evaluate_limbs(prob_rev, prep, ("revision",)))
        timings["revision_scoring"] = round(time.perf_counter() - t0, 3)
    finally:
        mem._conn.close()
        try:
            db.unlink(missing_ok=True)
        except PermissionError:
            pass

    if fixed_temporal is not None and svc.fixed_cursor != len(fixed_temporal):
        raise AssertionError(
            f"arm {label}: the run ended after {svc.fixed_cursor} of "
            f"{len(fixed_temporal)} fixed temporal graphs")

    return {
        "label": label,
        "cap": cap,
        "admission": ("none" if admission is None
                      else "support" if admission == prep.get("support")
                      else "shuffled"),
        "seconds": timings,
        "seconds_total": round(sum(timings.values()), 3),
        "coverage": round(coverage, 4),
        "readout_precision": round(readout_precision, 4),
        "layer1_coverage": round(layer1_coverage, 4),
        "layer1_precision_world": (None if layer1_precision_world is None
                                   else round(layer1_precision_world, 4)),
        "layer1_precision_support": (None if layer1_precision_support is None
                                     else round(layer1_precision_support, 4)),
        "asserted_edges": len(asserted),
        "covered_world_edges": len(covered),
        "layer1_edges": len(triggered),
        "scores": scores,
        "per_type": summary["per_type"],
        "total_prediction_admissions": sum(len(a) for a in svc.admitted),
        "max_pre_cap_candidates": max((len(p) for p in svc.pre_cap), default=0),
        "_raw": {
            "pre_cap": svc.pre_cap,
            "admitted": svc.admitted,
            "eligible": svc.eligible,
            "pre_cap_evidence": svc.pre_cap_evidence,
            "admitted_evidence": svc.admitted_evidence,
            "temporal_pairs": temporal_pairs,
            "temporal_reads": svc.temporal_reads,
            # The diagnostic needs the readout's exact input, not only its score.
            # These are popped by the campaign's run_task_seed before the artifact
            # is written, so the campaign artifact does not grow.
            "asserted_rows": asserted_rows,
            "post_asserted": post_asserted,
            "frozen_candidates": frozen,
            "post_candidates": post,
        },
    }


# ---------------------------------------------------------------------------
# The eight audits — each one able to fail
# ---------------------------------------------------------------------------

def audit_arm_differential(coverage: dict[str, float],
                           gate: float = COVERAGE_GATE) -> dict[str, Any]:
    """A1: the arms must sit on the sides of the gate the protocol names."""
    checks = {
        "A_below_gate": coverage["A"] < gate,
        "B_at_or_above_gate": coverage["B"] >= gate,
        "C_at_or_above_gate": coverage["C"] >= gate,
    }
    passed = all(checks.values())
    if passed:
        reason = (f"arms differ as specified: A {coverage['A']:.4f} < "
                  f"{gate:.2f} <= B {coverage['B']:.4f}, C {coverage['C']:.4f}")
    else:
        failing = [k for k, ok in checks.items() if not ok]
        reason = ("the arms did not differ as specified; failing: "
                  + ", ".join(failing))
    return {"audit": "A1", "name": "arm differential", "passed": passed,
            "applicable": True, "checks": checks,
            "evidence": {"coverage": coverage, "gate": gate}, "reason": reason}


def audit_oracle_exactness(eligible: list[list[tuple[str, str]]],
                           admitted: list[list[tuple[str, str]]],
                           support: set[tuple[str, str]],
                           cap: int,
                           pre_cap_evidence: list[dict] | None = None,
                           admitted_evidence: list[dict] | None = None
                           ) -> dict[str, Any]:
    """A2: the filter admits the support and nothing else, with nothing lost.

    This is the committed audit, on the arm's OWN candidate stream.  The
    denominator is the set of pairs the engine's own count threshold permits on
    the temporal graph C reads — recorded BEFORE the filter runs — intersected
    with the generator's support.  C's admitted set must equal it: no extra
    pair, no missing permitted pair, and the evidence attached to each must be
    the engine's own.

    It deliberately does NOT fold the C-versus-B comparison into A2.  Under
    Amendment 1 the admission arms read arm B's temporal graph, so the evidence
    is shared by construction; A8 checks that separately and as a gate.  A2's
    question is the filter's exactness on the stream it was given.

    The cap check matters: filtering before truncation is the treatment.  If the
    filtered set ever exceeded the cap, C would drop permitted pairs, and the
    admitted set would no longer be the support restricted by the threshold.
    """
    if len(eligible) != len(admitted):
        return {"audit": "A2", "name": "oracle exactness", "passed": False,
                "applicable": True, "checks": {},
                "evidence": {"cycles_eligible": len(eligible),
                             "cycles_admitted": len(admitted)},
                "reason": "the arm's two recordings cover different cycle counts"}

    mismatches: list[dict] = []
    extra: set[tuple[str, str]] = set()
    cap_bound = 0
    pairs_checked = 0
    max_permitted = 0
    for n, (pairs, adm) in enumerate(zip(eligible, admitted)):
        expected = {p for p in pairs if p in support}
        got = set(adm)
        pairs_checked += len(expected)
        max_permitted = max(max_permitted, len(expected))
        extra.update(p for p in got if p not in support)
        if len(expected) > cap:
            cap_bound += 1
        if got != expected:
            mismatches.append({
                "cycle": n,
                "expected": len(expected),
                "admitted": len(got),
                "missing": sorted(expected - got)[:5],
                "unexpected": sorted(got - expected)[:5],
            })
            if len(mismatches) >= 5:
                break

    evidence_mismatches = 0
    if pre_cap_evidence is not None and admitted_evidence is not None:
        for before, after in zip(pre_cap_evidence, admitted_evidence):
            for pair, ev in after.items():
                if pair in before and before[pair] != ev:
                    evidence_mismatches += 1

    passed = (not mismatches and not extra and evidence_mismatches == 0
              and cap_bound == 0)
    if passed:
        reason = (f"{pairs_checked} permitted candidates across "
                  f"{len(eligible)} cycles admitted exactly; the cap never "
                  "bound after filtering")
    elif extra:
        reason = f"a non-permitted pair was admitted: {sorted(extra)[:3]}"
    elif cap_bound:
        reason = (f"the cap bound after filtering on {cap_bound} cycle(s); "
                  "permitted candidates were dropped")
    elif mismatches:
        first = mismatches[0]
        reason = (f"cycle {first['cycle']}: expected {first['expected']} "
                  f"permitted candidates, admitted {first['admitted']}")
    else:
        reason = f"{evidence_mismatches} candidates carried different evidence"
    return {"audit": "A2", "name": "oracle exactness", "passed": passed,
            "applicable": True,
            "checks": {"no_extra": not extra,
                       "no_missing": not mismatches,
                       "evidence_identical": evidence_mismatches == 0,
                       "cap_never_bound_after_filtering": cap_bound == 0},
            "evidence": {"cycles": len(eligible), "pairs_checked": pairs_checked,
                         "max_permitted_candidates": max_permitted,
                         "cap": cap,
                         "cap_bound_cycles": cap_bound,
                         "mismatch_count": len(mismatches),
                         "evidence_mismatches": evidence_mismatches,
                         "first_mismatches": mismatches[:3]},
            "reason": reason}


def audit_temporal_input(
        b_graphs: list[dict[str, dict[str, int]]],
        b_eligible: list[list[tuple[str, str]]],
        b_evidence: list[dict[tuple[str, str], dict]],
        followers: dict[str, dict[str, Any]],
        engine_own_table_symdiff: int | None = None) -> dict[str, Any]:
    """A8 — the admission arms read arm B's temporal graph, every cycle.

    Amendment 1 fixes Layer 1's temporal basis at the unfiltered arm's: B is
    run first, its ``_load_temporal()`` graph is recorded at the start of each
    sleep cycle, and C and S are given that graph.  This audit checks the
    substitution at two resolutions — the graph the service actually read, and
    the eligible pair stream it built from that graph — and compares the
    engine's evidence on the pairs both arms carry.  It is a GATE: if a cycle's
    graph or stream differs, the contrast is not "same evidence, different
    admission" and the campaign stops.

    It deliberately does not require the engine's OWN ``precedes`` tables to
    agree.  C's table is still written by the engine from C's own sleep rows;
    Layer 1 no longer reads it.  Its symmetric difference is reported as a
    footnote because it is the channel the amendment exists to close.
    """
    checks: dict[str, bool] = {}
    failures: list[dict[str, Any]] = []
    evidence_mismatches = 0
    pairs_checked = 0
    graph_diff_cycles = 0
    stream_diff_cycles = 0
    cycle_counts: dict[str, int] = {}

    for label, follower in followers.items():
        graphs = follower["graphs"]
        eligible = follower["eligible"]
        follower_evidence = follower.get("evidence") or []
        cycle_counts[label] = len(graphs)
        if len(graphs) != len(b_graphs) or len(eligible) != len(b_eligible):
            checks[f"{label}_cycle_count"] = False
            checks[f"{label}_graphs_identical"] = False
            checks[f"{label}_streams_identical"] = False
            failures.append({"arm": label, "cycle": None,
                             "kind": "cycle_count",
                             "graphs_b": len(b_graphs), "graphs_arm": len(graphs),
                             "eligible_b": len(b_eligible),
                             "eligible_arm": len(eligible)})
            continue
        graph_diffs = 0
        stream_diffs = 0
        for n, (b_graph, arm_graph, b_set, arm_set) in enumerate(
                zip(b_graphs, graphs, b_eligible, eligible)):
            b_pairs = {(u, v) for u, targets in b_graph.items() for v in targets}
            arm_pairs = {(u, v) for u, targets in arm_graph.items() for v in targets}
            if b_graph != arm_graph:
                graph_diffs += 1
                if len(failures) < 8:
                    failures.append({
                        "arm": label, "cycle": n + 1, "kind": "temporal_graph",
                        "edges_b": len(b_pairs), "edges_arm": len(arm_pairs),
                        "symmetric_difference": len(b_pairs ^ arm_pairs)})
            if set(b_set) != set(arm_set):
                stream_diffs += 1
                if len(failures) < 8:
                    failures.append({
                        "arm": label, "cycle": n + 1, "kind": "eligible_stream",
                        "b": len(set(b_set)), "arm_value": len(set(arm_set)),
                        "missing": len(set(b_set) - set(arm_set)),
                        "extra": len(set(arm_set) - set(b_set))})
            pairs_checked += len(set(b_set))
            if n < len(follower_evidence):
                for pair in set(b_evidence[n]) & set(follower_evidence[n]):
                    if b_evidence[n][pair] != follower_evidence[n][pair]:
                        evidence_mismatches += 1
                        if len(failures) < 8:
                            failures.append({"arm": label, "cycle": n + 1,
                                             "kind": "evidence", "pair": pair})
        checks[f"{label}_cycle_count"] = True
        checks[f"{label}_graphs_identical"] = graph_diffs == 0
        checks[f"{label}_streams_identical"] = stream_diffs == 0
        graph_diff_cycles += graph_diffs
        stream_diff_cycles += stream_diffs
    checks["evidence_identical_on_shared_pairs"] = evidence_mismatches == 0
    passed = all(checks.values())

    if passed:
        reason = (f"B and the admission arms read the same temporal graph at "
                  f"every cycle ({len(b_graphs)} cycles per arm, "
                  f"{pairs_checked} eligible-pair checks); evidence identical "
                  "on the shared pairs.")
        if engine_own_table_symdiff is not None:
            reason += (f" The engine's own precedes tables still differ by "
                       f"{engine_own_table_symdiff} edge(s); Layer 1 no longer "
                       "reads them.")
    else:
        first = failures[0] if failures else {}
        reason = (f"an admission arm did not read B's temporal input: first "
                  f"failure {first.get('kind')} on {first.get('arm')} at cycle "
                  f"{first.get('cycle')}; {graph_diff_cycles} graph and "
                  f"{stream_diff_cycles} stream cycle(s) differ across "
                  f"{len(followers)} arm(s).")
    return {"audit": "A8", "name": "temporal input invariance",
            "passed": passed, "applicable": True, "checks": checks,
            "evidence": {"cycles": len(b_graphs),
                         "cycles_per_arm": cycle_counts,
                         "eligible_pair_checks": pairs_checked,
                         "graph_edges_b_final_cycle": sum(
                             len(t) for t in b_graphs[-1].values()) if b_graphs else 0,
                         "engine_own_table_symmetric_difference":
                             engine_own_table_symdiff,
                         "evidence_mismatches": evidence_mismatches,
                         "first_failures": failures[:5]},
            "reason": reason}


def audit_precision_premise(precision_b_layer1: float | None,
                            layer1_precision_c_support: float | None,
                            ceiling: float = PRECISION_CEILING,
                            tol: float = PRECISION_TOL,
                            band_applies: bool = True) -> dict[str, Any]:
    """A3: B's Layer-1 precision stays in the measured band; C's is exact.

    Both quantities are Layer-1 quantities, because that is the layer the
    oracle controls and the basis on which 0.3443 was measured.  The readout's
    all-structure precision is reported elsewhere and is NOT 1.0 for C.

    ``band_applies`` is False on a world where the band has no provenance.  The
    0.3443 ceiling was measured on the compositional world (T2); T1 is the
    calibration/control task and has no committed band, so its precision is
    reported and the band is not applied.  Applying a T2 constant to T1 would
    be the wrong-metric defect AGENTS rule 23(a) records.
    """
    if not band_applies:
        return {"audit": "A3", "name": "precision premise", "passed": None,
                "applicable": False,
                "checks": {"C_admission_exact": layer1_precision_c_support == 1.0},
                "evidence": {"precision_b_layer1_world": precision_b_layer1,
                             "layer1_precision_c_support":
                                 layer1_precision_c_support,
                             "committed_band": None},
                "reason": ("the 0.3443 ceiling was measured on T2; this world "
                           "has no committed band, so precision is reported "
                           f"(B {precision_b_layer1}) and not gated")}
    checks = {
        "B_within_band": (precision_b_layer1 is not None
                          and precision_b_layer1 <= ceiling + tol),
        "C_admission_exact": layer1_precision_c_support == 1.0,
    }
    passed = all(checks.values())
    if passed:
        reason = (f"B Layer-1 precision {precision_b_layer1:.4f} <= "
                  f"{ceiling + tol:.4f}; C's admission precision is 1.0")
    elif layer1_precision_c_support is None:
        reason = "C admitted no Layer-1 predictions; precision is not measurable"
    elif precision_b_layer1 is None:
        reason = "B asserted no Layer-1 predictions; precision is not measurable"
    elif not checks["B_within_band"]:
        reason = (f"B Layer-1 precision {precision_b_layer1:.4f} left the "
                  f"measured band (<= {ceiling + tol:.4f}); the premise changed")
    else:
        reason = f"C's admitted precision is {layer1_precision_c_support}, not 1.0"
    return {"audit": "A3", "name": "precision premise", "passed": passed,
            "applicable": True, "checks": checks,
            "evidence": {"precision_b_layer1_world": precision_b_layer1,
                         "layer1_precision_c_support": layer1_precision_c_support,
                         "band_upper": round(ceiling + tol, 4)},
            "reason": reason}


def audit_denominators(limb_counts: dict[str, dict[str, int]]) -> dict[str, Any]:
    """A4: every limb must have something to score against."""
    empty = [name for name, c in limb_counts.items() if c["events"] < 1 or c["cells"] < 1]
    passed = not empty
    reason = ("every limb has a non-zero denominator"
              if passed else f"empty limb(s): {', '.join(empty)} — not measurable")
    return {"audit": "A4", "name": "denominators", "passed": passed,
            "applicable": True,
            "checks": {name: c["events"] >= 1 and c["cells"] >= 1
                       for name, c in limb_counts.items()},
            "evidence": limb_counts, "reason": reason}


def audit_readout_construct(readout_factory: Callable = make_organica_backoff
                            ) -> dict[str, Any]:
    """A5: on a synthetic world with a known answer, the readout recovers it.

    The synthetic alpha is 1.0, not the study's 256.0: this audits the CONSTRUCT
    (does evidence move the prediction toward the observed answer), which is a
    different question from the calibrated smoothing the study uses.
    """
    rows = {"amber": {"birch": 40.0}}
    base = {"amber": 1 / 3, "birch": 1 / 3, "cedar": 1 / 3}
    vocab = {"amber", "birch", "cedar"}
    ctx = [["amber"]]
    truth = [["birch"]]
    wrong = [["cedar"]]
    try:
        prob = readout_factory(rows, base, SYNTHETIC_ALPHA)
        p_true = prob("amber", "birch")
        p_other = prob("amber", "cedar")
        base_prob = lambda u, v: base.get(v, 0.0)  # noqa: E731
        ll_true = house_score(prob, ctx, truth, vocab)["log_loss"]
        ll_wrong = house_score(prob, ctx, wrong, vocab)["log_loss"]
        ll_base = house_score(base_prob, ctx, truth, vocab)["log_loss"]
    except Exception as exc:  # a readout that cannot be called has failed
        return {"audit": "A5", "name": "readout matches construct",
                "passed": False, "applicable": True, "checks": {},
                "evidence": {"error": repr(exc)},
                "reason": f"the readout raised {exc!r}"}
    checks = {
        "ranks_true_target_above_distractor": p_true > p_other,
        "beats_base_rate_on_the_true_answer": ll_true < ll_base,
        "is_worse_than_base_rate_on_a_wrong_answer": ll_wrong > ll_base,
    }
    passed = all(checks.values())
    reason = ("the readout recovers the known answer and can be wrong"
              if passed else
              "the readout does not recover the known answer: "
              + ", ".join(k for k, ok in checks.items() if not ok))
    return {"audit": "A5", "name": "readout matches construct",
            "passed": passed, "applicable": True, "checks": checks,
            "evidence": {"p_true_target": round(p_true, 6),
                         "p_distractor": round(p_other, 6),
                         "log_loss_true": ll_true,
                         "log_loss_wrong_answer": ll_wrong,
                         "log_loss_base_rate": ll_base,
                         "synthetic_alpha": SYNTHETIC_ALPHA},
            "reason": reason}


def audit_no_leakage(shuffled: dict, c: dict, shuffle_meta: dict,
                     coverage_gate: float = COVERAGE_GATE,
                     ceiling: float = PRECISION_CEILING,
                     tol: float = PRECISION_TOL,
                     score_tol: float = A6_SCORE_TOL) -> dict[str, Any]:
    """A6: a wrong filter of the same shape must not reproduce C's advantage."""
    if shuffle_meta["retained_permitted"] > 0:
        return {"audit": "A6", "name": "no leakage", "passed": None,
                "applicable": False,
                "checks": {},
                "evidence": shuffle_meta,
                "reason": ("the shuffled filter retains "
                           f"{shuffle_meta['retained_permitted']} of "
                           f"{shuffle_meta['support_size']} permitted pairs, so a "
                           "size-matched wrong filter does not exist on this "
                           "world; the control cannot discriminate and is not gated")}
    c_ll = c["scores"]["transfer"]["house_shape"]["log_loss"]
    s_ll = shuffled["scores"]["transfer"]["house_shape"]["log_loss"]
    # Layer-1 quantities: the filter controls Layer 1 only, so a shuffle that
    # leaves Layer-1 coverage intact is leakage no matter what the other layers
    # (which the filter never touches) contribute to the all-structure figure.
    checks = {
        "shuffled_precision_in_B_band": (shuffled["layer1_precision_world"]
                                          is not None
                                          and shuffled["layer1_precision_world"]
                                          <= ceiling + tol),
        "shuffled_coverage_below_gate": shuffled["layer1_coverage"] < coverage_gate,
        "shuffled_not_as_good_as_C": s_ll >= c_ll - score_tol,
    }
    passed = all(checks.values())
    if passed:
        reason = (f"shuffling collapsed Layer-1 coverage to "
                  f"{shuffled['layer1_coverage']:.4f} and Layer-1 precision to "
                  f"{shuffled['layer1_precision_world']}; transfer "
                  f"{s_ll:.4f} vs C's {c_ll:.4f}")
    else:
        failing = [k for k, ok in checks.items() if not ok]
        reason = "the oracle's content is not doing the work: " + ", ".join(failing)
    return {"audit": "A6", "name": "no leakage", "passed": passed,
            "applicable": True, "checks": checks,
            "evidence": {"shuffled": shuffle_meta,
                         "shuffled_layer1_coverage": shuffled["layer1_coverage"],
                         "shuffled_layer1_precision": (
                             shuffled["layer1_precision_world"]),
                         "shuffled_readout_precision": shuffled["readout_precision"],
                         "shuffled_transfer": s_ll,
                         "c_transfer": c_ll,
                         "score_tolerance": score_tol},
            "reason": reason}


def audit_attribution(per_type: dict[str, dict],
                      minimum: float = ATTRIBUTION_MIN) -> dict[str, Any]:
    """A7: the oracle-controlled layer must carry most of the readout's weight."""
    weights = {t: float(v.get("edge_weight", 0.0)) for t, v in per_type.items()}
    total = sum(weights.values())
    if total <= 0:
        return {"audit": "A7", "name": "attribution share", "passed": False,
                "applicable": True, "checks": {},
                "evidence": {"weights": weights},
                "reason": "the readout has no evidence at all"}
    controlled = weights.get("prediction_candidate", 0.0)
    share = controlled / total
    hypothesis = weights.get("hypothesis", 0.0) / total
    passed = share >= minimum
    reason = (f"Layer 1 carries {share:.4f} of the readout's edge weight "
              f"(hypotheses {hypothesis:.4f}); threshold {minimum:.2f}")
    return {"audit": "A7", "name": "attribution share", "passed": passed,
            "applicable": True,
            "checks": {"controlled_share_at_or_above_minimum": passed},
            "evidence": {"total_edge_weight": round(total, 3),
                         "controlled_weight": round(controlled, 3),
                         "control_share": round(share, 4),
                         "hypothesis_share": round(hypothesis, 4),
                         "per_type_weight": {t: round(w, 3)
                                             for t, w in sorted(weights.items())},
                         "minimum": minimum},
            "reason": reason}


# ---------------------------------------------------------------------------
# Analysis (§7) — implemented, but never called on a single seed
# ---------------------------------------------------------------------------

def paired_bootstrap(deltas: list[float], alpha: float = DECISION_ALPHA,
                     reps: int = BOOTSTRAP_REPS,
                     seed: int = BOOTSTRAP_SEED) -> dict[str, Any]:
    """Percentile bootstrap over seeds, paired by seed.

    ``deltas`` are oriented so POSITIVE favours the arm:
    ``baseline_log_loss - arm_log_loss``.  A win is a lower bound above zero.
    """
    if len(deltas) < 2:
        raise ValueError(
            "a verdict needs at least two seeds; one seed is a draw, not a test")
    rng = random.Random(seed)
    m = len(deltas)
    mean = sum(deltas) / m
    means = sorted(sum(deltas[rng.randrange(m)] for _ in range(m)) / m
                   for _ in range(reps))
    lo_idx = int((1 - alpha) / 2 * reps)
    hi_idx = min(reps - 1, int((1 + alpha) / 2 * reps))
    return {"mean": round(mean, 6), "lo": round(means[lo_idx], 6),
            "hi": round(means[hi_idx], 6), "n": m, "reps": reps,
            "interval": f"{alpha:.4f}"}


def verdict_of(lo: float, hi: float) -> str:
    if lo > 0:
        return "win"
    if hi < 0:
        return "loss"
    return "tie"


def map_outcome(b_verdict: str, c_verdict: str) -> dict[str, str]:
    """The four-cell mapping of §7, in exactly one of four labels."""
    if c_verdict == "win" and b_verdict == "win":
        return {"label": "utilization works; precision does not bind",
                "target": "use / abstraction"}
    if c_verdict == "win":
        return {"label": "correct structure suffices; the defect is selection",
                "target": "candidate selection / precision"}
    if b_verdict == "win":
        return {"label": "invalid: C loses while B wins",
                "target": "report A2 or A7, not the score"}
    return {"label": "utilization fails with correct structure",
            "target": "the use path (retrieval / activation / readout)"}


def analyse(records: list[dict]) -> dict[str, Any]:
    """Per task, per arm, per limb: paired difference against the frozen bar."""
    by_cell: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for r in records:
        for arm in ("A", "B", "C"):
            entry = r["arms"][arm]
            for limb in LIMBS:
                bar = r["bar"][limb]
                baseline_ll = r["comparators"][bar["member"]][limb]["house_shape"]["log_loss"]
                arm_ll = entry["scores"][limb]["house_shape"]["log_loss"]
                by_cell[(r["task"], arm, limb)].append(baseline_ll - arm_ll)

    out: dict[str, Any] = {"tasks": {}}
    for task in sorted({r["task"] for r in records}):
        cells = {}
        for arm in ("A", "B", "C"):
            cells[arm] = {}
            for limb in LIMBS:
                deltas = by_cell.get((task, arm, limb), [])
                if len(deltas) < 2:
                    cells[arm][limb] = {"verdict": "not measurable",
                                        "reason": "fewer than two seeds",
                                        "n": len(deltas)}
                    continue
                bs = paired_bootstrap(deltas)
                cells[arm][limb] = {**bs, "verdict": verdict_of(bs["lo"], bs["hi"])}
        b_transfer = cells["B"]["transfer"]["verdict"]
        c_transfer = cells["C"]["transfer"]["verdict"]
        if b_transfer == "not measurable" or c_transfer == "not measurable":
            # A cell without two seeds has no verdict; mapping it into the
            # "utilization fails" branch would turn an unmeasured quantity into
            # a negative result (AGENTS rule 13b).
            mapping = {"label": "not measurable",
                       "target": "none — fewer than two seeds per cell"}
            summary_claim = "not measurable"
        else:
            mapping = map_outcome(b_transfer, c_transfer)
            summary_claim = "not supported"
            if c_transfer in ("win", "tie"):
                if (cells["C"]["retention"].get("verdict") != "loss"
                        and cells["C"]["revision"].get("verdict") != "loss"):
                    summary_claim = "utilization works"
        out["tasks"][task] = {
            "cells": cells,
            "mapping": mapping,
            "summary_claim": summary_claim,
            "note": ("a summary claim requires C to win or tie on transfer AND "
                     "not lose on retention or revision"),
        }
    return out


# ---------------------------------------------------------------------------
# One seed, one task: four runs and eight audits
# ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def calibration_bar(task: str) -> dict[str, Any]:
    """Pick the comparator that is best per limb on the calibration seed.

    Each comparator's configuration is frozen (a declared grid was swept on
    this seed once, and the results are committed in
    ``docs/acquisition_baseline_calibration.json``).  What is chosen here is
    WHICH comparator is the bar for each limb — chosen on calibration data,
    never on a scoring window or a confirmatory seed.
    """
    prep = prepare_world(task, CALIBRATION_SEED)
    funcs = comparator_functions(prep)
    scores = {name: evaluate_limbs(p, prep) for name, p in funcs.items()}
    bar = {}
    for limb in LIMBS:
        member = min(scores, key=lambda n: scores[n][limb]["house_shape"]["log_loss"])
        bar[limb] = {"member": member,
                     "calibration_log_loss": scores[member][limb]["house_shape"]["log_loss"]}
    return {"task": task, "seed": CALIBRATION_SEED, "bar": bar,
            "calibration_scores": scores}


def comparator_functions(prep: dict) -> dict[str, Callable[[str, str], float]]:
    return {
        "replay": fit_replay_learner(prep["rows"], prep["vocab"], **REPLAY_CFG),
        "bigram": fit_bigram(prep["rows"], prep["vocab"], *STAT_CFG),
        "cell_counter": fit_cell_counter(prep["rows"], prep["vocab"],
                                         prep["tag_to_latent"], *STAT_CFG),
    }


def run_task_seed(task: str, seed: int) -> dict[str, Any]:
    prep = prepare_world(task, seed)
    support = build_support(task, prep["world"], 0)
    support_new = build_support(task, prep["world"], 1)
    if support != support_new:
        raise AssertionError(
            f"{task} seed {seed}: the generator's support differs between "
            "regimes; one frozen filter cannot serve the revision limb")
    missing = prep["world_edges"] - support
    if missing:
        raise AssertionError(
            f"{task} seed {seed}: {len(missing)} observed training edge(s) are "
            f"outside the generator's support, e.g. {sorted(missing)[:3]}")
    prep["support"] = support
    shuffled, shuffle_meta = shuffled_support(support, seed)

    t_comp = time.perf_counter()
    comparators = comparator_functions(prep)
    comparator_scores = {name: evaluate_limbs(p, prep)
                         for name, p in comparators.items()}
    comparator_seconds = round(time.perf_counter() - t_comp, 3)

    arms: dict[str, dict[str, Any]] = {}
    for label, cap, admission in (("A", CAP_A, None), ("B", CAP_B, None)):
        arms[label] = run_arm(prep, label, cap, admission)
        print(f"[{task} seed {seed}] arm {label}: "
              f"coverage {arms[label]['coverage']:.4f}, "
              f"{arms[label]['seconds_total']:.1f}s", flush=True)

    # Amendment 1: B is run first and its graph is recorded at the start of
    # every sleep cycle; the admission arms read it instead of their own.
    b_graphs = arms["B"]["_raw"]["temporal_reads"]
    for label, admission in (("C", support), ("S", shuffled)):
        arms[label] = run_arm(prep, label, CAP_B, admission,
                              fixed_temporal=b_graphs)
        print(f"[{task} seed {seed}] arm {label}: "
              f"coverage {arms[label]['coverage']:.4f}, "
              f"{arms[label]['seconds_total']:.1f}s", flush=True)

    engine_own_symdiff = len(arms["B"]["_raw"]["temporal_pairs"]
                             ^ arms["C"]["_raw"]["temporal_pairs"])
    audits = {
        "A1": audit_arm_differential({k: arms[k]["coverage"] for k in "ABC"}),
        "A2": audit_oracle_exactness(arms["C"]["_raw"]["eligible"],
                                     arms["C"]["_raw"]["admitted"], support,
                                     CAP_B,
                                     arms["C"]["_raw"]["pre_cap_evidence"],
                                     arms["C"]["_raw"]["admitted_evidence"]),
        "A3": audit_precision_premise(arms["B"]["layer1_precision_world"],
                                      arms["C"]["layer1_precision_support"],
                                      band_applies=(task == TASK_T2)),
        "A4": audit_denominators(prep["limb_counts"]),
        "A5": audit_readout_construct(),
        "A6": audit_no_leakage(arms["S"], arms["C"], shuffle_meta),
        "A7": audit_attribution(arms["C"]["per_type"]),
        "A8": audit_temporal_input(
            b_graphs,
            arms["B"]["_raw"]["eligible"],
            arms["B"]["_raw"]["pre_cap_evidence"],
            {label: {"graphs": arms[label]["_raw"]["temporal_reads"],
                     "eligible": arms[label]["_raw"]["eligible"],
                     "evidence": arms[label]["_raw"]["pre_cap_evidence"]}
             for label in ("C", "S")},
            engine_own_symdiff),
    }

    bar = calibration_bar(task)["bar"]
    for arm in arms.values():
        arm.pop("_raw")

    failing = [k for k, a in audits.items() if a.get("passed") is False]
    campaign_ready = not failing
    if failing:
        ready_reason = ("an audit failed: " + ", ".join(failing)
                        + "; the campaign stops and reports not measurable")
    else:
        ready_reason = ("all eight audits pass or are not applicable, and the "
                        "admission arms read arm B's temporal graph at every cycle")

    return {
        "task": task,
        "seed": seed,
        "support_size": len(support),
        "support_regime_invariant": True,
        "world_edges": len(prep["world_edges"]),
        "world_edges_in_support": len(prep["world_edges"] & support),
        "regime_switch_cycle": prep["regime_switch_cycle"],
        "shuffle": shuffle_meta,
        "arms": arms,
        "comparators": comparator_scores,
        "bar": bar,
        "audits": audits,
        "campaign_ready": campaign_ready,
        "campaign_ready_reason": ready_reason,
        "timings": {
            "prepare": prep["prepare_seconds"],
            "comparators": comparator_seconds,
            "arms": {k: arms[k]["seconds_total"] for k in arms},
        },
        "limb_counts": prep["limb_counts"],
    }


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _audit_rows(result: dict) -> dict[str, dict]:
    return result["audits"]


def _status_text(a: dict) -> str:
    if a.get("passed") is None:
        return "not applicable"
    return "PASS" if a["passed"] else "FAIL"


def render_timing_markdown(artifact: dict) -> str:
    task_names = list(artifact["tasks"])
    lines: list[str] = []
    lines.append("# Formation versus utilization — one-seed timing pass")
    lines.append("")
    lines.append(f"**Generated:** {artifact['generated_utc']}  ")
    lines.append(f"**Engine:** Organica {artifact['engine_version']}  ")
    lines.append(f"**Command:** `{artifact['command']}`  ")
    lines.append(f"**Status:** timing pass only — one exploratory seed "
                 f"(`{artifact['seed']}`). No campaign result, no win/tie/loss, "
                 "no verdict.  ")
    readiness = ("READY" if artifact["campaign_ready"]
                 else "NOT AUTHORISED by this pass")
    readiness_reason = artifact["campaign_ready_reasons"][task_names[0]]
    readiness_reason = readiness_reason[:1].upper() + readiness_reason[1:]
    lines.append(f"**Campaign readiness:** {readiness}. {readiness_reason}")
    lines.append("")
    lines.append("This artifact exists to report the measured cost of the "
                 "pre-registered campaign before it starts, and to record that "
                 "the eight audits behave. It is not "
                 "`docs/formation_utilization.json`; only a full campaign may "
                 "write that. Arms C and S read arm B's per-cycle temporal "
                 "graph (Amendment 1, protocol §12); A and B are unchanged.")
    lines.append("")

    lines.append("## 1. Measured cost")
    lines.append("")
    lines.append("| Task | Arm | Cap | Admission | Acquisition (s) | Revision learn (s) "
                 "| Scoring (s) | Total (s) |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for task, r in artifact["tasks"].items():
        for label in ("A", "B", "C", "S"):
            arm = r["arms"][label]
            s = arm["seconds"]
            lines.append(
                f"| {task} | {label} | {arm['cap']} | {arm['admission']} "
                f"| {s['acquisition']:.1f} | {s['revision_learning']:.1f} "
                f"| {s['scoring'] + s['revision_scoring']:.1f} "
                f"| {arm['seconds_total']:.1f} |")
    lines.append("")
    proj = artifact["projection"]
    lines.append(f"Mean engine run: **{proj['mean_arm_seconds']:.1f} s** over "
                 f"{proj['runs_measured']} measured runs. Arm C's filter adds no "
                 "measurable cost (the filter is a set membership test over at "
                 "most a few hundred candidate pairs per cycle).")
    lines.append("")
    lines.append(f"- Campaign arms (A, B, C × 2 tasks × {proj['seeds']} seeds = "
                 f"{proj['campaign_arm_runs']} runs): **{proj['campaign_arm_hours']:.1f} h** "
                 "sequential.")
    lines.append(f"- A6's shuffled arm (2 tasks × {proj['seeds']} seeds = "
                 f"{proj['audit_arm_runs']} runs): "
                 f"**{proj['audit_arm_hours']:.1f} h** sequential.")
    lines.append(f"- Comparators (2 tasks × {proj['seeds']} seeds = "
                 f"{proj['comparator_runs']} fits): "
                 f"**{proj['comparator_hours']:.2f} h** sequential.")
    lines.append(f"- **Total sequential: {proj['total_hours']:.1f} h.** Each "
                 "task-seed unit is independent, so `--workers` divides this "
                 "without changing any per-run measurement.")
    lines.append("")
    lines.append("The projection is arithmetic on the measured runs, not a "
                 "second measurement. It excludes A2's recording, which is "
                 "in-memory and was on for every run above.")
    lines.append("")

    task_names = list(artifact["tasks"])
    lines.append("## 2. The audits")
    lines.append("")
    header = " | ".join(task_names)
    lines.append(f"| Audit | {header} | Evidence ({task_names[0]}) |")
    lines.append("|---" * (len(task_names) + 2) + "|")
    for key in ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"):
        cells = [_status_text(artifact["tasks"][t]["audits"][key])
                 for t in task_names]
        evidence = artifact["tasks"][task_names[0]]["audits"][key]["reason"]
        cells_text = " | ".join(cells)
        lines.append(f"| {key} {artifact['tasks'][task_names[0]]['audits'][key]['name']} "
                     f"| {cells_text} | {evidence} |")
    lines.append("")
    failing = [(t, k) for t, r in artifact["tasks"].items()
               for k, a in r["audits"].items() if a.get("passed") is False]
    if failing:
        names = ", ".join(f"{k} on {t}" for t, k in failing)
        lines.append(f"**AUDIT FAILED: {names}.** The campaign is stopped and "
                     "reports not measurable. No gate is relaxed.")
    else:
        lines.append("No audit failed. A6 is marked not applicable where the "
                     "shuffled filter necessarily retains permitted pairs; the "
                     "retained share is in its evidence. A6 is gated on the "
                     "primary task T2, where the shuffle retains none.")
    lines.append("")

    lines.append("## 3. Audit A8 — temporal input invariance (gate)")
    lines.append("")
    for task in task_names:
        a8 = artifact["tasks"][task]["audits"]["A8"]
        lines.append(f"- **{task}:** {_status_text(a8)}. {a8['reason']}")
    lines.append("")
    lines.append("A8 checks the graph each admission arm actually read and the "
                 "eligible pair stream it built from that graph, every cycle. "
                 "It is a gate, and it replaces the pre-amendment diagnostic "
                 "D1, whose measurement is preserved at "
                 "`docs/formation_utilization_timing_pre_amendment.json`. The "
                 "engine's own `precedes` tables still differ — C's own sleep "
                 "rows are still recorded — but Layer 1 no longer reads them.")
    lines.append("")

    lines.append("## 4. Scores (descriptive — not a result)")
    lines.append("")
    lines.append("| Task | Arm | Retention | Transfer | Revision |")
    lines.append("|---|---|---|---|---|")
    for task, r in artifact["tasks"].items():
        for label in ("A", "B", "C", "S"):
            sc = r["arms"][label]["scores"]
            lines.append(
                f"| {task} | {label} "
                f"| {sc['retention']['house_shape']['log_loss']:.4f} "
                f"| {sc['transfer']['house_shape']['log_loss']:.4f} "
                f"| {sc['revision']['house_shape']['log_loss']:.4f} |")
        bar = r["bar"]
        lines.append(
            f"| {task} | bar "
            f"| {r['comparators'][bar['retention']['member']]['retention']['house_shape']['log_loss']:.4f} "
            f"| {r['comparators'][bar['transfer']['member']]['transfer']['house_shape']['log_loss']:.4f} "
            f"| {r['comparators'][bar['revision']['member']]['revision']['house_shape']['log_loss']:.4f} |")
    lines.append("")
    gaps = []
    c_is_best: list[bool] = []
    for task in task_names:
        r = artifact["tasks"][task]
        for limb in LIMBS:
            bar_member = r["bar"][limb]["member"]
            c_ll = r["arms"]["C"]["scores"][limb]["house_shape"]["log_loss"]
            bar_ll = r["comparators"][bar_member][limb]["house_shape"]["log_loss"]
            gaps.append((task, limb, c_ll, bar_ll, c_ll - bar_ll))
            others = [r["arms"][k]["scores"][limb]["house_shape"]["log_loss"]
                      for k in ("A", "B", "S")]
            c_is_best.append(c_ll <= min(others) + 1e-12)
    cleared = [g for g in gaps if g[4] <= 0]
    worse = [g for g in gaps if g[4] > 0]
    transfer = [g for g in gaps if g[1] == "transfer"]
    cleared_text = ("none" if not cleared else
                    ", ".join(f"{g[0]} {g[1]}" for g in cleared))
    transfer_text = " and ".join(f"{g[4]:+.4f} nats on {g[0]}" for g in transfer)
    lead = ("**Where the oracle arm sits.** On this seed arm C is the best "
            "Organica arm on every limb"
            if all(c_is_best) else
            "**Where the oracle arm sits.** On this seed arm C is not the best "
            "Organica arm on every limb")
    if worse:
        lines.append(lead + f", and it clears the bar on {len(cleared)} of "
                     f"{len(gaps)} task-limbs ({cleared_text}). Its difference "
                     f"from the bar on the primary transfer limb (positive = "
                     f"worse) is {transfer_text}. One seed is not a verdict and "
                     "these numbers may not be quoted as a loss; they are "
                     "recorded because an oracle-admitted arm that does not "
                     "clear a counting baseline on its own timing seed is a "
                     "warning the campaign should carry.")
    else:
        lines.append(lead + f", and it clears the bar on all {len(gaps)} "
                     "task-limbs. One seed is not a verdict and these numbers "
                     "may not be quoted as a win.")
    lines.append("")
    lines.append("The bar row names the comparator selected per limb on the "
                 "calibration seed. One seed cannot produce a verdict: the "
                 "decision rule needs a paired bootstrap over seeds, and "
                 "`analyse()` refuses to run below two. Nothing in this table "
                 "may be quoted as a win, a loss or a tie.")
    lines.append("")
    lines.append("A1's coverage is the Gate 13 quantity over the world edges "
                 "derived from the training stream, on the all-structure basis "
                 "the gate pins. A3's precision is the Layer-1 quantity on which "
                 "the 0.3443 ceiling was measured. Arm C's all-structure readout "
                 "precision is reported in the artifact and is not 1.0, because "
                 "the readout still aggregates all six structure types; only its "
                 "Layer-1 admission is exact.")
    lines.append("")

    lines.append("## 5. Disclosures")
    lines.append("")
    for d in artifact["disclosures"]:
        lines.append(f"**{d['id']}.** {d['text']}")
        lines.append("")
    lines.append("## 6. Provenance")
    lines.append("")
    lines.append(f"- Artifact: `{TIMING_OUT}`; this file is rendered from it.")
    lines.append(f"- Seed `{artifact['seed']}` is the exploratory seed Gate 13 "
                 "already spent; it is not one of the 30 confirmatory seeds.")
    if "T1" in artifact["tasks"]:
        lines.append(f"- T1 was generated with a regime switch at cycle "
                     f"`{artifact['tasks']['T1']['regime_switch_cycle']}`, "
                     "matching the limb table; the generator's own default is 150.")
    lines.append("- The pre-amendment timing artifact is preserved as "
                 "`docs/formation_utilization_timing_pre_amendment.json`; its "
                 "C and S cells are not a result of the amended design.")
    if artifact.get("provenance_note"):
        lines.append(f"- {artifact['provenance_note']}")
    return _assert_no_placeholder("\n".join(lines) + "\n")


def _assert_no_placeholder(md: str) -> str:
    if re.search(r"\{[A-Za-z_]", md):
        raise AssertionError(
            "generated markdown contains an unsubstituted placeholder")
    return md


def render_campaign_markdown(artifact: dict) -> str:
    lines = ["# Formation versus utilization — campaign", ""]
    lines.append(f"**Generated:** {artifact['generated_utc']}  ")
    lines.append(f"**Status:** {artifact['status']}")
    lines.append("")
    if artifact["status"] != "complete":
        lines.append("The campaign stopped at an audit and reports **not "
                     "measurable**. The audits are named below; no score is "
                     "reported and no gate was relaxed.")
        lines.append("")
        lines.append(artifact["audits"]["reason"])
        lines.append("")
        for f in artifact["audits"]["failing"][:20]:
            lines.append(f"- audit **{f['audit']}** failed on **{f['task']}** "
                         f"seed `{f['seed']}`")
        return _assert_no_placeholder("\n".join(lines) + "\n")

    for task, res in artifact["analysis"]["tasks"].items():
        lines.append(f"## {task}")
        lines.append("")
        lines.append("| Arm | Limb | Mean difference | 98.33% interval | Verdict |")
        lines.append("|---|---|---|---|---|")
        for arm in ("A", "B", "C"):
            for limb in LIMBS:
                cell = res["cells"][arm][limb]
                if "lo" not in cell:
                    lines.append(f"| {arm} | {limb} | — | — | not measurable |")
                else:
                    lines.append(f"| {arm} | {limb} | {cell['mean']:+.4f} "
                                 f"| [{cell['lo']:+.4f}, {cell['hi']:+.4f}] "
                                 f"| {cell['verdict']} |")
        lines.append("")
        lines.append(f"**Mapping:** {res['mapping']['label']} → target "
                     f"`{res['mapping']['target']}`. Summary claim: "
                     f"**{res['summary_claim']}**.")
        lines.append("")
    return _assert_no_placeholder("\n".join(lines) + "\n")


def _projection(results: list[dict], seeds: int) -> dict[str, Any]:
    totals = [r["timings"]["arms"][k] for r in results for k in ("A", "B", "C", "S")]
    mean_arm = statistics.mean(totals) if totals else 0.0
    comp = statistics.mean(r["timings"]["comparators"] for r in results) if results else 0.0
    campaign_runs = 3 * 2 * seeds
    audit_runs = 2 * seeds
    comparator_runs = 2 * seeds
    return {
        "runs_measured": len(totals),
        "mean_arm_seconds": round(mean_arm, 3),
        "mean_comparator_seconds": round(comp, 3),
        "seeds": seeds,
        "campaign_arm_runs": campaign_runs,
        "campaign_arm_hours": round(campaign_runs * mean_arm / 3600, 2),
        "audit_arm_runs": audit_runs,
        "audit_arm_hours": round(audit_runs * mean_arm / 3600, 2),
        "comparator_runs": comparator_runs,
        "comparator_hours": round(comparator_runs * comp / 3600, 3),
        "total_hours": round((campaign_runs * mean_arm
                              + audit_runs * mean_arm
                              + comparator_runs * comp) / 3600, 2),
    }


DISCLOSURES = [
    {"id": "A6 wording superseded",
     "text": ("The committed audit asked that shuffling the oracle make C "
              "\"collapse to B's coverage\". B's coverage is 98–100 %, so no "
              "shuffle can produce that value: the direction is impossible. "
              "A6 is implemented as shuffled precision in B's measured band, "
              "shuffled coverage under A1's own 0.50 gate, and the shuffled "
              "transfer score not matching C's. The thresholds are the "
              "protocol's own; none was relaxed.")},
    {"id": "three limbs, not four",
     "text": ("§3.4 says four scored windows; §4.4 lists revision 200–249 and a "
              "held-out 250–299; the pinned runner scores three limbs. Three is "
              "what §7's Bonferroni-over-three assumes. This harness scores "
              "retention 110–149, transfer 150–199 and revision 250–299, and "
              "treats 200–249 as the learning window it is.")},
    {"id": "T1's regime switch",
     "text": ("The T1 generator defaults to a law change at cycle 150, which "
              "would put the change inside the transfer window §4.4 says is "
              "under the old law. The harness generates T1 with a switch at 200 "
              "and verifies the recorded regime at the boundary. The module "
              "default and §4.4 disagree.")},
    {"id": "A6 on T1 is not a control",
     "text": ("T1's support covers 12 of 16 targets per source, so a "
              "size-matched wrong filter necessarily retains permitted pairs "
              "(the retained share is printed). A6 is therefore gated on the "
              "primary task T2 and reported as not applicable on T1. A control "
              "that cannot discriminate is not a passed control.")},
    {"id": "bar selection",
     "text": ("The comparators' configurations are frozen from the calibration "
              "artifact; only WHICH comparator is the bar per limb is chosen, "
              "on seed 20261099. Three comparators are fitted (replay, bigram, "
              "cell counter) rather than the protocol's two, which can only "
              "raise the bar.")},
    {"id": "A2's scope",
     "text": ("A2 is the committed audit on the arm's own stream: admitted = "
              "count-threshold-eligible pairs intersected with the support. A "
              "stronger C-versus-B comparison was implemented first and failed; "
              "it was reported as diagnostic D1 before Amendment 1 and is now "
              "audit A8, which gates the run. The comparison is retained because "
              "it measures whether the admission arms read the same evidence, "
              "which is the condition the amendment exists to establish.")},
    {"id": "amendment 1 — fixed temporal evidence",
     "text": ("The pre-amendment timing pass measured that an admission filter "
              "changed the next cycle's temporal graph: the engine's lookback "
              "window is the last three rows of `events`, and sleep rows are "
              "rows. Arms C and S now read arm B's per-cycle graph, recorded at "
              "the start of each sleep cycle, instead of their own; A and B are "
              "unchanged. This closes the feedback path into Layer 1 but does "
              "not make the engine sleep-blind: B's graph still contains B's "
              "own sleep rows, and C's own payload and prior still differ (that "
              "is the treatment). C is therefore a counterfactual trajectory on "
              "B's evidence, and a C result is admission filtering at fixed "
              "temporal evidence, not 'the engine with this filter installed'. "
              "See protocol §12 and the preserved pre-amendment artifact.")},
    {"id": "A3's band is T2's",
     "text": ("The 0.3443 precision ceiling was measured on the compositional "
              "world. A3 applies it on T2 and reports T1's precision without "
              "gating, because T1 has no committed band. Applying a T2 constant "
              "to T1 would measure the wrong population.")},
    {"id": "orientation of the decision difference",
     "text": ("§7 writes d = score(arm) − score(baseline) and calls a positive "
              "lower bound a win. With log-loss, lower is better, so the "
              "orientation that makes the rule coherent is "
              "d = baseline log-loss − arm log-loss. That is the quantity "
              "bootstrapped, and it is named in every artifact.")},
]


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------

def timing_pass(seed: int = TIMING_SEED, tasks: tuple[str, ...] = TASKS,
                command: str = "") -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()
    results = {}
    for task in tasks:
        t0 = time.perf_counter()
        results[task] = run_task_seed(task, seed)
        results[task]["wall_seconds"] = round(time.perf_counter() - t0, 3)
    artifact = {
        "kind": "timing",
        "seed": seed,
        "generated_utc": started,
        "engine_version": ENGINE_VERSION,
        "command": command,
        "constants": {
            "alpha": ALPHA,
            "cap_A": CAP_A,
            "cap_B": CAP_B,
            "coverage_gate": COVERAGE_GATE,
            "precision_ceiling": PRECISION_CEILING,
            "precision_tolerance": PRECISION_TOL,
            "attribution_minimum": ATTRIBUTION_MIN,
            "a6_score_tolerance": A6_SCORE_TOL,
            "decision_alpha": DECISION_ALPHA,
            "bootstrap_reps": BOOTSTRAP_REPS,
            "calibration_seed": CALIBRATION_SEED,
            "regime_switch_cycle": T1_REGIME_CYCLES,
        },
        "tasks": results,
        "projection": _projection(list(results.values()), CAMPAIGN_SEED_COUNT),
        "disclosures": DISCLOSURES,
    }
    failing = [(task, key) for task, r in results.items()
               for key, a in r["audits"].items() if a.get("passed") is False]
    artifact["audits_passed"] = not failing
    artifact["audits_failing"] = [f"{k} on {t}" for t, k in failing]
    artifact["campaign_ready"] = all(r["campaign_ready"]
                                     for r in results.values())
    artifact["campaign_ready_reasons"] = {
        task: r["campaign_ready_reason"] for task, r in results.items()}
    return artifact


def campaign_pass(seed_count: int = CAMPAIGN_SEED_COUNT,
                  workers: int = 1, command: str = "") -> dict[str, Any]:
    seeds = list(range(CAMPAIGN_SEED_START, CAMPAIGN_SEED_START + seed_count))
    units = [(task, seed) for task in TASKS for seed in seeds]
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(_run_unit, units))
    else:
        results = [_run_unit(unit) for unit in units]

    artifact: dict[str, Any] = {
        "kind": "campaign",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "engine_version": ENGINE_VERSION,
        "command": command,
        "seeds": seeds,
        "results": results,
    }
    failing = [(r["task"], r["seed"], key)
               for r in results for key, a in r["audits"].items()
               if a.get("passed") is False]
    if failing:
        artifact["status"] = "not measurable"
        artifact["audits"] = {
            "failing": [{"task": t, "seed": s, "audit": k} for t, s, k in failing],
            "reason": ("an audit failed; the campaign stops and reports not "
                       "measurable, never a zero and never a relaxed gate"),
        }
        return artifact
    artifact["status"] = "complete"
    artifact["audits"] = {
        "all_passed": True,
        "note": ("A6 entries with passed=null are not applicable on that world "
                 "and are excluded from the gate; the campaign's gate is T2."),
        "not_applicable": [{"task": r["task"], "seed": r["seed"], "audit": key}
                           for r in results
                           for key, a in r["audits"].items()
                           if a.get("passed") is None],
    }
    artifact["analysis"] = analyse(results)
    return artifact


def _run_unit(unit: tuple[str, int]) -> dict[str, Any]:
    return run_task_seed(*unit)


def _write_json(path: str, payload: dict) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--timing", action="store_true",
                      help="one-seed timing pass (default)")
    mode.add_argument("--campaign", action="store_true",
                      help="the full pre-registered campaign")
    parser.add_argument("--seed", type=int, default=TIMING_SEED)
    parser.add_argument("--tasks", nargs="+", default=list(TASKS),
                        choices=list(TASKS))
    parser.add_argument("--seeds", type=int, default=CAMPAIGN_SEED_COUNT)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--out", default=None)
    parser.add_argument("--md-out", default=None)
    args = parser.parse_args(argv)

    command = "python " + " ".join(["benchmarks/formation_utilization.py"]
                                   + (argv if argv is not None else sys.argv[1:]))

    if args.campaign:
        artifact = campaign_pass(args.seeds, args.workers, command)
        _write_json(args.out or CAMPAIGN_OUT, artifact)
        md = render_campaign_markdown(artifact)
        md_path = Path(args.md_out or CAMPAIGN_MD)
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(md, encoding="utf-8")
        print(f"campaign status: {artifact['status']}")
        if artifact["status"] == "complete":
            for task, res in artifact["analysis"]["tasks"].items():
                print(f"{task}: B transfer {res['cells']['B']['transfer']['verdict']}, "
                      f"C transfer {res['cells']['C']['transfer']['verdict']} -> "
                      f"{res['mapping']['label']}")
        else:
            for f in artifact["audits"]["failing"][:5]:
                print(f"  audit {f['audit']} failed on {f['task']} seed {f['seed']}")
        print(f"wrote {args.out or CAMPAIGN_OUT} and {args.md_out or CAMPAIGN_MD}")
        return 0

    artifact = timing_pass(args.seed, tuple(args.tasks), command)
    _write_json(args.out or TIMING_OUT, artifact)
    md = render_timing_markdown(artifact)
    md_path = Path(args.md_out or TIMING_MD)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(md, encoding="utf-8")

    for task, r in artifact["tasks"].items():
        print(f"[{task}] seed {r['seed']}  wall {r['wall_seconds']:.1f}s  "
              f"support {r['support_size']}  world edges {r['world_edges']}")
        for label in ("A", "B", "C", "S"):
            arm = r["arms"][label]
            print(f"    {label}: cap {arm['cap']:>5}  "
                  f"coverage {arm['coverage']:.4f}  "
                  f"L1 {arm['layer1_coverage']:.4f}  "
                  f"L1 precision {arm['layer1_precision_world']}  "
                  f"transfer {arm['scores']['transfer']['house_shape']['log_loss']:.4f}  "
                  f"({arm['seconds_total']:.1f}s)")
        for key in ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"):
            a = r["audits"][key]
            print(f"    {key} {_status_text(a):<14} {a['reason']}")
    print(f"projection: {artifact['projection']}")
    print(f"wrote {args.out or TIMING_OUT} and {args.md_out or TIMING_MD}")
    return 0 if artifact["audits_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
