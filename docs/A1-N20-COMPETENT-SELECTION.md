# A1 N=20 competent target-selection rule — pre-registered draft

**ID:** `A1-N20-COMPETENT-1`
**Status:** `DRAFT — RULE PRE-REGISTERED, NOT FROZEN, NOT APPLIED, NOT RUN, NO GRANT`

**This is not an A1 result, a target freeze, a target selection, a grant or a run.** It fixes a rule and counts whether the existing candidate pool could supply it. No target edge has been selected.

## Rule

| Element | Value |
| --- | --- |
| Rows per seed | **20** |
| Candidate universe | The first 36 acquisition cycles, one orientation per candidate, with positive cycle-36 U strength and cycle membership. |
| Competence screen | Both baseline A and baseline K must be true in the no-arm A+K+ replay. A row missing either path is ineligible; there is no fallback to a non-competent row. |
| Selection order | Force the current N4 targets that pass the competence screen. Then visit the remaining eligible edges in ascending sha256('A1-N20-COMPETENT-1|seed|source>target') order and accept an edge only when both endpoint caps remain and the residual graph still admits enough edges to reach 20. The result is the lexicographically earliest 20-edge b-matching, not a first-fit greedy pass. The hash is blind to U magnitude, treatment outputs, reports and outcomes. |
| Endpoint cap | at most **3** selected edges per tag |
| Overlap | permitted; each tag may appear in at most three selected edges |
| Failure | If fewer than 20 eligible rows can be selected after the degree cap, that seed fails and the block is not run. Do not add non-competent rows, relax the cap, or re-select after seeing treatment data. |
| Current N4 preservation | Only the current N4 targets that pass the competence screen. The carrier-missing N4 rows are deliberately dropped; this is a replacement N20 block, not a superset of the current N4 set. |

The screen is **pre-treatment but not future-blind to the 120-cycle no-arm baseline**. It uses no treatment output and no report field, but it changes the target population. It is a new estimand, not a repair of the current representative target set.

## Feasibility

| Seed | Competent candidates | Required | Current N4 competent | Current N4 dropped | New rows needed | Max cap matching | Feasible? |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `20630101` | 32 | 20 | 2 | 2 | 18 | 32 | YES |
| `20630102` | 23 | 20 | 3 | 1 | 17 | 23 | YES |
| `20630103` | 36 | 20 | 3 | 1 | 17 | 36 | YES |
| `20630104` | 27 | 20 | 1 | 3 | 19 | 27 | YES |
| `20630105` | 35 | 20 | 2 | 2 | 18 | 35 | YES |
| `20630106` | 33 | 20 | 1 | 3 | 19 | 33 | YES |

**Seeds feasible:** **6/6**; competent candidates **23–36** per seed; maximum capacity-respecting matching **23–36** rows; current N4 contributes **12/24** rows and drops **12/24**.

A capacity-respecting b-matching with the current competent N4 rows forced reaches at least 20 on all six seeds: 23-36 A&K-available candidates per seed, and a maximum matching of 23-36 rows under the three-edge endpoint cap. The current N4 block contributes only 12 of its 24 rows; the other 12 are carrier- or admission-missing and are dropped. Existence is not a selected target set, a freeze or a result.

## Consequences

| Gate | Consequence |
| --- | --- |
| C2 | All selected rows are baseline A/K-competent under the stated reading. Exact C2 remains a treatment measurement; this rule removes the baseline-ineligible rows rather than proving C2 will pass. |
| C8 | 20 rows give a 1/20 = 0.05 step at the unchanged 0.05 ceiling; one assertion is at the ceiling and two exceed it. The C8 threshold is not changed. |
| C1 | Unaffected. C1's full-stream K availability remains 31-44 against the 60-row floor; a competent target block cannot repair the denominator. |
| Estimand | Changes the target population from representative eligible edges to baseline-competent edges. It is a new estimand and cannot be described as a repair of the current representative target set. |
| Blindness | The screen uses no treatment output and no report field. It is pre-treatment, but it is not future-blind to the 120-cycle no-arm baseline. That limitation is part of the rule. |

## Disposition

This is a draft rule only. It is not adopted, not frozen, not applied and not run. Adopting it requires a separate target-freeze act and a separate dated grant; it does not change the current N4 manifest or authorise an N20 cell.

**Not evidence:** A pre-registered selection rule and a feasibility count over existing no-arm artifacts. No target edge is selected, no target is frozen, no grant exists, no A1 cell runs and no C2/C8 result is measured.

## Reproduce

```bash
python -m benchmarks.a1_n20_competent_selection --check
python -m benchmarks.a1_n20_competent_selection --self-test
```
