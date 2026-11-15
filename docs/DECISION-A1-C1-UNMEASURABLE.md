# C1 gains an unmeasurable reason code; `C1_THRESHOLD` keeps its one meaning

**ID:** `A1-C1-UNMEASURABLE-1`

**Date:** 2026-11-15

**Status:** `ADOPTED — BINDING FOR A1; NO FREEZE, NO GRANT, NO RUN`

**Decision source:** owner direction, 2026-11-15. The owner named both options and delegated the choice to this
record; the amendment is therefore the owner's act, not an inference from the code.

**Scope:** the C1 reason-code vocabulary in [`A1-C1-C4-VOID-GATE-1`](A1-C1-C4-VOID-GATE.md). It changes no
threshold, no gate condition, no row set, no denominator and no disposition.

## The question

[`A1-GATE-MEASURABILITY-AUDIT`](A1-GATE-MEASURABILITY-AUDIT.md) repaired the gates so that an unmeasurable
flag or delta fails rather than passes. That left a reporting defect one layer up: `_c1_reason` classifies a
failed C1 by its **denominators** alone, so a seed whose denominator is sound but whose retention rate could not
be computed VOIDs as `C1_THRESHOLD` — the code that means *"a measured rate fell below 0.95"*.

Two ways to fix it: give the case its own code, or widen `C1_THRESHOLD` to cover both.

## Decision

**C1 gains `C1_UNMEASURABLE`. `C1_THRESHOLD` is not widened; it keeps exactly one meaning.**

A C1 VOID now reads, in precedence order:

| Order | Code | Condition |
| ---: | --- | --- |
| 1 | `C1_NO_DENOMINATOR` | no paired-control denominator on a required seed or path; a missing denominator is not zero |
| 2 | `C1_DENOMINATOR_BELOW_FLOOR` | the observed minimum denominator is below 60, even if every available row is retained |
| 3 | `C1_UNMEASURABLE` | the denominator is sound, but an `A−` or `K−` retention rate cannot be computed |
| 4 | `C1_THRESHOLD` | the rate **was** computed and is below 0.95 |

Structural causes outrank unmeasurability because a missing or below-floor denominator also makes the rate
uncomputable, and the cause that fired first is the one worth reporting.

## Why this option

1. **`C1_THRESHOLD` is an assertion about a computation.** "Retention fell below 0.95" is a claim about a number
   that was calculated. Widening it to also mean "no number exists" would put back, at the reporting layer, the
   exact defect the measurability audit removed at the gate layer: a label asserting a measurement that never
   happened. A run would then read as *failed the bar* when it never reached the bar.
2. **C4 already draws this line.** `C4_UNMEASURABLE` and `C4_DELTA` are separate codes for the same reason, and
   the adopted declaration's clause 2 requires a failure to name what fired. C1 having one code for two
   different causes is an asymmetry, not a simplification.
3. **The cost is one code and one branch.** `score_c1` now reports the unmeasurable paths per seed, `_c1_reason`
   reads them, and no gate logic changes. There is no consumer outside `a1_result`, no threshold and no row set
   involved.
4. **The narrowing is free of history.** No A1 cell has run, so there is no past VOID whose label this changes.
   If one had, the correct treatment would have been to mark the old label superseded rather than rewrite it.

## What was rejected

- **Widen `C1_THRESHOLD` to cover "not measurable".** Rejected on the naming rule this project already applies
  to counts: a label must name what it counts. One code for two causes also makes a later reader unable to tell
  a failed manipulation from a failed measurement — the distinction the whole measurability repair exists to
  preserve.
- **Report no code and let the null fractions speak.** Rejected: the VOID path guarantees at least one reason
  code, and a run that voids without naming a cause is the `C1_C4_INCOMPLETE` fallback, which would misdescribe
  a complete assembly.

## What changes on disk

- `benchmarks/a1_arms.py`: `score_c1` reports `unmeasurable` per seed (`["A-"]`, `["K-"]` or both) and a
  top-level list of `{seed, path}` entries.
- `benchmarks/a1_result.py`: `_c1_reason` gains the third branch, after the two denominator checks.
- The gate-condition tables in [`A1-C1-C4-VOID-GATE`](A1-C1-C4-VOID-GATE.md) and
  [`A1-PROVISIONAL-FREEZE-GATE-ORDER`](A1-PROVISIONAL-FREEZE-GATE-ORDER.md) gain the row and the code list
  gains the code; both carry a dated amendment note.
- Two tests: the code fires on a sound 60-row denominator with one measured-hole, and a below-floor denominator
  still outranks it.

## What this does not do

It does not make C1 more or less likely to pass, does not change the 60-row floor or the 0.95 threshold, does
not alter `gate_c1`, does not touch C4, and does not freeze, grant or run anything. It makes the vocabulary able
to say which of two different things happened.

## Reproduce

```bash
python -m pytest tests/test_a1_gate_measurability.py -q
python -m benchmarks.a1_gate_readiness --check
```
