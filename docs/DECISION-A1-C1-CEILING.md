# Decision: the C1 ceiling is the preplanned universe, not the number 64

**ID:** `DECISION-A1-C1-CEILING`

**Date:** 2026-11-15

**Status:** `ADOPTED BY OWNER 2026-11-15 — THE 63–64 CLAUSE GOVERNS THE CANDIDATE-PLAN COUNT; THE CEILING IS THE PREPLANNED UNIVERSE; IN FORCE`

**Decision owner:** Owner

**Signature and date:** 2026-11-15, adoption instructed in session; no personal name is recorded in this repository

**Scope:** one clause of one binding record. It changes no preservation threshold, no denominator floor, no gate and no
seed. It reads committed baseline artifacts only; no cell ran, nothing is frozen and nothing is granted.

---

## 1. The conflict

[`A1-PATH-A-C1-RULE-1`](DECISION-A1-PATH-A-C1-RULE.md) (adopted 2026-11-14, *binding for A1*) closes the top of the
C1 acceptance band:

> | 64 | 61 | 3 | C1 may be read |
> | >64 | n/a | n/a | `VOID — design inconsistency; score preplanned rows only` |

> If the observed minimum is **above 64**, the run is **`VOID — design inconsistency`**. Score only the preplanned
> rows; do not add rows after the fact.

The same table's preceding row defines what 63–64 is:

> Planned upper bound | 63–64 rows per seed (candidate count; not observed baseline availability)

[`DECISION-A1-C1-DENOMINATOR-1`](DECISION-A1-C1-DENOMINATOR.md) (adopted 2026-11-15, one day later) then fixed the
operative denominator as the **recorded cell row** — *"Every observed paired-control row of the cell stream, non-target
edges included. Not the candidate count."* It said nothing about the ceiling, and neither record names the other
superseded. The full conflict is recorded in [`A1-C1-CEILING-CONFLICT`](A1-C1-CEILING-CONFLICT.md).

## 2. The measurement

The adopted block's own no-arm baseline
([`a1_baseline_availability_adopted.json`](a1_baseline_availability_adopted.json)) observes these minimum
paired-control denominators — the quantity C1's unit names:

| Seed | `20740101` | `20740102` | `20740103` | `20740104` | `20740105` | `20740106` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Observed minimum | **79** | 64 | **79** | **74** | **72** | **74** |
| Above 64? | yes | no | yes | yes | yes | yes |

Read literally, the run is `VOID — design inconsistency` on five seeds before any retention is inspected — not because
preservation failed, but because the denominator is larger than the band. Note what did **not** happen: no row was
added. The universe was 112 candidate edges per seed all along; the 63–64 figure was a planning estimate of how many
of them the cell stream would record.

## 3. Why the clause cannot be read against the operative denominator

The clause sits in a table cell whose neighbours say *candidate count* and whose purpose is stated in the same
paragraph: **stop rows being added after the fact**. It was written against one quantity and later applied to another.

`DECISION-A1-C1-DENOMINATOR-1` changed the denominator's unit — explicitly, in the sentence quoted above — and left
the ceiling on its old scale. That is a unit error in the sense of the corpus's own rule 17(a): **a count must be
named as what it counts.** Applying a candidate-plan ceiling to a cell-row count compares 63–64 edges *planned* with
79 edges *recorded*, and reports a design inconsistency where the only inconsistency is between two records written a
day apart.

The narrow reading is therefore not a convenience. It is what the two records say when each quantity is read as the
record that introduced it names it. What is missing is a record that says so and replaces the constant with something
that still does the clause's job.

## 4. Decision

**The `>64` clause is narrowed to the quantity it names — the 63–64 candidate-plan count — and does not govern the
operative cell-row denominator that `DECISION-A1-C1-DENOMINATOR-1` adopted.**

**The ceiling's function is carried by a comparison rather than a constant: the scored denominator must equal the
preplanned universe recorded in the freeze act, and any denominator larger than that universe is `VOID — design
inconsistency`.**

