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
from benchmarks import engine_stamp

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
RELIABILITIES = (1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3)


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


def observed_spearman(rho_s, reliability):
    """Population Spearman after classical error in the predictor only.

    Under bivariate normality, classical error in one variable multiplies the *Pearson* correlation
    by sqrt(reliability); the Spearman value of a bivariate normal follows from
    rho_s = (6/pi) asin(rho_g / 2). Multiplying the rank correlation by the reliability itself,
    which an earlier version of this artifact did, is not that rule and overstates the loss.
    """
    g = gaussian_copula_rho(rho_s) * math.sqrt(reliability)
    return (6.0 / math.pi) * math.asin(max(-1.0, min(1.0, g / 2.0)))


def check_observed_spearman(rho_s, reliability, rng, sims=300, worlds=48):
    """Monte-Carlo check of `observed_spearman` on samples of the block's own size."""
    g = gaussian_copula_rho(rho_s)
    scale = math.sqrt(max(0.0, 1.0 - g * g))
    noise = math.sqrt(max(0.0, 1.0 - reliability))
    est = math.sqrt(max(0.0, reliability))
    values = []
    for _ in range(sims):
        xs, ys = [], []
        for _ in range(worlds):
            z1 = rng.gauss(0.0, 1.0)
            z2 = rng.gauss(0.0, 1.0)
            xs.append(est * z1 + noise * rng.gauss(0.0, 1.0))
            ys.append(g * z1 + scale * z2)
        values.append(spearman(xs, ys))
    return sum(values) / len(values)


