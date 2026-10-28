"""The strong count-based baselines, and the gap test that must match the claim.

The complaint this answers (2026-10-27): the endpoint probe's 0.05-nat
headroom check compared the ceiling against a **base-rate** predictor, so
the probe could pass while the benchmark left no room to show an
advantage over transition counting.  The headroom must be measured against
the **best simple baseline**, and the baseline must be swept over a
declared grid with its best configuration used (AGENTS rule 11 — a baseline
may never be handicapped).

Baselines
---------

* **base rate** — the marginal frequency of each tag.
* **bigram** — a first-order tag-transition table with Beta(alpha, alpha)
  smoothing.
* **decayed bigram** — the same, with recency decay over a half-life.
* **cell-level counter (latent-state baseline)** — the same table but
  aggregated over the cells, i.e. a learner that has inferred the latent
  cell structure and counts transitions between cells.  This is the
  strongest count-based baseline available, and it is the one that matters:
  if even it reaches the ceiling, no count-based learner will, and the
  benchmark has no room.

The gap test
------------

On the PRIMARY test split, the gap between the Bayes ceiling and the best
simple baseline is measured across INDEPENDENT WORLDS, and the **lower
uncertainty bound** of that gap must clear 0.05 nats before the benchmark
is called discriminative.  A point estimate is not enough: a benchmark that
is discriminative on the seed that was looked at is not discriminative.

The positive control (a learner holding the generating rule) must reach the
ceiling; the broken-rule control must be clearly worse.

Read-only.  No engine run.  Standard library only.
"""
from __future__ import annotations

import math
import random
from collections import defaultdict

EPS = 1e-12


# ---------------------------------------------------------------------------
# Scoring helper
# ---------------------------------------------------------------------------

def score(prob, contexts, observations, vocabulary, exclude_self=True) -> dict:
    """The house pairwise log-loss, plus Brier.

    `exclude_self` reproduces the house `_score` shape, which skips the
    cell where target == source.  The alternative is measured and reported
    separately, because the house shape was found to shield the baseline on
    the transition world.
    """
    ll = brier = n = 0.0
    for ctx, obs in zip(contexts, observations):
        truth = set(obs) & vocabulary
        for source in ctx:
            for target in vocabulary:
                p = min(1 - EPS, max(EPS, prob(source, target)))
                y = int(target in truth)
                if exclude_self:
                    y = int(target in truth and target != source)
                ll -= y * math.log(p) + (1 - y) * math.log1p(-p)
                brier += (p - y) ** 2
                n += 1
    return {"log_loss": round(ll / n, 6), "brier": round(brier / n, 6)}


# ---------------------------------------------------------------------------
# Baselines
# ---------------------------------------------------------------------------

def fit_base_rate(rows, vocab):
    cnt = defaultdict(int)
    for r in rows:
        for t in r.split():
            cnt[t] += 1
    tot = sum(cnt.values()) or 1
    base = {t: n / tot for t, n in cnt.items()}
    return lambda u, v: base.get(v, 0.0)


def fit_bigram(rows, vocab, alpha=0.5, half_life=None, decay_window=None):
    """First-order tag transition table.

    `half_life` applies recency decay to each transition.  `decay_window`
    restricts the table to the last N rows.
    """
    use = rows if decay_window is None else rows[-decay_window:]
    n = len(use)
    cnt = defaultdict(lambda: defaultdict(float))
    for i in range(1, n):
        w = 1.0
        if half_life:
            w = 0.5 ** ((n - i) / half_life)
        for a in use[i - 1].split():
            for b in use[i].split():
                cnt[a][b] += w
    def p(u, v):
        row = cnt.get(u, {})
        t = sum(row.values())
        if t <= 0:
            return 1.0 / len(vocab)
        return (row.get(v, 0.0) + alpha) / (t + alpha * len(vocab))
    return p


def fit_cell_counter(rows, vocab, tag_to_cell, alpha=0.5, half_life=None,
                     decay_window=None):
    """The latent-state baseline: transitions counted over CELLS.

    This is the strongest count-based baseline: a learner that has inferred
    the cell structure (here granted, because the point is to test whether
    counting alone suffices) and counts cell-to-cell transitions.
    """
    use = rows if decay_window is None else rows[-decay_window:]
    n = len(use)
    cell_of = {t: c for t, c in tag_to_cell.items()}
    members = defaultdict(list)
    for t, c in tag_to_cell.items():
        members[c].append(t)
    cnt = defaultdict(lambda: defaultdict(float))
    for i in range(1, n):
        w = 1.0
        if half_life:
            w = 0.5 ** ((n - i) / half_life)
        src = [cell_of.get(t) for t in use[i - 1].split() if t in cell_of]
        dst = [cell_of.get(t) for t in use[i].split() if t in cell_of]
        for a in src:
            for b in dst:
                cnt[a][b] += w
    def p(u, v):
        sc = tag_to_cell.get(u)
        tc = tag_to_cell.get(v)
        if sc is None or tc is None:
            return 1.0 / len(vocab)
        row = cnt.get(sc, {})
        t = sum(row.values())
        if t <= 0:
            return 1.0 / len(vocab)
        p_next = (row.get(tc, 0.0) + alpha) / (t + alpha * len(set(tag_to_cell.values())))
        share = 1.0 / len(members[tc]) if members[tc] else 0.0
        return p_next * share
    return p


# The declared grid.  Every baseline is swept over it and its BEST
# configuration is used, selected on the TUNING SPLIT only.
BIGRAM_GRID = [
    (alpha, half_life, window)
    for alpha in (0.1, 0.5, 1.0)
    for half_life in (None, 25, 50, 100)
    for window in (None, 200, 400, 800)
]
CELL_GRID = [
    (alpha, half_life, window)
    for alpha in (0.1, 0.5, 1.0)
    for half_life in (None, 25, 50, 100)
    for window in (None, 200, 400, 800)
]


def select_best(kind, rows, vocab, tag_to_cell, tune_ctx, tune_obs,
                 exclude_self=True):
    """Select a baseline's configuration on the TUNING SPLIT."""
    best = None
    for alpha, half_life, window in (BIGRAM_GRID if kind == "bigram"
                                     else CELL_GRID):
        if kind == "bigram":
            p = fit_bigram(rows, vocab, alpha, half_life, window)
        else:
            p = fit_cell_counter(rows, vocab, tag_to_cell, alpha, half_life,
                                 window)
        s = score(p, tune_ctx, tune_obs, vocab, exclude_self)
        if best is None or s["log_loss"] < best[0]:
            best = (s["log_loss"], (alpha, half_life, window), p)
    return best


# ---------------------------------------------------------------------------
# The gap test
# ---------------------------------------------------------------------------

def bootstrap_lower_bound(gaps, reps=10000, seed=20261101, alpha=0.99):
    """The lower uncertainty bound of the mean gap, by resampling WORLDS.

    The worlds are the independent units, so the bootstrap resamples worlds
    (not cells, not events).  A point estimate is not enough: a benchmark
    that is discriminative on the worlds that were looked at is not
    discriminative.
    """
    if not gaps:
        return 0.0, 0.0, 0.0
    rng = random.Random(seed)
    m = len(gaps)
    means = []
    for _ in range(reps):
        s = 0.0
        for _ in range(m):
            s += gaps[rng.randrange(m)]
        means.append(s / m)
    means.sort()
    lo_idx = int((1 - alpha) / 2 * reps)
    hi_idx = min(reps - 1, int((1 + alpha) / 2 * reps))
    mean = sum(gaps) / m
    return round(mean, 6), round(means[lo_idx], 6), round(means[hi_idx], 6)
