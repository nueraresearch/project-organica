# Formation vs. utilization — campaign result

**Run:** 2026-10-30, artifact generated 2026-10-31T02:09:33.631084+00:00.  
**Design:** the protocol committed at `8536d9a`; Amendment 1 (§12) was appended on 2026-10-30, before any confirmatory seed.  
**Artifact:** [`docs/formation_utilization.json`](formation_utilization.json) — 60 units, 30 seeds × 2 tasks.  
**Status:** complete — 60 of 60 units `campaign_ready`, 0 failing audits, 60 not-applicable audit instances.

---

## 1. The pre-committed verdict

> **Both formed arms lose transfer on both tasks → *"utilization fails even with correct structure"* → V2 targets the use path (retrieval / activation / readout). Summary claim: not supported.**

The §7 mapping returns exactly one cell per task, and both tasks return the same cell:

| Task | B transfer | C transfer | Mapping | Target | Summary claim |
|---|---|---|---|---|---|
| T1 | loss (d = -0.0296) | loss (d = -0.0262) | utilization fails with correct structure | the use path (retrieval / activation / readout) | not supported |
| T2 | loss (d = -0.0795) | loss (d = -0.0227) | utilization fails with correct structure | the use path (retrieval / activation / readout) | not supported |

The failing limbs, named: **transfer and retention**. C loses retention on both tasks (T1 d = -0.0267; T2 d = -0.0230). Revision is **not** a failing limb: C wins it on T1 (d = +0.1002) and ties it on T2 (d = +0.0007). A summary claim requires C to win or tie transfer and not lose retention or revision; C loses both transfer and retention, so the claim fails on two independent grounds.

## 2. Every cell

This table is the artifact's `analysis` block. **d = bar − arm**: a positive d favours the arm, so a loss is a negative d. Intervals are 98.33 % percentile bootstraps over 10,000 replicates, paired by seed (n = 30); the bar is the best comparator on the calibration seed, per limb.

**Notation note.** §7 writes `d = score(arm) − score(best baseline)` and then states the win rule as a lower bound above zero. Those two sentences use opposite orientations, because lower log loss is better. The artifact and this document use the orientation the win rule requires — `d = bar − arm`, positive favours the arm — as the harness's `paired_bootstrap` docstring states. The discrepancy is in the protocol's notation, not in the analysis: the intervals and verdicts in the artifact are computed on the oriented difference. No criterion, interval or verdict changes.

| Arm | Limb | d | 98.33% interval | Verdict |
|---|---|---|---|---|
| T1 / A | retention | -0.0768 | [-0.0827, -0.0707] | loss |
| T1 / A | transfer | -0.0752 | [-0.0809, -0.0692] | loss |
| T1 / A | revision | +0.0292 | [+0.0239, +0.0342] | win |
| T1 / B | retention | -0.0302 | [-0.0320, -0.0283] | loss |
| T1 / B | transfer | -0.0296 | [-0.0312, -0.0281] | loss |
| T1 / B | revision | +0.0877 | [+0.0830, +0.0922] | win |
| T1 / C | retention | -0.0267 | [-0.0284, -0.0249] | loss |
| T1 / C | transfer | -0.0262 | [-0.0275, -0.0249] | loss |
| T1 / C | revision | +0.1002 | [+0.0956, +0.1047] | win |
| T2 / A | retention | -0.1126 | [-0.1149, -0.1101] | loss |
| T2 / A | transfer | -0.1132 | [-0.1154, -0.1107] | loss |
| T2 / A | revision | -0.1130 | [-0.1159, -0.1096] | loss |
| T2 / B | retention | -0.0797 | [-0.0814, -0.0778] | loss |
| T2 / B | transfer | -0.0795 | [-0.0811, -0.0778] | loss |
| T2 / B | revision | -0.0676 | [-0.0694, -0.0657] | loss |
| T2 / C | retention | -0.0230 | [-0.0246, -0.0213] | loss |
| T2 / C | transfer | -0.0227 | [-0.0242, -0.0211] | loss |
| T2 / C | revision | +0.0007 | [-0.0012, +0.0026] | tie |

A is the cap-20 arm that failed Gate 13 on the compositional task; here it loses five of six task-limbs, the T1 revision win being the exception. B, the cap-1,000 formation arm, also loses five of six (a T1 revision win; all three T2 limbs). C, the oracle-admitted arm, loses four of six — T1 retention and transfer, T2 retention and transfer — wins T1 revision, and ties T2 revision.

