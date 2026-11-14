# A1 design viability — C1 ceiling and conditional C2/C8 target competence

**ID:** `A1-DESIGN-VIABILITY-1`
**Status:** `FLAGGED — C1 CEILING BELOW FLOOR; C2/C8 TARGET COMPETENCE CONDITIONAL`

**This is not an A1 result.** It is a read-only report over committed no-arm artifacts; no cell was run, no target was frozen, no grant was issued and no threshold was changed.

## C1 ceiling — proof for the current stream

C1's denominator is the count of paired-control available rows across every target and non-target row in the stream. Target selection only partitions those rows; it cannot add available rows. The largest denominator any target selection can produce is therefore min(A_available, K_available) for the stream.

### Candidate-protocol stream

| Seed | Stream rows | Baseline A | Baseline K | Max attainable C1 | Floor | Shortfall | Reaches floor? |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `20630101` | 64 | 44 | 44 | 44 | 60 | 16 | NO |
| `20630102` | 63 | 44 | 31 | 31 | 60 | 29 | NO |
| `20630103` | 64 | 52 | 39 | 39 | 60 | 21 | NO |
| `20630104` | 64 | 43 | 35 | 35 | 60 | 25 | NO |
| `20630105` | 64 | 49 | 43 | 43 | 60 | 17 | NO |
| `20630106` | 63 | 49 | 36 | 36 | 60 | 24 | NO |

**Seeds reaching the floor:** **0/6**; maximum attainable **44**, minimum **31**.

Every seed's maximum is below the 60-row floor. The current candidate stream is not C1-capable, even if every candidate is selected and every available row is retained. This is a branch-closing result for target selection on this stream.

### Current cell stream

| Seed | Stream rows | Baseline A | Baseline K | Max attainable C1 | Floor | Shortfall | Reaches floor? |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `20630101` | 112 | 70 | 82 | 70 | 60 | 0 | YES |
| `20630102` | 112 | 72 | 59 | 59 | 60 | 1 | NO |
| `20630103` | 112 | 89 | 69 | 69 | 60 | 0 | YES |
| `20630104` | 112 | 67 | 58 | 58 | 60 | 2 | NO |
| `20630105` | 112 | 85 | 72 | 72 | 60 | 0 | YES |
| `20630106` | 112 | 85 | 72 | 72 | 60 | 0 | YES |

**Seeds reaching the floor:** **4/6**; maximum attainable **72**, minimum **58**.

The 112-row cell stream reaches 60 on four seeds, but that is reverse-orientation duplication rather than a wider independent universe. On unique undirected edges the C1 ceiling remains 31-44, below 60 on every seed. Switching to it also changes the C4 stream to 108/92 directed rows, or 59-60/43-44 unique non-target rows.

### Cell-stream composition and dedupe

| Seed | Candidate edges | Reverse orientations | Extra orientations | Cell rows | Unique undirected | Cell C1 max | Candidate C1 max | Inflation |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `20630101` | 64 | 48 | 0 | 112 | 64 | 70 | 44 | 26 |
| `20630102` | 63 | 47 | 2 | 112 | 64 | 59 | 31 | 28 |
| `20630103` | 64 | 48 | 0 | 112 | 64 | 69 | 39 | 30 |
| `20630104` | 64 | 48 | 0 | 112 | 64 | 58 | 35 | 23 |
| `20630105` | 64 | 48 | 0 | 112 | 64 | 72 | 43 | 29 |
| `20630106` | 63 | 47 | 2 | 112 | 64 | 72 | 36 | 36 |

**Totals:** 382 candidate rows, 286 reverse orientations, 4 extra orientations, 672 cell rows, 384 unique undirected edges. The unique-edge C1 ceiling is **31-44**, still below 60.

The 112-row cell stream is the candidate stream plus reverse orientations, not a wider independent universe. The four-seed apparent C1 pass is reverse-orientation duplication; on unique undirected edges the ceiling is still the candidate 31-44, below the 60-row floor on every seed.

### What the ceiling means

