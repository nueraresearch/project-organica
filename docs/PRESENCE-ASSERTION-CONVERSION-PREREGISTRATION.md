# Presence-to-assertion conversion program — preregistration

**Status: DRAFT — NOT FROZEN AS A PROGRAM, NOT RUN.** No cell has run. Q1, Q2 and Q3 are frozen separately (`PRESENCE-CONSTRUCT-1`, `PRESENCE-CAP-1`, `PRESENCE-CONVERSION-1`); none of the three is authorised to run, and this document is still not a frozen preregistration because the program freezes question by question. It is not a result and not an authorisation to change the engine. No block may be cited as passed while it is unrun; §6 states the reading rule.

**Build under audit:** `0.14.0`, engine digest `477aeb2ff34dd2cc857520d139d1b452892ec95a8158aedf72a089e8318f05e2`.

**Question.** For each world edge, where does it leave the conversion path between raw temporal presence and final asserted structure on the shipped 0.14.0 engine — and which stage is the first dominant loss?

This replaces the count-only reading in `docs/presence_assertion_audit_0.14.0.json`. That audit established a same-build count difference. It did not identify edges, assert subset relations, or provide witnesses.

The program has **three pre-registered questions, one freeze**:

1. **Construct audit** — are presence, candidate, admitted and asserted measured as comparable quantities on the same edge population?
2. **Cap sweep** — does assertion scale when only the Layer-1 prediction cap changes?
3. **Conversion audit** — which stage loses the most world edges, using an instrumented full-chain observer?

## Status at a glance

| Question | Frozen record | State | Authorised | Cells run | Result artifact |
| --- | --- | --- | --- | --- | --- |
| Q1 construct audit | `PRESENCE-CONSTRUCT-1` (`docs/presence_construct_audit_prereg.json`) | `FROZEN, RUN` | yes, 2026-11-10 | 6 + control | `CONSTRUCT VALID` — `docs/PRESENCE-CONSTRUCT-AUDIT-RESULT.md` |
| Q2 cap sweep | `PRESENCE-CAP-1` (`docs/presence_cap_prereg.json`) | `FROZEN, RUN` | yes, 2026-11-10 | 24 + witness | `CAP LIMITING` — `docs/PRESENCE-CAP-RESULT.md` |
| Q3 conversion audit | `PRESENCE-CONVERSION-1` (`docs/presence_conversion_observer_prereg.json`) | `FROZEN, RUN` | yes, 2026-11-10 | 12 + witness + control | `OBSERVER NOT NEUTRAL` — `docs/PRESENCE-CONVERSION-OBSERVER-RESULT.md` |
| Q4 instrument repair | `PRESENCE-CONVERSION-2` (`docs/presence_conversion_repair_prereg.json`) | `FROZEN, NOT RUN` | no — `docs/AUTHORISATION-PRESENCE-CONVERSION-2.md` | 12 + witness + determinism rerun | none — no cell has run and no runner is built |

All three records carry `authorisation.granted: true` (`Authorize all runs`, 2026-11-10) and `no_cells_run: false`; each result artifact exists and its page is generated from it. The table is a status summary; the verdicts and their limits are in the result pages.

No engine change follows from any answer. A named loss stage is a target for a separate preregistration, not a licence to edit the engine.

## 1. One correction before the stages

`40 / 112 = 35.7%` is **not** a maximum final assertion rate.

The 40-slot cap is a **per-cycle Layer-1 prediction-admission budget**. It is not a cap on:

- `S_ever`, the union of admitted prediction edges across 120 cycles; this can exceed 40 distinct edges;
- `S_final`, the predictions retained at the end;
- `A`, the final asserted structure, which aggregates all six structure types;
- `A_W`, the world edges in that final structure.

The observed final `A_W` count of 34–47 is **not** “34–47 of 40 slots used.” It is a count of final world assertions after the whole pipeline. A single cycle may fill all 40 slots, fewer, or use a different 40 edges. The “4–12 unused slots” question is a per-cycle question, and the current count audit does not measure it.

The right stage questions are:

- how full is each cycle’s 40-slot prediction set;
- which world edges enter that set;
- which ever-admitted edges survive into final assertion;
- which final assertions arrived by a non-prediction route.

