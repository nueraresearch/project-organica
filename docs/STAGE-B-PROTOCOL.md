# Stage B — protocol, complete draft for independent methods review

**Status: DRAFT PROTOCOL FOR REVIEW. Stage B is not authorised.** No seed is allocated, no world is generated
and no run is authorised by this document. Every number here is written by
`benchmarks/stage_b_protocol.py` into `docs/stage_b_protocol.json`, and `tests/test_stage_b_protocol.py` asserts
this document against that artifact.

This is the experiment the construct record was preparation for. `docs/DI-TRANSITION-CONSTRUCT.md` fixed *what
onset means*; this document specifies *what would be done with it*, and it reopens nothing it inherits. Where a
parameter comes from the construct record it is cited rather than restated, because a protocol that copies a
constant is a second place for it to drift.

**One thing this document cannot say, and does not:** whether the relation exists. **No relation between onset
and behaviour has been computed** — not on the 240 stored records, not on any new world. That is the design's
central discipline: the predictor was fixed on measurement grounds precisely so that this study could test it
without first having to decide what it means while looking at the outcome.

---

## 1. Primary hypothesis and estimand

> **Within a generating configuration in which sustained structure emerges, worlds whose `DI` emerges earlier
> behave differently afterwards — in the direction that structure available earlier supports later revision.**

| element | value |
| --- | --- |
| level | **2 — prediction**, not causation |
| unit of analysis | one world (seed) within one configuration |
| predictor | confirmed onset of `DI`, in cycles |
| outcome | `revision_held_out`, the held-out next-tag score after learning |
| estimand | the within-configuration rank relation between onset and that score |
| populations claimed | the four configurations that produce sustained structure: `2:1`, `3:1`, `4:1`, `6:1` |
| populations not claimed | `1:1`–`1:4`, where the quantity is not produced (construct record §3.3) |

**Level 2 is a ceiling, not a modesty.** Nothing here manipulates the structural variable: onset is measured from
the formation phase, and the behaviour is scored later in the same run. A positive result licenses *predicts*.
The words *causes*, *produces* and *drives* are reserved for an in-process arm that changes the structural
quantity and nothing else, which is not designed here.

**The direction is stated in advance so that a reversal is a result.** "Behaves differently" is not a
direction; the predicted one is that earlier confirmed onset predicts a **higher** held-out score after
learning, on the reading that structure available earlier is structure that can be revised with. A relation of
the opposite sign is pre-committed as **reversed** — a stronger statement than unsupported — and is not
re-described as noise.

---

## 2. The predictor and eligibility: inherited, frozen, not re-chosen

The predictor is fixed by the construct record and is **not** a parameter of this protocol:

| property | value | source |
| --- | --- | --- |
| the event | first cycle of the qualifying sustained run, confirmed at the 10th consecutive non-zero reading | construct §3.1 |
| sustention rule | **10** cycles, frozen before the run | construct §3.2 |
| availability | the confirmation cycle; the predictor does not exist before it | construct §3.1 |
| eligibility | onset defined in **≥ 90 %** of a configuration's runs | construct §3.3 |
| resolution | within-configuration SD **≥ 3 cycles**, with IQR, range and distinct values beside it | construct §3.4 |

Stage B **re-verifies** both eligibility criteria inside every claimed configuration on its own worlds before
any relation is estimated. The values below are from the Phase L record and are the *expectation*, not a
substitute for the check:

| configuration | defined share (Phase L) | onset SD (cycles) | median onset | worlds planned |
| --- | --- | --- | --- | --- |
| `2:1` | 0.967 | 27.3 | 539 | 104 |
| `3:1` | 1.000 | 25.1 | 404 | 104 |
| `4:1` | 1.000 | 19.3 | 362 | 104 |
| `6:1` | 1.000 | 12.4 | 329 | 104 |

A configuration that fails either criterion on its own worlds is **out of scope and reported as such** — a world
property, never a null about the organism. It does not rescue the claim and it does not sink the others; §5's
aggregation rule decides what remains.

---

## 3. The behavioural endpoint

