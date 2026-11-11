# Presence to assertion: the conversion observer — result

Generated from `docs/presence_conversion_observer_run.json` by `python -m benchmarks.presence_conversion_observer --finish`. Do not edit by hand.

**Engine:** `0.14.0`. **Design:** 12 design cells over 6 seeds at 120 cycles, plus the observer-off witness cell and the X7 determinism control.

**Verdict: `OBSERVER NOT NEUTRAL`.**

## Per-seed retained chain

| Seed | W | P | C | S_cycle | S_ever | A_pred | Bypass | Primary suspect | Neutral |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 20611501 | 112 | 112 | 112 | 29 | 99 | 44 | 0 | C->S_cycle | NO |
| 20611502 | 112 | 112 | 112 | 29 | 86 | 25 | 4 | C->S_cycle | NO |
| 20611503 | 112 | 112 | 112 | 31 | 93 | 40 | 0 | C->S_cycle | NO |
| 20611504 | 112 | 112 | 112 | 28 | 91 | 38 | 4 | C->S_cycle | NO |
| 20611505 | 112 | 112 | 112 | 25 | 95 | 59 | 3 | C->S_cycle | NO |
| 20611506 | 112 | 112 | 112 | 29 | 85 | 32 | 7 | C->S_cycle | NO |

## Gates

| Gate | Result |
| --- | --- |
| `X1_observer_neutral` | FAIL |
| `X2_stage_complete` | pass |
| `X3_no_unobserved_imputation` | pass |
| `X4_same_object` | pass |
| `X5_witnesses` | pass |
| `X6_seed_axis` | pass |
| `X7_determinism` | pass |
| `X8_control_reproduces_audit` | pass |

The witness cell reproduced the published audit row: yes.

The loss rule runs over `W -> P -> C -> S_cycle -> S_ever -> A_pred`. `E` is the reason record attached to `P -> C`, not a retention step; `A_other` is the bypass and is counted in neither retention nor loss.

## What this does not establish

This record measures where world edges leave the conversion path on one world family, one engine build and one cap, with a benchmark-only observer. It does not show that any stage is a defect, that a mechanism is responsible, that raising the cap or changing the ranking would help, or that the assertion endpoint is wrong. `U`, the readout/use stage, is not observed. A named loss stage is a target for a separate preregistration, not a licence to edit the engine.

## Reproduce

```bash
python -m benchmarks.presence_conversion_observer --measure
python -m benchmarks.presence_conversion_observer --finish
python -m benchmarks.presence_conversion_observer --check
```