This distinction is the reason for the stage table below.

## 2. Stage chain

The full chain is:

`Present → Candidate → Eligible → Scored → Admitted → Asserted → Used`

Not every stage is observable through the current public path. The protocol records observability rather than inventing a measurement.

| Stage | Symbol | Definition | Current observability |
| --- | --- | --- | --- |
| World | `W` | World-law edges derived from the training stream | observable |
| Present | `P` | Raw temporal edges present after acquisition | observable: `mem.temporal_edges(min_count=1)` |
| Candidate | `C` | Prediction candidates constructed before the cap | not exposed; needs a benchmark-only observer |
| Eligible | `E` | Candidates passing the engine’s eligibility filters | not exposed separately; needs an observer |
| Scored | `R` | Candidates with their engine ranking/score | not exposed as a per-edge record; needs an observer |
| Admitted | `S` | Prediction edges emitted by a cycle after the cap | observable from the `SleepReport` |
| Asserted | `A` | Edges in the final structure across all six types | observable: `structure_edges(_load_prior_candidates())` |
| Used | `U` | Edges used by a readout or held-out prediction | not measured by the acquisition gate; needs a separate readout instrument |

Within admission, distinguish:

- `S_cycle`: prediction edges emitted in one cycle, `len(S_cycle) <= cap`;
- `S_ever`: union of `S_cycle` over the acquisition run;
- `S_final`: prediction edges still live at the end.

Within assertion, distinguish:

- `A_W = A ∩ W`;
- `A_pred = A_W ∩ S_ever`;
- `A_other = A_W \ S_ever`.

`A_other` is not a defect. It is the non-prediction route: loops, processes or other structure types can assert a world edge without that edge having been admitted as a prediction. The audit must report it rather than assume every final assertion came through the prediction cap.

### Observability matrix

| Stage | Q1 construct | Q2 cap sweep | Q3 conversion |
| --- | --- | --- | --- |
| `W` | yes | yes | yes |
| `P` | yes | yes | yes |
| `C` | define only | no | instrumented |
| `E` | define only | no | instrumented |
| `R` | define only | no | instrumented |
| `S_cycle` / `S_ever` | yes | yes | yes |
| `S_final` | yes | yes | yes |
| `A` / `A_W` | yes | yes | yes |
| `A_pred` / `A_other` | yes | yes | yes |
| `U` | no | no | separate readout required |

A stage marked “no” is not a zero. It is **not measured** in that question. No count-only shortcut may substitute for it.

## 3. Question 1 — construct audit

**Purpose.** Verify that the quantities are comparable, on the same build, the same world, the same edge set, and the same observation window.

| Field | Value |
| --- | --- |
| build | `0.14.0`, digest above |
| cap | shipped `40`; no manipulation |
| seeds | `20261100`–`20261105` |
| cycles | 120 (warmup + acquisition) |
| cells | 6 (one per seed) |
| output | per-edge rows for `W`, `P`, `S_cycle`/`S_ever`, `S_final`, `A`, `A_W` |

Q1 does **not** measure `C`, `E`, `R` or `U`; it defines them so later questions cannot silently collapse them. Q1 also does not run a cap sweep.

### Gates for Q1

| Gate | Requirement |
| --- | --- |
| `C1_build` | one build, the exact digest, all 14 modules pinned; no `organica/` module differs from the pinned digest |
| `C2_world` | one `W` per seed; no perturbation of event order or training window |
| `C3_presence` | `P` is a set, not a count; record its digest and per-edge membership |
| `C4_denominator` | `W`, `P` and `S_ever` are non-empty; a zero denominator is not measurable |
| `C5_object` | `A_W ⊆ P`; a failure is `OBJECT MISMATCH` |
| `C6_witnesses` | at least one positive `A_W` and one negative `P \ A_W` edge per seed |
| `C7_seed_axis` | at least two distinct `(P, S_ever, A_W)` fingerprints across the six seeds |
| `C8_determinism` | a fresh-process rerun of one seed reproduces its stage fingerprints |

