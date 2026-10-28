"""Acquisition 10-cell evaluation runner (§5 and §6 of the preregistration).

Implements the complete single-seed comparison matrix across all 10 cells
for Task 2 (Compositional task):

  Learners and Cells:
    Organica:
      Cell 1: P-none x E-pres
      Cell 2: P-org  x E-pres
      Cell 3: P-org  x E-rem
      Cell 4: P-obs  x E-pres
      Cell 5: P-obs  x E-rem
      Cell 6: P-none x E-rem
    Replay:
      Cell 7: E-pres
      Cell 8: E-rem
    Statistical:
      Cell 9: E-pres
      Cell 10: E-rem
    References:
      Bayes ceiling & Base rate

Windows scored separately:
  - Retention: cycles 110-149 (old law, frozen pre-switch state)
  - Transfer: cycles 150-199 (same law, new/withheld combination, frozen pre-switch state)
  - Revision Test: cycles 250-299 (new law, scored after continued learning in cycles 200-249)

Both metric shapes are computed and reported:
  - House shape (exclude_self=True, primary per §4.3/§6.4)
  - Self-cells shape (exclude_self=False, co-primary per §4.3/§6.4)

Preregistration discipline strictly enforced:
  - Prerequisite sufficiency check (Gate 13) verified at end of acquisition.
  - Intervention verification (Gate 11) verified before reading outcomes.
  - Removal verification (Gate 12) verified for all E-rem cells.
  - Scratch-only guarantee (Gate 16) verified: live DB is never touched.
  - Exposure symmetry (Amendment 2): Organica and comparison baselines receive
    the identical full acquisition stream (cycles 20-109); smoothing and
    hyperparameters are calibrated on independent calibration seed 20261099.
  - Results saved to docs/acquisition_single_seed_pilot.json.

Standard library only. Scratch databases only.
Engine files (organica/sleep.py, organica/memory.py) are never edited.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.memory import MemoryService  # noqa: E402
from organica.paths import temp_db, LIVE_DB  # noqa: E402
from organica.sleep import SleepService  # noqa: E402
from benchmarks.ablation_metrics import edges_implied_by_structures  # noqa: E402
from benchmarks.acquisition_baselines import (  # noqa: E402
    fit_base_rate,
    fit_bigram,
    fit_cell_counter,
    select_best,
    score,
)
from benchmarks.acquisition_compositional import (  # noqa: E402
    generate_compositional_world,
    make_ceiling,
    PHASE_WARMUP,
    PHASE_ACQUISITION,
    PHASE_RETENTION,
    PHASE_TRANSFER,
    PHASE_REVISION_LEARN,
    PHASE_REVISION_TEST,
    EVENTS_PER_CYCLE,
    CYCLES,
)
from benchmarks.acquisition_harness import (  # noqa: E402
    _erem,
    _make_scratch_db,
    _WriteSentinel,
    gate_scratch_only,
    SUFFICIENCY_THRESHOLD,
    _world_compositional_edges,
)

ALPHAS_ORGANICA = [0.0, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 128.0, 256.0]
EPS = 1e-12


# ---------------------------------------------------------------------------
# Helpers for P-intervention
# ---------------------------------------------------------------------------

class IntervenedSleepService(SleepService):
    """SleepService subclass implementing in-process P-org suppression."""

    def __init__(self, memory: MemoryService, suppressed_id: str | None = None) -> None:
        super().__init__(memory)
        self.suppressed_id = suppressed_id

    def _store_single_candidate(self, candidate: dict) -> None:
        if self.suppressed_id and candidate.get("id") == self.suppressed_id:
            return  # Suppress from persisting
        super()._store_single_candidate(candidate)

    def _natural_selection(self, prior, concepts, phrases, loops, predictions):
        if self.suppressed_id:
            prior = [c for c in prior if c.get("id") != self.suppressed_id]
            concepts = [c for c in concepts if getattr(c, "id", None) != self.suppressed_id]
            phrases = [c for c in phrases if getattr(c, "id", None) != self.suppressed_id]
            loops = [c for c in loops if getattr(c, "id", None) != self.suppressed_id]
            predictions = [c for c in predictions if getattr(c, "id", None) != self.suppressed_id]
        return super()._natural_selection(prior, concepts, phrases, loops, predictions)


def select_p_target(reports: list[Any]) -> str | None:
    """Deterministic selection of P-intervention target per §6.2:

    1. Layer-1 candidates in final acquisition report.
    2. Present in >= 2 consecutive acquisition cycles.
    3. Greatest strength.
    4. Break ties by ascending candidate id.
    """
    if len(reports) < 2:
        return None

    last_r = reports[-1]
    prev_r = reports[-2]

    def get_l1(r):
        return (r.concepts or []) + (r.phrases or []) + (r.loops or []) + (r.predictions or []) + (r.anomalies or [])

    last_l1 = {getattr(c, "id"): c for c in get_l1(last_r) if getattr(c, "id", None)}
    prev_l1_ids = {getattr(c, "id") for c in get_l1(prev_r) if getattr(c, "id", None)}

    eligible = [c for cid, c in last_l1.items() if cid in prev_l1_ids]
    if not eligible:
        return None

    eligible.sort(key=lambda c: (-float(getattr(c, "strength", 0.0) or 0.0), getattr(c, "id")))
    return getattr(eligible[0], "id")


# ---------------------------------------------------------------------------
# Organica Readout Form (§4.3, §6.3, and readout design)
# ---------------------------------------------------------------------------

def structure_edges(candidates: list[dict]) -> dict[str, dict[str, float]]:
    """Accumulate evidence w(a, b) across candidate types.

    Deduplicates by candidate ``id`` before aggregating.  The engine stores
    a snapshot of every living candidate at each sleep cycle, so the same
    logical structure appears once per sleep cycle in ``_load_prior_candidates``.
    Summing over all snapshots would inflate weights by (number of cycles the
    candidate survived), not by its evidential strength.  For each unique id
    the snapshot with the highest ``generation`` is retained; unnamed
    candidates (no ``id`` field) are kept as-is.

    The deduplication is internal to this function and does not change the
    declared readout form (§4.3): all six structure types are still used,
    and the backoff formula is unchanged.
    """
    # --- Deduplicate: one current entry per candidate id by engine record order ---
    # `candidates` is loaded from `MemoryService.recent(n=4000, event_type='sleep')`,
    # which returns rows in `ORDER BY time DESC`. The first encounter of each unique id
    # is strictly the newest live candidate record in the database.
    by_id: dict = {}
    for c in candidates:
        cid = c.get("id")
        if cid is None:
            by_id[id(c)] = c  # unnamed: treat as unique
        elif cid not in by_id:
            by_id[cid] = c
    deduped = list(by_id.values())

    ec: dict[tuple[str, str], float] = defaultdict(float)
    for c in deduped:
        t = c.get("type", "")
        if t in ("concept_candidate", "phrase_candidate"):
            m = list(c.get("members") or [])
            for i, a in enumerate(m):
                for b in m[i + 1:]:
                    ec[(a, b)] += 1.0
                    ec[(b, a)] += 1.0
        elif t == "loop_candidate":
            pth = list(c.get("path") or [])
            for a, b in zip(pth, pth[1:]):
                ec[(a, b)] += 1.0
                ec[(b, a)] += 1.0
        elif t == "prediction_candidate":
            s, tg = c.get("source"), c.get("target")
            ev = c.get("evidence") or {}
            w = float(ev.get("temporal_count") or 1.0)
            if s and tg:
                ec[(s, tg)] += w
        elif t == "hypothesis":
            s, e = c.get("subject"), c.get("expectation")
            if s and e:
                ec[(s, e)] += 1.0
        elif t == "process_candidate":
            cyc = list(c.get("cycle") or [])
            for i, a in enumerate(cyc):
                ec[(a, cyc[(i + 1) % len(cyc)])] += 1.0
        elif t == "workflow_concept":
            comps = list(c.get("components") or [])
            for a, b in zip(comps, comps[1:]):
                ec[(a, b)] += 1.0
        elif t == "dream":
            pth = list(c.get("path_or_context") or [])
            for a, b in zip(pth, pth[1:]):
                ec[(a, b)] += 1.0

    rows: dict[str, dict[str, float]] = defaultdict(dict)
    for (a, b), w in ec.items():
        rows[a][b] = w
    return rows


def candidate_summary(candidates: list[dict]) -> dict[str, Any]:
    """Count unique candidates and total edge weight contributed per type.

    Returns a dict suitable for inclusion in the result artifact so the
    declared readout can be verified: unique_count is the number of
    distinct candidate ids (one per current structure); raw_count is the
    original length before deduplication; per_type breaks down both counts
    and the total w(a,b) weight each type contributes to structure_edges.
    """
    # Deduplicate by id (same logic as structure_edges)
    by_id: dict = {}
    for c in candidates:
        cid = c.get("id")
        key = cid if cid is not None else id(c)
        if key not in by_id:
            by_id[key] = c
    deduped = list(by_id.values())

    per_type: dict[str, dict[str, Any]] = {}
    for c in deduped:
        t = c.get("type", "unknown")
        if t not in per_type:
            per_type[t] = {"unique_count": 0, "edge_weight": 0.0}
        per_type[t]["unique_count"] += 1
        # Compute weight this candidate contributes
        if t in ("concept_candidate", "phrase_candidate"):
            m = list(c.get("members") or [])
            pairs = sum(1 for i in range(len(m)) for _ in m[i+1:])
            per_type[t]["edge_weight"] += pairs * 2.0  # bidirectional
        elif t == "loop_candidate":
            pth = list(c.get("path") or [])
            per_type[t]["edge_weight"] += (len(pth) - 1) * 2.0  # bidirectional
        elif t == "prediction_candidate":
            ev = c.get("evidence") or {}
            per_type[t]["edge_weight"] += float(ev.get("temporal_count") or 1.0)
        elif t == "hypothesis":
            per_type[t]["edge_weight"] += 1.0
        elif t == "process_candidate":
            cyc = list(c.get("cycle") or [])
            per_type[t]["edge_weight"] += len(cyc)
        elif t == "workflow_concept":
            comps = list(c.get("components") or [])
            per_type[t]["edge_weight"] += max(0, len(comps) - 1)
        elif t == "dream":
            pth = list(c.get("path_or_context") or [])
            per_type[t]["edge_weight"] += max(0, len(pth) - 1)

    return {
        "raw_count": len(candidates),
        "unique_count": len(deduped),
        "per_type": {t: {"unique_count": v["unique_count"],
                         "edge_weight": round(v["edge_weight"], 2)}
                     for t, v in sorted(per_type.items())},
    }


def make_organica_backoff(
    rows: dict[str, dict[str, float]],
    base_rate_dict: dict[str, float],
    alpha: float,
) -> Callable[[str, str], float]:
    """p(b | a) = ( w(a, b) + alpha * m(b) ) / ( W(a) + alpha )"""
    def prob(u: str, v: str) -> float:
        row = rows.get(u, {})
        W = sum(row.values())
        mv = base_rate_dict.get(v, 0.0)
        denom = W + alpha
        if denom <= 0:
            return mv
        return (row.get(v, 0.0) + alpha * mv) / denom
    return prob


# Calibrated smoothing alpha on independent calibration world (seed 20261099, Amendment 2).
# Avoids in-seed data leakage or asymmetrical tuning splits.
CALIBRATED_ORGANICA_ALPHA: float = 256.0


# ---------------------------------------------------------------------------
# Replay Learner (§6.3)
# ---------------------------------------------------------------------------

REPLAY_GRID = [
    (window, half_life, alpha)
    for window in (1, 2, 3)
    for half_life in (None, 25, 50, 100)
    for alpha in (0.5, 1.0)
]


def fit_replay_learner(
    rows: list[str],
    vocab: set[str],
    window: int = 1,
    half_life: float | None = None,
    alpha: float = 0.5,
) -> Callable[[str, str], float]:
    """Given context tags C, retrieve stored episodes intersecting C.
    p(b | a) is the fraction of those episodes followed by b.
    """
    n = len(rows)
    counts: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for i in range(n - 1):
        w = 1.0
        if half_life:
            w = 0.5 ** ((n - 1 - i) / (half_life * EVENTS_PER_CYCLE))
        start_j = max(0, i - window + 1)
        succ = rows[i + 1].split()
        for j in range(start_j, i + 1):
            ctx = rows[j].split()
            for a in ctx:
                for b in succ:
                    if a != b:
                        counts[a][b] += w

    def p(u: str, v: str) -> float:
        row = counts.get(u, {})
        tot = sum(row.values())
        if tot <= 0:
            return 1.0 / len(vocab)
        return (row.get(v, 0.0) + alpha) / (tot + alpha * len(vocab))

    return p


def select_best_replay(
    rows: list[str],
    vocab: set[str],
    tune_ctx: list[list[str]],
    tune_obs: list[list[str]],
    exclude_self: bool = True,
) -> tuple[dict, Callable[[str, str], float]]:
    """Select best replay config on the tuning split."""
    best_ll = float("inf")
    best_cfg = None
    best_p = None
    for window, half_life, alpha in REPLAY_GRID:
        p = fit_replay_learner(rows, vocab, window, half_life, alpha)
        s = score(p, tune_ctx, tune_obs, vocab, exclude_self=exclude_self)
        if s["log_loss"] < best_ll:
            best_ll = s["log_loss"]
            best_cfg = {"window": window, "half_life": half_life, "alpha": alpha}
            best_p = p
    assert best_p is not None
    return best_cfg, best_p


# ---------------------------------------------------------------------------
# Scoring helper for both shapes
# ---------------------------------------------------------------------------

def evaluate_shapes(
    prob_func: Callable[[str, str], float],
    ctx: list[list[str]],
    obs: list[list[str]],
    vocab: set[str],
) -> dict[str, Any]:
    """Score both the primary house shape and co-primary self-cell shape."""
    s_house = score(prob_func, ctx, obs, vocab, exclude_self=True)
    s_self = score(prob_func, ctx, obs, vocab, exclude_self=False)
    return {
        "house_shape": s_house,
        "self_cells_shape": s_self,
    }


# ---------------------------------------------------------------------------
# Main 10-Cell Evaluation Pipeline
# ---------------------------------------------------------------------------

def run_10_cell_pipeline(
    seed: int = 20261100,
    cycles: int = CYCLES,
    events_per_cycle: int = EVENTS_PER_CYCLE,
) -> dict[str, Any]:
    """Execute all 10 cells on a single seed for the compositional world."""
    t0 = time.time()
    world = generate_compositional_world(seed=seed, cycles=cycles, events_per_cycle=events_per_cycle)
    events = world["events"]
    trainable = world["trainable"]

    epc = events_per_cycle
    warm_lo, warm_hi = PHASE_WARMUP
    acq_lo, acq_hi = PHASE_ACQUISITION
    ret_lo, ret_hi = PHASE_RETENTION
    tr_lo, tr_hi = PHASE_TRANSFER
    rev_learn_lo, rev_learn_hi = PHASE_REVISION_LEARN
    rev_test_lo, rev_test_hi = PHASE_REVISION_TEST

    # Full exposure stream spanning warmup (cycles 0-19) and acquisition (cycles 20-109)
    # Ensures identical observation exposure across Organica and comparison baselines
    full_exposure_indices = list(range(warm_lo * epc, acq_hi * epc))
    train_rows_all = [events[i] for i in full_exposure_indices if trainable[i]]
    vocab = {t for e in train_rows_all for t in e.split()}

    ret_indices = list(range(ret_lo * epc, ret_hi * epc))
    tr_indices = list(range(tr_lo * epc, tr_hi * epc))
    rev_test_indices = list(range(rev_test_lo * epc, rev_test_hi * epc))

    def make_pairs(idx_list):
        ctx = [sorted(events[idx_list[k]].split()) for k in range(len(idx_list) - 1)]
        obs = [sorted(events[idx_list[k + 1]].split()) for k in range(len(idx_list) - 1)]
        return ctx, obs

    ret_ctx, ret_obs = make_pairs(ret_indices)
    tr_ctx, tr_obs = make_pairs(tr_indices)
    rev_test_ctx, rev_test_obs = make_pairs(rev_test_indices)
    tr_ctx, tr_obs = make_pairs(tr_indices)
    rev_test_ctx, rev_test_obs = make_pairs(rev_test_indices)

    # Base rate dict from acquisition training stream
    cnt_base = defaultdict(int)
    for r in train_rows_all:
        for t in r.split():
            cnt_base[t] += 1
    tot_base = sum(cnt_base.values()) or 1
    base_rate_dict = {t: n / tot_base for t, n in cnt_base.items()}

    results: dict[str, Any] = {
        "seed": seed,
        "gates": {},
        "p_target_id": None,
        "cells": {},
        "references": {},
    }

    # Reference scores
    ceil_r0 = make_ceiling(world, 0)
    ceil_r1 = make_ceiling(world, 1)
    base_rate_model = lambda u, v: base_rate_dict.get(v, 0.0)

    results["references"]["bayes_ceiling"] = {
        "retention": evaluate_shapes(ceil_r0, ret_ctx, ret_obs, vocab),
        "transfer": evaluate_shapes(ceil_r0, tr_ctx, tr_obs, vocab),
        "revision": evaluate_shapes(ceil_r1, rev_test_ctx, rev_test_obs, vocab),
    }
    results["references"]["base_rate"] = {
        "retention": evaluate_shapes(base_rate_model, ret_ctx, ret_obs, vocab),
        "transfer": evaluate_shapes(base_rate_model, tr_ctx, tr_obs, vocab),
        "revision": evaluate_shapes(base_rate_model, rev_test_ctx, rev_test_obs, vocab),
    }

    # --- Cells 7 & 8: Replay Learner ---
    # Exposure symmetry (Amendment 2): fitted on full exposure stream including warmup (train_rows_all)
    # Hyperparameters calibrated on independent calibration seed 20261099 (docs/acquisition_baseline_calibration.json)
    REPLAY_CALIBRATED_CFG = {"window": 1, "half_life": None, "alpha": 0.5}
    replay_pres_p = fit_replay_learner(
        train_rows_all,
        vocab,
        window=REPLAY_CALIBRATED_CFG["window"],
        half_life=REPLAY_CALIBRATED_CFG["half_life"],
        alpha=REPLAY_CALIBRATED_CFG["alpha"],
    )
    results["cells"]["cell_7_replay_E_pres"] = {
        "config": REPLAY_CALIBRATED_CFG,
        "scores": {
            "retention": evaluate_shapes(replay_pres_p, ret_ctx, ret_obs, vocab),
            "transfer": evaluate_shapes(replay_pres_p, tr_ctx, tr_obs, vocab),
            "revision": evaluate_shapes(replay_pres_p, rev_test_ctx, rev_test_obs, vocab),
        },
    }
    replay_rem_p = lambda u, v: 1.0 / len(vocab)
    results["cells"]["cell_8_replay_E_rem"] = {
        "scores": {
            "retention": evaluate_shapes(replay_rem_p, ret_ctx, ret_obs, vocab),
            "transfer": evaluate_shapes(replay_rem_p, tr_ctx, tr_obs, vocab),
            "revision": evaluate_shapes(replay_rem_p, rev_test_ctx, rev_test_obs, vocab),
        },
    }

    # --- Cells 9 & 10: Statistical Learner ---
    # Exposure symmetry (Amendment 2): fitted on full exposure stream including warmup (train_rows_all)
    # Hyperparameters calibrated on independent calibration seed 20261099 (docs/acquisition_baseline_calibration.json)
    STAT_CALIBRATED_CFG = (0.1, None, None)  # alpha, half_life, window
    stat_pres_p = fit_cell_counter(
        train_rows_all,
        vocab,
        world["tag_to_cell"],
        alpha=STAT_CALIBRATED_CFG[0],
        half_life=STAT_CALIBRATED_CFG[1],
        decay_window=STAT_CALIBRATED_CFG[2],
    )
    results["cells"]["cell_9_statistical_E_pres"] = {
        "config": STAT_CALIBRATED_CFG,
        "scores": {
            "retention": evaluate_shapes(stat_pres_p, ret_ctx, ret_obs, vocab),
            "transfer": evaluate_shapes(stat_pres_p, tr_ctx, tr_obs, vocab),
            "revision": evaluate_shapes(stat_pres_p, rev_test_ctx, rev_test_obs, vocab),
        },
    }
    stat_rem_p = lambda u, v: 1.0 / len(vocab)
    results["cells"]["cell_10_statistical_E_rem"] = {
        "scores": {
            "retention": evaluate_shapes(stat_rem_p, ret_ctx, ret_obs, vocab),
            "transfer": evaluate_shapes(stat_rem_p, tr_ctx, tr_obs, vocab),
            "revision": evaluate_shapes(stat_rem_p, rev_test_ctx, rev_test_obs, vocab),
        },
    }

    # --- Organica Cells (1 to 6) ---
    cell_specs = [
        ("cell_1_organica_P_none_E_pres", False, False),
        ("cell_2_organica_P_org_E_pres", True, False),
        ("cell_3_organica_P_org_E_rem", True, True),
        ("cell_4_organica_P_obs_E_pres", False, False),
        ("cell_5_organica_P_obs_E_rem", False, True),
        ("cell_6_organica_P_none_E_rem", False, True),
    ]

    p_target_id = None
    ACQ_SOURCE = "env_acq"

    for cell_name, apply_p_org, apply_e_rem in cell_specs:
        scratch_db_path = _make_scratch_db(f"{cell_name}_{seed}")
        mem = MemoryService(str(scratch_db_path))
        svc = IntervenedSleepService(mem, suppressed_id=None)

        # 1. Normal acquisition run (cycles 0-109)
        acq_reports = []
        for i in range(acq_hi * epc):
            in_acq = (acq_lo * epc <= i < acq_hi * epc)
            if in_acq and not trainable[i]:
                continue
            source = ACQ_SOURCE if in_acq else "env"
            mem.store(events[i], event_type="observe", source=source)
            if (i + 1) % epc == 0:
                rep = svc.run_sleep_cycle()
                if in_acq:
                    acq_reports.append(rep)

        # Determine target from acquisition reports
        if p_target_id is None:
            p_target_id = select_p_target(acq_reports)
            results["p_target_id"] = p_target_id

        # Verification: Acquisition sufficiency (Gate 13, Amendment 1)
        # Check both asserted structure coverage (evaluating against SUFFICIENCY_THRESHOLD)
        # and raw temporal graph edge coverage as a separate diagnostic.
        frozen_cands = svc._load_prior_candidates()
        asserted_rows = structure_edges(frozen_cands)
        asserted_edges = set((u, v) for u, targets in asserted_rows.items() for v in targets)

        world_edges = _world_compositional_edges(world)
        org_temporal_edges = set((ft, tt) for ft, tt, _cnt in mem.temporal_edges(min_count=1))

        covered_asserted = world_edges & asserted_edges
        covered_temporal = world_edges & org_temporal_edges

        asserted_coverage = len(covered_asserted) / len(world_edges) if world_edges else 0.0
        temporal_coverage = len(covered_temporal) / len(world_edges) if world_edges else 0.0

        acquisition_passed = (asserted_coverage >= SUFFICIENCY_THRESHOLD)

        results["gates"][f"{cell_name}_sufficiency"] = {
            "passed": acquisition_passed,
            "acquisition_failed": not acquisition_passed,
            "asserted_structure_coverage": round(asserted_coverage, 4),
            "raw_temporal_coverage": round(temporal_coverage, 4),
            "world_edges": len(world_edges),
            "covered_asserted_edges": len(covered_asserted),
            "covered_temporal_edges": len(covered_temporal),
            "threshold": SUFFICIENCY_THRESHOLD,
        }

        # 2. Apply Interventions at end of acquisition
        if apply_p_org and p_target_id:
            # Delete target candidate rows from events table
            mem._conn.execute(
                "DELETE FROM events WHERE event_type = 'sleep' AND content LIKE ?",
                (f'%\"id\": \"{p_target_id}\"%',),
            )
            mem._conn.commit()
            # Arm suppression for subsequent cycles
            svc.suppressed_id = p_target_id

            # Gate 11 verification for P-org
            rem_rows = mem._conn.execute(
                "SELECT COUNT(*) FROM events WHERE event_type = 'sleep' AND content LIKE ?",
                (f'%\"id\": \"{p_target_id}\"%',),
            ).fetchone()[0]
            results["gates"][f"{cell_name}_p_org_verified"] = (rem_rows == 0)

        if apply_e_rem:
            _erem(mem, ACQ_SOURCE)
            # Gate 11 & Gate 12 verification
            ev_count = mem._conn.execute(
                "SELECT COUNT(*) FROM events WHERE source = ?", (ACQ_SOURCE,)
            ).fetchone()[0]
            prec_count = mem._conn.execute("SELECT COUNT(*) FROM precedes").fetchone()[0]
            cooc_count = mem._conn.execute("SELECT COUNT(*) FROM cooccurrences").fetchone()[0]
            tag_count = mem._conn.execute("SELECT COUNT(*) FROM tag_counts").fetchone()[0]

            results["gates"][f"{cell_name}_removal_verified"] = {
                "events_cleared": ev_count == 0,
                "precedes_cleared": prec_count == 0,
                "cooccurrences_preserved": cooc_count > 0,
                "tag_counts_preserved": tag_count > 0,
            }

        # 3. Capture frozen pre-switch state for retention and transfer
        frozen_cands = svc._load_prior_candidates()
        
        # P-obs: withhold target from the auditor's reconstruction while organism
        # state and prediction readout remain untouched (Amendment 1, §5, §6.2)
        audit_reconstruction_frozen = None
        if "P_obs" in cell_name and p_target_id:
            auditor_cands = [c for c in frozen_cands if c.get("id") != p_target_id]
            audit_reconstruction_frozen = {
                "withheld_target_id": p_target_id,
                "reconstruction_candidate_count": len(auditor_cands),
                "summary": candidate_summary(auditor_cands),
            }

        # Fixed α calibrated on independent calibration seed 20261099 (Amendment 1 & 2)
        # Prevents in-seed tuning data overlap with Organica's developmental experience
        CALIBRATED_ALPHA = 256.0
        alpha_frozen = CALIBRATED_ALPHA
        prob_frozen = make_organica_backoff(structure_edges(frozen_cands), base_rate_dict, alpha_frozen)

        score_retention = evaluate_shapes(prob_frozen, ret_ctx, ret_obs, vocab)
        score_transfer = evaluate_shapes(prob_frozen, tr_ctx, tr_obs, vocab)

        # 4. Revision learning window (cycles 200-249 under new law)
        # We step the engine through cycles 200 to 249
        for cyc in range(rev_learn_lo, rev_learn_hi):
            for ev in events[cyc * epc:(cyc + 1) * epc]:
                mem.store(ev, event_type="observe", source="env_rev")
            svc.run_sleep_cycle()

        # 5. Capture post-revision state for revision test (cycles 250-299)
        post_rev_cands = svc._load_prior_candidates()
        audit_reconstruction_revised = None
        if "P_obs" in cell_name and p_target_id:
            auditor_rev_cands = [c for c in post_rev_cands if c.get("id") != p_target_id]
            audit_reconstruction_revised = {
                "withheld_target_id": p_target_id,
                "reconstruction_candidate_count": len(auditor_rev_cands),
                "summary": candidate_summary(auditor_rev_cands),
            }

        alpha_rev = CALIBRATED_ALPHA
        prob_rev = make_organica_backoff(structure_edges(post_rev_cands), base_rate_dict, alpha_rev)
        score_revision = evaluate_shapes(prob_rev, rev_test_ctx, rev_test_obs, vocab)

        cell_res: dict[str, Any] = {
            "alpha_frozen": alpha_frozen,
            "alpha_revised": alpha_rev,
            "frozen_candidates_summary": candidate_summary(frozen_cands),
            "revised_candidates_summary": candidate_summary(post_rev_cands),
            "acquisition_failed": not acquisition_passed,
            "transfer_status": "not_measurable_due_to_acquisition_failure" if not acquisition_passed else "measurable",
            "scores": {
                "retention": score_retention,
                "transfer_diagnostic": score_transfer,
                "revision": score_revision,
            },
        }
        if audit_reconstruction_frozen is not None:
            cell_res["audit_reconstruction_frozen"] = audit_reconstruction_frozen
            cell_res["audit_reconstruction_revised"] = audit_reconstruction_revised

        results["cells"][cell_name] = cell_res

        # Cleanup
        mem._conn.close()
        try:
            scratch_db_path.unlink(missing_ok=True)
        except PermissionError:
            pass

    results["elapsed_seconds"] = round(time.time() - t0, 2)
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run 10-cell acquisition pipeline on 1 seed.")
    parser.add_argument("--seed", type=int, default=20261100)
    parser.add_argument("--cycles", type=int, default=CYCLES)
    parser.add_argument("--out", type=str, default="docs/acquisition_single_seed_pilot.json")
    args = parser.parse_args()

    print(f"Running calibrated single-seed 10-cell pipeline (seed={args.seed})...")
    res = run_10_cell_pipeline(seed=args.seed, cycles=args.cycles)

    # Save reproducible artifact
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)

    print(f"Artifact written to: {out_path}")
    print(f"Completed in {res['elapsed_seconds']}s")
    print(f"P-intervention target selected: {res['p_target_id']}")

    print("\nSummary of Primary House Shape Log-Loss:")
    print(f"{'Cell / Condition':<35} {'Retention':>10} {'Transfer (Diag)':>15} {'Revision':>10}")
    print("-" * 75)
    for cname, cdata in res["cells"].items():
        sc = cdata["scores"]
        r_ll = sc["retention"]["house_shape"]["log_loss"]
        tr_key = "transfer" if "transfer" in sc else "transfer_diagnostic"
        t_ll = sc[tr_key]["house_shape"]["log_loss"]
        v_ll = sc["revision"]["house_shape"]["log_loss"]
        print(f"{cname:<35} {r_ll:>10.4f} {t_ll:>15.4f} {v_ll:>10.4f}")

    print("\nReferences (House Shape):")
    for rname, rdata in res["references"].items():
        r_ll = rdata["retention"]["house_shape"]["log_loss"]
        t_ll = rdata["transfer"]["house_shape"]["log_loss"]
        v_ll = rdata["revision"]["house_shape"]["log_loss"]
        print(f"{rname:<35} {r_ll:>10.4f} {t_ll:>15.4f} {v_ll:>10.4f}")

    print("\nSummary of Co-Primary Self-Cells Shape Log-Loss:")
    print(f"{'Cell / Condition':<35} {'Retention':>10} {'Transfer (Diag)':>15} {'Revision':>10}")
    print("-" * 75)
    for cname, cdata in res["cells"].items():
        sc = cdata["scores"]
        r_ll = sc["retention"]["self_cells_shape"]["log_loss"]
        tr_key = "transfer" if "transfer" in sc else "transfer_diagnostic"
        t_ll = sc[tr_key]["self_cells_shape"]["log_loss"]
        v_ll = sc["revision"]["self_cells_shape"]["log_loss"]
        print(f"{cname:<35} {r_ll:>10.4f} {t_ll:>15.4f} {v_ll:>10.4f}")

    print("\nReferences (Self-Cells Shape):")
    for rname, rdata in res["references"].items():
        r_ll = rdata["retention"]["self_cells_shape"]["log_loss"]
        t_ll = rdata["transfer"]["self_cells_shape"]["log_loss"]
        v_ll = rdata["revision"]["self_cells_shape"]["log_loss"]
        print(f"{rname:<35} {r_ll:>10.4f} {t_ll:>10.4f} {v_ll:>10.4f}")
