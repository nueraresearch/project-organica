# A1 viability: what 0/6 is made of, and what each lever costs

**ID:** `A1-VIABILITY-LEVERS-1`  
**Date:** 2026-11-15  
**Status:** `FLAGGED — ONE LEVER WORKS AND IT CHANGES THE ESTIMAND; THE OTHER TWO CANNOT WORK`

**This is not an A1 result.** No cell ran, no target was frozen, no grant issued. It counts the baseline paths a target row would need for C2's four cells to be observable, and prices the three ways out of the 0/6 finding in [`A1-TARGET-VIABILITY-ADOPTED`](A1-TARGET-VIABILITY-ADOPTED.md).

**Only one lever works, and it is the one already built.** The unfiltered block cannot be made C2-viable by raising `N`, and no block drawn from the same universes will be viable on six seeds; what does work is selecting rows that carry both paths at baseline, which is exactly the competent selection `A1-C8-SELECTION` already specifies and which scores **0 failures in 115 rows**. Its cost is not computational but interpretive: the target population stops being *representative eligible edges* and becomes *baseline-competent edges*, so C2's finding would be about a conditioned population. That is the decision in front of the owner, and it is a decision about what the experiment is a experiment on.

## What makes each seed non-viable

A target row is C2-viable only if it has **both** an `A` carrier and a `K` path at baseline: without `A` it cannot show `A=True` in `A+K-`, and without `K` it cannot show `K=True` in `A-K+`. `neither` is the count that matters for the weakest lever — those rows are unscorable even if C2 asks for one direction instead of two.

| Seed | N20 rows | No `A` | No `K` | **Neither** | Scorable | Fully viable | N4 rows | N4 viable | Eligible | Competent pool |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `20740101` | 20 | 7 | 6 | **3** | 17 | 10 | 4 | 3 | 64 | 38 |
| `20740102` | 20 | 4 | 11 | **2** | 18 | 7 | 4 | 0 | 64 | 27 |
| `20740103` | 20 | 7 | 5 | **3** | 17 | 11 | 4 | 3 | 64 | 37 |
| `20740104` | 20 | 3 | 6 | **2** | 18 | 13 | 4 | 2 | 64 | 40 |
| `20740105` | 20 | 7 | 7 | **4** | 16 | 10 | 4 | 2 | 64 | 32 |
| `20740106` | 20 | 6 | 8 | **1** | 19 | 7 | 4 | 2 | 62 | 31 |

**58 of 120** selected rows are fully viable, and **15** are unscorable even under the weakest reading. This is why the seed-level verdict is 0/6 rather than 5/6: C2 is judged per seed and fails on a single row.

## Lever 1 — raise `N`: it moves the wrong way

`N` is the number of target rows a seed must carry. Raising it adds rows that must *all* pass, so a seed's chance of being viable is the chance that a whole draw from the eligible universe is baseline-competent:

| Seed | `k = 4` | `k = 17` | `k = 20` |
| ---: | ---: | ---: | ---: |
| `20740101` | 1.16e-01 | 2.09e-05 | 1.71e-06 |
| `20740102` | 2.76e-02 | 6.12e-09 | 4.50e-11 |
| `20740103` | 1.04e-01 | 1.15e-05 | 8.11e-07 |
| `20740104` | 1.44e-01 | 6.43e-05 | 7.03e-06 |
| `20740105` | 5.66e-02 | 4.10e-07 | 1.15e-08 |
| `20740106` | 5.64e-02 | 3.59e-07 | 9.20e-09 |

**Cost:** none, because it cannot succeed. **Buys:** nothing. At `k = 4` a seed already has only a 2.8%–14.4% chance; at `k = 20` it is 10⁻⁶ or worse, and the six-seed requirement multiplies those figures together. Raising `N` makes the blocker strictly harder, so this lever is closed by arithmetic rather than by opinion.

## Lever 2 — a different block: the draw makes it hopeless

Drawing a fresh block from the same universes does not change the per-row availability, so it screens seeds rather than fixing rows. The six-seed joint chance is the product of the `k = 20` column above — around **10⁻³⁴** — which means the search is not expensive, it is unavailable. This lever is also the one that would look like outcome-independent screening while in fact being a search for a favourable draw.

## Lever 3 — change `C2`: only its strongest form works

Three readings, in decreasing strength:

| Reading | What it admits | Seeds viable | What it costs |
| --- | --- | ---: | --- |
| both directions on every row (adopted) | nothing; 0 unscorable rows | **0/6** | the current blocker |
| one direction on every row | `15` rows still unscorable | **0/6** | no change; still fails |
| a share of rows per seed | needs ≤ **35%%** scorable-or-not | 6/6 only by redefining the gate | the gate stops being C2 |
| select only rows carrying both paths | `115` rows, 0 unscorable | **6/6** | a new estimand |

**A per-row threshold cannot be tuned into working.** The best seed has **13 of 20** rows scorable; the worst has **7 of 20**. Admitting any seed at all through a share-of-rows gate means accepting that **35%** of a block need not be scorable, which is not C2 with a tolerance — it is a different gate wearing C2's name.

## The one lever that works is already built

The fourth reading is not hypothetical: [`a1_c8_target_selection_competent.json`](a1_c8_target_selection_competent.json) already selects blocks of 17–20 rows whose every member has both an `A` carrier and a `K` path, and the screen above confirms **0 failures in 115 rows** across the six seeds. C8's adopted floor of 17 is the level at which that block forms on every seed.

So the 0/6 finding is not a wall in front of the experiment; it is a wall in front of *one target population*. The unfiltered block asks C2 a question about representative eligible edges and cannot answer it. The filtered block asks it about baseline-competent edges and can. The difference is the whole decision, and it is the reason `A1-C8-SELECTION` is pending: adopting the filter changes what a positive C2 result would be evidence about.

## Limits

- **Availability is not a pass.** A row with both paths can still fail C2 on its cells; this record counts whether the cells are *observable*, not whether they behave.
- **`Y` is not screened by the gate.** 0 of 115 filtered rows also lack a baseline `Y`; the gate does not require it for the two `Y_MINUS` cells, and this record does not add a requirement the gate does not have. It records the count so the gap is visible rather than assumed away.
- **The filtered number is a tautology with a price.** The filter is defined as *has both paths*, so 0 failures is a restatement of the definition, not corroboration of it. What is informative is what the definition excludes: 177 of 382 eligible rows.

**Not evidence:** A count of the baseline paths each target row would need for C2's cells to be observable. It scores no C2, runs no cell, freezes no target, issues no grant, and makes no causal or capability claim. Availability is not a pass.

## Provenance

| Artifact | sha256 |
| --- | --- |
| `a1_baseline_availability_adopted.json` | `4c01b4e9c2b1c058ae35c33079b004f03eb49c715fe689b81f4ee8ffc817fa5b` |
| `a1_c8_target_selection.json` | `2af0a2e0f4d8464b8c8e9fcaeefeb0268b896551fb2046491962b6465c73d54b` |
| `a1_target_selection.json` | `6c8ff41c669b3973597244f3991ad24015640632371123af69bba59845556695` |
| `a1_c8_target_selection_competent.json` | `697dc9f95c606936a1d7b7bc8d59f4192f25db9e5b89a0a5b06a6a0a5d5dabde` |

_Generated by `python -m benchmarks.a1_viability_levers --write`; `--check` fails when this page, the artifact or either source disagrees. The verdict and threshold paragraphs are the only hand-written text._
