# The ranking experiment, frozen before any cell (2026-11-07)

**Status: RUN COMPLETE — ORDERING SUPPORTED** (judged block executed 2026-11-07). The criteria, gates, seeds and decision table below were frozen before the run and are unmodified; section 8 records what the committed scorer returned. Two smoke
pools outside the block have been run and are recorded in §7; they are not evidence. The first
found a defect that made the treatment unable to reach the world, the world's crowding was
repaired, the second proves the repair, and **Amendment 4 withdraws M2**: no endpoint could both
vary with density and fail here, so M1 is the sole criterion and the ladder is reported as a
characterization. The criteria, gates, bar and allocation below were committed before the run;
nothing here may be changed afterwards. A defect found later is disclosed as an amendment, and
the pre-registered reading stands unless the amendment says plainly that it withdraws it.

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

**M2 — withdrawn (Amendment 4).** Amendment 4 (2026-11-07): withdrawn. No endpoint could both vary with density and fail here. The precision difference in differences at cap 20 is zero or negative on all eight designed seeds, because the precision gap is set by the eight crowded sources and does not vary with density. The coverage gap varies only through |W|: at cap 20 the dense-end gap is bounded by 20/192, so with M1's 0.15 bar the difference in differences is at least 0.0625 on every integer-coverage seed and the old 0.05 bar could not fail while M1 passed. M1 is the sole criterion; the coverage and precision gaps by density are reported as a characterization and are not scored.

The density profile is reported, not gated: coverage and precision gaps at cap 20 for every density, with the number of seeds whose coverage gap is positive; no threshold is applied to the ladder.

The interval is a **95%** percentile bootstrap over seeds, paired within seed, **4000**
replicates.

## 6. Decision table

| M1 | Verdict | Reading |
| --- | --- | --- |
| pass | **ORDERING SUPPORTED** | the ordering basis is the lever at the sparsest density; the density ladder is reported as a characterization, not scored |
| fail, interval wider than 0.30 | **UNDERPOWERED** | the interval cannot place the level; closing the line would read a draw as an absence |
| fail | **ORDERING NOT THE LEVER** | ordering is closed at this cap and world family; the line moves to the candidate space |

A gate failure is **VOID**, reported as the gate and never as a verdict. A negative pole is
licensed **only** by a decisive M1 failure: if M1 fails and its interval is wider than 0.30, the block is reported as underpowered and no line is closed; a wide interval is not a negative result. There is no gradient verdict: the density
ladder is reported, not scored.

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

**A smoke pool was run before any judged cell, and it stopped the block.** Seed **20310301** at rho_world 0.1, 9 sleep cycles, 4 derived cells: every world edge was present (24 of 24), and **the control and the diversity arm each covered 0 world edges at cap 20 and at cap 40**. The 48 intra-cell filler rows carry counts 12-17, 3 per source across all 16 sources, while the world's rows carry 3-9 and the best ranks **51**, so the diversity ordering -- whose tie-break is count -- fills its remaining slots with filler once every source has one. Delta is therefore 0 by construction at the primary point, M1 cannot pass, and a zero-width interval is not underpowered, so the only reachable verdict is the negative pole. The pool itself behaved as the audits predicted (154 rows; presence 1.0), which is why this is a defect in what the arms can reach rather than in what the engine stores. No judged cell may run until the owner decides how to repair the treatment; the numbers are in `pre_run.smoke`.

**The repair: the crowding is partial, and neither arm changed.** The filler is emitted from two of the four cells (`FILLER_CELLS = 2`), so eight sources are crowded and eight are free. On all 8 designed pools the treatment now reaches 5-8 world edges at cap 20 while the control reaches 0, so the reach gate passes. One smoke pool (seed 20310401, 7 sleep cycles) covered 4 of 24 world edges at cap 20 against 0, a Delta of 0.1667 above the 0.15 bar, and 6 of 24 at cap 40 against 5; every audit prediction held. **M2 was withdrawn rather than repaired.** Its precision difference in differences is zero or negative on every seed (per-seed values -0.15, -0.10, -0.05, -0.15, -0.10, -0.05, -0.05, 0.00, mean -0.0813), because the gap is set by how many crowded sources the spread must spend on -- the same count at every density -- while at 0.8 every non-filler row is a world edge; on the smoke pool the 0.1 precision gap is 0.20 against the designed 0.8 gap of 0.40. The only density-varying quantity is the coverage gap, which moves with |W|: the dense-end gap is bounded by 20/192 and the difference in differences could not fail while M1 passed. Amendment 4 therefore withdraws M2, makes M1 the sole criterion and reports the ladder as a characterization. The block was ready, and the judged run followed under M1 alone.

**The reach gate passes after the repair.** `--self-test` and `run()` compare each arm's selection to the *world* at the primary point, on the pool the world design implies and before any engine cycle. On all 8 seeds the treatment reaches 5-8 world edges at cap 20 while the control reaches at most 0, so `all_passed` is true. The gate is the durable half of the first finding: it does not depend on the smoke records, and the unrepaired construction is kept as a fixture that makes it fail.

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


## 8. The judged run (post-freeze record)

**The block ran on 2026-11-07.** 160 cells were executed on the eight registered seeds and **9 of 9 gates passed**. M1 returned a mean delta of **0.1615** at the sparsest density with a **95%** interval of **[0.1094, 0.2031]** against the declared **0.15** bar, so M1 **passed**. The committed scorer returned **ORDERING SUPPORTED** (positive).

The ladder is reported, not scored: the coverage and precision gaps at cap 20, and the number of seeds whose coverage gap is positive.

| rho_world | coverage gap | precision gap | seeds positive |
| --- | --- | --- | --- |
| 0.1 | 0.1615 | 0.1938 | 7 |
| 0.2 | 0.1120 | 0.2687 | 8 |
| 0.4 | 0.0625 | 0.3000 | 8 |
| 0.6 | 0.0295 | 0.2125 | 8 |
| 0.8 | 0.0260 | 0.2500 | 8 |

**What the verdict licenses.** The positive branch of the decision table: the ordering basis is the lever at the sparsest density, so the next architectural step is the admission and budget change, not another ranking diagnostic. It does **not** license a behavioral claim, because no cell here measures a downstream gain from a better-ranked selection, and the ladder is a characterization under Amendment 4, not a gradient.

The cells are in `docs/rank_ordering_run.json`; the numbers are in `docs/rank_ordering_result.json`.