# Why within-cycle counts top out at 3-4

**Status: diagnostic, not a result.** Generated from `docs/ceiling_diagnostic.json` by `python -m benchmarks.ceiling_diagnostic --write`.

## Cells

| Block | Seed | Role | S_ever | Source max | Present | Base max | No-prior-group max | Intergroup lift | Freq support max | Window-6 >= 5 | Order-low | Window-sensitive class |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| T1 | 20612204 | zero | 0 | 4 | 112 | 4 | 4 | 0 | 4 | 69 | 5/112 | WINDOW-SENSITIVE |
| T1 | 20612205 | zero | 0 | 3 | 112 | 3 | 3 | 0 | 3 | 61 | 6/112 | WINDOW-SENSITIVE |
| T1b | 20612208 | zero | 0 | 4 | 112 | 4 | 3 | 1 | 3 | 66 | 2/112 | WINDOW-SENSITIVE |
| T1b | 20612210 | zero | 0 | 3 | 112 | 3 | 3 | 0 | 3 | 62 | 7/112 | WINDOW-SENSITIVE |
| T1b | 20612212 | zero | 0 | 4 | 112 | 4 | 4 | 0 | 4 | 69 | 1/112 | WINDOW-SENSITIVE |
| T1 | 20612201 | control | 9 | 6 | 112 | 6 | 6 | 0 | 7 | 91 | 3/112 | MIXED |
| T1 | 20612202 | control | 3 | 6 | 112 | 6 | 6 | 0 | 7 | 90 | 4/112 | MIXED |
| T1 | 20612203 | control | 6 | 5 | 112 | 5 | 5 | 0 | 7 | 80 | 4/112 | MIXED |
| T1 | 20612206 | control | 5 | 6 | 112 | 6 | 6 | 0 | 5 | 78 | 6/112 | MIXED |
| T1b | 20612209 | control | 1 | 5 | 112 | 5 | 5 | 0 | 5 | 79 | 0/112 | MIXED |
| T1b | 20612211 | control | 3 | 6 | 112 | 6 | 5 | 1 | 6 | 71 | 4/112 | MIXED |
| T1b | 20612213 | control | 3 | 5 | 112 | 5 | 5 | 0 | 6 | 88 | 3/112 | MIXED |

## What this establishes

- The five zero cells have 0 admissible world-edge candidates at floor 5.
- The zero is created at candidate formation, before ranking, admission and assertion.
- Within-cycle counts on these seeds occupy 1-4; floor 5 slices through that distribution.
- PersistenceOff removes carried support only when a processed cycle boundary fires; a withheld block-end event suppresses the reset.

## What this does not establish

- The exact contribution of the read floor, lookback horizon, cycle-boundary reset behavior and world structure.
- That extending the engine lookback is a clean horizon treatment; event rows persist, so it reintroduces cross-cycle context.

## Window sweep

Exact replay with the engine's persistent event history. Window 3 is the engine default; the window counts the current event plus prior events.

| Block | Seed | 1 | 2 | 3 | 4 | 6 | 8 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| T1 | 20612204 | 0 | 4 | 4 | 7 | 9 | 11 |
| T1 | 20612205 | 0 | 3 | 3 | 6 | 9 | 12 |
| T1b | 20612208 | 0 | 3 | 4 | 6 | 9 | 11 |
| T1b | 20612210 | 0 | 3 | 3 | 5 | 8 | 11 |
| T1b | 20612212 | 0 | 4 | 4 | 7 | 9 | 11 |
| T1 | 20612201 | 0 | 5 | 6 | 11 | 15 | 17 |
| T1 | 20612202 | 0 | 6 | 6 | 9 | 10 | 13 |
| T1 | 20612203 | 0 | 5 | 5 | 7 | 10 | 14 |
| T1 | 20612206 | 0 | 4 | 6 | 8 | 11 | 15 |
| T1b | 20612209 | 0 | 4 | 5 | 6 | 10 | 13 |
| T1b | 20612211 | 0 | 5 | 6 | 9 | 13 | 18 |
| T1b | 20612213 | 0 | 4 | 5 | 8 | 10 | 13 |

## Permutation test

Within-cycle order permutations preserve the event multiset and cycle boundaries. `Fraction above observed` is the share of permutations whose cell maximum exceeds the observed maximum.

| Block | Seed | Observed max | Perm p05 | Perm p50 | Perm p95 | Fraction above observed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| T1 | 20612204 | 4 | 4 | 5 | 6 | 0.559 |
| T1 | 20612205 | 3 | 4 | 5 | 5 | 1.000 |
| T1b | 20612208 | 4 | 4 | 4 | 5 | 0.325 |
| T1b | 20612210 | 3 | 4 | 4 | 5 | 0.992 |
| T1b | 20612212 | 4 | 4 | 5 | 5 | 0.598 |
| T1 | 20612201 | 6 | 5 | 6 | 7 | 0.272 |
| T1 | 20612202 | 6 | 5 | 5 | 7 | 0.083 |
| T1 | 20612203 | 5 | 5 | 5 | 7 | 0.431 |
| T1 | 20612206 | 6 | 5 | 5 | 6 | 0.021 |
| T1b | 20612209 | 5 | 5 | 5 | 7 | 0.459 |
| T1b | 20612211 | 6 | 5 | 6 | 7 | 0.105 |
| T1b | 20612213 | 5 | 5 | 5 | 7 | 0.389 |

## Verdict

**LOCALIZED (window-sensitive).** The five zero cells have no world-edge candidate at floor 5: the zero is created before ranking, admission or assertion can operate. The window sweep is a counterfactual and makes the ceiling window-sensitive; it does not establish which of the read floor, horizon, boundary resets or world structure is the root cause.

Do not extend the engine lookback as an intervention; persistent event rows make it a different treatment family. A horizon study needs a preregistered within-cycle counterfactual.

A replay-only diagnostic on stored seeds; it adjudicates no block, consumes no fresh seed, runs no engine cell and makes no capability, retention or transfer claim. It localizes the zero to candidate formation; it does not identify the full mechanism or adjudicate the floor, horizon, boundary-reset or world-structure contribution.
