# Structure and Behavior — Design Record

**Status: design record, written before any seed is named. No seed has been allocated, no run is
authorised, and no number in this document comes from a run of this design.** It is written under the
freeze in the action list (row 13): the measurement framework is fixed, and this record may specify a
question and an analysis but may not add apparatus to answer it. Independent review is required before
seeds are named (§8), and the reviewer must not have written the estimator or selected the historical
result.

## 0. What this document is

A complete experimental protocol, written so that a reviewer who did not build these measurements can
assess it without reconstructing the project. It is **not** a paper and it reports no result. It has nine
required elements, and each has one home:

| Element | Section |
| --- | --- |
| research question and falsifiable hypothesis | §1 |
| the structural variable and how it is measured | §2 |
| the behavioural endpoint | §3 |
| estimand and statistical model | §6 |
| null hypothesis and permutation control | §6 |
| held-out transition methodology | §4 |
| sign-resolution criterion, and its computed value | §6 |
| conditions under which the hypothesis is rejected | §10 |
| what a positive result would and would not license | §7 |

**Independent pre-experiment review is not journal peer review.** The first asks whether this experiment
deserves to be run; the second asks whether a finished contribution deserves publication. This protocol
exists for the first, and a paper is a later decision that this record does not take.

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

> **2026-11-02 — the window is contested, and unresolved.** `docs/DI-CONSTRUCT-AUDIT.md` audits the
> construct from the 240 stored Phase L records. It finds `DI` to be a **state at a designated time**
> rather than a stable trait or a trajectory, and it finds that this window has **no support in the only
> per-cycle data the project holds**: applied to those records, 110–150 is pre-arrival and returns 240
> identical zeros, and the matched 40-cycle post-arrival window returns 234/240 all-zero records with an
> ICC of 0.068. The transition these records show occupies hundreds of cycles, so a 40-cycle post-arrival
> window measures the floor. **The window is therefore not fixed: it is recorded as unresolved and no seed
> is allocated.** Correcting it is an owner decision on that evidence; this note does not rewrite the
> parameter, and the independent review in §8 must be told the window is contested rather than handed this
> paragraph as settled.

Two properties are fixed, not adjustable:

