# Formation versus utilization — one-seed timing pass

**Generated:** 2026-10-31T00:30:24.817939+00:00  
**Engine:** Organica 0.10.0  
**Command:** `python benchmarks/formation_utilization.py --timing --tasks T2 && python benchmarks/formation_utilization.py --timing --tasks T1`  
**Status:** timing pass only — one exploratory seed (`20261100`). No campaign result, no win/tie/loss, no verdict.  
**Campaign readiness:** READY. All eight audits pass or are not applicable, and the admission arms read arm B's temporal graph at every cycle

This artifact exists to report the measured cost of the pre-registered campaign before it starts, and to record that the eight audits behave. It is not `docs/formation_utilization.json`; only a full campaign may write that. Arms C and S read arm B's per-cycle temporal graph (Amendment 1, protocol §12); A and B are unchanged.

## 1. Measured cost

| Task | Arm | Cap | Admission | Acquisition (s) | Revision learn (s) | Scoring (s) | Total (s) |
|---|---|---|---|---|---|---|---|
| T2 | A | 20 | none | 38.2 | 23.7 | 0.3 | 62.2 |
| T2 | B | 1000 | none | 42.0 | 29.3 | 0.3 | 71.5 |
| T2 | C | 1000 | support | 39.4 | 26.5 | 0.3 | 66.1 |
| T2 | S | 1000 | shuffled | 37.6 | 25.8 | 0.3 | 63.7 |
| T1 | A | 20 | none | 46.4 | 21.9 | 0.3 | 68.6 |
| T1 | B | 1000 | none | 54.1 | 30.4 | 0.3 | 84.7 |
| T1 | C | 1000 | support | 55.4 | 27.2 | 0.3 | 82.9 |
| T1 | S | 1000 | shuffled | 50.8 | 26.8 | 0.3 | 77.9 |

Mean engine run: **72.2 s** over 8 measured runs. Arm C's filter adds no measurable cost (the filter is a set membership test over at most a few hundred candidate pairs per cycle).

- Campaign arms (A, B, C × 2 tasks × 30 seeds = 180 runs): **3.6 h** sequential.
- A6's shuffled arm (2 tasks × 30 seeds = 60 runs): **1.2 h** sequential.
- Comparators (2 tasks × 30 seeds = 60 fits): **0.01 h** sequential.
- **Total sequential: 4.8 h.** Each task-seed unit is independent, so `--workers` divides this without changing any per-run measurement.

The projection is arithmetic on the measured runs, not a second measurement. It excludes A2's recording, which is in-memory and was on for every run above.

## 2. The audits

| Audit | T2 | T1 | Evidence (T2) |
|---|---|---|---|
| A1 arm differential | PASS | PASS | arms differ as specified: A 0.0000 < 0.50 <= B 1.0000, C 1.0000 |
| A2 oracle exactness | PASS | PASS | 14455 permitted candidates across 131 cycles admitted exactly; the cap never bound after filtering |
| A3 precision premise | PASS | not applicable | B Layer-1 precision 0.3373 <= 0.3543; C's admission precision is 1.0 |
| A4 denominators | PASS | PASS | every limb has a non-zero denominator |
| A5 readout matches construct | PASS | PASS | the readout recovers the known answer and can be wrong |
| A6 no leakage | PASS | not applicable | shuffling collapsed Layer-1 coverage to 0.0000 and Layer-1 precision to 0.0; transfer 0.5007 vs C's 0.3661 |
| A7 attribution share | PASS | PASS | Layer 1 carries 0.9502 of the readout's edge weight (hypotheses 0.0048); threshold 0.50 |
| A8 temporal input invariance | PASS | PASS | B and the admission arms read the same temporal graph at every cycle (131 cycles per arm, 75488 eligible-pair checks); evidence identical on the shared pairs. The engine's own precedes tables still differ by 28 edge(s); Layer 1 no longer reads them. |

No audit failed. A6 is marked not applicable where the shuffled filter necessarily retains permitted pairs; the retained share is in its evidence. A6 is gated on the primary task T2, where the shuffle retains none.

## 3. Audit A8 — temporal input invariance (gate)

- **T2:** PASS. B and the admission arms read the same temporal graph at every cycle (131 cycles per arm, 75488 eligible-pair checks); evidence identical on the shared pairs. The engine's own precedes tables still differ by 28 edge(s); Layer 1 no longer reads them.
- **T1:** PASS. B and the admission arms read the same temporal graph at every cycle (160 cycles per arm, 80200 eligible-pair checks); evidence identical on the shared pairs. The engine's own precedes tables still differ by 15 edge(s); Layer 1 no longer reads them.

A8 checks the graph each admission arm actually read and the eligible pair stream it built from that graph, every cycle. It is a gate, and it replaces the pre-amendment diagnostic D1, whose measurement is preserved at `docs/formation_utilization_timing_pre_amendment.json`. The engine's own `precedes` tables still differ — C's own sleep rows are still recorded — but Layer 1 no longer reads them.

## 4. Scores (descriptive — not a result)

