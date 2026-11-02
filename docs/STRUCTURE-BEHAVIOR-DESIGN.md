# Structure and Behavior — Design Record

**Status: design record, written before any seed is named. No seed has been allocated, no run is
authorised, and no number in this document comes from a run of this design.** It is written under the
freeze in the action list (row 13): the measurement framework is fixed, and this record may specify a
question and an analysis but may not add apparatus to answer it. Independent review is required before
seeds are named (§8), and the reviewer must not have written the estimator or selected the historical
result.

## 1. The hypothesis, and the level of evidence it targets

Adopted as the project's **working** hypothesis on 2026-11-02, at Level 2:

> **Within one generating configuration, the organism's displacement index at the end of formation
> predicts its prediction score on held-out transitions later in the same run — and that relation
> persists, weakens, disappears, or reverses when the generating configuration changes.**

| Level | Claim | Status in this design |
| --- | --- | --- |
| 1. Association | structural properties correlate with behavior | a necessary first read; not sufficient for the claim |
| 2. Prediction | structure measured **earlier** predicts behavior on **genuinely held-out** events | **the objective of this experiment** |
| 3. Causal influence | changing the structural property changes the behavior, other factors controlled | **not attempted here**; named as the later objective |

**Why Level 3 is excluded, in the record rather than in a footnote.** Nothing in this design manipulates
the structural variable: `DI` is measured from a run, and the behavior is scored from the same run later.
A positive, stable relation would license "predicts" and nothing stronger. The engine is frozen (AGENTS
rule 12), so a causal test needs an in-process arm that changes the structural quantity and nothing else —
the pattern the strength-assignment harness already uses — and that arm is not designed here. Every
sentence this experiment licenses is accordingly a prediction sentence.

## 2. The structural variable

**`DI = late_retained / late_available`** — the Phase L displacement index, computed from the
organism's predicted structure against the late gold pairs in the retention window
(cycles 110–150). Its companion `PI` and the difference `DI - PI` are reported as diagnostics; neither
enters the criterion.

Two properties are fixed, not adjustable:

- **A zero denominator is not measurable.** `late_available == 0` means the late structure was never
  available to be retained, so `DI` is reported `None` and the cell is **excluded**, never scored 0.0
  (AGENTS 13b; this is the exact defect that produced the Phase L pilot's fake `DI = 0.000` sweep).
- **`DI` is structural, not behavioral.** It counts retained gold pairs, not predictions of held-out
  events. The behavioral variable is a different measurement on different cycles (§3).

The variable is made to vary by the strength manipulation K3 already exercised: the late group's support
weight at 3:1 versus 1:3 against the early group, with `DI` the measured consequence. A design whose
`DI` values do not vary is a dead axis and stops the run before any outcome is read (AGENTS 13a).

## 3. The behavioral outcome

**`revision_held_out`** — next-tag prediction on the revision-test window (cycles 250–300) under the rotated
law (`LAW_R1`), restricted to the transitions withheld from **both** formation and revision learning. It
is scored by the calibrated readout with **no refit during evaluation**.

Named for what it measures: *next-tag prediction on transitions the organism never saw and could not have
learned from either exposure window*. It is **not** a measure of belief revision in any semantic sense,
and it is not "understanding". The project's belief-revision task returned REVERSED (0.4111 against
0.9846) and this endpoint is deliberately a different one.

## 4. Temporal order, and why the outcome is not a residue of the predictor

- `DI` is computed at the end of the retention window, cycle 110–150.
- The revision-learning window (200–250) comes after it; the revision-test window (250–300) comes last.
- The behavioral pairs are the two directed transitions in `WITHHELD`, and they are withheld from
  formation **and** from revision learning, so the scoring set is disjoint from everything the organism
  was shown.
- **Guard to be computed and reported:** the overlap between the pair set backing `DI` and the pair set
  scored as the outcome must be empty. It is disjoint by construction; the design requires the emptiness
  to be *measured* and printed, because "disjoint by construction" is the kind of claim that is right
  until an index is off by one.

