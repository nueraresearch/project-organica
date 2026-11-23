"""The scaling ladder: is a run's resolution the bottleneck, or its replication?

The question is fixed before the run in `docs/SCALING-LADDER.md`: for the
endpoint this project actually reports — the Organica readout against the
strongest simple comparator, paired per observation — how much of a run's
variability is **within** a run (sampling one world's scored window) and how
much is **between** runs (a different world)? More observations per run can only
shrink the first; only more runs shrink the second.

The intervention is the scored window, not the exposure. Formation is 110 cycles
in every cell and every arm, so the ladder changes how much of one world a run is
scored on and nothing else — no new seeds, no confirmatory block, no engine
change.

What this module does not do
----------------------------

* It does not compare any delta with a study bar, does not form a verdict about
  Organica, and never reads a confirmatory seed. Its seeds are fresh (20270501+)
  and disjoint from every study block; `refuse_study_seed` enforces that before a
  database is opened.
* It does not measure the effect of a longer *exposure*. A longer formation
  stream is a different intervention (more learning, not more observation) and is
  not part of this ladder.

The law is held at `LAW_R0` for the whole world, deliberately: the readout is
formed under that law, and a regime rotation inside the scored window would
change the generating process partway through a run and confound the ladder. This
is a declared difference from the frozen design's default world (`caveats` in the
artifact).
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import random
import sys
import time
from statistics import NormalDist, mean, stdev
from typing import Any, Sequence

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from benchmarks import functional_structure as fs  # noqa: E402
from benchmarks.acquisition_compositional import (  # noqa: E402
    EVENTS_PER_CYCLE, PHASE_TRANSFER, generate_compositional_world,
)
from benchmarks.acquisition_runner import (  # noqa: E402
    CALIBRATED_ORGANICA_ALPHA, make_organica_backoff,
)
from benchmarks.functional_harness import (  # noqa: E402
    CONFIRMATORY_SEEDS as FS_CONFIRMATORY, DESIGN_SEEDS as FS_DESIGN,
    base_rates, run_formation,
)
from benchmarks.reusable_knowledge import (  # noqa: E402
    MAX_PREDICTIONS, TUNE_CYCLES, _pairs, comparator_sweep,
    conditioned_formation_stream,
)
from benchmarks.strength_assignment_harness import (  # noqa: E402
    CONFIRMATORY_SEEDS as SA_CONFIRMATORY, DESIGN_SEEDS as SA_DESIGN,
)
from benchmarks import engine_stamp

# ---------------------------------------------------------------------------
# Fixed constants. None of these is a parameter of the study.
# ---------------------------------------------------------------------------

#: Fresh methodology seeds. They carry no scientific claim, are in no study
#: block, and are listed here so the block is auditable rather than implied.
SEEDS: tuple[int, ...] = (20270501, 20270502, 20270503, 20270504, 20270505)

#: The scored window starts where the frozen study's primary window starts (150)
#: and is extended. `1x` is the frozen design's 50-cycle window (150-200).
BASE_CYCLES = PHASE_TRANSFER[1] - PHASE_TRANSFER[0]     # 50
SCALES: dict[str, int] = {"1x": 1, "2x": 2, "4x": 4, "8x": 8, "16x": 16}


def window_end(factor: int) -> int:
    """The last cycle of the scored window at a scale: 150 + 50 x factor.

    The scale is a length, `_pairs` takes an end. They are different numbers, and
    treating one as the other produced an empty window that scored as nothing.
    """
    return PHASE_TRANSFER[0] + BASE_CYCLES * factor

CAP = MAX_PREDICTIONS
ALPHA = CALIBRATED_ORGANICA_ALPHA
BASELINE_FAMILIES = ("replay", "bigram", "decayed_bigram")

#: Contiguous quarters of the scored window: the consistency diagnostic and the
#: cluster bootstrap's resampling unit. Blocks, not pairs, because consecutive
#: observations of one world are not independent draws.
BLOCKS = 4
BOOTSTRAP_RESAMPLES = 2_000
BOOTSTRAP_SEED = 20270500

#: Paired observations are scored in chunks so a 16x window never holds millions
#: of cell records at once. The chunking does not change any number: per-pair
#: means are accumulated and only their list is kept.
CHUNK = 400

#: The pre-committed decision rule (docs/SCALING-LADDER.md §5). `rho` is the
#: mean within-run standard error over the between-run standard deviation at the
#: same scale. Fixed before any cell ran.
RHO_REPLICATE = 0.5      # within-run error at most half the between-run SD
RHO_RESOLUTION = 1.0     # within-run error at least the between-run SD
EXPECTED_SLOPE = -0.5    # independent observations: SE falls as n^-1/2
SLOPE_BAND = 0.15        # pre-committed band on the fitted log-log slope

#: Added after the run was read (`docs/SCALING-LADDER.md` §8): the probability
#: that one run at a given window reports the sign of its own world's effect.
#: It is a measurement-design diagnostic, not part of §5's rule, and it cannot
#: re-score the verdict that rule produced.
SIGN_TARGET = 0.90
SIGN_REPLICATES = 20_000
SIGN_RESEED = 20270506

FORBIDDEN_SEEDS: frozenset[int] = frozenset(
    set(FS_DESIGN) | set(FS_CONFIRMATORY) | set(SA_DESIGN) | set(SA_CONFIRMATORY)
)

OUT = "docs/scaling_ladder.json"


# ---------------------------------------------------------------------------
# Guards
# ---------------------------------------------------------------------------

def refuse_study_seed(seed: int) -> int:
    """A methodology cell may never be spent on a study's design or confirmatory block."""
    if seed in FORBIDDEN_SEEDS:
        raise SystemExit(
            f"seed {seed} belongs to a study block: the ladder measures resolution "
            "and may not consume a study seed, design or confirmatory")
    if seed not in SEEDS:
        raise SystemExit(f"seed {seed} is not in the methodology block {SEEDS}")
    return seed


