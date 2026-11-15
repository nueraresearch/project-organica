# A1 cap-112 ordering term

Generated from `docs/a1_cap112_ordering_term.json` by `python -m benchmarks.a1_cap112_ordering_term --write`. Do not edit by hand.

**Descriptive attribution, not an A1 result.** Counterfactual orderings re-rank a frozen stream; they are not runs.

## Result

The target-entropy term gates these edges, but it cannot be what selects `flip_q` over `flip_p`: the engine computes **one** entropy over each source's outgoing distribution, so every edge out of a source shares it. What tracks exclusion is entropy's **level**: served candidates average **3.147** and unserved ones **3.678**, on the same 0-4 bit scale, so the window is filled by low-entropy sources and emptied of high-entropy ones regardless of family. Within a source the decision falls to the terms after entropy: of **11232** source-cycles that carry both a `flip_p` and a `flip_q` candidate, **11232** have identical entropy (as the construction requires), **8343** give the `flip_p` edge the higher probability (**0.1229** against **0.0569** on average) and **8491** rank the `flip_p` edge first. The family split in the unserved set follows from that: `flip_q` candidates average **0.0569** transition probability and **12.3** count against **0.1229** and **10.7** for `flip_p`, and `flip_q` serves at **0.829** against **0.979**. Removing entropy from the key does not recover the window — re-ranking by probability alone rescues **17** of **73** and by count alone **20** — because the excluded edges are also low on both of those terms. The ordering that pushes them out is therefore entropy-`then`-probability-`then`-count acting on a low-count, high-entropy tail, not an entropy penalty aimed at `flip_q`.

## Served against unserved

| Set | Candidates | Mean entropy | Mean probability | Mean count |
| --- | ---: | ---: | ---: | ---: |
| served | 691 | 3.147 | 0.0952 | 11.7 |
| unserved | 73 | 3.678 | 0.0402 | 9.7 |

## Recovered by ordering

| Ordering | Unserved edges inside the transition window |
| --- | ---: |
| engine (observed) | 0 |
| probability only | 17 |
| count only | 20 |

## By family

| Family | Candidates | Served | Serve rate | Mean entropy | Mean probability | Mean count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| flip_p | 383 | 375 | 0.979 | 2.942 | 0.1229 | 10.7 |
| flip_q | 381 | 316 | 0.829 | 3.455 | 0.0569 | 12.3 |

## Within a source

| Quantity | Value |
| --- | ---: |
| Source-cycles carrying both families | 11232 |
| Of those, identical entropy | 11232 |
| Of those, flip_p has the higher probability | 8343 |
| Of those, flip_p ranks first | 8491 |

## Per seed

| Block | Seed | Candidates | A | Unserved | Probability | Count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| current-16 | 20630101 | 64 | 57 | 7 | 2 | 3 |
| current-16 | 20630102 | 63 | 57 | 6 | 2 | 3 |
| current-16 | 20630103 | 64 | 60 | 3 | 1 | 0 |
| current-16 | 20630104 | 64 | 55 | 9 | 2 | 2 |
| current-16 | 20630105 | 64 | 59 | 5 | 3 | 4 |
| current-16 | 20630106 | 63 | 57 | 6 | 0 | 0 |
| fresh-16 | 20650101 | 64 | 59 | 5 | 2 | 3 |
| fresh-16 | 20650102 | 64 | 56 | 8 | 2 | 1 |
| fresh-16 | 20650103 | 64 | 59 | 5 | 2 | 1 |
| fresh-16 | 20650104 | 64 | 63 | 1 | 0 | 0 |
| fresh-16 | 20650105 | 63 | 52 | 11 | 1 | 3 |
| fresh-16 | 20650106 | 64 | 57 | 7 | 0 | 0 |

## Limits

- The counterfactual orderings re-rank frozen candidate lists; they are not runs, because serving a different set would change later reinforcement.
- Entropy is per source, so no within-source comparison can test it as a family discriminator; the test is between sources.
- Served versus unserved entropy is a comparison of the sets the window did and did not reach, not an intervention on the key.
- One cap pair and one world family: this attributes the cap-112 exclusion, not a general property of the ordering.

## What this does not claim

A descriptive attribution of the cap-112 window on twelve no-arm 16-tag seeds. It does not show that a different ordering would serve these edges in a real run, and it is not a treatment, target, freeze, grant or A1 cell.