`PRESENCE-CONSTRUCT-1` adds one gate this table does not have: `C9_audit_row_reproduced` requires every Q1 cell to reproduce its published audit row — world edges, present edges, asserted world edges and asserted fingerprint — because Q1 reuses the audit's seeds and build, and a cell that differs from the audit would make the construct comparison answer a different world. The addition was made at freeze time, before any cell, and is recorded in the record's `freeze_notes`; `C1`–`C8` stand unchanged. The frozen record also names the determinism control seed, which this draft leaves open.

Q1 verdicts are `CONSTRUCT VALID`, `OBJECT MISMATCH`, `NOT MEASURABLE`, or `VOID`. A construct pass does not say the cap is causal or that assertion is defective.

## 4. Question 2 — cap sweep

**Purpose.** Hold the world, presence and every non-cap parameter fixed; change only the Layer-1 prediction cap; determine whether admitted and asserted world-edge membership scales with capacity.

| Field | Value |
| --- | --- |
| variable | `layer1_prediction_cap` |
| levels | `40`, `80`, `112`, `uncapped` (`10**9` diagnostic ceiling) |
| implementation | benchmark-only `CapOnlySleepService(SleepService)` with only the class constant changed |
| engine edit | none |
| cells | 24 (4 caps × 6 seeds) |
| cycles | 120 |
| pairing | same seed/world across caps; only the cap differs |
| seeds | `20611401`–`20611406`; bootstrap `20611407` reserved and not run |
| witness cell | seed `20261100` at cap `40`; it must reproduce the published audit row for the shipped control |

The treatment class must not override `_build_predictions`, candidate ordering, filtering, retention, decay, or any other method. The existing `_CapOverrideSleepService` is **not** the treatment: it replaces candidate construction as well as the cap, so it cannot answer a one-variable question.

`uncapped` means a diagnostic ceiling of `10**9`, not a proposed setting. It is a positive control for whether capacity is binding at all.

### Gates for Q2

| Gate | Requirement |
| --- | --- |
| `K1_build` | all cells name one build and digest; no mixed-build rows |
| `K2_same_world` | `W` is identical across the four caps of every seed |
| `K3_presence_invariant` | `P` is identical across the four caps of every seed |
| `K4_cap_live` | each cell records its cap; the 40 arm has `len(S_cycle) <= 40`; at least five of six seeds produce a full 40-edge cycle; the higher caps produce a different `S_ever` on at least five of six seeds |
| `K5_cap_only` | the subclass overrides no method and differs only in `MAX_PREDICTIONS`; cap 40 reproduces the shipped control’s fingerprints |
| `K6_denominator` | `W`, `P` and `S_ever` are non-empty in every cell |

A cap that never fills or never changes admission is `CAP NOT BINDING`; no scaling reading is made.

### Readings for Q2

These are membership readings, not aggregate-count readings.

| Reading | Rule |
| --- | --- |
| `SCALES` | moving from 40 to 112 or uncapped adds world edges to `A_W` on at least five of six seeds, in the same direction across levels |
| `FLAT` | at least five of six seeds gain no `A_W` edges at 112 or uncapped relative to 40 |
| `MIXED` | neither `SCALES` nor `FLAT`; report the per-seed membership changes and do not force a label |
| `ADMISSION SCALES, ASSERTION FLAT` | `S_ever` changes but `A_W` does not on at least five of six seeds |

`SCALES` is consistent with a capacity/ranking explanation. `FLAT` is consistent with a pathway explanation, but neither is a causal finding: the cap sweep narrows the alternatives; it does not name the mechanism.

## 5. Question 3 — conversion audit

**Purpose.** With the full chain instrumented, locate the **first stage that loses the largest number of world edges** for each seed. That stage, not the end-point discrepancy, becomes the target for any later intervention.

**Status: frozen outside this draft.** Q3 is `PRESENCE-CONVERSION-1`, frozen 2026-11-10 in `docs/presence_conversion_observer_prereg.json`, with the generated page `docs/PRESENCE-CONVERSION-OBSERVER-PREREGISTRATION.md` and the `conversion observer prereg` gate. It was frozen and authorised on 2026-11-10 (`Authorize all runs`) and **ran the same day**: six fresh seeds observer-off and observer-on, plus one observer-off witness cell on the audit's first seed, at 120 cycles. **The verdict is `OBSERVER NOT NEUTRAL`.** The observer-on arm differed from the observer-off arm on every seed, and `X1` names the first, seed 20611501, with differing admission windows, admitted union, final assertion and asserted world edges. So the instrument changed the run it was recording. Under the record's own decision table that licenses nothing about conversion: its stage table is not a conversion result, the instrument must be fixed, and a new block must be registered. `docs/PRESENCE-CONVERSION-OBSERVER-RESULT.md`.

