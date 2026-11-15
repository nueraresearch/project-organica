# A1 C2/C8 competence rule — draft for owner decision

**Date:** 2026-11-15

**Status:** `DRAFT — FOR OWNER DECISION; NOT IN FORCE; NO CELL RUN`

**Scope:** target selection and adjudication for C8, and for the C2 cells that ride on the same rows. This document freezes no manifest, assigns no seed, changes no threshold, authorises no cell and measures no treatment effect. Nothing in it is in force until the owner chooses the options in the last section.

## Why this document exists

The A1 pre-freeze checklist records C2/C8 target competence as **unowned**: the viability record calls competence *conditional* and asks for "an owner rule", and no rule had been written. C8 needs a declared number of rows per seed on which an A−K− double block can actually be observed; C2 needs all four of its cells on a target. If a target's baseline A or K path is absent, its row cannot exercise those cells, and the gate has nothing to score.

This is a draft rule with measured consequences, not a decision. The decision is the owner's.

## The competence reading, stated as an assumption

A row is **competent** when both of its baseline paths (A and K) are present at the recorded no-arm baseline. Under that reading, a row lacking baseline A or K cannot support all of C2's cells and cannot test a genuine A−K− double block.

Two limits are part of the reading, not caveats bolted on afterwards:

- **C2 is a treatment gate, not a no-arm gate.** The baseline cannot show that a missing path stays missing under A− or K+ treatment. If an unblocked arm can induce the absent path, exact C2 is unmeasured by this rule rather than decided by it.
- **Absence at baseline is not treatment failure.** The counts below are a target-selection incompatibility, not a proof that C2 or C8 must fail.

## The rule, as drafted

1. **Row unit.** One target edge. A row is competent if and only if both baseline paths A and K are present for that directed edge in the recorded no-arm baseline. Competence is a property of the row at selection time; it carries no claim about treatment.
2. **Selection.** C8 rows are selected only from the competent pool, by a declared rule, and the pool is recorded **before** the freeze. No non-competent row is ever added as a fallback.
3. **Pre-registration.** The rule, the pool and the block are recorded in the freeze. Changing any of them after a run voids C8 for that block; the block may not be re-filtered to fit an outcome.
4. **Disclosure.** Report the unfiltered selection beside the filtered block, so the filter's effect is visible rather than silently baked in.

## The adjudication contract — written as though the run were tomorrow

This is the part the repository did not have: not *whether* competence occurred, but **what observation would constitute it**. Every line below is either quoted from a committed document or derived from it arithmetically; none of it is new policy.

**Unit of analysis.** One row = one directed target edge in one seed. C8's rate is **per seed, over its N target rows**; rows are never pooled, never averaged across seeds, and there is no best-seed reading (`A1-C7-C8-DENOMINATOR-1` §2). A "block" is the set of rows one seed contributes.

**Required row count.** **N = 20** for C8. The Path A four-row block is a different design and does not supply C8 (`A1-C7-C8-DENOMINATOR-1` §3: "C7 does not need 20 rows; C8 does").

**Success threshold.** Unchanged and quoted: the A−K− assertion rate in a seed, over its N target rows, must be **at most 0.05**, and above that ceiling the seed reads `THIRD ROUTE PRESENT` (`A1-PRECOMMITTED-THRESHOLDS.md`). At N = 20 the rate step is `1/20 = 0.05`, so the bar is arithmetic: **at most one asserting row out of twenty**.

**Interpretation — three outcomes per seed, and one that is not an outcome.**

| Competent rows in the seed | asserting rows | Reading |
| ---: | ---: | --- |
| 20 | 0 or 1 | **ADJUDICABLE — C8 PASSES** on that seed |
| 20 | 2 or more | **ADJUDICABLE — THIRD ROUTE PRESENT** on that seed |
| fewer than 20 | — | **NOT ADJUDICABLE (VOID)** — no rate at the declared step |

**Why the third row matters, and why it is a choice rather than a consequence.** A rate over fewer rows does not simply weaken the claim; it changes the step. At 18 rows the step is `1/18 = 0.0556`, above the ceiling, so **zero** asserting rows would be tolerated — a stricter per-row bar than the full block's one-in-twenty. A short block is therefore not uniformly weaker evidence: it is a different test with a different resolution. "Exactly N or VOID" is a decision about which test to run, not a fact that follows from the threshold.

**Pre-flight under this contract, on the adopted block, with nothing run.** From
[`A1-COMPETENCE-FILTER-DRAFT-1`](A1-COMPETENCE-FILTER-DRAFT.md):

| Design | Seeds forming a competent block | Per-seed verdict tomorrow |
| --- | ---: | --- |
| N=4 | **6 of 6** | adjudicable on every seed |
| N=20 | **4 of 6** | two seeds not adjudicable (one impossible, one undecided) |

