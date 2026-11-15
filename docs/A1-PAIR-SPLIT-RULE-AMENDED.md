# A1 pair-split rule, amended

Generated from `docs/a1_pair_split_rule_amended.json` by `python -m benchmarks.a1_pair_split_rule_amended --write`. Do not edit by hand.

**Amended design rule, not a result. No split block has been run.**

## Result

The amended rule keeps the committed construction, the committed six seeds per block and the committed **0.05** floor, and moves **one** number: the density ceiling falls from **0.09** to **0.07**. What it supersedes is the previous rule's cost, not its intent. `A1-OFFSET-DISCRIMINATOR-SPEC-1` needed **9** seeds per block at a 5%/5% guarantee and reached only **0.767** density-branch power at six; at the repaired ceiling the same six seeds hold the false-density rate at **0.0357** and the false-size rate at **0.0425**, with **0.818** power on the size branch and **0.894** on the density branch — admissible at the stated budget, so the seeds the construction already lists are enough and no new seed is bought. The amended rule is therefore: **size** if |d| ≤ **0.05**, **density** if d ≤ **−0.07**, undecided between them, on the split-32 minus split-48 difference with predictions **0.000** and **−0.116**. The ceiling cannot fall further at this budget: **0.0633** is the admissible edge at six seeds, and below it the rule starts calling density on seeds where the size summary is true. The ceiling touches only the density branch's two outcomes: the size branch's false rate is **0.0425** under either band, which is why the floor, not the ceiling, binds the size account. The amendment costs nothing to adopt — it removes the need for the three extra seeds the committed bands implied — and it is written as a separate artifact so the committed spec remains readable as the rule that was signed.

## The rule

| Element | Value |
| --- | --- |
| Statistic | measured offset(split-32) minus offset(split-48) |
| Size if | `|d| <= 0.05` |
| Density if | `d <= -0.07` |
| Undecided if | `-0.07 < d < -0.05, or d > 0.05` |
| Predictions | size 0.000, density -0.11638 |
| Seeds per block | 6 (20690101, 20690102, 20690103, 20690104, 20690105, 20690106) |
| Error budget | 0.05 per wrong branch |
| Power target | 0.80 per correct branch |

## What changed and what it costs

| Quantity | Committed | Amended |
| --- | ---: | ---: |
| Density ceiling | 0.09 | 0.07 |
| Seeds per block at 5% | 9 | 6 |
| Seeds saved per block | — | 3 |

## At the committed six seeds per block

| Quantity | Committed bands | Amended bands |
| --- | ---: | ---: |
| Size branch power | 0.8179 | 0.8179 |
| Density branch power | 0.7672 | 0.8935 |
| Declares density when size is true | 0.0127 | 0.0357 |
| Declares size when density is true | 0.0425 | 0.0425 |

## Superseded numbers

| Artifact | Field | Committed | Amended |
| --- | --- | --- | --- |
| A1-OFFSET-DISCRIMINATOR-SPEC-1 | decision_rule.if_abs_above | 0.09 with the density sign -> density tracks the level | 0.07 with the density sign |
| A1-SPLIT-POWER-1 | found.seeds_both_at_primary | 9 | 6 |

## Provenance

| Value | Artifact | Field |
| --- | --- | --- |
| floor 0.05 | `a1_offset_discriminator_spec.json` | `constants.decision_floor` |
| ceiling 0.09 (superseded) | `a1_offset_discriminator_spec.json` | `constants.decision_ceiling` |
| ceiling 0.07 (amended) | `a1_band_frontier.json` | `found.cheapest_ceiling` |
| six seeds per block | `a1_offset_discriminator_spec.json` | `construction.seeds` |
| admissible ceiling edge 0.0633 | `a1_band_frontier.json` | `found.bounds[0].ceiling_min` |
| per-seed SD 0.066656 | `a1_split_power.json` | `found.primary_sigma` |

## Limits

- The amendment changes a rule on paper only; no split block has been run, so the error rates it guarantees are the design's, not a measurement.
- The seeds the construction lists are reused, but they have never been spent on a split block; the budget statement says the block is sufficient, not that it has been executed.
- The per-seed SD is borrowed from 16-tag blocks; at a larger SD the admissible ceiling rises and the rule would need re-pricing before use.
- The committed spec is left unedited on purpose: a reader must be able to see the rule that was signed beside the rule that replaces it.

## What this does not claim

An amended design rule priced from committed artifacts. It runs no arm, measures no split block, and is not a treatment, target, freeze, grant or A1 cell.