| Task | Arm | Retention | Transfer | Revision |
|---|---|---|---|---|
| T2 | A | 0.4530 | 0.4539 | 0.4634 |
| T2 | B | 0.4244 | 0.4254 | 0.4212 |
| T2 | C | 0.3656 | 0.3661 | 0.3490 |
| T2 | S | 0.5002 | 0.5007 | 0.5293 |
| T2 | bar | 0.3473 | 0.3507 | 0.3522 |
| T1 | A | 0.2826 | 0.2820 | 0.4598 |
| T1 | B | 0.2370 | 0.2359 | 0.4014 |
| T1 | C | 0.2350 | 0.2346 | 0.3890 |
| T1 | S | 0.3008 | 0.2921 | 0.4548 |
| T1 | bar | 0.2066 | 0.2117 | 0.4679 |

**Where the oracle arm sits.** On this seed arm C is the best Organica arm on every limb, and it clears the bar on 2 of 6 task-limbs (T2 revision, T1 revision). Its difference from the bar on the primary transfer limb (positive = worse) is +0.0154 nats on T2 and +0.0229 nats on T1. One seed is not a verdict and these numbers may not be quoted as a loss; they are recorded because an oracle-admitted arm that does not clear a counting baseline on its own timing seed is a warning the campaign should carry.

The bar row names the comparator selected per limb on the calibration seed. One seed cannot produce a verdict: the decision rule needs a paired bootstrap over seeds, and `analyse()` refuses to run below two. Nothing in this table may be quoted as a win, a loss or a tie.

A1's coverage is the Gate 13 quantity over the world edges derived from the training stream, on the all-structure basis the gate pins. A3's precision is the Layer-1 quantity on which the 0.3443 ceiling was measured. Arm C's all-structure readout precision is reported in the artifact and is not 1.0, because the readout still aggregates all six structure types; only its Layer-1 admission is exact.

## 5. Disclosures

**A6 wording superseded.** The committed audit asked that shuffling the oracle make C "collapse to B's coverage". B's coverage is 98–100 %, so no shuffle can produce that value: the direction is impossible. A6 is implemented as shuffled precision in B's measured band, shuffled coverage under A1's own 0.50 gate, and the shuffled transfer score not matching C's. The thresholds are the protocol's own; none was relaxed.

**three limbs, not four.** §3.4 says four scored windows; §4.4 lists revision 200–249 and a held-out 250–299; the pinned runner scores three limbs. Three is what §7's Bonferroni-over-three assumes. This harness scores retention 110–149, transfer 150–199 and revision 250–299, and treats 200–249 as the learning window it is.

**T1's regime switch.** The T1 generator defaults to a law change at cycle 150, which would put the change inside the transfer window §4.4 says is under the old law. The harness generates T1 with a switch at 200 and verifies the recorded regime at the boundary. The module default and §4.4 disagree.

**A6 on T1 is not a control.** T1's support covers 12 of 16 targets per source, so a size-matched wrong filter necessarily retains permitted pairs (the retained share is printed). A6 is therefore gated on the primary task T2 and reported as not applicable on T1. A control that cannot discriminate is not a passed control.

**bar selection.** The comparators' configurations are frozen from the calibration artifact; only WHICH comparator is the bar per limb is chosen, on seed 20261099. Three comparators are fitted (replay, bigram, cell counter) rather than the protocol's two, which can only raise the bar.

**A2's scope.** A2 is the committed audit on the arm's own stream: admitted = count-threshold-eligible pairs intersected with the support. A stronger C-versus-B comparison was implemented first and failed; it was reported as diagnostic D1 before Amendment 1 and is now audit A8, which gates the run. The comparison is retained because it measures whether the admission arms read the same evidence, which is the condition the amendment exists to establish.

**amendment 1 — fixed temporal evidence.** The pre-amendment timing pass measured that an admission filter changed the next cycle's temporal graph: the engine's lookback window is the last three rows of `events`, and sleep rows are rows. Arms C and S now read arm B's per-cycle graph, recorded at the start of each sleep cycle, instead of their own; A and B are unchanged. This closes the feedback path into Layer 1 but does not make the engine sleep-blind: B's graph still contains B's own sleep rows, and C's own payload and prior still differ (that is the treatment). C is therefore a counterfactual trajectory on B's evidence, and a C result is admission filtering at fixed temporal evidence, not 'the engine with this filter installed'. See protocol §12 and the preserved pre-amendment artifact.

**A3's band is T2's.** The 0.3443 precision ceiling was measured on the compositional world. A3 applies it on T2 and reports T1's precision without gating, because T1 has no committed band. Applying a T2 constant to T1 would measure the wrong population.

**orientation of the decision difference.** §7 writes d = score(arm) − score(baseline) and calls a positive lower bound a win. With log-loss, lower is better, so the orientation that makes the rule coherent is d = baseline log-loss − arm log-loss. That is the quantity bootstrapped, and it is named in every artifact.

## 6. Provenance

- Artifact: `docs/formation_utilization_timing.json`; this file is rendered from it.
- Seed `20261100` is the exploratory seed Gate 13 already spent; it is not one of the 30 confirmatory seeds.
- T1 was generated with a regime switch at cycle `200`, matching the limb table; the generator's own default is 150.
- The pre-amendment timing artifact is preserved as `docs/formation_utilization_timing_pre_amendment.json`; its C and S cells are not a result of the amended design.
- Run as two foreground invocations (T2, then T1) after a background invocation was interrupted; each task was measured in full on the same seed and the same code, and the two task artifacts were merged without changing a measurement.
