# The `DI` measurement window: Stage A, and a Stage B that is not authorised

**Status: exploratory measurement design. No engine run, no seed allocated, no reliability coefficient, no window adopted.**
Stage A reads the 240 stored Phase L records; Stage B is specified here and not executed.
Every number is written by `benchmarks/di_window_design.py` into `docs/di_window_design.json`, and
`tests/test_di_measurement_window.py` asserts this document against that artifact.

This document answers the five Stage A questions the owner set, and it reports one result he did not ask for
and which changes the design more than the window does: **the record contains no settled state for a window to
measure, and 98 % of the endpoint's variance is between configurations rather than inside one.** The
within-configuration spread is real but narrow — 0.44 pairs at the latest window — and §4 carries a dated
correction to an earlier, stronger reading of it.

---

## 1. What is preserved

- The 240 Phase L records, untouched: the same file, the same seeds, the same values.
- The protocol's window (110–150), untouched: it is still written in `docs/STRUCTURE-BEHAVIOR-DESIGN.md` §2 and
  §4, with a dated note that it is contested and unresolved.
- The construct audit's verdict, untouched: `DI` is a **state at a designated time**, measured by one cycle's
  report, quantised in steps of 1/18.
- V1 and its results, untouched. The sample-size discussion stays paused.

This is a design decision informed by a failure, not a revision of the record. Nothing above is re-scored.

---

## 2. The constraints the audit established, restated as design constraints

| Constraint | Consequence for a window |
| --- | --- |
| `DI` is 0 before the late material arrives | a window ending before arrival measures the floor, not the organism |
| `DI` is a per-cycle snapshot, not an accumulator | a decrease may be omission or decay; the instrument cannot separate them |
| the denominator is 18 pairs | the resolution is one pair; differences below 0.0556 cannot exist |
| the settled reading is configuration-dominated | the ICC of 0.890 is **not** a repeatability coefficient — each world is read once, so it cannot say whether the same world scored twice would agree. It says `DI` separates configurations. |
| four of eight configurations never express `DI` | a window "informative across all configurations" does not exist for this axis |

The last row is the one that reorganises the problem, and §4 gives it a number.

---

## 3. Stage A: when `DI` emerges, and whether the record contains a settled state

### 3.1 Emergence, per configuration

| configuration | runs ever non-zero | median first non-zero | median first **sustained** (10 cycles) |
| --- | --- | --- | --- |
| `1:1` | 1 / 30 | 150 | **never** |
| `1:2` | 1 / 30 | 150 | **never** |
| `1:3` | 1 / 30 | 150 | **never** |
| `1:4` | 1 / 30 | 154 | **never** |
| `2:1` | 29 / 30 | 539 | 539 |
| `3:1` | 30 / 30 | 401 | 404 |
| `4:1` | 30 / 30 | 362 | 362 |
| `6:1` | 30 / 30 | 329 | 329 |

The single non-zero reading in each `1:x` configuration is a one-cycle blip at the arrival boundary (cycles
150–154); no run in those four configurations holds a non-zero value for ten consecutive cycles. **117 of the
240 runs never leave zero at all**, and the four configurations that produce them are the four on the
late-disadvantaged side of the support ratio. That is the project's own AGENTS 13a condition in its exact
form: on those arms the manipulated quantity produces no measurable `DI`, so they are a dead axis for this
endpoint rather than a low-`DI` condition.

### 3.2 Settling — and why the record cannot supply a window

Among the 119 runs that ever move:

| configuration | runs that move | median settle cycle | max settle cycle | runs still moving in the last 50 cycles |
| --- | --- | --- | --- | --- |
| `2:1` | 29 | 589 | 599 | 25 |
| `3:1` | 30 | 590 | 599 | 25 |
| `4:1` | 30 | 586 | 599 | 27 |
| `6:1` | 30 | 586 | 599 | 25 |

"Settled" here is a mechanical definition: the last cycle at which the run's value differs from its own final
value by at least one pair. **A median settle cycle of 586 in a 600-cycle run, and 25–27 of 30 runs still
changing in the last 50 cycles, means the run ends while the transition is still going.** No asymptote is demonstrated anywhere in this record; it holds the first 600 cycles of a transition that is
still in progress.

That single fact rules out the obvious repair. Moving the window to the end of these runs would place it
inside the transition for most runs, and the "settled" window at cycles 550–600 is settled only in the
arithmetic sense that each run's last change happened near the end. **No cycle number can be selected from
this record without being an artefact of where the run happened to stop**, which is exactly the caution the
owner raised against choosing 600 because it looks informative.

