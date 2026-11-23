# Choosing the temporal-decay fix: a measured comparison of the four options

**Status: measurement for an owner decision, 2026-11-06. The engine is unchanged.**
`docs/RERUN-0.12.0.md` recorded four candidate fixes for the 0.12.0 collapse and
applied none, because changing the selection path is an engine decision (rules
2 and 12). This document replaces the plausibility of each story with the same
run of each option.

**Update (2026-11-06): this recommendation has not been adopted.** The owner
kept Option 2r as a lead candidate. A confirmation run with a threshold
calibrated on separate seeds and held-out low/medium/high-degree worlds is
preregistered in `docs/DECAY-FIX-CONFIRMATION-PREREGISTRATION.md`; the engine
is unchanged until it passes.

Harness: `benchmarks/prediction_decay_options.py`. Artifact:
`docs/prediction-decay-options.json`. One seed (`20261023`), the Tier-1 matrix's
own stimulus (`L1_hub1_t3_disjoint`), `PYTHONHASHSEED=0`, four worker processes.

## What each arm changes

| arm | strength | decay | threshold |
|---|---|---|---|
| shipped | `count / source_frequency` | 0.95 every cycle | 0.30 |
| opt1 | unchanged | 0.95, but edges reinforced this cycle are restored | 0.30 |
| opt2 | `count / out_counts[source]` (the `transition_prob` the engine already computes) | 0.95 | 0.30 |
| opt2r | `count / out_counts[source]` | 0.95 | 0.15 |
| opt3 | unchanged | 0.99 | 0.30 |
| opt4 | unchanged | 0.95 | 0.15 |

`opt2r` is not a separate idea from opt2; it exists because a redefined strength
is not on the shipped threshold's scale. Running both says whether the
definition is viable and what changing it costs.

The engine files are not edited. `opt1` replaces the decay call for the probe's
own instance and `opt2` rescales candidates before storage, both by subclassing,
as `benchmarks/ablation_study.py` does.

## Protocol

* **Stationary:** 300 cycles of one design. The liveness gate is the one
  `docs/COMPARISON-0.9-0.12-PREREGISTRATION.md` now requires: at least one
  theory in the final 10% of cycles and mean beliefs of at least 2.
* **Shift:** 80 cycles of design A, then 40 of a relabelled
  design B with a disjoint vocabulary, so a build that keeps asserting A is
  failing to revise.
* **Scoring:** stable predictions are compared with the world's own directed
  edge set (30 edges in A, 30 in B), derived from the
  stimulus by the engine's own lookback rule. Labels score the selector; they
  never enter it.

## Results

Theories at cycles 80, 160 and 300; the last cycle with any theory; stable
predictions and their precision and coverage of the world's edges at cycle 300;
B-edge coverage 20 and 40 cycles after the shift; share of stable edges still
belonging to A at the end.

| arm | th80 | th160 | th300 | last live | stable | precision | coverage | B+20 | B+40 | A share |
|---|---|---|---|---|---|---|---|---|---|---|
| shipped | 0 | 0 | 0 | 58 | 0 | n/a | 0.0 | 0.7 | 0.6 | 0.0 |
| opt1: decay only unreinforced | 5 | 0 | 0 | 97 | 7 | 1.0 | 0.2333 | 0.6333 | 0.6 | 0.0 |
| opt2: transition prob., th 0.30 | 0 | 0 | 0 | 11 | 12 | 1.0 | 0.4 | 0.4 | 0.4 | 0.4286 |
| opt2r: transition prob., th 0.15 | 5 | 5 | 5 | 299 | 18 | 1.0 | 0.6 | 0.7 | 0.6 | 0.4706 |
| opt3: factor 0.99 | 5 | 5 | 0 | 253 | 12 | 1.0 | 0.4 | 0.6 | 0.5 | 0.4444 |
| opt4: threshold 0.15 | 5 | 0 | 0 | 147 | 10 | 1.0 | 0.3333 | 0.7 | 0.9 | 0.0 |

## What each option actually does

**Shipped.** No theory after cycle 58, no stable prediction left
at 300. This is the failure being fixed.

**Option 1 — decay only unreinforced edges.** The longest-lived of the cheap
attempts, and still dead: theories through cycle 97, 7
stable predictions at 300, coverage 0.2333. Removing the ratchet on edge
counts is not sufficient, because the survival filter reads the *stored
candidate strength*, and a candidate is refreshed only if it wins one of the 40
prediction slots in a cycle. Edges can stay alive while their candidate is
starved by the allocation order. The arm is also a harness approximation
(count-increase detection plus an SQL restore), so its failure is evidence about
this implementation, not a proof that the idea cannot work.

