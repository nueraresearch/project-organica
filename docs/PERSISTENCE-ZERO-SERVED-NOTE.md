# Why the persistence-off arm serves zero world edges on some seeds

**Status: diagnostic, not a result.** Generated from `docs/persistence_zero_served_diagnostic.json` by `python -m benchmarks.persistence_zero_diagnostic --write`.

## The mechanism

`PersistenceOffMemory` zeroes every `precedes` count at the end of each cycle. `SleepService.run` loads temporal edges at the start of the next cycle, and `_build_predictions` admits a transition only when `count >= PREDICTION_MIN_COUNT = 5`. The reset therefore leaves only counts accumulated inside one cycle; a world edge must be observed at least 5 times in that cycle to become a candidate at all.

## Admissibility replay

| Block | Seed | Arm | Observed S_ever | Admissible world edges | Max world count | Cycles with one |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| T1 | 20612201 | shipped | 97 | 112 | 51 | 86 |
| T1 | 20612201 | persistence_off | 9 | 9 | 6 | 2 |
| T1 | 20612202 | shipped | 106 | 112 | 53 | 81 |
| T1 | 20612202 | persistence_off | 3 | 3 | 6 | 2 |
| T1 | 20612203 | shipped | 103 | 112 | 58 | 85 |
| T1 | 20612203 | persistence_off | 6 | 6 | 5 | 2 |
| T1 | 20612204 | shipped | 102 | 112 | 50 | 117 |
| T1 | 20612204 | persistence_off | 0 | 0 | 4 | 0 |
| T1 | 20612205 | shipped | 95 | 112 | 54 | 115 |
| T1 | 20612205 | persistence_off | 0 | 0 | 3 | 0 |
| T1 | 20612206 | shipped | 94 | 112 | 57 | 82 |
| T1 | 20612206 | persistence_off | 5 | 5 | 6 | 1 |
| T1b | 20612208 | shipped | 101 | 112 | 55 | 116 |
| T1b | 20612208 | persistence_off | 0 | 0 | 4 | 0 |
| T1b | 20612209 | shipped | 95 | 112 | 51 | 84 |
| T1b | 20612209 | persistence_off | 1 | 1 | 5 | 1 |
| T1b | 20612210 | shipped | 100 | 112 | 54 | 115 |
| T1b | 20612210 | persistence_off | 0 | 0 | 3 | 0 |
| T1b | 20612211 | shipped | 103 | 112 | 60 | 82 |
| T1b | 20612211 | persistence_off | 3 | 3 | 6 | 2 |
| T1b | 20612212 | shipped | 98 | 111 | 56 | 115 |
| T1b | 20612212 | persistence_off | 0 | 0 | 4 | 0 |
| T1b | 20612213 | shipped | 99 | 112 | 50 | 80 |
| T1b | 20612213 | persistence_off | 3 | 3 | 5 | 2 |

## Full serving run

The five zero cells and the highest-`S_ever` non-zero cell of each block were run through the real observer and sleep cycle on fresh scratch databases. The controls are present so the check can fail.

| Block | Seed | Observed S_ever | Served world edges | Windows | Predictions |
| --- | ---: | ---: | ---: | ---: | ---: |
| T1 | 20612204 | 0 | 0 | 120 | 23 |
| T1 | 20612205 | 0 | 0 | 120 | 19 |
| T1b | 20612208 | 0 | 0 | 120 | 13 |
| T1b | 20612210 | 0 | 0 | 120 | 31 |
| T1b | 20612212 | 0 | 0 | 120 | 26 |
| T1 | 20612201 | 9 | 9 | 91 | 61 |
| T1b | 20612211 | 3 | 3 | 89 | 62 |

## Finding

Every zero-S_ever persistence-off cell is a seed on which no world edge reaches the prediction floor of 5 inside a single cycle after the reset: 5 such cells, all with 0 admissible world edges and a maximum observed world-edge count of [3, 4]. The full observer/sleep path confirms it: all 5 zero cells serve 0 world edges. On the 7 non-zero cells the admissibility ceiling equals the observed S_ever exactly (T1/20612201 9=9; T1/20612202 3=3; T1/20612203 6=6; T1/20612206 5=5; T1b/20612209 1=1; T1b/20612211 3=3; T1b/20612213 3=3), and the two positive controls serve T1/20612201 9, T1b/20612211 3 world edges. The zero is a threshold consequence, not a failed measurement: the reset removes the cross-cycle counts that carry a world edge over the floor, and within-cycle repetition alone reaches 5 only on some seeds.

The replay is a ceiling, not a re-scoring: on the shipped arm the observed `S_ever` is at or below the admissible set because the cap and ranking still choose among candidates; on the persistence-off arm the two coincide, so the zero cells are exactly the seeds where the ceiling is zero. The full serving run confirms the zero cells serve nothing and the controls serve what the stored cells recorded.

## What this establishes

This is a mechanism-level statement for these seeds: cross-cycle accumulation is required to reach `PREDICTION_MIN_COUNT = 5` within a cycle when the reset removes the carried counts. It is not evidence that threshold 5 is mis-calibrated. The measured 3-4 within-cycle ceiling is the next question: topology, tag pattern, lookback and calibration are untested explanations. Lowering the floor is a separate intervention, not licensed by this diagnostic.

A diagnostic replay and a fresh scratch serving run on stored seeds; it adjudicates no block, changes no gate or verdict, and makes no capability claim. It explains the zero S_ever cells in T1 and T1b.
