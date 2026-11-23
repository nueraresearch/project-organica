# Retention entry-transition follow-up — design

**Status: `FROZEN, NOT RUN`.** The design is frozen as `CONFIRMATORY-RETENTION-ENTRY-TRANSITION-1` in `docs/retention_entry_transition_prereg.json`; see `docs/RETENTION-ENTRY-TRANSITION-PREREGISTRATION.md`. The runner is built behind the grant check; there is no grant, cell or result. Nothing here is evidence.

**Frozen ID:** `CONFIRMATORY-RETENTION-ENTRY-TRANSITION-1`

## Why the prior block cannot answer the question

`CONFIRMATORY-RETENTION-FORMATION-ANCHORED-1` returned **`CONFIRMED, TEMPORALLY AMBIGUOUS`**. Its early-retention OR was **2.09** (1.36–3.23), but post-landmark retention had OR **32.83** (8.66–124.44), so the design could not separate early timing from later timing.

The ambiguity is structural, not only statistical. In that block, `assertion_cycle` was the first structure appearance after the landmark. An edge that was already in structure before the landmark, left, and returned after it received a post-landmark `assertion_cycle`. That is a re-entry, not a first assertion transition. The corrected population therefore mixed:

- edges that were never in structure before the landmark and entered later;
- edges that were in structure before the landmark and re-entered later.

Both were labelled "asserted" if present at cycle 120. The reverse association was also a boundary contrast, not a dose-response: **11/11** edges at late retention **1.0** were asserted, **58/100** in between, against **1/55** at **0.0**. A "post-landmark appearance" is still a snapshot property. This follow-up replaces it with an explicit absent-to-present transition and a pre-outcome structure-free interval.

## Question

Among never-served world edges that first loop by cycle 60 and remain absent from the readout structure through cycle `f + 39`, does loop retention in the first 20 cycles predict a **sustained first structure entry** in cycles `f + 40` through 120, after controlling for retention in the adjacent 20-cycle window and for early rank, count, strength and follow-up horizon?

`f` is the edge's first loop cycle. The answer is observational and applies only to this synthetic world family.

## What counts as the transition

| Term | Definition |
| --- | --- |
| Loop entry (`f`) | First cycle the edge appears in a reported loop. |
| Early window | Cycles `f` through `f + 19`, inclusive. |
| Proximal window | Cycles `f + 20` through `f + 39`, inclusive. |
| Structure-free interval | No structure appearance for the edge at any cycle `<= f + 39`. Required for every eligible edge. |
| Entry candidate | A cycle `t >= f + 40` at which the edge appears in the readout structure. |
| Sustained entry (the event) | The first `t >= f + 40` such that the edge appears at both `t` and `t + 1`. `entry_cycle = t`. |
| Final assertion | Presence in the structure at cycle 120. Descriptive only; not the outcome. |

```
f .............. f+19 | f+20 ........ f+39 | f+40 ................ 120
     early retention      proximal retention     first sustained entry
     <----------- structure-free through f+39 ----------->
```

This makes the event a **transition**, not persistence:

- the edge is absent at every cycle through `f + 39`;
- the event is the first two-cycle structure run at or after `f + 40`;
- a one-cycle flicker does not count;
- the outcome is not "present at 120", so entry followed by exit is still an entry event;
- final presence at 120 is reported separately as a descriptive secondary outcome.

The event is called a structure-entry transition rather than an assertion to keep "assertion" from silently meaning "presence at the end of the run." If the block is frozen, the preregistration should use these names.

## Population

Include a never-served world edge when all of the following hold:

- it is a world edge in the compositional world;
- it is never served at cap 40;
- it first loops at `f <= 60`;
- it has no structure appearance at any cycle `<= f + 39`;
- its early and proximal retention are defined over full 20-cycle windows;
- its follow-up horizon `f + 40` through 120 contains at least 20 cycles.

Exclude:

- never-served edges that never loop;
- edges forming after cycle 60;
- edges present in structure at any cycle through `f + 39`;
- edges served at least once;
- edges with incomplete predictor windows.