**`revision_held_out`** — next-tag prediction on the revision-test window under the rotated law, restricted to
transitions withheld from **both** formation and revision learning, scored by the calibrated readout with **no
refit during evaluation**. The definition is inherited from `docs/STRUCTURE-BEHAVIOR-DESIGN.md` §3.

It is named for what it measures: *next-tag prediction on transitions the organism never saw and could not have
learned from either exposure window*. It is not a measure of belief revision in any semantic sense, and it is
not "understanding". The project's belief-revision task returned REVERSED (0.4111 against 0.9846); this endpoint
is deliberately a different one, and a positive result here does not repair that one.

**Where the endpoint is defined in code, so a reviewer can read it rather than trust this paragraph:**

| question | where it is answered |
| --- | --- |
| what is scored | `benchmarks/reusable_knowledge.py` — `revision_held_out`, and `held_out['revision_held_out_pairs']` |
| which transitions are withheld | `benchmarks/reusable_knowledge.py` — the `WITHHELD` set of cell transitions, selected inside `limbs()` by `held_only()`. This is the rule the endpoint is scored under |
| whether the count is non-zero before a cell is scorable | the `E6` gate in `benchmarks/reusable_knowledge.py`, which requires `revision_held_out_pairs > 0` |

**Two corrections to that table, from the machine pre-pass (`docs/AI-REVIEW-2026-11-02.md`, rubric 3).** The
"which transitions are withheld" row previously named `formation_provenance_study.py`'s `held_out_pairs()` and
`PHASE_TRANSFER`. That helper returns *its own study's* observed ordered tag pairs from the transfer phase; it is
not the withholding rule the endpoint is scored under, and a reader sent there reads the wrong selector. And
`limbs()` selects by **fixed phase indices**, while Stage B's window is positioned relative to each world's
confirmed onset — the rule is the same one re-parameterised, but disjointness for the onset-relative window is
established by the pre-run enumeration, not by reading the calibration code.

**A resolution requirement gates the run, and it is stated as a requirement rather than a number** because the
number depends on a withheld set that does not exist yet. Before any world is generated, the harness must report
the endpoint's **scale**, the **count** of held-out transitions per world, and a **per-world standard error**
measured by resampling that world's withheld transitions — the count alone does not buy it (§3.1). If twice a
world's standard error exceeds the smallest effect this protocol asserts, the endpoint cannot separate two worlds
the claim distinguishes, the design is unmeasurable for its own claim, and the run does not start (AGENTS 13). This is not a documentation detail: it
determines whether the experiment can measure its stated outcome at all, and it is the check that would have
caught the Phase L design defect before the campaign.

### 3.1 What the endpoint's scale is, and what the withheld count buys

**A correction first, because the previous version of this section described an endpoint this protocol does not
use.** It said that "the outcome is a proportion over the withheld transitions, so the endpoint's quantum is one
divided by that count", and printed a quantum of **0.009434** with **107** distinguishable levels. The endpoint is
not a proportion: `benchmarks/acquisition_compositional.py`'s `score()` computes a **pairwise binary log loss**
over each context source crossed with the vocabulary and averages it, and `benchmarks/reusable_knowledge.py`
scores `revision_held_out` with that function. The machine pre-pass named this as a blocking defect
(`docs/AI-REVIEW-2026-11-02.md`, rubric 1 and the §10 endpoint question), and it is right: a log loss has no
`1/count` lattice of outcome levels, so both figures are **withdrawn** and no resolution argument rests on them.

**What the count is still good for.** A world's score is a mean over its withheld cells, so the count is the
denominator of that mean: it sets the **precision** of a per-world reading, not the number of representable
levels. Measured on the design-block cells already in the record:

| quantity | value |
| --- | --- |
| withheld transitions per world | **82 to 110**, median **106** |
| endpoint scale | mean pairwise binary log loss, in nats per scored cell |
| effect gap assumed at ρ = 0.50, across-world SD 0.05 | **0.05** |