It does not wait for Q1 or the Q2 block, and it does not use the Q2 cells: observing `C`, `E` and `R` does not depend on either, and the record states the consequence — if Q1 later changes a definition, this block is not re-scored. It adds no cap level and no new mechanism.

**Q1 is frozen too.** `PRESENCE-CONSTRUCT-1` fixes the construct audit in `docs/presence_construct_audit_prereg.json`, with its generated page and the `construct audit prereg` gate: the audit's own six seeds, the shipped build, the shipped cap, 120 cycles and gates `C1`–`C9`, where `C9` requires every cell to reproduce its published audit row and `C8` names the first seed as the determinism control. It was frozen and authorised on 2026-11-10 (`Authorize all runs`) and **ran the same day**: the six reading cells and the `C8` control all passed, so the verdict is **`CONSTRUCT VALID`**. It reuses the audit's seeds deliberately rather than claiming a fresh block, every cell reproduces its published audit row (`C9`), and `A_W` is a subset of `P` on every seed (`C5`). Its authorisation record is `docs/AUTHORISATION-PRESENCE-CONSTRUCT-1.md` and its result is `docs/PRESENCE-CONSTRUCT-AUDIT-RESULT.md`. That licenses the program's construct step — later blocks may treat their per-edge readings as same-object measurements — and nothing else.

### Required instrumentation

A benchmark-only observer must record, per edge and cycle:

- `C`: candidate construction before the cap;
- `E`: eligibility outcome and filter reason;
- `R`: score/rank and the ordering key;
- `S`: admission outcome and cap;
- `A`: final asserted structure and supporting type;
- `U`: readout use, only if a separate readout instrument is defined.

The observer must be proven behavior-neutral against the shipped control: same stage fingerprints with the observer on and off. If it changes behavior, it is not an observer and Q3 is `VOID`.

**Implemented.** The observer is `benchmarks.presence_conversion_observer.StageObserverSleepService`. It overrides `_build_predictions` only, calls the engine's own method with `MAX_PREDICTIONS` at the diagnostic ceiling, records the full pre-cap list, restores the shipped cap and returns the engine's own first rows; a detector walks the MRO and fails if a second method is overridden. `measure` refuses until the owner authorises the block.

**An identity this engine makes.** Construction already applies the eligibility filters, so `C` and `E` hold the same edges here: `E` is a reason record (`constructed`, `below_prediction_min_count`, `unexplained`), not a separate retention step. The frozen record states that rather than inventing a stage; an engine that separates construction from eligibility would gain a step and be re-registered, not re-read.

`C`, `E` and `R` are internal stages. If they cannot be observed without changing behavior, Q3 stops at `S` and must say so; it may not assign a loss to an unobserved stage. `U` is outside the current acquisition instrument and is not claimed in this draft.

### Loss rule

For each seed, count world edges retained at each observed stage:

`retained_0 = |W|`, `retained_1 = |P ∩ W|`, `retained_2 = |C ∩ W|`, and so on through `A_W`.

The **first dominant loss** is the earliest stage with the largest absolute drop in world-edge count. Ties are broken by the earlier stage. Report the relative retention beside the absolute drop; a large relative loss on a small denominator is not the same finding as a large absolute loss.

If `C`, `E` or `R` is unobserved, the loss rule runs only through the observed stages and says so. It does not fill the missing stage with an estimate.

The frozen record's chain is `W → P → C → S_cycle → S_ever → A_pred`. `E` is not a step in it, because here it is an identity with `C`; `A_other` is the bypass and is counted in neither retention nor loss.

### Gates for Q3

| Gate | Requirement |
| --- | --- |
| `X1_observer_neutral` | observer-on and observer-off produce identical stage fingerprints and final assertions |
| `X2_stage_complete` | every observed stage has per-edge membership and a nonzero denominator |
| `X3_no_unobserved_imputation` | no stage is assigned a count without an observation |
| `X4_same_object` | `A_W ⊆ P` |
| `X5_witnesses` | positive `A_W` and negative `P \ A_W` witnesses for every seed |
| `X6_seed_axis` | at least two distinct stage fingerprints across seeds |
| `X7_determinism` | a fresh-process rerun reproduces the first seed’s observed stages |