That last-change statistic is also **not evidence of an asymptote**, and the word is now retired from these
documents. `docs/DI-TRANSITION-CONSTRUCT.md` §4 separates the three criteria it had been conflating: entry into
a one-pair band (median persistence **13 cycles**), persistence for a stated duration (17 of 119 runs reach 50
cycles, 4 reach 100), and no remaining trend (96 of 119 runs moved by at least two pairs over the final 100
cycles). Only **4 of 119** moving runs satisfy the last two together. A future run may claim an asymptote only
if both are declared before it runs and both are met afterwards.

---

## 4. Stage A: the predictor variance that a within-configuration test would have

The protocol's claim is *within one generating configuration* (§1 of the design record). That clause fixes
which variance matters: not the spread across configurations, but the spread across worlds inside one.

| candidate window (40 cycles) | within-config SD, median | within-config SD, max | within-config share of variance | configurations with a single value |
| --- | --- | --- | --- | --- |
| 150–190 | 0.01 pairs | 0.05 | 0.984 | 8 |
| 210–250 | 0.00 | 0.00 | 0.000 | 8 |
| 260–300 | 0.00 | 0.05 | 0.971 | 8 |
| 310–350 | 0.00 | 0.86 | 0.411 | 6 |
| 360–400 | 0.00 | 1.36 | 0.063 | 5 |
| 410–450 | 0.00 | 1.53 | 0.039 | 5 |
| 460–500 | 0.06 | 2.02 | 0.028 | 4 |
| 510–550 | 0.39 | 1.74 | 0.020 | 4 |
| 560–600 | 0.44 | 1.72 | 0.020 | 4 |

Two readings, both unfavourable and both robust across the whole range:

1. **The within-configuration spread never exceeds about two pairs, and its median is under one pair.** In the
   settled window the per-configuration spread is `2:1` SD 1.62 pairs over
   0–6 pairs, `3:1` 1.03 over 9–14, `4:1` 1.04 over 11–15, `6:1` 0.86 over 11–15.
2. **At least 97 % of the predictor's variance is between configurations**, at every window from 460 cycles
   onward (97.2 % at 460–500, 98.0 % at 510–550 and 560–600). A rank correlation computed inside one configuration would therefore rest on a predictor
   that moves by roughly one pair across worlds, while the same predictor moves by six or more pairs across
   the arms.

**Correction (2026-11-02).** An earlier version of this section put that spread "against a resolution of one
pair" and concluded that the design removes the dynamic range. That comparison was wrong, and the conclusion is
withdrawn. The quantum of 0.0556 pairs is the resolution of a **single-cycle** reading; a 40-cycle mean moves in
steps of 1/(18 × 40) pairs, so 0.44 pairs is a real spread of about eight single-cycle quanta, not a value
sitting on a floor. What the table actually shows is narrower, and still matters: the settled window is 98 %
arm-determined, so a **pooled** relation would be an arm effect restated — which is why the protocol computes the
relation within a configuration. The decisive defect is not the size of the spread but §3.2: there is no settled
state in this record for the window to measure. `docs/DI-TRANSITION-CONSTRUCT.md` §2 carries the corrected
comparison for the candidate predictors, where onset varies by 12.4 cycles on a one-cycle grid and exposure by
0.44 pairs on a fine one — both real, neither sub-resolution.

---

## 5. Stage A: the schedule

The protocol keeps a strict order: structural measurement, then revision learning, then the held-out test.

| quantity | cycles |
| --- | --- |
| protocol's run length | 150 |
| protocol's measurement ends at | 150 |
| median settle cycle (runs that move) | 586 |
| median entry into a one-pair band, sustained-onset runs | 587 |
| run length needed for settled measurement, then 50 learning, then 50 test | **686** |

The protocol's run is **4.6× too short** for the sequence it specifies, on the only per-cycle evidence the
project holds. That is a schedule defect, not an adjustment: within 150 cycles this endpoint cannot be
measured after its transition and still leave room for the behavioural limb that follows it.

---

## 6. What Stage A proposes — and what it refuses to propose

**It refuses to propose a cycle number.** Every number available would be read off a transition that is still
running, so a specific window would encode the run length rather than the organism. Choosing 600 because it is
where the data ends is the same error as choosing 110–150 because it was where the previous protocol said.

**It proposes a measurement design, in the order the questions have to be answered:**

1. **Runs long enough to satisfy a declared stopping criterion**, with the length and the criterion both
   declared before running and the criterion demonstrated afterwards — not assumed. On this evidence 150 cycles
   cannot work and 600 does not suffice; the length is a Stage B output, not a Stage A choice. The criterion is
   a pair of conditions, not one statistic: persistence inside a one-pair band for a stated number of cycles,
   and no remaining trend over a stated span (§4 of `docs/DI-TRANSITION-CONSTRUCT.md`).
2. **A window placed after that criterion is met**, with its tolerance declared, and with the window's own
   length fixed rather than tuned.
3. **Two disjoint late-pair sets of equal size**, so that the reliability question can eventually be asked as
   parallel forms rather than as a split over time. This is also the only route to the resolution problem: more
   late pairs per set means a finer grid and a wider within-configuration range.
