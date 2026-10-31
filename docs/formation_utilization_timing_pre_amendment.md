# Formation versus utilization — one-seed timing pass (pre-amendment)

> **Preserved, superseded.** This is the timing pass as it stood before
> Amendment 1 (§12 of the preregistration). Its C and S cells were measured
> under the temporal-feedback confound its own D1 reports, and they are **not**
> a result of the amended design. A and B are unchanged by the amendment; their
> reported cells are the reproducibility check between the two passes, at the
> four decimals they are reported to. The live artifact
> is `docs/formation_utilization_timing.json`.

**Generated:** 2026-10-30T22:49:42.430439+00:00  
**Engine:** Organica 0.10.0  
**Command:** `python benchmarks/formation_utilization.py --timing`  
**Status:** timing pass only — one exploratory seed (`20261100`). No campaign result, no win/tie/loss, no verdict.  
**Campaign readiness:** NOT AUTHORISED by this pass. All applicable audits pass, but D1 shows the arms do not share a temporal graph; the protocol's arm table claims all counts are untouched, and that is false for this engine. The campaign is not authorised by this pass pending a protocol amendment.

This artifact exists to report the measured cost of the pre-registered campaign before it starts, and to record that the seven audits behave. It is not `docs/formation_utilization.json`; only a full campaign may write that.

## 1. Measured cost

| Task | Arm | Cap | Admission | Acquisition (s) | Revision learn (s) | Scoring (s) | Total (s) |
|---|---|---|---|---|---|---|---|
| T2 | A | 20 | none | 35.3 | 21.4 | 0.2 | 56.9 |
| T2 | B | 1000 | none | 38.9 | 27.0 | 0.2 | 66.2 |
| T2 | C | 1000 | support | 36.0 | 27.6 | 0.2 | 63.8 |
| T2 | S | 1000 | shuffled | 36.4 | 23.9 | 0.2 | 60.5 |
| T1 | A | 20 | none | 46.1 | 21.1 | 0.3 | 67.4 |
| T1 | B | 1000 | none | 51.0 | 31.7 | 0.3 | 83.0 |
| T1 | C | 1000 | support | 64.8 | 33.5 | 0.3 | 98.6 |
| T1 | S | 1000 | shuffled | 59.1 | 26.5 | 0.3 | 85.9 |

Mean engine run: **72.8 s** over 8 measured runs. Arm C's filter adds no measurable cost (the filter is a set membership test over at most a few hundred candidate pairs per cycle).

- Campaign arms (A, B, C × 2 tasks × 30 seeds = 180 runs): **3.6 h** sequential.
- A6's shuffled arm (2 tasks × 30 seeds = 60 runs): **1.2 h** sequential.
- Comparators (2 tasks × 30 seeds = 60 fits): **0.01 h** sequential.
- **Total sequential: 4.9 h.** Each task-seed unit is independent, so `--workers` divides this without changing any per-run measurement.

The projection is arithmetic on the measured runs, not a second measurement. It excludes A2's recording, which is in-memory and was on for every run above.

## 2. The audits

| Audit | T2 | T1 | Evidence (T2) |
|---|---|---|---|
| A1 arm differential | PASS | PASS | arms differ as specified: A 0.0000 < 0.50 <= B 1.0000, C 1.0000 |
| A2 oracle exactness | PASS | PASS | 14379 permitted candidates across 131 cycles admitted exactly; the cap never bound after filtering |
| A3 precision premise | PASS | not applicable | B Layer-1 precision 0.3373 <= 0.3543; C's admission precision is 1.0 |
| A4 denominators | PASS | PASS | every limb has a non-zero denominator |
| A5 readout matches construct | PASS | PASS | the readout recovers the known answer and can be wrong |
| A6 no leakage | PASS | not applicable | shuffling collapsed Layer-1 coverage to 0.0000 and Layer-1 precision to 0.0; transfer 0.5002 vs C's 0.3670 |
| A7 attribution share | PASS | PASS | Layer 1 carries 0.9458 of the readout's edge weight (hypotheses 0.0045); threshold 0.50 |

No audit failed. A6 is marked not applicable where the shuffled filter necessarily retains permitted pairs; the retained share is in its evidence. A6 is gated on the primary task T2, where the shuffle retains none.

## 3. Diagnostic D1 — arm independence

- **T2:** **NOT independent**. The arms do not share a temporal graph: 32 edges differ (374 vs 380), and the permitted candidate streams differ on 59 cycle(s), first at cycle 6 (248 missing, 172 extra). The engine's lookback includes sleep rows, so an admission filter changes Layer 1's own input; the arm table's 'all counts are untouched' is not true of this engine.
- **T1:** **NOT independent**. The arms do not share a temporal graph: 21 edges differ (362 vs 351), and the permitted candidate streams differ on 107 cycle(s), first at cycle 40 (274 missing, 120 extra). The engine's lookback includes sleep rows, so an admission filter changes Layer 1's own input; the arm table's 'all counts are untouched' is not true of this engine.

