# The scaling ladder: resolution or replication?

**Status:** protocol §1–§6 fixed before the run. §7 records what the run returned.

## 1. The question

Two different problems look the same from a distance:

- a run sees **too little of the system** to establish what it is doing;
- a run sees enough, but the experiment is **not repeated enough** to establish that the behaviour is real.

Only the first is fixed by making runs bigger. The second is fixed by running more of them, and spending on the first while the second binds buys nothing. This document is the measurement that separates them, not a larger experiment.

## 2. The unit that is scaled

**The scored window.** Formation is 110 cycles in every cell, so every run is the *same exposure* and a different amount of one world is scored. The alternative — a longer formation stream — is a different intervention (more learning, not more observation) and is left untested; conflating the two would make it impossible to say which one moved the estimate.

| Scale | Scored window (cycles) | Pairs | Purpose |
| --- | --- | --- | --- |
| `1x` | 150–200 | 399 | the frozen design's own primary window |
| `2x` | 150–250 | 799 | measurement stability |
| `4x` | 150–350 | 1,599 | emerging pattern |
| `8x` | 150–550 | 3,199 | does it stabilise |
| `16x` | 150–950 | 6,399 | breakdown or unexpected behaviour |

These are relative scales chosen for the ladder, not validated sample sizes.

## 3. The endpoint

The one this project reports: the **paired** difference in per-event-pair log-loss between the frozen Organica readout and the strongest simple comparator (the comparator family is chosen by tuning loss, as in the frozen studies, so no baseline is handicapped).

One event pair is one observation. Positive means the readout's loss is lower. The `1x` cell asserts that the per-pair means average to the same aggregate the frozen endpoint reports; if they do not, the ladder is measuring something else and the run stops.

## 4. What is measured at each scale

1. **Effect size** — the mean delta and its spread across worlds.
2. **Within-run error** — a cluster bootstrap over contiguous quarters of the scored window. Quarters rather than pairs because consecutive observations of one world are not independent; the ratio of the block error to the i.i.d. error is reported, so an over-optimistic per-observation error bar is visible rather than assumed.
3. **Consistency** — the delta in each quarter, and how many quarters share the sign of the whole-window delta.
4. **Between-run spread** — the standard deviation of the same delta across five worlds.
5. **Cost** — pairs scored and wall time.

## 5. The decision rule, fixed before the run

Let `rho` be the mean within-run standard error divided by the between-run standard deviation of the delta at the same scale.

| `rho` at `1x` | Reading |
| --- | --- |
| ≤ 0.50 | **replication-limited** — a run resolves its own estimate well; the spread is between worlds, and only more runs reduce it |
| ≥ 1.00 | **resolution-limited** — one run does not resolve its own estimate; more observations per run is the binding constraint |
| between | both — the ladder's slope says which direction buys more |

The scaling curve is the slope of `log(within-run SE)` against `log(pairs)`. Independent observations give **−0.5** (four times the data halves the error). It is reported against a pre-committed band of ±0.15: a shallower slope means the observations are clustered, a steeper one means a small part of the window was carrying the estimate.

Two pre-committed obligations, so the ladder cannot be read loosely:

- **A flat result is a defect until proven otherwise.** If the delta or the error does not move across the ladder, the first reading is that the axis is dead, and the run is reported as such.
- **The number of runs needed is derived, not asserted.** From `sqrt(between²/n + within²)`, the n that puts total error at half the between-run spread is computed — and reported as *not achievable* when the within-run term alone already exceeds it.

## 6. Seeds

`20270501`–`20270505`: a fresh methodology block. It is disjoint from every study block, and the module refuses a design or confirmatory seed before it opens a database. The ladder mints no scientific claim and cannot authorise one.

## 7. What the run returned

Five worlds, 150–950 cycles, 149.9 s. Artifact: `docs/scaling_ladder.json`. The shorter worlds were verified to be prefixes of the longest, so every scale scores the same world and only the amount differs.

