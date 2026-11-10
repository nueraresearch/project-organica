# Presence-to-assertion conversion program — preregistration

**Status: DRAFT — NOT FROZEN, NOT RUN.** No cell has run. This document is a protocol draft, not a result and not an authorisation to change the engine.

**Build under audit:** `0.14.0`, engine digest `477aeb2ff34dd2cc857520d139d1b452892ec95a8158aedf72a089e8318f05e2`.

**Question.** For each world edge, where does it leave the conversion path between raw temporal presence and final asserted structure on the shipped 0.14.0 engine — and which stage is the first dominant loss?

This replaces the count-only reading in `docs/presence_assertion_audit_0.14.0.json`. That audit established a same-build count difference. It did not identify edges, assert subset relations, or provide witnesses.

The program has **three pre-registered questions, one freeze**:

1. **Construct audit** — are presence, candidate, admitted and asserted measured as comparable quantities on the same edge population?
2. **Cap sweep** — does assertion scale when only the Layer-1 prediction cap changes?
3. **Conversion audit** — which stage loses the most world edges, using an instrumented full-chain observer?

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

Q3 uses the Q2 cells when the observer is proven behavior-neutral; otherwise it uses a fresh block. It may not add a cap level or a new mechanism.

### Required instrumentation

A benchmark-only observer must record, per edge and cycle:

- `C`: candidate construction before the cap;
- `E`: eligibility outcome and filter reason;
- `R`: score/rank and the ordering key;
- `S`: admission outcome and cap;
- `A`: final asserted structure and supporting type;
- `U`: readout use, only if a separate readout instrument is defined.

The observer must be proven behavior-neutral against the shipped control: same stage fingerprints with the observer on and off. If it changes behavior, it is not an observer and Q3 is `VOID`.

`C`, `E` and `R` are internal stages. If they cannot be observed without changing behavior, Q3 stops at `S` and must say so; it may not assign a loss to an unobserved stage. `U` is outside the current acquisition instrument and is not claimed in this draft.

### Loss rule

For each seed, count world edges retained at each observed stage:

`retained_0 = |W|`, `retained_1 = |P ∩ W|`, `retained_2 = |C ∩ W|`, and so on through `A_W`.

The **first dominant loss** is the earliest stage with the largest absolute drop in world-edge count. Ties are broken by the earlier stage. Report the relative retention beside the absolute drop; a large relative loss on a small denominator is not the same finding as a large absolute loss.

If `C`, `E` or `R` is unobserved, the loss rule runs only through the observed stages and says so. It does not fill the missing stage with an estimate.

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

### Reading for Q3

Q3 does not test an engine mechanism. It returns:

- the per-seed stage table;
- the first dominant observed loss stage;
- the route split `A_pred` versus `A_other`;
- the positive and negative witnesses;
- a statement of which stages were not observed.

That is the target-selection artifact. It is not an intervention, a defect verdict, or an adoption decision.

## 6. Rival explanations this program separates

| Rival | What would support it | What would weaken it |
| --- | --- | --- |
| Instrument/object mismatch | `A_W ⊄ P`, or `P` differs across cap arms | `A_W ⊆ P` and invariant `P` |
| Capacity or ranking | `SCALES`, with additional world edges entering `A_W` as the cap rises | `FLAT` |
| Admission-only bottleneck | `S_ever` rises but `A_W` does not | `ADMISSION SCALES, ASSERTION FLAT` |
| Non-prediction assertion route | `A_other` is a large share of `A_W` | `A_other` is empty or negligible |
| Downstream pathway loss | observed `C/E/R/S` retain edges, but `A` loses them | loss is already visible before admission |
| Readout/use failure | `A` retains edges but `U` does not use them | `U` is outside this draft; not claimed |

A diagnosis must name the alternative it excludes. Q1–Q3 are designed to do that before any engine change.

## 7. Freeze checklist

Before this becomes a frozen preregistration:

1. Implement a benchmark-only stage observer for `C`, `E` and `R`; prove it behavior-neutral.
2. Implement `CapOnlySleepService` and prove it overrides no method; cap 40 must reproduce the shipped control.
3. Add a test that the stage recorder can fail on a deliberately altered edge set.
4. Confirm the 14-module engine pin and the digest above in every cell.
5. Freeze Q1, Q2, Q3, their gates, their reading order, and the output schema before the first cell.
6. Record the owner’s authorisation to run. This draft does not provide it.

## 8. Stop condition

One program, three questions, one edge-level table, no engine change. Q1 must pass before Q2 is read; Q2 must establish a live cap before Q3 is read. Q3 may name a dominant stage; it may not implement an intervention. Any intervention needs its own preregistration, control, and withdrawal rule.

## 9. What this does not claim

This draft does not show that the cap causes the presence/assertion gap, that the gap is an engine defect, that any structure type is responsible, or that raising the cap would improve capability. It does not establish a conversion rate beyond these six historical seeds. It does not replace the D3 records, the C003 count audit, or the 0.13.0 presence artifact. `U` is not measured here.
