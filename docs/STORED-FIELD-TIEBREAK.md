# Stored-field tie-break — post hoc diagnostic

Generated from `docs/stored_field_tiebreak.json` by `python -m benchmarks.stored_field_tiebreak --write`. Do not edit by hand.

**Verdict: `SERVED SET UNCHANGED; ORDER CHANGES IN 12 CYCLES`.** Replacing source/target with the stored strength/ratio proxy changes no top-20 membership. It changes only the order inside tie groups.

## Design

- Six consumed seeds (`20611601, 20611602, 20611603, 20611604, 20611605, 20611606`), 120 cycles each, **111275** ranked rows.
- **701** nonempty cycles and **13604** top-20 seats.
- Baseline tie-break: `source`, then `target`.
- Alternative tie-break: stored `strength` descending, then `source`, then `target`.
- The stored field is **`min(1, ratio)`**, not the uncapped ratio.
- **Served set** means top-20 membership, not the full cap allocation.

## Served-set change

| Quantity | Change |
| --- | ---: |
| Top-20 seats changed | **0** |
| Windows changed | **0** |
| Edge–seed pairs gained | **0** |
| Edge–seed pairs lost | **0** |

The unique edge–seed set is identical: **848** pairs in both orders.

## Order change

The stored field does change the order inside tie groups:

| Quantity | Value |
| --- | ---: |
| Windows with a changed top-20 order | **12** |
| Top-20 positions changed | **37** |
| Mean absolute shift | **1.189** |
| Maximum absolute shift | **2** |

## Tie structure

| Quantity | Value |
| --- | ---: |
| Windows with a cutoff tie | **120 / 701 (17.12%)**
| Cutoff ties resolved by strength | **0** |
| Cutoff ties with both strengths at 1.0 | **24** |
| Adjacent top-20 primary ties | **2677 / 12903 (20.75%)**
| Adjacent full-list primary ties | **29319 / 110574 (26.52%)**
| Top-20 rows involved in a primary tie | **4944 / 13604 (36.34%)**
| Tie groups with different stored strength | **24** |
| Those groups inside the top 20 | **23** |

Every cutoff tie has the same stored strength. The 24 cutoff ties where both rows are saturated at 1.0 are the cases where an exact uncapped ratio could still separate them; that comparison is not available from this cache.

## Checks

| Check | Passes |
| --- | --- |
| `all_cycles_present` | yes |
| `nonempty_cycles` | yes |
| `same_top20_membership` | yes |
| `no_pairs_gained_or_lost` | yes |
| `stored_field_engages` | yes |
| `cutoff_ties_present` | yes |
| `cutoff_ties_have_equal_strength` | yes |
| `different_strength_ties_not_at_cutoff` | yes |

## What this does and does not establish

This is a null on top-20 membership under a stored-field tie-break. It does not show that ratio is irrelevant to ranking: it shows that the stored capped ratio is constant within every cutoff tie in these six worlds, so it cannot choose among the rows that decide the boundary.

The result is candidate ordering only. It does not measure served predictions, asserted edges, downstream acquisition, transfer or capability, and the six seeds are reused. No engine file changed.

A post-hoc diagnostic on six already-consumed seeds. The stored strength is capped at 1, so an exact uncapped ratio is not tested where both tied rows are saturated. The result is candidate ordering, not served prediction, assertion, transfer or capability.