def verdict(rho: float | None) -> str:
    """§5 in one place: which constraint binds at this scale."""
    if rho is None:
        return "not measurable"
    if rho <= RHO_REPLICATE:
        return "replication-limited"
    if rho >= RHO_RESOLUTION:
        return "resolution-limited"
    return "both"


# ---------------------------------------------------------------------------
# One reading: the world, the frozen readout, the comparator
# ---------------------------------------------------------------------------

def window_pairs(events: Sequence[str], end_cycle: int) -> tuple[list[list[str]], list[list[str]]]:
    """The scored window: cycle 150 to `end_cycle`, as the frozen study defines pairs."""
    ctx, obs = _pairs(list(events), PHASE_TRANSFER[0], end_cycle)
    if not ctx:
        raise AssertionError(
            f"the scored window 150-{end_cycle} is empty: the scale axis is dead "
            "and a dead axis reads as a null (AGENTS rule 13c)")
    return ctx, obs


def arm_pair_losses(prob, ctx, obs, vocab) -> list[float]:
    """Mean loss per event pair, so a pair is one observation of the endpoint."""
    out: list[float] = []
    for start in range(0, len(ctx), CHUNK):
        acc: dict[Any, list[float]] = {}
        stop = start + CHUNK
        for cell in fs.cells(prob, ctx[start:stop], obs[start:stop], vocab):
            acc.setdefault(cell["pair"], []).append(fs.cell_loss(cell["y"], cell["p"]))
        out.extend(mean(v) for _, v in sorted(acc.items()))
    return out