The `f <= 60` ceiling is deliberate. It gives every eligible edge at least 21 cycles in the outcome window and avoids the prior block's late-formation subgroup, which the strict structure-free requirement would make too sparse to support a separate claim.

## Predictors

| Predictor | Definition |
| --- | --- |
| `early_retention` | Distinct loop cycles in `f..f+19`, divided by 20. |
| `proximal_retention` | Distinct loop cycles in `f+20..f+39`, divided by 20. |
| `rank20` | Minimum 1-based rank in the repaired observer's full pre-cap universe over `f..f+19`. |
| `count20` | Direct temporal transition count at `f+19`. |
| `strength20` | Maximum loop-candidate strength over reported loops in `f..f+19`. |
| `followup` | Outcome cycles from `f+40` through 120, divided by 120. It is the single horizon control; `f` is descriptive. |
| `rank40` (sensitivity) | Minimum 1-based rank over `f+20..f+39`; reported only in the sensitivity model. |
| `count40` (sensitivity) | Direct temporal transition count at `f+39`; reported only in the sensitivity model. |
| `strength40` (sensitivity) | Maximum loop-candidate strength over `f+20..f+39`; reported only in the sensitivity model. |
| `final_assertion` | Presence in the structure at cycle 120. Descriptive secondary outcome; never the primary event. |

`proximal_retention` is measured **before** the outcome window. It is not a reverse-time variable and it is not defined after the event. This is the main repair: the prior block's "reverse" predictor could be measured after the very appearance it was supposed to predict.

## Model

Primary model, fitted by Firth penalized logistic regression:

```
logit P(sustained entry) =
    b0
  + b_early   * z(early_retention)
  + b_proximal* z(proximal_retention)
  + b_rank    * z(log2(rank20))
  + b_count   * z(count20)
  + b_strength* z(strength20)
  + b_followup* z(followup)
  + seed fixed effects
```

- The single primary coefficient is `b_early`. It is the association of early retention with the later transition, conditional on proximal retention and the early controls.
- Standardization uses complete-case mean and population SD.
- Seed is a fixed effect with the first seed as reference.
- No predictor selection.
- `proximal_retention` is a control, not a second primary test. Its coefficient is reported because it determines whether the early window is distinguishable from the adjacent window.

Supporting models, reported but not used for the verdict:

- base model without `proximal_retention`;
- full sensitivity model adding `rank40`, `count40` and `strength40` from the proximal window;
- final-presence model with `final_assertion` as outcome.

The sensitivity models are diagnostics. They cannot rescue a failed primary criterion.

## Criteria

| ID | Criterion |
| --- | --- |
| `P1` | Primary joint-model `early_retention` OR > 1. |
| `P2` | Primary joint-model `early_retention` 95% CI lower bound > 1. |
| `P3` | Every gate D1–D10 passes. |
| `P4` | `proximal_retention` OR <= 1, or its 95% CI includes 1. |

`P4` is a separation criterion, not a claim that proximal retention is null. It asks whether the early window carries an association that the adjacent pre-outcome window does not.

## Verdicts

| Verdict | Reading |
| --- | --- |
| `CONFIRMED` | P1–P4 pass. Early retention adds a positive association with the later transition beyond proximal retention and the controls. |
| `CONFIRMED, PROXIMALLY AMBIGUOUS` | P1–P3 pass but P4 fails. Both windows carry positive associations; this block does not identify the early window as the relevant one. |
| `DIRECTIONAL ONLY` | P1 and P3 pass but P2 fails. The point estimate is positive, the interval is not. |
| `NOT CONFIRMED` | P1 fails. |
| `VOID` | A gate fails. No coefficient is read. |

A `VOID` verdict is not a null result about retention. It says this design could not measure the transition.

## Gates

