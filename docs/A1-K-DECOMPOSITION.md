# A1 K-availability decomposition — descriptive

**ID:** `A1-K-DECOMPOSITION-1`
**Status:** `DESCRIPTIVE — K SCARCITY DECOMPOSITION; NO ARM, NO THRESHOLD, NO DISPOSITION`

**This is not an A1 result.** It decomposes the no-arm K-availability counts; it runs no cell, selects no target, sets no threshold and chooses no redesign.

Six registered seeds, 382 first-36-cycle candidate edges, and the no-arm A+K+ baseline at 120 cycles. All quantities are descriptive; no treatment was applied and no threshold was set.

## Headline

- Candidate edges: **382**. A available: **281** (73.6%). K available: **228** (59.7%). A&K: **186** (48.7%).
- **K-specific gap:** 95 rows have A but no K; 42 have K but no A; 59 have neither. K is the larger single-path deficit.

## By seed

| Seed | Edges | A | K | A&K | A, no K | K, no A | Neither | K rate | K rate needed for 60 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `20630101` | 64 | 44 | 44 | 32 | 12 | 12 | 8 | 68.8% | 93.8% |
| `20630102` | 63 | 44 | 31 | 23 | 21 | 8 | 11 | 49.2% | 95.2% |
| `20630103` | 64 | 52 | 39 | 36 | 16 | 3 | 9 | 60.9% | 93.8% |
| `20630104` | 64 | 43 | 35 | 27 | 16 | 8 | 13 | 54.7% | 93.8% |
| `20630105` | 64 | 49 | 43 | 35 | 14 | 8 | 7 | 67.2% | 93.8% |
| `20630106` | 63 | 49 | 36 | 33 | 16 | 3 | 11 | 57.1% | 95.2% |

K is lower than A on five seeds and ties on `20630101`. Even if every candidate were selected, the K ceiling is 31–44; the remaining K shortfall to 60 is **16–29 rows** per seed.

## U-strength quartiles

Pooled quartiles across all 382 candidate edges. Strength is the cycle-36 directed U value; the bins are Q1 ≤ 11, Q2 12–16, Q3 17–20, Q4 ≥ 21.

| Quartile | Strength range | Edges | K available | K rate |
| --- | ---: | ---: | ---: | ---: |
| Q1 | 2–11 | 107 | 34 | 31.8% |
| Q2 | 12–16 | 107 | 53 | 49.5% |
| Q3 | 17–20 | 104 | 84 | 80.8% |
| Q4 | 21–26 | 64 | 57 | 89.1% |

| Seed | Low-U half rows | Low-U K rate | High-U half rows | High-U K rate |
| ---: | ---: | ---: | ---: | ---: |
| `20630101` | 35 | 54.3% | 29 | 86.2% |
| `20630102` | 32 | 21.9% | 31 | 77.4% |
| `20630103` | 34 | 38.2% | 30 | 86.7% |
| `20630104` | 36 | 41.7% | 28 | 71.4% |
| `20630105` | 35 | 42.9% | 29 | 96.6% |
| `20630106` | 32 | 37.5% | 31 | 77.4% |

The high-U half has a higher K rate on all six seeds, but it contains only 28–31 edges per seed. Enriching U cannot by itself produce a 60-row C1 stream.

## When K appears

| First K cycle | Edges | Share of all candidates | Share of K-available |
| --- | ---: | ---: | ---: |
| 1–30 | 138 | 36.1% | 60.5% |
| 31–60 | 62 | 16.2% | 27.2% |
| 61–90 | 19 | 5.0% | 8.3% |
| 91–120 | 9 | 2.4% | 3.9% |
| never | 154 | 40.3% | — |

154 of 382 rows have no K in 120 cycles; only 28 of the 228 available rows first form K after cycle 60. The main pattern is absence, not late arrival.

## By tag

Tag rows count **endpoint incidences**, not edges; each edge contributes to two tags. Pooled across seeds, so seed and tag are confounded.

