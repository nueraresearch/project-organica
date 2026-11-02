"""Sign resolution for the structure -> behavior block, computed before any seed is allocated.

The ladder's `sign_resolution` answers a per-world question: if this run scored one world, how often
would it report that world's sign correctly? This block's unit is not one world but a block of worlds —
the estimand is a rank correlation *across* worlds — so the analogous question is:

    at n worlds per configuration, how often would this protocol's decision rule recover the relation
    with the correct sign, if the relation were the smallest one the design would call predictive?

The rule simulated is the protocol's own, not a convenient approximation: Spearman rank correlation
across worlds, an interval from resampling worlds at the project's 98.33 % level, and a block resolved
only when that interval excludes zero **with the predicted sign**. The analytic Fisher-z value is
computed beside it and the two are compared, so the number reported is a simulation of the committed
rule rather than a power formula wearing its name.

No engine runs. No seed is spent. The worlds are synthetic, which is the limitation stated in the
artifact's `limits` list: this measures a property of the estimator under a declared generative model,
not the size of the real relation.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path
from statistics import NormalDist

ART = Path(__file__).resolve().parent.parent / "docs" / "sign_resolution_structure_behavior.json"

LEVEL = 0.9833          # the project's interval convention
THRESHOLD = 0.90        # the bar the protocol declares
RHO_REF = 0.50          # the smallest relation the design would call predictive
RHOS = (0.30, 0.40, 0.50, 0.60, 0.70)
NS = (5, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100)
BOOTSTRAP_REPS = 300
SIMS = 200
VALIDATION = ((10, 0.50), (48, 0.50), (32, 0.60), (21, 0.70), (79, 0.40), (30, 0.30))
MAX_N = 400


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


def fisher_interval(r, n, level=LEVEL):
    if abs(r) >= 1.0 or n < 4:
        return (r, r)
    z = math.atanh(r)
    se = 1.0 / math.sqrt(n - 3)
    zc = NormalDist().inv_cdf(0.5 + level / 2.0)
    return (math.tanh(z - zc * se), math.tanh(z + zc * se))


def z_critical(level=LEVEL):
    return NormalDist().inv_cdf(0.5 + level / 2.0)


def analytic_p(n, rho, level=LEVEL):
    """P(the interval excludes zero with the predicted sign) under Fisher's z on Spearman's r."""
    if n < 4:
        return 0.0
    return NormalDist().cdf(math.atanh(rho) * math.sqrt(n - 3) - z_critical(level))


def gaussian_copula_rho(rho_s):
    """Pearson correlation of the copula that yields Spearman's rho_s under normality."""
    return 2.0 * math.sin(math.pi * rho_s / 6.0)


def draw_block(n, rho_s, rng):
    g = gaussian_copula_rho(rho_s)
    scale = math.sqrt(max(0.0, 1.0 - g * g))
    xs, ys = [], []
    for _ in range(n):
        z1 = rng.gauss(0.0, 1.0)
        z2 = rng.gauss(0.0, 1.0)
        xs.append(z1)
        ys.append(g * z1 + scale * z2)
    return xs, ys


def simulate_block(n, rho_s, rng, sims=SIMS, reps=BOOTSTRAP_REPS):
    """Frequency with which the protocol's bootstrap rule reports the predicted sign."""
    hits = 0
    for _ in range(sims):
        xs, ys = draw_block(n, rho_s, rng)
        boot = []
        for _ in range(reps):
            idx = [rng.randrange(n) for _ in range(n)]
            boot.append(spearman([xs[i] for i in idx], [ys[i] for i in idx]))
        lo, _hi = percentiles(boot, LEVEL)
        if lo > 0.0:
            hits += 1
    return hits / sims


def minimum_n(rho, threshold=THRESHOLD):
    for n in range(4, MAX_N + 1):
        if analytic_p(n, rho) >= threshold:
            return n
    return None