**The gap is a model, not an identity.** `2 × 0.50 × 0.05` is the expected difference in **nats** between two
worlds two across-world SDs apart in onset, and it holds only under three stated conditions: the relation is linear
in standardised units, the across-world SD of the endpoint is 0.05, and ρ = 0.50 is read as the correlation between
onset and *this* score. A Spearman coefficient does not imply that contrast on its own — which is the second
pass's point (`docs/AI-REVIEW-2026-11-03.md`, finding 3) — so the artifact now carries the three conditions beside
the number instead of presenting it as derived.

**And the count is not a count of independent contributions.** `score()` averages pairwise binary log loss over
every context source crossed with the vocabulary, so one withheld transition contributes many correlated cells. The
transition count is the **denominator** of a per-world mean and an **upper bound** on its precision, not a
measurement of it. The previous version of the table above divided the SD of scored cells by `√cells` and read the
result as a per-world standard error; that substitution is **withdrawn**, because the cells are nested and the
scorer returns neither a per-world SD nor a per-world SE.

**The standard error has now been measured, on the cells that exist.** `benchmarks/stage_b_endpoint_precision.py`
bootstraps **transitions**, not cells — each withheld transition moves its whole set of cells — and reports the
standard deviation of the world's mean. On the five design-block cells twice that standard error is
**0.009 to 0.011 nats** at the exact latent rule and **0.059 to 0.071** at the wrong-law control, against the 0.05
gap (`docs/stage_b_endpoint_precision.json`). The bracket **straddles** the gap, and that is the finding rather than
an inconvenience: precision depends on the readout's loss distribution, so whether 82–110 transitions suffice is
decided by a distribution that does not exist until a world runs. The method is discharged; the gate is not.

What can no longer be claimed is that a **5.3-quantum** margin shows the endpoint resolves the effect — or that a
`√N` calculation shows it does not. Two things are true instead: the score is continuous, so quantization is not
the binding constraint, and whether the score moves across worlds, and how noisily, is a question only the run
answers.

**The gate therefore stays open, with four rules attached, restated on the scale the endpoint actually has:**

| failure | rule |
| --- | --- |
| **too coarse** | twice a world's standard error of the endpoint larger than the effect gap at the declared smallest effect is a design defect and the run does not start — but that standard error must be **measured** by a cluster bootstrap over the world's withheld transitions, so **this rule cannot be evaluated before the run** and is not claimed to pass |
| **too sparse** | fewer than half the planned worlds at 40 or more withheld transitions is a design defect, and the run does not start |
| **saturated** | a configuration whose realised **across-world SD is below twice the median per-world standard error** is unmeasurable there: excluded and reported, never scored as a null — answered from the run's measured precision, not from the count |
| **undefined** | zero withheld transitions is excluded by the existing `E6` gate, and never scored as zero (AGENTS 13b) |

`resolution_confirmed` stays **false**, and `status` now reads **open** rather than *informed*: two of the four
rules consume a per-world standard error that cannot exist until a withheld set does, so the state before the run
is **undetermined**, not passed. These numbers *inform* the gate; the enumeration for the four claimed
configurations **is** the gate, it runs before any world does, and §5 now requires it to report the measured
precision those two rules consume.

---

## 4. Run horizon and the follow-up clock

| element | value |
| --- | --- |
| post-confirmation margin | **1 cycle** — the earliest legal cycle |
| learning | 50 cycles |
| held-out test | 50 cycles |
| follow-up | **100 cycles**, identical in every world |
| first behavioural index | confirmation index + 1 |
| last behavioural index | confirmation index + 100 |
| horizon per world | **confirmation index + 101 readings** |
| reported per observation | absolute cycle **and** cycles since confirmation |

**The horizon is per world, and that is a criterion, not an implementation detail.** A fixed horizon that ends
mid-follow-up fails criterion 4 rather than shortening the follow-up, because a shortened follow-up would be
shortest for exactly the worlds that emerged latest — the worlds a late-emergence relation is most informative
about. This is the Phase L defect (late structure arriving after the run ended) in a form the design would
choose rather than suffer.