| Gate | Requirement |
| --- | --- |
| `D1_population` | At least **60** eligible edges and **20** sustained entries; one row per seed-edge. |
| `D2_structure_free` | Every eligible edge has no structure appearance at any cycle `<= f + 39`, finite early and proximal retention in full 20-cycle windows, and `f <= 60`. |
| `D3_rank_coverage` | At least **95%** of eligible edges have a finite `rank20`. |
| `D4_seed_levels` | All **24** planned seeds contribute eligible rows. |
| `D5_convergence` | The primary joint fit and the base fit converge with finite coefficients. |
| `D6_complete` | Every fitted row has finite `count20`, `strength20` and `followup`. |
| `D7_entry_validity` | Every entry has a finite `entry_cycle > f + 39` with appearances at `entry_cycle` and `entry_cycle + 1`; every non-entry has `entry_cycle = None`; no edge has a structure appearance before `f + 40`. |
| `D8_no_collision` | The seed block is collision-free at design, freeze and check. |
| `D9_separation` | `abs(Pearson r(early_retention, proximal_retention)) <= 0.80`; otherwise the two windows are not separable and the block is `VOID`. |
| `D10_exposure` | Every eligible edge has at least **20** cycles in `f + 40..120`; `f <= 60` already implies at least 21. |

`D1` is the feasibility gate. The strict structure-free interval may leave too few edges or events. If it does, the block is `VOID`; the thresholds are not lowered after seeing the count.

## Sample and freshness

- **24 fresh seeds:** `20620101`–`20620124`.
- **120 cycles**, cap **40**, same compositional world and PHASE_ACQUISITION schedule.
- One replay per seed.
- Collision scan over `docs` JSON is empty at design time.
- No seed, row or part from `CONFIRMATORY-RETENTION-FORMATION-ANCHORED-1` is reused.
- No late-formation cohort. Edges with `f > 60` are outside this block's scope.

Twenty-four seeds are proposed because the structure-free 40-cycle requirement is stricter than the prior block's population rule. This is not a power calculation. `D1` is the only feasibility check, and it is applied once.

## Design rationale

**Why require structure-free through `f + 39`?** It makes the event the first entry, not a re-entry. Without it, an edge that was in structure before the landmark can re-enter and be counted as a new assertion, which is the defect that produced the prior block's ambiguity.

**Why measure proximal retention before the outcome?** The prior reverse model used post-landmark retention that could include cycles after the event. That cannot distinguish "retention preceded entry" from "retention continued after entry." A pre-outcome adjacent window is a legitimate control.

**Why a two-cycle entry?** A single appearance can be a transient readout fluctuation. Requiring `t` and `t + 1` makes the event a sustained state transition, while still allowing the edge to leave later. Final presence remains descriptive.

**Why not use final assertion as the outcome?** Final presence mixes entry with persistence. The question is whether retention predicts the **entry transition**; persistence after entry is a different question and would need its own design.

**Why include `followup`?** Edges forming earlier have longer outcome windows. The control keeps the comparison from being a formation-timing comparison. `f` itself is descriptive and is not separately fitted because `followup` is an affine transform of it.

## What this would establish

A `CONFIRMED` verdict would establish, within this world family and cap, that early loop retention carries information about a later sustained structure-entry transition beyond adjacent pre-entry retention and early rank, count and strength. It would still be observational.

A `CONFIRMED, PROXIMALLY AMBIGUOUS` verdict would establish that retention predicts entry but not that the early window is special. It would not rescue the prior temporal-order claim.

A `NOT CONFIRMED` verdict would leave the prior ambiguous result unresolved.

A `VOID` verdict would mean the design is infeasible at this cap and seed count; it would not mean early retention has no effect.

None of these outcomes establishes a mechanism, a capability, transfer, a causal effect, a general engine property, or a claim about edges forming after cycle 60. The result is one synthetic world family at one cap.

## Stop condition

This is one block. After it is frozen:

- no moderator, predictor or cohort may be added;
- no gate may be relaxed after seeing the population;
- no failed criterion may be re-read;
- a `VOID` result ends this design rather than triggering a threshold change.

If the result is `CONFIRMED, PROXIMALLY AMBIGUOUS` or `NOT CONFIRMED`, the next step is a synthesis of what the retention line has and has not shown, not another retention block with the same structure.

## Next actions

The design is frozen. The owner must decide whether to:

1. record a dated grant;
2. run the built runner, which captures full appearance cycles, not only the first post-landmark appearance;
3. adjudicate the 24 cells once.

The runner is built; no grant, cell or result exists.
