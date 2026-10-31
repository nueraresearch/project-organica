"""Use-path diagnostic — the pre-registered decomposition after the campaign.

The protocol is ``docs/USE-PATH-DIAGNOSTIC-PREREGISTRATION.md`` (frozen by
SHA-256 in ``docs/use_path_diagnostic_freeze.json``).  This module is the
runner, the analysis and the result-document generator.

THE ORDER THAT MATTERS
----------------------
    D0 reproduction  ->  room estimate  ->  mechanism mapping

D0 must reproduce the formation-utilization campaign's arm-C scores for all
30 seeds and all three scored limbs within ``1e-4``.  It is a validity gate,
not a control: if it fails, the decomposition is operating on a different
object than the one that produced the ceiling result, and the only honest
outcome is **AUDIT REQUIRED** — no room estimate, no mechanism mapping.

The arms are observer-side re-scorings of the same asserted structure.  No
file in ``organica/`` is changed.  The engine runs are B and C only, using
the campaign's own harness; the variants are offline.

Standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from organica import __version__ as ENGINE_VERSION  # noqa: E402

from benchmarks import formation_utilization as fu  # noqa: E402
from benchmarks.acquisition_compositional import (  # noqa: E402
    EVENTS_PER_CYCLE,
    PHASE_REVISION_LEARN,
    PHASE_REVISION_TEST,
)
from benchmarks.acquisition_runner import (  # noqa: E402
    candidate_summary,
    make_organica_backoff,
    structure_edges,
)

# ---------------------------------------------------------------------------
# Frozen constants — mirrored in the protocol and the freeze record
# ---------------------------------------------------------------------------

PROTOCOL = REPO / "docs/USE-PATH-DIAGNOSTIC-PREREGISTRATION.md"
FREEZE = REPO / "docs/use_path_diagnostic_freeze.json"
CAMPAIGN = REPO / "docs/formation_utilization.json"
ARTIFACT = REPO / "docs/use_path_diagnostic.json"
RESULT_MD = REPO / "docs/USE-PATH-DIAGNOSTIC-RESULTS.md"
PARTS = REPO / ".scratch" / "use_path_diagnostic_parts"
CALIBRATION_CACHE = REPO / ".scratch" / "use_path_diagnostic_calibration.json"

TASKS = ("T2", "T1")
SEEDS = tuple(range(20261101, 20261131))
LIMBS = ("retention", "transfer", "revision")
CALIBRATION_SEED = 20261099

D0_TOLERANCE = 1e-4
EFFECT_THRESHOLD = 0.01
ROOM_THRESHOLD = 0.01
DECISION_ALPHA = fu.DECISION_ALPHA
BOOTSTRAP_REPS = fu.BOOTSTRAP_REPS
BOOTSTRAP_SEED = fu.BOOTSTRAP_SEED

D0_ALPHA = fu.ALPHA
ALPHA_GRID = (16.0, 64.0, 256.0, 1024.0)
HASH_SEED = "0"
D2_CONSTANTS = {"prediction_candidate": 1.0, "__other__": 0.5}
D4_ADD_ONE = 1.0
REGIME_BY_LIMB = {"retention": 0, "transfer": 0, "revision": 1}


class ProtocolNotFrozen(RuntimeError):
    """The protocol file no longer matches its freeze record."""


class AuditRequired(RuntimeError):
    """The D0 gate failed; no mechanism may be mapped."""


def require_hash_seed() -> str:
    """The engine is hash-order sensitive; the campaign reproduces at seed 0.

    The formation-utilization campaign's artifact was produced with
    ``PYTHONHASHSEED=0`` but did not record it.  The diagnostic's self-test
    found a 4.7e-4 drift without the pin, so the pin is a declared
    reproducibility constant, not an option.
    """
    value = os.environ.get("PYTHONHASHSEED")
    if value != HASH_SEED:
        raise RuntimeError(
            "PYTHONHASHSEED must be 0 for the diagnostic; run "
            "`PYTHONHASHSEED=0 python benchmarks/use_path_diagnostic.py ...`")
    return value


# ---------------------------------------------------------------------------
# Freeze, campaign reference, and small helpers
# ---------------------------------------------------------------------------

def _sha256(path: Path) -> str:
    """SHA-256 of the LF-normalized bytes.

    The protocol is frozen across Git's line-ending conversion: a CRLF checkout
    and an LF checkout must produce the same freeze hash.
    """
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()



def check_freeze(protocol: Path = PROTOCOL, freeze: Path = FREEZE) -> dict[str, Any]:
    """Return the freeze record only if the protocol's bytes still match it."""
    if not protocol.exists():
        raise ProtocolNotFrozen(f"protocol is missing: {protocol}")
    if not freeze.exists():
        raise ProtocolNotFrozen(f"freeze record is missing: {freeze}")
    record = json.loads(freeze.read_text(encoding="utf-8"))
    actual = _sha256(protocol)
    expected = record.get("protocol_sha256")
    if expected != actual:
        raise ProtocolNotFrozen(
            "the protocol has changed since it was frozen; "
            f"recorded {expected!r}, actual {actual!r}. "
            "Amend, disclose and re-freeze before running.")
    recorded = str(record.get("protocol", ""))
    if Path(recorded).name != protocol.name and recorded != str(protocol):
        raise ProtocolNotFrozen(
            f"the freeze record names {recorded!r}, not {str(protocol)!r}")
    return record


def load_campaign_c(path: Path = CAMPAIGN) -> dict[tuple[str, int], dict[str, float]]:
    """The campaign artifact's arm-C scores, keyed by (task, seed)."""
    if not path.exists():
        raise FileNotFoundError(f"campaign artifact is missing: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    out: dict[tuple[str, int], dict[str, float]] = {}
    for result in data.get("results", []):
        task = result.get("task")
        seed = result.get("seed")
        arm_c = (result.get("arms") or {}).get("C") or {}
        scores = arm_c.get("scores") or {}
        out[(task, seed)] = {
            limb: float(scores[limb]["house_shape"]["log_loss"])
            for limb in LIMBS if limb in scores
        }
    return out


def _iter_dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (int, float)):
        return f"{float(value):.{digits}f}"
    return str(value)


# ---------------------------------------------------------------------------
# Per-type structure — the decomposition must reconcile to structure_edges
# ---------------------------------------------------------------------------

def _dedupe_candidates(candidates: list[dict]) -> list[dict]:
    by_id: dict = {}
    for c in candidates:
        cid = c.get("id")
        key = cid if cid is not None else id(c)
        if key not in by_id:
            by_id[key] = c
    return list(by_id.values())


