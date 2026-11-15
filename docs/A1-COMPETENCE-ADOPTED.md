# A1 adopted-block target competence — the C2/C8 numbers as a record

**ID:** `A1-COMPETENCE-ADOPTED-1`

**Date:** 2026-11-15

**Status:** `MEASURED — NO SEED SUPPLIES A CLEAN BLOCK UNDER THE CURRENT SELECTION; THE COMPETENT POOL DOES`

**Block:** `2074` — `the reserved A1-TWO-PATH-1 candidate block; this record names it and measures it only from committed no-arm artifacts`

## Reading

A row is **competent** when both baseline paths, A and K, are present at the recorded no-arm baseline for that directed edge. C2 is a treatment gate, not a no-arm gate. The no-arm baseline cannot show that a missing path stays missing under A- or K+ treatment, so these counts are a conditional target-selection incompatibility and not a proof that C2 or C8 must fail.

## Per seed

| Seed | Universe | N=4 competent | N=20 competent | Competent pool | Clean N=4 block | Clean N=20 block |
| ---: | ---: | ---: | ---: | ---: | --- | --- |
| 20740101 | 64 | **3 of 4** | **10 of 20** | 38 | no | no |
| 20740102 | 64 | **0 of 4** | **7 of 20** | 27 | no | no |
| 20740103 | 64 | **3 of 4** | **11 of 20** | 37 | no | no |
| 20740104 | 64 | **2 of 4** | **13 of 20** | 40 | no | no |
| 20740105 | 64 | **2 of 4** | **10 of 20** | 32 | no | no |
| 20740106 | 62 | **2 of 4** | **7 of 20** | 31 | no | no |

## Summary

| Design | Rows | Competent | Per seed | Seeds with a clean block |
| --- | ---: | ---: | --- | ---: |
| **N=4** | 24 | **12** | 0-3 | **0 of 6** |
| **N=20** | 120 | **58** | 7-13 | **0 of 6** |

Competent pool: **27-40** per seed, 20 required for an N=20 block; sufficient on every seed: **True**.

## What the record establishes

On the adopted block the current N=4 selection supplies 12 competent rows of 24 and the N=20 selection 58 of 120, while the competent pool is 27-40 per seed against 20 required. The block has no seed on which either selection can be adjudicated, and the pool is large enough to build one.

under the drafted C2/C8 competence rule a block with any non-competent row is VOID rather than partial-scored, so both current selections would be void as recorded

**What this does not establish:** that C8 would pass on a competent block, that the 2063 block behaves the same way per seed, or that any treatment effect exists. It counts availability, not outcomes.

## Integrity

Selected rows with no availability record: **0**. N=20 rows outside the candidate universe: **0**. a selected row with no availability record is not called incompetent; the count is zero here, which is what makes the competence figures exact rather than lower bounds

**Not evidence:** A read-only join of committed no-arm artifacts. It runs no A1 cell, selects no target, freezes no target, changes no threshold and measures no treatment effect.

Reproduce with `python -m benchmarks.a1_competence_adopted --write`; `--check` re-derives every figure from the source artifacts.
