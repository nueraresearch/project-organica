# The confidence-formula amendment — pre-registration

**Status: authorized 2026-11-04, committed before any cell runs.** The owner's
decision is recorded in `docs/USER-MANUAL.md` action row 50. This document is
the protocol; it is fixed before the harness exists and may not be edited to
match a result. An amendment is a new dated section, published with the reason.

## 0. What is being changed, and what is not

Confidence is a **share**:

```
confidence = support / (support + contradiction)
```

where `contradiction` is the subject's competing flow — the count of transitions
to *other* successors, not observations that contradicted the claim
(AGENTS rule 17a). This is the expression at `organica/sleep.py:1495`, and the
belief dies when `confidence < DEATH_THRESHOLD` (0.15) with at least three
observations against it.

The amendment replaces that expression with a **smoothed posterior**:

```
confidence = (support + alpha) / (support + contradiction + alpha + beta)
```

Three things are **not** changed, and are not being tested here:

1. **`organica/` is not modified.** The engine is frozen at `v0.9.0`
   (AGENTS rule 12) and `tests/test_v1_freeze.py` must stay green. The
   amendment is applied as an in-process override in `benchmarks/`, which is
   where this project's ablations already live, so the archival engine, the two
   deposited papers and the software record keep meaning what they said.
2. **Nothing else in the cognition changes.** Which structures compete, how
   layers select candidates, the death threshold, the lookback, the caps and
   the streams are all held exactly as they are. One expression moves.
3. **No existing result is revised.** The frozen engine's record stands as
   measured. A result here is a result about a different engine, and the papers
   are not edited to absorb it.

Promoting the posterior into a tagged engine (`v1.1`) is a **separate owner
decision** and is not implied by this protocol.

## 1. The question

The recorded finding is conditional in a way that has never been tested:

> G5 (theories and questions) appears on the engineered study stream, and does
> **not** appear on the one unengineered stimulus; and widening the temporal
> lookback from 3 to 30 destroys it.

The proposed mechanism is that the share is the binding constraint: a subject
with many successors dilutes every minority expectation, so a belief about a
genuinely split subject collapses below the death threshold however much
evidence accumulates. If that account is right, the posterior should (a) make
G5 insensitive to the lookback width and (b) let G5 appear without a stream
that was designed to contain a branch point.

**The question is therefore not "does the formula change behaviour" — it
obviously does — but "was the formula the constraint, or is G5's dependence on
an engineered stream structural?"**

## 2. The arms

| Arm | Formula | Role |
|---|---|---|
| `share` | `support / (support + contradiction)` | the frozen engine, run through the harness unchanged |
| `jeffreys` | `(support + 0.5) / (support + contradiction + 1.0)` | the amendment, primary |
| `laplace` | `(support + 1.0) / (support + contradiction + 2.0)` | the amendment, sensitivity |

`jeffreys` is primary because it is the standard non-informative prior for a
proportion and it maps a 10-to-10 split to exactly 0.5. `laplace` exists so
that the alpha/beta choice cannot silently do the work: if the two posterior
arms disagree about the direction of P1, the result is a statement about the
prior family and not about the amendment.

## 3. The streams

Six conditions of the existing cold-start harness, unchanged, at 40 cycles:

`baseline`, `no_branch`, `cold_start`, `cold_start_unbranched`,
`real_git_history`, `wide_lookback`

The three that carry the question are `wide_lookback` (the ablation that
destroyed G5), and `cold_start_unbranched` / `real_git_history` (the
unengineered conditions). `baseline` is the regression check. The full grid is
six streams x three arms x twelve seeds = **216 cells**, each 40 cycles, with no
extension of the horizon after any result is seen.

## 4. Seeds

A fresh block, allocated at authorization because no existing block is free and
the Stage B spares must not be drawn:

- **confirmatory:** `700001001`–`700001012` (twelve seeds, every cell of the grid)
- **reserve:** `700001013`–`700001024` — held, never drawn, not substitutable

Every cell runs all twelve seeds. A cell that cannot run is reported as not
measured, never dropped and never replaced by a reserve seed without a dated
amendment published before the replacement runs.

The harness varies the engine's only source of stochasticity, its fixed
`RANDOM_SEED`, and nothing else; the streams, the cycle count and the event
delivery are identical across arms.