def candidate_edge_weights(c: dict) -> dict[tuple[str, str], float]:
    """The edge contribution of ONE candidate, exactly as structure_edges."""
    t = c.get("type", "")
    out: dict[tuple[str, str], float] = defaultdict(float)
    if t in ("concept_candidate", "phrase_candidate"):
        members = list(c.get("members") or [])
        for i, a in enumerate(members):
            for b in members[i + 1:]:
                out[(a, b)] += 1.0
                out[(b, a)] += 1.0
    elif t == "loop_candidate":
        path = list(c.get("path") or [])
        for a, b in zip(path, path[1:]):
            out[(a, b)] += 1.0
            out[(b, a)] += 1.0
    elif t == "prediction_candidate":
        source, target = c.get("source"), c.get("target")
        evidence = c.get("evidence") or {}
        weight = float(evidence.get("temporal_count") or 1.0)
        if source and target:
            out[(source, target)] += weight
    elif t == "hypothesis":
        subject, expectation = c.get("subject"), c.get("expectation")
        if subject and expectation:
            out[(subject, expectation)] += 1.0
    elif t == "process_candidate":
        cycle = list(c.get("cycle") or [])
        for i, a in enumerate(cycle):
            out[(a, cycle[(i + 1) % len(cycle)])] += 1.0
    elif t == "workflow_concept":
        components = list(c.get("components") or [])
        for a, b in zip(components, components[1:]):
            out[(a, b)] += 1.0
    elif t == "dream":
        path = list(c.get("path_or_context") or [])
        for a, b in zip(path, path[1:]):
            out[(a, b)] += 1.0
    return out


def per_type_rows(candidates: list[dict]) -> dict[str, dict[str, dict[str, float]]]:
    """Edge rows split by candidate type, with the same weights as structure_edges."""
    rows: dict[str, dict[str, dict[str, float]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(float)))
    for c in _dedupe_candidates(candidates):
        t = c.get("type", "")
        for (a, b), weight in candidate_edge_weights(c).items():
            rows[t][a][b] += weight
    return {
        t: {a: dict(targets) for a, targets in by_source.items()}
        for t, by_source in rows.items()
    }


def aggregate_type_rows(per_type: dict[str, dict[str, dict[str, float]]],
                        weight_of: Callable[[str], float]
                        ) -> dict[str, dict[str, float]]:
    rows: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for t, by_source in per_type.items():
        weight = weight_of(t)
        if weight == 0.0:
            continue
        for a, targets in by_source.items():
            for b, value in targets.items():
                rows[a][b] += weight * value
    return {a: dict(targets) for a, targets in rows.items()}


def layer1_weight(t: str) -> float:
    return 1.0 if t == "prediction_candidate" else 0.0


def d2_weight(t: str) -> float:
    """The declared D2 constants.  No score, seed or artifact can change them."""
    return D2_CONSTANTS["prediction_candidate"] if t == "prediction_candidate" \
        else D2_CONSTANTS["__other__"]


def _row_difference(a: dict[str, dict[str, float]],
                    b: dict[str, dict[str, float]]) -> float:
    """Largest absolute per-edge difference between two edge tables."""
    worst = 0.0
    for source in set(a) | set(b):
        ta = _iter_dict(a.get(source))
        tb = _iter_dict(b.get(source))
        for target in set(ta) | set(tb):
            worst = max(worst, abs(float(ta.get(target, 0.0))
                                   - float(tb.get(target, 0.0))))
    return worst


# ---------------------------------------------------------------------------
# The direct conditional — D4
# ---------------------------------------------------------------------------

def fit_direct_conditional(rows: list[str], vocab: set[str],
                           add_one: float = D4_ADD_ONE
                           ) -> Callable[[str, str], float]:
    """p(b|a) = (count(a,b) + 1) / (count(a,*) + |V|).

    A direct first-order conditional with the declared add-one constant and
    no backoff.  It is fitted on the same exposure rows the other readouts
    see; for the revision limb the caller appends the revision-learning rows
    so the form has the same access to the new law that the engine had.
    """
    counts: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for i in range(1, len(rows)):
        for a in rows[i - 1].split():
            for b in rows[i].split():
                counts[a][b] += 1.0

    def prob(u: str, v: str) -> float:
        row = counts.get(u, {})
        total = sum(row.values())
        return (row.get(v, 0.0) + add_one) / (total + add_one * len(vocab))

    return prob


# ---------------------------------------------------------------------------
# One unit: B, C, and the offline arms
# ---------------------------------------------------------------------------

def _score(prob: Callable[[str, str], float], prep: dict, limb: str
           ) -> dict[str, Any]:
    return fu.evaluate_limbs(prob, prep, (limb,))[limb]


def _log_loss(score_entry: dict[str, Any]) -> float:
    return float(score_entry["house_shape"]["log_loss"])