def build():
    rng = random.Random(20261102)
    analytic = {f"{n}": {f"{r:.2f}": round(analytic_p(n, r), 4) for r in RHOS} for n in NS}
    mins = {f"{r:.2f}": minimum_n(r) for r in RHOS}

    validation = []
    for n, r in VALIDATION:
        sim = simulate_block(n, r, rng)
        a = analytic_p(n, r)
        validation.append({
            "n": n, "rho": r, "analytic": round(a, 4), "simulated": round(sim, 4),
            "difference": round(sim - a, 4), "sims": SIMS, "bootstrap_reps": BOOTSTRAP_REPS,
            "monte_carlo_se": round(math.sqrt(max(sim * (1 - sim), 1e-9) / SIMS), 4),
        })
    worst = max(abs(v["difference"]) for v in validation)

    n_ref = mins[f"{RHO_REF:.2f}"]
    p_ref = analytic_p(n_ref, RHO_REF)
    block = {
        "kind": "sign resolution for the structure -> behavior block",
        "subject": "docs/STRUCTURE-BEHAVIOR-DESIGN.md \u00a76; synthetic worlds; no engine run, no seed",
        "question": ("at n worlds per configuration, how often does this block's decision rule recover "
                     "the relation with the correct sign, for a relation of size rho?"),
        "decision_rule_simulated": ("Spearman rank correlation across worlds; interval by resampling "
                                    "worlds; resolved only when the interval excludes zero with the "
                                    "predicted sign"),
        "reference_rule": {
            "name": "smallest relation of interest",
            "rho": RHO_REF,
            "why": ("the bar is set at the weakest relation the design would call predictive. Setting it "
                    "at a guessed effect size would make the answer depend on a number no artifact "
                    "supplies; setting it at the smallest effect worth detecting makes the block's size "
                    "a consequence of the claim instead of the claim a consequence of the size."),
        },
        "threshold": THRESHOLD,
        "level": LEVEL,
        "grid": {"ns": list(NS), "rhos": list(RHOS), "analytic": analytic},
        "bootstrap_validation": {
            "rows": validation, "worst_abs_difference": round(worst, 4),
            "note": ("the analytic column is Fisher's z on Spearman's r; the simulated column applies "
                     "the protocol's bootstrap. They are two different interval constructions, so the "
                     "difference is a check that the closed form is not doing the work alone, not an "
                     "error estimate of either."),
        },
        "minimum_n": mins,
        "verdict": {
            "reference_n": n_ref,
            "p_at_reference_n": round(p_ref, 4),
            "p_at_reference_n_without_bar": None,
            "reading": (f"at a true rank relation of {RHO_REF:.2f}, a block of {n_ref} worlds per "
                        f"configuration resolves the sign with probability {p_ref:.3f} at the "
                        f"{THRESHOLD:.2f} bar. Smaller blocks resolve only larger relations."),
            "smallest_relation_at_n": {
                "5": next((f"{r:.2f}" for r in RHOS if analytic_p(5, r) >= THRESHOLD), None),
                "10": next((f"{r:.2f}" for r in RHOS if analytic_p(10, r) >= THRESHOLD), None),
                "20": next((f"{r:.2f}" for r in RHOS if analytic_p(20, r) >= THRESHOLD), None),
                "30": next((f"{r:.2f}" for r in RHOS if analytic_p(30, r) >= THRESHOLD), None),
            },
        },
        "limits": [
            "The worlds are synthetic. This measures the estimator, not the size of the real relation.",
            "Attenuation from DI's own measurement error is not modelled, so the computed probability is an upper bound on the real one. A noisy predictor shrinks the observed rank correlation before the interval is built.",
            "The Gaussian copula assumes worlds are exchangeable draws. If configurations cluster as §5 suggests, the effective number of independent worlds is smaller than n and the probability is again an upper bound.",
            "Only the primary configuration's rule is simulated. A secondary configuration with its own withheld set has its own outcome distribution and no number is transferred to it.",
            "The 98.33 % level and the 0.90 bar are conventions. The artifact reports the grid so a different bar can be read off without recomputation.",
        ],
        "generated_by": "python -m benchmarks.sign_resolution_behavior",
    }
    ART.write_text(json.dumps(block, indent=2) + "\n", encoding="utf-8")
    return block


def main():
    block = build()
    v = block["verdict"]
    print(f"minimum n per relation: {block['minimum_n']}")
    print(f"reference rho {block['reference_rule']['rho']:.2f} -> n = {v['reference_n']}, "
          f"p = {v['p_at_reference_n']:.4f}")
    print(f"worst analytic-vs-bootstrap difference: {block['bootstrap_validation']['worst_abs_difference']}")
    print(f"written: {ART.relative_to(ART.parents[1])}")


if __name__ == "__main__":
    main()
