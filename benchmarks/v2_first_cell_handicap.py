"""Where the null handicap comes from, and whether any readout can remove it.

The null calibration measured `d = L_C − L_A = +0.000847` on structureless
worlds. This diagnostic decomposes it from the stored artifact and then tests
the only two ways a readout could be unbiased there:

* **β pseudo-counts (arm B, frozen membership).** `B − A` with the same β grid
  and no revision: the cost of adding membership mass at all.
* **The revision rule (arm C − arm B).** Maintaining membership in a 20-cycle
  window changes how much mass is added, so it can add or remove handicap.
* **A row-preserving mixture.** `p' = (1−λ)·p_counts + λ·q_member`, where
  `q_member` is the normalised membership distribution. This keeps each
  source's total probability at one instead of adding pseudo-counts, and is the
  strongest candidate for an unbiased readout.

The reason to expect no non-trivial unbiased variant: on a structureless world
the true next-tag distribution is uniform, so *any* deviation from the counts'
estimate increases expected log-loss by convexity. The handicap is the price of
using membership, not a calibration bug that a better formula can remove. β = 0
is exactly unbiased and exactly the baseline, which is why the control is in
the table.

    python -m benchmarks.v2_first_cell_handicap --check
    python -m benchmarks.v2_first_cell_handicap --write
"""
from __future__ import annotations

import argparse
import collections
import json
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from benchmarks import engine_stamp, v2_first_cell_null as null, v2_first_cell_readout as readout  # noqa: E402
from benchmarks.heldout_prediction import _score  # noqa: E402
from organica.streams import EVENTS_PER_CYCLE  # noqa: E402

ARTIFACT = Path("docs/v2_first_cell_handicap.json")
PAGE = Path("docs/V2-FIRST-CELL-HANDICAP.md")
NULL_ARTIFACT = Path("docs/v2_first_cell_null.json")
LAMBDAS = (0.1, 0.2)


def stored_decomposition() -> dict:
    record = json.loads(NULL_ARTIFACT.read_text(encoding="utf-8"))
    beta_only = [row["arms"]["B"]["log_loss"] - row["arms"]["A"]["log_loss"] for row in record["per_seed"]]
    net = [row["d"] for row in record["per_seed"]]
    revision = [c - b for b, c in zip(beta_only, net)]
    return {
        "n": len(net),
        "beta_only_mean": round(statistics.fmean(beta_only), 6),
        "beta_only_sd": round(statistics.stdev(beta_only), 6),
        "revision_mean": round(statistics.fmean(revision), 6),
        "revision_sd": round(statistics.stdev(revision), 6),
        "net_mean": round(statistics.fmean(net), 6),
        "beta_only_positive": sum(1 for value in beta_only if value > 0),
        "revision_positive": sum(1 for value in revision if value > 0),
        "net_positive": sum(1 for value in net if value > 0),
        "betas": sorted({row["arms"]["B"]["beta"] for row in record["per_seed"]}),
    }


def mixture_probability(counts, totals, vocab, membership, lam: float):
    """Row-preserving mix of the counts estimate and membership's allocation."""
    member_totals: collections.Counter = collections.Counter()
    for edge, weight in membership.items():
        for tag in edge:
            member_totals[tag] += weight

    def p(source: str, target: str) -> float:
        if source not in vocab:
            return 0.0
        base = ((counts.get((source, target), 0) + readout.ALPHA)
                / (totals.get(source, 0) + readout.ALPHA * len(vocab)))
        mass = member_totals.get(source, 0)
        if not mass:
            return base
        q = membership.get(frozenset((source, target)), 0) / mass
        return (1 - lam) * base + lam * q
    return p


def score_mixture(tags, region, membership, lam: float) -> dict:
    counts, totals, vocab = readout.transition_counts(tags, 0, region[0])
    start, stop = region[0] * EVENTS_PER_CYCLE, min(region[1] * EVENTS_PER_CYCLE, len(tags))
    contexts = [tags[t] for t in range(start, stop - 1)]
    observations = [tags[t + 1] for t in range(start, stop - 1)]
    return _score("mix", mixture_probability(counts, totals, vocab, membership, lam),
                  contexts, observations, vocab)


