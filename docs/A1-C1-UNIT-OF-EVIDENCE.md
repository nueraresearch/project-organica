# C1's unit of evidence — one page, one question

**Date:** 2026-11-15

**Status:** `OWNER NOTE — DEFINITIONAL QUESTION; NOTHING DECIDED, NOTHING IN FORCE`

**The question, and only this:** for C1, is one observation a **directed edge**, or one **underlying relation** counted once however many orientations it has?

No power analysis, no C4 strategy, no competence rule. Those are downstream and each needs this answered first.

## What is already settled, by evidence rather than by taste

- **Row inclusion is fixed.** C1's denominator is the observed paired-control rows, including baseline-available non-target edges (`DECISION-A1-C1-DENOMINATOR-1`, owner-confirmed 2026-11-15). The 63–64 figure is a planning quantity, not the adjudicating denominator.
- **The implementation is fixed.** `a1_arms.run_cell` builds `rows + neighbor_rows` from the **directed-edge** 120-cycle stream; `c1_rows()` and `score_c1()` read it that way. Nothing in code would have to change for the directed convention — it is already what runs.
- **The bar is a proportion, not a count.** `C1_path_separation` is 0.95: the proportion of paired-control carrier-available edges *still available* under A−/K−, per seed (`A1-PRECOMMITTED-THRESHOLDS.md`). The "60" and "57" that appear beside it are `0.95 × 63` and `0.95 × 60` — the count form of that proportion **at the planning denominator**.

## What is not settled

The protocol says which rows participate. It does not say whether `a → b` and `b → a` are two observations or one. `A1-DESIGN-VIABILITY.md` records the gap explicitly: *"whether two orientations of one relation are independent C1 observations is a convention the protocol does not fix"*, and it keeps the relation-level reading verbatim rather than declaring it wrong.

## The consequence, with the arithmetic the table invites you to skip

Available paired-control rows per seed, both blocks (`A1-DESIGN-VIABILITY-1`):

| Unit | 2063 | 2074 |
| --- | ---: | ---: |
| directed edges | 58–72 | **64–79** |
| relations, any orientation | 31–46 | 35–51 |
| relations, both orientations | 28–42 | 31–38 |

Read as proportions, **both units are adjudicable**, and the difference is strictness rather than possibility:

| Unit | Denominator | Failures the 0.95 bar tolerates |
| --- | ---: | ---: |
| directed | 64–79 | **3** |
| relation, any orientation | 35–51 | **1–2** |
| relation, both orientations | 31–38 | **1** |

So the relation convention is **not** "below floor" and **not** unviable. It is the same gate with roughly half the rows and two to three times less tolerance: at 64 directed rows three failures still pass; at 35 relations a single failure is 2.9% and passes, and a second is 5.7% and fails.

The "opposite viability verdicts" you saw come from a subtler version of the earlier error: the table's relation-level **ceilings** are compared against the directed-scale **count** 60. That comparison answers "can the plan's 63–64 paired-control rows be reached at this unit?" — and the answer is genuinely no — but it does not answer "does C1 pass at this unit?", which the proportion decides. I wrote that table; the mixing is mine to flag.

## What measurement cannot settle, and what it can

No run can say which unit is *the* observation; that is definitional, as you say. But the engine can say how much the two orientations actually share, and that is measured: **A availability differs across orientations on 15–28 of 64 relations per seed** (`A1-DESIGN-VIABILITY-1`), and K is 97.2% concordant across candidate/reverse pairs (`A1-K-DECOMPOSITION.md`, 278/286).

That cuts both ways and is the reason this is a real decision rather than a formality. The orientations are not duplicates — availability is orientation-specific on a third to a half of relations — so counting one discards genuine variation. They are also not independent — they are two readings of one coupling — so counting both inflates n with correlated members. A directed-edge denominator treats correlated rows as if they were free; a relation denominator answers a different question, "does the relation survive", which is not what C1's carrier claim is about.

## The repository already uses both units, and has not said so

Target selection uses **one orientation per unordered pair** — the published rule and the competence filter both say so, and C8's twenty rows are twenty *relations*. C1 reads **directed** rows. So the design is relation-unit where it selects and directed-unit where it scores, and that inconsistency has never been declared as a choice.

It is defensible: C8 asks whether an A−K− double block exists for a relation, and a relation needs one orientation; C1 asks whether a *directed carrier path* survives A−, and a path is directional by construction. Two estimands, two units. But then the mixture must be written down, because it is exactly the thing that makes two readers disagree about whether the same run passed.

## What I would do, marked as a recommendation

**Directed edge as the unit of evidence, relation as the dependence class — both declared before the freeze.**

- C1's estimand is path preservation along a directed carrier; the carrier is directional in this engine, so the observation is directional.
- The relation is then a **dependence dimension, not a competing denominator**: report the relation-level proportion once per relation beside the directed result, as a robustness check with the floor applied to *its own* denominator, and never pool the two.
- That keeps the count form of the floor at 60 (60/63), keeps C4's protected set at the size already measured, and makes the relation reading a declared sensitivity analysis rather than an alternative adjudication.

The alternative — relations as the unit outright — is coherent and stricter: it answers "does the coupling survive", it halves the C4 protected set too (59–60 unique non-target rows at N=4, 43–44 at N=20), and it makes C1 and C8 use one unit. If that is the claim you want, it should be chosen deliberately, not inherited from a table.

## What this note does not do

It does not decide, does not amend the denominator decision, does not change the 0.95 floor, and does not re-score any viability verdict. It corrects one comparison in my own table, states the arithmetic that the two conventions imply, and puts the question where it belongs: the owner's.

## Reproduce

```bash
python -m benchmarks.a1_design_viability --check    # directed and relation ceilings, per seed
python -m benchmarks.a1_competence_filter_draft --check   # one orientation per pair in selection
```

Reads committed no-arm artifacts; runs no engine.

## Closure

The owner names the unit for C1. Under the directed convention the count form of the floor is 60 of 63, and the relation reading is recorded as a declared sensitivity check. Under the relation convention the floor's count form is 34 of 35 at the tightest seed, C4's protected set halves, and C1 and C8 share a unit. Either way this note is superseded by an amended `DECISION-A1-C1-DENOMINATOR-1` rather than left standing beside it.