## 3. Absolute levels, and how much of the gap C closes

**T1** (bar: Replay on retention, Replay on transfer, Replay on revision)

| Learner | Retention | Transfer | Revision |
|---|---|---|---|
| A (cap 20) | 0.2866 | 0.2845 | 0.4602 |
| B (cap 1,000) | 0.2400 | 0.2389 | 0.4017 |
| C (cap 1,000 + support) | 0.2365 | 0.2355 | 0.3892 |
| Replay (bar) | 0.2099 | 0.2093 | 0.4893 |
| Bigram | 0.2381 | 0.2376 | 0.5279 |
| Cell counter | 0.2352 | 0.2345 | 0.5173 |

**T2** (bar: Cell counter on retention, Cell counter on transfer, Cell counter on revision)

| Learner | Retention | Transfer | Revision |
|---|---|---|---|
| A (cap 20) | 0.4539 | 0.4537 | 0.4639 |
| B (cap 1,000) | 0.4209 | 0.4200 | 0.4185 |
| C (cap 1,000 + support) | 0.3643 | 0.3632 | 0.3502 |
| Replay | 0.3434 | 0.3424 | 0.3525 |
| Bigram | 0.3455 | 0.3445 | 0.3544 |
| Cell counter (bar) | 0.3413 | 0.3405 | 0.3509 |

Closure is `(A − C) / (A − bar)` on the limbs where the bar is better than A. C closes **65.2 %** of A's retention gap and **65.2 %** of its transfer gap on T1, and **79.6 % / 79.9 %** on T2, leaving residuals of 0.0267 / 0.0262 nats on T1 and 0.0230 / 0.0227 nats on T2.

C versus B, the formation arm it is meant to improve on: 0.0034 nats better on T1 transfer and 0.0568 better on T2 transfer. Correct structure is worth a great deal; it is not worth the last 0.0227–0.0267 nats.

