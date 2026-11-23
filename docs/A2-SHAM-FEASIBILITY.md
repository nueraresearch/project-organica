# A2 sham matching feasibility

**ID:** `A2-SHAM-FEASIBILITY-1`  
**Status:** NOT FEASIBLE PER EDGE — NO SHAM MATCHES EVERY NON-TARGET EDGE; AGGREGATE FORM AVAILABLE  
**Selection:** `docs/a1_c8_target_selection_competent.json` (`697dc9f95c606936`)  
**Cycles:** 120 · **endpoint cap:** 3 · **tolerance:** 6 cycles

A placebo-controlled A2 removes carriers for a matched sham block as well as for the target block,
so the non-local interference lands in the control. This page asks whether such a sham exists, using
only pre-treatment data: the no-arm replay's carriers, a static prediction of the carrier loss a
removal implies, and a hill-climb search under the target block's own size and degree cap.

## Result

| Seed | Targets | Carrier appearances | Target loss (cycles) | Sham mean abs diff | Max abs diff | Within tolerance | Sham disjoint |
|---|---|---|---|---|---|---|---|
| 20740101 | 20 | 1962 | 1075 | 1.97 | 30 | 90.2% | yes |
| 20740102 | 17 | 2611 | 1486 | 0.19 | 5 | 100.0% | yes |
| 20740103 | 20 | 2571 | 705 | 2.58 | 51 | 88.4% | yes |
| 20740104 | 20 | 2506 | 1017 | 2.76 | 78 | 92.9% | yes |
| 20740105 | 18 | 2562 | 1329 | 0.30 | 5 | 100.0% | yes |
| 20740106 | 20 | 2625 | 1186 | 0.59 | 13 | 96.4% | yes |

**Worst seed:** 88.4% of non-target edges within 6 cycles, mean absolute difference 2.76 cycles.

## The aggregate form

A C4' defined on the *mean* non-target perturbation, rather than on every edge, is a different design —
it was specified after the per-edge test failed and is recorded as such. On that reading the sham matches
on all six seeds: worst mean absolute difference 2.76 cycles, worst total gap 8.1%.

## What this decides

**Per edge: no construction found.** Three of six seeds put fewer than 95% of non-target edges within six cycles of the target block, with worst-case differences of 30 to 78 cycles, and a stronger max-first search did not find one either (89.3%, 75.9%, 85.7% on the three failing seeds). A C4' that judges every non-target edge separately is therefore left without a witnessed construction from this selection — which does not establish that none exists.

**This is not evidence about the organism.** It is a matching check on the no-arm carriers. A feasible
sham makes the pre-registration possible; it does not show the arms behave the same, and it must not be
reported as a result.