| Scale | Pairs | Delta | Within-run SE | Between-world SD | `rho` | Worlds positive | Quarters same sign |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `1x` | 399 | +0.007468 | 0.008830 | 0.012157 | 0.726 | 3 / 5 | 14 / 20 |
| `2x` | 799 | +0.003536 | 0.003804 | 0.012849 | 0.296 | 4 / 5 | 14 / 20 |
| `4x` | 1,599 | +0.002085 | 0.003265 | 0.011831 | 0.276 | 4 / 5 | 13 / 20 |
| `8x` | 3,199 | +0.003233 | 0.002578 | 0.010614 | 0.243 | 4 / 5 | 13 / 20 |
| `16x` | 6,399 | +0.004817 | 0.001450 | 0.010247 | 0.142 | 4 / 5 | 15 / 20 |

### The axis is live, and it is the curve that was expected

Within-run error falls from 0.008830 to 0.001450 while pairs grow 16×: a 6.09× reduction. The fitted exponent is **−0.577** with r² **0.928**, inside the pre-committed band (expected −0.5 ± 0.15). The block-to-i.i.d. ratio runs 0.54–0.85 across scales, so contiguous quarters are *less* variable than independent draws would be — there is no positive temporal clustering inflating the error, and a per-observation error bar would not have been optimistic.

### The between-world spread does not scale

Between-world SD is 0.012157 at `1x` and 0.010247 at `16x`. Sixteen times the data moved it by 16 %, which is inside what five worlds can resolve. `rho` therefore falls 0.726 → 0.142 for one reason only: the numerator got smaller. **No window length reduces the between-world term**, because it is a property of the worlds, not of the window.

### What is derived from it

Total error at n runs is `sqrt(between²/n + within²)`. Setting it to half the between-world SD:

| Scale | Target | Runs required |
| --- | --- | --- |
| `1x` | 0.006078 | **not reachable** — the within-run term alone (0.008830) exceeds it |
| `2x` | 0.006424 | 6.16 |
| `4x` | 0.005915 | 5.75 |
| `8x` | 0.005307 | 5.24 |
| `16x` | 0.005124 | 4.35 |

At the frozen window no number of runs reaches the target, because one run's own noise already floors it. From `2x` on, six worlds are enough and further window growth buys precision that is not needed.

### The verdict, and why "both" is not a hedge

By §5 the `1x` cell is **both**: `rho` 0.726 sits between the two thresholds. The substance behind that label is firmer than the label:

- at `1x` a run's own standard error (0.008830) is **1.18× its own delta** (0.007468), so a single run cannot establish the sign of what it measured;
- the derived n is *unreachable* at `1x` — replication cannot rescue the frozen window;
- from `2x` (100 cycles) on, `rho` is ≤ 0.30, which is replication-limited territory, and the between-world spread is flat.

So the two diagnoses are not alternatives here, they are **ordered**: fix resolution once, then spend everything else on replication. Ordering them the other way — running more worlds on the frozen 50-cycle window — would multiply an estimate that each run cannot resolve on its own.

### What it does not say

- **Not that the readout beats the comparator.** At `16x` the delta is +0.004817 with a between-world SD of 0.010247 over five worlds: a pooled standard error of 0.004582, about 1.05× the delta. The sign is positive in 4 of 5 worlds and 15 of 20 quarters, which is a description of five worlds, not evidence of an advantage. One world (20270504) is negative at every scale.
- **The between-world SD is itself uncertain** at n = 5, and it is the denominator of every `rho` here.
- **The `1x` cell is not the frozen world's 150–200 window**: the law is held at `LAW_R0` for the whole run so the generating process cannot rotate inside a scored window. That is a declared difference, listed in the artifact's caveats.
- **Exposure was never varied.** A longer formation stream is a different intervention and is untested.

### The answer

The project is not short of observations in the way that a bigger run would fix. It is short of **worlds**, with one qualification that matters: the frozen 50-cycle window is too short for a single run to resolve its own estimate, and more seeds on that window cannot repair it. The cheap remedy is one measurement decision — score at least `2x` (100 cycles) — after which the binding constraint is the number of independent worlds, and it stays that way at every window length tested, because the between-world spread does not shrink with the window.