On T1 revision the bar is worse than A (Replay 0.4893 against A's 0.4602), so a closure fraction is not defined there; C's +0.1002 win is against a comparator that cannot revise. On T2 the bar is at 0.3509 and C at 0.3502 — a tie, not a win.

## 4. Audits

On every unit, every audit is either a pass or not applicable. The two not-applicable audits are design-scoped and were recorded before the campaign: A3's 0.3443 precision band was measured on T2, and A6's size-matched wrong filter does not exist on T1.

| Audit | T1 | T2 |
|---|---|---|
| A1 arm differential | A 0.1553–0.2549, B/C 0.8812–0.9935 | A 0.0000–0.0625, B/C 0.9643–1.0000 |
| A2 oracle exactness | 612,005 permitted candidates over 160 cycles/unit, 0 mismatches, cap never bound | 473,351 over 121–160 cycles/unit, 0 mismatches, cap never bound |
| A3 precision premise | not gated (B precision 0.4549–0.5217, C admission 1.0) | B 0.3182–0.3394 ≤ 0.3543; C admission 1.0 |
| A4 denominators | 319 / 399 / 399 events, 0 excluded | 319 / 399 / 399 events, 0 excluded |
| A5 readout construct | 30/30 pass | 30/30 pass |
| A6 no leakage | not applicable (the shuffled filter retains 52.9 % of permitted pairs and cannot be size-matched) | shuffled 0.4957–0.5052 vs C 0.3569–0.3726; Layer-1 coverage 0.0 |
| A7 attribution share | 96.2–97.7 % from Layer 1 | 94.0–96.2 % |
| A8 temporal input | 2,408,224 eligible-pair checks, 0 mismatches, own-table symmetric difference 0–19 edges (unread) | 2,539,326 checks, 0 mismatches, 17–93 edges (unread) |

A2's denominator is the permitted candidate stream the arm was actually given, recorded before the filter. A8 checks the graph and that stream against arm B's at every cycle; the engine's own `precedes` tables still differ because C's own sleep rows are still written, but Layer 1 does not read them. That difference is reported as a footnote, not hidden.

## 5. What the verdict does and does not mean

**What it does mean.** With the generator's support admitted at Layer 1 — and 94.0–97.7 % of C's readout edge weight on that layer across the two tasks — correct structure is not sufficient to clear the strongest simple baseline on retention or transfer in this design. C's loss is not a candidate-selection loss: it was given the support. The mapping therefore names the use path, not selection or precision, as the V2 target.

**What it does not mean.**

- It is not *"the engine cannot use structure"*. C improves transfer over A by 0.0490 nats on T1 and 0.0905 on T2, closes 65–80 % of A's gap, and wins T1 revision by +0.1002. The label means *does not clear the bar*, not *no use*.
- It is not *"the oracle arm failed to transfer"*. C transfers and scores better than both closed-loop Organica arms; it loses the comparison to the bar. The verdict is about the comparison, not about whether any transfer happened.
- It is not a discovery result. C is given the generator's support; B is the discovery arm, and B also loses transfer on both tasks.
- It is not a self-sourcing result. B's temporal graph still contains B's own sleep rows, and C inherits that graph under Amendment 1. Nothing here attributes anything to self-sourced support.
- It is not *"the engine with this filter installed"*. C is a counterfactual trajectory on B's temporal evidence: a C result is admission filtering at fixed evidence.
- It does not localize the defect inside the use path. It names the path — retrieval, activation, readout — not which of them is binding.
- It does not generalize beyond T1 and T2, and it does not authorise a V2 build.

## 6. The bar's name: "data-only" is too wide

The protocol's question and §12.5 call the comparator *"the strongest data-only learner"*. On T2 the bar is the **cell-level latent-state counter**, which is **granted the latent cell structure**: `fit_cell_counter` takes `tag_to_cell` from the generator, and its docstring says the structure is *"here granted"*. It is not a data-only learner, and the phrase should not be used for this bar. The counter is nevertheless a declared member of the statistical-learner family (acquisition protocol §6.3), so this is a naming defect, not a deviation from the committed comparator set.

The verdict does not depend on it. Post hoc, not a criterion:

| Task | Comparator | Limb | d | 98.33% interval | Verdict |
|---|---|---|---|---|---|
| T1 | replay | retention | -0.0267 | [-0.0284, -0.0249] | loss |
| T1 | replay | transfer | -0.0262 | [-0.0275, -0.0249] | loss |
| T1 | bigram | retention | +0.0015 | [-0.0005, +0.0037] | tie |
| T1 | bigram | transfer | +0.0021 | [+0.0003, +0.0037] | win |
| T2 | replay | retention | -0.0209 | [-0.0224, -0.0193] | loss |
| T2 | replay | transfer | -0.0208 | [-0.0224, -0.0192] | loss |
| T2 | bigram | retention | -0.0187 | [-0.0206, -0.0169] | loss |
| T2 | bigram | transfer | -0.0187 | [-0.0205, -0.0168] | loss |

On T1 the bar is already Replay, a data-only episodic learner, and C loses transfer to it by 0.0262 nats. On T2 C also loses to Replay by 0.0208 and to the bigram by 0.0187, so the verdict survives dropping the oracle-informed counter. The counter is also not a stronger oracle than C: C is given the generator's full transition support, while the counter is given the four-cell latent map. The loss is not explained by the baseline having a better oracle.

## 7. Provenance and reproduction

- **Seeds and units:** 20261101–20261130, two tasks, 60 task-seed units; four arms (A, B, C, S) and three comparator fits per unit.
- **Engine:** 0.10.0; no engine file changed (`tests/test_v1_freeze.py`).
- **Cost:** the artifact's per-unit timings sum to 12.72 worker-hours across the 240 arm runs and the 180 comparator fits. Mean per-arm times under contention (the shuffled arm S is the fourth): T1 A/B/C 205/225/217 s; T2 157/173/172 s. The isolated timing pass measured 72.2 s per run.
- **Execution:** `python .scratch/run_campaign_resumable.py --seeds 30 --workers 10`, a resumable wrapper over the harness's own `run_task_seed`; each unit was checkpointed, no unit failed or was re-run, and the artifact was assembled with the harness's own `analyse()` and renderer.
- **Provenance correction:** the artifact was re-assembled from the same units at 2026-10-31T02:20:59.593005+00:00 to correct the `command` field; `status`, `results`, `audits` and `analysis` are identical to the first assembly.
- **Re-render:** `python benchmarks/formation_utilization_results.py`. `tests/test_formation_utilization_results.py` compares this document with the artifact and can fail.

**See also:** protocol §7 and §12; [`docs/USER-MANUAL.md`](USER-MANUAL.md) §8.20–§8.21, finding 39; [`docs/formation_utilization.md`](formation_utilization.md) (the artifact's own table); journal §65; AGENTS rule 24.

