# The `DI` construct audit

**Status: read-only. No engine run, no seed spent, and no reliability coefficient computed.**
Every number below is written by `benchmarks/di_construct_audit.py` into
`docs/di_construct_audit.json` from the 240 stored Phase L records, and `tests/test_di_construct_audit.py`
checks that this document and the artifact agree. Nothing here is transcribed by hand.

The question this answers is *what `DI` is*, in the order the project now needs it: construct first,
estimator second, sample size third. The 240 records are `docs/phase_l_results.json` — eight support
configurations (`1:1`, `1:2`, `1:3`, `1:4`, `2:1`, `3:1`, `4:1`, `6:1`) × 30 seeds, arm `V1`, 600 cycles
each, one `di_trajectory` entry per cycle.

---

## 0. Why the audit comes before the reliability estimate

`DI` admits at least three readings, and each needs a different reliability analysis:

| Reading | What it says the number is | Estimator it would license |
| --- | --- | --- |
| Stable structural property | a trait of the configuration | split-half or test–retest over time |
| Developmental state | a value at a designated moment | parallel forms or repeated measurement of that same state |
| Developmental trajectory | the shape of change | reliability of fitted trajectory parameters |

Choosing the estimator first would decide the construct by implication. So this audit settles the
reading from the code and the stored trajectories, and computes no coefficient. If it turns out that
the honest reading is "a state at a time", then a split-half coefficient over two halves of a window is
not a conservative estimate of anything — it is an answer to a question nobody asked.

---

## 1. The five answers, in one table

| # | Question | Answer |
| --- | --- | --- |
| 1 | Where and how is `DI` calculated? | `benchmarks/phase_l_campaign.py::indices()`, `DI = late_retained / late_available`, from **one cycle's report**; zero denominator → `None`, never `0.0`. |
| 2 | What does a `di_trajectory` value mean? | That cycle's own report: the share of the 18 late gold pairs asserted **in that cycle**. Per-cycle, *not* cumulative. Quantised in steps of 1/18. |
| 3 | Stable property, current state, or trajectory? | **A state at a designated time.** It is exactly 0 before the late material arrives, transitions over hundreds of cycles, and is arm-dominated only once it settles (ICC 0.890 on cycles 400–600, arm label 98.5 % of between-run variance). |
| 4 | What is the meaningful measurement window? | One defined **relative to the transition**, not by absolute cycle. The protocol's 110–150 is 40 cycles after arrival; in these records a 40-cycle post-arrival window is 234/240 all-zero with ICC 0.068. **The protocol's window has no support in the only per-cycle data the project holds.** |
| 5 | Can error be separated from developmental change in the 240 records? | **No**, for five separate reasons (§6). It is not that the separation is hard; at the protocol's offset there is nothing to separate. |

---

## 2. Q1 — where and how `DI` is calculated

`benchmarks/phase_l_campaign.py::indices()` computes three quantities from one pair set:

```
DI = len(predicted & late_gold)  / late_available
PI = len(predicted & early_gold) / early_available
DS = DI - PI                        # a diagnostic; never averaged, never a criterion
```

Four properties of that code matter for the construct:

1. **The denominator is the world's late gold set**, `_available(world, late_gold)` — the number of late
   pairs *present anywhere in the event stream*, 18 in every one of the 240 records. It is not the number
   of late pairs shown in the window being scored.
2. **A zero denominator is reported `None`**, with `displacement_measurable = False`, and the cell is
   excluded. The function's docstring names the reason: the Phase L pilot at reduced scale reported
   `DI = 0.000` across a whole sweep for exactly this reason. **That rule is not what fires in these
   records:** `late_available` is 18 in all 240, so every `DI = 0.0` below is a measured zero retention,
   not an absent denominator.
3. **The final index comes from the last cycle's report alone** (`_pairs_from_report(report)` after the
   loop). The 600-cycle run is summarised by what the organism asserted in cycle 599.