**Both clocks are recorded.** Behavioural opportunity is equalised — same margin, same phases, same duration.
Developmental age at which the window opens is not, and is reported. In the Phase L record the first behavioural
index ranges 299–599; the claim is about behaviour over a fixed window *after emergence*, so the window follows
the event. A result may be stated in one clock; it may not be stated in both.

---

## 5. Configuration-specific analysis

| element | specification |
| --- | --- |
| unit | one world (seed) within one configuration |
| primary statistic | **Spearman rank correlation** between onset and `revision_held_out` |
| effect size beside it | OLS slope of standardised outcome on standardised onset |
| interval | percentile bootstrap resampling **worlds within the configuration**, 10,000 replicates, **98.33 %** |
| pooling | **none.** Every configuration is reported alone; no pooled coefficient may be quoted as the finding |
| permutation control | onset shuffled across worlds within the configuration; the interval must include zero |
| size baseline | the same estimator with structural *size* in place of onset, reported beside it |

**Aggregation rule, fixed before any world is generated:** the construct is supported only if the predicted
relation holds with an interval excluding zero in **every** claimed configuration. Holding in some and not others
is reported as **mixed** and is **not supported as stated**. This is stricter than "any configuration" on
purpose: a protocol that could report whichever configuration performed best would be choosing its population
after seeing the outcome, which is the same defect as choosing the predictor after seeing the outcome.

**Reported per configuration, beside the relation:** the two measurement criteria, the onset distribution
(median, SD, IQR, range, distinct values), the realised denominators including every censored world, the size
baseline, and the permutation control's own result whether or not the relation holds.

**Shared instrument, stated rather than hidden.** Onset and the outcome come from one engine and one readout.
The size baseline and the permutation control *bound* that explanation; they do not remove it. A relation that
survives both is still one instrument predicting its own later output.

---

## 6. Sample size, and the reliability this protocol does not have

The block is a consequence of the claim. Three numbers are fixed: the smallest relation worth calling
predictive (**0.50** rank correlation, in observed units), the decision level (**98.33 %**, the project's
convention) and the bar a block must clear (**90 %** of blocks must resolve a relation of that size).

The count is solved from the decision rule itself — a rank correlation whose interval must exclude zero with the
predicted sign. At effect 0.50 and full reliability that gives **48 worlds per configuration**, which is the
published sign-resolution floor for this endpoint; the closed form reproduces it exactly, which is what licenses
using the same form for every other row.

### 6.1 Onset has no reliability estimate, and the protocol does not pretend otherwise

An earlier draft of this section treated the construct record's **0.972** sustention-rule agreement as a
reliability coefficient and sized the block at **54** worlds per configuration. **That is withdrawn in place, and
it was wrong for a reason worth stating precisely.**

The 0.972 is the rank correlation between onset measured under a 5-cycle and a 20-cycle sustention rule. It
establishes something real: **the ordering of worlds is robust to the sustention rule**, so the predictor's
ranking does not depend on the declared 10-cycle choice. It does **not** establish reliability, because the two
measurements come from the same trajectories, share nearly all their measurement information, and differ in
operational definition rather than through independent random error. It bounds only the rule-choice component of
measurement error — not the reliability of onset. Using it as a reliability coefficient required an unjustified
substitution, and it is **not used in the block-size arithmetic** (`sustention_rule_agreement.used_in_the_block_size`
is `false` in the artifact).

A reliability coefficient is also not obtainable by the usual route here: the engine is deterministic per seed,
so re-running a world is not a replication and there is no test–retest estimate to be had. **The protocol
therefore declares an assumption instead of inferring one**, prints the whole ladder so the assumption can be
replaced rather than argued, and sizes the block at the conservative end.

### 6.2 The ladder, and the declared assumption

| reliability assumed | observed relation | worlds per configuration | worlds total |
| --- | --- | --- | --- |
| 1.00 | 0.5000 | 48 | 192 |
| 0.90 | 0.4738 | 54 | 216 |
| 0.80 | 0.4462 | 62 | 248 |
| 0.70 | 0.4169 | 72 | 288 |
| 0.60 | 0.3855 | 85 | 340 |
| **0.50 (planning assumption)** | **0.3515** | **104** | **416** |
| 0.40 | 0.3140 | 131 | 524 |
| 0.30 | 0.2717 | 177 | 708 |

