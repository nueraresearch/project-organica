# The admission change, pre-registered with fresh seeds (2026-11-07)

**This block has run: the frozen analysis path returned ADOPT THE ADMISSION RULE.** §9 records the result, and §1–§8 are preserved exactly as committed before the run.

**Status: FROZEN, NOT RUN (ready; no judged cell).** No cell, no judged world and no judged
engine cycle exist for this block. The criteria, the bar, the guard, the seeds and the
decision table below are committed before the run and may not be changed afterwards; a
defect found later is disclosed as an amendment, and the pre-registered reading stands
unless the amendment says plainly that it withdraws it.

This block confirms one thing: whether the admission change specified in
`docs/RANKING-ADMISSION-DESIGN.md` reproduces the coverage gain the completed ordering run
measured, on seeds that block did not use. The numbers are in
`docs/ranking_admission_prereg.json`, and this document is rendered from that artifact.

## 1. Question

Does **global count-ranked admission** beat **diversity-first admission** in world-edge coverage at the sparsest
density, on fresh seeds, without losing coverage where the world is dense?

## 2. Design

- **Arms:** control is the engine's own selection: rank every eligible candidate by count and take the top k at the cap; treatment is each slot takes the eligible candidate whose left-hand tag has the fewest already-admitted outgoing edges, with count as the tie-break.
- **Caps:** 20 and 40.
- **World family:** one family, 16 tags, so |P_world| = 240 directed non-self pairs.
- **Densities:** 0.1, 0.2, 0.4, 0.6, 0.8, i.e. 24, 48, 96, 144, 192 true edges.
- **Eligibility:** all rows stay eligible, including intra-cell co-occurrence rows.
- **Exposure:** the ordering block's constant exposure scheme, unchanged.
- **Horizon:** the ordering block's constant horizon, unchanged.
- **Cells:** 160 — 2 arms x 2 caps x 5 densities x 8 seeds = 160.

## 3. Seeds

Block **20310501–20310508**, bootstrap **20310509**. the first contiguous window of nine numbers at or after 20310501 that appears in no file under docs, tests, benchmarks, research-journal or papers; the bootstrap seed is the ninth and is not a world seed

recording this block consumes it for the corpus seed scan, which is the intended effect: a declared block is registered rather than left free

## 4. The bar, and where it comes from

**Adoption bar 0.08.** calibrated on the completed ordering run (docs/rank_ordering_result.json): one half of its measured mean delta, 0.1615, floored to two decimals. That run is not the block being judged, so the bar is not computed from the data it judges, and the rule is a policy rather than a fit: an adoption must retain half the observed effect under replication

**Guard bar -0.05.** declared, not calibrated: 0.05 is the smallest difference this instrument has been asked to distinguish, the bar the withdrawn M2 used, so a dense-end loss larger than it voids adoption

The adoption criterion is a conjunction, judged whole: the mean gain at the sparsest
density at cap 20 must clear the bar, its 95% interval's lower bound must
clear zero, and at least 7 of 8 seeds must move the same way. Any one of the
three failing means the gain does not reproduce.

## 5. Decision table

| Condition | Verdict | Reading |
| --- | --- | --- |
| all gates pass; adoption passes; guard passes | **ADOPT THE ADMISSION RULE** | the rule reproduces its gain on fresh seeds without a dense-end loss; the cognition change is recorded separately |
| all gates pass; adoption passes; guard fails | **PRICE THE TRADE** | the rule gains where the world is sparse and loses where it is dense; nothing is adopted until the trade is priced |
| all gates pass; adoption fails; interval width at or below 0.30 | **CLOSE ORDERING** | the gain does not reproduce; ordering is closed at this cap and world family and no admission variant follows |
| all gates pass; adoption fails; interval width above 0.30 | **UNDERPOWERED** | the interval cannot place the level; closing the line would read a draw as an absence |
| a gate fails | **VOID** | reported as the gate, never as a verdict |

A gate failure is **VOID**, reported as the gate and never as a verdict. The dense-end guard
is not a second criterion: it can only prevent adoption, and a failure routes the result to
a priced trade rather than to a negated adoption.

## 6. Gates

* **G0 liveness** — at the sparsest density, at both caps, the two arms' selected sets must differ on every seed, or the manipulation did not occur
* **G1 presence ceiling** — the world's edges must be present in memory in every cell, or the cell tests memory rather than ranking
* **G2 arithmetic consistency** — covered cannot exceed asserted, and coverage must equal covered over the world's edges
* **G3 axis live** — rho_rank must rise from the sparsest to the densest density at each cap
* **G4 control reproduces Gate 13** — the control's coverage at the sparsest density must not exceed the recorded ceiling
* **G5 identity at density 1** — at density 1 the two arms must select identical rows and Delta must be zero

**Void rule.** a failed gate voids the block and no criterion is read; a gate cannot be reported as a verdict, and a cell set that is not the pre-registered grid is refused rather than scored

## 7. Analysis path

./.venv/bin/python -m benchmarks.score_ranking_admission --results docs/ranking_admission_run.json --out docs/ranking_admission_result.json

The analysis path is `benchmarks/score_ranking_admission.py`, frozen with this registration. It reads only the cells
the runner writes, imports nothing from the engine, and refuses a cell set that is not the
pre-registered grid. Its input is `docs/ranking_admission_run.json`.

## 8. Allocation

8 world seeds, 1 bootstrap seed, 160 cells,
2 thresholds and 2 bars. two thresholds are declared: the adoption bar and the dense-end guard. Both are fixed here, before any cell, and neither may be recomputed on the block it judges

No cell may run before this file is committed.

## 9. Result (post-freeze)

The block ran on 160 cells and the frozen analysis path returned **ADOPT THE ADMISSION RULE**.

- **Adoption:** mean gain +0.171875 at the sparsest density, 95% interval
  [+0.135417, +0.213542], width 0.078125, 8 of 8 seeds positive,
  bar 0.08 — passed.
- **Guard:** mean gain +0.026042 at the densest density against -0.05 —
  passed.
- **Gates:** no gate failed.
- **Coverage gap by density:** 0.1 -> +0.171875; 0.2 -> +0.130208; 0.4 -> +0.059896; 0.6 -> +0.030382; 0.8 -> +0.026042.

Cells are in `docs/ranking_admission_run.json`; the decision is in
`docs/ranking_admission_result.json`. The adoption this verdict licenses is a cognition
change, so it is recorded as an owner decision in the manual and is not applied to the
engine by this document.
