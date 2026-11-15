# A1 disposition — Path A continues (adopted 2026-11-15)

**ID:** `A1-DISPOSITION-2`

**Date:** 2026-11-15

**Status:** `ADOPTED — PATH A CONTINUES; NO FREEZE, NO GRANT, NO RUN`

**Decision owner:** owner direction, 2026-11-15.

**Signature and date:** owner direction recorded 2026-11-15; no name is typed into this record by anyone
other than the owner.

**Scope:** program disposition only. This document assigns no seed, freezes no target, authorises no cell,
changes no engine file and records no result. It replaces a disposition whose stated basis has changed; it
does not touch C1, C4, C7, C8 or C9.

## 1. What this record is for

[`DECISION-A1-DISPOSITION`](DECISION-A1-DISPOSITION.md) was adopted on 2026-11-14 as **committed to target
resolution**, on a basis that has since been replaced in four separate places: C1 was said to be unreachable,
C8 was not adjudicable, C4's exposure was undecided, and the gates that judge all of them read an unmeasurable
value as a pass. None of those four statements is true of the tree today.

The branch question — **continue, redesign or park** — was therefore re-opened rather than inherited
([`A1-DISPOSITION-REREAD`](A1-DISPOSITION-REREAD.md)). **This record answers it: Path A continues.**
Adoption on 2026-11-15 supersedes the 2026-11-14 disposition and the re-read, and restates the commitment
against what the tree now contains. The 2026-12-14 lapse clock carried by the earlier record continues to run
against this one.

## 2. What changed, and where it is recorded

| Premise | On 2026-11-14 | Now | Record |
| --- | --- | --- | --- |
| C1 reachability | relation-level denominator read against a directed-row floor → "unreachable" | directed rows clear the floor: `2063` reads 70/59/69/58/72/72 at N=4 and 79/64/79/74/72/74 at N=6, against 60/57 at 0.95 | `DECISION-A1-C1-DENOMINATOR-1`, `A1-DESIGN-VIABILITY-1` |
| C1 unit | undecided, so the denominator above had no defined row | directed edge is the unit; a relation is a declared dependence class reported once per relation, never pooled | `DECISION-A1-C1-UNIT-1` |
| C8 adjudicability | VOID on the adopted block | floor is *at least* `N_min = 17`, certified by exhaustive enumeration on seed `20740102`; adjudicable on 6/6 seeds | `DECISION-A1-C8-NMIN-1` |
| C4 exposure | undecided, presented as a risk choice | **posture A adopted**: veto stays a maximum at 0.05, multiplicity declared, failing edge named, VOID probability declared unmeasured | `DECISION-A1-C4-POSTURE-1` |
| Gate measurability | not audited | an unmeasurable delta or flag fails the gate, repaired at four gates, the join and the C1 scorer; and C1 reports `C1_UNMEASURABLE` rather than borrowing `C1_THRESHOLD` | `A1-GATE-MEASURABILITY-AUDIT`, `DECISION-A1-C1-UNMEASURABLE-1` |

The checklist's own summary of this is one sentence: **no substantive owner choice remains open**
([`A1-PRE-FREEZE-CHECKLIST`](A1-PRE-FREEZE-CHECKLIST.md)).

## 3. The disposition

**Path A continues.** The commitment is no longer to "target resolution" as an open-ended preparation, because
target resolution has happened and the two gates that were said to block it are now decided. The commitment is
to a named sequence, and nothing beyond it:

```text
freeze review  →  provisional target freeze  →  dated grant  →  run once
      →  assemble C1 + C4 from actual parts  →  PASS, or A1 VOID — C1/C4
```

The run is read for one thing: whether the executed comparison is admissible. No model is read before that
decision, and a VOID is a result about the design, not a treatment result.

## 4. Conditions of continuing, named

Continuing is conditional. Each condition below is stated with its state on this date, so that a later reader
can tell which ones were met for the run that happened.

| # | Condition | State | Where |
| --- | --- | --- | --- |
| D1 | C1 is read on the **recorded cell row** as the operative denominator, with 63–64 a planning quantity | **met** | `DECISION-A1-C1-DENOMINATOR-1` |
| D2 | C1's unit is the **directed edge**; a relation is reported once per relation on its own denominator | **met** | `DECISION-A1-C1-UNIT-1` |
| D3 | C8 reads on **at least `N_min = 17`** competent rows, operative sizes `20/17/20/20/18/20` | **met** | `DECISION-A1-C8-NMIN-1` |
| D4 | C4's exposure is **accepted as posture A**, not assumed small | **met** | `DECISION-A1-C4-POSTURE-1` |
| D5 | An **unmeasurable** quantity VOIDs; it never passes and never crashes | **met** | `A1-GATE-MEASURABILITY-AUDIT`, `DECISION-A1-C1-UNMEASURABLE-1` |
| D6 | No first-order pre-freeze question is open | **met** | `A1-PRE-FREEZE-CHECKLIST` |
| D7 | Both **provisional target freeze** acts are signed and dated | **not met** — owner act | `A1-PRE-FREEZE-CHECKLIST` |
| D8 | A **dated grant** authorises the seed block and the attempt | **not met** — owner act | `A1-PRE-FREEZE-CHECKLIST` |
| D9 | The planned cells run **once**, and C1/C4 are assembled before any model is read | **not met** — follows D7 and D8 | `A1-C1-C4-VOID-GATE` |