The mapping is the one `docs/STRUCTURE-BEHAVIOR-DESIGN.md` §6 established: the latent correlation is attenuated
by `√reliability` and mapped back to Spearman, `ρ_s = (6/π)·asin(ρ_g/2)`. That document's table displays the relation rounded to two decimals, and recomputing from the unrounded
mapping reproduces its world counts at **every** row exactly -- 48, 54, 62, 72, 85, 104, 131 and 177. That
agreement is a check on both documents rather than a coincidence: if either the mapping or the rounding had
drifted, these rows would disagree, and the test asserts every one of them against the artifact.

**The planning assumption is 0.50, and the reason is not convenience.** No reliability estimate exists, so the
honest choice is the weakest predictor still worth testing: at 0.50 the measure carries as much signal as error,
and below it the construct would not be worth a run. Sizing at that end means the block cannot be accused of
assuming a good instrument. If the reviewer accepts a higher reliability, the block shrinks: **0.70 gives 288
worlds in total**, and that substitution is a reviewer decision recorded in §7 of the review, not an author's
convenience.

**What 0.50 is not.** It is a **declared planning assumption, not an established lower bound**. The argument
that reliability below 0.50 leaves more error than signal is a statement inside the assumed model; it does not
establish that onset's true reliability is at least 0.50, because that quantity is unmeasured. So **104 worlds
per configuration is the requirement conditional on this assumption** — not a demonstration that the experiment
has adequate resolution under the actual measurement properties. The reviewer may reject the assumption without
proposing a replacement, and the ladder gives the consequence of every row so that rejection is a recorded
change rather than a negotiation.

**The count is a floor, not a budget.** Unmodelled dependence between worlds and any further measurement error
lower the real resolution probability, so 104 is the least number this claim can be tested with, not the most.

### 6.3 The ladder is a closed form; the analysis is not

The rows above are Fisher's z. §5 builds the interval by **resampling worlds**, and those are different
constructions — so the ladder's resolution claim is now checked by simulating the committed rule at its own
points (`benchmarks/stage_b_resolution_simulation.py`, artifact `docs/stage_b_resolution_simulation.json`). The
machine pre-pass asked for exactly this (rubric 4) and was right that no such check existed.

| reliability row | worlds | Fisher's z | committed bootstrap |
| --- | --- | --- | --- |
| 1.00 | 48 | 0.9018 | 0.863 (SE 0.017) |
| 0.90 | 54 | 0.9005 | 0.845 (SE 0.018) |
| 0.80 | 62 | 0.9020 | 0.902 (SE 0.015) |
| 0.70 | 72 | 0.9022 | 0.890 (SE 0.016) |
| 0.60 | 85 | 0.9011 | 0.887 (SE 0.016) |
| **0.50 (planning)** | **104** | **0.9026** | **0.895 (SE 0.008)** |
| 0.40 | 131 | 0.9004 | 0.887 (SE 0.016) |
| 0.30 | 177 | 0.9002 | 0.905 (SE 0.015) |

**What that shows, and what it does not.** The closed form is optimistic at six of the eight rows, and it has to
be: every row's `n` was solved to put Fisher's z at 0.90, so the ladder is a statement about the closed form, not
about the rule the analysis runs. The gap is widest where the block is smallest — at the 48-world floor the two
constructions sit **0.039** apart, about **2.3** Monte-Carlo standard errors — and it points the same way almost
everywhere, which is a property of the estimator rather than of one cell.

**It does not, however, choose a block size.** Each row carries the Monte-Carlo standard error of its own share,
and against that error the bar is not separable at the planning row: 104 gives **0.895 ± 0.008**, which is
**0.7 SE below** 0.90, while 112 gives **0.914 (SE 0.010)** and 120 gives **0.931 (SE 0.009)** — **1.4 SE and
3.6 SE** above it. So of the three sizes the simulation separates only 120 from the bar; 104 and 112 are each
consistent with a design that clears it and with one that does not, and they are consistent with each other. The second pass made this point
(`docs/AI-REVIEW-2026-11-03.md`, finding 2) and it is right: the simulation prices the sizes and establishes a
direction of bias in the closed form, but on its own precision it cannot certify that 104 fails or that 112
passes.

