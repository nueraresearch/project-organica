# Phase L — A Synthesis

> **What this document is.** A formal read of what Phase L established, what
> it did not, and what the two of those together mean for what to do next. It
> is not a campaign, not a preregistration, and **not a V2 design.**
>
> It exists because the shape of the result changed. Phase L was written to
> find a **continuous coherence–plasticity trade-off** — a curve on which
> displacement rises smoothly as pressure rises, crossing preservation once,
> in one place. What the measurement returned is a **step function with two
> plateaus and a transition region**, and the protocol's own success criteria
> cannot be satisfied by a curve of that shape at any practical sample size.
>
> Every claim below cites a committed artifact. Nothing here is a claim
> without one, and nothing here is new evidence.

**Status: SYNTHESIS. No new experiment. No architecture change. No V2.**

**The protocol verdict is unchanged and stands: `H3-L — INCONCLUSIVE`.** This
document does not re-score it, does not soften it, and does not replace it.
What it does is publish the **characterisation** — the pattern that survived
increasing n — which is a different kind of claim from the verdict, and is
stated separately for that reason.

---

## 1. The one-sentence conclusion

> **Organica 1 does not appear to exhibit a continuous coherence–plasticity
> trade-off. It appears to exhibit regime behaviour separated by a
> reproducible transition region.**

That sentence is the owner's reading of the pattern that survived raising the
sample size from 10 seeds to 30. It is a **characterisation**, and it carries
two halves that are not equally supported:

- **"Regime behaviour with a reproducible transition region"** — supported by
  direct measurement, and it got *stronger* as n rose.
- **"Does not exhibit a continuous trade-off"** — supported by the absence of
  the property the protocol asked for, established not by an argument but by
  the protocol's own success criteria being unsatisfiable on a step-shaped
  curve.

Neither half is a capability claim. Neither half is a boundary claim. The
protocol's `H3-L` verdict is what it is, and the protocol's own sentence for
it — *"raise n; do not conclude anything"* — has been carried out to its end:
n was raised, the bar was not cleared, and **nothing is concluded about a
boundary**.

---

## 2. What Phase L established

These are the properties that survived increasing n. Each cites where it was
measured.

### 2.1 The displacement curve is step-shaped, not a ramp

```
DI   0.000  0.000  0.000  0.000 │ 0.204 │ 0.706  0.722  0.715
PI   0.743  0.754  0.748  0.717 │ 0.606 │ 0.039  0.000  0.000
     1:4    1:3    1:2    1:1    │  2:1  │  3:1    4:1    6:1
     └──── preservation ────┘    └─────┘ └──── displacement ────┘
                              └─ transition region ─┘
```

Three plateaus and two transitions. The plateaus are **structural, not
statistical**: DI is **exactly 0.000** at 1:4, 1:3, 1:2 and 1:1 for **all 30
seeds**, and PI is **exactly 0.000** at 4:1 and 6:1 for **all 30 seeds** —
verified on the raw records, not on rounded means
([`docs/phase_l_results.json`](../docs/phase_l_results.json)).

The low plateau means something specific and strong: **under these
displacement pressures the late structure is never incorporated at all.** The
high plateau means the early structure is **entirely** gone, not merely
reduced.

### 2.2 The transition location is the most reproducible quantity in the phase

The crossing is at **3:1**, and it did not move when n tripled:

| | n = 10 | n = 30 |
|---|---|---|
| Crossing label | 3:1 | **3:1** |
| Paired-bootstrap interval (99%) | [5.0, 5.0] | **[5.0, 5.0]** |
| Replicates that found a crossing | 10,000 / 10,000 | **10,000 / 10,000** |
| Alternative bootstrap seeds `INTERIOR` | 8 / 8 | **8 / 8** |
| Leave-one-seed-out crossings at 3:1 | 10 / 10 | **30 / 30** |

([`docs/phase_l_results.md` §4](../docs/phase_l_results.md); analysis in
[`benchmarks/phase_l_analyze.py`](../benchmarks/phase_l_analyze.py))

> **The scope of that robustness — narrowed 2026-10-26.** The 3:1 crossing is
> robust **within this defined experiment**: this engine, this world family,
> this support-ratio axis. The eight alternative bootstrap seeds test
> **resampling stability, not new worlds** — they re-draw from the same
> measured seeds, so they say the crossing is not an artefact of one resample,
> not that the crossing would land in the same place in a different world.
> Leave-one-seed-out is the same kind of check on the same data.
> **3:1 is therefore not a general threshold for Organica**, and this document
> does not assert one. The correct reading is: *within the axis, world family
> and engine tested, the transition location is highly reproducible and does
> not drift with n.*

### 2.3 The transition is abrupt, not gradual

Revision latency goes from **0 of 30** seeds reaching DI > 0.5 at 2:1 to
**30 of 30** at 3:1 (mean 356 cycles, median 351). The organism does not
revise *slightly more* under higher pressure. It goes from **never** to
**always** between two adjacent points on the sweep.