**Option 2 at the shipped threshold.** 12 stable predictions at
300 and **zero theories from cycle 80 onward**. This is the important negative
result: transition probability is roughly `1 / out-degree`, so a threshold of
0.30 calibrated on `count / source_frequency` throws away almost the whole
graph. A definition change is not a drop-in; it moves the scale.

**Option 2r — transition probability, threshold recalibrated.** The only arm
alive at 300: five theories, fifteen beliefs, 18 stable
predictions, precision 1.0, coverage 0.6. It also revises:
B coverage reaches 0.7 twenty cycles after the shift and
0.6 forty cycles after, while the share of stable edges still
belonging to A falls to 0.4706. This is the only arm that is
*asymptotically* stationary, and the reason is structural: numerator and
denominator are decayed by the same factor, so the ratio is an exponentially
weighted transition frequency, and uniform decay cancels out of it while both
counts stay above the minimum count.

**Option 3 — slower decay (0.99).** Alive at 160, dead at 300: last theory at
cycle 253. It is a delay, not a fix, and the arithmetic says it must
be: with per-cycle arrivals `a` and factor `f`, an edge's count reaches an
equilibrium near `a / (1 - f)` while the source frequency keeps growing linearly,
so the ratio still tends to zero for every `f < 1`. The only difference between
0.95 and 0.99 is where the crossing happens.

**Option 4 — lower threshold (0.15).** Alive at 80, dead by 160, last theory at
cycle 147. The strength keeps declining; the threshold only moves the
crossing later. It hides the monotone trend, which is what the option list
already said it would do, and the measurement confirms it.

## Recommendation (proposed, not adopted)

**Adopt option 2 as a single engine decision, with the threshold recalibrated to
0.15 in the same amendment — and treat the pair as one mechanism change, not
two.** No other arm is alive at 300. For options 3 and 4 the outcome is forced:
any factor below 1 leaves a ratio whose denominator grows without bound. Option 1
is a different case — dead in this implementation, but not refuted by it.

The evidence for it, in order of weight:

1. It is the only arm that passes the liveness gate at 300 cycles (five
   theories, fifteen beliefs, 18 stable predictions at 300).
2. Its assertions are the world's edges: precision 1.0, coverage
   0.6 — the best coverage of any arm at 300, and no schema terms
   in the stable set.
3. It revises: 0.6 of B's edges within forty cycles, with A's share
   down to 0.4706.
4. It adds no state and no parameter sweep: one expression at extraction
   (`cand_strength = transition_prob`, already computed at
   `organica/sleep_extraction.py:453`) and one constant.

What the owner should weigh before accepting it:

* **The threshold moves with the definition.** At 0.30 the same mechanism
  produces zero theories. The 0.15 value is not a free parameter to tune later;
  it is part of the change, and it currently equals `DEATH_THRESHOLD`, so
  "stable" and "not yet dead" coincide at that boundary. If that coupling is
  unwanted, the threshold should be set by a separate calibration and the death
  boundary moved — a second, separately recorded decision.
* **Transition probability penalises hubs.** A source with twelve outgoing
  edges caps near 0.083; `organica/scale_streams.py:88-98` already records that
  the survival filter eats degree-12 hubs under the current ratio. The fix may
  invert that specific problem rather than solve it. A hub-degree sweep is
  required before claiming the fix generalises, and it was not run here.
* **One seed, one stimulus, 300 cycles.** This is enough to rank the four
  options and not enough to characterise the engine. The confirmation is the
  3,000-cycle matrix rerun, which is downstream of the decision.
* **Option 1 is not refuted, only out-implemented.** If the owner prefers to
  keep `count / source_frequency`, the next thing to measure is whether the
  candidate-refresh budget, not the decay, is what starves it — the arm's own
  numbers point there.

If the owner wants the smallest possible change instead, option 3 is the
cheapest delay but cannot survive a 3,000-cycle run by the argument above, and
recommending it would be recommending a slower version of the defect.

## Reproduction

```bash
PYTHONHASHSEED=0 PYTHONPATH="$PWD" .venv/bin/python benchmarks/prediction_decay_options.py
```

Writes `docs/prediction-decay-options.json`; exits non-zero if the shipped arm
does not die or if no option survives, so the probe can fail in both directions.