**One limitation is withdrawn rather than repeated.** The artifact first said that using 300 bootstrap replicates
against the protocol's 10,000 made the measured share *slightly conservative*. Nothing in the artifact supported
that: at the 98.33 % level the lower edge is the **3rd smallest of 300** replicates where the protocol's 10,000
give the **84th of 10,000**, and the direction of the resulting bias in the resolved share was never measured. The
artifact says that instead, and the numbers above carry the unknown with them.

**What that does not license.** 104 is not silently increased here. Moving it re-derives the published ladder —
the 48-world floor included — which is a change to the design record, not an erratum in this protocol. The same
rule prices the alternative: **112 worlds gives 0.914 (SE 0.010)** and **120 gives 0.931 (SE 0.009)** — 120 clear
of the bar, 112 not separable from it. Choosing between 104 at the edge, 112 with clear, and leaving the published construction alone
is a decision for the owner at step 2 of `docs/DECISION-STAGE-B-SEQUENCE.md`; it is recorded here as **open**, not
resolved by this document.

### 6.4 Cost

| configuration | median confirmation | horizon per world | worlds | cycles |
| --- | --- | --- | --- | --- |
| `2:1` | 548 | 649 | 104 | 67,496 |
| `3:1` | 413 | 514 | 104 | 53,456 |
| `4:1` | 371 | 472 | 104 | 49,088 |
| `6:1` | 338 | 439 | 104 | 45,656 |
| **total** | — | — | **416** | **215,696** |

That is **1.4979** of Phase L's 144,000 cycles for a block of 416 worlds. The figure is *higher* than Phase L
despite the per-world saving, because the block is now four times the size the withdrawn 54-world figure implied
— which is the cost of not assuming a good instrument. The estimate uses Phase L's median confirmation per
configuration as the guess at where fresh worlds will emerge; it is an estimate and is labelled as one.

---

## 7. Falsifiers and pre-committed outcomes

Written before any world is generated:

1. **Absence.** A within-configuration interval containing zero in any claimed configuration leaves the construct
   unsupported. It is not "weakly supported" and it is not rescued by another configuration, by the pooled
   relation, or by re-reading the claim.
2. **Reversal.** A relation of the opposite sign is recorded as reversed — stronger than unsupported — and is
   reported as such in the headline, not in a footnote.
3. **Dead configuration.** Onset undefined in most runs of a configuration is a property of that world under this
   rule (AGENTS 13a), reported as out of scope and never as a null about the organism.
4. **Pooled only.** A relation that appears across configurations but not inside one does not answer the
   protocol's question and does not support the construct.

| observed | outcome | the sentence the record may carry |
| --- | --- | --- |
| predicted sign, interval excluding zero, in every claimed configuration; size baseline and permutation both null | **supported** | "earlier confirmed emergence predicts the held-out score within the configurations tested" |
| present in some, absent in others | **mixed** | "the relation is configuration-dependent in the tested set"; not supported as stated |
| absent in every configuration | **not supported** | "no predictive relation was detected" |
| reversed in any configuration | **reversed** | "the relation runs opposite to the hypothesis in that configuration" |
| explained by structural size | **size effect** | "structure quantity, not onset, predicts the outcome" |
| permutation non-null, a predictor built from behavioural cycles, or an endpoint that cannot resolve the effect | **design defect** | no result is reported; the defect is the finding |
| fewer usable worlds than the floor after censoring | **inconclusive** | "inconclusive", never "null" |
| the reviewer or the power computation concludes the block is too small | **underpowered for the claim** | a design limitation found before any cycle is spent, not a failure of the project |

A **rejection** of the construct is a result of the design and is not renegotiated into a smaller claim in a
later edit. The record keeps the rejection and the reason.

---

## 8. Missing, censored and ineligible worlds

