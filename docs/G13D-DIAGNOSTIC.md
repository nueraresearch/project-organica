# G13-D — diagnostic report

**Generated from [`docs/g13d_diagnostic.json`](g13d_diagnostic.json); do not edit
by hand.** Regenerate with
`PYTHONHASHSEED=0 python -m benchmarks.g13d_diagnostic --report`.

Plan: [`docs/G13-D-DIAGNOSTIC-PLAN.md`](G13-D-DIAGNOSTIC-PLAN.md), committed before the run.
Seeds: 20261101, 20261102, 20261103, 20261104, 20261105 (diagnostic only).

## The condition

Two interventions together: capacity `MAX_PREDICTIONS = 1000`
(baseline 20) and a lookback restricted to
`event_type != 'sleep'`. The readout is held at its calibrated
`alpha = 256.0`, which is a constant in both arms and **not** an
intervention. Both overrides are in-process subclasses; no engine file was edited.

## Paired difference (log-loss, g13d minus baseline)

Negative means the combined condition scored better. No threshold is applied.

| window.shape | 20261101 | 20261102 | 20261103 | 20261104 | 20261105 | mean |
|---|---|---|---|---|---|---|
| `retention.house_shape` | -0.0311 | -0.0333 | -0.0299 | -0.0258 | -0.0280 | -0.0296 |
| `retention.self_cells_shape` | -0.0311 | -0.0333 | -0.0299 | -0.0258 | -0.0280 | -0.0296 |
| `revision.house_shape` | -0.0435 | -0.0413 | -0.0429 | -0.0410 | -0.0471 | -0.0432 |
| `revision.self_cells_shape` | -0.0435 | -0.0413 | -0.0429 | -0.0410 | -0.0471 | -0.0432 |
| `transfer_diagnostic.house_shape` | -0.0332 | -0.0294 | -0.0312 | -0.0296 | -0.0293 | -0.0305 |
| `transfer_diagnostic.self_cells_shape` | -0.0332 | -0.0294 | -0.0312 | -0.0296 | -0.0293 | -0.0305 |

## Absolute scores, house shape (primary)

| arm | window | 20261101 | 20261102 | 20261103 | 20261104 | 20261105 |
|---|---|---|---|---|---|---|
| baseline | `retention` | 0.4467 | 0.4552 | 0.4544 | 0.4534 | 0.4556 |
| baseline | `transfer_diagnostic` | 0.4554 | 0.4546 | 0.4522 | 0.4485 | 0.4575 |
| baseline | `revision` | 0.4697 | 0.4617 | 0.4650 | 0.4628 | 0.4718 |
| g13d | `retention` | 0.4156 | 0.4219 | 0.4245 | 0.4276 | 0.4276 |
| g13d | `transfer_diagnostic` | 0.4223 | 0.4252 | 0.4210 | 0.4189 | 0.4282 |
| g13d | `revision` | 0.4262 | 0.4205 | 0.4221 | 0.4218 | 0.4247 |

## Fixed references, house shape

| reference | window | 20261101 | 20261102 | 20261103 | 20261104 | 20261105 |
|---|---|---|---|---|---|---|
| replay | `retention` | 0.3295 | 0.3384 | 0.3409 | 0.3467 | 0.3460 |
| replay | `transfer_diagnostic` | 0.3430 | 0.3446 | 0.3358 | 0.3349 | 0.3424 |
| replay | `revision` | 0.3579 | 0.3458 | 0.3420 | 0.3504 | 0.3542 |
| cell_counter | `retention` | 0.3264 | 0.3367 | 0.3403 | 0.3442 | 0.3439 |
| cell_counter | `transfer_diagnostic` | 0.3406 | 0.3430 | 0.3341 | 0.3327 | 0.3404 |
| cell_counter | `revision` | 0.3521 | 0.3447 | 0.3413 | 0.3475 | 0.3530 |
| bayes_ceiling | `retention` | 0.2702 | 0.2763 | 0.2682 | 0.2750 | 0.2737 |
| bayes_ceiling | `transfer_diagnostic` | 0.2744 | 0.2742 | 0.2683 | 0.2714 | 0.2711 |
| bayes_ceiling | `revision` | 0.2760 | 0.2747 | 0.2750 | 0.2739 | 0.2744 |
| base_rate | `retention` | 0.4047 | 0.4103 | 0.4102 | 0.4113 | 0.4113 |
| base_rate | `transfer_diagnostic` | 0.4099 | 0.4093 | 0.4067 | 0.4059 | 0.4143 |
| base_rate | `revision` | 0.4159 | 0.4118 | 0.4111 | 0.4101 | 0.4129 |

## Intervention checks

- provenance filter bit on every seed: **True**
- capacity bound reached above 20 on every seed: **not measured** — the committed counter covers prior candidates of all types, not predictions, so it cannot show that the prediction cap bound; the cap is verified structurally only (MAX_PREDICTIONS 1,000 vs 20)

## What this is not

A diagnostic of how the frozen engine scores when two confounds are removed
together. It establishes no acquisition, transfer, comparative-advantage or V2
result, it applies no threshold, and it authorizes no confirmatory run. The
closed acquisition preregistration, its Gate 13 threshold, the Task 2 stopped
verdict and every confirmatory seed assignment are unchanged.