D5 required one vocabulary decision, taken on 2026-11-15: a C1 failure with a sound denominator but an
unmeasurable retention rate used to VOID as `C1_THRESHOLD`, which named the wrong cause. It now carries
`C1_UNMEASURABLE`, with `C1_THRESHOLD` narrowed to a measured rate below 0.95
([`DECISION-A1-C1-UNMEASURABLE-1`](DECISION-A1-C1-UNMEASURABLE.md)). No condition in this table is left open.

## 5. Limitations this disposition accepts, stated as costs

Continuing accepts four things that no pre-run measurement can settle. They are listed here so that reading a
later VOID does not require re-discovering them.

1. **C8 has almost no slack.** With `N_min = 17` and a tolerance of `floor(0.05 × N)`, a 17- or 18-row seed
   permits **zero** failed assertions, and a 20-row seed permits **one**. The operative block is
   `20/17/20/20/18/20`, so two of six seeds carry no slack at all. That is the cost of the floor, and it was
   chosen over exact-20 because `20740102` cannot field eighteen.
2. **C4's VOID probability is unmeasured.** The veto is a **maximum** over 324 non-target deltas per seed and
   **1,944** per block, against a fixed 0.05, with no correction. No distribution of a non-target neighbour
   delta under these arms exists, and none can exist before the run without amending blindness — assessed and
   recommended against (`A1-C4-NOISE-FEASIBILITY`).
3. **C1 will either clear or void; it will not be estimated.** The floor is reachable on the measured rows, not
   guaranteed on the executed ones, and "reachable" is a statement about the design, not a prediction.
4. **This is a bet on design adequacy, not on the mechanism.** Continuing says the experiment can be judged; it
   does not say what it will show. No outcome is anticipated by this record, and none may be claimed from it.

## 6. Rejected alternatives

- **Redesign.** Rejected on measurement, not on appetite: a predeclared fresh block (`20650101–20650106`) fails
  **0/6** at C1 with ceilings 40/37/46/42/31/38, and a 28-tag larger universe fails worse (C1 23/40/42/55/47/37,
  K diluted to 23–55). Raising edges raised K-available rows by two (242 → 244) while candidate edges rose
  383 → 1000 — a new universe is a new study, and the one construction tested does not repair what it would
  cost. See `A1-DISPOSITION-MEMO` §6.
- **Park.** Rejected because the reason for parking has been removed twice: C1's unreachability was a
  denominator-convention artefact, and C8's unavailability was a floor convention that a certified `N_min`
  replaced. Parking now would discard the evidence C1, C4 and C7 can still yield while claiming nothing.
- **Continue with D5 unaddressed.** Rejected: running a gate that reads an unmeasurable value as a pass would
  spend the registered attempt on a comparison that cannot void correctly. That was repaired on 2026-11-15 and
  is a condition, not a suggestion.

## 7. The clock

Signature does **not** extend the deadline. If the provisional target freeze and the grant are not both recorded
by **2026-12-14**, this disposition lapses to **A1 PARKED** by default, with reason and revisit condition
recorded — the same default as the disposition it replaces. A deadline that moves when a disposition is
re-issued is not a deadline.

## 8. What this adoption does and does not do

**Does:** answers the branch question with **continue**; records that the four premises the previous disposition
rested on have been replaced; names the conditions under which continuing is authorised and which of them remain
owner acts; keeps the 2026-12-14 clock.

**Does not:** freeze a target, reserve a seed, authorise a cell, issue a grant, clear any gate, change any
threshold, or authorise a result to be read. D7, D8 and D9 remain outstanding after adoption, and D7 — the two
provisional target freeze acts — is the next one due.

## 9. Reproduce the state this rests on

```bash
python -m benchmarks.a1_design_viability --check          # C1 row counts on directed rows
python -m benchmarks.a1_competence_filter_draft --check   # C8 coverage at N_min = 17
python -m benchmarks.a1_gate_readiness --check            # gate contracts and measurability
python -m benchmarks.decision_graph --check               # the decisions this cites
```

All four read committed no-arm artifacts. No engine is started, no seed is spent and no cell is written.
