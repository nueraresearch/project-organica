# Density padding: does the partial final pass explain the ladder?

**Pre-registration**: `DENSITY-PADDING-1`. **Status**: RUN. **Date**: 2026-11-07.

**Inherited grid**: seeds and densities by reference from `docs/density_interaction_a2_prereg.json`,
cap 20, filler `constant`. The A2 block is **not** amended: its schemes, criteria and artifacts are
untouched, and this block adds one scheme.

## 1. Question

The A2 record shows the primary scheme's advantage is not monotone across the ladder while the sensitivity scheme's rises. The decision record attributes this to the primary scheme's partial final pass. If that attribution is right, a scheme that pads in whole cycles should have a monotone ladder.

## 2. The third scheme

`whole_cycle`: the base stream (world edges in sorted order, then the within-cell filler) repeated ceil(TOTAL_EVENTS / len(base)) times, so every base occurrence is emitted the same number of times and the stream always ends on the filler tail.

Events per density: 0.1 = 432, 0.2 = 480, 0.4 = 432, 0.6 = 624, 0.8 = 408.

Why the total is not held fixed: holding total exposure at 400 events is exactly what forces a partial final pass, so this scheme removes the phase by letting the total vary.

## 3. Endpoint

precision at cap 20; Delta = treated precision - control precision.

## 4. Gate

`phase_neutral`: at every density each base occurrence appears exactly `passes` times, the last event is a filler event, and len(stream) == passes * len(base). The gate is checked before any cell runs, and the primary stream is put
through the same check as a negative control: if the primary stream is already phase-neutral,
the gate cannot fire and the run is refused.

## 5. Criteria

- **P1**: for every adjacent pair in the ladder, mean Delta(next) - mean Delta(current) >= 0.
- **P2**: mean Delta(0.6) >= mean Delta(0.1).

Both are judged, and the block passes only if both hold. The rule is exact rather than
tolerance-based because the question is qualitative: a negative step means the ladder is not
monotone, whatever its size.

## 6. Decision table

- **Monotone**: the padding phase explains the mid-ladder dip: report the primary ladder as an instrument property in the decision record and quote the whole-cycle profile as the phase-free reading.
- **Not monotone**: the padding phase is not the whole story: name the failing step and the class that holds the budget there, and stop attributing the ladder to padding alone.

## 7. Not claimed

- no cognitive or behavioural claim: the endpoint is a selection reading.
- no claim about exposure in general: the scheme varies total exposure with density.
- no amendment to A2: its schemes, criteria and artifacts are unchanged.

## 8. Result

**WHOLE-CYCLE PADDING DOES NOT RESTORE A MONOTONE LADDER.** the padding phase is not the whole story; the failing step is 0.4->0.6 (-0.0344).

Cells: 160. Slots are means over the inherited seeds; the phase gate passed.

| rho | control | treated | Delta | seeds positive |
| --- | --- | --- | --- | --- |
| 0.1 | 0.3812 | 0.4344 | 0.0531 | 10 of 16 |
| 0.2 | 0.5094 | 0.5813 | 0.0719 | 12 of 16 |
| 0.4 | 0.6969 | 0.7812 | 0.0844 | 15 of 16 |
| 0.6 | 0.8562 | 0.9062 | 0.0500 | 14 of 16 |
| 0.8 | 0.8500 | 1.0000 | 0.1500 | 16 of 16 |

Slots in the cap-20 selection (means over the inherited seeds). The treated arm cannot
hold an intra-cell row by construction, so its non-world slots are all cross-cell:

| rho | control intra-cell | control cross-cell non-world | treated cross-cell non-world |
| --- | --- | --- | --- |
| 0.1 | 3.94 | 8.44 | 11.31 |
| 0.2 | 3.56 | 6.25 | 8.38 |
| 0.4 | 2.44 | 3.62 | 4.38 |
| 0.6 | 1.06 | 1.81 | 1.88 |
| 0.8 | 3.00 | 0.00 | 0.00 |

Adjacent steps:

- 0.1 -> 0.2: +0.0187
- 0.2 -> 0.4: +0.0125
- 0.4 -> 0.6: -0.0344
- 0.6 -> 0.8: +0.1000

Criteria: P1 **failed**, P2 **failed**. Negative control: the same P1 on the A2 primary profile returns not monotone, as it must,
so the check is known to be able to fail on the profile it was written for.