def simulate_dependence(rho_s, icc, rng, sims=150, reps=200, worlds=48, block=4):
    """Does dependence between worlds narrow or widen the interval? Measure, do not assume."""
    g = gaussian_copula_rho(rho_s)
    scale = math.sqrt(max(0.0, 1.0 - g * g))
    naive = blocked = 0
    for _ in range(sims):
        shared = rng.gauss(0.0, 1.0)
        xs, ys = [], []
        for _ in range(worlds):
            z1 = math.sqrt(icc) * shared + math.sqrt(max(0.0, 1.0 - icc)) * rng.gauss(0.0, 1.0)
            z2 = rng.gauss(0.0, 1.0)
            xs.append(z1)
            ys.append(g * z1 + scale * z2)
        naive_boot = [spearman([xs[i] for i in idx], [ys[i] for i in idx])
                      for idx in ([rng.randrange(worlds) for _ in range(worlds)] for _ in range(reps))]
        block_boot = []
        for _ in range(reps):
            starts = [rng.randrange(worlds) for _ in range(worlds // block)]
            idx = []
            for start in starts:
                idx.extend((start + j) % worlds for j in range(block))
            block_boot.append(spearman([xs[i] for i in idx], [ys[i] for i in idx]))
        if percentiles(naive_boot, LEVEL)[0] > 0.0:
            naive += 1
        if percentiles(block_boot, LEVEL)[0] > 0.0:
            blocked += 1
    return naive / sims, blocked / sims


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
        empirical = observed_spearman(RHO_REF, reliability)
        simulated = check_observed_spearman(RHO_REF, reliability, rng)
        attenuation.append({
            "reliability": reliability,
            "naive_product": round(RHO_REF * reliability, 4),
            "pearson_sqrt_rule": round(RHO_REF * math.sqrt(reliability), 4),
            "measured_rho": round(empirical, 4),
            "monte_carlo_rho": round(simulated, 4),
            "worlds_required": minimum_n(empirical),
        })

    dependence = []
    for icc in (0.0, 0.10, 0.20):
        naive_p, block_p = simulate_dependence(RHO_REF, icc, rng)
        dependence.append({
            "world_icc": icc,
            "p_iid_bootstrap": round(naive_p, 4),
            "p_block_bootstrap": round(block_p, 4),
            "difference": round(naive_p - block_p, 4),
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
            "model": ("Classical error in the predictor only: observed = sqrt(reliability) * latent + "
                      "sqrt(1 - reliability) * noise. Under bivariate normality this multiplies the PEARSON "
                      "correlation by sqrt(reliability); the observed SPEARMAN value then follows from "
                      "rho_s = (6/pi) asin(rho_g / 2), which `observed_spearman` computes and "
                      "`check_observed_spearman` verifies on samples of the block's own size. An earlier "
                      "version multiplied the rank correlation by the reliability itself, which is not the "
                      "same rule and overstated the loss at every level."),
            "latent_rho": RHO_REF,
            "rows": attenuation,
            "reading": ("reliability is measured nowhere in this project for DI, so the table is a sensitivity "
                        "curve under one stated error model, not a correction. It assumes classical, "
                        "independent error; DI is a bounded ratio and a different error model gives a "
                        "different curve. The measured reliability, once it exists, is the input; the curve "
                        "only says how far the requirement moves as that input varies."),
        },
        "dependence": {
            "assumption": ("worlds within one configuration are exchangeable, so the interval resamples them "
                           "individually."),
            "test": ("worlds are simulated with a shared component (intraclass correlation) in the predictor, "
                     "and the same data are resampled two ways: individual worlds, and contiguous blocks."),
            "rows": dependence,
            "finding": ("the direction is measured, not assumed. Positive intraclass correlation makes the "
                        "individual-world interval narrower than the block interval, so the i.i.d. probability "
                        "is the optimistic one; a different dependence structure could run the other way."),
            "required_diagnostic": ("report seed generation and ordering, whether seeds are independent "
                                    "experimental worlds, dependence beyond lag 1, and both the individual-world "
                                    "and contiguous-block intervals with the resolution probability under each."),
        },
        "status": ("provisional. The block's size is withheld pending independent review, and the reviewer is to see "
                   "the 48-world floor and the attenuation table together, not the floor alone."),
        "limits": [
            "The worlds are synthetic. This measures the estimator, not the size of the real relation.",
            "Attenuation from DI's own measurement error is not fitted; the attenuation table prices it under one stated assumption. The effect is to raise the worlds required, so 48 is a floor.",
            "The Gaussian copula assumes worlds are exchangeable draws. Within-configuration dependence changes the interval in a direction that depends on the structure of the dependence; the simulation in `dependence` does not resolve that direction at its simulation size, so the block measures it rather than assuming it.",
            "Only the primary configuration's rule is simulated. A secondary configuration with its own withheld set has its own outcome distribution and no number is transferred to it.",
            "The 98.33 % level and the 0.90 bar are conventions. The artifact reports the grid so a different bar can be read off without recomputation.",
        ],
        "generated_by": "python -m benchmarks.sign_resolution_behavior",
    }
    ART.write_text(json.dumps(engine_stamp.stamp(block), indent=2) + "\n", encoding="utf-8")
    return block


def main():
    block = build()
    v = block["verdict"]
    print(f"minimum n per relation: {block['minimum_n']}")
    print(f"reference rho {block['reference_rule']['rho']:.2f} -> n = {v['reference_n']}, "
          f"p = {v['p_at_reference_n']:.4f}")
    print(f"worst analytic-vs-bootstrap difference: {block['bootstrap_validation']['worst_abs_difference']}")
    print("attenuation (R, naive, sqrt, empirical, mc, worlds):")
    for r in block["attenuation"]["rows"]:
        print("  ", r["reliability"], r["naive_product"], r["pearson_sqrt_rule"],
              r["measured_rho"], r["monte_carlo_rho"], r["worlds_required"])
    print("dependence:", [(d["world_icc"], d["p_iid_bootstrap"], d["p_block_bootstrap"])
                          for d in block["dependence"]["rows"]])
    print(f"written: {ART.relative_to(ART.parents[1])}")


if __name__ == "__main__":
    main()
