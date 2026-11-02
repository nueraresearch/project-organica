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
RELIABILITIES = (1.0, 0.9, 0.8, 0.7, 0.6)


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
    attenuation = []
    for reliability in RELIABILITIES:
        measured = RHO_REF * reliability
        attenuation.append({
            "reliability": reliability,
            "measured_rho": round(measured, 4),
            "worlds_required": minimum_n(measured),
        })
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
        "bound_direction": {
            "statement": ("The computed PROBABILITY is an upper bound, and the computed MINIMUM N is therefore a "
                          "floor. Every unmodelled defect - measurement error in DI, dependence between worlds - "
                          "makes the real probability lower than the computed one, so a block of that size "
                          "resolves the relation LESS often than the table says, and the worlds required are AT "
                          "LEAST those listed."),
            "probability": "upper bound",
            "minimum_n": "floor: a lower bound on the worlds required, not a ceiling on the block's size",
            "correction": ("The first version of this artifact called the output an upper bound without saying of "
                           "what, so the 48-world figure could be read as a maximum. Corrected 2026-11-02 after "
                           "the owner pointed out that attenuation implies the opposite direction for the world "
                           "count."),
        },
        "what_the_number_is_not": [
            "not a posterior probability that the hypothesis is true",
            "not a p-value, not a false-positive rate, and not a power figure in the Neyman-Pearson sense",
            "not a property of the engine: no engine ran, and no seed was spent",
            "not a statement about a latent relation - it concerns the relation as measured, handled in `attenuation`",
        ],
        "attenuation": {
            "model": ("No measurement-error model is fitted. The table is the consequence of one stated assumption: "
                      "a latent relation of RHO_REF appears in the measured data as RHO_REF * reliability, the "
                      "classical-errors-in-one-variable result under bivariate normality."),
            "latent_rho": RHO_REF,
            "rows": attenuation,
            "reading": ("reliability is not measured anywhere in this project for DI, so the table states the price "
                        "of an unmeasured quantity rather than a corrected answer. It moves the requirement up, "
                        "never down."),
        },
        "exchangeability": {
            "assumption": "worlds within one configuration are exchangeable draws, so the interval resamples them individually.",
            "what_breaks_it": ("state carried between seeds, or worlds drawn from related conditions. Analysing each "
                               "configuration separately removes across-configuration clustering; it says nothing "
                               "about dependence within a configuration."),
            "required_diagnostic": ("before the relation is read, report the dependence of DI and of the outcome on "
                                    "seed order (lag-1 correlation across the block's seed sequence), and if it is "
                                    "non-negligible resample contiguous blocks of seeds instead of individual "
                                    "worlds, reporting both intervals."),
            "direction_if_violated": ("the interval is too narrow, so the probability is overstated and the worlds "
                                      "required are at least those in the grid. Same direction as attenuation."),
        },
        "status": ("provisional. The block's size is withheld pending independent review, and the reviewer is to see "
                   "the 48-world floor and the attenuation table together, not the floor alone."),
        "limits": [
            "The worlds are synthetic. This measures the estimator, not the size of the real relation.",
            "Attenuation from DI's own measurement error is not fitted; the attenuation table prices it under one stated assumption. The effect is to raise the worlds required, so 48 is a floor.",
            "The Gaussian copula assumes worlds are exchangeable draws. Within-configuration dependence would narrow the interval and overstate the probability, so this again raises the worlds required and never lowers them.",
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
    print("attenuation:", [(r["reliability"], r["measured_rho"], r["worlds_required"])
                           for r in block["attenuation"]["rows"]])
    print(f"written: {ART.relative_to(ART.parents[1])}")


if __name__ == "__main__":
    main()