**The preplanned universe is restated from the pre-treatment baseline artifact before either act is signed, and the
restated value is written into the act it freezes.**

**This amends the planned-upper-bound row of §2.1 and the third paragraph of §2.3 in `A1-PATH-A-C1-RULE-1`, and nothing
else.** The 0.95 preservation threshold, the 60-row floor, the three-loss band at 60–64, the missing-denominator rule,
the below-floor disposition, the power criterion and every other row of the decision table stand unchanged. The amendment
is recorded there as a dated note pointing here, not as a deletion.

The restated universe is the baseline's own per-seed minimum on the operative row — **79 / 64 / 79 / 74 / 72 / 74** on
the current representative selection. If the competent estimand decision is adopted, the selection changes and the
universe must be restated from the re-derived baseline; the act must carry whichever number its own selection produces.

## 5. What the replacement catches that 64 did not

The constant fails in both directions, which is why it cannot simply be raised:

| Case | Under `>64` | Under the preplanned universe |
| --- | --- | --- |
| 79 rows recorded, 79 preplanned | **VOID** — wrong: nothing was added | passes — correct |
| 64 rows recorded, 60 preplanned | passes — wrong: four rows appeared after the baseline | **VOID** — correct |

The first row is the adopted block. The second is the defect the clause exists to catch, and the constant is blind to
it: any addition that stays under 64 looks like a preplanned universe. A comparison against the recorded universe
catches every addition at any size, and fires on nothing that was planned.

## 6. Rejected alternatives

**Read the clause literally and accept five seeds as VOID.** It voids the adopted block before any retention is read,
for a denominator that is exactly the preplanned one; and it would still pass a 64-row run that added four rows after
the baseline, so it fires where nothing is wrong and stays silent where the defect is.

**Keep the ceiling and shrink the candidate universe to 64 rows or fewer.** It changes the target population to satisfy
a planning number, drops rows the baseline shows are available, shrinks the non-target stream C4 is computed over, and
would be a design change made after the baseline was seen.

**Delete the ceiling and rely on the instruction to score preplanned rows.** A check that must be remembered is not a
check: with no comparison against the recorded universe, a scored population larger than the planned one is invisible.

**Treat the narrow reading as already settled by the checklist footnote.** A documentation edit cannot decide a binding
record, and that footnote has been retracted; the clause needs a record of its own.

## 7. Dependencies and what this does not do

- It does not change the 0.95 threshold, the 60-row floor, the three-loss band or the C4 ceiling.
- It does not re-score, re-read or void any result. The block it is measured against is a baseline; no cell ran.
- It does not resolve the competent estimand ([`DECISION-A1-COMPETENT-ESTIMAND`](DECISION-A1-COMPETENT-ESTIMAND.md),
  PENDING). The two are independent, and the order does not matter, because **the universe is selection-invariant**:
  C1 counts every recorded row of the cell stream, targets included, so the minima 79 / 64 / 79 / 74 / 72 / 74 are a
  property of the 112-row universe. The competent selection reproduces them exactly, so adopting that decision changes
  C4's stream and not this number.
- **Which act the universe is written into.** `A1-TARGET-FREEZE-1` freezes four targets per seed, and four rows per
  seed can never reach C8's adopted `N_min = 17`; that incompatibility is C8's, not this decision's. On the current
  state the act that can carry a competent block is `A1-TARGET-FREEZE-N20-1`, so the restated universe goes there.
- It does not adopt the C1 branch, freeze a target, issue a grant or authorise a run.

Adopting it, then restating the universe in the freeze act, leaves the C1 branch closed at both ends for the first time:
the floor at 60 with its VOID disposition, and a top that is whatever the design planned rather than a number carried
over from a superseded quantity.

## 8. Reproduce

```bash
.venv/bin/python -c "
import json
d=json.load(open('docs/a1_baseline_availability_adopted.json'))
mins=[r['c1_min_denominator'] for r in d['per_seed']]
print(mins, 'above 64:', sum(m > 64 for m in mins))"
.venv/bin/python -m pytest tests/test_a1_c1_ceiling.py -q
```
