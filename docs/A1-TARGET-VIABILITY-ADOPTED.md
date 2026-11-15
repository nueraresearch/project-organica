# A1 target viability on the adopted block

**ID:** `A1-TARGET-VIABILITY-ADOPTED-1`
**Date:** 2026-11-15
**Status:** `FLAGGED — NO SEED IS C2-VIABLE ON EITHER TARGET DESIGN, MEASURED ON THE ADOPTED BLOCK`

**This is not an A1 result.** It reads the adopted block's no-arm baseline
([`a1_baseline_availability_adopted.json`](a1_baseline_availability_adopted.json), `A1-BASELINE-AVAILABILITY-ADOPTED-1`) and
counts how many of the frozen target strings could carry the manipulation C2 has to show. No cell ran, no target was
changed, no arm was applied.

## Why this record exists

[`A1-TARGET-VIABILITY.md`](A1-TARGET-VIABILITY.md) found **0/6** C2-viable seeds at both N4 and N20 — but it measured
seeds `20630101–20630106`. The freeze acts moved to `20740101–20740106` after that block was spent, and the viability
finding was never re-derived for the new targets. This record does that from committed data, so the acts are not held on
a number belonging to a different block.

## Relationship to the competence record

The headline competence counts already exist in [`A1-COMPETENCE-ADOPTED`](A1-COMPETENCE-ADOPTED.md)
(`A1-COMPETENCE-ADOPTED-1`, generated) — 12 of 24 and 58 of 120 competent, competent pool 27–40, 0/6 clean blocks.
This record does not restate them as its own: it adds the **per-path split** (how many targets lack `A` versus `K`,
which is why the union exceeds either marginal) and the **construction frontier** below, which neither record
computed.

## What C2 needs from a target row

`a1_arms.gate_c2` requires, per non-target and target row: in `A-K+`, `A` blocked **and** `K` present; in `A+K-`, `A`
present **and** `K` blocked. A target edge with no `A` carrier in the baseline cannot show `A=True` in `A+K-`; one with no
`K` served cannot show `K=True` in `A-K+`. Either gap fails C2 on that row, and C2 is judged per seed.

## Measurement

| Design | Seed | Targets | No `A` carrier | No `K` served | Seed C2-viable? |
| --- | ---: | ---: | ---: | ---: | --- |
| N4 | `20740101` | 4 | 0 | 1 | NO |
| N4 | `20740102` | 4 | 1 | 4 | NO |
| N4 | `20740103` | 4 | 1 | 0 | NO |
| N4 | `20740104` | 4 | 1 | 2 | NO |
| N4 | `20740105` | 4 | 1 | 2 | NO |
| N4 | `20740106` | 4 | 0 | 2 | NO |
| **N4 total** | | **24** | **4** | **11** | **0/6** |
| N20 | `20740101` | 20 | 7 | 6 | NO |
| N20 | `20740102` | 20 | 4 | 11 | NO |
| N20 | `20740103` | 20 | 7 | 5 | NO |
| N20 | `20740104` | 20 | 3 | 6 | NO |
| N20 | `20740105` | 20 | 7 | 7 | NO |
| N20 | `20740106` | 20 | 6 | 8 | NO |
| **N20 total** | | **120** | **34** | **43** | **0/6** |

Every target string is present in the baseline stream — `not in stream` is 0 in both designs, so these are rows that exist
and lack the path, not rows that are missing from the world.

## Reading

**The viability verdict reproduces on the adopted block, but its numbers do not.** The earlier report counted **10** of 24
and **52** of 120 carrier-missing rows on the spent block; the adopted block gives **4** of 24 and **34** of 120 against
`A`, and **11** of 24 and **43** of 120 against `K`. So the counts were not carried across blocks — the *verdict* was, and
it survives the re-derivation on its own data.

A freeze of either act would freeze target sets that C2 cannot score on any of the six seeds. That is a target-competence
blocker, and it is independent of the C1 denominator: the adopted block's cell-stream C1 minimum is **64** against the
floor of **60**, so C1 is met on its operative row while C2 is not.

## Construction frontier at C8's adopted floor

Competence is necessary but not sufficient: the block also has to be *constructible* under the endpoint cap of 3
that `A1-C8-EXPANSION-1` and the N20 rule share. Reading the competent pool from the same artifacts and searching
exactly for a `k`-row subset with every tag's degree ≤ 3:

| Seed | Competent pool | `k = 20` | `k = 18` | `k = 17` |
| ---: | ---: | --- | --- | --- |
| `20740101` | 38 | witness | witness | witness |
| `20740102` | 27 | **impossible** (exhaustive) | **impossible** (exhaustive) | witness |
| `20740103` | 37 | witness | witness | witness |
| `20740104` | 40 | witness | witness | witness |
| `20740105` | 32 | undecided (node budget) | witness | witness |
| `20740106` | 31 | witness | witness | witness |

## The frontier is a function of the cap, not a coincidence

Repeating the search at other endpoint caps shows what the number 17 is and is not:

| Cap | `k = 17` | `k = 18` | `k = 20` |
| ---: | --- | --- | --- |
| 2 | fails on `20740102`, `20740105`, `20740106` | fails on the same three | fails on the same three |
| **3** | **forms on all six** | fails on `20740102` | fails on `20740102` |
| 4 | forms on all six | forms on all six | forms on all six |

With a cap of 4 every seed takes twenty rows; with a cap of 2 not even seventeen does. So **17 is not overdetermined
by two independent arguments** — it is one point on a `(cap, k)` feasibility surface, and both the cap of 3 and the
floor of 17 were chosen by the project. What the agreement does establish is narrower and still useful: **given the
cap already in use, 17 is the largest block that forms on every seed, so C8's floor sits exactly at the ceiling.** A
larger `N_min` would have been infeasible at the cap; a smaller one would have been feasible at a cap the design does
not use. The number is tight, not corroborated twice.

**A competent block of 17 exists on all six seeds. At 18 it already fails on `20740102`.** C8's adopted floor is
`N_min = 17`, decided on 2026-11-15 for tolerance reasons that had nothing to do with construction; the two
decisions meet exactly at that number. That is the one piece of good news in this record: the competence blocker is
a **selection** problem, and the adopted floor is the level at which it is solvable on every seed.

What it costs is stated in [`A1-COMPETENCE-FILTER-DRAFT`](A1-COMPETENCE-FILTER-DRAFT.md) and is not a repair: a
screen on baseline `A` and `K` changes the target population from *representative eligible edges* to
*baseline-competent edges*. That is a new estimand, and it needs the owner's adoption before any act is re-issued
against it.

## Limits

Counts only. Nothing here scores C2, because no cell has run and C2 needs the treatment cells; this record counts whether
each target *could* satisfy C2's per-row requirement, from baseline availability alone. The C2 gate is the authority on
the cell, not this table.

## Reproduce

```bash
.venv/bin/python - <<'PY'
import json
base = json.load(open("docs/a1_baseline_availability_adopted.json"))
rows = {str(r["seed"]): {x["edge"]: x for x in r["rows"]} for r in base["per_seed"]}
for art, label in (("docs/a1_target_selection.json", "N4"), ("docs/a1_c8_target_selection.json", "N20")):
    a = json.load(open(art))
    for seed, block in a["per_seed"].items():
        t = block["selected"]; r = rows[seed]
        print(label, seed, len(t), sum(not r[x]["A"] for x in t), sum(not r[x]["K"] for x in t))
PY
```