If the overlap is non-empty, the run does not produce a result: it produces a design defect and stops.

## 5. The generating configurations

Primary configuration: the compositional world family (`CELLS` cells, `TAGS_PER_CELL` tags per cell,
`CYCLES` cycles), law rotation `LAW_R0` → `LAW_R1` at the revision boundary.

Declared secondary configurations, in order of cost, all of which reuse the frozen engine and need no new
apparatus:

1. **Presentation.** Block versus burst exposure of the same content (`scale_streams.burst_stream`),
   which changes when structure becomes available without changing what the content is.
2. **Hub structure.** The `scale_streams.hub_groups` variant, changing how many anchors the same tag
   budget is organised around.
3. **Cause-world ambiguity.** The `ground_truth_worlds.generate_cause_world` knobs — `overlap_features`
   and `noise_rate` — which change how identifiable the generating cause is while leaving the event
   vocabulary legal.

**Gate on the secondary configurations:** each needs its own withheld-transition set, enumerated under the
same criteria used for `WITHHELD` (28-subset enumeration, 25 % of directed transitions, criteria written
before the enumeration). If a configuration's analogue cannot be pre-enumerated under those criteria, that
configuration is **dropped and the omission reported**; it is never approximated by reusing the primary
`WITHHELD` set, which would score a different quantity under the same name (AGENTS 8).

**The ladder convention.** The 100-cycle scoring rule adopted in `docs/SCALING-LADDER.md` §10 governs the
graded-window endpoint those worlds were measured on. This design uses the acquisition windows above, so
it is a declared deviation: before seeds are named, the block's predicted sign-resolution probability must
be computed from stored design-block cells under a **named** reference rule and recorded here. If that
prediction cannot be computed for this endpoint, the block does not proceed on this window.

## 6. Analysis, null, and both directions of falsification

**Unit:** one world (seed), one configuration. **Estimand:** the slope of `revision_held_out` on `DI`
across worlds within a configuration — reported per configuration, never pooled across configurations
into one number.

**Null:** no relation — the slope is zero, or the sign of the relation is at chance across worlds.

**Falsifier A — direction.** The relation is absent or reversed *where the structure is present*: worlds
with high `DI` do not score above the comparator on the withheld transitions. This is a failure of the
hypothesis, not a failure of the instrument, provided the axis is live (§2's liveness check passed).

**Falsifier B — configuration.** The relation's **sign flips** across configurations while `DI` is
measured identically. This is the sharper outcome: it would show the behavior is driven by the generating
configuration rather than by the measured structure, and it is the result the design is built to be able
to report rather than explain away.

**Pre-committed outcomes**, each reported as the finding, in the project's own vocabulary: *persists*,
*weakens*, *disappears*, *reverses*. "Weakens across conditions" is a publishable result here; it is not a
failure to be re-analysed into a stronger claim.

**Comparator discipline:** the behavioral score is compared with the strongest simple baseline on the same
withheld pairs, tuned on the declared split and taking its best score (AGENTS 11). Organica's margin is
not the claim; the relation between `DI` and the score is.

## 7. What this design does not establish

- **No causal claim.** Level 3 is a separate experiment (§1).
- **No generalization beyond the named configurations.** Three configurations are three, and the
  conditions axis is otherwise untested.
- **No average-effect claim.** A pooled statement would need the pooling rules of
  `docs/SCALING-LADDER.md` §10 and more worlds than this design proposes.
- **Nothing about intelligence**, capability, or comparison with other systems.

## 8. The review gate, and what comes before seeds

Before any seed is named, an independent reviewer must examine, and be recorded as having examined:

1. the `DI` definition and its zero-denominator policy (§2);
2. the choice of `WITHHELD` and the claim that it survives the law rotation (§4);
3. the readout and its calibration, including the smoothing constant and the seed it was calibrated on;
4. the comparator sweep and its tuning split (§6);
5. the overlap guard in §4, and whether it can fail;
6. the level discipline — that no sentence in the report can be read as causal (§1).

Until that review is recorded, this document authorises **nothing**: no seed, no run, no analysis of new
data.