## 5. What is measured

**Primary (criterion-bearing).** For each cell, whether G5 appeared within 40
cycles and at which cycle — the harness's existing
`cycles_to_first_emergence["G5 theories"]`.

**Descriptive (no criterion).** `competing_subjects_final`, the final
population of each generation, and the confidence of surviving hypotheses at
the final cycle. The last is reported because the mechanism predicts beliefs no
longer collapsing toward the death threshold; it is **descriptive only**, and
no pass or fail is attached to it, so a shift in it cannot rescue a failed
prediction.

## 6. Predictions, and the premise they rest on

**P1 — the lookback stops mattering.** Under `jeffreys`, `wide_lookback` reaches
G5 in **at least 9 of 12** seeds; under `share`, in **at most 1 of 12**.

**Premise check (P0).** P1 is only readable if the frozen engine still fails the
way the record says it does. If `share` reaches G5 on `wide_lookback` in **6 or
more of 12** seeds, the recorded "widening the lookback destroys G5" is not
reproduced and P1 is **not read**; the non-reproduction is the finding.

**P2 — G5 without an engineered stream.** Under `jeffreys`, G5 appears in at
least **6 of 12** seeds on at least one of `cold_start_unbranched`,
`real_git_history`; under `share`, in at most **1 of 12** on each of them.

**P3 — no regression.** Under `jeffreys`, `baseline` reaches G5 in at least
**11 of 12** seeds, and at a median cycle no later than the `share` arm's median
plus 2 cycles.

## 7. Controls

Each control can fail, and a failed control voids the reading rather than being
explained away.

- **C1 — the override is behaviour-identical when it does not change anything.**
  A `share_reimplemented` subclass recomputes the frozen `share` expression
  verbatim, subject to the same death rule. Over all six streams and twelve
  seeds it must reproduce the `share` arm **exactly**, cycle for cycle. If one
  cell differs, the harness has changed more than the formula and the study is
  void (R3).
- **C2 — the independent variable is live.** At least one cell must differ
  between `share` and each posterior arm in G5 appearance or final population.
  A formula change that alters nothing is a defect in the override, not a null
  result (AGENTS rule 13a).
- **C3 — the stream is reachable.** `baseline` under `share` must reach G5 in at
  least 11 of 12 seeds. If the control stream cannot produce G5 under the frozen
  engine, no absence elsewhere is interpretable.

## 8. Readings

- **R1 — the formula was the constraint.** C1, C2 and C3 pass; P0 does not fire;
  P1 and P2 are met. G5's dependence on an engineered branch point is then a
  property of the confidence formula, not of the architecture, and Paper 01's
  boundary needs a companion record rather than a revision.
- **R2 — partly, and named as such.** C1, C2 and C3 pass, but exactly one of P1
  or P2 is met, or P0 fires, or `jeffreys` and `laplace` disagree in direction.
  The met half is reported as met and the unmet half as unmet; neither is
  allowed to stand for the other, and no claim about "the formula" is made.
- **R3 — void.** Any of C1, C2 or C3 fails. Nothing is read. The reason is
  reported with the arm and cell that fired it, as the jitter diagnostic
  reported its own R3.

## 9. Stop conditions

The grid is fixed at 216 cells. No stream, arm, seed or cycle count is added
after a result is seen; a new question is a new pre-registration. The run
reports every cell, including cells that did not finish, which are reported as
not measured.

## 10. What this cannot show

- It cannot show that the posterior is *more human-like*, or that G5 as this
  project defines it is intelligence. It measures the appearance of a structure
  in a frozen ladder.
- It cannot show that the posterior is better on any external task. No external
  task family is part of this protocol.
- It cannot license retroactive claims about the deposited papers, whose engine
  is unchanged and whose results stand as measured.

## 11. Provenance

- Decision: owner, 2026-11-04 (`docs/USER-MANUAL.md` action row 50).
- The expression under test: `organica/sleep.py:1495`; death rule `:1499`.
- The streams and the harness: `benchmarks/cold_start.py`, unchanged.
- The proposal's origin: `docs/USER-MANUAL.md` §8.1 and journal §7 and §14.5.
- The recorded finding this tests: the cold-start study and the `wide_lookback`
  ablation, as reported in `docs/FACTS-SHEET.md` (B5) and the manual's §8.1.