def run_unit(task: str, seed: int, calibrated_alpha: float | None) -> dict[str, Any]:
    """Run B and C for one (task, seed), then score D0–D5 offline."""
    require_hash_seed()
    t0 = time.perf_counter()
    prep = fu.prepare_world(task, seed)
    support = fu.build_support(task, prep["world"], 0)
    support_new = fu.build_support(task, prep["world"], 1)
    if support != support_new:
        raise AssertionError(
            f"{task} seed {seed}: the generator's support differs between regimes")
    missing = prep["world_edges"] - support
    if missing:
        raise AssertionError(
            f"{task} seed {seed}: {len(missing)} observed training edge(s) "
            "are outside the generator's support")
    prep["support"] = support

    b = fu.run_arm(prep, "B", fu.CAP_B, None)
    c = fu.run_arm(prep, "C", fu.CAP_B, support,
                   fixed_temporal=b["_raw"]["temporal_reads"])
    raw = c["_raw"]

    asserted = raw["asserted_rows"]
    post = raw["post_asserted"]
    frozen = raw["frozen_candidates"]
    post_candidates = raw["post_candidates"]

    by_type = per_type_rows(frozen)
    post_by_type = per_type_rows(post_candidates)

    full = aggregate_type_rows(by_type, lambda _t: 1.0)
    max_edge_diff = _row_difference(full, asserted)
    post_max_edge_diff = _row_difference(
        aggregate_type_rows(post_by_type, lambda _t: 1.0), post)
    attribution_ok = max_edge_diff <= 1e-6 and post_max_edge_diff <= 1e-6

    layer1 = aggregate_type_rows(by_type, layer1_weight)
    layer1_post = aggregate_type_rows(post_by_type, layer1_weight)
    weighted = aggregate_type_rows(by_type, d2_weight)
    weighted_post = aggregate_type_rows(post_by_type, d2_weight)

    base_rate = prep["base_rate"]
    d0_retention = _score(make_organica_backoff(asserted, base_rate, D0_ALPHA),
                          prep, "retention")
    d0_transfer = _score(make_organica_backoff(asserted, base_rate, D0_ALPHA),
                         prep, "transfer")
    d0_revision = _score(make_organica_backoff(post, base_rate, D0_ALPHA),
                         prep, "revision")
    d0 = {limb: _log_loss(value) for limb, value in (
        ("retention", d0_retention), ("transfer", d0_transfer),
        ("revision", d0_revision))}

    variants: dict[str, dict[str, float | None]] = {}
    for arm, rows, rows_post in (
            ("D1", layer1, layer1_post),
            ("D2", weighted, weighted_post),
            ("D3", asserted, post)):
        scores: dict[str, float | None] = {}
        alpha = calibrated_alpha if arm == "D3" else D0_ALPHA
        if arm == "D3" and alpha is None:
            scores = {limb: None for limb in LIMBS}
        else:
            scores["retention"] = _log_loss(
                _score(make_organica_backoff(rows, base_rate, alpha),
                       prep, "retention"))
            scores["transfer"] = _log_loss(
                _score(make_organica_backoff(rows, base_rate, alpha),
                       prep, "transfer"))
            scores["revision"] = _log_loss(
                _score(make_organica_backoff(rows_post, base_rate, alpha),
                       prep, "revision"))
        variants[arm] = scores

    direct = fit_direct_conditional(prep["rows"], prep["vocab"], D4_ADD_ONE)
    rev_lo, rev_hi = PHASE_REVISION_LEARN
    epc = prep["epc"]
    rows_rev = prep["rows"] + [prep["events"][i]
                               for i in range(rev_lo * epc, rev_hi * epc)]
    direct_rev = fit_direct_conditional(rows_rev, prep["vocab"], D4_ADD_ONE)
    variants["D4"] = {
        "retention": _log_loss(_score(direct, prep, "retention")),
        "transfer": _log_loss(_score(direct, prep, "transfer")),
        "revision": _log_loss(_score(direct_rev, prep, "revision")),
    }

    ceiling = {}
    for limb in LIMBS:
        regime = REGIME_BY_LIMB[limb]
        prob = fu.reference_ceiling(task, prep["world"], regime)
        ceiling[limb] = _log_loss(_score(prob, prep, limb))

    summary = candidate_summary(frozen)
    post_summary = candidate_summary(post_candidates)
    total_weight = sum(sum(targets.values()) for targets in asserted.values())
    per_type_weight = sum(
        sum(sum(targets.values()) for targets in by_source.values())
        for by_source in by_type.values())

    record = {
        "task": task,
        "seed": seed,
        "support_size": len(support),
        "world_edges": len(prep["world_edges"]),
        "d0": {limb: round(d0[limb], 6) for limb in LIMBS},
        "variants": {
            arm: {limb: (None if score is None else round(score, 6))
                  for limb, score in scores.items()}
            for arm, scores in variants.items()
        },
        "d5": {limb: round(ceiling[limb], 6) for limb in LIMBS},
        "alpha": calibrated_alpha,
        "attribution": {
            "ok": bool(attribution_ok),
            "max_edge_diff": round(max_edge_diff, 9),
            "post_max_edge_diff": round(post_max_edge_diff, 9),
            "total_weight": round(total_weight, 6),
            "per_type_weight": round(per_type_weight, 6),
        },
        "per_type": summary["per_type"],
        "post_per_type": post_summary["per_type"],
        "limb_counts": prep["limb_counts"],
        "seconds": {
            "B": b["seconds_total"],
            "C": c["seconds_total"],
            "total": round(time.perf_counter() - t0, 3),
        },
    }
    return record


def _run_unit_worker(task: str, seed: int, alpha: float | None) -> dict[str, Any]:
    return run_unit(task, seed, alpha)


# ---------------------------------------------------------------------------
# Calibration — D3 only, on 20261099
# ---------------------------------------------------------------------------

def calibrate(task: str) -> dict[str, Any]:
    """Select the D3 α on the calibration seed, on the transfer window."""
    prep = fu.prepare_world(task, CALIBRATION_SEED)
    support = fu.build_support(task, prep["world"], 0)
    prep["support"] = support
    b = fu.run_arm(prep, "B", fu.CAP_B, None)
    c = fu.run_arm(prep, "C", fu.CAP_B, support,
                   fixed_temporal=b["_raw"]["temporal_reads"])
    rows = c["_raw"]["asserted_rows"]
    grid: dict[str, dict[str, float]] = {}
    for alpha in ALPHA_GRID:
        score = _score(make_organica_backoff(rows, prep["base_rate"], alpha),
                       prep, "transfer")
        grid[str(alpha)] = {"transfer_log_loss": _log_loss(score)}
    selected = min(ALPHA_GRID,
                   key=lambda a: grid[str(a)]["transfer_log_loss"])
    return {
        "task": task,
        "seed": CALIBRATION_SEED,
        "grid": grid,
        "selected_alpha": selected,
        "selected_score": grid[str(selected)]["transfer_log_loss"],
        "note": ("selected on the calibration seed only; no confirmatory "
                 "seed takes part"),
    }