> ### 2.3a What this finding is called — narrowed 2026-10-26
>
> The Phase L result is **structural displacement**: later *structure*
> displacing earlier *structure*, measured by a structure-retention index
> (DI/PI). It is **not** a measurement of whether a *belief* was corrected
> against ground truth. The two are different capabilities and the project's
> record separates them:
>
> | | Phase L (structural displacement) | Phase K (belief revision) |
> |---|---|---|
> | Question | Do later structures displace earlier ones? | Is a wrong belief corrected against ground truth? |
> | Metric | DI / PI — a structure-retention index | Task score against a known truth |
> | Result | reproducible transition at 3:1 | Organica **0.4111** vs best simple baseline **0.9846** |
> | Difference | — | **−0.5735**, 98.33% interval **[−0.6162, −0.5309]**, **REVERSED** |
>
> **Belief revision remains a separate capability question, and the one time
> the project measured it head-to-head against a strong baseline, Organica
> lost cleanly.** So "revision exists" is not a supported summary of Phase L;
> "structural displacement occurs, and is sharply thresholded" is. Nothing in
> this document's characterisation carries over to the belief-revision
> question, and the earlier wording that read Phase L as a revision result has
> been corrected wherever it appeared.

### 2.4 The instrument is sound, and its seed axis is exchangeable

All four instrument audits passed on the live run; **no cell was unmeasurable**;
and a dedicated audit established that the seed axis behaves as the bootstrap
assumes. Thirty fresh, non-consecutive, pre-declared seeds gave DI 0.7241 at
6:1 against the campaign's own 0.7148 (30 seeds) and 0.7500 (its original
ten) — a difference of +0.0093, **p = 0.60** against random 30/30 splits of
all 60 measured values ([`docs/phase_l_seed_audit.json`](../docs/phase_l_seed_audit.json)).

The original ten seeds were an **unlucky high draw**, not a seed-block
artefact. So the n=30 curve is the better estimate because there are more
seeds, not because they were different.

---

## 3. What Phase L did not establish

### 3.1 No boundary in the protocol's sense

Two of the four pre-committed criteria are not met. The pre-committed verdict
is `H3-L — INCONCLUSIVE`, and the protocol's sentence for it is *raise n;
conclude nothing*. **No boundary is claimed, and no V2 is authorised.**

### 3.2 No continuous trade-off — and this is a statement about the *curve*, not about the criteria

This is the negative half of the conclusion, and it deserves precision. The
protocol's monotone criteria are evaluated on the **mean** curve, so each is
a statement about the **sign** of an adjacent difference. On a curve with
plateaus, that is a test the organism cannot pass at any practical n:

| Criterion | random 10-seed subsets | random 20-seed subsets | n = 30 |
|---|---|---|---|
| 1. DI monotone increasing | 19.3% | 16.1% | 0% |
| 2. PI monotone decreasing | 12.0% | 6.6% | 0% |
| 3. DI range ≥ 0.25 | **100.0%** | **100.0%** | met |
| 3b. Crossing interior | **100.0%** | **100.0%** | met |
| **All four together** | **2.9%** | **1.2%** | 0% |

The two stable criteria are the two that hold in every resample. The two
fragile ones hold in 7–19% of random draws — so the n=10 run's criterion-1
pass was itself one of the lucky 19%. **Strict monotonicity is not a property
this organism's displacement curve has**, and more seeds cannot turn a
plateau into a ramp.

### 3.3 Nothing else

- **Nothing about capability.** Nothing about intelligence, learning, or what
  this means for any task.
- **Nothing about belief revision.** Phase L measured structural displacement.
  Whether a belief is corrected against ground truth is a different question,
  measured elsewhere and answered against Organica (§2.3a).
- **Nothing about the secondary axes.** V2–V5 were **not run**. No Phase L
  outcome authorises a V2, and the protocol says so in advance.
- **Nothing about support ratio being *the* operative variable** beyond this
  one axis on this one frozen engine.
- **Nothing about order dependence, strictly.** Phase L varied a pressure
  ratio, not an event order. The project's *schedule*-dependence results
  (curriculum, history) vary the event **multiset and order together**, so
  they support **path dependence** and do **not** isolate strict order
  dependence — that would need the event multiset held fixed with only the
  order changed, and that comparison has not been run.
- The **baseline rule** was recorded and **not exercised** in V1: the arm is
  the organism's own curve, bracketed by the control and ceiling check rather
  than by a competing system.

---

## 4. Why the verdict and the characterisation differ

They do not contradict each other; they answer different questions.

| | Question it answers | Answer |
|---|---|---|
| **Protocol verdict** | Do the curve's four pre-committed properties hold? | **No** → `H3-L — INCONCLUSIVE` |
| **Characterisation** | What shape does the curve actually have? | **A step function with a reproducible transition at 3:1** |

The mechanism is visible in the paired differences. Every adjacent step whose
99% interval excludes zero is a real transition; every step whose interval
contains zero is a plateau edge — and **both failing criteria are sign tests
at plateau edges**
([`docs/phase_l_results.md` §5](../docs/phase_l_results.md)).