def measure(seed: int) -> dict:
    stream = null.null_stream(seed, null.CYCLES)
    data = readout.replay(seed, null.CYCLES, stream)
    scored = readout.arms_for(data["tags"], data["detections"], null.CYCLES)
    arms = scored["arms"]
    boundary = scored["boundaries"]
    tags = data["tags"]
    detections = data["detections"]
    frozen, _ = readout.evolve(detections, boundary["train"] - 1, boundary["window"], False)
    maintained, mutations = readout.evolve(detections, boundary["train"] - 1, boundary["window"], True)
    revision_only = round(readout.score(tags, boundary["holdout"], maintained, 0)["log_loss"]
                          - arms["A"]["log_loss"], 9)
    frozen_edges = readout.membership_counts(frozen)
    maintained_edges = readout.membership_counts(maintained)
    return {
        "seed": seed,
        "d_beta_only": round(arms["B"]["log_loss"] - arms["A"]["log_loss"], 6),
        "d_net": round(arms["C"]["log_loss"] - arms["A"]["log_loss"], 6),
        "d_revision_only": revision_only,
        "mutations": mutations,
        "composites": len(frozen),
        "mean_edges_frozen": round(statistics.fmean(len(edges) for edges in frozen.values()), 6),
        "mean_edges_maintained": round(statistics.fmean(len(edges) for edges in maintained.values()), 6),
        "mixture": {
            str(lam): {
                "B": round(score_mixture(tags, boundary["holdout"], frozen_edges, lam)["log_loss"]
                           - arms["A"]["log_loss"], 6),
                "C": round(score_mixture(tags, boundary["holdout"], maintained_edges, lam)["log_loss"]
                           - arms["A"]["log_loss"], 6),
            }
            for lam in LAMBDAS
        },
    }


def build(seeds=None) -> dict:
    seeds = list(null.NULL_SEEDS if seeds is None else seeds)
    rows = [measure(seed) for seed in seeds]
    decomposition = stored_decomposition()
    mixture = {}
    for lam in LAMBDAS:
        for arm in ("B", "C"):
            values = [row["mixture"][str(lam)][arm] for row in rows]
            mixture.setdefault(str(lam), {})[arm] = {
                "mean": round(statistics.fmean(values), 6),
                "sd": round(statistics.stdev(values), 6) if len(values) > 1 else None,
                "positive": sum(1 for value in values if value > 0),
            }
    revision_only = [row["d_revision_only"] for row in rows]
    net = round(statistics.fmean([row["d_net"] for row in rows]), 6)
    factorial = {
        "arms": {
            "A": {"composite_term": False, "revision": False, "mean_d": 0.0},
            "D": {"composite_term": False, "revision": True,
                  "mean_d": round(statistics.fmean(revision_only), 9),
                  "note": "structurally equal to A: with beta = 0 the membership term is multiplied by zero"},
            "B": {"composite_term": True, "revision": False, "mean_d": decomposition["beta_only_mean"]},
            "C": {"composite_term": True, "revision": True, "mean_d": net},
        },
        "effects": {
            "composite_given_frozen": decomposition["beta_only_mean"],
            "composite_given_revision": net,
            "revision_given_no_composite": round(statistics.fmean(revision_only), 9),
            "revision_given_composite": round(net - decomposition["beta_only_mean"], 6),
        },
        "structural_zero": ("a revision-only arm is the baseline; the 2x2 design has one empty cell, so the "
                            "interaction equals the revision effect and is not separately identifiable"),
        "interaction": round(net - decomposition["beta_only_mean"], 6),
        "prediction": ("A < B < C (revision adds a second penalty) is not what the null shows: C pays less than B, "
                       "because it holds fewer member edges, 2.571 to 0.783 per composite"),
    }
    return engine_stamp.stamp({
        "factorial": factorial,
        "kind": "v2_first_cell_handicap",
        "id": "V2-FIRST-CELL-HANDICAP-1",
        "date": "2026-11-16",
        "status": "PROTOCOL DIAGNOSTIC — WHERE THE NULL HANDICAP COMES FROM, NOT A CELL AND NOT A VERDICT",
        "source": {"null_artifact": str(NULL_ARTIFACT), "seeds": seeds, "cycles": null.CYCLES},
        "decomposition": decomposition,
        "mass": {
            "mean_edges_frozen": round(statistics.fmean(row["mean_edges_frozen"] for row in rows), 6),
            "mean_edges_maintained": round(statistics.fmean(row["mean_edges_maintained"] for row in rows), 6),
            "mean_composites": round(statistics.fmean(row["composites"] for row in rows), 6),
            "mean_mutations": round(statistics.fmean(row["mutations"] for row in rows), 6),
        },
        "mixture": mixture,
        "beta_zero": {"B": 0.0, "C": 0.0,
                      "note": "beta = 0 removes the membership term exactly, so d = 0 by construction; it is the baseline, not a fix"},
        "verdict": {
            "unbiased_possible": False,
            "reason": ("on a structureless world the true next-tag distribution is uniform, so any non-trivial tilt away "
                       "from the counts estimate raises expected log-loss by convexity; only beta = 0 is unbiased, and "
                       "that is arm A"),
            "reducible": True,
            "reducible_by": ("less added mass — a smaller beta or fewer member edges, which the revision rule already "
                             "does; a row-preserving mixture does not reduce it, because normalising a sparse member set "
                             "concentrates the tilt"),
        },
        "per_seed": rows,
        "note": ("the handicap is priced into the decision rule: the power diagnostic needs 0.001449 nats gross and an "
                 "observed mean difference of -0.000602 at 90% power, which already includes it."),
    })


