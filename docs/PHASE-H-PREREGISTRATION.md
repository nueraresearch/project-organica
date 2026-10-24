# Phase H — External Validity Preregistration

**Frozen before the multi-seed campaign; 2026-10-23.** The single-seed
prediction and clean-world recovery pilots in the preceding PR informed this
protocol and remain pilot results. They are not counted as independent
confirmatory evidence outside the seed set below.

## Question

Do Organica's frozen next-event predictions or surviving structures outperform
simple statistical baselines across repeated synthetic samples and increasingly
ambiguous latent-cause worlds?

## Seed and process controls

* Run ten seeds: **20261023–20261032**, inclusive.
* Pin `PYTHONHASHSEED=0` for the whole campaign. This controls process-level
  collection ordering; it is not treated as a sampled uncertainty source.
* Pass each seed to Organica's sleep RNG. The prediction curriculum is
  deterministic and identical across seeds, so prediction intervals measure
  Organica's seeded stochasticity on the fixed stream; Markov and decayed
  baseline scores repeat on that same stream. The recovery generator varies
  its synthetic event sample by seed.
* Use fresh disposable databases for each run. The live study database is not
  an input or output.
* Report every seed. No seed exclusion, threshold tuning, or post-run selection.

## H1 — Held-out prediction

Keep the existing `benchmarks/heldout_prediction.py` task and models fixed:
bootstrap scaffold plus burst curriculum, train on cycles 1–200, freeze all
models, and score cycles 201–300. Compare Organica Generation-1 predictions,
first-order tag Markov, and one-event recency-decayed temporal association.
Keep the F1 threshold at 0.5 and decay half-life at 50 cycles. Report known-tag
and open-vocabulary scores separately. F1 is the primary comparison; precision
and recall are supporting metrics. Brier score and log loss are descriptive
for Organica because its strengths are not calibrated probabilities.

## H2/H3 — Known-cause structure recovery league

Train Organica and all graph baselines on the same 200 cycles; do not provide
hidden cause or regime labels to any model. Score undirected recovered feature
pairs against the generator's same-cause gold pairs. Keep pair threshold 5
fixed. Compare Organica surviving structures, same-event co-occurrence, and
the temporal transition graph in each condition:

| Condition | Noise-event rate | Shared features per cause | False-correlation event rate |
|---|---:|---:|---:|
| Clean reference | 0.10 | 0 | 0.00 |
| Overlapping | 0.20 | 2 | 0.10 |
| Stress | 0.30 | 3 | 0.25 |

Shared feature tags belong to both latent causes, making their role ambiguous.
False-correlation events pair a feature from the selected cause with a cause-
specific decoy that is excluded from the gold pairs. The dominant cause still
switches every 100 cycles. F1 is the primary structural-recovery comparison;
precision and recall are supporting metrics.

## Uncertainty and decision rules

For each model and metric, report the per-seed mean, sample standard deviation,
range, and deterministic 10,000-resample percentile bootstrap 95% interval for
the mean. Also report paired per-seed differences against Organica. Positive
difference means the comparison model scored higher; for Brier and log loss,
lower is better, so interpret those signs accordingly.

* A task-specific Organica F1 advantage is demonstrated only when the paired
  95% interval for **Organica minus the simple baseline** lies wholly above
  zero.
* If that interval lies wholly below zero, an Organica F1 advantage is
  falsified for that task and condition under this protocol.
* If it includes zero, the result is inconclusive; a numerical mean lead alone
  is not evidence of superiority.
* A win in one condition does not establish a general advantage. Report all
  conditions and baselines; do not tune the world or score after seeing results.

For structure-recovery F1, also compute paired changes in Organica's advantage
over each graph baseline from clean to overlapping and from clean to stress:
`(Organica F1 - baseline F1)_harder - (Organica F1 - baseline F1)_clean`.
A positive interval wholly above zero indicates that Organica's relative F1
position improved as that condition became harder; a negative interval wholly
below zero indicates it worsened. An interval containing zero is inconclusive.
This is a relative trend and does not imply that either model's absolute score
improved.

These intervals quantify variation across the specified synthetic seeds only.
They do not establish external validity to natural environments, causal
intervention knowledge, or held-out regime prediction. No cognitive-layer or
engine changes are part of Phase H.

**Protocol clarification before results inspection:** the held-out curriculum
does not consume the seed; it is the same fixed stream for all ten runs. Only
Organica's sleep RNG varies for H1. H2/H3 vary the generated recovery worlds
and Organica's sleep RNG.
