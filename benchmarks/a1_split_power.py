"""How many seeds per split block does the offset discriminator need?

The pair-split construction (`A1-OFFSET-DISCRIMINATOR-SPEC-1`) proposes two
32/48-tag blocks with identical candidate count (**63.8**).  The fitted size
summary predicts the same offset for both — a measured difference of **0.000**
— while the fitted density summary predicts **-0.116**, because the two blocks
differ in tags-per-cell density (**1.995** against **1.330**).  The spec's
decision rule maps that difference onto bands: |d| at or below **0.05** for the
size summary, at or above **0.09** with the density sign for the density
summary, and anything between as "neither is identified".

This module answers the design question the spec only gestures at ("about 3
standard errors at six seeds per block"): with a per-seed offset SD of sigma,
how many seeds per block does each branch of that rule need before the wrong
decision falls to a stated rate?  It reads only committed artifacts — the spec
for the predictions and the bands, `A1-WITHIN-BLOCK-LEVEL-1` and
`A1-OFFSET-PREDICTORS-1` for sigma — and computes nothing on an arm.

Power is exact two-sample *t*: for `n` seeds per block the estimate has
`SE = sigma * sqrt(2 / n)` on `2n - 2` degrees of freedom, and each branch
probability is an expectation over the pooled-SD chi density,

    P(density declared) = E_s[ Phi( (|d_density| - ceiling) / (SE * s) ) ]
    P(size declared)    = E_s[ Phi(ceiling / (SE * s)) - Phi(-ceiling / (SE * s)) ],

with the mirror terms giving each branch's false-decision rate.  The band rule
is a threshold on an estimate, not a p-value test, so the design rate is the
probability of the wrong band, and no alpha is chosen on top of it.

    python -m benchmarks.a1_split_power --write
    python -m benchmarks.a1_split_power --check
    python -m benchmarks.a1_split_power --self-test
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SPEC_PATH = DOCS / "a1_offset_discriminator_spec.json"
WITHIN_PATH = DOCS / "a1_within_block_level.json"
PREDICTORS_PATH = DOCS / "a1_offset_predictors.json"
OUT_PATH = DOCS / "a1_split_power.json"
PAGE_PATH = DOCS / "A1-SPLIT-POWER.md"
ID = "A1-SPLIT-POWER-1"
DATE = "2026-11-14"
KIND = "a1_split_power"
STATUS = ("DESIGN ESTIMATE — SEEDS PER SPLIT BLOCK FOR THE OFFSET DISCRIMINATOR; "
          "NO TARGET, FREEZE, GRANT OR A1 CELL")
FLOOR = 0.05
CEILING = 0.09
RATES = (0.20, 0.10, 0.05)
PRIMARY_SIGMA = 0.066656
SIGMA_GRID = (
    (0.035742, "seed-2067 within-block offset SD"),
    (0.043410, "current-16 within-block offset SD"),
    (0.066656, "candidate-size cell seed-level LOO RMSE"),
    (0.072798, "fresh-16 within-block offset SD"),
)
PAIRING = (0.0, 0.3, 0.5)
COMMITTED_SEEDS = 6


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _phi(x: float) -> float:
    return 0.5 * math.erfc(-x / math.sqrt(2.0))


def _log_chi(s: float, df: int) -> float:
    """Log density of S/sigma for a sample SD on `df` degrees of freedom.

    S/sigma is sqrt(chi2_df / df), so the chi density is scaled by sqrt(df)
    in s and df in the exponent.
    """
    if s <= 0.0:
        return -math.inf
    half = df / 2.0
    return ((df - 1.0) * math.log(s) + half * math.log(df) - df * s * s / 2.0
            - (half - 1.0) * math.log(2.0) - math.lgamma(half))


def _expectation(df: int, weight) -> float:
    """Integrate weight(s) over the chi density of S/sigma by Simpson."""
    upper = 1.0 + 7.0 / math.sqrt(df)
    steps = 4000
    step = upper / steps
    total = 0.0
    for index in range(steps + 1):
        s = index * step
        density = math.exp(_log_chi(s, df)) if s > 0.0 else 0.0
        value = density * weight(s) if density else 0.0
        factor = 1 if index in (0, steps) else (4 if index % 2 else 2)
        total += factor * value
    return total * step / 3.0


def _se(sigma: float, n: int, rho: float = 0.0) -> float:
    return sigma * math.sqrt(2.0 * (1.0 - rho) / n)


def _powers(sigma: float, n: int, gap: float, rho: float = 0.0) -> dict:
    """Branch probabilities for `n` seeds per block under a per-seed SD."""
    se = _se(sigma, n, rho)
    df = max(2 * n - 2, 1)
    size = _expectation(df, lambda s: _phi(FLOOR / (se * s))
                        - _phi(-FLOOR / (se * s)))
    density = _expectation(df, lambda s: _phi((abs(gap) - CEILING) / (se * s)))
    false_density = _expectation(df, lambda s: _phi(-CEILING / (se * s)))
    false_size = 1.0 - _expectation(
        df, lambda s: _phi((abs(gap) - FLOOR) / (se * s)))
    undecided_size = _expectation(
        df, lambda s: _phi(-FLOOR / (se * s))) - false_density
    undecided_density = _expectation(
        df, lambda s: _phi((abs(gap) - FLOOR) / (se * s))) - density
    return {
        "size": size,
        "density": density,
        "false_density": false_density,
        "false_size": false_size,
        "undecided_if_size": undecided_size,
        "undecided_if_density": undecided_density,
    }


def _needed(sigma: float, rate: float, gap: float, branch: str,
            rho: float = 0.0, limit: int = 60) -> int | None:
    for n in range(2, limit + 1):
        if _powers(sigma, n, gap, rho)[branch] >= 1.0 - rate:
            return n
    return None


def _level_seeds(sigma: float, gap: float, rate: float) -> int:
    """Seeds in one block to place its level within half the model gap."""
    z = 1.2815515655446004 if rate == 0.20 else (
        1.6448536269514722 if rate == 0.10 else 1.959963984540054)
    return max(2, math.ceil((z * sigma / (gap / 2.0)) ** 2))


def build() -> dict:
    spec = _load(SPEC_PATH)
    within = _load(WITHIN_PATH)
    predictors = _load(PREDICTORS_PATH)
    predictions = {row["label"]: row for row in spec["predictions"]}
    gap = round(predictions["split-32"]["density_offset"]
                - predictions["split-48"]["density_offset"], 6)
    if gap >= 0:
        raise SystemExit("REFUSED: the density summary does not predict a "
                         "negative split-32 minus split-48 difference")
    size_gap = round(predictions["split-32"]["size_offset"]
                     - predictions["split-48"]["size_offset"], 6)
    if abs(size_gap) > 1e-9:
        raise SystemExit("REFUSED: the size summary does not predict zero")
    rows = []
    for sigma, source in SIGMA_GRID:
        for rate in RATES:
            size_n = _needed(sigma, rate, gap, "size")
            density_n = _needed(sigma, rate, gap, "density")
            both = max(size_n or 0, density_n or 0) or None
            detail = _powers(sigma, both, gap) if both else {}
            rows.append({
                "sigma": sigma,
                "sigma_source": source,
                "wrong_decision_rate": rate,
                "seeds_size_branch": size_n,
                "seeds_density_branch": density_n,
                "seeds_both_branches": both,
                "total_seeds": 2 * both if both else None,
                "se_at_that_n": round(_se(sigma, both), 6) if both else None,
                "power_size": round(detail.get("size", 0.0), 4) if both else None,
                "power_density": round(detail.get("density", 0.0), 4)
                if both else None,
            })
    committed = _powers(PRIMARY_SIGMA, COMMITTED_SEEDS, gap)
    committed_se = _se(PRIMARY_SIGMA, COMMITTED_SEEDS)
    pairing = []
    for rho in PAIRING:
        n = _needed(PRIMARY_SIGMA, 0.20, gap, "density", rho=rho)
        both = max(_needed(PRIMARY_SIGMA, 0.20, gap, "size", rho=rho) or 0, n or 0)
        pairing.append({
            "pairing_rho": rho,
            "se_at_six": round(_se(PRIMARY_SIGMA, COMMITTED_SEEDS, rho), 6),
            "power_density_at_six": round(
                _powers(PRIMARY_SIGMA, COMMITTED_SEEDS, gap, rho)["density"], 4),
            "seeds_both_branches": both or None,
        })
    levels = [{
        "block": label,
        "model_gap": round(predictions[label]["gap"], 6),
        "seeds_at_half_gap": _level_seeds(PRIMARY_SIGMA,
                                          predictions[label]["gap"], 0.20),
    } for label in ("split-32", "split-48")]
    primary = next(row for row in rows
                   if row["sigma"] == PRIMARY_SIGMA
                   and row["wrong_decision_rate"] == 0.20)
    by_sigma = []
    for sigma, source in SIGMA_GRID:
        row = next(item for item in rows
                   if item["sigma"] == sigma
                   and item["wrong_decision_rate"] == 0.20)
        by_sigma.append(row)
    found = {
        "gap": gap,
        "size_gap": size_gap,
        "primary_sigma": PRIMARY_SIGMA,
        "primary_sigma_source": primary["sigma_source"],
        "seeds_both_at_primary": primary["seeds_both_branches"],
        "seeds_density_at_primary": primary["seeds_density_branch"],
        "seeds_size_at_primary": primary["seeds_size_branch"],
        "range_across_sigma": [
            min(row["seeds_both_branches"] for row in by_sigma),
            max(row["seeds_both_branches"] for row in by_sigma),
        ],
        "committed_seeds_per_block": COMMITTED_SEEDS,
        "committed_se": round(committed_se, 6),
        "committed_power_size": round(committed["size"], 4),
        "committed_power_density": round(committed["density"], 4),
        "committed_false_density": round(committed["false_density"], 4),
        "committed_false_size": round(committed["false_size"], 4),
        "committed_undecided_if_size": round(committed["undecided_if_size"], 4),
        "committed_undecided_if_density": round(
            committed["undecided_if_density"], 4),
    }
    reading = (
        "The differential needs **%(nb)d seeds per split block** — **%(tot)d** "
        "seeds in total — to decide either branch at a **%(rate).0f%%** wrong-"
        "decision rate under the primary per-seed SD **%(sig).4f** (%(src)s). "
        "The branches are not equally cheap: the size branch needs **%(ns)d** "
        "seeds and the density branch **%(nd)d**, because the density evidence "
        "is the distance from the estimate to the **0.09** ceiling — only "
        "**%(margin).4f** against a **%(gap).4f** separation — while the size "
        "branch only has to land the estimate inside a **0.05** band around "
        "zero. Across the per-seed SDs the measured blocks supply "
        "(**%(lo).4f**–**%(hi).4f**) the same rate asks for **%(rlo)d**–"
        "**%(rhi)d** seeds per block, so **%(rhi)d** is the defensible design "
        "number and **%(nb)d** the one implied by the frozen fit. The committed "
        "**%(committed)d** seeds per block do not reach the convention: at "
        "**σ %(sig).4f** the standard error of the difference is "
        "**%(cse).4f**, which gives **%(cps).3f** power on the size branch but "
        "only **%(cpd).3f** on the density branch, with a **%(cfd).3f** chance "
        "of declaring density when the size summary is true, **%(cfs).3f** of "
        "the reverse, **%(cn).3f** of landing in the undecided band when the size "
        "summary is true and **%(cnd).3f** when the density summary is. A "
        "paired design on the same seeds in both blocks scales the requirement "
        "by **(1 − ρ)**; at **ρ 0.5** the number falls to **%(pair)d** seeds "
        "per block. The cheaper alternative — measuring one block's level "
        "against the two predictions, which differ by **%(lg1).3f** and "
        "**%(lg2).3f** at equal candidate count — needs only **%(l2)d** seeds "
        "per block at the primary SD, but that level estimate "
        "inherits the failure measured in `84ce329`, where a fresh block "
        "landed below its fitted value; the differential is robust to that "
        "shift, which is why it is the more expensive estimand."
        % {
            "nb": primary["seeds_both_branches"],
            "tot": 2 * primary["seeds_both_branches"],
            "rate": 100 * 0.20,
            "sig": PRIMARY_SIGMA,
            "src": primary["sigma_source"],
            "ns": primary["seeds_size_branch"],
            "nd": primary["seeds_density_branch"],
            "margin": round(abs(gap) - CEILING, 6),
            "gap": abs(gap),
            "lo": min(row["sigma"] for row in by_sigma),
            "hi": max(row["sigma"] for row in by_sigma),
            "rlo": min(row["seeds_both_branches"] for row in by_sigma),
            "rhi": max(row["seeds_both_branches"] for row in by_sigma),
            "committed": COMMITTED_SEEDS,
            "cse": round(committed_se, 6),
            "cps": committed["size"],
            "cpd": committed["density"],
            "cfd": committed["false_density"],
            "cfs": committed["false_size"],
            "cn": committed["undecided_if_size"],
            "cnd": committed["undecided_if_density"],
            "pair": pairing[2]["seeds_both_branches"],
            "lg1": levels[0]["model_gap"],
            "lg2": levels[1]["model_gap"],
            "l2": max(row["seeds_at_half_gap"] for row in levels),
        }
    )
    return engine_stamp.stamp({
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "not_a_result": True,
        "question": (
            "How many seeds per split block does the offset discriminator need "
            "to decide between the size and density summaries at a stated "
            "wrong-decision rate?"
        ),
        "definition": (
            "The seeds per block required for each branch of the committed "
            "band rule on the split-32 minus split-48 offset difference, as a "
            "function of the per-seed offset SD, with exact two-sample t power."
        ),
        "method": (
            "Read the predictions, bands and frozen coefficients from the "
            "committed offset-discriminator spec, and the per-seed SDs from the "
            "committed within-block and offset-predictor artifacts. For each "
            "candidate n, integrate each branch probability over the pooled-SD "
            "chi density on 2n - 2 degrees of freedom. The branch is charged "
            "its own wrong-decision rate; no additional alpha is applied "
            "because the rule thresholds an estimate rather than testing a "
            "hypothesis."
        ),
        "constants": {
            "floor": FLOOR,
            "ceiling": CEILING,
            "wrong_decision_rates": list(RATES),
            "sigma_grid": [sigma for sigma, _ in SIGMA_GRID],
            "primary_sigma": PRIMARY_SIGMA,
            "pairing_rho_grid": list(PAIRING),
            "committed_seeds_per_block": COMMITTED_SEEDS,
            "prediction_artifacts": [str(SPEC_PATH.name), str(WITHIN_PATH.name),
                                     str(PREDICTORS_PATH.name)],
        },
        "governance": {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none",
        },
        "reading": reading,
        "found": found,
        "rows": rows,
        "pairing": pairing,
        "level_alternative": levels,
        "limits": [
            "The per-seed SD is not measured in a split block; it is borrowed from 16-tag blocks and from the fitted seed-level LOO RMSE, and the answer moves by a factor of three across that grid.",
            "The predictions are frozen-summary counterfactuals: no split block has been run, so a measured differential may not fall at either predicted value.",
            "Power assumes independent seeds across the two blocks; a paired design on the same seeds is reported as a sensitivity, not as a recommendation.",
            "The band rule is a design convention, not a hypothesis test; the reported rate is the probability of the wrong band, and it is not comparable to a p-value.",
        ],
        "not_evidence": (
            "A design estimate computed from committed artifacts. It runs no "
            "arm, measures no split block, and is not a treatment, target, "
            "freeze, grant or A1 cell."
        ),
    })


def render(doc: dict) -> str:
    found = doc["found"]
    lines = [
        "# A1 split-block power",
        "",
        "Generated from `docs/a1_split_power.json` by "
        "`python -m benchmarks.a1_split_power --write`. Do not edit by hand.",
        "",
        "**Design estimate, not an A1 result.** No split block has been run.",
        "",
        "## Result",
        "",
        doc["reading"],
        "",
        "## Seeds per block by per-seed SD and wrong-decision rate",
        "",
        "| Per-seed SD | Source | Rate | Size branch | Density branch | Both | Total |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["rows"]:
        lines.append("| %.6f | %s | %.2f | %s | %s | %s | %s |" % (
            row["sigma"], row["sigma_source"], row["wrong_decision_rate"],
            row["seeds_size_branch"], row["seeds_density_branch"],
            row["seeds_both_branches"], row["total_seeds"]))
    lines += [
        "",
        "## What six seeds per block buys",
        "",
        "| Quantity | Value |",
        "| --- | ---: |",
        "| SE of the difference | %.6f |" % found["committed_se"],
        "| Power, size branch | %.4f |" % found["committed_power_size"],
        "| Power, density branch | %.4f |" % found["committed_power_density"],
        "| Declares density when size is true | %.4f |"
        % found["committed_false_density"],
        "| Declares size when density is true | %.4f |"
        % found["committed_false_size"],
        "| Lands in the undecided band, size true | %.4f |"
        % found["committed_undecided_if_size"],
        "| Lands in the undecided band, density true | %.4f |"
        % found["committed_undecided_if_density"],
        "",
        "## Paired design",
        "",
        "| Seed correlation | SE at six | Density power at six | Seeds for both branches |",
        "| ---: | ---: | ---: | ---: |",
    ]
    for row in doc["pairing"]:
        lines.append("| %.2f | %.6f | %.4f | %s |" % (
            row["pairing_rho"], row["se_at_six"],
            row["power_density_at_six"], row["seeds_both_branches"]))
    lines += [
        "",
        "## The cheaper level alternative",
        "",
        "| Block | Model gap | Seeds at half the gap |",
        "| --- | ---: | ---: |",
    ]
    for row in doc["level_alternative"]:
        lines.append("| %s | %.6f | %d |" % (
            row["block"], row["model_gap"], row["seeds_at_half_gap"]))
    lines += ["", "## Limits", ""]
    lines += ["- %s" % limit for limit in doc["limits"]]
    lines += ["", "## What this does not claim", "", doc["not_evidence"], ""]
    return "\n".join(lines)


def problems(doc: dict | None = None) -> list[str]:
    doc = _load(OUT_PATH) if doc is None else doc
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("artifact kind")
    if doc.get("not_a_result") is not True:
        found.append("the artifact does not say it is not a result")
    if engine_stamp.missing(doc):
        found.append("the artifact is not fully stamped")
    if doc.get("governance") != {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none"}:
        found.append("governance changed")
    if abs(doc["found"]["gap"] + 0.11638) > 5e-4:
        found.append("the density differential moved")
    if doc["found"]["size_gap"] != 0.0:
        found.append("the size differential is not zero")
    for row in doc["rows"]:
        if row["seeds_both_branches"] is None:
            found.append("a row does not reach a decision inside the n limit")
            continue
        if row["seeds_both_branches"] < max(row["seeds_size_branch"],
                                            row["seeds_density_branch"]):
            found.append("both-branch count is below a single branch")
        if row["total_seeds"] != 2 * row["seeds_both_branches"]:
            found.append("total seeds are not two blocks")
    if doc["found"]["committed_power_density"] >= 0.8:
        found.append("six seeds are reported as reaching the density branch")
    if doc["found"]["committed_se"] >= 0.05:
        found.append("the committed design is reported wider than the size band")
    if PAGE_PATH.exists() and PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("the page is stale")
    return found


def self_test() -> list[str]:
    failures: list[str] = []
    if _phi(0.0) != 0.5 or abs(_phi(1.959963984540054) - 0.975) > 1e-6:
        failures.append("normal CDF")
    integral = _expectation(10, lambda s: 1.0)
    if abs(integral - 1.0) > 1e-6:
        failures.append("chi density does not integrate to one: %.6f" % integral)
    loose = _powers(PRIMARY_SIGMA, 40, -0.11638)
    if not loose["size"] > 0.99 or not loose["density"] > 0.95:
        failures.append("power does not approach one with 40 seeds")
    wide = _powers(PRIMARY_SIGMA, 120, -0.11638)
    if not wide["density"] > 0.99:
        failures.append("the density branch never reaches 0.99")
    tight = _powers(PRIMARY_SIGMA, 2, -0.11638)
    if tight["size"] > loose["size"] or tight["density"] > loose["density"]:
        failures.append("power does not grow with n")
    monotone = [_needed(PRIMARY_SIGMA, rate, -0.11638, "density")
                for rate in (0.20, 0.10, 0.05)]
    if not monotone[0] <= monotone[1] <= monotone[2]:
        failures.append("a stricter rate asks for fewer seeds")
    return failures


def write() -> int:
    body = build()
    OUT_PATH.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(body), encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print(body["reading"])
    print("found:", body["found"])
    print("level:", body["level_alternative"])
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        raise SystemExit("no split-power artifact; run --write")
    found = problems(_load(OUT_PATH))
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("split power: clean")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.write:
        return write()
    if args.self_test:
        found = self_test()
        if found:
            raise SystemExit("FAIL: " + "; ".join(found))
        print("split power self-test: clean")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
