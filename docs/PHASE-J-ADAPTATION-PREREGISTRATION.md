# Phase J — Gradual Post-Shift Adaptation Preregistration

**Status: preregistered before benchmark implementation and outcome generation.**
Phase J asks whether Organica adapts its online predictive model to a gradual
environmental transition with less shift-specific predictive error than simple
statistical baselines. The cognitive engine and paused longitudinal study
remain unchanged.

## Question and confirmatory hypothesis

Across two specified synthetic generator families, does Organica incur a
smaller shift-induced increase in predictive log loss than both a first-order
Markov model and a recency-decayed transition-association model during a
gradual transition and the ensuing stable period, while reaching acceptable
predictive accuracy after the transition?

For each model and seed, define **adaptation cost** as the mean next-event
negative log likelihood (NLL) in the shifted world over cycles 30–79 minus
that model's mean NLL in its paired stationary control over the same cycles.
For each baseline, define the paired advantage as `baseline adaptation cost −
Organica adaptation cost`; positive values favor Organica. A family supports
the hypothesis only if, against **both** baselines, the mean paired advantage
is at least **0.05 nats per predicted event**, its paired 97.5% bootstrap
interval is wholly above zero, and Organica is non-inferior in absolute
shifted-world NLL during final stable cycles 60–79: the upper endpoint of the
paired 97.5% interval for `Organica NLL − baseline NLL` must be at most
**0.05 nats/event**. The primary claim is met if either predefined family
passes every gate. The 97.5% interval adjusts for the two family opportunities;
requiring both baseline comparisons is an intersection-union rule. Failure
does not establish that Organica cannot help on other tasks.

## Worlds and schedule

Each world lasts 80 cycles with 8 context/outcome trials per cycle. Each trial
is presented to all models as two ordered text events. All tags have at least
four letters. The generators retain latent parameters for scoring only; models
receive no regime labels, transition schedule, or hidden parameter values.

Every seed generates a paired shifted world and stationary control using
common random numbers: the same underlying uniform draws are used for contexts,
noise decisions, and outcomes in both members of the pair. Cycles 0–29 use the
initial rule. Cycles 30–49 linearly interpolate from the initial to final rule
over 20 cycle steps. Cycles 50–79 use the final rule in shifted worlds; controls
keep the initial rule throughout.

1. **Cause-mixture ramp.** The context is `causea` or `causeb`. The probability
   of `causea` moves from 0.85 to 0.15 linearly across the ramp. Each cause has
   four fixed outcomes (`amber`–`maple` or `indigo`–`yarrow`). On 10% of trials,
   the outcome is drawn uniformly from all eight outcomes.
2. **Mapping-mixture ramp.** One of four contexts is selected uniformly. The
   initial mapping is `ctxa→amber`, `ctxb→birch`, `ctxc→cedar`, `ctxd→maple`;
   the final mapping is `ctxa→birch`, `ctxb→amber`, `ctxc→maple`,
   `ctxd→cedar`. At each trial, the old versus new mapping is selected with
   the ramp's linear mixture probability. On 10% of trials, the outcome is
   instead drawn uniformly from the four outcomes. Context and outcome
   marginals remain uniform by design.

Use 20 paired seeds, **20270101–20270120**, in both families. These are
replications within two specified synthetic families, not independent samples
of real environments. Launch with `PYTHONHASHSEED=0`; record it in the output.
Run models in fresh disposable databases, never the live database.

## Models and information parity

All models receive the same ordered event strings. At each cycle, each model
forecasts every next-tag transition using only information available before
that cycle is ingested; it then receives that cycle's events and updates.
Score all within-cycle transitions and the transition from the preceding
cycle's final tag to the next cycle's first tag, over the generator's full
declared tag vocabulary. Use a probability floor of `1e-9`.

- **Organica:** normalize the current `SleepService` report's prediction
  strengths by source tag; use a uniform row when no prediction exists. Seed
  the service RNG with the world seed.
- **First-order Markov:** cumulative adjacent-tag transition counts with
  symmetric Dirichlet smoothing `alpha = 0.5`.
- **Decayed association:** the same transitions with a 20-cycle half-life and
  the same smoothing.

All systems begin without prior events, update only after scoring the current
cycle, and use the same task vocabulary. No model receives explicit change
labels or privileged latent data.

## Outcomes and analysis

The confirmatory endpoints are adaptation cost and final-stable NLL as defined
above. Report each model's shifted and control NLL separately, both paired
differences against Organica, and every seed-level value. Use 10,000 paired
percentile-bootstrap resamples of the 20 seeds, with bootstrap RNG seed
`20270123`; report 97.5% intervals for both families. Do not exclude seeds,
retune the ramp, or select a family after seeing results.

Secondary descriptive outcomes:

- **Adaptation settling time:** first cycle at which three consecutive,
  non-overlapping five-cycle means of shifted-world NLL are no more than
  0.05 nats/event above that model's final-stable mean (cycles 70–79). Search
  from cycle 30 through 79; report not-settled as 51. This self-referenced
  measure is descriptive and cannot satisfy the primary rule.
- Per-cycle NLL curves and Organica inventory, theory, question, and anomaly
  counts. Internal counts are exploratory only.

No significance claim will be made from the secondary measures. Report both
families and all models, including unfavorable outcomes. The campaign tests
two controlled synthetic gradual changes, not abrupt shifts, arbitrary
nonstationarity, natural environments, causal discovery, or which individual
cognitive layer causes an outcome. No cognitive-engine changes are in scope.

## Operational constraints

The live study remains paused pending a stable V1.0.0 review. The benchmark
must use only temporary databases and must not read from or write to
`memory.db`. Freeze this protocol before implementation and before any
campaign outcomes are generated. Amendments, if needed, must be dated and made
before outcome inspection; disclose every amendment.