def render_doc(record: dict) -> str:
    dec = record["decomposition"]
    mass = record["mass"]
    power = json.loads((REPO / "docs" / "v2_first_cell_power.json").read_text(encoding="utf-8"))
    fact = record["factorial"]
    mix_rows = "\n".join(
        "| %.1f | %.6f | %d/%d | %.6f | %d/%d |" % (
            float(lam), record["mixture"][lam]["B"]["mean"], record["mixture"][lam]["B"]["positive"],
            dec["n"], record["mixture"][lam]["C"]["mean"], record["mixture"][lam]["C"]["positive"], dec["n"])
        for lam in sorted(record["mixture"], key=float))
    return f"""# Where the null handicap comes from — a protocol diagnostic

**Status:** `{record['status']}`

**Question:** the null calibration measured `d = L_C − L_A = +{dec['net_mean']:.6f}` nats on structureless worlds. Is that
the β pseudo-counts, the revision rule, or an estimator that can be made unbiased before the cell runs?

## 1. The decomposition

Arm B is frozen membership and arm C is maintained membership, both at the same per-arm β and the same grid. So
`B − A` is the pseudo-count cost with no revision, and `C − B` is what revision adds.

| Component | Mean `d` (nats) | sd | Positive |
|---|---|---|---|
| β pseudo-counts, frozen (`B − A`) | **{dec['beta_only_mean']:.6f}** | {dec['beta_only_sd']:.6f} | {dec['beta_only_positive']}/{dec['n']} |
| Revision rule (`C − B`) | **{dec['revision_mean']:.6f}** | {dec['revision_sd']:.6f} | {dec['revision_positive']}/{dec['n']} |
| Net (`C − A`) | **{dec['net_mean']:.6f}** | | {dec['net_positive']}/{dec['n']} |

**The pseudo-counts are the handicap; the revision rule reduces it.** Frozen membership costs
{dec['beta_only_mean']:.6f} nats on a world with nothing to learn, and maintenance gives back
{abs(dec['revision_mean']):.6f} of it. The mechanism is visible in the mass: maintenance leaves
{mass['mean_edges_maintained']:.3f} member edges per composite against {mass['mean_edges_frozen']:.3f} when frozen, over
{mass['mean_composites']:.0f} composites — fewer edges, less added mass, less tilt. Both arms selected β =
{dec['betas'][0]} throughout, so the difference is not a different β.

### 1a. The factorial, and the structural zero

The four-arm decomposition has one cell that cannot be filled:

| Arm | Composite term | Revision | Mean `d` |
|---|---|---|---|
| A | no | no | 0.000000 (reference) |
| D | no | yes | **{fact['arms']['D']['mean_d']:.6f}** on all {dec['n']} seeds |
| B | yes | no | **{dec['beta_only_mean']:.6f}** |
| C | yes | yes | **{dec['net_mean']:.6f}** |

**D is A by construction.** With the composite term absent, β multiplies an empty membership table, so the revision rule
cannot reach the prediction; measured on every null seed, D − A is exactly 0.000000. That is not a failed arm — it is the
proof that revision acts only through the composite term.

The estimable effects are therefore two, and they add exactly: composite evidence given frozen membership
**{fact['effects']['composite_given_frozen']:.6f}**, revision given a composite term
**{fact['effects']['revision_given_composite']:.6f}**. The 2×2 has a structural zero, so the interaction equals the
revision effect ({fact['interaction']:.6f}) and is not separately identifiable.

**The predicted ordering `A < B < C` is not what the null shows.** C pays less than B: revision *reduces* the penalty by
{abs(fact['effects']['revision_given_composite']):.6f} — 35% of the pseudo-count cost — because it holds fewer member edges per composite,
{mass['mean_edges_frozen']:.3f} against {mass['mean_edges_maintained']:.3f}. The prior that β pseudo-counts dominate
is confirmed; the prior that revision adds a second penalty is reversed here.

## 2. Can it be made unbiased?

**No — not on a structureless world, for any readout that uses membership at all.** On such a world the true next-tag
distribution is uniform, so the counts estimate is already an unbiased-but-noisy estimate of it; *any* non-trivial tilt
away from that estimate increases expected log-loss by convexity. β = 0 removes the term exactly and is exactly arm A, so
the only unbiased setting is the baseline.

That claim was tested against a **row-preserving mixture**, `p' = (1−λ)·p_counts + λ·q_member`, where `q_member` is the
normalised membership allocation. It keeps each source's total probability at one instead of adding mass — the construction
most likely to be unbiased if row sums were the problem.

| λ | Frozen, mean `d` | positive | Maintained, mean `d` | positive |
|---|---|---|---|---|
{mix_rows}

Every non-trivial variant is still positive, and the bias **rises** with λ, as convexity predicts. Row-preservation does
not help: at λ = 0.1 the maintained arm's mixture (+{record['mixture']['0.1']['C']['mean']:.6f}) is worse than its additive form (+{dec['net_mean']:.6f}), because normalising
a sparse member set — {mass['mean_edges_maintained']:.3f} edges per composite — concentrates the tilt instead of diluting it.

**The handicap is the price of the treatment, not a calibration defect.** It is reducible by adding **less mass** — a
smaller β, or fewer member edges, which is what the revision rule already does — but every reduction also shrinks the tilt
that could help on a structured world, and the null cannot measure that trade. A matched control on the same null
worlds separates mass from selection: at equal total mass a random frozen allocation is cheaper than maintained, and it
is still cheaper at equal mass and non-empty composite count, so the revision offset is a mass effect and the retained
selection is not a recency advantage ([`V2-FIRST-CELL-MASS-MATCH`](V2-FIRST-CELL-MASS-MATCH.md)).

## 3. What this means for the cell

The handicap is already priced into the decision rule. The power diagnostic at the same null noise requires a gross benefit
of **{power['mde']['0.9']:.6f}** nats for 90% power, which corresponds to an observed mean difference of **{power['required_mean_d']['0.9']:.6f}** nats: the benefit has
to clear the handicap before the observed difference turns negative at all.

The factorial separates the two outcomes cleanly: the handicap is **β-dependent** — removing the composite term returns
exactly to the baseline on every seed — so there is no implementation asymmetry and no repair is indicated before the cell.
The alternative — subtracting a null-calibrated offset from `d` — would make the statistic zero-mean on null worlds **by
construction**, but the null worlds are structureless and their detection statistics are not the cell's, so the offset is
not transferable. It would also be a protocol change after signature, and it would hide the cost rather than report it.
**Recommendation: keep the readout as pre-registered and report the handicap beside the result; do not debias it.**

## 4. Reproduction

```bash
python -m benchmarks.v2_first_cell_handicap --write    # artifact and this page
python -m benchmarks.v2_first_cell_handicap --check    # decomposition arithmetic, mixture sign, page freshness
```

Artifact: [`v2_first_cell_handicap.json`](v2_first_cell_handicap.json).
"""