## 8. Added after the run: does a run identify its own sign?

This section was written **after §7 was read**, at the owner's request, and it re-analyses the same five worlds' stored cells (`python -m benchmarks.scaling_ladder --reanalyse`). It runs no world, spends no seed and touches no study block. It is a measurement-design diagnostic: **§1–§6 and §7 stand as committed, and nothing here re-scores the verdict**, which was produced once by the rule in §5.

### The criterion

Let `p(w, s)` be the probability that world `w`'s run at window `s` lands on the same side of zero as **that world's true effect**, not as the block average. It is estimated by Monte Carlo (20,000 replicates), propagating both uncertainties:

1. draw the world's effect from its **reference cell** — the widest scale *other than* the one being judged — with that cell's own standard error;
2. draw the run's estimate from `N(effect, se)` with `se` the block-bootstrap error at scale `s`;
3. count sign agreement.

The leave-one-out reference is the point of the exercise: judging `16x` against `16x` would make the widest row perfect by construction, so `16x` is judged against `8x` and is the conservative row. The 0.90 target is a convention fixed for this section, not a validated requirement.

### The numbers

| Scale | Cycles | Mean `p` | Min world | Max world | Worlds ≥ 0.90 | Sign of the block | Plug-in mean | Φ(pooled ratio) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `1x` | 200 | 0.855 | 0.780 | 0.917 | 1 / 5 | 0.694 | 0.836 | 0.801 |
| `2x` | 250 | 0.977 | 0.917 | 0.997 | 5 / 5 | 0.780 | 0.894 | 0.824 |
| `4x` | 350 | 0.961 | 0.822 | 1.000 | 4 / 5 | 0.761 | 0.913 | 0.739 |
| `8x` | 550 | 0.974 | 0.925 | 1.000 | 5 / 5 | 0.770 | 0.949 | 0.895 |
| `16x` | 950 | 0.944 | 0.853 | 1.000 | 3 / 5 | 0.720 | 0.990 | 1.000 |

| World | `1x` | `2x` | `4x` | `8x` | `16x` | First window at 0.90 |
| --- | --- | --- | --- | --- | --- | --- |
| 20270501 | 0.79 | 0.92 | 0.82 | 0.92 | 0.85 | `2x` |
| 20270502 | 0.89 | 1.00 | 1.00 | 1.00 | 1.00 | `2x` |
| 20270503 | 0.78 | 1.00 | 0.99 | 1.00 | 1.00 | `2x` |
| 20270504 | 0.90 | 0.98 | 0.99 | 1.00 | 1.00 | `2x` |
| 20270505 | 0.92 | 0.99 | 1.00 | 0.95 | 0.87 | `1x` |

The 0.90 target is reached for every world from `2x`. At `1x` it is reached for one world in five: the frozen window leaves a run unable to report its own world's sign with the reliability the project would want to assume.

### What it corrects about the ratio

`SE / delta` is a t-statistic, not a probability. Through Φ its values read **0.80, 0.82, 0.74, 0.79, 0.62** at the five scales — so a ratio above one (the 200-cycle row, 1.57) is not “a coin flip”, it is about 0.74, and a ratio of 1.18 is not a failure, it is 0.80. Two further problems with reading the threshold off that ratio:

- **The numerator moves for reasons that have nothing to do with the window.** The ratio falls from 1.57 at `4x` to 0.80 at `8x` because the *pooled* delta rose (0.002085 → 0.003233), not because the window improved. The pooled delta is an average of five noisy world effects; dividing it by a shrinking denominator mixes between-world variation into a within-run criterion.
- **It separates neither question.** Per-world, the plug-in numbers are optimistic (0.894 at `2x` against 0.977 propagated); the propagated figure is the one that answers “would this run have told me what happened in this world?”.

### Two criteria, two answers

