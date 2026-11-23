# A1 competence filter — the rule, and what it would change

**ID:** `A1-COMPETENCE-FILTER-DRAFT-1`

**Date:** 2026-11-15

**Status:** `DRAFT — RULE STATED, CHANGE MEASURED, AND THE N=20 FILTER DOES NOT FORM ON EVERY SEED; NOT APPLIED, NOT FROZEN, NO GRANT, NO RUN`

**Block:** `2074` — the reserved A1-TWO-PATH-1 candidate block; this draft re-selects it from committed artifacts and spends nothing

## The rule

**A1-COMPETENCE-FILTER-1.** Restrict each published selection's eligible set to the rows whose baseline A and K paths are both present, and leave everything else in the rule alone.

1. Rebuild the candidate universe exactly as the published rule does: the first 36 acquisition cycles, one orientation per unordered pair.
2. Apply the published eligibility test: positive cycle-36 U strength and cycle membership.
3. Add one predicate: both baseline paths, A and K, must be true for that directed edge in the recorded no-arm availability.
4. Order the remaining edges by ascending sha256('A1-TARGET-1|seed|a>b') — the published salt, unchanged — and walk that order, skipping an edge whose endpoint already holds its cap, until n rows are taken.
5. For this draft the walk is repeated under deterministic shuffles to exhibit the best block that exists at all; the published order is reported beside it, because the two differ.
6. Stop at n = 4 (endpoint cap 1) or n = 20 (endpoint cap 3). One orientation per pair; no edge repeated.
7. If fewer than n edges are accepted, the seed forms no target set and the block is VOID. No non-competent row is ever added as a fallback.

**Unchanged:** the candidate universe and the 36-cycle boundary; the strength and cycle-member eligibility test; the hash order and its salt; the row counts (4 and 20) and the endpoint caps; every threshold: no gate, floor or criterion moves.

**Changed:** which rows are eligible: A-and-K-available only; therefore which rows are selected, on every seed; and, in consequence, the population the C8 result would speak about.

## What it would change — N=4

| Design | Rows | Kept | Replaced | Added | Seeds with a block | Seeds changed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **N=4** | 24 | 10 | 14 | 14 | **6 of 6** | 6 of 6 |

| Seed | Competent pool | Published walk | Best found | Kept | Replaced | Added | Verdict |
| ---: | ---: | --- | --- | ---: | ---: | ---: | --- |
| 20740101 | 38 | 4 rows | **4 rows** | 3 | 1 | 1 | FORMED — WITNESS RECORDED |
| 20740102 | 27 | 4 rows | **4 rows** | 0 | 4 | 4 | FORMED — WITNESS RECORDED |
| 20740103 | 37 | 4 rows | **4 rows** | 2 | 2 | 2 | FORMED — WITNESS RECORDED |
| 20740104 | 40 | 4 rows | **4 rows** | 2 | 2 | 2 | FORMED — WITNESS RECORDED |
| 20740105 | 32 | 4 rows | **4 rows** | 2 | 2 | 2 | FORMED — WITNESS RECORDED |
| 20740106 | 31 | 4 rows | **4 rows** | 1 | 3 | 3 | FORMED — WITNESS RECORDED |

## What it would change — N=20

| Design | Rows | Kept | Replaced | Added | Seeds with a block | Seeds changed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **N=20** | 120 | 38 | 42 | 42 | **4 of 6** | 6 of 6 |

| Seed | Competent pool | Published walk | Best found | Kept | Replaced | Added | Verdict |
| ---: | ---: | --- | --- | ---: | ---: | ---: | --- |
| 20740101 | 38 | 20 rows | **20 rows** | 10 | 10 | 10 | FORMED — WITNESS RECORDED |
| 20740102 | 27 | 17 rows | **17 rows** | 0 | 0 | 0 | IMPOSSIBLE — EXHAUSTIVE |
| 20740103 | 37 | 20 rows | **20 rows** | 11 | 9 | 9 | FORMED — WITNESS RECORDED |
| 20740104 | 40 | 20 rows | **20 rows** | 13 | 7 | 7 | FORMED — WITNESS RECORDED |
| 20740105 | 32 | 16 rows | **18 rows** | 0 | 0 | 0 | UNDECIDED — BEST FOUND ONLY |
| 20740106 | 31 | 19 rows | **20 rows** | 4 | 16 | 16 | FORMED — WITNESS RECORDED |