So **as written, this contract would return C8 as VOID on the adopted block today** — not because any treatment fails, but because two seeds cannot field twenty competent rows under the endpoint cap. That is the state the rule exists to make visible before a run rather than after one.

## What is measured

On the **2063** block (recorded in `docs/a1_design_viability.json`):

- selected N=4 rows competent per seed: **2, 3, 3, 1, 2, 1** — at most **3 of 4**;
- selected N=20 rows competent per seed: **5–12** of 20;
- candidate pool that is A- and K-available: **23–36** edges per seed.

On the **adopted 2074** block, recorded in [`A1-COMPETENCE-ADOPTED-1`](A1-COMPETENCE-ADOPTED.md) — `docs/a1_competence_adopted.json`, rebuilt and guarded by `python -m benchmarks.a1_competence_adopted --check`:

- selected N=4 rows competent per seed: **3, 0, 3, 2, 2, 2** — **12 of 24**, at most **3 of 4**;
- selected N=20 rows competent per seed: **10, 7, 11, 13, 10, 7** — **58 of 120**, at most **13 of 20**;
- candidate pool that is A- and K-available: **27–40** edges per seed.

The two blocks agree on the shape of the finding: **no seed supplies a clean C8 block under the current selection.** What differs is the supply reading: on the adopted block the pool holds 27–40 competent rows against 20 needed, but that is a count and not a construction — the filter draft shows a twenty-row competent block cannot be built on every seed while the endpoint cap stands.

## Three options for the owner

**Option A — adopt the filter and re-select.** C8 rows are re-selected from the A- and K-available pool under a declared rule. The filter is nevertheless **necessary and not sufficient**: [`A1-COMPETENCE-FILTER-DRAFT-1`](A1-COMPETENCE-FILTER-DRAFT.md) applies it and finds a competent four-row block on all six adopted seeds, but a competent twenty-row block on only four — `20740102` is impossible by exhaustion (all 888,030 twenty-row subsets checked) and `20740105` is undecided with a best block of eighteen. Adopting A therefore also means declaring a change to the endpoint cap or to the selection rule that can find a block, and recording that as the design change it is.

**Option B — declare C8 not adjudicable.** Keep the current selections and record on the act that C8 cannot be scored on them. Cost: nothing today, and C8 never becomes measurable under this design.

**Option C — redesign the universe** to raise A∩K per seed, or to raise the number of tags so the cap binds less. Cost: the largest, and it contradicts what is already known about K (window-limited; the loop cap moved it only sublinearly).

**A recommendation, marked as one:** Option A, but not alone. The filter fixes the population a C8 result would speak about; it cannot produce a twenty-row block on every adopted seed while the endpoint cap stands. The defensible step is the filter together with a declared cap change, or Option C; Option B remains the honest fallback if neither is acceptable.

## The five questions, answered as recommendations

The "run tomorrow" exercise surfaced five ambiguities. Each is answered below with the reason, what
the answer commits to, and what would overturn it. They are recommendations for the owner to ratify
or amend; none is in force.

### 1. A short block: **VOID. Do not run a partial C8 block, and do not substitute a reduced N.**

The gate reads **per seed**, and three reasons make VOID the only answer consistent with that.

- **Uniformity.** C8 fails if *any* seed's rate exceeds the ceiling. If one seed runs 20 rows and
  another 18, their steps are `1/20` and `1/18` — different bars, not the same gate at different
  precision. "Any seed above the ceiling" would compare incomparable quantities.
- **It is not a weaker test, it is a different one.** At 18 rows the step `0.0556` exceeds 0.05, so
  zero asserting rows are tolerated, against one at twenty. A short block is *stricter* per row.
  Choosing it after discovering that only 18 are available is choosing which gate to run with
  knowledge of feasibility — the same class of freedom the pre-registration exists to remove.
- **A reduced N is a new design, not a fallback.** It needs its own precommitment, its own step and
  its own statement of what it estimates. Declaring it in advance is legitimate; discovering it at
  selection time is not.

**Commits to:** C8 VOID on any seed fielding fewer than twenty competent rows — which on the adopted
block is two seeds today, so C8 is VOID unless the cap or the universe changes. **Overturns if:** the
owner pre-declares a reduced-N ladder with its steps and tolerances before the block is fixed.

### 2. Where the filter applies: **a selection predicate, applied before the run, recorded in the freeze.**

Competence is measured on the **no-arm baseline**, so it is available before any treatment and there
is no timing excuse for applying it later. Applied after the run it is an exclusion, and an exclusion
that produces the same row set is indistinguishable in the table from a pre-declared selection — the
distinction is entirely in when it was fixed. Since the filter changes the population the result
speaks about, it belongs with the target rule, the block and the digest.