4. **The predictor's within-configuration spread reported beside every relation**, because §4 shows that the
   quantity that decides whether the test can work at all is not the correlation but the predictor's range.
5. **Only then** reliability and sample size — which stays paused, and which will need the attenuation curve
   re-derived for whatever denominator the parallel forms finally have.

**That alternative has since been decided, explicitly, and it is a different construct.** On 2026-11-02 the
owner made a transition summary the primary candidate predictor and kept the settled state as a separate,
unresolved construct. `docs/DI-TRANSITION-CONSTRUCT.md` records the audit that decision required and chooses
**onset of `DI`** as the primary summary: it is defined on a one-cycle grid, it varies within a configuration by
12.4 cycles in `6:1`, and — unlike slope or accumulated exposure — its value cannot change because the run was
stopped early. Slope is recorded as exploratory and currently unestimable, its ranking reversing (-0.315) when
the run is cut at cycle 450. Nothing about that decision moves the window, and it consumes no seed.

---

## 7. Stage B: independent validation, specified and not run

Stage A has a selection problem it cannot resolve from inside: the same 240 records that revealed the defect
would also be used to place the repair. So a window chosen on them is exploratory, and must be validated on
worlds that were **not** used to choose it.

**Design.** Fresh methodology worlds from the frozen engine, generated on seeds disjoint from every Phase L
seed and from every confirmatory seed block; the same generator, the same readout, the same measurement code.
The window, the run length and the tolerance are declared before any of these worlds is run.

**Pre-committed criteria** (all four, judged whole, no re-scoring):

1. **Non-degenerate.** The measurement is not identically zero on the configurations it is declared for, on the
   same 30-run basis that exposed the `1:x` arms here.
2. **Resolution.** Within-configuration spread is at least two pairs at the declared window, so the predictor
   can distinguish worlds at a granularity better than its own floor.
3. **Consistency.** The declared stopping criterion is met, within its stated tolerance, in every configuration
   the endpoint claims; configurations that never reach it are reported as out of scope rather than pooled.
4. **Ordering.** The measurement window ends strictly before revision learning begins, and the overlap between
   the pair set behind `DI` and the withheld test set is measured and empty.

**Failure rule.** If any criterion fails, the window is rejected and no confirmatory seed is allocated. A
rejection is recorded as the design's result, not renegotiated into a smaller claim.

**Cost.** Stage B spends methodology seeds, so it is **not authorised here**: no seed is allocated, no world is
generated, and the owner decides whether and when to run it. Nothing in this document commits the project to it.

---

## 8. The five Stage A questions, answered

| Question | Answer |
| --- | --- |
| 1. When does meaningful `DI` emergence begin? | configuration-dependent: median first sustained non-zero at 329 (`6:1`), 362 (`4:1`), 404 (`3:1`), 539 (`2:1`); never in `1:1`–`1:4` |
| 2. When does the transition reach an informative state? | **not within this record** — median settle 586 of 600, with 25–27 of 30 runs per arm still changing in the last 50 cycles |
| 3. Is there a defensible interval across all configurations? | **no** — four configurations never express `DI` sustainably, so they are out of scope for this endpoint rather than a low-`DI` condition |
| 4. Is the snapshot sufficiently informative there? | **not at the only offset with signal**: no settled state exists to measure there (§3.2), and 98 % of variance is between configurations |
| 5. Does the behavioural endpoint occur after the measurement? | not in a 150-cycle run: a settled measurement plus the protocol's 50-cycle learning and 50-cycle test needs 686 cycles |

---

## 9. What this changes, and what it does not

- **It changes the design problem.** The window is not the only defect; the endpoint's within-configuration
  dynamic range is too small to carry a within-configuration claim, and the run is too short for its own
  schedule. A new window alone would not fix either.
- **It does not change the record.** 240 records intact, protocol window intact and flagged, construct verdict
  intact, V1 intact, review gate intact and §7 still empty.
- **It does not allocate anything.** No seed, no world, no run. Stage B is specified so it can be authorised or
  refused on its own terms, and the sample-size discussion remains paused.

---

## 10. Verification

```bash
./.venv/bin/python -m benchmarks.di_window_design      # regenerates docs/di_window_design.json
./.venv/bin/python -m pytest tests/test_di_measurement_window.py -q
```

The test recomputes the artifact, asserts every number quoted here against it, asserts that the five Stage A
questions are answered, and asserts that the document neither adopts a window nor reports a reliability
coefficient. The transition construct has its own artifact and test, `docs/DI-TRANSITION-CONSTRUCT.md` and
`tests/test_di_transition_construct.py`. The full suite was green on the commit that added this document; the count is not repeated here,
because a test count in a document goes stale the next time a test is added.