D1 is a diagnostic, not a gate: the protocol has no audit for arm independence and adding one after the commit would be a new feature. It is reported because it bears on what the arms mean, and because a campaign run under a confound is worse than no campaign.

## 4. Scores (descriptive — not a result)

| Task | Arm | Retention | Transfer | Revision |
|---|---|---|---|---|
| T2 | A | 0.4530 | 0.4539 | 0.4634 |
| T2 | B | 0.4244 | 0.4254 | 0.4212 |
| T2 | C | 0.3667 | 0.3670 | 0.3486 |
| T2 | S | 0.4996 | 0.5002 | 0.5286 |
| T2 | bar | 0.3473 | 0.3507 | 0.3522 |
| T1 | A | 0.2826 | 0.2820 | 0.4599 |
| T1 | B | 0.2370 | 0.2359 | 0.4014 |
| T1 | C | 0.2350 | 0.2346 | 0.3890 |
| T1 | S | 0.3038 | 0.2973 | 0.4523 |
| T1 | bar | 0.2066 | 0.2117 | 0.4679 |

**Where the oracle arm sits.** On this seed arm C is the best Organica arm on every limb, but it clears the bar on only 2 of 6 task-limbs (T2 revision, T1 revision). On the primary transfer limb it is worse than the bar by 0.0163 nats on T2 and 0.0229 nats on T1. One seed is not a verdict and these numbers may not be quoted as a loss; they are recorded because an oracle-admitted arm that does not clear a counting baseline on its own timing seed is a warning the campaign should carry.

The bar row names the comparator selected per limb on the calibration seed. One seed cannot produce a verdict: the decision rule needs a paired bootstrap over seeds, and `analyse()` refuses to run below two. Nothing in this table may be quoted as a win, a loss or a tie.

A1's coverage is the Gate 13 quantity over the world edges derived from the training stream, on the all-structure basis the gate pins. A3's precision is the Layer-1 quantity on which the 0.3443 ceiling was measured. Arm C's all-structure readout precision is reported in the artifact and is not 1.0, because the readout still aggregates all six structure types; only its Layer-1 admission is exact.

## 5. Disclosures

**A6 wording superseded.** The committed audit asked that shuffling the oracle make C "collapse to B's coverage". B's coverage is 98–100 %, so no shuffle can produce that value: the direction is impossible. A6 is implemented as shuffled precision in B's measured band, shuffled coverage under A1's own 0.50 gate, and the shuffled transfer score not matching C's. The thresholds are the protocol's own; none was relaxed.

**three limbs, not four.** §3.4 says four scored windows; §4.4 lists revision 200–249 and a held-out 250–299; the pinned runner scores three limbs. Three is what §7's Bonferroni-over-three assumes. This harness scores retention 110–149, transfer 150–199 and revision 250–299, and treats 200–249 as the learning window it is.

**T1's regime switch.** The T1 generator defaults to a law change at cycle 150, which would put the change inside the transfer window §4.4 says is under the old law. The harness generates T1 with a switch at 200 and verifies the recorded regime at the boundary. The module default and §4.4 disagree.

**A6 on T1 is not a control.** T1's support covers 12 of 16 targets per source, so a size-matched wrong filter necessarily retains permitted pairs (the retained share is printed). A6 is therefore gated on the primary task T2 and reported as not applicable on T1. A control that cannot discriminate is not a passed control.

**bar selection.** The comparators' configurations are frozen from the calibration artifact; only WHICH comparator is the bar per limb is chosen, on seed 20261099. Three comparators are fitted (replay, bigram, cell counter) rather than the protocol's two, which can only raise the bar.

**A2's scope.** A2 is the committed audit on the arm's own stream: admitted = count-threshold-eligible pairs intersected with the support. A stronger C-versus-B comparison was implemented first and failed; it is reported as D1, not folded into A2. The strict comparison is kept because it measures whether the arms are independent, and it is not used to pass or fail the protocol.

**A3's band is T2's.** The 0.3443 precision ceiling was measured on the compositional world. A3 applies it on T2 and reports T1's precision without gating, because T1 has no committed band. Applying a T2 constant to T1 would measure the wrong population.

**orientation of the decision difference.** §7 writes d = score(arm) − score(baseline) and calls a positive lower bound a win. With log-loss, lower is better, so the orientation that makes the rule coherent is d = baseline log-loss − arm log-loss. That is the quantity bootstrapped, and it is named in every artifact.

## 6. Provenance

- Artifact: `docs/formation_utilization_timing.json`; this file is rendered from it.
- Seed `20261100` is the exploratory seed Gate 13 already spent; it is not one of the 30 confirmatory seeds.
- T1 was generated with a regime switch at cycle `200`, matching the limb table; the generator's own default is 150.
