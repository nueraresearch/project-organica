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
| which transitions are withheld | `benchmarks/formation_provenance_study.py` — `held_out_pairs()` and `PHASE_TRANSFER` |
| whether the count is non-zero before a cell is scorable | the `E6` gate in `benchmarks/reusable_knowledge.py`, which requires `revision_held_out_pairs > 0` |

**A resolution requirement gates the run, and it is stated as a requirement rather than a number** because the
number depends on a withheld set that does not exist yet. Before any world is generated, the harness must report
the endpoint's **quantum** (one held-out transition) and the **count** of held-out transitions per world, by
running the enumeration named above. If the quantum is coarser than the smallest effect this protocol asserts,
the endpoint cannot resolve that effect, the design is unmeasurable for its own claim, and the run does not
start (AGENTS 13). This is not a documentation detail: it determines whether the experiment can measure its
stated outcome at all, and it is the check that would have caught the Phase L design defect before the campaign.

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

**The count is a floor, not a budget.** Unmodelled dependence between worlds and any further measurement error
lower the real resolution probability, so 104 is the least number this claim can be tested with, not the most.

### 6.3 Cost

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