| case | treatment |
| --- | --- |
| a run whose onset is censored (fewer than 10 readings since its last zero at the record's end) | reported as censored, **excluded** from the relation, never scored as a late onset |
| a run with no non-zero reading at all | reported as censored; it is a world property under this rule, not a null |
| a missing reading inside a run | breaks the run; it is never read as non-zero |
| a configuration below the 90 % defined share | out of scope, reported, not dropped from the accounting |
| a world whose usable n falls below the 48 floor after censoring | the configuration is **inconclusive** |
| a censored world | **not replaced**. The denominator is reported as realised, so the block size cannot drift upward by attrition |

The last row decides whether the study can be trusted: replacing censored worlds is how a block of 104 quietly
becomes a search for 104 that worked.

---

## 9. Separation from previous experimental blocks

- **Fresh worlds.** Stage B generates new worlds from the frozen engine at the same four sweep points. **No
  Phase L record is reused.** The 240 stored records are the source of the *measurement audit*, not evidence for
  this claim.
- **Disjoint seeds, proved rather than asserted.** The candidate block is **700000001**–**700000420**: **420**
  integers, chosen as a plain block rather than a date-like one so that no reader mistakes it for calendar
  values. At build time the protocol scans every artifact in `docs/` for integers filed under a key naming a seed
  and compares: **192** consumed seeds across **71** artifacts, and **0 overlap** with the candidate block.
- **Pre-assigned, with the spares named.** The **416** worlds are assigned to configurations *before* any run —
  **104** each, in four contiguous ranges recorded in the artifact — and the remaining **four** seeds
  (`700000417`–`700000420`) are recorded as **unused**. **Substitution is prohibited**: a censored world does not
  release its seed to another world, and the four spare seeds are never drawn. Without that rule the difference
  between 416 planned worlds and 420 candidate seeds would be an ambiguity in the attrition policy rather than a
  margin.
- **The candidate block is not an allocation.** It is proved *unused*, which is not the same as *spent*. No seed
  in it is allocated by this document.

**Three words, defined so they are never used as synonyms:**

| word | means |
| --- | --- |
| **pre-assigned** | mapped to a configuration in this protocol, in advance, with a specific seed. It is a *plan*: no world runs on it and nothing is spent until the review records an outcome |
| **allocated** | released for an *executed* run. No seed is allocated by this document |
| **reserved** | deliberately not used: the four spares are reserved and never drawn, and a censored world does not release its seed |

That distinction is what lets "the 416 worlds are pre-assigned" and "no seed is allocated" both be true, and
saying it once here is cheaper than a reviewer having to decide whether the protocol contradicts itself.
- **The engine is the frozen one.** Organica 1 at `v0.9.0`, unchanged, enforced by `tests/test_v1_freeze.py`.

---

## 10. What the reviewer decides, and what they must be shown

The gate is `docs/INDEPENDENT-METHODS-REVIEW.md`. Its §7 is empty and this protocol does not fill it. The
reviewer's outcome is **Approved**, **Approved with conditions** or **Rejected**; a rejection may not be argued
into an approval in the record, and a condition must be specific enough to be re-reviewed.

**The reviewer is authorised to reject this protocol**, and is asked specifically:

1. **Is the block size adequately justified at the declared reliability assumption, and is the ladder the right
   way to handle an unmeasured reliability?** A reviewer who concludes 104 per configuration is too few has not
   undermined the project; they have found a design limitation before any cycle is spent.
2. **Is the sustention-rule agreement correctly described as robustness rather than reliability, and is it right
   to exclude it from the arithmetic?**
3. **Does the behavioural endpoint have sufficient resolution, and is its operational definition unambiguous in
   the code named in §3?**
4. **Are the pre-assigned seeds, the four unused seeds and the no-substitution rule sufficient to keep attrition
   from becoming a search?**
5. **Does the aggregation rule, which requires the relation in every claimed configuration, prevent a favourable
   but misleading reading?**

**What the reviewer must be shown, including what embarrasses the design.** The package named in
`docs/stage_b_protocol.json` (`review_gate.send_with_the_package`) carries the Stage A record, the construct
record, this protocol and its artifact, the design record whose endpoint is inherited, the sign-resolution
artifact and `docs/V1-SYNTHESIS.md`. Alongside them the reviewer receives the **history of the design's own
corrections**, because a record that shows only its final favourable numbers has hidden its reasoning:

- the Stage A dynamic-range claim — "0.44 pairs against a one-pair floor" — and its **withdrawal in place**;
- the **20 of 119** onsets that are not the first non-zero reading (one by 279 cycles);
- the **2 runs** whose eligibility depends on the sustention rule, and the **0.900** marginal share that follows;
- the behavioural horizon's **index-versus-count** reconciliation;
- **the 0.972 agreement statistic first presented as a reliability proxy, and its correction** (§6.1): it is
  robustness of the ordering, and the block is now sized at a declared assumption instead;
- the four block-level criteria that **failed** in earlier phases and were reported rather than re-scored.

---

## 11. State

**Stage B is not authorised.** No seed is allocated, no world is generated, no run is started, and no result
exists. This document authorises nothing on its own: it becomes authorisable only when §7 of
`docs/INDEPENDENT-METHODS-REVIEW.md` carries an outcome of *Approved* or *Approved with conditions resolved*.

What the protocol establishes on its own is narrower and worth stating plainly: the predictor is
**operationally defined**, its eligibility and dispersion criteria are **measured per configuration**, its clock
is **fixed and disjoint from the outcome**, its falsifiers are **pre-committed**, its block size is **solved from
the claim at a stated reliability assumption**, and its seeds are **proved unused, pre-assigned, and closed to
substitution**. Whether the predictor is scientifically valuable remains an open empirical question; whether the
block is large enough is a question the reviewer is explicitly asked to answer, and may answer in the negative.

---

## 12. Verification

```bash
./.venv/bin/python -m benchmarks.stage_b_protocol        # writes docs/stage_b_protocol.json
./.venv/bin/python -m pytest tests/test_stage_b_protocol.py -q
```

The test recomputes the artifact, asserts every number quoted here against it — including every row of the
reliability ladder — asserts that the seed block is disjoint from every seed in the record and that the spare
seeds are named, asserts that the closed form reproduces the published 48-world floor, asserts that the
sustention-rule agreement is excluded from the block arithmetic and is listed among the withdrawn claims, and
asserts that nothing is authorised or allocated.

---

## 13. The authorisation route, as decided on 2026-11-03

§11 says this document becomes authorisable only when §7 of `docs/INDEPENDENT-METHODS-REVIEW.md` carries an
outcome. **That remains the route if a reviewer can be found, and it has been sequenced rather than met.** On
2026-11-03 the owner recorded that no eligible reviewer can be found under §2 of the brief, and that the sequence
is therefore: a **machine pre-pass** recorded against a named model and commit, then the **owner's dated
authorisation**, then allocation. The decision and its costs are in
[`docs/DECISION-STAGE-B-SEQUENCE.md`](DECISION-STAGE-B-SEQUENCE.md); the prompt is
[`docs/AI-REVIEW-PROMPT.md`](AI-REVIEW-PROMPT.md).

Three properties of that route are recorded here because a later reader will look for them:

- **§7 stays empty.** No step in the new sequence fills it, and nothing in the record may describe a pre-pass as
  an approval. A machine pass that is cited as "the review before the run" would be a fabricated provenance, and
  that is the defect class this project has spent months finding in its own numbers.
- **Nothing above changes the science.** The hypothesis, the predictor, the endpoint, the four falsifiers, the
  outcomes table, the declared reliability assumption, the ladder and the 416 pre-assigned seeds are exactly as
  they were; the decision is about who signs, and when.
- **A pre-pass can stop the run and cannot start it.** A blocking finding fixes the protocol and restarts the
  sequence. A clean finding is not a licence: the licence is step 2, and it is the owner's.

**Stage B is not authorised by this section.** No seed is allocated, no world is generated, no run is started and
no relation between onset and behaviour has been computed. What has changed is that the route no longer depends on
finding a person who satisfies §2.
