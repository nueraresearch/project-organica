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
                    seed: int = SIGN_RESEED) -> dict[str, Any]:
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
            "references": {l: (cell["scales"][_reference_scale(l)]["delta"],
                               cell["scales"][_reference_scale(l)]["se_block"])
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
            "reference_at_widest": _reference_scale(labels[-1]),
        })

    return {
        "kind": "derived after the run; a re-analysis of the same five worlds",
        "question": "Would one run at each window report the sign of its own world's effect?",
        "target": target,
        "replicates": replicates,
        "reseed": seed,
        "reference_rule": ("the widest scale other than the one judged, propagated with "
                           "that scale's own standard error, so no cell is judged "
                           "against its own estimate"),
        "scales": scales,
        "worlds": rows,
        "all_worlds_at_target_from": next(
            (l for l in labels if scales[l]["worlds_at_target"] == len(worlds)), None),
        "any_world_at_target_from": next(
            (l for l in labels if scales[l]["worlds_at_target"] > 3), None),
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
    path.write_text(json.dumps(art, indent=2) + "\n", encoding="utf-8")
    return path


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seeds", type=int, nargs="*", default=None,
                        help="subset for a resumable run; the artifact is marked incomplete")
    parser.add_argument("--out", default=OUT)
    parser.add_argument("--reanalyse", action="store_true",
                        help="recompute the derived §8 analysis from an existing artifact")
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
    seeds = tuple(args.seeds) if args.seeds else SEEDS
    for seed in seeds:
        refuse_study_seed(seed)
    art = run(seeds)
    path = write(art, args.out)
    s = art["summary"]
    print(f"wrote {path.relative_to(ROOT)}")
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
