"""The Stage B block ladder, checked with the interval the analysis actually uses.

`stage_b_protocol._worlds_for()` sizes the block with Fisher's z on Spearman's rho.
Protocol §5 builds the interval by **resampling worlds** (percentile bootstrap,
98.33 %, 10,000 replicates). Those are two different interval constructions, and the
record already shows them apart at one cell: `docs/sign_resolution_structure_behavior.json`
gives 0.9018 for the closed form and 0.85 for the simulated bootstrap, at 48 worlds and
a true rank correlation of 0.50.

So the ladder is a closed-form requirement whose bootstrap realisation was never checked
where it matters -- the planning row, reliability 0.50, observed Spearman 0.351510, 104
worlds per configuration. A machine pre-pass (`docs/AI-REVIEW-2026-11-02.md`, rubric 4)
made exactly that objection. This script answers it by simulation, at every row, using
`stage_b_protocol`'s own ladder functions so the points cannot drift from the protocol's.

What it reports is the probability that this protocol's decision rule -- Spearman across
worlds, percentile interval at 98.33 %, resolved only if the interval excludes zero with
the predicted sign -- clears the declared 90 % bar, per row.

No engine runs, no seed is spent, no world is generated. Worlds are synthetic draws from
a Gaussian copula with the stated rank correlation, which is the same generator the
sign-resolution artifact uses. The limitation is stated in the artifact, not implied.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path
from statistics import NormalDist

from benchmarks.stage_b_protocol import (
    LEVEL, RELIABILITY_GRID, SMALLEST_EFFECT, _attenuate, _worlds_for,
)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "stage_b_resolution_simulation.json"

BAR = 0.90              # the protocol's resolution bar
BOOTSTRAP_REPS = 300    # the same replicate count the sign-resolution artifact used
SIMS = 400              # per row; Monte-Carlo SE = sqrt(0.25/sims) ~ 0.025
SEED = 20261103

PREDICTED_SIGN = 1      # the claim is a positive relation; a resolved block must show it


# --- the estimator, copied from benchmarks/sign_resolution_behavior.py --------------
# Copied rather than imported so this check cannot be changed by an edit to a module
# with its own main(), and so the arithmetic here is readable in one screen.

def ranks(values):
    """Average ranks, so ties are handled the way Spearman defines them."""
    order = sorted(range(len(values)), key=values.__getitem__)
    out = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        shared = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            out[order[k]] = shared
        i = j + 1
    return out


def pearson(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = math.sqrt(sum((x - ma) ** 2 for x in a))
    db = math.sqrt(sum((y - mb) ** 2 for y in b))
    if da == 0.0 or db == 0.0:
        return 0.0
    return num / (da * db)


def spearman(x, y):
    return pearson(ranks(x), ranks(y))


def percentiles(values, level):
    ordered = sorted(values)
    alpha = (1.0 - level) / 2.0
    lo = ordered[int(alpha * (len(ordered) - 1))]
    hi = ordered[int((1.0 - alpha) * (len(ordered) - 1))]
    return lo, hi


def gaussian_copula_rho(rho_s: float) -> float:
    return 2.0 * math.sin(math.pi * rho_s / 6.0)


def analytic_p(n: int, rho: float, level: float = LEVEL) -> float:
    """Fisher's z resolution probability -- the ladder's closed form, as a reference."""
    if n < 4:
        return 0.0
    z_crit = NormalDist().inv_cdf(0.5 + level / 2.0)
    return NormalDist().cdf(math.atanh(rho) * math.sqrt(n - 3) - z_crit)


def simulate(rho_s: float, n: int, sims: int, reps: int, seed: int) -> dict:
    """Resolution share of the protocol's own rule at (n worlds, true rho)."""
    g = gaussian_copula_rho(rho_s)
    scale = math.sqrt(max(0.0, 1.0 - g * g))
    rng = random.Random(seed)
    resolved = 0
    idx = range(n)
    for _ in range(sims):
        xs = [0.0] * n
        ys = [0.0] * n
        for i in idx:
            x = rng.gauss(0.0, 1.0)
            xs[i] = x
            ys[i] = g * x + scale * rng.gauss(0.0, 1.0)
        boot = [0.0] * reps
        for b in range(reps):
            pick = [rng.randrange(n) for _ in idx]
            boot[b] = spearman([xs[i] for i in pick], [ys[i] for i in pick])
        lo, hi = percentiles(boot, LEVEL)
        excludes_zero = lo > 0.0 if PREDICTED_SIGN > 0 else hi < 0.0
        resolved += 1 if excludes_zero else 0
    share = resolved / sims
    return {
        "simulations": sims,
        "bootstrap_replicates": reps,
        "resolved_share": round(share, 4),
        "monte_carlo_se": round(math.sqrt(max(share * (1.0 - share), 0.0) / sims), 4),
        "clears_bar": bool(share >= BAR),
    }


