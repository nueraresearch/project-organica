# A degree-invariant strength, and its held-out confirmation — pre-registration

**Status: PREREGISTRATION, 2026-11-07. Written before any held-out cell. One
reference-arm check had already run and is disclosed in §5.**

`docs/DECAY-FIX-CONFIRMATION-PREREGISTRATION.md` §18 closed the
transition-probability candidate at its calibration stage: neither the transition
arm nor the ratio control had a threshold in the committed grid that was live on
every degree *and* kept precision at 0.95 on every degree, so both carry "no
global threshold clears all degree regimes". §18 also says a revival needs a new
pre-registration with its own seeds and its decision rule fixed before cells.
This is that document.

## 1. Why a threshold sweep could not have worked

Every strength of the form *this edge's share of its source's flow* is
approximately `1 / out-degree` for a uniform source. The shipped ratio is one of
those, and transition probability is another. So the calibration gates bound at
opposite ends of one ladder: a threshold high enough to keep precision at degree
4 starves degree 12, and a threshold low enough for degree 12 admits everything
at degree 4. That is a property of the measure, not of the threshold, and no
grid over a single number can remove it.

The defect the 0.12.0 collapse rests on is separate and additive: the ratio's
numerator is decayed while its denominator, a cumulative source frequency, only
grows. Decay is therefore monotone in strength by construction.

## 2. The change

Prediction strength becomes a **lift over a uniform draw** from the same source,
computed from the same decayed counts:

```
uniform_share = out_total / out_degree
lift          = count / uniform_share
strength      = min(1, STABLE_THRESHOLD * lift)
```

- `out_total` and `count` are counts of the same decayed temporal edges, so
  uniform decay cancels out of the ratio and a stationary stream has a
  stationary strength.
- Dividing by the uniform share removes the degree dependence: a uniform
  transition has lift 1.0 at every degree, so one threshold means one thing
  across the ladder.
- Scaling by `STABLE_THRESHOLD` means the engine's existing filter
  (`strength >= STABLE_THRESHOLD`) admits exactly `lift >= 1`. **No threshold is
  recalibrated and no constant is changed**, which is what distinguishes this
  from the candidate §18 rejected.
- The ratio and transition probability stay in the candidate's evidence, so the
  old quantities remain auditable and the change is attributable.

**One mechanism, one parameter, fixed by construction.** `lift >= 1` is "at
least as frequent as a uniform draw", declared here rather than selected from a
grid. A value other than 1 would be a different claim and is out of scope.

## 3. The reference arm

The falsifier from the change-to-failure map: 300 cycles on the pinned engine,
and live theories throughout would mean the mechanism was never what caused the
death. This is a check, not the confirmation:

| run | cycles | theories | beliefs | TDC |
|---|---|---|---|---|
| shipped 0.13.0 (`docs/decay_falsifier.json`) | 300 | 37 of 300, last at 38 | 112, last at 113 | 0.123 |
| 0.12.0 reference (`docs/rerun-0.12.0/parts/FULL.json`) | 3,000 | 37, last at 38 | 112, last at 113 | 0.123 |

## 4. Arms

| arm | strength | threshold | what it is |
|---|---|---|---|
| **E** engine | lift over uniform | 0.30 (unchanged) | the change under test |
| **S** shipped control | `count / source_frequency` | 0.30 (unchanged) | the formula restored by subclass, so the comparison is the same code path |

The control is a harness subclass of `_build_predictions` that overwrites the
candidate strength from the recorded `ratio`. It exists because the engine now
computes the lift: without it there would be no baseline at all, and the
run would compare the change with itself.

## 5. What had already run, and why it does not choose anything

Before this document, the reference-arm check in §6 was run once on the matrix
stimulus with the matrix's own seed (`20261023`, 300 cycles): theories in 299 of
300 cycles, final 5; beliefs 299 of 300, final 15; `TDC = 0.997` against 0.123.
It is disclosed because it was seen first. It selects no parameter — the
threshold is fixed by construction in §2, the seeds below were chosen by scan,
and no cell in §7 had run when this was written.

## 6. Held-out block, chosen by scan

- Seeds `20300401`–`20300404`, computed by scanning every seed-bearing artifact
  under `docs/` and taken from a window above `20300301`. The harness reruns the
  scan on every invocation and refuses to start if any of the four is claimed.
  No seed is added, dropped or substituted after the first cell.
- Degree regimes **4** and **12**: the two that bound the failed calibration, a
  mid-degree world and the hub. Each world's realised out-degree is measured and
  recorded; a cell whose realised degree differs from its label is not
  comparable and is excluded (rule 13a).
- 300 cycles, both arms, one run per cell. Nothing is pooled across degrees.

## 7. Decision rule, fixed now

Evaluated once by `benchmarks/decay_fix_confirm.py --analyze`, on these cells
only. `CONFIRMED` requires all of:

1. **Liveness.** Arm E is live — at least one theory in the final 10 % of cycles
   and mean beliefs of at least 2 — in at least 90 % of cells at degree 4 **and**
   at degree 12. At four seeds that is 4 of 4.
2. **Honesty.** Zero false assertions in at least 90 % of cells at both degrees.
3. **Coverage at the hub.** Median coverage at degree 12 is at least 0.50.

The shipped control is reported beside every cell. It is expected to fail
liveness at high degree — `docs/DECAY-FIX-CONFIRMATION-PREREGISTRATION.md`
Amendment 1 established that the shipped formula forms no stable hub edge at
degree 4 and above — so its absence is recorded as its known ceiling and is
**not** counted as a win for arm E.

## 8. Falsifiers

- Arm E not live at degree 12 means the degree-invariance claim is false and the
  hub starvation has moved rather than been removed.
- Strength not at the uniform share for a uniform source means the formula is
  wrong, not the world.
