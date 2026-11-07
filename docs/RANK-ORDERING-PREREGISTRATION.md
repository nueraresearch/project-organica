# The ranking experiment, frozen before any cell (2026-11-07)

**Status: FROZEN, NOT RUN.** No cell has been executed, no world generated, no engine cycle
spent, and no result artifact exists. The criteria, gates, bar and allocation below were
committed before the run; nothing here may be changed afterwards. A defect found later is
disclosed as an amendment, and the pre-registered reading stands unless the amendment says
plainly that it withdraws it.

The hypothesis is in `docs/NONFREQUENCY-RANKING-DESIGN.md`; this file is the test of it. The
numbers are in `docs/rank_ordering_prereg.json`, and this document is rendered from that
artifact by `benchmarks/write_rank_ordering_prereg.py`.

## 1. Question

Does ordering eligible candidates by **source diversity**, rather than by count, recover more
of a sparse world's edges at the engine's own cap? The design record varies the ordering at
fixed eligibility; the density record varies eligibility at fixed ordering. Neither subsumes
the other, and this block tests the first.

## 2. Design

- **Arms:** `control` (**global count-ranked top-k**) and `diversity` (**diversity-first ordering**).
- **Caps:** 20 and 40.
- **World family:** 16 tags, the Gate 13 world family; |P_world| = 240 directed non-self pairs, so |P_world| = 240 directed non-self pairs.
- **Densities:** 0.1, 0.2, 0.4, 0.6, 0.8, i.e. 24, 48, 96, 144, 192 true edges.
- **Eligibility:** every candidate row, including intra-cell co-occurrence rows; the density record varies eligibility and this one does not.
- **Exposure:** fixed total exposure, the density record's primary scheme; the sensitivity scheme is not run and is not a licence to add cells.
- **Horizon:** one horizon, identical in both arms at each density.
- **Cells:** 160 (2 arms x 2 caps x 5 densities x 8 seeds = 160).

Coverage is |asserted and W| / |W|; precision is |asserted and W| / |asserted|, always
reported beside rho_rank; the presence ceiling is |W available in memory| / |W|.

## 3. Seeds

World seeds **20310201-20310208**, eight of them, plus bootstrap seed **20310209** for the analysis interval.
the first contiguous window of nine numbers at or after 20310201 that appears in no file under docs, tests, benchmarks, research-journal or papers; the bootstrap seed is the ninth and is not a world seed. The block is the ninth number of the same window, and it is not a world seed.

recording this block makes it consumed for the corpus seed scan, which is the intended effect: a declared block is registered rather than left free to be reallocated.

## 4. Gates — comparability, not success

| Gate | Requirement |
| --- | --- |
| G0 liveness | at rho_world = 0.1, at each cap, the two arms' selected sets differ on at least 7 of the 8 seeds |
| G1 presence | the world's edges present in memory over the world's edges equals 1.0 in every cell |
| G2 arithmetic | every cell's covered and asserted counts reconcile with its coverage and precision, coverage and precision lie in [0, 1], and precision is reported beside rho_rank rather than gated on it |
| G3 axis live | mean rho_rank at rho_world = 0.8 exceeds mean rho_rank at rho_world = 0.1, at each cap |
| G4 control reproduces | mean control coverage at cap 20 and rho_world = 0.1 does not exceed 0.15 |
| G5 identity at density 1 | a harness self-test on a synthetic population where every candidate is a true edge selects identical sets in both arms and returns exactly zero delta; it spends no engine cell |

any gate failure voids the block and is reported as the gate; no criterion is read. The control ceiling in G4 is **0.15**: if the count ordering already covers the world at
the sparsest level, the world or the cap is wrong and no delta can be read.

**A gate was amended before any cell ran.** the original gate was unsatisfiable for any informative ranker: rho_rank is the base rate of the population, so a rule that selects better than chance necessarily reports precision above it. As written, G2 would have voided exactly the result the block exists to detect. Amended before any cell ran.

## 5. Criteria

**M1 — the level.** mean Delta at cap 20 and rho_world = 0.1, where Delta = diversity coverage - control coverage per seed, is at least the bar and its 95% bootstrap interval's lower bound is above zero. The bar is **0.15**.

The bar's provenance, fixed before any cell: declared before any cell, not computed from a run: 0.15 of the world's 24 edges at the sparsest level is at least a sixth of the world recovered beyond control, and the control's sampling expectation at that density is 20 x 0.1 / 24, about 0.083 It is not recomputed from the run it judges,
and a later block may not inherit it as a convention.

**M2 — the gradient.** the precision gap, diversity minus control at cap 20, must be larger at rho_world = 0.1 than at rho_world = 0.8: a positive mean difference in differences of at least 0.05, a 95% interval lower bound above zero, and a wider gap at the sparser level on at least 7 of the 8 seeds.

The interval is a **95%** percentile bootstrap over seeds, paired within seed, **4000**
replicates.

## 6. Decision table

| M1 | M2 | Verdict | Reading |
| --- | --- | --- | --- |
| pass | pass | **ORDERING SUPPORTED** | the ordering basis is the lever: replace the count order with a diversity-based order in the next engine version, recorded as a cognition change |
| pass | fail | **ORDERING HELPS, GRADIENT ABSENT** | a level difference without the predicted interaction; no engine change follows |
| fail | pass | **GRADIENT WITHOUT LEVEL** | an interaction without a level the bar accepts; no engine change follows |
| fail | fail | **ORDERING NOT THE LEVER** | ordering is closed; the line moves to the candidate space, and no second ordering variant is run |
| fail, interval wider than 0.30 | either | **UNDERPOWERED** | the interval cannot place the level; closing the line would read a draw as an absence |

A gate failure is **VOID**, reported as the gate and never as a verdict. A negative pole is
licensed **only** by a decisive M1 failure: if M1 fails and its interval is wider than 0.30, the block is reported as underpowered and no line is closed; a wide interval is not a negative result.

## 7. Analysis code path

`benchmarks/score_rank_ordering.py`, frozen with this file and importing nothing from
`organica`. It reads `docs/rank_ordering_run.json` and writes
`docs/rank_ordering_result.json`:

```
./.venv/bin/python -m benchmarks.score_rank_ordering --results docs/rank_ordering_run.json --out docs/rank_ordering_result.json
```

It refuses a cell set that is not exactly the pre-registered grid, a duplicate cell, and a
result with no identity self-test. It computes the gates first; if any gate fails it reports
the gate and reads no criterion. The bootstrap seed comes from the artifact, so the interval
is deterministic given the cells.

The runner, `benchmarks/run_rank_ordering.py`, is built and passes its self-tests: the G5
identity check on an all-true population, a generator audit of the density ladder, and an
arm-liveness check that the two orderings differ at the sparsest density. `--run` refuses a
pre-registration that is not frozen, a seed block that is not contiguous, and an existing output
file without `--force`. No cell may run before this file is committed.

## 8. Allocation

**9** seeds (of which **8** are world seeds), **160** cells, **0** thresholds, **1** bar.
The bar is declared here and never computed from the outcome.

## 9. What this block cannot say

- A pass is support within **one** world family, **two** caps and **eight** seeds. It is not a
  general claim that diversity ordering works, and it does not generalise to other families.
- A null is about this cap and this world family. It does not show that ordering is irrelevant
  anywhere else.
- Coverage is not behavior. Nothing here measures whether a belief predicts anything.
- The identity check at density 1 spends **no** engine cell: it is a harness self-test on a
  synthetic population, and it validates the arms, not the world.
- It does not touch the bottleneck map. That artifact keeps exactly one specified experiment,
  the density interaction, and a test asserts it.
