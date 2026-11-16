# Where the null handicap comes from — a protocol diagnostic

**Status:** `PROTOCOL DIAGNOSTIC — WHERE THE NULL HANDICAP COMES FROM, NOT A CELL AND NOT A VERDICT`

**Question:** the null calibration measured `d = L_C − L_A = +0.000847` nats on structureless worlds. Is that
the β pseudo-counts, the revision rule, or an estimator that can be made unbiased before the cell runs?

## 1. The decomposition

Arm B is frozen membership and arm C is maintained membership, both at the same per-arm β and the same grid. So
`B − A` is the pseudo-count cost with no revision, and `C − B` is what revision adds.

| Component | Mean `d` (nats) | sd | Positive |
|---|---|---|---|
| β pseudo-counts, frozen (`B − A`) | **0.001312** | 0.000927 | 18/20 |
| Revision rule (`C − B`) | **-0.000465** | 0.000641 | 4/20 |
| Net (`C − A`) | **0.000847** | | 18/20 |

**The pseudo-counts are the handicap; the revision rule reduces it.** Frozen membership costs
0.001312 nats on a world with nothing to learn, and maintenance gives back
0.000465 of it. The mechanism is visible in the mass: maintenance leaves
0.783 member edges per composite against 2.571 when frozen, over
126 composites — fewer edges, less added mass, less tilt. Both arms selected β =
1 throughout, so the difference is not a different β.

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
| 0.1 | 0.000572 | 17/20 | 0.001546 | 19/20 |
| 0.2 | 0.002357 | 19/20 | 0.004937 | 20/20 |

Every non-trivial variant is still positive, and the bias **rises** with λ, as convexity predicts. Row-preservation does
not help: at λ = 0.1 the maintained arm's mixture (+0.001546) is worse than its additive form (+0.000847), because normalising
a sparse member set — 0.783 edges per composite — concentrates the tilt instead of diluting it.

**The handicap is the price of the treatment, not a calibration defect.** It is reducible by adding **less mass** — a
smaller β, or fewer member edges, which is what the revision rule already does — but every reduction also shrinks the tilt
that could help on a structured world, and the null cannot measure that trade.

## 3. What this means for the cell

The handicap is already priced into the decision rule. The power diagnostic at the same null noise requires a gross benefit
of **0.001449** nats for 90% power, which corresponds to an observed mean difference of **-0.000602** nats: the benefit has
to clear the handicap before the observed difference turns negative at all.

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