4. **The trajectory is per-cycle, not cumulative.** `organica_run(..., trace=True)` appends each cycle's
   `{cycle, di, pi, late_retained, early_retained}`, and its docstring says so explicitly: each entry
   "reflects what the engine asserted *in that cycle*", because the trace's purpose is to answer *when*
   the organism started asserting the late structure, not *whether it ever did*.

That last point is the one that decides §3. A per-cycle snapshot can fall back to zero after the
structure was asserted, and this data does: **1,598** single-cycle decreases across the 240 trajectories,
and only **122 of 240** trajectories are non-decreasing over their whole length. `DI` is a reading of the
current report, not an accumulator of retention.

---

## 3. Q2 — what each `di_trajectory` value is

Each value is the fraction of the 18 late gold pairs asserted in that cycle's sleep report. Three
consequences follow arithmetically, and all three are visible in the artifact:

- **The resolution floor is one pair.** 15 distinct final values occur, and their smallest gap is
  **0.055556** — exactly `1/18`. Every value is an integer multiple of `1/18` (checked mechanically:
  `quantised_to_pair_count` is true, with a one-rounding-unit tolerance because the stored values carry
  6 decimal places). One pair more or less moves `DI` by 5.6 percentage points.
- **`late_retained` spans 0–15 of 18.** No run asserts the full late set in its final cycle, and the
  observed maximum is 15.
- **Zero has two meanings and they must not be confused.** A zero *before the late material arrives* is
  the pre-arrival floor; a zero *after* the material is available is a measured failure to assert. §5 shows
  that the protocol's window lands in the first case in these records.

---

## 4. Q3 — which construct `DI` is

**Verdict: a state at a designated time.** The evidence, in the order that settles it:

**It is zero by construction before arrival.** Phase L's arrival cycle is 150 in every record
(`ARRIVAL_FRACTION = 0.25` of 600). Mean `DI` across the 240 records is `0.0` at cycle 0 and cycle 100,
`0.003` at cycle 150 (a one-cycle blip at the boundary), `0.0` again at cycle 200. No reading in which
`DI` is a standing property of the configuration survives this: before the material exists, the property
is absent by construction, not measured as absent.

**It is still moving hundreds of cycles later.** Mean `DI` is `0.0002` at cycle 300, `0.110` at 400,
`0.241` at 500 and `0.293` at 599 — the last cycle of the run. The median cycle at which a run first
reaches its *own* final value is 424.5 (`6:1`), 481 (`4:1`), 559 (`3:1`) and 586 (`2:1`); the median
cycle at which it first reaches `0.5` is 384.5, 428.5, 493 and 595. These are not settled trajectories
with noise on top; they are transitions that mostly end when the run ends.

**Once it settles, it is the configuration, not the world.** Over cycles 400–600 the within-run variance
is small against the between-run variance — ICC **0.890** — and **98.5 %** of the between-run variance is
explained by the arm label alone. 121 of 240 records are *exactly constant* over those 200 cycles, and the
median within-run SD is `0.0` (maximum `0.293`, so a minority are still moving). The arm means are

| configuration | mean `DI`, cycles 400–600 |
| --- | --- |
| `1:1`, `1:2`, `1:3`, `1:4` | **0.000** |
| `2:1` | 0.043 |
| `3:1` | 0.433 |
| `4:1` | 0.628 |
| `6:1` | 0.698 |

**That ICC is not a repeatability coefficient.** Each world is read once, so nothing in these records can say
whether the same world scored twice would agree; what 0.890 says is that `DI` separates configurations, and
`docs/DI-MEASUREMENT-WINDOW.md` §4 shows the consequence — 98 % of the predictor's variance is between
configurations, leaving about one pair of spread inside one. A coefficient computed across arms would have
looked excellent while the variance a within-configuration test needs was almost absent.

