# A1 C5 carrier divergence — the two cycles, measured per block

**ID:** `A1-C5-CARRIER-DIVERGENCE-1`

**Date:** 2026-11-15

**Status:** `MEASURED — OBSERVED AND CURRENT CARRIER CYCLES DIVERGE AND ARE DISTINCT OBSERVABLES`

`earliest_observed_carrier_cycle` is the earliest cycle any of the **120** N=20 rows is carried; `earliest_current_carrier_cycle` is the earliest cycle any of the **24** current Path A rows is carried. The current rows are four of the twenty per seed, so the observed minimum can only be earlier or equal — equality on a block is a coincidence of that block's carriers, not an identity.

## 1. Measured blocks

| Block | Role | Observed | Current | Current − observed | Before U=4 | Carriers / missing | Verdict |
| ---: | --- | ---: | ---: | ---: | ---: | --- | --- |
| 2074 | ADOPTED CANDIDATE | 6 | 8 | +2 | 0 | 77 / 43 | **CLEARS C5** |
| 2071 | SCREENED — REJECTED BY C5 | 4 | 10 | +6 | 1 | 68 / 52 | **FAILS C5** |

## 2. The equality case, cited rather than re-measured

| Block | Role | Observed | Current | Verdict | Source |
| ---: | --- | ---: | ---: | --- | --- |
| 2063 | SUPERSEDED — EQUALITY CASE | 5 | 5 | CLEARS C5 | docs/a1_c5_target_timing.json at commit 61ac416 |

**Why it is cited:** 20630101-20630106 is spent by A1-BASELINE-AVAILABILITY-1; a spent block is not reused, so this row is cited from its superseded artifact rather than re-derived.

## 3. What the record establishes

The two cycles are distinct observables: they diverge in a block that clears C5 and in a block that fails it, so neither value implies the other and neither verdict follows from the divergence itself. The earlier block where they were equal is cited, not re-measured, because its seeds are spent.

- Divergent blocks measured: 2074, 2071.
- Divergence with a clearing C5: **True**; divergence with a failing C5: **True**.

**What this does not establish:** that either cycle predicts a C5 outcome, or that any block is typical. Two measured blocks cannot order a population.

## 4. Cross-check against the C5 audit

The adopted block is measured here twice: once by this record, once by `a1_c5_target_timing`. Both readings agree — observed **6**, current **8** — which is what keeps this record from becoming a second account of the same block.

## 5. Replay

`120` cycles per seed, prediction cap `40`, none — the registered world is replayed with no treatment.

**Not evidence:** A no-arm record of two carrier cycles per block. It runs no A1 cell, freezes no target, changes no threshold and makes no causal, capability or transfer claim. It does not select, reserve or spend a seed block.

Reproduce with `python -m benchmarks.a1_c5_carrier_divergence --write`; `--check` verifies the record and this page.
