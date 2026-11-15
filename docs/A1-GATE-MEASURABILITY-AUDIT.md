# A1 gate audit — does an unmeasurable input read as a pass?

**Date:** 2026-11-15

**Status:** `AUDIT — FOUR GATES REPAIRED, PLUS THE JOIN AND THE C1 SCORER; THE REASON-CODE GAP IS DECIDED`

**Scope:** the eight gate functions in `benchmarks/a1_gate_readiness.py` plus C6, which is read from its
committed block rather than computed. No threshold, row set, denominator or verdict on a measured stream
changed. No engine ran, no seed was spent, no cell was written.

## Why this audit exists

C4 was repaired on 2026-11-15 after its comparison `float(delta[path]) > tolerance` was found to read `nan`
as clean — `nan > 0.05` is `False` — and to crash on `None`. That is one instance of a class, not a bug in one
gate: **any gate that compares a measured quantity must decide what it does with a quantity that was not
measured.** Rule 13(b) already states the answer — an unmeasurable quantity is not a zero — and rule 13(a)
says a condition without a denominator is not a condition.

The probes below were run against the synthetic fixture each gate is self-tested on, mutating one field to
`None` or `nan`. "Before" is the behaviour on the pre-audit code.

| Gate | Unmeasurable input probed | Before | After |
| --- | --- | --- | --- |
| **C1** path separation | `K = nan` on an `A-K+` row | **PASS** — `nan` is truthy, so the row counted as retained | fails |
| **C1** path separation | `K = None` on an `A-K+` row | fails (by accident: `None` is falsy) | fails, explicitly |
| **C2** treatment consistency | `A = None` on an `A-K+` row | **PASS** — `not None` is `True`, so "A driven to zero" was satisfied by a hole | fails |
| **C3** positivity | no measured quantity | structurally safe | unchanged |
| **C4** no interference | `nan` / `None` delta | **PASS** / crash | failed, fixed earlier today |
| **C5** common cause | `strength = None`, malformed cycle | fails | unchanged |
| **C6** order variation | read from `c6_timing_block.json` | not computed here; no such input | unchanged |
| **C7** assertion block | `nan` delta, `None` delta, `inf` delta, missing path | **PASS** on `nan`, **crash** on `None`, crash on a missing path | fails |
| **C7** assertion block | `Y = nan` | **PASS** — `nan` truthy, so the rate looked higher, and a higher Y- rate read as "not lowered"… in the fixture it happened to fail; on a real row it can pass | fails |
| **C8** third route | `Y = None` on an `A-K-` row | **PASS** — `None` is falsy, so an unmeasured control read as 0% asserted, which is the best possible control | fails |
| **C9** same object | `fingerprint = None` | fails | unchanged |

## What was repaired

Two shared defects, not four separate patches.

**1. A rate whose numerator is unmeasured is not a rate.** `_fraction` computed
`sum(1 for row in rows if row[field]) / len(rows)`, which reads `nan` as retained (truthy) and `None` as not
retained (falsy). It now returns `None` unless every row's flag is a real observation, and C1, C7 and C8
treat `None` as a failure. This is what closed C1's `nan → PASS`, C8's `None → PASS`, and C7's `Y` comparison.

**2. A delta that is not a number is not within tolerance.** `_delta_clean` refuses a missing path, a null, a
non-numeric and a non-finite value, and C4 and C7 both use it. The C4 repair was this function written in
place; making it shared is what closed C7's identical `nan → PASS` and its `None → crash`.

C2 was the third case and is not a comparison at all: it asks whether a manipulated path is `False`, and
`not None` answers `True`. It now requires a measurable flag before it reads one, on both the primary and the
`Y-` branches.

## Two layers under the gates

Probing the gates only asks what happens when an unmeasurable value *reaches* them. Two functions sit
upstream and downstream of the veto, and both carried the same defect.

| Layer | Function | Probe | Before | After |
| --- | --- | --- | --- | --- |
| Join (producer) | `attach_neighbor_deltas` | a null or non-numeric `A_rate` on a paired row | **`TypeError` / `ValueError`** — the delta could not be represented, so assembly crashed | writes `"A": null` and `delta_status = "UNMEASURABLE"`, which C4 already classifies as `C4_UNMEASURABLE` |
| Scorer (downstream) | `score_c1` | a `nan` flag among a seed's `A-` rows | **per-seed `pass: True`** and a `nan` in `a_minus_fraction`; the top-level verdict was safe only because it delegates to `gate_c1` | per-seed `pass: False`, fractions reported as `null`, never `nan` |

The join is the more interesting one: a null rate did not produce a wrong number, it produced **an
exception**, which is the gate being unable to express the state it exists to model. `score_c1` repeated the
gate's own defect one layer down — its per-seed rows and reported fractions used a local
`sum(1 for row if row[field])`, so a `nan` (truthy) was reported as retained. Both now use
`measurable_fraction`, the single rule the gates use, which is why the repair is a rename rather than a third
copy of the check.

## The reason-code gap, and how it was decided

`_c1_reason` classifies a failed C1 by its **denominators** — no denominator, below floor, or otherwise
`C1_THRESHOLD`. A seed whose denominator is fine but whose retention rate is unmeasurable therefore VOIDs with
`C1_THRESHOLD`, which says *"retention fell below 0.95"* about a rate that was never computed. The disposition
is right (VOID, not pass); the label is wrong.

This was **not** repaired in the audit, because the reason codes are adopted vocabulary in
[`A1-C1-C4-VOID-GATE-1`](A1-C1-C4-VOID-GATE.md) and inventing a code would amend an owner decision inside a bug
fix. It was put to the owner the same day and decided:
[`DECISION-A1-C1-UNMEASURABLE-1`](DECISION-A1-C1-UNMEASURABLE.md) adds `C1_UNMEASURABLE` and narrows
`C1_THRESHOLD` to a measured rate below 0.95, with the precedence
`C1_NO_DENOMINATOR` → `C1_DENOMINATOR_BELOW_FLOOR` → `C1_UNMEASURABLE` → `C1_THRESHOLD`.

## What this does not claim

- **It does not make the gates total.** A flag of the wrong type (a string, a list) still fails closed rather
  than being classified; the gates answer "not measurable" and the run voids, which is the intended disposition.
- **It changes no measured verdict.** Every repair makes an unmeasurable row fail where it previously passed or
  crashed. On the audit fixture — all flags measured, all deltas finite — all eight gates still accept, which
  `--self-test` asserts and the nine new tests in `tests/test_a1_gate_measurability.py` pin.
- **It says nothing about whether a row should have been measurable.** "Missing" is the producer's failure to
  record; the gate's job is only to refuse to score it.

## Reproduce

```bash
python -m benchmarks.a1_gate_readiness --self-test    # each gate accepts its fixture, rejects its defect
python -m pytest tests/test_a1_gate_measurability.py -q
```

The nine tests are the probe table above, executable: C1 `nan`/`None`, C2 `None` on four rows, C7 `nan`/`inf`/
`None`/missing-path/`nan` `Y`, C8 `None`/`nan`, plus the passing fixture.