- Coverage below 0.50 at degree 12 with liveness passing means structure forms
  but is not the world's structure: precision without coverage.

## 9. What this run cannot say

- **Four seeds per degree.** It separates a live arm from a dead one; it is not
  an estimate of coverage or precision, and no interval is quoted.
- **Precision is not evaluated below 40 stable edges**, per the earlier
  protocol's §8: a ratio over eighteen edges is not a precision estimate.
- **No task endpoint.** Held-out next-tag log-loss over the strongest simple
  baseline is not measured here, so nothing here says the arm predicts better
  than a bigram — only that it stays alive and asserts the world's edges.
- **Two degrees, one stimulus family, 300 cycles.** No claim is made beyond
  them, and none is made about the 3,000-cycle matrix until it is rerun.

## 10. Stop condition

The build is finished when the change is in `organica/sleep_extraction.py` with
its unit tests, the harness runs cells and analysis, and this document fixes the
rule. No feature may be added afterwards; defects may be fixed. If §7 fails,
the fix is not adopted and the engine returns to 0.13.0's behaviour with this
document recording why.

## 11. Adoption, if it passes

The version bump (`0.13.0` → `0.14.0`), the changelog entry, the re-pinned
engine hashes and the manual's action row are the same change as the result.
The 3,000-cycle matrix rerun is downstream and is not authorised by this
document.

## Amendment 1 — the stimulus cannot carry the dependent variable (2026-11-07, after a block, before the replacement cells)

The first held-out block ran and is **excluded as NOT COMPARABLE**. It is
reported here rather than deleted, and it changes no criterion.

**What happened.** All sixteen cells (degrees 4 and 12, four seeds, both arms)
returned zero theories, so no cell could be judged on liveness. The engine arm
did form stable structure — 12 stable edges and coverage 0.67 at degree 4, 32
and 0.59 at degree 12 — and the shipped control formed none (0 stable edges,
coverage 0.0) on the same worlds and seeds. A cell with no theory in any cycle
has no liveness measurement, so scoring it as a failure would be reporting an
unmeasurable quantity as zero (rule 13b), and scoring it as a pass would be
worse.

**Why the world is at fault, not the arms.** `degree_world` builds its stimulus
with `scale_stream`, a generator this project's diagnosis never used, while the
matrix and every recorded theory run use `lattice_stream` on
`L1_hub1_t3_disjoint` — three triangles on one hub, realised hub out-degree 6.
The reference-arm check in section 3 uses that lattice and holds five theories
for its whole run. The two generators present different event orders for the
same triangles, and only the lattice one has ever carried Layer 5 in this
repository. That is a property of the stimulus that should have been audited
before the block ran: rule 13(a) asks whether the design can produce the
variable it scores, and this one could not.

**The replacement, fixed before its first cell.**

* **Generator:** `lattice_stream` on triangles that share one hub (`alpha`), the
  matrix's own construction.
* **Degimes:** hub out-degree **6** (three triangles, the matrix's L1 working
  point) and **12** (six triangles). The degree is measured from each world's
  own edge set and recorded; a cell whose realised degree differs from its label
  is not comparable and is excluded.
* **Seeds:** `20300405`–`20300408`, scanned free before use; the previous block
  is spent and is never reused.
* **Everything else is unchanged**, including the arms, the 300 cycles, the
  liveness definition, the honesty rule, the coverage floor at degree 12 and the
  evaluation script.

**Disclosure.** The engine arm's stable-edge result on the discarded block is
recorded beside the new cells and is not used as evidence for adoption; only the
replacement block is scored.

## 12. Result — NOT CONFIRMED (2026-11-07)

The held-out block fixed by Amendment 1 ran once: `lattice_stream` on
`expanding_triangles`, hub `alpha`, degrees 6 and 12, seeds 20300405-20300408,
300 cycles, both arms, 16 cells. The analyzer writes
`docs/decay_fix_confirm.json`; its verdict is **NOT CONFIRMED**.

**Engine arm (E).** Live in 4 of 4 cells at degree 6 and 4 of 4 at degree 12.
Median coverage 0.60 at degree 6 (median 18 stable edges of 30) and 0.40 at
degree 12 (median 24 of 60).

**Shipped control (S).** Live in 0 of 8 cells, 0 stable edges, coverage 0.00.
As section 7 says, that is its known ceiling and is not counted as a win for E.

**Decision.** Liveness passes at both degrees that ran. Coverage at degree 12
fails at 0.40 against the pre-committed 0.50, which is the section 8 falsifier
"structure forms but is not the world's structure: precision without coverage".
The rule is judged whole and the bar is not recomputed from the cells it judged
(rules 14 and 19).

**Two disclosures.** Section 7 names degree 4 for the liveness criterion while
Amendment 1 replaced the block with degrees 6 and 12; the slip does not reach
the verdict, because liveness passes at both degrees actually run and coverage
fails on its own. And the reference-arm observation in section 3 - 299 of 300
cycles live, 5 theories, 15 beliefs, TDC 0.997 against 0.123 - remains a
measurement of the candidate build that this document does not adopt, not a
statement about the engine.

**Stop condition executed.** `organica/sleep_extraction.py` is reverted to its
0.13.0 behaviour, `tests/test_decay_fix.py` is retired with it, and no version
bump, changelog entry, re-pin or manual behaviour row accompanies this result.
`benchmarks/decay_fix_confirm.py` is kept as the record of the experiment; with
the engine reverted both of its arms run the shipped formula, so it reproduces
arm S twice rather than the block above.

**What this leaves open.** Whether a fixed theory budget can express enough of a
degree-12 lattice to meet a 0.50 coverage bar at all is a separate question with
its own pre-registration; it is not licensed by this document, and the failed
bar is not evidence that the bar was wrong.
