# A1 band frontier

Generated from `docs/a1_band_frontier.json` by `python -m benchmarks.a1_band_frontier --write`. Do not edit by hand.

**Design estimate, not an A1 result.** No split block has been run.

## Result

Yes, but only in one direction and by a bounded amount. At a 5%/5% guarantee the admissible bands at six seeds per block are **c ≥ 0.0633** and **f ≤ 0.0531**, so the committed **0.05** floor is already almost as high as it can go — raising it past **0.0531** starts declaring the size summary when the density summary is true — while the **0.09** ceiling is conservative and can drop to **0.0633** with the error budget intact. Widening that way is not a weakening: the cheapest admissible pair is **f 0.0500 / c 0.0700**, which holds both wrong-branch rates at 5% and both correct branches at 80% at **6 seeds per block** instead of the **9** the committed pair needs at the same guarantee — **3 seeds saved per block**. Widening past **c 0.0633** is where the discriminator does weaken: at six seeds and the committed floor, a ceiling below that value pushes the false-density rate above 5%, and at nine seeds the floor cannot rise past **0.0647** either. Collapsing the dead band into a single threshold at the midpoint is worse than either: it needs **8 seeds per block** at 5%, because a single cut cannot spend the error budget on one side and the power budget on the other, and it leaves no undecided outcome for the cases the design should refuse to call. No band choice does better than that floor: searching floors **0.02–0.10** against ceilings **0.03–0.12**, the cheapest admissible pair needs **6 seeds per block** at a 5% guarantee and **4** at 10%, so the bands as committed are worth **3 seeds** and no more at this per-seed SD. At the looser 10% budget the ordering flips and the single threshold wins with **4** seeds, because a budget that wide no longer repays the seeds the dead band spends on refusing to decide.

## Admissible band edges

| Seeds | SE | Ceiling can drop to | Floor can rise to |
| ---: | ---: | ---: | ---: |
| 6 | 0.038484 | 0.0633 | 0.0531 |
| 9 | 0.031422 | 0.0517 | 0.0647 |

At a 5% error budget with 80% power on both branches.

## Band pairs

| Floor | Ceiling | Dead band | Seeds 5% | Seeds 10% | Density power at 6 | Size power at 6 |
| ---: | ---: | --- | ---: | ---: | ---: | ---: |
| 0.0500 | 0.0900 | yes | 9 | 9 | 0.767 | 0.818 |
| 0.0582 | 0.0582 | no | 8 | 4 | 0.937 | 0.874 |
| 0.0500 | 0.0700 | yes | 6 | 6 | 0.894 | 0.818 |
| 0.0510 | 0.0650 | yes | 6 | 6 | 0.914 | 0.826 |
| 0.0700 | 0.0900 | yes | 12 | 9 | 0.767 | 0.929 |
| 0.0400 | 0.1000 | yes | 23 | 23 | 0.676 | 0.722 |
| 0.0680 | 0.0680 | no | 11 | 6 | 0.902 | 0.921 |
| 0.0600 | 0.0900 | yes | 9 | 9 | 0.767 | 0.884 |

## At six seeds per block

| Floor | Ceiling | Size true → density | Density true → size | Undecided (size) | Undecided (density) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.0500 | 0.0900 | 0.0127 | 0.0425 | 0.1694 | 0.1903 |
| 0.0582 | 0.0582 | 0.0628 | 0.0628 | 0.0628 | 0.0001 |
| 0.0500 | 0.0700 | 0.0357 | 0.0425 | 0.1464 | 0.0640 |
| 0.0510 | 0.0650 | 0.0456 | 0.0446 | 0.1287 | 0.0411 |
| 0.0700 | 0.0900 | 0.0127 | 0.1065 | 0.0587 | 0.1263 |
| 0.0400 | 0.1000 | 0.0073 | 0.0256 | 0.2705 | 0.2979 |
| 0.0680 | 0.0680 | 0.0394 | 0.0977 | 0.0394 | 0.0000 |
| 0.0600 | 0.0900 | 0.0127 | 0.0683 | 0.1029 | 0.1645 |

## Limits

- The band edges are a design convention, not a hypothesis test; the error budget is the probability of the wrong branch, not a p-value.
- Everything inherits the per-seed SD borrowed from 16-tag blocks; the admissible edges move with sigma, so a larger SD moves them inward.
- The two predictions are taken as point values, so a real split block landing between them is the undecided outcome the rule is designed to produce.
- Moving the bands changes only this design's cost; it does not make either summary better supported by the existing blocks.

## What this does not claim

A design estimate over committed artifacts. It runs no arm, measures no split block, and is not a treatment, target, freeze, grant or A1 cell.