| Tag | Incidences | K available | K missing | K rate | Seed rate range | Seeds below 50% |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `amber` | 47 | 21 | 26 | 44.7% | 0.0–100.0% | 3/6 |
| `fern` | 48 | 24 | 24 | 50.0% | 0.0–100.0% | 2/6 |
| `indigo` | 48 | 24 | 24 | 50.0% | 0.0–75.0% | 2/6 |
| `cedar` | 48 | 25 | 23 | 52.1% | 37.5–87.5% | 4/6 |
| `teal` | 48 | 25 | 23 | 52.1% | 0.0–87.5% | 2/6 |
| `sable` | 48 | 26 | 22 | 54.2% | 37.5–100.0% | 3/6 |
| `willow` | 48 | 26 | 22 | 54.2% | 0.0–87.5% | 1/6 |
| `maple` | 47 | 28 | 19 | 59.6% | 42.9–100.0% | 1/6 |
| `crimson` | 48 | 29 | 19 | 60.4% | 12.5–100.0% | 1/6 |
| `olive` | 48 | 30 | 18 | 62.5% | 37.5–87.5% | 1/6 |
| `yarrow` | 47 | 30 | 17 | 63.8% | 25.0–100.0% | 1/6 |
| `umber` | 47 | 31 | 16 | 66.0% | 50.0–87.5% | 0/6 |
| `ochre` | 48 | 32 | 16 | 66.7% | 0.0–100.0% | 1/6 |
| `birch` | 48 | 33 | 15 | 68.8% | 12.5–100.0% | 1/6 |
| `verdant` | 48 | 35 | 13 | 72.9% | 0.0–100.0% | 1/6 |
| `slate` | 48 | 37 | 11 | 77.1% | 37.5–100.0% | 1/6 |

No tag is consistently unavailable: the pooled range is 44.7–77.1%, but every tag swings widely by seed. Tag identity is not a stable redesign axis on these six seeds.

## Orientation and topology

| Candidate/reverse pair | Count |
| --- | ---: |
| Both K | 177 |
| Neither K | 101 |
| Candidate only | 3 |
| Reverse only | 5 |

K is **97.2%** concordant across candidate/reverse pairs (278/286). Only 8 pairs differ, so reverse orientation is not a K lever.

The candidate universe is near-regular: every 64-edge seed is 8-regular on 16 tags, and each 63-edge seed has fourteen tags of degree 8 and two of degree 7. Endpoint degree has no useful variation, so local degree cannot explain the K split.

## Redesign arithmetic

At 63–64 independent edges, reaching 60 K-available rows would require a K rate of 93.8–95.2%. The observed seeds are at 49.2–68.8%, and the high-U half is at 71.4–96.6% but has only 28–31 rows per seed. A larger independent universe lowers the required rate; 80 rows need 75%, 96 need 62.5%, and 120 need 50%. These are arithmetic requirements, not a proposed design.

| Independent edges | K rate needed for 60 |
| ---: | ---: |
| 63 | 95.2% |
| 64 | 93.8% |
| 80 | 75.0% |
| 96 | 62.5% |
| 120 | 50.0% |

## Limits

- K is measured in a no-arm replay over 120 cycles; it is not a treatment measurement.
- U is measured at cycle 36. The K–U association has no identified direction: K may support later U, or both may share a cause.
- Tag rows count endpoint incidences, not edges; an edge contributes to two tags. Pooled tag rates are confounded with seed.
- Six seeds do not establish a world-family-wide structure.
- No target was selected, no threshold changed, no freeze or grant exists and no A1 cell ran.

**Not evidence:** A descriptive decomposition of existing no-arm artifacts. It does not identify a cause, select targets, set a threshold, choose a redesign or park A1.

## Reproduce

```bash
python -m benchmarks.a1_k_decomposition --check
python -m benchmarks.a1_k_decomposition --self-test
```