The frozen record keeps these seven and adds `X8_control_reproduces_audit`: the observer-off witness cell on seed `20261100` must reproduce the published audit row — present count, asserted count and asserted fingerprint — because an observer that changes behaviour is not an observer.

### Reading for Q3

Q3 does not test an engine mechanism. It returns:

- the per-seed stage table;
- the first dominant observed loss stage;
- the route split `A_pred` versus `A_other`;
- the positive and negative witnesses;
- a statement of which stages were not observed.

That is the target-selection artifact. It is not an intervention, a defect verdict, or an adoption decision.

### Q4: the conversion question re-asked with a neutral observer

**Status: frozen outside this draft, NOT RUN, NOT GRANTED.** Q4 is `PRESENCE-CONVERSION-2`, frozen 2026-11-10 in
`docs/presence_conversion_repair_prereg.json`, with the generated page
`docs/PRESENCE-CONVERSION-2-PREREGISTRATION.md`, the request
`docs/AUTHORISATION-PRESENCE-CONVERSION-2.md` and the `conversion repair prereg` gate. It is not authorised, no
cell has run, and no runner is installed; the repaired observer is the prerequisite.

Q3's instrument was not neutral: it lifted `MAX_PREDICTIONS` and returned the first cap rows, assuming the cap is
consulted only at the final truncation. It is spent earlier as a **quota split** — half the budget to
entropy-ranked transitions, the remainder to count-ranked cooccurrences — so a lifted cap serves a differently
composed list. On Q3's own published parts the lifted top-40 matched the shipped window in 0 of 89 cycles, mean
overlap 0.297, and 70.8% of admitted edges ranked at or below 40.

Q4's observer serves the engine's own list from a call at the shipped cap, returned untouched, and records the
pre-cap universe from a second call at the diagnostic ceiling. Six fresh seeds 20611601-20611606 with bootstrap
20611607, one witness cell on the published audit's seed 20261100, 120 cycles, 12 design cells and one determinism
rerun. Every cycle also records the allocation — transitions and cooccurrences served, summing to the window size.

Its gates are `N1_served_is_engine`, `N2_observation_cannot_leak`, `N3_allocation_recorded`,
`N4_stage_complete`, `N5_witness_reproduces_audit`, `N6_seed_axis` and `N7_determinism`. Its verdicts are
`SERVED NOT ENGINE`, `OBSERVATION LEAKS`, `VOID` and `CONVERSION STAGE MEASURED`; under the reading rule below,
no verdict from an unrun block may be cited as a result.

## 6. Reading rule: a frozen protocol is not a result

A block may be cited as **passed** only when all four conditions hold:

1. the owner's authorisation for that block is recorded;
2. the block's own runner has run and written its result artifact;
3. every gate the block declares has passed; and
4. the published verdict is the one its gates imply.

Until then the block is **not evidence**. A frozen, unrun or unauthorised block may be
described by its question, protocol, gates and runner, but no synthesis may cite it as
passed, validated, supported, or as licensing a later reading. `VOID`, `NOT MEASURABLE`,
`CAP NOT BINDING` and a failed gate are not passes either.

The rule binds cross-question synthesis as well as per-question results. No synthesis may
pool a block that has not run, substitute a planned or authorised run for an artifact, or use
an unrun block as a premise for another. A result is citable only within its declared scope:
Q1 licenses construct comparability, not a cap or conversion finding; Q2 licenses a cap
reading only after `K1`–`K6` pass, and a `CAP NOT BINDING` result is not a cap finding; Q3
licenses a target-selection table, not an intervention or a defect verdict.

