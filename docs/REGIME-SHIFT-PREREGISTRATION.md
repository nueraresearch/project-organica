# Phase I — Regime-Shift Detection Preregistration

**Status: frozen before any Phase I campaign output is generated.** This
protocol tests whether Organica's existing prediction structures support
faster detection of a change in a synthetic environment than simple
sequential baselines. It does not modify the cognitive engine or the paused
longitudinal study.

## Research question and hypothesis

When an environment changes its generating rule after a stable learning
period, does Organica detect the change sooner than (1) a first-order Markov
model and (2) a recency-decayed transition-association model, while keeping
false alarms low in a stationary control?

The primary hypothesis is deliberately task-specific: in at least one of two
predefined generator families, Organica will reduce restricted detection
delay by at least **2 cycles** versus **each** baseline, with both paired
97.5% confidence intervals for baseline-minus-Organica delay wholly above
zero and with each model's empirical stationary-control false-alarm rate at
or below **10%**. The 97.5% intervals apply a Bonferroni adjustment for the
two generator-family opportunities to meet the primary claim. A failure to
meet this rule is not evidence that the
architecture has no comparative advantage on other tasks.

## Synthetic worlds

Each world contains 90 cycles, with 8 trials per cycle. A trial is presented
as two separate events: a context tag followed by an outcome tag. All tags
have at least four letters. Models receive only these event strings. The
generator retains the regime label for scoring; labels are never ingested by
any model.

Two generator families create different kinds of change:

1. **Cause-mixture switch.** A trial's context is `causea` or `causeb`. Before
   cycle 60, `causea` is selected with probability 0.85; after the shift it is
   selected with probability 0.15. The selected cause is followed by one of
   its four fixed outcome tags (`amber`–`maple` or `indigo`–`yarrow`). With
   probability 0.10, the outcome is instead sampled from the eight-tag
   outcome vocabulary. This changes cause prevalence and the context/outcome
   joint frequencies.
2. **Mapping-swap.** One of four context tags is selected uniformly. In the
   first regime it predicts its paired outcome (`amber`, `birch`, `cedar`,
   `maple`); after the shift, the mapping is permuted to
   (`birch`, `amber`, `maple`, `cedar`). With probability 0.10, the outcome
   is sampled uniformly from those four outcomes. Context and outcome
   marginals remain uniform; the conditional mapping changes.

For each family, run **20 shifted worlds** (seeds 20261201–20261220) and
paired **stationary controls** with the same seeds and pre-shift rule held for
all 90 cycles. The seed is the only source of stochastic variation. These
are replications within two specified synthetic generator families, not
independent real-world environments.

Launch the campaign with `PYTHONHASHSEED=0` so process-level hash iteration is
common across systems and worlds; record the value in the output artifact.

## Models and information parity

All systems receive the same ordered event stream. They start without prior
events and update only after the current cycle has been scored. Each system
uses the immediately preceding event tag to predict the next event tag across
the fixed full tag vocabulary. The score includes transitions within a cycle
and the transition from the preceding cycle's final event to the current
cycle's first event:

- **Organica:** prediction strengths from the final `SleepService` report
  after the preceding cycle. For each source tag, strengths over the full
  tag vocabulary are normalized into a categorical distribution; an empty
  row is uniform.
- **First-order Markov:** cumulative counts of adjacent tag transitions, with
  symmetric Dirichlet smoothing `alpha = 0.5`.
- **Recency-decayed association:** the same transition counts, exponentially
  decayed with a **20-cycle half-life**, with the same smoothing.

The full tag vocabulary is part of the synthetic task specification, not
hidden cause or regime information. No model receives the change point, the
new mapping, or regime labels. Organica's `SleepService` RNG is seeded with
the world seed. Each system forecasts a complete cycle before any event in
that cycle is added to its state.

## Primary score and alarm rule

For each cycle, compute the mean categorical negative log-likelihood of all
observed next-event tags under each model's forecasts. Higher surprise means
worse fit to the current stream. Freeze probability floors at `1e-9`.

For each model and each world, calibrate the alarm level from its own stable
pre-shift score: compute non-overlapping five-cycle mean-surprise blocks for
cycles 20–59 (eight blocks), then set the threshold to their mean plus three
sample standard deviations. Starting at cycle 60, compute the trailing
five-cycle mean. Alarm after **two consecutive** trailing windows exceed the
threshold. Do not tune the threshold using shifted-world results.

For shifted worlds, the primary metric is **restricted detection delay**:
the alarm cycle minus 60, capped at 31 when no alarm occurs within the
30-cycle evaluation horizon (cycles 60–89). Lower is better. A miss therefore
cannot disappear from the primary analysis. For stationary controls, a false
alarm is any alarm during cycles 60–89; report the fraction of control worlds
with a false alarm.

Report for every family and model: detection fraction within 30 cycles,
restricted mean delay and paired 97.5% percentile-bootstrap intervals for
`baseline delay − Organica delay`, plus stationary-control false-alarm rate.
Use 10,000 paired resamples of the 20 seeds with bootstrap RNG seed `20261023`.

## Decision rules and secondary measures

- The primary hypothesis is met only under the full effect-size, paired
  interval, and false-alarm rule stated above for at least one family.
- If either baseline's interval includes zero, comparative superiority over
  that baseline is inconclusive for that family.
- A stationary-control false-alarm rate above 10% invalidates a superiority
  claim for that family, regardless of the delay score.
- Report both families even if one is unfavorable. No generator or threshold
  may be selected or tuned after looking at scores.
- Report per-cycle internal inventory, theory, question, and anomaly counts
  only as exploratory secondary outcomes; they cannot satisfy the success
  criterion.

This benchmark evaluates online detection from predictive surprise. It does
not isolate contradiction weighting or establish that any particular
cognitive layer caused a result. The live study remains paused pending a
stable V1.0.0 build and review. No engine changes are part of Phase I.