- **Does a run resolve its own world's sign?** Yes from `2x`: mean `p` 0.977, every world at or above 0.917. This is the criterion the owner proposed, and `2x` meets it.
- **Does a run agree with what the block says?** No, and no window fixes it: 0.694 → 0.780 → 0.761 → 0.770 → 0.720. It is *below* the per-world figure at every scale and it falls again at `16x`. That is the between-world wall expressed as a probability: one world's effect is negative, so a run in it can be perfectly resolved and still disagree with the average. More observations of that world will never make it agree.

So the two scalings are not merely different in efficiency; they have **different ceilings**. Per-world resolution has a ceiling of 1 and buys it with window length. Block-level agreement has a ceiling set by the spread of true effects across worlds, and only more — or different — worlds move it.

### The recommendation, amended

Score at `2x` (100 cycles) — the smallest window where every tested world reaches 0.90 — and stop lengthening the window for *this* reason. The number is unchanged from §7; the **argument** is replaced. It now rests on the sign criterion, not on `rho ≤ 0.30`, and it survives the test the owner applied.

Two cautions belong with it. The relation is **not monotone**: `4x` (0.961) and `16x` (0.944) sit below `2x` (0.977). Part of that is mechanical — `16x`'s reference is `8x` and each scale's SE is itself estimated — and all of it is inside what five worlds can separate, so it is disclosed rather than smoothed. And 0.90 is a convention: at 0.95, `2x` would not qualify (its minimum world is 0.917).

### What this analysis cannot do

- **It is the same five worlds re-analysed.** It inherits their selection and is not out of sample; it can refine a measurement decision, not create evidence.
- **The reference is an estimate too.** Treating the world's effect as normal around its reference cell means a biased reference biases both the number and the sign it is judged against.
- **It says nothing about conditions.** The third axis — whether the effect survives a change of generating configuration — is still untouched, as §8 of the artifact's `not_measured` list records.

**Status, added with §9:** provisional, not a validated minimum. The audit below shows that the reference rule and the 0.90 target each move which worlds qualify, so the number is a declared convention rather than an established requirement.

## 9. Audit of the sign estimator

Written after the owner challenged §8 on two grounds: that 0.90 is a convention introduced **after** the
run, and that the reference estimate is not independent of the estimate it judges, because the scored
windows are nested. Both objections are correct in principle. The audit is computed from the stored cells
of the same five worlds (`python -m benchmarks.scaling_ladder --audit`, artifact `docs/sign_audit.json`);
no engine ran and no seed was spent.

### What the estimator actually computes

`p` is a **posterior-predictive** agreement probability, not a coverage guarantee. The world's effect is
drawn from `N(delta_ref, se_ref²)`, a run's estimate from `N(effect, se_s²)`, and `p` is the frequency with
which the two signs agree. Conditional on the effect this is exactly `Phi(|effect| / se_s)`, so the only
substantive modelling choice is how the effect is known. §8 named that choice; this section measures how
much it matters, and how far the number can be trusted.

### 1. The nesting is real, and it does not enter this number

| Judged | Reference | Pairs | Share of the larger | Correlation if pairs independent |
| --- | --- | --- | --- | --- |
| `1x` | `16x` | 399 / 6,399 | 6.2 % | 0.164 |
| `2x` | `16x` | 799 / 6,399 | 12.5 % | 0.381 |
| `4x` | `16x` | 1,599 / 6,399 | 25.0 % | 0.444 |
| `8x` | `16x` | 3,199 / 6,399 | 50.0 % | 0.562 |
| `16x` | `8x` | 6,399 / 3,199 | 50.0 % | 0.562 — the judged window is the *larger* one |

Both windows start at cycle 150, so one contains the other and their union is the longer one. With
independent pairs the covariance is therefore the variance of the longer window, which caps the
correlation at `sqrt(short / long)` — 0.16 to 0.56 here.

**Why it does not bias the reported probability:** conditional on a world's effect, a run's error is its
own. The reference's likelihood depends only on its own standard error, so `p = E[Phi(|effect| / se_s)]`
contains no covariance term. What the nesting *does* affect is inference **across** rows: they are five
dependent comparisons of the same worlds, so the §7/§8 curve cannot be read as a monotone dose-response,
and `16x` is the row where the containment reverses.

