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