def block_stats(values: Sequence[float], blocks: int = BLOCKS,
                resamples: int = BOOTSTRAP_RESAMPLES,
                seed: int = BOOTSTRAP_SEED) -> dict[str, Any]:
    """Within-run standard error and consistency of one run's paired deltas.

    `se_iid` treats pairs as independent draws; `se_block` resamples contiguous
    quarters, which is what a temporally ordered stream actually costs. The ratio
    of the two is a measurement in its own right: above 1, the pairs are not
    independent and a per-observation error bar is too optimistic.
    """
    n = len(values)
    if n < blocks:
        return {"n": n, "se_iid": None, "se_block": None, "block_over_iid": None,
                "quarters": [], "quarters_positive": 0, "spread": None}
    bounds = [i * n // blocks for i in range(blocks + 1)]
    groups = [list(values[bounds[i]:bounds[i + 1]]) for i in range(blocks)]
    sizes = [len(g) for g in groups]
    means = [mean(g) for g in groups]
    rng = random.Random(seed)
    draws = []
    for _ in range(resamples):
        pick = [rng.randrange(blocks) for _ in range(blocks)]
        total = sum(sizes[i] for i in pick)
        draws.append(sum(sizes[i] * means[i] for i in pick) / total)
    se_iid = stdev(values) / math.sqrt(n) if stdev(values) else 0.0
    se_block = stdev(draws)
    return {
        "n": n,
        "se_iid": round(se_iid, 9),
        "se_block": round(se_block, 9),
        "block_over_iid": round(se_block / se_iid, 4) if se_iid else None,
        "quarters": [round(m, 9) for m in means],
        "quarters_positive": sum(1 for m in means if m > 0),
        "spread": round(max(means) - min(means), 9),
    }


def _seed_cell(seed: int) -> dict[str, Any]:
    """One run's setup: the world, the formation exposure, the two probabilities.

    The world is generated at the longest scale and sliced for the others; the
    generator consumes the same random stream for its prefix, and `prefix_check`
    proves that rather than assuming it.
    """
    started = time.time()
    longest = window_end(max(SCALES.values()))
    world = generate_compositional_world(
        seed=seed, cycles=longest, regime_cycles=longest)   # LAW_R0 throughout
    formation = conditioned_formation_stream(world, seed)
    engine = run_formation(formation, seed, CAP)
    rate = base_rates(formation["events"])
    vocab = {t for row in world["events"] for t in row.split()}
    events = formation["events"]
    fit_rows = events[:len(events) - TUNE_CYCLES * EVENTS_PER_CYCLE]
    comps = comparator_sweep(events, fit_rows, vocab, world["tag_to_cell"])
    family = min(BASELINE_FAMILIES, key=lambda name: comps[name]["tuning_log_loss"])
    return {
        "world": world, "vocab": vocab, "events": world["events"],
        "org": make_organica_backoff(engine["rows"], rate, ALPHA),
        "baseline": {"family": family, "config": comps[family]["config"],
                     "prob": comps[family]["prob"]},
        "setup_seconds": round(time.time() - started, 1),
    }


def prefix_check(seed: int) -> dict[str, Any]:
    """The sliced worlds are prefixes of the longest one — checked, not assumed."""
    longest = window_end(max(SCALES.values()))
    full = generate_compositional_world(seed=seed, cycles=longest, regime_cycles=longest)
    ok = True
    checked = []
    for label, factor in SCALES.items():
        cycles = window_end(factor)
        short = generate_compositional_world(seed=seed, cycles=cycles, regime_cycles=cycles)
        same = short["events"] == full["events"][:cycles * EVENTS_PER_CYCLE]
        ok = ok and same
        checked.append({"scale": label, "cycles": cycles, "prefix_identical": same})
    return {"consistent": ok, "checked": checked}


def measure(seed: int) -> dict[str, Any]:
    """Every scale for one run: the paired delta, its within-run error, its quarters."""
    refuse_study_seed(seed)
    cell = _seed_cell(seed)
    out: dict[str, Any] = {"seed": seed, "baseline": {
        "family": cell["baseline"]["family"],
        "config": cell["baseline"]["config"]}, "scales": {}}
    for label, factor in SCALES.items():
        cycles = window_end(factor)
        started = time.time()
        ctx, obs = window_pairs(cell["events"], cycles)
        org = arm_pair_losses(cell["org"], ctx, obs, cell["vocab"])
        base = arm_pair_losses(cell["baseline"]["prob"], ctx, obs, cell["vocab"])
        if len(org) != len(base):
            raise AssertionError("the two arms scored a different number of pairs")
        # Positive = the readout's loss is lower than the comparator's.
        deltas = [b - o for o, b in zip(org, base)]
        if label == "1x":
            # The endpoint must be the frozen one: per-pair means average to the
            # aggregate the study reports, or this ladder measures something else.
            aggregate = fs.score(cell["org"], ctx, obs, cell["vocab"])["log_loss"]
            if abs(mean(org) - aggregate) > 1e-9:
                raise AssertionError(
                    f"per-pair scoring disagrees with the frozen endpoint "
                    f"({mean(org)!r} vs {aggregate!r})")
        stats = block_stats(deltas)
        stats.update({
            "cycles": cycles, "pairs": len(deltas),
            "delta": round(mean(deltas), 9),
            "spread_cycles": [PHASE_TRANSFER[0], cycles],
            "score_seconds": round(time.time() - started, 1),
        })
        out["scales"][label] = stats
    return out


# ---------------------------------------------------------------------------
# The decomposition and the decision
# ---------------------------------------------------------------------------

def summarise(per_seed: Sequence[dict]) -> dict[str, Any]:
    """Per scale: the distribution of deltas, and within-versus-between error."""
    out: dict[str, Any] = {}
    for label in SCALES:
        rows = [cell["scales"][label] for cell in per_seed]
        deltas = [r["delta"] for r in rows]
        se_block = [r["se_block"] for r in rows if r["se_block"] is not None]
        se_iid = [r["se_iid"] for r in rows if r["se_iid"] is not None]
        between = stdev(deltas) if len(deltas) > 1 else None
        within = mean(se_block) if se_block else None
        quarters = [q for r in rows for q in r["quarters"]]
        out[label] = {
            "cycles": rows[0]["cycles"],
            "pairs": rows[0]["pairs"],
            "runs": len(deltas),
            "delta_mean": round(mean(deltas), 9),
            "delta_sd_between": None if between is None else round(between, 9),
            "delta_min": round(min(deltas), 9),
            "delta_max": round(max(deltas), 9),
            "within_se_block_mean": None if within is None else round(within, 9),
            "within_se_iid_mean": (round(mean(se_iid), 9) if se_iid else None),
            "rho": (round(within / between, 6)
                    if within is not None and between else None),
            "block_over_iid_mean": (round(mean([r["block_over_iid"] for r in rows
                                               if r["block_over_iid"] is not None]), 4)
                                    if any(r["block_over_iid"] is not None for r in rows)
                                    else None),
            "runs_positive": sum(1 for d in deltas if d > 0),
            "quarters_positive": sum(1 for q in quarters if q > 0),
            "quarters": len(quarters),
            "pooled_effect_over_within": (round(mean(deltas) / within, 3)
                                          if within else None),
        }
    return out


def slope_of(summary: dict[str, Any]) -> dict[str, Any]:
    """The scaling curve: log(within-run SE) against log(pairs).

    An exponent of -0.5 means the observations behave like independent draws: to
    halve the error you need four times as many. Shallow means clustering; steep
    means a small number of observations was carrying the estimate.
    """
    xs = [math.log(summary[label]["pairs"]) for label in SCALES]
    ys = [math.log(summary[label]["within_se_block_mean"]) for label in SCALES]
    n = len(xs)
    mx, my = mean(xs), mean(ys)
    denom = sum((x - mx) ** 2 for x in xs)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / denom if denom else None
    fitted = [my + slope * (x - mx) for x in xs]
    ss_res = sum((y - f) ** 2 for y, f in zip(ys, fitted))
    ss_tot = sum((y - my) ** 2 for y in ys)
    return {
        "exponent": round(slope, 4) if slope is not None else None,
        "expected": EXPECTED_SLOPE,
        "band": SLOPE_BAND,
        "within_band": (slope is not None and abs(slope - EXPECTED_SLOPE) <= SLOPE_BAND),
        "r_squared": round(1 - ss_res / ss_tot, 4) if ss_tot else None,
        "points": [{"pairs": summary[label]["pairs"],
                    "se": summary[label]["within_se_block_mean"]} for label in SCALES],
    }


def runs_for_precision(between: float | None, within: float | None,
                       target_fraction: float = 0.5) -> float | None:
    """How many independent runs put the total error at `target_fraction` of the between-SD.

    Total error at n runs is `sqrt(between^2/n + within^2)`. Once the within-run
    term alone is at or above the target there is no n that reaches it, and that
    is reported as not achievable rather than as a large number.
    """
    if not between or within is None:
        return None
    target = between * target_fraction
    if within >= target:
        return None
    return round(between ** 2 / (target ** 2 - within ** 2), 2)


def decide(summary: dict[str, Any]) -> dict[str, Any]:
    """§5 applied once, at the baseline scale, with the trend reported beside it."""
    base = summary["1x"]
    rho = base["rho"]
    label = verdict(rho)
    if label == "replication-limited":
        text = (
            "At the design's own window the within-run standard error is at most "
            "half the between-run spread, so a longer scored window cannot be what "
            "is limiting the estimates: repeating the run is.")
    elif label == "resolution-limited":
        text = (
            "At the design's own window the within-run standard error is at least "
            "the between-run spread, so one run does not resolve its own estimate: "
            "observing more per run is the constraint.")
    elif label == "both":
        text = (
            "At the design's own window the two sources are within a factor of two "
            "of each other, so neither dominates: the ladder's slope says which "
            "direction buys more.")
    else:
        text = "rho is not measurable at the baseline scale; no verdict is formed."
    return {
        "scale": "1x",
        "rho": rho,
        "label": label,
        "text": text,
        "rule": {
            "rho_replicate_at_or_below": RHO_REPLICATE,
            "rho_resolution_at_or_above": RHO_RESOLUTION,
            "rho_definition": "mean within-run block-bootstrap SE / between-run SD of the delta",
        },
    }


# ---------------------------------------------------------------------------
# Derived after the run: does a run identify its own sign? (docs §8)
# ---------------------------------------------------------------------------

def sign_probability(theta: float, se: float) -> float:
    """P(a run whose estimate is N(theta, se^2) lands on theta's side of zero).

    `se` is the run's own standard error, so this is what the owner's SE/delta
    ratio is a crude proxy for. The ratio is a t-statistic, not a probability:
    a ratio of 1 is 0.84, not a coin flip, and a ratio of 1.57 is still 0.74.
    """
    if se is None:
        return 0.0
    if se <= 0.0:
        return 0.5 if theta == 0 else 1.0
    return NormalDist(0, 1).cdf(abs(theta) / se)


#: How the "true effect" of a world is estimated. `leave_one_out` is the rule
#: §8 used; the others exist so the sensitivity of the number to it is measured
#: rather than assumed (§9). A judged scale is never its own reference.
REFERENCE_RULES = ("leave_one_out", "fixed_8x", "fixed_4x")


def reference_label(label: str, rule: str = "leave_one_out") -> str:
    """Which scale estimates the truth for `label` under a reference rule."""
    if rule == "leave_one_out":
        return _reference_scale(label)
    if rule not in REFERENCE_RULES:
        raise SystemExit(f"unknown reference rule {rule!r}; known: {REFERENCE_RULES}")
    ref = rule.split("_", 1)[1]
    if ref not in SCALES:
        raise SystemExit(f"reference rule {rule!r} names a scale that does not exist")
    return _reference_scale(label) if ref == label else ref


def _reference_scale(label: str) -> str:
    """The widest scale other than the one being judged.

    Judging a cell against the same cell's estimate would manufacture the answer
    at the widest window, where truth and estimate share their noise. For `16x`
    the reference is therefore `8x`, which is noisier and makes that row the
    conservative one rather than the flattering one.
    """
    order = [other for other in SCALES if other != label]
    if not order:
        raise AssertionError("a single scale cannot provide its own reference")
    return order[-1]


def sign_resolution(per_seed: Sequence[dict], target: float = SIGN_TARGET,
                    replicates: int = SIGN_REPLICATES,
                    seed: int = SIGN_RESEED,
                    reference_rule: str = "leave_one_out") -> dict[str, Any]:
    """How often one run reports the sign of its own world's underlying effect.

    Two uncertainties are propagated, because both are real and only one of them
    scales with the window: the run's estimate of its world (`se_block` at that
    scale), and what that world's true effect *is* (the reference scale's delta
    and its own `se_block`). Treating the second as known is what makes a
    plug-in `sign_probability(delta, se)` optimistic; `plugin_mean` is reported
    beside the propagated number so the size of that optimism is visible rather
    than argued about.

    `p_pooled_sign` asks the different question a study actually needs: does the
    run agree with what the whole block says, not with its own world?
    """
    if not per_seed:
        raise AssertionError("no worlds: the sign question has no data")
    labels = list(SCALES)
    worlds = []
    for cell in per_seed:
        worlds.append({
            "seed": cell["seed"],
            "cells": {l: (cell["scales"][l]["delta"], cell["scales"][l]["se_block"])
                      for l in labels},
            "references": {l: (cell["scales"][reference_label(l, reference_rule)]["delta"],
                               cell["scales"][reference_label(l, reference_rule)]["se_block"])
                           for l in labels},
        })

    rng = random.Random(seed)
    hits = {l: 0 for l in labels}
    pooled = {l: 0 for l in labels}
    by_world = {w["seed"]: {l: 0 for l in labels} for w in worlds}
    for _ in range(replicates):
        thetas = []
        for w in worlds:
            drawn = {}
            for l in labels:
                mu, sd = w["references"][l]
                drawn[l] = rng.gauss(mu, sd) if sd else mu
            thetas.append(drawn)
        # What the block as a whole says, from the same draws.
        bar = {l: mean(t[l] for t in thetas) for l in labels}
        for w, theta in zip(worlds, thetas):
            for l in labels:
                _, se = w["cells"][l]
                if not se:
                    continue
                estimate = rng.gauss(theta[l], se)
                agree = (estimate > 0) == (theta[l] > 0)
                hits[l] += agree
                by_world[w["seed"]][l] += agree
                pooled[l] += (estimate > 0) == (bar[l] > 0)

    total = replicates * len(worlds)
    scales: dict[str, Any] = {}
    for l in labels:
        rates = sorted(by_world[w["seed"]][l] / replicates for w in worlds)
        deltas = [w["cells"][l][0] for w in worlds]
        errors = [w["cells"][l][1] for w in worlds]
        plug = [sign_probability(d, s) for d, s in zip(deltas, errors)]
        scales[l] = {
            "cycles": window_end(SCALES[l]),
            "p_correct": round(hits[l] / total, 4),
            "p_correct_min": round(rates[0], 4),
            "p_correct_max": round(rates[-1], 4),
            "worlds_at_target": sum(1 for r in rates if r >= target),
            "runs": len(worlds),
            "p_pooled_sign": round(pooled[l] / total, 4),
            "plugin_mean": round(mean(plug), 4),
            "phi_of_pooled_ratio": round(
                sign_probability(mean(deltas), mean(errors)), 4),
        }

    rows = []
    for w in worlds:
        p = {l: round(by_world[w["seed"]][l] / replicates, 4) for l in labels}
        reached = [l for l in labels if p[l] >= target]
        rows.append({
            "seed": w["seed"],
            "p_by_scale": p,
            "window_for_target": reached[0] if reached else None,
            "reference_at_widest": reference_label(labels[-1], reference_rule),
        })

    return {
        "kind": "derived after the run; a re-analysis of the same five worlds",
        "question": "Would one run at each window report the sign of its own world's effect?",
        "target": target,
        "replicates": replicates,
        "reseed": seed,
        "reference_rule": reference_rule,
        "reference_note": ("the truth for a cell is estimated from another window of the "
                           "same world and propagated with that window's own standard "
                           "error, so no cell is judged against its own estimate"),
        "scales": scales,
        "worlds": rows,
        "all_worlds_at_target_from": next(
            (l for l in labels if scales[l]["worlds_at_target"] == len(worlds)), None),
        "any_world_at_target_from": next(
            (l for l in labels if scales[l]["worlds_at_target"] > 3), None),
    }


# ---------------------------------------------------------------------------
# Audit of the sign estimator (docs §9): nesting, reference rule, calibration
# ---------------------------------------------------------------------------

#: The measured block-bootstrap SEs of the 2026-11-02 run, so the calibration sits
#: in the same regime as the ladder. `audit_sign_estimator` asserts they match.
SIGN_CALIBRATION_SE = {"1x": 0.008830, "2x": 0.003804, "4x": 0.003265,
                       "8x": 0.002578, "16x": 0.001450}
CALIBRATION_EFFECTS = (0.0, 0.25, 0.5, 1.0, 2.0, 4.0)   # |effect| / se(1x); 0 is
#: excluded below, because a zero effect has no sign to report.
CALIBRATION_WORLDS = 20
CALIBRATION_RUNS = 2_000
CALIBRATION_REPLICATES = 400
CALIBRATION_SEED = 20270507
SIGN_AUDIT_OUT = "docs/sign_audit.json"


def nested_overlap(summary: dict[str, Any]) -> dict[str, Any]:
    """How much of each reference window is the window it judges.

    The scored windows start at the same cycle, so the shorter is contained in the
    longer. Under independent pairs this fixes the covariance exactly: for a subset
    mean and a superset mean with the same per-pair variance, `Cov = V_superset`, so
    the correlation is `sqrt(overlap)`. It is reported because a reader is entitled
    to know how dependent the reference is on the data it judges.
    """
    out: dict[str, Any] = {}
    for label in SCALES:
        ref = reference_label(label, "leave_one_out")
        n_s = summary[label]["pairs"]
        n_r = summary[ref]["pairs"]
        v_s = summary[label]["within_se_block_mean"] ** 2
        v_r = summary[ref]["within_se_block_mean"] ** 2
        # Both windows start at the same cycle, so one contains the other and the
        # union is the longer of them. Under independent pairs the covariance is the
        # variance of that longer window -- the *smaller* of the two -- which caps the
        # correlation at 1 by construction. The first version divided by the judged
        # window's variance unconditionally and returned 1.78 at 16x, where the judged
        # window is the longer one; an impossible correlation is a bug, not a finding.
        v_long, v_short = max(v_s, v_r), min(v_s, v_r)
        covariance = v_short
        conditional = math.sqrt(max(v_s - covariance ** 2 / v_r, 0.0))
        out[label] = {
            "judged": label,
            "reference": ref,
            "judged_pairs": n_s,
            "reference_pairs": n_r,
            "judged_contains_reference": n_s > n_r,
            "overlap_of_smaller_in_larger": round(min(n_s, n_r) / max(n_s, n_r), 4),
            "correlation_if_independent_pairs": round(math.sqrt(v_short / v_long), 4),
            "conditional_sd_given_reference": round(conditional, 9),
            "sd_if_independent_propagation": round(math.sqrt(v_s + v_r), 9),
            "variance_inflation_if_ignored": round(
                (v_s + v_r) / max(v_s - covariance ** 2 / v_r, 1e-18), 4),
        }
    return out


def calibrate_sign_estimator(effects: Sequence[float] = CALIBRATION_EFFECTS,
                             worlds: int = CALIBRATION_WORLDS,
                             runs: int = CALIBRATION_RUNS,
                             replicates: int = CALIBRATION_REPLICATES,
                             seed: int = CALIBRATION_SEED) -> dict[str, Any]:
    """Known-truth check: does the reported probability match the frequency?

    Each simulated world has a fixed true effect. Its reference cell is that effect
    plus the reference window's own error, exactly as the ladder's cells are, and a
    fresh run is then drawn from the truth. The frequency with which it reports the
    right sign is what the probability is supposed to predict, so the difference
    between them is the calibration error — positive means optimistic.
    """
    rng = random.Random(seed)
    rows = []
    for effect in effects:
        theta = effect * SIGN_CALIBRATION_SE["1x"]
        cells = []
        for w in range(worlds):
            cells.append({"seed": w, "scales": {
                l: {"delta": rng.gauss(theta, SIGN_CALIBRATION_SE[reference_label(l)]),
                    "se_block": SIGN_CALIBRATION_SE[l]} for l in SCALES}})
        reported = sign_resolution(cells, replicates=replicates, seed=seed + 1)
        for l in SCALES:
            hits = sum(1 for _ in range(runs)
                       if (rng.gauss(theta, SIGN_CALIBRATION_SE[l]) > 0) == (theta > 0))
            rows.append({
                "effect_over_se_1x": effect,
                "scale": l,
                "reported": reported["scales"][l]["p_correct"],
                "realised_frequency": round(hits / runs, 4),
                "exact_frequency": round(sign_probability(theta, SIGN_CALIBRATION_SE[l]), 4),
                "sign_undefined": effect == 0.0,
                "calibration_error": round(reported["scales"][l]["p_correct"] - hits / runs, 4),
            })
    return {
        "worlds_per_effect": worlds,
        "runs_per_cell": runs,
        "replicates": replicates,
        "se_assumed": dict(SIGN_CALIBRATION_SE),
        "rows": rows,
        # A zero effect has no sign, so agreement there is not measurable: those cells
        # are reported and excluded rather than scored as a large error (AGENTS 13b).
        "excluded_zero_effect": sum(1 for r in rows if r["sign_undefined"]),
        "max_abs_calibration_error": max(
            (abs(r["calibration_error"]) for r in rows if not r["sign_undefined"]),
            default=0.0),
        "note": ("rows with sign_undefined=True have no true sign and are excluded from "
                 "the error; they are kept because their failure mode is informative -- "
                 "a reference can look precise against a run's own error while the truth "
                 "has no direction to report."),
    }


def audit_sign_estimator(per_seed: Sequence[dict], summary: dict[str, Any]) -> dict[str, Any]:
    """The five checks §9 asks for, on the stored cells. No engine, no seed."""
    for label, se in SIGN_CALIBRATION_SE.items():
        if abs(summary[label]["within_se_block_mean"] - se) > 5e-6:
            raise AssertionError(
                f"the calibration regime does not match the artifact at {label}: "
                f"{summary[label]['within_se_block_mean']!r} vs {se!r}")

    nesting = nested_overlap(summary)
    default = sign_resolution(per_seed, replicates=8_000)
    rules = {}
    for rule in REFERENCE_RULES:
        r = sign_resolution(per_seed, replicates=8_000, reference_rule=rule)
        rules[rule] = {
            "scales": {l: {"p_correct": r["scales"][l]["p_correct"],
                           "p_correct_min": r["scales"][l]["p_correct_min"],
                           "worlds_at_target": r["scales"][l]["worlds_at_target"]}
                       for l in SCALES},
            "all_worlds_at_target_from": r["all_worlds_at_target_from"],
        }
    thresholds = {f"{t:.2f}": {l: sum(1 for w in default["worlds"]
                                       if w["p_by_scale"][l] >= t) for l in SCALES}
                  for t in (0.80, 0.85, 0.90, 0.95)}
    worlds = [{"seed": cell["seed"],
               "effect_over_se_1x": round(abs(cell["scales"]["1x"]["delta"])
                                          / cell["scales"]["1x"]["se_block"], 3),
               "effect_over_se_16x": round(abs(cell["scales"]["16x"]["delta"])
                                           / cell["scales"]["16x"]["se_block"], 3)}
              for cell in per_seed]
    calibration = calibrate_sign_estimator()
    lo = min(w["effect_over_se_16x"] for w in worlds)
    hi = max(w["effect_over_se_16x"] for w in worlds)
    small = [r for r in calibration["rows"] if r["effect_over_se_1x"] <= 0.5]
    large = [r for r in calibration["rows"] if r["effect_over_se_1x"] >= 2.0]
    return {
        "kind": "audit of the sign-resolution estimator",
        "subject": "docs/scaling_ladder.json, the same five worlds; no engine run, no seed",
        "nesting": nesting,
        "reference_sensitivity": rules,
        "threshold_sensitivity_worlds_at_target": thresholds,
        "worlds": worlds,
        "calibration": calibration,
        "findings": [
            (f"The judged window and its reference overlap: the smaller holds "
             f"{nesting['2x']['overlap_of_smaller_in_larger']:.1%} of the larger at 2x "
             f"and {nesting['16x']['overlap_of_smaller_in_larger']:.1%} at 16x, a "
             f"correlation of {nesting['2x']['correlation_if_independent_pairs']:.2f} "
             f"and {nesting['16x']['correlation_if_independent_pairs']:.2f} if pairs "
             "were independent. At 16x the judged window is the longer one, so the "
             "containment runs the other way. That covariance does not enter the "
             "reported probability - conditional on a world's effect a run's own error "
             "stands apart from the reference, and the reference's likelihood depends "
             "only on its own standard error - but it does make the five rows dependent "
             "comparisons, so the curve cannot be read as a monotone dose-response "
             "across them."),
            (f"The reference's precision moves the decision: at 2x the probability is "
             f"{rules['leave_one_out']['scales']['2x']['p_correct']:.3f} with the "
             f"leave-one-out reference "
             f"({rules['leave_one_out']['scales']['2x']['worlds_at_target']}/5 worlds at "
             f"target), {rules['fixed_8x']['scales']['2x']['p_correct']:.3f} with a fixed "
             f"8x reference ({rules['fixed_8x']['scales']['2x']['worlds_at_target']}/5) "
             f"and {rules['fixed_4x']['scales']['2x']['p_correct']:.3f} with a fixed 4x "
             f"reference ({rules['fixed_4x']['scales']['2x']['worlds_at_target']}/5). "
             "'Every world clears 0.90 at 100 cycles' holds only against the most precise "
             "reference available; with a noisier one it is three worlds of five. That is "
             "a condition on the claim, not a detail."),
            (f"Against known truths the worst error is "
             f"{calibration['max_abs_calibration_error']:.3f} over effects of "
             f"{min(r['effect_over_se_1x'] for r in calibration['rows'] if not r['sign_undefined']):.2f}"
             f"-{max(r['effect_over_se_1x'] for r in calibration['rows']):.2f} SE(1x), and it runs "
             "conservative for resolved effects rather than optimistic: the estimator "
             "under-reports as often as it over-reports, and by less than the spread it "
             "is trying to describe. At an exactly zero effect the sign is undefined, so "
             "those cells are excluded from the error rather than scored."),
            (f"The target is a convention and the window it selects moves with it: at 1x "
             f"{thresholds['0.80']['1x']}/5 worlds clear 0.80, "
             f"{thresholds['0.90']['1x']}/5 clear 0.90 and {thresholds['0.95']['1x']}/5 "
             f"clear 0.95; at 2x the counts are {thresholds['0.80']['2x']}/5, "
             f"{thresholds['0.90']['2x']}/5 and {thresholds['0.95']['2x']}/5."),
            ("Taken together: the nesting does not bias the probability the estimator "
             "reports, its error against known truth is small, and both the reference "
             "rule and the target move the decision. 100 cycles is a provisional "
             "resolution target under a declared reference rule and a declared "
             "threshold, not a validated minimum."),
        ],
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

CAVEATS = (
    "The world is held at LAW_R0 for the whole run (regime_cycles = cycles), "
    "because the readout is formed under that law and a rotation inside the "
    "scored window would change the generating process partway through a run. "
    "The frozen design's default world rotates at REGIME_SWITCH_CYCLE; the "
    "ladder's 1x cell is therefore not the frozen world's 150-200 window.",
    "The intervention is the scored window at fixed exposure (110 formation "
    "cycles). A longer exposure is a different intervention and is not measured.",
    "The between-run SD rests on five worlds. It is an estimate of that spread, "
    "not its population value, and rho inherits its error.",
    "The endpoint is one comparator family, chosen by tuning loss as in the "
    "frozen studies. A different baseline family would move the delta, and the "
    "decomposition is about this contrast.",
    "Within-run variability is measured by resampling contiguous quarters of one "
    "world; it measures sampling error inside a run, not how a different world "
    "would have differed.",
)


def run(seeds: Sequence[int] = SEEDS) -> dict[str, Any]:
    started = time.time()
    per_seed = []
    checked = prefix_check(seeds[0])
    for seed in seeds:
        cell = measure(seed)
        per_seed.append(cell)
        print(f"  seed {seed}: " + ", ".join(
            f"{label} d={cell['scales'][label]['delta']:+.6f} "
            f"se={cell['scales'][label]['se_block']:.6f}"
            for label in SCALES), flush=True)
    summary = summarise(per_seed)
    sign = sign_resolution(per_seed)
    art = {
        "kind": "scaling_ladder",
        "question": ("Is a run scored on too little of the world to establish what "
                     "it is doing, or is it repeated too few times to establish that "
                     "the behaviour is real?"),
        "measured": [
            "the paired endpoint (readout minus strongest simple comparator) per event pair",
            "within-run standard error from a cluster bootstrap over contiguous quarters",
            "between-run standard deviation of the same delta across five worlds",
            "consistency of the delta across quarters of one run",
            "wall time and pairs scored, per scale",
        ],
        "not_measured": [
            "any comparison of a delta with a study bar, and any direction for Organica",
            "the effect of a longer formation exposure",
            "any seed from a study's design or confirmatory block",
        ],
        "design": {
            "seeds": list(seeds),
            "methodology_block": list(SEEDS),
            "formation_cycles": 110,
            "cap": CAP,
            "alpha": ALPHA,
            "base_window": list(PHASE_TRANSFER),
            "scales": SCALES,
            "blocks": BLOCKS,
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "law": "LAW_R0 throughout",
        },
        "prefix_check": checked,
        "rule": decide(summary)["rule"],
        "per_seed": per_seed,
        "summary": summary,
        "slope": slope_of(summary),
        "verdict": decide(summary),
        "sign_resolution": sign,
        "runs_for_half_between_sd": runs_for_precision(
            summary["1x"]["delta_sd_between"], summary["1x"]["within_se_block_mean"]),
        "caveats": list(CAVEATS),
        "confirms_seeds_touched": False,
        "complete": tuple(seeds) == SEEDS,
        "runtime_seconds": round(time.time() - started, 1),
    }
    return art


def write(art: dict[str, Any], out: str = OUT) -> pathlib.Path:
    path = ROOT / out
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(engine_stamp.stamp(art), indent=2) + "\n", encoding="utf-8")
    return path


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seeds", type=int, nargs="*", default=None,
                        help="subset for a resumable run; the artifact is marked incomplete")
    parser.add_argument("--out", default=OUT)
    parser.add_argument("--reanalyse", action="store_true",
                        help="recompute the derived §8 analysis from an existing artifact")
    parser.add_argument("--audit", action="store_true",
                        help="audit the sign estimator on the stored cells (docs §9)")
    args = parser.parse_args(argv)
    if args.reanalyse:
        path = ROOT / args.out
        if not path.exists():
            raise SystemExit(f"{args.out} does not exist; run the ladder first")
        art = json.loads(path.read_text(encoding="utf-8"))
        art["sign_resolution"] = sign_resolution(art["per_seed"])
        write(art, args.out)
        s = art["sign_resolution"]
        print(f"wrote {args.out} ({s['kind']})")
        for label in SCALES:
            row = s["scales"][label]
            print(f"  {label:>3}  p={row['p_correct']:.3f}  min={row['p_correct_min']:.3f}  "
                  f"max={row['p_correct_max']:.3f}  at_target={row['worlds_at_target']}/"
                  f"{row['runs']}  pooled={row['p_pooled_sign']:.3f}  "
                  f"plugin={row['plugin_mean']:.3f}  "
                  f"phi(pooled ratio)={row['phi_of_pooled_ratio']:.3f}")
        print(f"  all worlds at {s['target']:.2f}: {s['all_worlds_at_target_from']}")
        for w in s["worlds"]:
            print(f"    {w['seed']}: "
                  + ", ".join(f"{k}={v:.2f}" for k, v in w["p_by_scale"].items())
                  + f"  -> {w['window_for_target']}")
        return 0
    if args.audit:
        path = ROOT / args.out
        if not path.exists():
            raise SystemExit(f"{args.out} does not exist; run the ladder first")
        art = json.loads(path.read_text(encoding="utf-8"))
        audit = audit_sign_estimator(art["per_seed"], art["summary"])
        out = write(audit, SIGN_AUDIT_OUT)
        print(f"wrote {out.relative_to(ROOT).as_posix()}")
        for f in audit["findings"]:
            print(f"  - {f}")
        print("  nesting (overlap of judged window in its reference):")
        for label, row in audit["nesting"].items():
            print(f"    {label:>3} judged {row['judged_pairs']:>5} vs reference "
                  f"{row['reference_pairs']:>5} ({row['reference']}): overlap "
                  f"{row['overlap_of_smaller_in_larger']:.1%}, corr "
                  f"{row['correlation_if_independent_pairs']:.3f}"
                  + ("  [judged is the longer window]"
                     if row["judged_contains_reference"] else ""))
        print("  reference rule -> p at 2x / 4x / 16x, worlds at target:")
        for rule, r in audit["reference_sensitivity"].items():
            print(f"    {rule:<16} " + "  ".join(
                f"{l}={r['scales'][l]['p_correct']:.3f}({r['scales'][l]['worlds_at_target']}/5)"
                for l in ("2x", "4x", "16x")))
        print("  threshold -> worlds at target by scale:")
        for t, row in audit["threshold_sensitivity_worlds_at_target"].items():
            print(f"    {t}: " + "  ".join(f"{l}={row[l]}/5" for l in SCALES))
        print("  calibration (effect/SE_1x, scale, reported, realised, error):")
        for r in audit["calibration"]["rows"]:
            if r["scale"] in ("1x", "16x"):
                print(f"    {r['effect_over_se_1x']:>3.1f} {r['scale']:>3} "
                      f"rep={r['reported']:.3f} real={r['realised_frequency']:.3f} "
                      f"err={r['calibration_error']:+.3f}")
        return 0
    seeds = tuple(args.seeds) if args.seeds else SEEDS
    for seed in seeds:
        refuse_study_seed(seed)
    art = run(seeds)
    path = write(art, args.out)
    s = art["summary"]
    print(f"wrote {path.relative_to(ROOT).as_posix()}")
    for label in SCALES:
        row = s[label]
        print(f"  {label:>3}  pairs={row['pairs']:>5}  delta={row['delta_mean']:+.6f}  "
              f"within={row['within_se_block_mean']:.6f}  between={row['delta_sd_between']:.6f}  "
              f"rho={row['rho']}")
    print(f"  slope={art['slope']['exponent']} (expected {EXPECTED_SLOPE} ± {SLOPE_BAND}, "
          f"within band: {art['slope']['within_band']})")
    print(f"  verdict at 1x: {art['verdict']['label']} (rho={art['verdict']['rho']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