**On 2026-11-10 all three blocks ran under the recorded grant, and one of the three failed its
own gate.** Q1 returned `CONSTRUCT VALID` with all nine gates passing, so the program's
construct step is citable as a measurement precondition and as nothing more. Q2 returned
`CAP LIMITING`: the mean paired gain at cap 112 is 15.83 world edges against a 10-edge bar,
the lower bound is 8.08, and six of six seeds moved in the predicted direction, which
licenses an owner decision on the cap and no engine change by itself. Q3 returned
`OBSERVER NOT NEUTRAL`: its neutrality gate failed, so it is **not** a conversion result and
its stage table is not citable. A block that is still `FROZEN, NOT RUN` remains not evidence,
and a run whose gate failed is not a pass either; each verdict is read in its own result page.

## 7. Rival explanations this program separates

| Rival | What would support it | What would weaken it |
| --- | --- | --- |
| Instrument/object mismatch | `A_W ⊄ P`, or `P` differs across cap arms | `A_W ⊆ P` and invariant `P` |
| Capacity or ranking | `SCALES`, with additional world edges entering `A_W` as the cap rises | `FLAT` |
| Admission-only bottleneck | `S_ever` rises but `A_W` does not | `ADMISSION SCALES, ASSERTION FLAT` |
| Non-prediction assertion route | `A_other` is a large share of `A_W` | `A_other` is empty or negligible |
| Downstream pathway loss | observed `C/E/R/S` retain edges, but `A` loses them | loss is already visible before admission |
| Readout/use failure | `A` retains edges but `U` does not use them | `U` is outside this draft; not claimed |

A diagnosis must name the alternative it excludes. Q1–Q3 are designed to do that before any engine change.

## 8. Freeze checklist

The program no longer freezes as one document. Q2 froze as `PRESENCE-CAP-1` and Q3 as `PRESENCE-CONVERSION-1`; Q1 remains this draft. What is done, and what is not:

1. **Stage observer for `C`, `E` and `R` — built, not yet proven on real cells.** `benchmarks/presence_conversion_observer.py` records the pre-cap candidate list, the eligibility reason per present edge, the rank and the ordered admission window, and `tests/test_presence_conversion_observer.py` drives the neutrality comparator with identical, dropped, reordered and changed-assertion arms so it is shown to fire. The real-cell proof is `X1_observer_neutral`, the first gate of the unrun block; until it runs, neutrality is an instrument-level result, not a measured one.
2. **`CapOnlySleepService` — built and frozen.** `benchmarks.presence_cap_experiment.CapOnlySleepService` overrides no pipeline method (only `__init__`, which sets the constant), and `K5_cap_only` reproduces the published audit row at cap 40. It is frozen as `PRESENCE-CAP-1` in `docs/presence_cap_prereg.json`.
3. **A test that the stage recorder can fail — done.** The Q3 test module proves the recorder and the loss rule fail on a deliberately altered edge set, a dropped window, a reordered window and a changed assertion, and that an unreported second override is caught.
4. **The 14-module engine pin and digest in every cell — pin in place, per-cell replay pending.** The `engine pin` gate checks the pin now; the digest is recorded in both frozen blocks and in this draft, but confirming it in every cell is owed by the run, not by this draft.
5. **Freeze Q1, Q2, Q3, their gates, reading order and output schema before the first cell — all three done.** Q1 is `PRESENCE-CONSTRUCT-1`, with gates `C1`–`C9` and a deliberately reused audit seed block; Q2 and Q3 remain as frozen. No cell of any of the three has run, and no cross-question reading may assume a construct pass.
6. **The owner’s authorisation to run — not granted.** All three frozen records carry `granted: false`; no cell may run, and Q1's, Q2's and Q3's entry points refuse without a grant.

## 9. Stop condition

One program, three questions, one edge-level table, no engine change. Q1 must pass before the program claims construct separation; Q2 must establish a live cap before its result is read as a cap finding. Q3 was frozen separately and reads ahead of both, because observing `C`, `E` and `R` does not depend on either block: its result is a target-selection table, not a construct or cap finding, and if Q1 later changes a definition it is not re-scored. Q3 may name a dominant stage; it may not implement an intervention. Any intervention needs its own preregistration, control, and withdrawal rule.

## 10. What this does not claim

This draft does not show that the cap causes the presence/assertion gap, that the gap is an engine defect, that any structure type is responsible, or that raising the cap would improve capability. It does not establish a conversion rate beyond these six historical seeds. It does not replace the D3 records, the C003 count audit, or the 0.13.0 presence artifact. `U` is not measured here.
