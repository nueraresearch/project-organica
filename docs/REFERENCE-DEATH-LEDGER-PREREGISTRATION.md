# Reference-arm death ledger — pre-registration

<!-- reference-death-ledger
executions: 1
-->

**Status:** the protocol below is frozen before the first cell. Date 2026-11-07, engine
0.13.0, Q042. Nothing in sections 1–8 is edited after the run; the outcome is section 9
and any correction is a dated appendix.

## 1. Question and unit of measurement

Q042 asks whether reference-arm death is itself the dominant failure mode of 0.13.0. Three
observations point that way — the degree-12 ceiling peaks at 0.5833 and ends at 0.00 at
every budget tested, the falsifier's reference arm is dead by cycle 38 of 300, and raising
the theory budget moves neither the peak nor the endpoint — but no artifact counts the
removal events per cycle and attributes each one to a mechanism. The claim is therefore a
pattern, not a measured share.

The unit of this ledger is a **removal event**: one identifier that was in the previous
cycle's retained population and is absent from this cycle's retained population. It is
not a distinct object. A theory that disappears, returns, and disappears again contributes
two removal events, because the question is how often the layer loses what it had, not how
many unique things it ever lost.

The reference arm is `FULL`, the unablated shipped service with alphabetical hypothesis
retention. **Reference removals** are removal events in that arm. **Other removals** are
removal events in the five ablation arms (`SALIENCE`, `NO_CONTRADICTIONS`, `NO_QUESTIONS`,
`NO_DREAMS`, `ANTI_EIG`) on the same seeds and settings. Both layers are recorded: beliefs
(the hypotheses formed and retained each cycle) and theories (formed from those hypotheses).

## 2. Setting

Six arms × three seeds × 300 cycles on the falsifier's own stimulus, `lattice_L1` (three
disjoint triangles), built exactly as `benchmarks/force_matrix.py` builds it. The engine is
unchanged; instrumentation is in-process subclassing only, as the force-matrix campaign
already does. Seeds are the previously unused block 20302001–20302003. The control seed is
20261023, whose reference-arm series is already committed in
`docs/decay_falsifier/parts/FULL.json`.

## 3. What counts as a death