Two limits of this audit. The correlations are the independent-pairs case, while the measured block/iid
ratio (0.54–0.85) says consecutive pairs are not independent, so they are order-of-magnitude rather than
exact. And each scale's standard error comes from its own quarter bootstrap, so the five rows are not one
joint resampling, and no joint covariance is available to test.

### 2. The reference rule moves the decision

| Reference rule at `2x` | `p` | Worlds at 0.90 |
| --- | --- | --- |
| leave-one-out (`16x`) | 0.976 | 5 / 5 |
| fixed `8x` | 0.946 | 3 / 5 |
| fixed `4x` | 0.898 | 3 / 5 |

So "every world clears 0.90 at 100 cycles" holds **only against the most precise reference available**.
With a noisier reference it is three worlds of five. The §8 figure is therefore conditional on the
reference rule, and that condition belongs in the claim.

### 3. Against known truths the estimator is calibrated, conservatively

Simulated worlds with fixed true effects: each reference cell is the truth plus the reference window's
own error, and fresh runs are drawn from the truth. The reported probability is compared with the
frequency that actually occurred (2,000 runs per cell; the simulated SEs are this run's measured values,
asserted against the artifact).

| Effect (`1x` SE units) | Reported `1x` | Realised `1x` | Reported `16x` | Realised `16x` |
| --- | --- | --- | --- | --- |
| 0.25 | 0.621 | 0.588 | 0.885 | 0.935 |
| 0.50 | 0.694 | 0.682 | 0.944 | 1.000 |
| 1.00 | 0.838 | 0.830 | 0.997 | 1.000 |
| 2.00 | 0.967 | 0.978 | 1.000 | 1.000 |
| 4.00 | 1.000 | 1.000 | 1.000 | 1.000 |

Worst error **0.068**, and it runs *conservative* for resolved effects: the estimator under-reports about
as often as it over-reports. The five worlds sit at 1.6–34 SE at `16x`, inside that regime.

The zero-effect cells are **excluded, not scored**. With no true sign there is nothing to be right about,
and there the estimator returns 0.856 at `16x` against a realised frequency of 0.497. That value is kept
in the artifact as a diagnostic of the degenerate case, and it is the reason a sentence like "p = 0.9 means
90 % of runs get it right" only means anything for a non-zero effect.

### 4. The threshold is a convention, and it selects the window

| Target | `1x` | `2x` | `4x` | `8x` | `16x` |
| --- | --- | --- | --- | --- | --- |
| 0.80 | 3 / 5 | 5 / 5 | 5 / 5 | 5 / 5 | 5 / 5 |
| 0.85 | 3 / 5 | 5 / 5 | 4 / 5 | 5 / 5 | 5 / 5 |
| 0.90 | 1 / 5 | 5 / 5 | 4 / 5 | 5 / 5 | 3 / 5 |
| 0.95 | 0 / 5 | 4 / 5 | 4 / 5 | 3 / 5 | 3 / 5 |

`2x` is the smallest window clearing 0.90, and it clears 0.95 for four worlds of five — never for all
five. None of these thresholds is validated; the table shows how much the answer depends on the one
chosen.

### 5. Status: provisional

The estimator measures what it says it measures, and the nesting does not bias it. What the audit does
**not** establish is that 100 cycles is a *minimum*, because the target is chosen, the reference rule is
chosen, and both move which worlds qualify. So:

- 100 cycles is a **provisional resolution target**, under a declared reference rule and a declared
  threshold — not a validated requirement.
- A study adopting it should name both, and report the per-world minimum rather than the mean.
- "A run resolves its own world after 100 cycles" is supported. "And therefore the effect is
  established" is not: block-level agreement stays near 0.78, and only more worlds move it.

### What would change this

A synthetic world family with **known** effects, where a fresh run's sign is checked against the truth
directly rather than against a reference estimate. The calibration in §3 is the engine-free first step;
a world generator that gives the truth by construction is the second. Until then the five-world
limitation stands, and no confirmatory seed has been spent.