**Commits to:** the freeze names the pool, the selection rule and the filter's effect (on the adopted
block: 14 of 24 N=4 rows and 42 of 80 N=20 rows replaced), and the unfiltered selection is reported
beside it. **Overturns if:** competence is ever computable only from treatment data — it is not.

### 3. Uninducible paths: **keep the screen, and declare C2's scope rather than its coverage.**

Baseline absence is the right precondition for *selecting* a row that can exercise four cells, and it
is not evidence that the absent path stays absent under A− or K+. So the screen stays, and the act
carries one sentence of scope: **C2 is scored on competent rows; C2 on baseline-incompetent rows is
unmeasured, not failed.** Writing that sentence is the honest close. The alternative — closing the
gap — needs an unblocked-arm diagnostic on a single seed, which is a different act and cannot be
replaced by rule text.

**Commits to:** C2's claim is scoped to the competent population, and the vocabulary "unmeasured"
is fixed in advance so it cannot later be read as "failed" or "passed". **Overturns if:** a
diagnostic shows an unblocked arm induces baseline-absent paths, in which case the screen is not a
precondition for C2 and this rule must be re-drafted.

### 4. Which block C8 reads: **one screen, two independently drawn blocks.**

Path A's four-row block and the C8 twenty-row block are separate target sets with separate digests,
and **both** are drawn from the competent pool. The alternative — C2 scored on the old unfiltered
four and C8 on a filtered twenty — would have the two gates speaking about different populations in
the same act, which is exactly the kind of quiet mismatch this project keeps finding after the fact.

The cost is already measured and declared: the filtered four-row block forms on 6 of 6 seeds by
replacing 14 of 24 rows, and that replacement set is a **new estimand**, not the representative
sample the published selection describes.

**Commits to:** both blocks report their pool, digest and replacement count; neither is described as
"the" target set. **Overturns if:** the owner prefers C2 on the published representative rows and
accepts that C2 and C8 then address different populations, which must be stated in the act.

### 5. The one-in-twenty bar: **declare it, and report the count, not only the verdict.**

At N=20 the ceiling 0.05 admits exactly one asserting row, and both 0 and 1 read as PASS. The act
should say so in those words, because "at most 0.05" invites the reading "a small number" when it is
precisely one row out of twenty. The report should carry the per-seed assertion count beside the
verdict, since the verdict discards the only information that distinguishes a clean block from one
that spent its entire allowance.

**Commits to:** one sentence in the act and one column in the report. **Overturns if:** the ceiling
is renegotiated, which is a threshold change and outside this rule.

## If the five are ratified, the rule issues as

The decision this document becomes, stated so it can be adopted verbatim:

> **C2/C8 competence rule, adopted [date].** A target row is competent when both baseline paths A and
> K are present in the recorded no-arm A+K+ replay. C8 rows are drawn only from the competent pool by
> the declared selection rule, before the run, and the pool, rule, block, digest and replacement
> count are recorded in the freeze with the unfiltered selection reported beside them. C8 reads per
> seed over exactly **N = 20** competent rows at the unchanged 0.05 ceiling — at most one asserting
> row — and a seed fielding fewer than twenty is **not adjudicable**, never run short and never
> re-filtered afterwards. Path A's four-row block is drawn under the same screen and reported
> separately. C2 is scored on competent rows and is **unmeasured**, not failed, on baseline-
> incompetent rows.

What that adoption would change, from the measured record: C8 is VOID on the adopted block as it
stands (two seeds short of twenty), the four-row block becomes the filtered set (6 of 6 seeds, 14 of
24 rows replaced, a new estimand), and C8 becomes adjudicable only if the endpoint cap or the tag
count is changed — the two repairs whose cancellation is recorded in
[`A1-INTERPRETATION`](A1-INTERPRETATION.md).

## What would change this

A measurement showing that baseline-absent paths are inducible by an unblocked arm would make competence irrelevant to C2 and force this rule to be re-drafted rather than adopted. An owner decision to run C8 on a declared filtered block, at a declared N and cap, closes it in the other direction.

## Closure

The owner selects A (with its cap or rule change), B or C, and ratifies or amends the five answers above. This document is then re-issued with the choices recorded: under A it gains the declared selection rule, cap and block; under B it becomes the recorded limitation on the freeze act; under C it becomes the specification for a new universe. Until then the checklist row stays **undecided**, and no C8 block is adjudicable.

## Reproduce the adopted-block figures

```bash
python -m benchmarks.a1_competence_adopted --check         # competence counts
python -m benchmarks.a1_competence_filter_draft --check    # the filter and its verdicts
python -m benchmarks.a1_competence_adopted --self-test
python -m benchmarks.a1_competence_filter_draft --self-test
```

Both records are read-only joins of committed no-arm artifacts. They run no engine, select no target and carry the competence reading and induction caveat stated above.