The current registered design is not C1-capable under either reported stream. Target selection cannot repair the candidate stream; a new universe, a different seed block with better baseline availability, or a changed C1 estimator is required.

This does not establish that A1 is impossible in principle. A different universe, seed block or C1 estimator could satisfy the floor. It establishes that the current stream and floor cannot be reconciled by selecting a different target block.

## C2/C8 target competence — conditional

**Status:** `CONDITIONAL — NOT A PROOF OF C2 OR C8 FAILURE`

This section treats baseline A and K availability as a precondition for a clean C2 row and a clean C8 double block. Under that target-competence reading, a row lacking baseline A or K cannot support all of C2's cells and cannot test a genuine A-K- double block.

C2 is a treatment gate, not a no-arm gate. The no-arm baseline cannot prove that a missing baseline path remains missing under A- or K+ treatment. If the unblocked arm can induce the absent path, exact C2 remains unmeasured. The counts are a conditional target-selection incompatibility, not a proof that C2 or C8 must fail.

A1-TARGET-VIABILITY-1 reports carrier-missing exposure under the same baseline A/K reading. This report makes that reading explicit and does not treat it as proof of treatment failure.

| Design | Target rows | Fully C2-viable | C8 rows required | Max clean rows per seed | Seeds with a clean block |
| --- | ---: | ---: | ---: | ---: | ---: |
| **N4** | 24 | 12 | 4 | 3 | **0/6** |
| **N20** | 120 | 54 | 20 | 12 | **0/6** |

### Per-seed competence

| Seed | N4 fully C2-viable | N4 needs | N4 clean? | N20 fully C2-viable | N20 needs | N20 clean? |
| ---: | ---: | ---: | --- | ---: | ---: | --- |
| `20630101` | 2 | 4 | NO | 10 | 20 | NO |
| `20630102` | 3 | 4 | NO | 5 | 20 | NO |
| `20630103` | 3 | 4 | NO | 12 | 20 | NO |
| `20630104` | 1 | 4 | NO | 7 | 20 | NO |
| `20630105` | 2 | 4 | NO | 10 | 20 | NO |
| `20630106` | 1 | 4 | NO | 10 | 20 | NO |

### Competent target pool

| Seed | Candidate edges | A available | K available | A&K available | C8 rows needed | Pool sufficient? |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `20630101` | 64 | 44 | 44 | 32 | 20 | YES |
| `20630102` | 63 | 44 | 31 | 23 | 20 | YES |
| `20630103` | 64 | 52 | 39 | 36 | 20 | YES |
| `20630104` | 64 | 43 | 35 | 27 | 20 | YES |
| `20630105` | 64 | 49 | 43 | 35 | 20 | YES |
| `20630106` | 63 | 49 | 36 | 33 | 20 | YES |

The candidate pool contains 23-36 A&K-available edges per seed, enough to construct a 20-row competent block on all six seeds. The current N20 selection has only 5-12 clean rows, so the current C2/C8 problem is a selection problem, not a supply problem. C1 is still not repaired: its full-stream K availability is 31-44.

Under the stated competence reading, N4 has at most 3 clean rows per seed for a 4-row block and N20 has at most 12 for a 20-row block. Neither current target set supplies a clean C8 block. The candidate pool has 23-36 A&K-available edges, so a 20-row competent block is constructible by a new selection rule; the current N20 selection, not the supply, is the C2/C8 problem. C1 remains unresolved. Exact C2/C8 adjudication still requires cells or a pre-registered competence filter; the current data do not prove treatment failure.

## Disposition

Do not freeze or run the current A1 design on these records. C1 is not target-selectable, and target competence requires an owner rule. A1 must be redesigned with a C1-capable universe or seed block and a pre-registered competence rule, or parked. No cell, target freeze, grant or threshold change is authorised.

**Not evidence:** A read-only design-viability report over committed no-arm artifacts. It runs no A1 cell, freezes no target, changes no threshold and measures no treatment effect. The C2/C8 section is conditional on baseline target competence, not a C2 or C8 verdict.

## Reproduce

```bash
python -m benchmarks.a1_design_viability --check
python -m benchmarks.a1_design_viability --self-test
```
