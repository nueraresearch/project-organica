# A1 target viability — N4 vs N20 carrier-missing rows and C2

**ID:** `A1-TARGET-VIABILITY-1`
**Status:** `FLAGGED — C2 NOT PASSABLE UNDER EITHER TARGET SET`

**This is not an A1 result.** It is a read-only report over the no-arm carrier and baseline-availability artifacts; no cell was run and no target was changed.

## C2 contract

C2 requires every target row in A-K+ to keep K, in A+K- to keep A, in Y_MINUS_A+K+ to keep A and K while Y is blocked, and in Y_MINUS_A-K+ to keep K while A and Y are blocked. A row that cannot meet a cell fails the seed because C2 is all-row and per-seed.

A carrier-missing target loses the three K-requiring cells. If it also lacks admission, it loses all four. Because C2 is all-row and per-seed, one such target makes the seed unable to pass C2.

## N4 vs N20

| Design | Target rows | Carrier-missing | Missing rate | Seeds with a missing row | C2 failing cell-rows | C2 failing rate | Fully C2-viable rows | C2-viable seeds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **N4** | 24 | 10 | 41.7% | 6/6 | 38/96 | 39.6% | 12 | 0/6 |
| **N20** | 120 | 52 | 43.3% | 6/6 | 202/480 | 42.1% | 54 | 0/6 |

**N20 does not repair C2.** It adds **96** target rows, of which **42** lack a carrier (43.8%), retains all **10** N4 carrier-missing rows, and leaves **0/6** seeds C2-viable versus **0/6** at N4. Its C2 failing cell-rows rise from **38** to **202** (39.6% to 42.1%).

## Per-seed rows

### N4

| Seed | Targets | Carrier-missing | Missing rate | C2 failing cells | C2 failing rate | Fully C2-viable | Seed C2-viable? |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `20630101` | 4 | 1 | 25.0% | 5/16 | 31.2% | 2 | NO |
| `20630102` | 4 | 1 | 25.0% | 3/16 | 18.8% | 3 | NO |
| `20630103` | 4 | 1 | 25.0% | 4/16 | 25.0% | 3 | NO |
| `20630104` | 4 | 2 | 50.0% | 9/16 | 56.2% | 1 | NO |
| `20630105` | 4 | 2 | 50.0% | 7/16 | 43.8% | 2 | NO |
| `20630106` | 4 | 3 | 75.0% | 10/16 | 62.5% | 1 | NO |

### N20

| Seed | Targets | Carrier-missing | Missing rate | C2 failing cells | C2 failing rate | Fully C2-viable | Seed C2-viable? |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `20630101` | 20 | 5 | 25.0% | 26/80 | 32.5% | 10 | NO |
| `20630102` | 20 | 12 | 60.0% | 48/80 | 60.0% | 5 | NO |
| `20630103` | 20 | 8 | 40.0% | 27/80 | 33.8% | 12 | NO |
| `20630104` | 20 | 11 | 55.0% | 41/80 | 51.2% | 7 | NO |
| `20630105` | 20 | 7 | 35.0% | 28/80 | 35.0% | 10 | NO |
| `20630106` | 20 | 9 | 45.0% | 32/80 | 40.0% | 10 | NO |

## What the counts mean

| Category | N4 | N20 |
| --- | ---: | ---: |
| Target rows | 24 | 120 |
| Carrier-missing rows | 10 | 52 |
| Carrier + admission missing | 4 | 18 |
| Admission missing, carrier present | 2 | 14 |
| Fully C2-viable rows | 12 | 54 |
| C2 failing cell-rows | 38 | 202 |
| C2-viable seeds | 0/6 | 0/6 |

The carrier-missing count is not a substitute for the C2 count: a target with a carrier but no admission still fails two C2 cells, and a target missing both fails four.

## Disposition

Do not treat N20 as a C2 repair. If C2 must be adjudicable, the target block needs a new pre-outcome viability criterion; a post-outcome swap is not permitted. Until then, record C2 as not adjudicable rather than freezing a target set that cannot pass it.

**Limits:** C2 treatment effects, C1, C4, C7 and C8 remain unmeasured. The 60-row C1 floor is separately below the observed baseline denominator. This report does not choose a replacement target set and does not freeze, grant or run one.

**Not evidence:** A read-only target-viability report over no-arm artifacts. It runs no A1 cell, freezes no target, makes no causal or capability claim, and does not measure C2 or any treatment effect.

## Reproduce

```bash
python -m benchmarks.a1_target_viability --check
python -m benchmarks.a1_target_viability --self-test
```
