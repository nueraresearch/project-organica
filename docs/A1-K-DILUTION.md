# A1 K dilution — more edges did not buy more K

**ID:** `A1-K-DILUTION-1`
**Status:** `DESCRIPTIVE — K DILUTION ACROSS TWO DECLARED WORLDS; NO ARM, NO THRESHOLD, NO REDESIGN`

**This is not an A1 result.** It compares two no-arm candidate universes; it runs no cell, selects no target, sets no threshold and chooses no redesign.

## Headline

| World | Tags | Seeds | Candidate edges | A available | K available | A&K | K density |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 16-tag | 16 | 6 | 383 | 279 | 242 | 197 | 63.2% |
| 28-tag | 28 | 6 | 1000 | 353 | 244 | 119 | 24.4% |

Candidate edges rose 383 -> 1000 (+161.1%), A-available rows rose 279 -> 353 (+26.5%), but K-available rows rose only 242 -> 244 (+0.8%). K density fell from 63.2% to 24.4%.

The edge count is not the constraint. The block-level K supply is almost unchanged while the denominator grows, so the **same K is spread across more edges**. That is dilution, not a shortage of possible edges.

## By seed

| World | Seed | Candidate edges | A | K | A&K | K density | K needed for 60 | Gap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 16-tag | `20650101` | 64 | 49 | 40 | 33 | 62.5% | 93.8% | 20 |
| 16-tag | `20650102` | 64 | 46 | 37 | 30 | 57.8% | 93.8% | 23 |
| 16-tag | `20650103` | 64 | 54 | 46 | 46 | 71.9% | 93.8% | 14 |
| 16-tag | `20650104` | 64 | 53 | 42 | 36 | 65.6% | 93.8% | 18 |
| 16-tag | `20650105` | 63 | 31 | 39 | 20 | 61.9% | 95.2% | 21 |
| 16-tag | `20650106` | 64 | 46 | 38 | 32 | 59.4% | 93.8% | 22 |
| 28-tag | `20660101` | 169 | 59 | 23 | 18 | 13.6% | 35.5% | 37 |
| 28-tag | `20660102` | 167 | 50 | 40 | 15 | 24.0% | 35.9% | 20 |
| 28-tag | `20660103` | 172 | 57 | 42 | 16 | 24.4% | 34.9% | 18 |
| 28-tag | `20660104` | 165 | 67 | 55 | 26 | 33.3% | 36.4% | 5 |
| 28-tag | `20660105` | 169 | 66 | 47 | 26 | 27.8% | 35.5% | 13 |
| 28-tag | `20660106` | 158 | 54 | 37 | 18 | 23.4% | 38.0% | 23 |

The 28-tag block's K supply is **23–55 rows** per seed, versus **37–46** in the 16-tag block. The larger block has more edges but not more K to distribute.

## K supply by transition type

| Transition | 16-tag edges | 16-tag K | 28-tag edges | 28-tag K | 16-tag K density | 28-tag K density |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| flip-P | 191 | 145 | 517 | 146 | 75.9% | 28.2% |
| flip-Q | 192 | 97 | 483 | 98 | 50.5% | 20.3% |

The absolute K counts by transition type are nearly identical across the two worlds, while the edge counts roughly double. This is the clearest signature of a numerator that does not scale with the denominator.

## Endpoint novelty

| Family | 16-tag edges | 16-tag K | 16-tag K density | 28-tag edges | 28-tag K | 28-tag K density |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| old-old | 383 | 242 | 63.2% | 296 | 56 | 18.9% |
| old-new | — | — | — | 531 | 140 | 26.4% |
| new-new | — | — | — | 173 | 48 | 27.7% |

The **old-old** family is not protected by being the original vocabulary: its K density falls as well. In the 28-tag world the new-involving families are not worse than old-old; the loss is not “new tags are bad”. It is lower support for each possible pair.

## U-strength quartiles

U quartiles are assigned **within each seed** (Q1 lowest strength, Q4 highest), then pooled. They are rank bins, not common absolute cut points.

| World | Quartile | U range | Edges | K available | K density |
| --- | --- | ---: | ---: | ---: | ---: |
| 16-tag | Q1 | 5–14 | 96 | 21 | 21.9% |
| 16-tag | Q2 | 11–17 | 96 | 51 | 53.1% |
| 16-tag | Q3 | 15–20 | 96 | 83 | 86.5% |
| 16-tag | Q4 | 19–27 | 95 | 87 | 91.6% |
| 28-tag | Q1 | 0–4 | 253 | 28 | 11.1% |
| 28-tag | Q2 | 3–6 | 249 | 37 | 14.9% |
| 28-tag | Q3 | 5–8 | 250 | 58 | 23.2% |
| 28-tag | Q4 | 7–18 | 248 | 121 | 48.8% |

The U gradient is real in both worlds, but it does not rescue the total: the 28-tag Q4 has 121 K rows across six seeds, about 20 per seed, not 60 per seed; the lower quartiles carry most of the diluted denominator. Selecting Q4 after seeing K would be selection on the preflight quantity.

## What this changes

- Candidate edges rose 383 -> 1000 (+161.1%), A-available rows rose 279 -> 353 (+26.5%), but K-available rows rose only 242 -> 244 (+0.8%). K density fell from 63.2% to 24.4%.
- The K supply is nearly constant by transition type as well: flip-P K rows 145 -> 146 while flip-P candidate edges 191 -> 517; flip-Q K rows 97 -> 98 while flip-Q candidate edges 192 -> 483.
- The old-old edge family also dilutes: 383 -> 296 edges, but K-available rows 242 -> 56 and K density 63.2% -> 18.9%. Old-new is 26.4% and new-new is 27.7% K in the 28-tag world, so the new tags are not the weak family by themselves; support per possible pair is what fell.
- The U gradient survives but does not rescue the numerator: Q4 K density is 91.6% in the 16-tag world and 48.8% in the 28-tag world, while Q1 is 21.9% and 11.1%. High-U edges are still the best K carriers, but Q4 supplies about 20 K rows per seed (121/6), not 60 per seed. Selecting Q4 after seeing K would also be selection on the preflight quantity.
- The 28-tag block's best seed has 55 K rows out of 165 edges (33.3%), needing 36.4% for 60 and therefore missing by 5 rows. Even its best seed does not reach the floor.

The redesign target is therefore **K-capable edges**, not independent edges. A larger universe that merely adds pairs without preserving K support repeats this failure.

## Limits

- K is a no-arm availability flag over 120 cycles, not a treatment measurement or a K-cycle rate.
- U is measured at cycle 36; the K-U association has no identified direction.
- The two worlds differ in tag count and tag mapping; six seeds per world do not isolate tag count from mapping or cell composition.
- U quartiles are within-seed ranks, not absolute strength thresholds; the labels are not comparable across seeds as cut points.
- The near-constant K total is descriptive for these two blocks, not a conservation law.
- No target was selected, no threshold changed, no freeze or grant exists and no A1 cell ran.

**Not evidence:** A descriptive comparison of existing no-arm candidate rows. It does not identify a cause, select a target, set a threshold, choose a redesign or park A1.

## Reproduce

```bash
python -m benchmarks.a1_k_dilution --check
python -m benchmarks.a1_k_dilution --self-test
```