def build(sims: int, reps: int, only: tuple[str, ...] = ()) -> dict:
    points: dict[str, dict] = {}
    for rel in RELIABILITY_GRID:
        label = "%.2f" % rel
        if only and label not in only:
            continue
        effect = _attenuate(SMALLEST_EFFECT, rel)
        worlds = _worlds_for(effect)
        row = {
            "reliability": rel,
            "observed_effect_spearman": round(effect, 6),
            "worlds_per_configuration": worlds,
            "fisher_z_says": round(analytic_p(worlds, effect), 4),
        }
        row.update(simulate(effect, worlds, sims, reps,
                            SEED + int(round(rel * 100))))
        points[label] = row
    return points


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sims", type=int, default=SIMS)
    ap.add_argument("--reps", type=int, default=BOOTSTRAP_REPS)
    ap.add_argument("--only", nargs="*", default=[],
                    help="ladder labels to compute, e.g. 0.50; default all")
    ap.add_argument("--explore", nargs="*", type=int, default=[],
                    help="extra world counts to simulate at the planning effect, "
                         "so a larger block can be priced rather than argued")
    args = ap.parse_args()

    previous: dict = {}
    previous_sizes: dict = {}
    if OUT.exists():
        try:
            document = json.loads(OUT.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            document = {}
        previous = document.get("points", {})
        previous_sizes = document.get("size_sensitivity_at_planning_effect", {})

    points = build(args.sims, args.reps, tuple(args.only))
    merged = dict(previous)
    merged.update(points)

    sizes = dict(previous_sizes)
    if args.explore:
        effect = _attenuate(SMALLEST_EFFECT, 0.50)
        for n in args.explore:
            row = {
                "observed_effect_spearman": round(effect, 6),
                "worlds_per_configuration": n,
                "fisher_z_says": round(analytic_p(n, effect), 4),
            }
            row.update(simulate(effect, n, args.sims, args.reps, SEED + 9000 + n))
            sizes[str(n)] = row

    planning = merged.get("%.2f" % 0.50)
    artifact = {
        "what_this_is": "The probability that Stage B's declared decision rule -- "
                        "Spearman across worlds, percentile bootstrap at 98.33 %, "
                        "resolved only when the interval excludes zero with the "
                        "predicted sign -- clears the 90 % bar, at each row of the "
                        "block ladder. Computed by simulation because the ladder "
                        "itself is a Fisher-z closed form.",
        "why_it_exists": "docs/AI-REVIEW-2026-11-02.md, rubric question 4: the ladder "
                         "is closed-form while the analysis is a percentile "
                         "bootstrap, and the bootstrap realisation was never checked "
                         "at the planning point.",
        "decision_rule_simulated": "Spearman rank correlation across worlds; interval "
                                   "by resampling worlds at the project's 98.33 % "
                                   "level; resolved only when it excludes zero with "
                                   "the predicted sign",
        "level": LEVEL,
        "bar": BAR,
        "generator": "Gaussian copula with the stated rank correlation; synthetic "
                     "worlds only, no engine, no seed spent",
        "prng_state": SEED,
        "points": {k: merged[k] for k in sorted(merged)},
        "size_sensitivity_at_planning_effect": {
            k: sizes[k] for k in sorted(sizes, key=int)
        },
        "planning_row": "0.50",
        "planning_clears_bar": None if not planning else planning["clears_bar"],
        "what_the_monte_carlo_allows": "each row carries the Monte-Carlo standard "
                                       "error of its own resolved share. Where that "
                                       "error spans the 90 % bar the row does not "
                                       "establish which side of the bar the design is "
                                       "on, and this artifact is not used to choose a "
                                       "size on such a row "
                                       "(docs/AI-REVIEW-2026-11-03.md, finding 2)",
        "limits": [
            "synthetic worlds under a Gaussian copula, not Stage B worlds; this "
            "measures a property of the estimator, not the size of the real relation",
            "300 bootstrap replicates per simulated block against the protocol's "
            "10,000. At the 98.33 % level the lower edge is the 3rd smallest of 300 "
            "replicates, where 10,000 give the 84th of 10,000, and the direction of "
            "the resulting bias in the resolved share is NOT measured here. An "
            "earlier version of this list asserted a direction for that bias; "
            "nothing in this artifact supported it "
            "(docs/AI-REVIEW-2026-11-03.md, finding 2)",
            "reliability is the declared planning assumption under one classical "
            "error model, not a measured property of DI",
        ],
    }
    OUT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")

    print(f"wrote {OUT.relative_to(ROOT)}  sims={args.sims} reps={args.reps}")
    for label, row in artifact["size_sensitivity_at_planning_effect"].items():
        print(f"  size {label:>3}  rho {row['observed_effect_spearman']:.6f}  "
              f"fisher-z {row['fisher_z_says']:.4f}  "
              f"bootstrap {row['resolved_share']:.3f} "
              f"(SE {row['monte_carlo_se']:.3f})  "
              f"{'clears' if row['clears_bar'] else 'BELOW BAR'}")
    for label, row in artifact["points"].items():
        print(f"  rel {label}  rho {row['observed_effect_spearman']:.6f}  "
              f"n {row['worlds_per_configuration']:>3}  "
              f"fisher-z {row['fisher_z_says']:.4f}  "
              f"bootstrap {row['resolved_share']:.3f} "
              f"(SE {row['monte_carlo_se']:.3f})  "
              f"{'clears' if row['clears_bar'] else 'BELOW BAR'}")


if __name__ == "__main__":
    main()