def load_or_run_calibration(force: bool = False) -> dict[str, Any]:
    require_hash_seed()
    if CALIBRATION_CACHE.exists() and not force:
        try:
            return json.loads(CALIBRATION_CACHE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    tasks = {}
    for task in TASKS:
        print(f"[calibration] {task} seed {CALIBRATION_SEED}", flush=True)
        tasks[task] = calibrate(task)
        print(f"[calibration] {task}: alpha = {tasks[task]['selected_alpha']}",
              flush=True)
    calibration = {"seed": CALIBRATION_SEED, "tasks": tasks}
    CALIBRATION_CACHE.parent.mkdir(parents=True, exist_ok=True)
    CALIBRATION_CACHE.write_text(
        json.dumps(calibration, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    return calibration


# ---------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------

def audit_d0_reproduction(records: list[dict], campaign: dict,
                          expected_units: int | None = None,
                          errors: list[dict] | None = None) -> dict[str, Any]:
    """The validity gate: every seed, every limb, within 1e-4."""
    if expected_units is None:
        expected_units = len(TASKS) * len(SEEDS)
    checks = []
    failures = []
    for record in records:
        task, seed = record["task"], record["seed"]
        reference = campaign.get((task, seed))
        if reference is None:
            failure = {"task": task, "seed": seed,
                       "reason": "missing from the campaign artifact"}
            failures.append(failure)
            checks.append({**failure, "passed": False})
            continue
        for limb in LIMBS:
            expected = reference.get(limb)
            actual = record.get("d0", {}).get(limb)
            if expected is None or actual is None:
                failure = {"task": task, "seed": seed, "limb": limb,
                           "reason": "missing score"}
                failures.append(failure)
                checks.append({**failure, "passed": False})
                continue
            diff = abs(float(actual) - float(expected))
            passed = diff <= D0_TOLERANCE
            checks.append({"task": task, "seed": seed, "limb": limb,
                           "expected": round(float(expected), 6),
                           "actual": round(float(actual), 6),
                           "abs_diff": round(diff, 9), "passed": passed})
            if not passed:
                failures.append({"task": task, "seed": seed, "limb": limb,
                                 "expected": round(float(expected), 6),
                                 "actual": round(float(actual), 6),
                                 "abs_diff": round(diff, 9)})
    if errors:
        for error in errors:
            failures.append({"task": error.get("task"), "seed": error.get("seed"),
                             "reason": error.get("error", "unit failed")})
    missing = expected_units - len(records)
    if missing > 0:
        failures.append({"reason": f"{missing} of {expected_units} units missing"})
    diffs = [c["abs_diff"] for c in checks if "abs_diff" in c]
    passed = (not failures and len(records) == expected_units
              and len(checks) == expected_units * len(LIMBS))
    reason = (
        f"all {len(checks)} seed-limbs reproduced within {D0_TOLERANCE:g}"
        if passed else
        f"{len(failures)} failure(s); the decomposition is not the campaign object"
    )
    return {
        "passed": bool(passed),
        "tolerance": D0_TOLERANCE,
        "expected_units": expected_units,
        "units_present": len(records),
        "n_checks": len(checks),
        "max_abs_diff": max(diffs) if diffs else None,
        "failures": failures[:50],
        "checks": checks,
        "reason": reason,
    }


def audit_denominators(records: list[dict]) -> dict[str, Any]:
    failures = []
    for record in records:
        for limb in LIMBS:
            counts = _iter_dict(record.get("limb_counts")).get(limb, {})
            if not counts.get("events") or not counts.get("cells"):
                failures.append({"task": record["task"], "seed": record["seed"],
                                 "limb": limb, "counts": counts})
    return {
        "passed": not failures,
        "failures": failures[:20],
        "reason": ("every limb has a denominator" if not failures
                   else "a limb has no denominator and is not measurable"),
    }


def audit_attribution(records: list[dict]) -> dict[str, Any]:
    failures = [
        {"task": r["task"], "seed": r["seed"],
         "max_edge_diff": _iter_dict(r.get("attribution")).get("max_edge_diff")}
        for r in records
        if not _iter_dict(r.get("attribution")).get("ok", False)
    ]
    return {
        "passed": not failures,
        "failures": failures[:20],
        "reason": ("per-type edges reconcile to the full asserted structure"
                   if not failures else
                   "a unit's per-type edges do not reconcile; its variants are invalid"),
    }


def audit_known_answer() -> dict[str, Any]:
    vocab = {"a", "b", "c", "d"}
    base = {t: 0.25 for t in vocab}
    rows = {"a": {"b": 20.0, "c": 1.0, "d": 1.0},
            "b": {"c": 20.0}, "c": {"a": 20.0}, "d": {"a": 20.0}}
    checks = {}
    for alpha in ALPHA_GRID:
        p = make_organica_backoff(rows, base, alpha)
        checks[f"backoff_{alpha:g}"] = bool(p("a", "b") > p("a", "c"))
    direct = fit_direct_conditional(["a", "b", "a", "c", "a", "b"], vocab, 1.0)
    checks["direct"] = bool(direct("a", "b") > direct("a", "c"))
    return {"passed": all(checks.values()), "checks": checks,
            "reason": ("the readouts recover a known relation" if all(checks.values())
                       else "a readout cannot recover a known relation")}


def audit_shuffled_collapse() -> dict[str, Any]:
    vocab = {"a", "b", "c", "d"}
    base = {t: 0.25 for t in vocab}
    uniform = {u: {v: 1.0 for v in vocab} for u in vocab}
    checks = {}
    for alpha in ALPHA_GRID:
        p = make_organica_backoff(uniform, base, alpha)
        checks[f"backoff_{alpha:g}"] = max(
            abs(p(u, v) - base[v]) for u in vocab for v in vocab) < 0.01
    direct = fit_direct_conditional(["a b c d"] * 8, vocab, 1.0)
    checks["direct"] = max(
        abs(direct(u, v) - 0.25) for u in vocab for v in vocab) < 0.08
    return {"passed": all(checks.values()), "checks": checks,
            "reason": ("uniform evidence collapses to the base rate"
                       if all(checks.values()) else
                       "a readout does not collapse on uniform evidence")}


def audit_calibration_isolation(calibration: dict) -> dict[str, Any]:
    tasks = _iter_dict(calibration.get("tasks"))
    checks = {
        "seed_is_calibration": calibration.get("seed") == CALIBRATION_SEED,
        "calibration_not_a_scoring_seed": CALIBRATION_SEED not in SEEDS,
        "every_task_has_a_selected_alpha": all(
            _iter_dict(tasks.get(t)).get("selected_alpha") in ALPHA_GRID
            for t in TASKS),
        "calibration_seed_recorded": all(
            _iter_dict(tasks.get(t)).get("seed") == CALIBRATION_SEED
            for t in TASKS),
    }
    return {"passed": all(checks.values()), "checks": checks,
            "reason": ("D3's alpha was selected only on the calibration seed"
                       if all(checks.values()) else
                       "the calibration is not isolated from the scoring seeds")}


def audit_d2_constants() -> dict[str, Any]:
    constants_ok = (D2_CONSTANTS.get("prediction_candidate") == 1.0
                    and D2_CONSTANTS.get("__other__") == 0.5)
    by_type = {
        "prediction_candidate": {"a": {"b": 10.0}},
        "concept_candidate": {"a": {"c": 10.0}},
    }
    weighted = aggregate_type_rows(by_type, d2_weight)
    layer1 = aggregate_type_rows(by_type, layer1_weight)
    effect_ok = (weighted.get("a", {}).get("c", 0.0) > 0.0
                 and layer1.get("a", {}).get("c", 0.0) == 0.0
                 and weighted.get("a", {}).get("b", 0.0) > 0.0)
    return {
        "passed": bool(constants_ok and effect_ok),
        "checks": {"constants": constants_ok, "type_weight_is_live": effect_ok,
                   "constants_recorded": dict(D2_CONSTANTS)},
        "reason": ("D2's constants are fixed and load-bearing"
                   if constants_ok and effect_ok else
                   "D2's constants are not the declared constants, or are inert"),
    }


def audit_one_seed(records: list[dict]) -> dict[str, Any]:
    return {"passed": len(records) >= 2,
            "n": len(records),
            "reason": ("at least two seeds" if len(records) >= 2
                       else "one seed is a draw, not a test")}


def record_is_valid(record: dict) -> bool:
    if not _iter_dict(record.get("attribution")).get("ok", False):
        return False
    for limb in LIMBS:
        counts = _iter_dict(record.get("limb_counts")).get(limb, {})
        if not counts.get("events") or not counts.get("cells"):
            return False
    return True


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def _interval(deltas: list[float]) -> dict[str, Any]:
    if len(deltas) < 2:
        return {"verdict": "not measurable", "reason": "fewer than two seeds",
                "n": len(deltas)}
    return fu.paired_bootstrap(deltas)


def _cell(deltas: list[float]) -> dict[str, Any]:
    interval = _interval(deltas)
    if interval.get("verdict") == "not measurable":
        return interval
    cell = dict(interval)
    cell["verdict"] = fu.verdict_of(cell["lo"], cell["hi"])
    cell["helps"] = bool(cell["lo"] > 0 and cell["mean"] >= EFFECT_THRESHOLD)
    return cell


def analyse(records: list[dict], calibration: dict | None = None,
            d0_gate: dict | None = None) -> dict[str, Any]:
    """Decompose the room and map it — only after the D0 gate has passed.

    When ``d0_gate`` is supplied and it failed, this raises rather than
    returning a mapping.  The caller may still write the audit-required
    artifact, but it cannot obtain a mechanism from this function.
    """
    if d0_gate is not None and not d0_gate.get("passed"):
        raise AuditRequired(
            "the D0 validity gate failed; no room estimate or mechanism may be "
            "mapped from this object")
    cells: dict[str, dict[str, dict[str, Any]]] = {}
    room: dict[str, dict[str, Any]] = {}
    for task in TASKS:
        task_records = [r for r in records if r["task"] == task]
        cells[task] = {}
        room[task] = {}
        if len(task_records) < 2:
            for arm in ("D1", "D2", "D3", "D4"):
                cells[task][arm] = {
                    limb: {"verdict": "not measurable",
                           "reason": "fewer than two seeds", "n": len(task_records)}
                    for limb in LIMBS}
            for limb in LIMBS:
                room[task][limb] = {"verdict": "not measurable",
                                    "reason": "fewer than two seeds",
                                    "n": len(task_records)}
            continue
        for arm in ("D1", "D2", "D3", "D4"):
            cells[task][arm] = {}
            for limb in LIMBS:
                deltas = []
                for record in task_records:
                    value = _iter_dict(record.get("variants")).get(arm, {})
                    arm_score = _iter_dict(value).get(limb)
                    if arm_score is None:
                        continue
                    deltas.append(float(record["d0"][limb]) - float(arm_score))
                cells[task][arm][limb] = _cell(deltas)
        for limb in LIMBS:
            deltas = []
            d0_values = []
            d5_values = []
            for record in task_records:
                ceiling = _iter_dict(record.get("d5")).get(limb)
                pinned = _iter_dict(record.get("d0")).get(limb)
                if ceiling is None or pinned is None:
                    continue
                d0_values.append(float(pinned))
                d5_values.append(float(ceiling))
                deltas.append(float(ceiling) - float(pinned))
            room[task][limb] = _cell(deltas)
            room[task][limb]["d0_mean"] = (
                round(sum(d0_values) / len(d0_values), 6) if d0_values else None)
            room[task][limb]["d5_mean"] = (
                round(sum(d5_values) / len(d5_values), 6) if d5_values else None)

    mapping = _map(cells, room)
    return {"status": "complete", "cells": cells, "room": room,
            "mapping": mapping, "calibration": calibration}


def _mapping_reason(cells: dict, room: dict, outcome: str, component: str | None,
                    primary: str | None = None) -> str:
    t2 = room["T2"]["transfer"].get("mean")
    t1 = room["T1"]["transfer"].get("mean")
    if outcome == "evidence_limited":
        return (f"the room is {_fmt(t2)} nats on T2 and {_fmt(t1)} on T1, "
                f"below the {ROOM_THRESHOLD:g}-nat threshold, and no arm helps")
    if outcome == "unknown_use_path_mechanism":
        return (f"the room is {_fmt(t2)} nats on T2 and {_fmt(t1)} on T1, "
                "but none of D1–D4 helps on both tasks")
    if outcome == "task_dependent":
        return ("the room or the helping arm differs between T2 and T1; "
                "no single target is selected")
    if outcome == "audit_anomaly":
        return ("a variant helps where the ceiling leaves less room than the "
                "effect threshold, or the readout beats the ceiling by more "
                "than 0.05 nats")
    if outcome == "mechanism_candidate":
        return (f"{primary} helps on transfer on both tasks with a room of "
                f"{_fmt(t2)} nats on T2 and {_fmt(t1)} on T1")
    return "not measurable"


def _map(cells: dict, room: dict) -> dict[str, Any]:
    t2_room = room["T2"]["transfer"].get("mean")
    t1_room = room["T1"]["transfer"].get("mean")
    if t2_room is None or t1_room is None:
        return {"outcome": "not_measurable",
                "reason": "the room estimate is not measurable",
                "room_means": {"T2": t2_room, "T1": t1_room}}

    def helped(task: str, arm: str) -> bool:
        return bool(cells[task][arm]["transfer"].get("helps", False))

    def both(arm: str) -> bool:
        return helped("T2", arm) and helped("T1", arm)

    def any_helped() -> bool:
        return any(helped(t, a) for t in TASKS for a in ("D1", "D2", "D3", "D4"))

    def room_ok(task: str) -> bool:
        value = room[task]["transfer"].get("mean")
        return value is not None and value >= ROOM_THRESHOLD

    helping = {t: {a: helped(t, a) for a in ("D1", "D2", "D3", "D4")}
               for t in TASKS}
    common = {"helping": helping,
              "room_means": {"T2": t2_room, "T1": t1_room}}

    if any(helped(t, a) and not room_ok(t) for t in TASKS
           for a in ("D1", "D2", "D3", "D4")):
        return {"outcome": "audit_anomaly",
                "reason": _mapping_reason(cells, room, "audit_anomaly", None),
                **common}
    if any(room[t]["transfer"].get("mean") is not None
           and room[t]["transfer"]["mean"] < -0.05 for t in TASKS):
        return {"outcome": "audit_anomaly",
                "reason": "the pinned readout beats the ceiling by more than 0.05 nats",
                **common}

    if not room_ok("T2") and not room_ok("T1"):
        if any_helped():
            return {"outcome": "audit_anomaly",
                    "reason": _mapping_reason(cells, room, "audit_anomaly", None),
                    **common}
        return {"outcome": "evidence_limited",
                "reason": _mapping_reason(cells, room, "evidence_limited", None),
                **common}

    if room_ok("T2") and room_ok("T1"):
        d1, d2 = both("D1"), both("D2")
        d3, d4 = both("D3"), both("D4")
        candidates = []
        if d1:
            candidates.append(("D1", "retrieval_activation"))
        if d2:
            candidates.append(("D2", "retrieval_activation"))
        if d3:
            candidates.append(("D3", "readout_form"))
        if d4:
            candidates.append(("D4", "readout_form"))
        if candidates:
            candidates.sort(
                key=lambda item: cells["T2"][item[0]]["transfer"].get("mean", -99),
                reverse=True)
            primary, component = candidates[0]
            components = []
            for _arm, comp in candidates:
                if comp not in components:
                    components.append(comp)
            losing = []
            for task in TASKS:
                for limb in ("retention", "revision"):
                    if cells[task][primary][limb].get("verdict") == "loss":
                        losing.append({"task": task, "limb": limb})
            return {
                "outcome": "mechanism_candidate",
                "component": component,
                "components": components,
                "arm": primary,
                "partial": bool(losing),
                "losing": losing,
                "reason": _mapping_reason(cells, room, "mechanism_candidate",
                                          component, primary),
                **common,
            }
        if any_helped():
            return {"outcome": "task_dependent",
                    "reason": _mapping_reason(cells, room, "task_dependent", None),
                    **common}
        return {"outcome": "unknown_use_path_mechanism",
                "reason": _mapping_reason(cells, room,
                                          "unknown_use_path_mechanism", None),
                **common}

    return {"outcome": "task_dependent",
            "reason": _mapping_reason(cells, room, "task_dependent", None),
            **common}


# ---------------------------------------------------------------------------
# Artifact assembly and the result document
# ---------------------------------------------------------------------------

def _assert_no_placeholder(md: str) -> str:
    match = re.search(r"\{[A-Za-z_][^}]*\}", md)
    if match:
        raise ValueError(f"unsubstituted placeholder in the result: {match.group(0)}")
    return md


def _limb_table(cells: dict, task: str) -> list[str]:
    lines = ["| Arm | Retention d | Transfer d | Revision d | Transfer verdict | Transfer helps |",
             "|---|---:|---:|---:|---|---|"]
    for arm in ("D1", "D2", "D3", "D4"):
        row = [arm]
        for limb in LIMBS:
            c = cells[task][arm][limb]
            if c.get("verdict") == "not measurable":
                row.append("n/a")
            else:
                row.append(f"{_fmt(c['mean'])} [{_fmt(c['lo'])}, {_fmt(c['hi'])}]")
        transfer = cells[task][arm]["transfer"]
        row.append(str(transfer.get("verdict", "n/a")))
        row.append(_fmt(transfer.get("helps")))
        lines.append("| " + " | ".join(row) + " |")
    return lines


def _room_table(room: dict, task: str) -> list[str]:
    lines = ["| Limb | D0 mean | D5 mean | Room (D5 − D0) | 98.33% interval | Verdict |",
             "|---|---:|---:|---:|---|---|"]
    for limb in LIMBS:
        r = room[task][limb]
        if r.get("verdict") == "not measurable":
            lines.append(f"| {limb} | n/a | n/a | n/a | n/a | not measurable |")
        else:
            lines.append(
                f"| {limb} | {_fmt(r.get('d0_mean'))} | {_fmt(r.get('d5_mean'))} | "
                f"{_fmt(r['mean'])} | [{_fmt(r['lo'])}, {_fmt(r['hi'])}] | "
                f"{r.get('verdict', 'n/a')} |")
    return lines


def _render_audit(artifact: dict) -> str:
    gate = artifact["d0_reproduction"]
    lines = [
        "# AUDIT REQUIRED — the use-path diagnostic",
        "",
        "**No room estimate and no mechanism mapping are reported.**",
        "",
        "## 0. The D0 validity gate",
        "",
        f"D0 was required to reproduce the formation-utilization campaign's arm-C "
        f"scores on all {gate.get('expected_units')} units and every scored limb "
        f"within {_fmt(gate.get('tolerance'), 6)}. "
        f"Units present: {gate.get('units_present')}. "
        f"Seed-limbs checked: {gate.get('n_checks')}. "
        f"Largest absolute difference: {_fmt(gate.get('max_abs_diff'), 6)}.",
        "",
        f"**{len(gate.get('failures', []))} failure(s)**:",
        "",
    ]
    for failure in gate.get("failures", [])[:20]:
        lines.append(
            f"- {failure.get('task', '?')} / {failure.get('seed', '?')} / "
            f"{failure.get('limb', '?')}: {failure}")
    if not gate.get("failures"):
        lines.append("- no individual failure recorded; the unit count is short")
    lines += [
        "",
        "## 1. What this means",
        "",
        "The diagnostic is decomposing a different object than the one that produced "
        "the campaign's ceiling result. A decomposition of that object cannot select "
        "a mechanism. The next step is an audit of the reproduction — the recorder, "
        "the fixed temporal basis, the engine version, or the saved structures — not "
        "a reading of D1–D5.",
        "",
        "## 2. What is not reported",
        "",
        "- No room estimate.",
        "- No variant effect.",
        "- No component, and no `evidence-limited` conclusion.",
        "",
        "## 3. Provenance",
        "",
        f"- Protocol: `{artifact.get('protocol')}`",
        f"- Protocol SHA-256: `{artifact.get('protocol_sha256')}`",
        f"- Freeze commit: `{artifact.get('freeze_commit')}`",
        f"- Campaign artifact: `{artifact.get('campaign_artifact')}`",
        f"- Engine: {artifact.get('engine_version')}",
        f"- Hash seed: `PYTHONHASHSEED={artifact.get('pythonhashseed', 'not recorded')}`",
        f"- Generated: {artifact.get('generated_utc')}",
        "",
    ]
    return _assert_no_placeholder("\n".join(lines))


def _mapping_label(mapping: dict) -> str:
    outcome = mapping.get("outcome", "not_measurable")
    if outcome == "mechanism_candidate":
        component = mapping.get("component", "")
        label = {"retrieval_activation": "retrieval / activation",
                 "readout_form": "readout form"}.get(component, component)
        suffix = " (partial)" if mapping.get("partial") else ""
        return f"MECHANISM CANDIDATE — {label}{suffix}"
    return {
        "evidence_limited": "EVIDENCE-LIMITED",
        "unknown_use_path_mechanism": "UNKNOWN USE-PATH MECHANISM",
        "task_dependent": "TASK-DEPENDENT",
        "audit_anomaly": "AUDIT ANOMALY",
        "not_measurable": "NOT MEASURABLE",
    }.get(outcome, outcome)


def render_results(artifact: dict) -> str:
    """Generate the result document from the artifact, gate first."""
    gate = artifact.get("d0_reproduction") or {}
    if not gate.get("passed"):
        return _render_audit(artifact)

    constants = _iter_dict(artifact.get("constants"))
    mapping = _iter_dict(artifact.get("mapping"))
    room = _iter_dict(artifact.get("room"))
    cells = _iter_dict(artifact.get("cells"))
    audits = _iter_dict(artifact.get("audits"))
    records = artifact.get("records") or []
    n_units = len(records)

    lines = [
        "# The use-path diagnostic — results",
        "",
        "> The formation-utilization campaign established that weak transfer despite "
        "correct internal structure is an observed ceiling condition and selected the "
        "use path as the target of investigation. It did not identify the binding "
        "component of that path and therefore did not, by itself, satisfy the mechanism "
        "requirement for a V2 build authorization.",
        "",
        "## 0. The D0 validity gate",
        "",
        f"D0 reproduced the campaign's arm-C scores on all {gate.get('expected_units')} "
        f"units and every scored limb within {_fmt(gate.get('tolerance'), 6)}. "
        f"Units present: {n_units}. Seed-limbs checked: {gate.get('n_checks')}. "
        f"Largest absolute difference: {_fmt(gate.get('max_abs_diff'), 6)}. "
        f"Hash seed: `PYTHONHASHSEED={artifact.get('pythonhashseed', 'not recorded')}`.",
        "",
        "**PASS.** The decomposition is of the object that produced the campaign result. "
        "The room estimate below is interpretable; nothing above it is.",
        "",
        "## 1. The room in the use path",
        "",
        f"`room = D5 − D0` on the same contexts. Positive means the true conditional "
        f"is above the pinned readout, i.e. there is room between the readout and the "
        f"best possible score. The threshold is {_fmt(constants.get('room_threshold'), 2)} nats.",
        "",
    ]
    if not artifact.get("protocol_complete", True):
        lines.insert(7,
                     "> **NON-CONFIRMATORY SUBSET.** This artifact does not contain "
                     "the protocol's 30 seeds on both tasks. It is a debugging run, "
                     "not the confirmatory result.\n")
    if artifact.get("control_failures"):
        lines.insert(7,
                     "> **CONTROL FAILURE.** One or more controls failed: "
                     + ", ".join(artifact["control_failures"])
                     + ". The affected arms are not measurable; see §4.\n")
    for task in TASKS:
        lines += [f"**{task}**", ""]
        lines += _room_table(room, task)
        lines += [""]
    if artifacts_room_below_floor(room):
        lines += [
            "The room is below the declared threshold on both tasks. That is the "
            "**evidence-limited** condition; it is a result, not a failure of the run.",
            "",
        ]

    lines += [
        "## 2. The variants",
        "",
        "`d = D0 − arm`; positive favours the variant. An effect is a win only when the "
        f"lower bound is above zero **and** the mean is at least "
        f"{_fmt(constants.get('effect_threshold'), 2)} nats.",
        "",
    ]
    for task in TASKS:
        lines += [f"**{task}**", ""]
        lines += _limb_table(cells, task)
        lines += [""]

    lines += [
        "## 3. The pre-committed mapping",
        "",
        f"**{_mapping_label(mapping)}**",
        "",
        f"{mapping.get('reason', '')}",
        "",
    ]
    if mapping.get("outcome") == "mechanism_candidate":
        lines += [
            f"- Primary arm: **{mapping.get('arm')}**",
            f"- Component: **{mapping.get('component')}**",
            f"- Components named: {', '.join(mapping.get('components', [])) or 'none'}",
            f"- Partial: **{_fmt(mapping.get('partial'))}**",
        ]
        if mapping.get("partial"):
            losing = ", ".join(
                f"{x.get('task')}/{x.get('limb')}" for x in mapping.get("losing", []))
            lines.append(f"- Losing limbs: {losing}")
        lines += [""]

    lines += [
        "## 4. Controls",
        "",
        "| Control | Result |",
        "|---|---|",
    ]
    for name in ("known_answer", "shuffled", "denominators", "attribution",
                 "calibration", "d2_constants", "one_seed"):
        audit = _iter_dict(audits.get(name))
        lines.append(f"| {name} | {_fmt(audit.get('passed'))} |")
    lines += [
        "",
        f"D0 itself is the first control and the validity gate: "
        f"**{_fmt(gate.get('passed'))}**.",
        "",
        "## 5. What this does not establish",
        "",
        "- It does not establish that the use path is the defect in general; it "
        "decomposes one world family and two tasks.",
        "- It does not establish a deployable fix: C is given the support and reads "
        "B's evidence, so a component candidate is a hypothesis for a confirmatory "
        "protocol.",
        "- It does not establish that the engine can form the structure; B remains "
        "the discovery arm.",
        "- It does not establish causality: the arms are re-scorings of the same "
        "asserted graph.",
        "- It does not authorise a V2 build. It can select a component for a V2 brief.",
        "",
        "## 6. Provenance",
        "",
        f"- Protocol: `{artifact.get('protocol')}`",
        f"- Protocol SHA-256: `{artifact.get('protocol_sha256')}`",
        f"- Freeze commit: `{artifact.get('freeze_commit')}`",
        f"- Campaign artifact: `{artifact.get('campaign_artifact')}`",
        f"- Engine: {artifact.get('engine_version')}",
        f"- Hash seed: `PYTHONHASHSEED={artifact.get('pythonhashseed', 'not recorded')}`",
        f"- Generated: {artifact.get('generated_utc')}",
        f"- Seeds: {len(artifact.get('seeds', []))} per task; tasks: "
        f"{', '.join(artifact.get('tasks', []))}",
        "",
    ]
    return _assert_no_placeholder("\n".join(lines))


def artifacts_room_below_floor(room: dict) -> bool:
    means = []
    for task in TASKS:
        value = _iter_dict(room.get(task)).get("transfer", {}).get("mean")
        if value is not None:
            means.append(value)
    return len(means) == len(TASKS) and all(v < ROOM_THRESHOLD for v in means)


# ---------------------------------------------------------------------------
# Run, resume, assemble
# ---------------------------------------------------------------------------

def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def _part_path(task: str, seed: int) -> Path:
    return PARTS / f"{task}_{seed}.json"


def _load_parts() -> list[dict]:
    if not PARTS.exists():
        return []
    parts = []
    for path in sorted(PARTS.glob("*.json")):
        try:
            parts.append(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    return parts


def _single_run(task: str, seed: int, calibration: dict) -> dict:
    alpha = None
    task_cal = _iter_dict(_iter_dict(calibration.get("tasks")).get(task))
    if task_cal.get("selected_alpha") is not None:
        alpha = float(task_cal["selected_alpha"])
    record = run_unit(task, seed, alpha)
    return {"task": task, "seed": seed, "status": "ok", "record": record}


def run_all(workers: int, force: bool = False, seeds: tuple[int, ...] = SEEDS,
            tasks: tuple[str, ...] = TASKS) -> dict:
    freeze = check_freeze()
    campaign = load_campaign_c()
    calibration = load_or_run_calibration()
    PARTS.mkdir(parents=True, exist_ok=True)

    todo = [(task, seed) for task in tasks for seed in seeds
            if force or not _part_path(task, seed).exists()]
    print(f"[run] {len(todo)} unit(s) to run, {workers} worker(s)", flush=True)
    if todo:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(_run_unit_worker, task, seed,
                            _iter_dict(_iter_dict(calibration["tasks"]).get(task))
                            .get("selected_alpha")): (task, seed)
                for task, seed in todo
            }
            for future in as_completed(futures):
                task, seed = futures[future]
                try:
                    record = future.result()
                    payload = {"task": task, "seed": seed, "status": "ok",
                               "record": record}
                    print(f"[done] {task} {seed} in {record['seconds']['total']:.1f}s",
                          flush=True)
                except Exception as exc:  # noqa: BLE001 - the failure is the record
                    payload = {"task": task, "seed": seed, "status": "error",
                               "error": f"{type(exc).__name__}: {exc}"}
                    print(f"[error] {task} {seed}: {payload['error']}", flush=True)
                _atomic_write(_part_path(task, seed),
                              json.dumps(payload, indent=2, sort_keys=True) + "\n")

    wanted = {(task, seed) for task in tasks for seed in seeds}
    parts = [p for p in _load_parts()
             if (p.get("task"), p.get("seed")) in wanted]
    records = [p["record"] for p in parts if p.get("status") == "ok"]
    errors = [p for p in parts if p.get("status") != "ok"]
    gate = audit_d0_reproduction(records, campaign,
                                 expected_units=len(tasks) * len(seeds),
                                 errors=errors)
    valid_records = [r for r in records if record_is_valid(r)]
    audits = {
        "denominators": audit_denominators(records),
        "attribution": audit_attribution(records),
        "known_answer": audit_known_answer(),
        "shuffled": audit_shuffled_collapse(),
        "calibration": audit_calibration_isolation(calibration),
        "d2_constants": audit_d2_constants(),
        "one_seed": audit_one_seed(records),
    }
    if gate["passed"]:
        analysis = analyse(valid_records, calibration, d0_gate=gate)
    else:
        analysis = {
            "status": "audit_required",
            "cells": None,
            "room": None,
            "mapping": None,
            "calibration": calibration,
        }
    control_failures = [name for name, audit in audits.items()
                        if not audit.get("passed")]
    status = analysis["status"]
    if status == "complete" and control_failures:
        status = "complete_with_control_failures"

    artifact = {
        "d0_reproduction": gate,
        "status": status,
        "protocol": str(PROTOCOL.relative_to(REPO)),
        "protocol_sha256": freeze.get("protocol_sha256"),
        "freeze_commit": freeze.get("freeze_commit"),
        "campaign_artifact": str(CAMPAIGN.relative_to(REPO)),
        "engine_version": ENGINE_VERSION,
        "pythonhashseed": os.environ.get("PYTHONHASHSEED"),
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "protocol_complete": (tuple(seeds) == SEEDS and tuple(tasks) == TASKS),
        "seeds": list(seeds),
        "tasks": list(tasks),
        "constants": {
            "d0_tolerance": D0_TOLERANCE,
            "pythonhashseed": HASH_SEED,
            "effect_threshold": EFFECT_THRESHOLD,
            "room_threshold": ROOM_THRESHOLD,
            "decision_alpha": DECISION_ALPHA,
            "bootstrap_reps": BOOTSTRAP_REPS,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "alpha_grid": list(ALPHA_GRID),
            "d2_constants": dict(D2_CONSTANTS),
            "d4_add_one": D4_ADD_ONE,
        },
        "calibration": calibration,
        "audits": audits,
        "control_failures": control_failures,
        "excluded_units": [
            {"task": r["task"], "seed": r["seed"],
             "reason": "attribution or denominator control failed"}
            for r in records
            if (r["task"], r["seed"]) not in
            {(v["task"], v["seed"]) for v in valid_records}
        ],
        "room": analysis.get("room"),
        "cells": analysis.get("cells"),
        "mapping": analysis.get("mapping"),
        "records": records,
    }
    _atomic_write(ARTIFACT, json.dumps(artifact, indent=2, sort_keys=False) + "\n")
    _atomic_write(RESULT_MD, render_results(artifact))
    return artifact


def self_test() -> int:
    require_hash_seed()
    freeze = check_freeze()
    campaign = load_campaign_c()
    record = run_unit("T2", SEEDS[0], None)
    gate = audit_d0_reproduction([record], campaign, expected_units=1)
    print(json.dumps({
        "freeze": freeze.get("protocol_sha256"),
        "pythonhashseed": os.environ.get("PYTHONHASHSEED"),
        "seed": record["seed"],
        "d0": record["d0"],
        "d0_gate": {"passed": gate["passed"],
                    "max_abs_diff": gate["max_abs_diff"],
                    "failures": gate["failures"]},
        "attribution": record["attribution"],
    }, indent=2))
    return 0 if gate["passed"] else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true",
                        help="check the freeze and run one unit end to end")
    parser.add_argument("--run", action="store_true",
                        help="run the 60 confirmatory units and write the artifact")
    parser.add_argument("--calibrate", action="store_true",
                        help="run the calibration seed and cache the result")
    parser.add_argument("--render", action="store_true",
                        help="regenerate the result document from the artifact")
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--force", action="store_true",
                        help="ignore existing part files and the calibration cache")
    parser.add_argument("--seeds", type=int, default=len(SEEDS),
                        help="number of confirmatory seeds (default 30)")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()
    if args.calibrate:
        print(json.dumps(load_or_run_calibration(force=args.force), indent=2))
        return 0
    if args.run:
        seeds = SEEDS[: args.seeds]
        artifact = run_all(args.workers, force=args.force, seeds=seeds)
        print(f"[written] {ARTIFACT}  status={artifact['status']}")
        return 0 if artifact["d0_reproduction"]["passed"] else 1
    if args.render:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        _atomic_write(RESULT_MD, render_results(artifact))
        print(f"[written] {RESULT_MD}")
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
