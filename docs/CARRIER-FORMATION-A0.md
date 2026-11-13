# Carrier formation A0 — stage identification

Generated from `docs/carrier_formation_a0.json` by `python -m benchmarks.carrier_formation_a0 --write`. Do not edit by hand.

**Status: ANALYSIS, NOT A RUN.** This reads six committed Q4 seeds and the Q4 stage table. It runs no cell, assigns no seed and changes no engine file.

## Verdict

**`NO SINGLE UPSTREAM SELECTION STAGE IDENTIFIED`**

Admission is the stage that excludes the direct edge from service; candidate formation is the stage that creates the loop carrier. The records place them on parallel paths to assertion, not in one upstream chain. The design's S cannot be named from the existing records without a new stage-level intervention.

## What the records show

| Quantity | Value |
| --- | ---: |
| Asserted-never-served rows | 26 |
| Loop-carrier rows | 26 |
| Carrier formation cycles | 37–117 (median first formation 76.0) |
| Direct temporal count | 23–47 (prediction floor 5) |
| Rows with rank inside cap 40 | 10 |
| Rows inside the served transition budget | 0 |
| Final prediction sources | 0 |
| Carrier formed at or before the best rank | 17 |
| Carrier formed after the best rank | 9 |

The 26 rows have a direct temporal count of 23–47, above the prediction floor of 5, so the direct edge is not a floor miss. Every row has a loop carrier; one also has a dream co-carrier. No row has a final prediction source.

## Q4 stage totals

| Stage quantity | Count |
| --- | ---: |
| Present | 672 |
| Constructed | 671 |
| Below prediction minimum | 1 |
| Served ever | 492 |
| Never served | 179 |
| Never served but inside the transition budget | 0 |
| Asserted at end | 247 |
| Asserted but never served | 26 |

Construction is not the loss: 671 of 672 present edges became candidates. The direct edges are present and constructed, but none enters the served transition budget. The carrier is built from temporal cycles, not from the served window, so the carrier can exist when admission fails.

## Stage map

| Stage | Observable? | Manipulable? | Independent of carrier? | Upstream of carrier? | Eligible as `S`? | Reading |
| --- | --- | --- | --- | --- | --- | --- |
| `candidate_formation` | yes | yes | no | yes | no | it creates C; manipulation changes C, so it is upstream but not independent |
| `admission` | yes | yes | yes | no | no | served-window allocation can be varied and the carrier forms without it, but it is parallel to the carrier path, not upstream of it |
| `service` | yes | no | yes | no | no | the current records do not separate service from admission; both are the served-window path |
| `assertion` | yes | yes | yes | no | no | assertion can be blocked by the ordering arm, but it is downstream of both paths; it cannot be the upstream S |

No stage satisfies all four. Candidate formation is upstream but not independent; admission and service are independent but parallel; assertion is independent but downstream. The 2×2 design needs an `S` that is upstream of `C` and independently manipulable, and the existing records do not contain one.

## Timing

| Carrier first formation relative to the best-rank cycle | Rows |
| --- | ---: |
| At or before | 17 |
| After | 9 |

The mixed order matters. In 17 rows the carrier exists at or before the best recorded rank; in 9 it appears afterwards. The record therefore does not support a single temporal ordering in which carrier formation precedes admission for every edge.

## Per-edge rows

| Seed | Edge | Category | Rank | In transition budget? | Best cycle | First carrier | Carrier before best? |
| ---: | --- | --- | ---: | --- | ---: | ---: | --- |
| 20611601 | `olive>umber` | identity mismatch | 31 | no | 15 | 62 | no |
| 20611601 | `olive>willow` | alternate assertion path | 39 | no | 104 | 104 | yes |
| 20611601 | `willow>olive` | alternate assertion path | 127 | no | 116 | 104 | yes |
| 20611601 | `willow>teal` | identity mismatch | 124 | no | 116 | 62 | yes |
| 20611602 | `amber>umber` | identity mismatch | 61 | no | 81 | 50 | yes |
| 20611602 | `indigo>umber` | identity mismatch | 52 | no | 31 | 110 | no |
| 20611602 | `sable>slate` | identity mismatch | 26 | no | 119 | 49 | yes |
| 20611602 | `willow>umber` | identity mismatch | 54 | no | 119 | 37 | yes |
| 20611603 | `sable>yarrow` | alternate assertion path | 111 | no | 110 | 76 | yes |
| 20611603 | `slate>umber` | identity mismatch | 27 | no | 106 | 66 | yes |
| 20611603 | `slate>yarrow` | alternate assertion path | 26 | no | 86 | 67 | yes |
| 20611603 | `umber>teal` | identity mismatch | 28 | no | 68 | 66 | yes |
| 20611603 | `willow>verdant` | identity mismatch | 41 | no | 84 | 69 | yes |
| 20611603 | `yarrow>indigo` | identity mismatch | 80 | no | 107 | 76 | yes |
| 20611603 | `yarrow>sable` | alternate assertion path | 79 | no | 107 | 76 | yes |
| 20611603 | `yarrow>slate` | alternate assertion path | 81 | no | 107 | 67 | yes |
| 20611603 | `yarrow>verdant` | identity mismatch | 77 | no | 107 | 66 | yes |
| 20611604 | `amber>maple` | alternate assertion path | 35 | no | 16 | 79 | no |
| 20611604 | `maple>amber` | alternate assertion path | 41 | no | 81 | 79 | yes |
| 20611605 | `amber>birch` | identity mismatch | 22 | no | 31 | 100 | no |
| 20611605 | `sable>birch` | identity mismatch | 31 | no | 12 | 85 | no |
| 20611605 | `sable>teal` | identity mismatch | 81 | no | 19 | 73 | no |
| 20611606 | `crimson>teal` | identity mismatch | 27 | no | 31 | 78 | no |
| 20611606 | `ochre>amber` | identity mismatch | 82 | no | 120 | 114 | yes |
| 20611606 | `teal>amber` | identity mismatch | 51 | no | 28 | 77 | no |
| 20611606 | `teal>willow` | identity mismatch | 50 | no | 28 | 97 | no |

## What this licenses

- **A0 does not license A1 as currently designed.** The design needs a single upstream `S`; the records contain two parallel stages instead.
- **Admission remains the named exclusion stage for the direct edge.** Q4 places the loss there, not at construction.
- **Candidate formation remains the carrier stage.** The loop builder creates the carrier from temporal cycles; the served window is not its input.
- **A revised design must be a two-path design or must name a new stage-level lever.** A carrier-only manipulation cannot separate common cause from readout, and an admission manipulation does not move the carrier path.
- **No causal, capability, retention or transfer claim follows.** This is a stage-identification result on one world family, one build and 120 cycles.

## What would change the verdict

A stage-level intervention that changes carrier availability without changing the carrier itself, or a design that treats admission and carrier as two parallel paths with separate interventions. Until one is registered, the 2×2 remains `NOT IDENTIFIED`.

## What this does not establish

An analysis of six committed Q4 seeds in one synthetic world family at one build and one cap. It runs no cell and establishes no causal, capability, retention or transfer claim. The absence of a single upstream stage is a limit of this design, not evidence that no selection process exists.