def check() -> None:
    record = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    if render_doc(record) != PAGE.read_text(encoding="utf-8"):
        raise SystemExit("handicap page is stale; rebuild with --write")
    decomposition = stored_decomposition()
    if abs(record["decomposition"]["beta_only_mean"] - decomposition["beta_only_mean"]) > 1e-6:
        raise SystemExit("stored decomposition no longer matches the null artifact")
    if abs(record["decomposition"]["beta_only_mean"] + record["decomposition"]["revision_mean"]
           - record["decomposition"]["net_mean"]) > 1e-6:
        raise SystemExit("the decomposition does not add up")
    if record["verdict"]["unbiased_possible"] is not False:
        raise SystemExit("the verdict no longer says no")
    for lam, arms in record["mixture"].items():
        for arm, row in arms.items():
            if row["mean"] <= 0:
                raise SystemExit("a non-trivial mixture is no longer positive at lambda %s arm %s" % (lam, arm))
    small = build(seeds=null.NULL_SEEDS[:2])
    if len(small["per_seed"]) != 2:
        raise SystemExit("small rebuild did not cover both seeds")
    print("check: decomposition adds up, every non-trivial mixture is positive, page is fresh")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify the decomposition and page freshness")
    parser.add_argument("--write", action="store_true", help="measure and write artifact and page")
    args = parser.parse_args()
    if args.check:
        check()
        return 0
    if args.write:
        record = build()
        ARTIFACT.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        PAGE.write_text(render_doc(record), encoding="utf-8")
        print(json.dumps({"decomposition": record["decomposition"], "mass": record["mass"],
                          "mixture": record["mixture"], "verdict": record["verdict"]}, indent=1))
        return 0
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