- **A zero denominator is not measurable.** `late_available == 0` means the late structure was never
  available to be retained, so `DI` is reported `None` and the cell is **excluded**, never scored 0.0
  (AGENTS 13b; this is the exact defect that produced the Phase L pilot's fake `DI = 0.000` sweep).
- **`DI` is structural, not behavioral.** It counts retained gold pairs, not predictions of held-out
  events. The behavioral variable is a different measurement on different cycles (§3).

The variable is made to vary by the strength manipulation K3 already exercised: the late group's support
weight at 3:1 versus 1:3 against the early group, with `DI` the measured consequence. A design whose
`DI` values do not vary is a dead axis and stops the run before any outcome is read (AGENTS 13a).

## 2a. The closest prior result, and the noun that keeps this hypothesis open

`docs/formation_provenance_study.json` is the nearest existing test and it must be named here, because
reading it carelessly would either overstate this design or erase it.

Its confirmatory block (15 seeds, `20270106`–`20270120`, run once under a preregistration, all four gates
passed) found that the **recorded provenance of a formed candidate** is associated with whether that
candidate's asserted pair **occurs** in the window the organism was never shown:

| arm | hits | n | rate |
| --- | --- | --- | --- |
| `pair_world_attributed` | 1938 | 4280 | 0.4528 |
| `origin_includes_self` | 2036 | 8528 | 0.2387 |

Difference **0.214061**, 98.33 % interval **[0.195886, 0.228119]**, lower bound above zero; the
permutation control's interval includes zero (gate G3 passed). That is a real result and it is about
**structure and the world's later content**.

**It is not this hypothesis, and the reason is one noun.** Its outcome is *occurrence*: a property of the
event stream — did the pair appear in cycles 150–200. This design's outcome is *response*: what the
organism's readout predicts on transitions it never saw. The study's own record says the same thing in its
`does_not_establish` list, first item: *"that the knowledge is useful or reusable"*. A structure can track
what the world will contain and still not be what the organism uses when it acts; those are different
claims, and only the second one is behavioural.

So the position is:

- **structure ↔ future world content:** established once, for provenance, at candidate level, in one
  configuration (0.214, interval above zero);
- **structure → the organism's own later behaviour:** not established for any structural variable, and it
  is what §1 states;
- **stability of either across generating configurations:** not established at all.

This also sets the right expectation for the result. If `DI` predicts `revision_held_out`, the finding is
not "structure tracks the world" — that is already in the record — but "structure predicts what the
organism does", which is the sentence the project has never been able to write.

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

- **The instrument is shared, and that is a second, harder guard.** `DI` counts pairs the organism's readout
  predicted; the outcome scores what that same readout predicts. Disjoint pair sets do not make the two
  measurements independent, because one instrument produces both. Two checks are therefore required and
  reported beside the relation: a **mechanical baseline** — the outcome regressed on structural *size*
  alone (how many pairs were predicted) and on the base rate, with no reference to which pairs — which must
  not already explain the relation; and the **permutation control** in §6. A relation that survives the pair
  guard but not the size baseline is a statement about how much structure exists, not about which structure
  it is, and must be reported that way.

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

**Unit, estimator, interval.** The unit is one world (seed) within one configuration. The primary statistic is
the **Spearman rank correlation** between `DI` and `revision_held_out` across worlds in that configuration;
the **OLS slope** of standardized outcome on standardized `DI` is reported beside it as an effect size. Rank
first because the number of worlds is small and the relation need not be linear; slope second because both a
direction and a magnitude are wanted. Uncertainty comes from a 10,000-replicate bootstrap resampling worlds
within the configuration, at the project's 98.33 % level, and is reported per configuration. Nothing is
pooled across configurations into a single number.

**Decision rule, fixed before data.** *Present*: the interval excludes zero with the predicted sign.
*Absent*: the interval includes zero. *Reversed*: the interval excludes zero with the opposite sign. Across
configurations, the four pre-committed outcomes follow from those: **persists** (present with the same sign
everywhere), **weakens** (present in some), **disappears** (absent in the rest), **reverses** (reversed in
any).

**The size baseline competes with the predictor.** The same estimator is run with structural *size* (how
many pairs were predicted) in place of `DI`. If the size baseline's interval excludes zero and `DI`'s does
not survive beside it, the result is reported as a **size effect**: structure quantity, not structural
content.

**Sign resolution, computed before seeds.** The confirmatory block may not open until the
probability that it returns the relation **with the correct sign** at its planned window and number of
worlds has been computed under a named reference rule. That computation is done:
`docs/sign_resolution_structure_behavior.json`, produced by `python -m benchmarks.sign_resolution_behavior`.
No engine ran and no seed was spent.

*The reference rule is named: the smallest relation of interest.* The bar is evaluated at a rank
correlation of **0.50**, the weakest relation this design would call predictive. Carrying an
assumed effect size instead would make the answer depend on a number no artifact supplies, and would let
the block size be chosen by guessing the effect and then testing for it. Setting the reference at the
smallest effect worth detecting makes the block's size a consequence of the claim.

*The estimator is the protocol's own decision rule, simulated.* Worlds are drawn from a Gaussian copula
with the stated rank correlation; the interval is built by resampling worlds (98.33 %, the project's
convention); a block counts as resolved only when that interval excludes zero **with the predicted sign**.
Fisher's z on Spearman's rho is computed beside it as a second construction, and over six cells the two
agree to within 0.052 (Monte-Carlo standard error up to 0.028). The closed form is not doing the
work alone.

*The result.* At a true relation of 0.50, the block needs **48** worlds per configuration
to clear the 0.90 bar (p = 0.902). The full ladder is:

| True rank relation | 0.30 | 0.40 | 0.50 | 0.60 | 0.70 |
| --- | --- | --- | --- | --- | --- |
| Worlds per configuration for p ≥ 0.90 | 144 | 79 | 48 | 32 | 21 |

Read the other way: at 20 worlds per configuration the block resolves only relations of 0.70 and above; at
30 worlds, 0.60 and above. A block sized for convenience would be testing a claim nobody made.

*What this forces, and it is not a rounding decision.* Three configurations at 48 worlds each is
**144 runs**. That is the size the claim requires, and it is larger than any block this project has run.
Two ways to make it smaller exist and both are protocol changes, not choices: shrink the claim to a larger
relation (which is a different hypothesis and must be written as one), or lower the bar (which must be done
before the block opens and recorded with its own justification). Choosing n = 20 after seeing this table
would let the design pick its own effect size, which is exactly the defect §10 exists to prevent.
**No seed is allocated by this document; the block size is a decision for the record, not a parameter
of the analysis.**

*What 0.902 is, and what it is not.* It is the simulated probability that this decision rule resolves
a relation of that size, under the stated data-generating assumptions. It is not a posterior probability
that the hypothesis is true, not a p-value, not a false-positive rate, and not a property of the engine —
no engine ran. It describes the relation **as measured**, not a latent relation, and the difference is
priced in the next paragraph.

*Which way the omissions cut: 48 is a floor, not a ceiling.* Every unmodelled defect — measurement error in
`DI`, dependence between worlds — makes the real probability **lower** than the computed one. The computed
probability is therefore an **upper bound**, and the computed world count is a **lower bound on the worlds
required**: a block of 48 resolves the relation *less* often than the table says, and 48 is the least
number the claim can be tested with, not the most. An earlier version of this paragraph said "upper bound"
without saying of what, and standing next to a world count it could be read as a maximum; corrected
2026-11-02 after the owner pointed out that the direction for the count is the opposite one.

*The measurement-error assumption, stated explicitly — and the mapping is not a product rule.* No error
model is fitted. What the artifact computes is the consequence of one stated model, classical independent
error in `DI` only, and the mapping matters: under that model the **Pearson** correlation is multiplied by
`sqrt(reliability)`, and the **Spearman** value of a bivariate normal then follows from
`rho_s = (6/pi) asin(rho_g / 2)`. An earlier version of this paragraph multiplied the rank correlation by the
reliability itself, which overstates the loss at every level; the corrected curve is computed by
`observed_spearman` and checked by Monte Carlo on samples of the block's own size, agreeing to within
0.021:

| `DI` reliability | Observed relation (Spearman) | Worlds per configuration |
| --- | --- | --- |
| 1.00 | 0.50 | 48 |
| 0.90 | 0.47 | 54 |
| 0.80 | 0.45 | 62 |
| 0.70 | 0.42 | 72 |
| 0.60 | 0.39 | 85 |
| 0.50 | 0.35 | 104 |
| 0.40 | 0.31 | 131 |
| 0.30 | 0.27 | 177 |

The difference is worth naming because a reviewer will check it: the naive product rule put reliability 0.80 at
0.40 and 79 worlds, where the correct mapping for this estimator puts it at 0.446 and
62. At 0.60 it is 85, at 0.50 104, and at 0.30
177. `DI`'s reliability is measured nowhere in this project, so this is a sensitivity curve under
one model rather than a correction, and a bounded ratio like `DI` would not follow a classical error model
exactly. Measuring its reliability remains the prerequisite.



*Exchangeability, and a direction this record had asserted without testing.* The interval resamples worlds
individually, which assumes they are exchangeable draws within a configuration. Analysing each configuration
separately removes across-configuration clustering; it says nothing about dependence *within* one, which would
arrive as state carried between seeds or as worlds drawn from related conditions.

An earlier version of this paragraph claimed that such dependence **narrows** the interval and therefore only
raises the requirement. That claim was untested, and the artifact now tests it: worlds are simulated with a
shared component and resampled two ways — individual worlds, and contiguous blocks of seeds. The difference in
resolution probability (individual minus block) is +0.033, +0.000, -0.013 at intraclass correlation 0.00, 0.10 and 0.20, which
is indistinguishable from Monte-Carlo noise at 150 simulations and is not consistently signed. The honest
statement is therefore that the direction depends on the structure of the dependence and has not been
established here. The block must **measure** it rather than assume it: report the seed-generation and ordering
procedure, whether seeds are independent experimental worlds, dependence beyond lag 1, and both the
individual-world and contiguous-block intervals with the resolution probability under each.


**Falsifier A — direction.** The relation is absent or reversed *where the structure is present*: worlds
with high `DI` do not score above the comparator on the withheld transitions. This is a failure of the
hypothesis, not a failure of the instrument, provided the axis is live (§2's liveness check passed).

**Falsifier B — configuration.** The relation's **sign flips** across configurations while `DI` is
measured identically. This is the sharper outcome: it would show the behavior is driven by the generating
configuration rather than by the measured structure, and it is the result the design is built to be able
to report rather than explain away.

**Permutation control, which must fail.** `DI` is shuffled across worlds within a configuration, the slope
is refitted, and its interval must include zero — the design the formation-provenance study used for its
gate G3, where the permuted difference was 0.000359 on an interval spanning zero. A control that cannot
produce a null is decoration (AGENTS 25c), so the control's own result is reported whether or not the main
relation holds.

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
- **Not the shared instrument.** `DI` and the outcome are produced by the same readout, so the mechanical
  baseline and the permutation control *bound* that explanation rather than removing it. A fully
  independent operationalization — a different readout for the structure and for the behavior — is not
  designed here. If the relation survives both guards it is still reported as one readout predicting its
  own later output, which is weaker than two instruments agreeing.

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

## 9. Verifying this record without trusting its author

Every number quoted here comes from a committed artifact, and the claims that reading cannot settle are
checkable by running. A reviewer who does not trust this document should run exactly these:

```bash
# 1. the artifact behind 2a, printed rather than paraphrased
python -c "import json;d=json.load(open('docs/formation_provenance_study.json'));\
print(d['verdict'],d['difference'],d['interval'],d['all_gates_passed']);\
[print(k,v['hits'],v['n'],round(v['rate'],6)) for k,v in d['arms'].items()]"
```

expected:

```
association detected 0.214061 [0.195886, 0.228119] True
pair_world_attributed 1938 4280 0.452804
origin_includes_self 2036 8528 0.238743
```

```bash
# 2. the guards on this document itself
python -m pytest tests/test_structure_behavior_design.py -q
```

expected: all pass — the level wording and the causal refusal, the six required items, the windows
imported from code, no seed from an unspent block named, the prior result quoted from the artifact, the two
independence guards, this verification section, and the manual/journal cross-reference.

```bash
# 3. the text that carries the result, at the commit that committed it
git log --oneline -1 -- docs/STRUCTURE-BEHAVIOR-DESIGN.md
```

If (1) prints a number that differs from 2a, the document is wrong and the artifact is right. If (2) fails,
a guard has been broken — a required phrase removed, a seed named, or a quoted number drifted — and none of
those is excusable as a documentation slip, because they are the mechanisms by which a design record stops
being a constraint.

## 10. Rejection and acceptance, stated before any data

| Observed | Conclusion | The sentence the record may carry |
| --- | --- | --- |
| present in every configuration with the predicted sign, intervals excluding zero, size baseline and permutation both null | **supported at Level 2** | "the organism's displacement index predicts its held-out revision behavior in the configurations tested" |
| present in some configurations, absent in others | **mixed / context-limited** | "the relation is configuration-dependent in the tested set" |
| absent in every configuration | **not supported** | "no predictive relation was detected" |
| reversed in any configuration | **reversed there** | "the relation runs opposite to the hypothesis in that configuration" |
| explained by the size baseline | **size effect** | "structure quantity, not structural content, predicts the outcome" |
| permutation control non-null, or the pair overlap non-empty | **design defect** | no result is reported; the defect is the finding |
| fewer worlds than the declared minimum after exclusions | **inconclusive** | "inconclusive", never "null" |

A positive result licenses **predicts**. The words *causes*, *produces* and *drives* are reserved for a
Level 3 design and may not appear in the result's summary or abstract.