For each cycle the ledger reads the engine's own inputs and outputs: the hypotheses formed
before retention, the hypotheses retained (the theory layer's input), and the theories that
result. A belief or theory present in the previous cycle's population and absent from this
cycle's is a removal event. Births are recorded separately and never netted against
removals: a cycle that loses three and gains three is one cycle with both, not a zero.

A theory's death is not the disappearance of a stored row — theories are re-formed each
cycle — so its death means the pipeline stopped producing it. That is exactly the quantity
the falsifier's series reports, which is why the same series is the control.

## 4. Mechanism vocabulary

Every removal event receives exactly one reason from a closed vocabulary. The attribution
uses only quantities the engine already exposes, and the order below is the order of
precedence.

**Belief removal**

- `capped` — the belief was formed this cycle but not retained (the 15-hypothesis cap or
  the arm's retention policy removed it).
- `not_reformed` — the belief was not formed this cycle at all; its supporting structure was
  no longer present.

**Theory removal**

- `superseded` — the subject still has a theory this cycle, but under a different id (the
  competing hypotheses or their order changed, so the identifier changed).
- `parent_loss` — at least one parent hypothesis is no longer in the retained belief set.
- `competing_collapse` — fewer than two retained hypotheses remain for the subject, so no
  theory can be formed.
- `capped` — the subject still has enough support and a theory was formed, but the layer is
  at its 8-theory cap and support ranking displaced this one.
- `unexplained` — none of the above holds. This is the ledger disagreeing with the engine,
  and it is reported, never absorbed.

## 5. Gates

The label is read only if all five gates pass. A failed gate returns `UNMEASURABLE` and no
scientific claim.

- **G1 — neutral observer.** The ledgered reference arm at seed 20261023 reproduces the
  committed falsifier's theory series and belief series exactly, element for element. The
  observer must not change behavior.
- **G2 — attribution completeness.** `unexplained` is at most 5 percent of the reference
  arm's theory removals, and the reference arm records at least one theory removal.
- **G3 — live axis.** At least one ablation differs from the reference in its per-seed death
  cycles or its mechanism counts. If all six arms are identical, the ledger cannot attribute
  reference-specificity and the campaign is not measurable.
- **G4 — denominators.** All 18 cells record 300 cycles, and the reference arm has at least
  10 theory-bearing cycles in every seed.
- **G5 — seed independence.** The seed block is absent from every artifact under `docs/`
  before this run.

## 6. Decision table

For each arm, its **death cycle** is one past its last cycle with at least one theory; an arm
that never forms a theory dies at cycle 1. Per arm, the median across the three seeds is used.
With `ref` the reference median and `others` the five ablation medians:

- `lead = ref − min(others)` — how many cycles earlier the earliest ablation dies.
- `lag = max(others) − ref` — how many cycles later the latest ablation dies.

`MARGIN = 10`. The margin is fixed from the reference's recorded 37-cycle theory lifetime
(last non-zero at cycle 38) in the falsifier artifact, which is not one of the seeds being
judged; it is about a quarter of that lifetime, so a difference smaller than it is within the
reference's own early transient.

| Label | Condition, evaluated in this order | Decision it licenses | Q042 |
| --- | --- | --- | --- |
| `UNMEASURABLE` | any gate fails | Build the missing denominator or observer check; claim nothing about the failure mode. | Stays open |
| `ABLATION_DOMINANT` | `lead >= 10` | The earliest death is an ablation's, so reference death is not the dominant failure mode; the reference is the comparatively healthy case and the ablation is the object of study. | `UNSUPPORTED` |
| `REFERENCE_DOMINANT` | `lag >= 10` | The reference's own configuration dies at least 10 cycles before every ablation; the retention policy is the first thing to fix, before any ablation question. | `SUPPORTED` |
| `SHARED_DOMINANT` | otherwise | Death is the shared mode: every arm dies within the margin, so the lever is the common belief-formation and decay substrate, not any arm's policy. | `SUPPORTED` (shared, not reference-specific) |

The rows are exhaustive and ordered: a straddle in which one ablation dies early and another
late is `ABLATION_DOMINANT`, because the reference is not the first to die.

## 7. Predictions

- **P1.** Every arm reaches zero theories before cycle 300.
- **P2.** Every ablation's death cycle is within `MARGIN` of the reference's.
- **P3.** The reference arm's modal theory-removal mechanism is `parent_loss`.
- **P4.** The reference arm records zero `unexplained` theory removals.

Predictions are recorded and reported whether or not they hold; the label comes from the
table in section 6 and is not re-read to fit them.

## 8. Scope and limits

One synthetic world family at one stimulus, 300 cycles, six arms of one engine. The ledger
measures formation-based death: a theory that fails to be re-formed is dead even if nothing
deleted a row. It cannot see why an edge failed to form, only that the belief carrying it was
not formed; the decay-attribution study is the instrument for that layer. Removal shares are
event shares, not population rates, and the two are reported side by side. No arm is
intervened on after the fact, so the ledger is observational: it attributes removals to the
mechanism visible in the engine's own state, not to a counterfactual cause.

## 9. Outcome

**Measured 2026-11-07: `SHARED_DOMINANT`.** 18 cells (6 arms x 3 seeds 20302001-20302003 x 300 cycles) plus the seed-20261023 neutrality control, on the falsifier's `lattice_L1` stimulus, engine 0.13.0. The artifact is `docs/reference_death_ledger.json`; sections 1-8 hash to `9005e175d7a958425ff6e5557b2dd6e355f0d7ffc6e0007fb7d21520a8ccd19e`.

**Completion note.** The first measurement was interrupted by a runner restart after all 18 cells had written their parts and before the control and the artifact. The campaign was completed with `--finish`, which reuses those 18 parts unchanged and ran only the control; the artifact records `resumed_from_parts: true`. No cell was rerun, replaced or dropped.

**Gates.**

| Gate | Result |
| --- | --- |
| G1_neutral_observer | pass |
| G2_attribution_complete | pass |
| G3_axis_live | pass |
| G4_denominators | pass |
| G5_seed_independence | pass |

The control is exact: the ledgered reference arm at seed 20261023 reproduces the committed falsifier's theory series (match) and belief series (match), with no first mismatch.

**Predictions.**

| Prediction | Result |
| --- | --- |
| P1_every_arm_dies_before_end | held |
| P2_every_ablation_within_margin | held |
| P3_reference_modal_parent_loss | failed |
| P4_no_unexplained_in_reference | held |

P3 is the one that failed, and it matters. The pre-committed prediction was that the reference's modal theory removal would be `parent_loss`; it is `superseded` (102 of 126 reference theory removals), with only 24 `parent_loss`, 0 `capped` and 0 `unexplained`. Most of the reference arm's disappearance events are identifier churn in which the subject keeps a theory, not a lost parent. The ablation arms are the other way round: each is `parent_loss`-dominated (249) and records 300 belief removals under the cap, against 30 capped belief removals in the reference.

**Death cycles.**

| Arm | Per-seed death cycle | Median | Theory removals |
| --- | --- | --- | --- |
| FULL | 39, 39, 39 | 39 | 126 |
| SALIENCE | 39, 39, 39 | 39 | 354 |
| NO_CONTRADICTIONS | 39, 39, 39 | 39 | 357 |
| NO_QUESTIONS | 39, 39, 39 | 39 | 354 |
| NO_DREAMS | 39, 39, 39 | 39 | 354 |
| ANTI_EIG | 39, 39, 39 | 39 | 354 |

**Mechanisms (theory removals).**

| Arm | superseded | parent_loss | competing_collapse | capped | unexplained |
| --- | --- | --- | --- | --- | --- |
| FULL | 102 | 24 | 0 | 0 | 0 |
| SALIENCE | 105 | 249 | 0 | 0 | 0 |
| NO_CONTRADICTIONS | 102 | 255 | 0 | 0 | 0 |
| NO_QUESTIONS | 105 | 249 | 0 | 0 | 0 |
| NO_DREAMS | 105 | 249 | 0 | 0 | 0 |
| ANTI_EIG | 105 | 249 | 0 | 0 | 0 |

Every arm's theory layer dies at cycle 39, so the timing is shared to the cycle and the label is the table's `SHARED_DOMINANT`: reference-arm death is not a distinct failure mode. The reference arm accounts for **126 of 1899** theory-removal events (**6.64 percent**); the route differs even though the timing does not. `unexplained` is 0 in the reference arm, so the attribution is complete.

**Q042.** `SUPPORTED`. Yes, but shared: every arm's theory layer dies within the margin, so death is the system's dominant failure mode and the lever is the common belief-formation and decay substrate, not any arm's policy.

The ledger's unit is a removal event, so a superseded theory counts as a death even though its subject remains covered; the mechanism table is what separates that churn from a genuine parent loss. The table was applied once, no band was moved, and the run's own numbers did not change a threshold.

## 10. Amendment, 2026-11-07 (wording only; no threshold moved)

Section 6's closing sentence says a straddle is `ABLATION_DOMINANT` "because the reference is not the first to die". Read literally, that would make a one-cycle difference an ablation lead and would contradict the margin the table uses. The rows are the decision rule: `lead >= 10` is a lead and `lag >= 10` is a lag; a straddle beyond the margin on both sides fires the first row, and a difference smaller than the margin is not a lead at all. This clarifies the sentence, changes no threshold, and changes no label for this run because every arm died at cycle 39.