**The N=20 result is the one that matters for the decision.** a competent twenty-row block forms on only 4 of 6 seeds; the published hash-order walk forms 3 of 6. 1 seed(s) are proven impossible by exhaustive enumeration — every candidate subset was checked and none satisfies the endpoint cap — and 1 are undecided with a best block of fewer than twenty rows. The count comparison (27-40 competent rows against 20 needed) was therefore not a construction: under the cap, competence is short at the block level.

The filter is necessary and, on its own, not sufficient. It fixes the rows a C8 result would speak about, but it cannot produce a twenty-row block on every seed under the endpoint cap the rule already carries. The remaining levers are a different cap, a wider universe (option C) or declining to adjudicate C8 on this block (option B). None of them is a no-op, and none is chosen here.

**Impossible by exhaustion:** 20740102. **Does not establish:** that a competent block exists on the undecided seeds, or that no block exists there under a different cap. A witness proves a block exists; the absence of one proves nothing, which is why the exhaustive verdict is reported separately from the search.

## What it does to the estimand

**Before.** The effect on the n selected rows of each seed, where selection is a hash over a universe screened only for strength and cycle membership.

**After.** The effect on the n selected rows of each seed, where selection is a hash over that same universe screened additionally for baseline A and K availability — the rows on which a C2 cell set and an A-K- double block can be observed at all.

- The population narrows: rows that cannot carry both paths leave the target set, so the measurement no longer averages over rows whose outcome is mechanically unavailable.
- Rates can rise by construction. A competent-only block removes rows that could not have produced the outcome, which is a denominator change, not evidence of a treatment effect.
- External validity narrows with it: a C8 result would speak about A-and-K-available edges on this universe, not about selected edges in general.
- Eligibility is measured before any arm is applied, so the filter is pre-treatment — which is what makes it admissible as a selection rule rather than a post-hoc exclusion.

**What does not move:**
- C1's denominator: it counts observed paired-control rows over the whole cell stream, so changing which rows are targets changes no count. C1 remains unscored.
- C4's exposure: the non-target set is the cell stream minus N, which is set by N and not by which edges are target rows. Filtering buys no relief from the 108 non-target rows per seed.
- Nothing about C2's treatment gate: a no-arm filter cannot show that an absent path stays absent under treatment.

## Consequences of adopting it

- **N=4:** 10 of 24 rows are kept and 14 replaced across the block; a competent four-row set forms on 6 of 6 seeds.
- **N=20:** a competent twenty-row block forms on only 4 of 6 seeds; the published hash-order walk forms 3 of 6. 1 seed(s) are proven impossible by exhaustive enumeration — every candidate subset was checked and none satisfies the endpoint cap — and 1 are undecided with a best block of fewer than twenty rows. The count comparison (27-40 competent rows against 20 needed) was therefore not a construction: under the cap, competence is short at the block level.
- **Records:** Adopting this rule re-issues both target tables and therefore both freeze acts' recorded target sets, the C5 carrier-cycle record (its N=20 rows would be re-selected) and every artifact that quotes the current selections. It cannot be adopted for C8 as it stands: the filter leaves at least one seed without a block.

## Integrity

The unfiltered pass reproduces every recorded selection edge for edge on all six seeds for both designs; that is what licenses calling the filtered pass a restriction of the published rule rather than a new one.

Eligible rows without an availability record: **0**. Selected rows that are not competent: **0**.

**Not evidence:** A draft selection rule and the change it would make. It applies nothing, freezes nothing, runs no cell, changes no threshold and makes no claim that C8 or C2 would pass under it. It does not select, reserve or spend a seed block.

Reproduce with `python -m benchmarks.a1_competence_filter_draft --write`; `--check` re-derives the whole draft from the source artifacts.