Four of the eight configurations never leave zero. A variable whose values are almost entirely a function
of the condition that generated the world is a *state the condition fixes*, and — importantly for §6 — a
reliability coefficient computed on it would largely report the separation between arms.

**It is not a trajectory in the protocol's sense.** The protocol takes one number at the end of a window
(§2 of the design record). Nothing in the criterion uses the shape. So the third reading is not the one
being measured, even though the data's behaviour is unmistakably a transition.

---

## 5. Q4 — the meaningful window, and the design's window

The design record fixes `DI` at the end of cycles **110–150**. In the protocol's worlds the late group is
exposed from cycle 110, so that window is **40 cycles after arrival**. Phase L's arrival is later — cycle
150 of 600 — so the protocol's window maps onto Phase L as cycles 110–150, which is *before* the late
material exists in those runs:

| window | what it contains | result |
| --- | --- | --- |
| 110–150 (the protocol's window, applied to Phase L) | pre-arrival | **240/240 constant at exactly 0.0**; one distinct window mean; zero variance |
| 150–190 (the same 40 cycles after Phase L's own arrival) | 40 cycles post-arrival | **234/240 records all-zero**; 99.85 % of the 9,600 cycle-values zero; 5 distinct window means; mean 0.000174, SD 0.00131; ICC 0.068; arm label 1.6 % of between-run variance |

The first row is the one that matters for planning. Applying the protocol's window to the only per-cycle
data the project holds does not produce a noisy estimate of `DI`; it produces **240 identical zeros**,
because the window ends before the material arrives. A reliability estimate computed there would divide by
a zero variance and report a number that means nothing.

The second row is the fair comparison, and it is no better for the design: 40 cycles after arrival, 97.5 %
of records have not asserted a single late pair, and the between-run spread is `0.0013` against an
asymptote spread several orders larger. Whatever reliability `DI` has, it is not expressed within 40
cycles of arrival under this engine's dynamics.

**How the window should be defined.** Relative to the transition, not absolutely. In these records the
transition occupies roughly 250–400 cycles after arrival for the configurations that ever express `DI`
(median first reach 424–586 from arrival at 150, i.e. 274–436 cycles after it). Two scaling readings are
available and both point the same way for the protocol's 150-cycle runs:

- **absolute:** 250–400 cycles of transition cannot fit in a run of 150 cycles at all;
- **proportional:** 250–400 of 600 is 42–67 % of the run, which on a 150-cycle run is 63–100 cycles — still
  longer than the 40 the protocol allows.

This is a **defect in the design record, and this audit does not fix it.** The window is a design
parameter with a scientific justification, and changing it is the owner's decision on evidence, not a
silent edit made during an audit. What the audit does is record that the justification currently written
in the record ("computed at the end of the retention window, cycle 110–150") has no support in the data,
and that the direction of the error is against the design: a window that is too early measures the
pre-arrival floor, where variance is zero and no relation can be estimated.

---

## 6. Q5 — can measurement error be separated from developmental change?

**No, not in these records, and the reasons are structural rather than statistical.** Five of them, each
checkable against the artifact:

1. **At the protocol's offset there is nothing to separate.** `DI` over 110–150 is 0.0 in all 240 records.
   Two halves of a constant are not a reliability estimate.
2. **At the matched offset the variable has not started.** 40 cycles post-arrival: 234/240 all-zero, ICC
   0.068. A split-half here would compare a zero first half with a zero second half.
3. **At the asymptote, variance is configuration, not measurement.** ICC 0.890 with 98.5 % of between-run
   variance carried by the arm label. A coefficient computed on cycles 400–600 would mostly re-report the
   arm ordering in §4 — reliability in the arithmetic sense, and a different quantity in the scientific
   sense.
4. **The denominator caps the resolution.** 18 late pairs means the smallest non-zero difference between
   two `DI` values is 0.0556. Any reliability coefficient computed at that granularity is limited by the
   pair count, not by the organism: the measurement cannot distinguish "asserted 11 of 18" from "asserted
   12 of 18" more finely than one whole pair.
5. **Measurement and momentary assertion are the same event.** A per-cycle snapshot records what the report
   asserted that cycle. A cycle in which a pair is omitted is indistinguishable from a cycle in which the
   structure decayed — 1,598 decreases occur, and 118 of 240 trajectories are not monotone. Separating
   omission from loss requires a second, independent read of the same state, which these records do not
   contain.

Points 4 and 5 are the ones that constrain any future estimator: with a pair-count denominator and a
per-cycle snapshot, the "error" term includes both a quantisation floor and genuine moment-to-moment
variation in what the readout asserts, and the design has no instrument that distinguishes them.

---

## 7. What follows for the estimator (still not computed)

The construct is a **state at a designated time**, so the frame that matches it is *parallel forms at a
fixed window*: two disjoint late-pair sets of comparable composition, scored on the same cycles, with the
agreement between them as the reliability. Split-half over time answers the trait question ("does the
organism's level persist?"), which §4 shows is the wrong question at the protocol's offset and a
configuration question at the asymptote.

That frame has a consequence the design must confront before it is used: **the 18-pair denominator is
small.** Two 9-pair forms would resolve `DI` in steps of `1/9` = 0.111, and a coefficient estimated from
nine binary-ish items per form is dominated by the item count, not by the construct. This is a statement
about feasibility, not a result, and it is the reason the reliability question cannot be closed by
re-analysing what exists: **the records contain one late-pair set and one reading per cycle, so no
parallel form exists in them.**

No coefficient is reported here. Reporting one — split-half over the two halves of a window, or over
cycles — would answer a question this audit has just shown to be ill-posed for this endpoint, and would
supply a number the sample-size calculation needs for reasons that do not survive inspection.

---

## 8. What would settle it, and what it would cost

A construct check, not a confirmatory experiment:

1. **Two disjoint late-pair sets of equal size**, both present in the same worlds and both scored on the
   same cycles, so a parallel-form coefficient can be computed at a window the transition actually reaches.
2. **A window chosen from the transition**, declared before the run, in units of the run — not inherited
   from 110–150.
3. **Both readings kept**: the per-cycle trajectory (for latency and for the omission-versus-loss question)
   and the window-end state (for the predictor).

This is a run of the frozen engine on methodology worlds, which is what the scaling ladder already did, and
it costs seeds — so it is **not authorised here and no seed is allocated**. It is also V2 territory: the
frozen V1 record, its results and its seed allocations are untouched by this document.

---

## 9. What this changes in the record

- `docs/STRUCTURE-BEHAVIOR-DESIGN.md` §2 gains a dated note recording that the 110–150 window's
  justification is contested by this audit, that the window is **unresolved**, and that no seed is
  allocated. The protocol's text is not otherwise rewritten: a design parameter is corrected on the
  owner's decision, not by an audit editing itself into the record.
- The sample-size discussion stays paused. The attenuation table remains a conditional planning estimate
  and `DI`'s reliability remains **unmeasured**, now with a documented reason: the estimator cannot be
  chosen until the window is, and the window is not supported.
- The review gate is unchanged. `docs/INDEPENDENT-METHODS-REVIEW.md` §7 remains empty and no reviewer has
  been approached; the reviewer must be told the window is contested rather than handed a protocol whose
  predictor is scored on a window the audit has questioned.

---

## 10. Verification

```bash
./.venv/bin/python -m benchmarks.di_construct_audit          # regenerates docs/di_construct_audit.json
./.venv/bin/python -m pytest tests/test_di_construct_audit.py -q
```

The test recomputes the artifact from `docs/phase_l_results.json`, asserts every number quoted above
against it, and asserts that the five questions are answered in this document and that the design record
carries the dated note. The audit reads the stored records only: it runs no engine, writes no seed, and
computes no reliability coefficient.