> **1:4 → 1:3** (criterion 2 fails here): dPI **+0.011 [−0.026, +0.044]**
> **4:1 → 6:1** (criterion 1 fails here): dDI **−0.007 [−0.037, +0.022]**
> **1:1 → 2:1**: dDI +0.204 [+0.148, +0.261] · dPI −0.111 [−0.157, −0.065]
> **2:1 → 3:1**: dDI +0.502 [+0.443, +0.559] · dPI −0.567 [−0.619, −0.522]

A protocol written for a monotone ramp asked a question this organism's curve
does not have an answer to. **That is a finding about the organism, not a
defect in the discipline** — the discipline is what made the shape legible,
because it held the bar it set and reported the shape anyway.

---

## 5. The raise-n experiment did its job

The protocol's remedy for `H3-L` was *"raise n"*, and the reason to take it
was specific: there was a plausible world in which the +0.005 PI reversal was
**noise around an otherwise monotone curve**, and another in which the curve
was **genuinely step-shaped**. Those worlds make different predictions, and
more data distinguishes them.

**It distinguished them.** At n=30 the low-end steps are each individually
consistent with zero, the plateaus are exact for all 30 seeds, and the two
criteria that test monotonicity now fail *more* firmly, not less. The world in
which the reversal was noise around a monotone curve is not supported.

This is why raising n a third time is not the answer: it would change nothing
about the thing being measured. **The campaign was not failing for want of
precision. It was failing because the curve is not the curve the protocol
expected.**

---

## 6. What this changes about what to measure next

Before Phase L, the secondary axes (arrival timing, novelty density, belief-cap
pressure, contradiction pressure) would have been read as tests of *which
variable moves a smooth boundary*. They are not, and the question is now more
specific and more interesting:

> **Why is the displacement curve step-shaped? What determines the width and
> location of the transition region?**

That is a question about **regime formation** — how much pressure is needed
before the organism switches from preserving to displacing, and what sets that
threshold. It is the natural successor, and the owner's decision is to
**publish the characterisation first** and only then consider the secondary
axes, so that they are read against a known shape rather than against a
hypothetical smooth boundary.

---

## 7. The dangerous question

The temptation this result creates is not "we nearly passed". It is:

> *A stable, reproducible threshold at 3:1 — that is a boundary, isn't it?*

**It is not, and the protocol's verdict is the reason.** A threshold is a
boundary only if the trade-off is a continuum that the threshold divides.
Here the curve is flat on both sides of the crossing, and the crossing
location is stable for a reason that has nothing to do with a continuum: the
organism switches regimes, and the switch is reproducible. That is a real
property. It is not the property the protocol asked for, and calling it one
would be the same category of error as re-scoring the failed criteria — only
more flattering.

The second temptation is to let "regime behaviour" become a claim about
intelligence. It is not one. **Phase L measured a displacement index, a
preservation index, and a latency on synthetic worlds.** The word "regime"
describes the shape of those curves. Nothing more.

---

## 8. What this document does not claim

- It does not claim a coherence–plasticity boundary. The protocol's verdict is
  `H3-L — INCONCLUSIVE`, and that verdict is reproduced in every artifact.
- It does not claim a **general** threshold for Organica. The 3:1 crossing is
  robust within this engine, world family and support-ratio axis (§2.2); it is
  not a property of the organism in general.
- It does not claim **belief revision** (§2.3a). It claims structural
  displacement.
- It does not claim **strict order dependence** (§3.3). It claims
  schedule dependence.
- It does not re-read, relax, or reinterpret a single pre-committed criterion.
  The criteria were evaluated once by committed code; criterion 1 was met at
  n=10 and is not met at n=30; that is what is reported.
- It does not claim anything about capability, learning, or intelligence.
- It does not claim anything about the secondary axes — they were not run.
- It does not authorise V2. **No Phase L outcome authorises a V2.**
- It does not add evidence. Everything here is a reading of
  `docs/phase_l_results.json` (240 cells, n=30) and the audit artifacts.

---

## 9. Where the evidence lives

| Artifact | What it holds |
|---|---|
| [`docs/phase_l_results.md`](phase_l_results.md) | The raise-n result: curve, criteria, RT, adjacent differences, stability analysis |
| [`docs/phase_l_results.json`](phase_l_results.json) | The canonical n=30 record — 240 cells, 30 seeds per point |
| [`docs/phase_l_results_n10.json`](phase_l_results_n10.json) | The n=10 record, preserved unmodified |
| [`docs/phase_l_seed_audit.json`](phase_l_seed_audit.json) | The seed-exchangeability audit |
| [`benchmarks/phase_l_analyze.py`](../benchmarks/phase_l_analyze.py) | The analysis, in committed code |
| [`benchmarks/phase_l_campaign.py`](../benchmarks/phase_l_campaign.py) | The harness |
| [`docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md`](PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md) | The frozen protocol and Amendments 1–3, all pre-outcome |
| [`research-journal/phase_g_findings_20261021.md`](../research-journal/phase_g_findings_20261021.md) §38–§40 | The full record, including the failures |
