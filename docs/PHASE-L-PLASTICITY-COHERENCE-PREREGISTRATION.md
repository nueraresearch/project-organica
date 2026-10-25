# Phase L — Plasticity–Coherence Measurement

**Status: FROZEN PROTOCOL. Committed before any Phase L outcome was
generated.**

**Amended once — Amendment 1 (2026-10-25), see
[Amendment 1](#amendment-1--2026-10-25).** The amendment was made before any
Phase L outcome existed. It corrects *harness* defects and adds an instrument
audit; it changes no hypothesis, no independent variable, no metric
definition, and no success criterion.

This is not a benchmark hunt. Every previous phase asked some version of
*"can Organica do X?"* — prediction, recovery, regime shifts, adaptation,
world modeling, belief revision, integration — and all of them came back
negative. Phase L asks a different question:

> **How much pressure is required for new structure to displace old
> structure?**

That question is not a retry of the others. It comes out of the strongest
measured phenomenon in V1, and it is the first question in this project that
treats Organica 1 as a **property to be characterised** rather than a system
to be compared against something.

The evidence that motivated it is in [`docs/V1-SYNTHESIS.md`](V1-SYNTHESIS.md)
§5, and the measurement that opened the door is in
[`docs/phase_k_results.md`](phase_k_results.md) §4.3.

---

## 1. Why this question, and not another benchmark

Organica 1 is **frozen** as of the `v0.9.0` tag (see
[`docs/V1-FREEZE.md`](V1-FREEZE.md)). It is the fixed reference object; every
measurement is taken against it.

The V1 evidence gives one thing a developmental architecture is *good* at and
one thing it is *bad* at, and they are the same thing:

- **Good:** development is history-dependent. Change the curriculum, change
  the outcome (74 → 91 → 113 → 119 → 128 items across
  presentation schedules).
- **Bad:** the early scaffold dominates. In K3, late-arriving structure was
  incorporated in **0 of 150 cycles** and **0 of 10 seeds**, while a
  co-occurrence counter reached 0.857.

And the 2×2 control turned "bad" into something usable: the late group
**is** incorporated when it is strictly stronger than the group that arrived
first (9–11 of 18 gold pairs at late weight 3 / early weight 1, against
0–1 otherwise). So Organica 1 is not incapable of revision. It is
**priority-ordered**: signal strength decides what displaces what, and arrival
order breaks ties in favour of the incumbent.

**A priority rule is a variable.** Variables can be measured, and they can be
manipulated. That is the entire justification for this phase.

---

## 2. Hypothesis

> **H-L1.** Organica 1 exhibits a measurable **coherence–plasticity
> boundary**: revision of early structure occurs only after a threshold of
> displacement pressure is exceeded, and that threshold is a property of the
> organism that can be located and reported with an interval.

Three claims, and they are separable:

| | Claim | If it fails |
|---|---|---|
| **H-L1a** | Displacement pressure **monotonically** increases late-structure incorporation | pressure is not the operative variable; the search has not found the mechanism |
| **H-L1b** | Displacement pressure **monotonically** decreases incumbent preservation | revision and preservation are not in tension for this system |
| **H-L1c** | There is a **threshold** — a pressure region in which late incorporation is partial and preservation is partial | the system is not at a boundary but at one of two poles |

**H-L1c is the one that matters.** A system that never revises and a system that
always revises are both *not* at a boundary. A boundary is the interesting
object: it is the trade-off itself, made visible.

---

## 3. What is being measured

### 3.1 The Displacement Index (DI)

```
DI = late_structure_retained / late_structure_available
```

**late_structure_available** is the number of gold pairs belonging to the
late-arriving group that the organism could have retained — the pairs that
actually occur in the event stream. **late_structure_retained** is how many of
those the organism's surviving structures assert, read through the same
`edges_implied_by_structures` extractor used by the published campaigns.

DI = 1.0 means the organism absorbed all of the late structure. DI = 0.0 means
it absorbed none.

### 3.2 The Preservation Index (PI)

```
PI = early_structure_retained / early_structure_original
```

**early_structure_original** is the number of gold pairs belonging to the
early group. **early_structure_retained** is how many of those the organism's
surviving structures still assert at the end of the run.

PI = 1.0 means the early scaffold survived intact. PI = 0.0 means it was
entirely displaced.

### 3.3 The Revision Threshold (RT)

The pressure value at which **DI crosses PI** — the point where late
structure is retained *more* strongly than early structure.

**RT is the headline quantity of this phase.** It is the boundary itself,
expressed as a number on a declared axis.

### 3.4 Secondary outcomes

| Quantity | Definition | Why it is here |
|---|---|---|
| **Revision latency** | cycles from the late group's arrival until DI first exceeds 0.5 | distinguishes *never* from *slowly*. **Elevated to co-primary reporting by Amendment 2** — two organisms can end at the same DI and PI while crossing at completely different times. |
| **Knowledge preservation** | fraction of early-group pairs still asserted at the end, across the whole run | PI at the final cycle is a snapshot; this is the trajectory |
| **Absolute late incorporation** | raw count of retained late pairs | DI is a ratio and can hide a small absolute number |
| **Displacement Score (DS)** | `DI − PI` — **added by Amendment 2 as a diagnostic** | DI and PI are not opposites: DI 0.8 / PI 0.8 is *coexistence*, not revision. The gap distinguishes accumulation from displacement. **Not a primary metric and not a success criterion.** |

**Reported separately, never averaged.** A harmonic mean that collapses to
zero when one component is zero destroyed an endpoint in Phase K (Amendment
1). **No composite score is computed in this phase.**

---

## 4. The independent variables, varied one at a time

**One at a time is not a simplification, it is the design.** Phase K's three
families each moved several things at once, which is why the K3 zero took
three separate diagnostics to interpret. A boundary that moves when five
things move at once is not a boundary; it is a correlation. So each variable
below is swept in its own arm, with every other variable held at its baseline
value.

| # | Variable | Baseline | Sweep | Rationale |
|---|---|---|---|---|
| **V1** | **Support ratio** (late : early) | 1 : 3 | 1:4, 1:3, 1:2, 1:1, 2:1, 3:1, 4:1, 6:1 | The axis the K3 2×2 already located. The primary axis. |
| **V2** | **Arrival timing** (cycle the late group appears) | 150 | 50, 100, 150, 250, 400 | Does an *earlier* incumbent bind harder than a *stronger* one? |
| **V3** | **Novelty density** (events per cycle) | baseline | 0.5×, 1×, 2×, 4× | Does a denser late stream change the threshold, or only the latency? |
| **V4** | **Belief-cap pressure** (competing subjects vs `MAX_HYPOTHESES = 15`) | 6 | 3, 6, 12, 18, 24 | Does the bound itself set the threshold? |
| **V5** | **Contradiction pressure** (late group contradicts the early group) | off | off, on | Does *conflict* displace, where *novelty* alone does not? |

**V5 is the arm that could overturn the framing**, and it is included
because of it. If late structure that *contradicts* early structure displaces
it while merely *new* structure does not, then the operative variable is not
strength but **conflict** — and the phase's title is wrong. That is a
result, and it is recorded as one.

The **primary axis is V1**. The other four are secondary and are reported
separately. **A secondary arm cannot overrule the primary axis**; it can
only explain it.

### 4.1 One world shape, many parameterisations

All arms use **one** world generator, so that the arms differ only in the
variable under study. The generator emits entities with four features each,
drawn by weight, with a 10% noise rate — the same construction as the
Phase K families, so the Phase K numbers are a direct comparison rather than a
foreign measurement.

---

## 5. The baselines, and the tuning advantage

**Every simple baseline is swept over a declared grid and its BEST score is
used.** This is not a courtesy; it is the rule that makes a negative result
meaningful (AGENTS.md rule 11).

| Baseline | Grid | What it is the control for |
|---|---|---|
| **Co-occurrence (windowed)** | windows {all, 300, 150, 75, 30} × min_count {3, 5, 10} | the "count and keep" strategy: unbounded, no capacity limit, trivially high DI and PI |
| **Temporal graph** | lookback {1, 3, 5} × min_count {3, 5, 10} | order-aware counting |
| **First-seen-wins** | n/a | **the control that matters.** A model that keeps the first structure and ignores everything after. DI ≈ 0, PI = 1.0. |
| **Last-seen-wins** | n/a | the mirror: keeps only the most recent. DI = 1.0, PI ≈ 0. |

**The baselines are not competitors.** Organica cannot be expected to beat
"keep everything" on DI, because "keep everything" trivially scores 1.0. The
baselines exist to **bracket the metric's range and to prove it can
discriminate**: if first-seen-wins and last-seen-wins both score 0.5 on DI,
the metric is measuring nothing.

**This is the analogue of Phase K's K0 control, and it is required.** The
metric must be able to distinguish a system that never revises from one that
always revises. If it cannot, the campaign does not run.

---

## 6. The success criterion

**Not** "Organica beats a baseline." **Not** "Organica wins a task."

> **A reproducible displacement curve exists.**

Concretely, Phase L succeeds if **all four** hold:

1. **DI is monotone increasing** in displacement pressure on the primary axis
   (V1), across the declared sweep, with a non-degenerate range (the DI at the
   high end must exceed the DI at the low end by at least 0.25).
2. **PI is monotone decreasing** in the same pressure, over the same sweep.
3. **The two curves cross**, and the crossing point (RT) is interior to the
   sweep — not at either endpoint.
4. **The crossing is reproducible**: the RT estimated from a paired bootstrap
   over seeds has a 99% interval that excludes both endpoints of the sweep.

Criterion 4 is what separates a boundary from a coincidence. A crossing point
that can be anywhere on the axis is not a boundary.

**If the criteria are met, the finding is the curve and its RT** — a
characterisation, not a victory. If Organica's curve is *worse* than a
baseline's, that is a legitimate finding too, and the phase reports it.

### 6.1 Stated plainly: what success looks like, and what failure looks like

This phase is designed to be able to **fail cleanly**. Both of the following
are publishable outcomes, and neither is a disappointment:

**SUCCESS — a stable displacement curve exists.**

```
low  pressure  ->  preservation dominates   (DI low,  PI high)
mid  pressure  ->  transition               (DI partial, PI partial)
high pressure  ->  displacement dominates   (DI high, PI low)
```

with an interior, reproducible crossing (RT) between the poles.

**FAILURE — no measurable relationship exists.**

```
DI flat across the sweep      (the dial is not connected to anything)
PI flat across the sweep
no crossing at all
```

A flat curve is a **characterisation**: the organism sits at one pole —
preservation is absolute, or revision is unconditional — and the phase has
located that pole. That is a real answer to the question, and it is the
answer H2-L′ names.

**The campaign must be able to fail.** It is not built to produce a win, and
no gate is relaxed to make it produce one. A flat DI and a flat PI are
recorded as flat.

---

## 7. Pre-committed terminal outcomes

Written before the run so that no outcome can be reinterpreted afterwards.

| Outcome | Condition | What it means |
|---|---|---|
| **H2-L — a boundary exists** | all four criteria met | Organica 1 has a measurable coherence–plasticity boundary, located with an interval. **This is the success case.** It names a property, not a capability. |
| **H2-L′ — no boundary** | the curves do not cross, or the RT interval includes an endpoint | the system sits at a pole, not at a trade-off. Either **preservation is absolute** (DI stays near 0 across the whole sweep) or **revision is unconditional** (PI stays near 1). Both are real characterisations and both are publishable. |
| **H2-L³ — the wrong variable** | the primary axis shows no monotone trend, **but** a secondary axis does | the operative variable is not support ratio. Name the axis that moved, and say plainly that the primary hypothesis was wrong. |
| **H3-L — inconclusive** | intervals too wide to place RT | raise n. Do not conclude anything. |

**There is no outcome here that authorises a V2.** The phase characterises a
property of a frozen architecture. What to do with that property is a
separate decision, taken afterwards.

---

## 8. Protocol

| | |
|---|---|
| **Seeds** | 10 (20261023–20261032), paired across arms — the same seed sees every arm |
| **Hash seed** | `PYTHONHASHSEED=0` in every process, so hash order is common-mode across arms |
| **Cycles** | 600 per world, matching the Phase K K3 family |
| **Decision interval** | 99% paired percentile bootstrap (Bonferroni across the five arms), 10,000 replicates |
| **Bootstrap seed** | derived from the arm name through Python's string hash, which is deterministic only because `PYTHONHASHSEED=0` is pinned — the robustness check re-runs it with 8 other seeds and reports if any verdict moves |
| **Engine** | **Organica 1, frozen.** `organica/sleep.py` and `organica/memory.py` are not modified. Verified by `tests/test_v1_freeze.py` |
| **Baseline rule** | best-of-grid, declared above, never handicapped |
| **Arms** | V1 (9 points × 10 seeds), V2 (5 × 10), V3 (4 × 10), V4 (5 × 10), V5 (2 × 10) |
| **Pilot** | permitted at reduced scale to confirm the harness executes, **disclosed in this document**, and **never evidence** |

### 8.1 Instrument audits, run before the campaign

The campaign **does not run** if any of them fails.

1. **The discrimination control.** First-seen-wins must score DI ≈ 0 and
   PI ≈ 1.0; last-seen-wins must score DI ≈ 1.0 and PI ≈ 0. If the
   metric cannot separate "never revises" from "always revises", it is
   measuring nothing and the campaign does not run.
2. **The endpoint ceiling check.** A synthetic perfect model must score 1.0 on
   DI and PI. A metric a perfect model cannot reach is a broken instrument.
3. **The degeneracy audit.** *(Added by Amendment 1.)* The first two audits
   check the metric; this one checks the **design**. In every cell of every
   arm, both groups must be available for measurement; the support ratio must
   actually change the early/late event mix; the contradiction arm must
   produce a different world from the plain arm; the density arm must
   actually change the event count; and the early and late gold sets must
   stay disjoint. A metric can be perfect and the design still dead, and
   that is exactly what the first pilot demonstrated.
4. **The V4 pressure audit.** *(Added by Amendment 2.)* Phase G measured the
   belief pool *starved* on the live study stream — mean 5.17 beliefs,
   maximum 6, against `MAX_HYPOTHESES = 15`. If the pool never fills, the
   belief-cap arm cannot change anything, and a flat V4 curve would be a
   statement about the engine rather than about the organism — the way V5
   was inert before Amendment 1. This audit runs the frozen engine at both
   ends of the V4 sweep and requires that the cap actually binds.

All four audits are permanent, and all four run on every invocation of the
harness. The V4 audit runs the engine, so it is computed **once at startup**
and carried into the run rather than recomputed per cell.

### 8.2 The harness must be resumable and lose nothing

This campaign is long. It is built to be **stopped and resumed**:
results are written atomically (temp file + `os.replace`), an append-only
NDJSON live recording is flushed and fsynced after every seed, and `--resume`
rebuilds from the recording if the results file is missing. **No seed may be
lost to a stop.**

---

## 9. What this phase cannot establish

- **Nothing about Organica 2.** The engine is frozen; this measures V1.
- **Nothing about natural environments.** These are synthetic worlds with
  four-tag entities. A result here is a result about this task family.
- **Nothing about the mechanism.** DI and PI describe *what* displaces what.
  They do not say *which layer* does it. Identifying that is a separate phase
  with its own ablation design.
- **Nothing about whether the boundary is desirable.** Locating a trade-off
  is not the same as having chosen it well.
- **No external-validity claim.** Organica is not being compared against a
  rival here. The baselines bracket the metric; they are not competitors.

---

## 10. Limits of the design, stated in advance

- **The axis is discrete.** Support ratio takes 8 values, so RT is located to
  within one grid step. A finer sweep is a follow-up, not a retrofit.
- **The metric reads structures, not intentions.** A pair is "retained" if a
  surviving structure asserts it. Whether the organism would have *used* it is
  not measured.
- **The incumbent is not retired.** In this design the early group keeps
  emitting, so PI measures retention *under continued support*. A design where
  the early group stops would measure something different and is **not** this
  phase.
- **One world shape.** One generator, varied parameters. A different
  vocabulary or entity count could shift the threshold.
- **Synthetic tags are drawn from a fixed 24-word alphabet.** Words carry no
  semantic structure, which is deliberate — it removes a confound — but
  it also means nothing here transfers to natural language.

---

## 11. Artifacts

Committed with this protocol, before any outcome:

- `benchmarks/phase_l_campaign.py` — the harness: world generator, the
  variable sweeps, the metric computations, the bootstrap, and both instrument
  audits.
- `docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md` — this document.

Produced by the campaign:

- `docs/phase_l_results.json` — every arm, every seed, every model.
- `docs/phase_l_results.ndjson` — the live recording.
- `docs/phase_l_results.md` — the write-up, including the displacement
  curves and the RT estimate with its interval.

---

## Amendment 1 — 2026-10-25

**Made before any Phase L outcome existed.** No Phase L campaign has been run.
The pilot that exposed these defects was a *reduced-scale execution check*
(section 8, "Pilot"), which is explicitly **never evidence**, and it is
reported below as a harness finding, not a scientific result.

### Why an amendment was needed

The pilot returned a clean-looking result that was entirely an artefact:

```
V1 1:4 seed 20261023: DI=0.000 PI=0.611
V1 1:3 seed 20261023: DI=0.000 PI=0.611
...
V1 6:1 seed 20261023: DI=0.000 PI=0.611
```

Eight identical points. Read naively, that is a negative result: *the late
structure never displaces the early structure, at any pressure*. It is not.
**The support ratio was not varying anything at all**, and the reason was a
harness defect, not a property of the organism.

### The four defects

**1. The late group arrived after the run ended.** `build_world` defaulted the
late group's arrival to cycle 150 in absolute terms. The pilot ran at reduced
scale (150 cycles), so the late group never became active, the late structure
was never available, and DI had no denominator. `build_jobs` scaled `arrival`
for the V2 arm but not for V1, V3, V4 or V5.

*Fix:* arrival is now a **fraction of the run** (`ARRIVAL_FRACTION = 0.25`,
i.e. 150 of 600 — the same proportion the original default expressed), and
every arm scales it proportionally.

**2. An unmeasurable index was reported as zero.** `indices()` returned
`0.0` when the denominator was zero. So "the late structure was never
available" was recorded as "the organism retained none of the late
structure" — a measurement of nothing reported as a measurement of zero.
This is the exact failure mode the Phase K harmonic-mean collapse produced,
and the project rule is explicit: *unmeasurable metrics are reported as "not
measurable", excluded — never zeroed.*

*Fix:* `indices()` returns `None` for an undefined ratio, and such cells are
**excluded** from the curve and counted under `unmeasurable_cells`. An arm
with any unmeasurable point returns the verdict `UNMEASURABLE` rather than
any scientific verdict.

**3. The contradiction arm (V5) was a no-op.** The code shared a feature of
the *late* group with itself, rebuilding `late_0` exactly as it already was.
The world was byte-identical with the arm on and off, so V5 measured nothing.

*Fix:* the shared feature now comes from the **early** group, so the two
compete for the same subject, as section 4 intends. Verified: the gold sets
and the event streams now differ between `off` and `on`.

**4. The density arm (V3) fed the engine only part of the world.** The engine
chunks the event stream at a fixed 12 events per cycle, but the density arm
varies that rate (6, 12, 24, 48). At density 4.0 the engine saw 7,200 of
28,800 events while the harness reported a complete run.

*Fix:* the world's own `events_per_cycle` is passed to the engine.

### A fifth correction: the RT bootstrap measured the wrong thing

The bootstrap was resampling the **DI−PI gap** and reporting its minimum and
maximum. Section 6, criterion 4 asks for something else: *the RT estimated
from a paired bootstrap over seeds has a 99% interval that excludes both
endpoints of the sweep.* The RT is the **crossing location**, so the
resampled statistic is now the index of the first label at which DI overtakes
PI, and the interval is a **percentile** interval over those locations, with
seeds resampled **paired across labels**. "Excludes both endpoints" is now
tested directly: the interval must lie strictly inside the sweep.

### A new instrument audit: the degeneracy audit

The two audits in section 8.1 both check the **metric**. Neither checked the
**design**, and that is why all three of the defects above passed them: the
metric was working perfectly on a world where nothing could be measured.

Section 8.1 now has a third audit, and the campaign does not run if it fails:

3. **The degeneracy audit.** For every cell of every arm: both groups must be
   available for measurement; the support ratio must actually change the
   early/late event mix; the contradiction arm must produce a different world
   from the plain arm; and the density arm must actually change the event
   count. Every check is failable by construction.

It earns its place immediately: the first version of the audit itself had a
scaling inconsistency with `build_jobs` (it applied the V2 arrival label
absolutely while the campaign applied it proportionally), and the audit
caught it by failing the run before a single cell was executed.

### One item for the owner to settle — **settled by Amendment 2**

Section 6 and section 8 stated a **98.33%** decision interval, and glossed it as
"Bonferroni across the arms". Across five arms, Bonferroni gives
0.05/5 = 0.01, i.e. a **99%** interval; 98.33% corresponds to 0.05/3 — which is
Phase K's correction factor over its three families, carried over by accident.

The owner settled this on 2026-10-25, before any Phase L outcome existed:
**the intent governs and the stray percentage is the accidental constant**, so
the procedure is preserved and the number is corrected. The interval is
**99%**. See Amendment 2.


### What did not change

No hypothesis (H-L1, H-L1a/b/c), no independent variable, no sweep point, no
seed, no metric definition, no baseline, no success criterion, and no
pre-committed terminal outcome was altered. The four defects were all in the
harness's *implementation* of the protocol as written; the corrections make
the code do what this document already said. No gate was relaxed, and one
audit was added.

---

## Amendment 2 — 2026-10-25

**Made before any Phase L outcome existed.** The campaign has not been run.

### The decision interval: 98.33% → 99%

Section 6 and section 8 stated a **98.33%** decision interval and glossed it
as "Bonferroni across the arms". Those disagree:

| | |
|---|---|
| "Bonferroni across the arms", five arms, family-wise α = 0.05 | 0.05 / 5 = 0.01 per arm → a **99%** interval |
| a stated 98.33% interval | α = 0.0167 = 0.05 / 3 — **Phase K's** correction factor, carried over by accident |

**The owner's ruling: the intent governs and the stray percentage is the
accidental constant.** The procedure — Bonferroni across the arms — is
preserved, and the number is corrected to **99%**. The harness now computes
`DECISION_ALPHA = 0.05 / 5`.

This changes which verdicts are reachable, which is exactly why it was
settled now, in the open, before any outcome existed rather than after a
result was in hand. Phase K's own 98.33% figures are **unaffected**: that
protocol had three families and 0.05/3 was correct there.

### Section 6.1 added: success and failure stated plainly

Section 6 already specified the success criterion and section 7 already
pre-committed four terminal outcomes, including H2-L′ ("no boundary"). The
owner's review asked for the same thing to be stated in the plainest
possible terms, so section 6.1 now says it directly:

- **Success** — a stable displacement curve exists: low pressure → preservation
  dominates; mid pressure → transition; high pressure → displacement
  dominates; with an interior, reproducible crossing.
- **Failure** — no measurable relationship exists: DI flat, PI flat, no
  crossing. A flat curve is a *characterisation* (the organism sits at one
  pole), and it is a publishable answer.

**The campaign must be able to fail.** It is not built to produce a win and
no gate is relaxed to make it produce one.

### Two preregistered secondary outcomes the harness was not computing

Section 3.4 declares three secondary outcomes: *revision latency*,
*knowledge preservation* (the PI trajectory), and *absolute late
incorporation*. The harness computed only the third. The first two are now
implemented, from a per-cycle DI/PI trace taken as the engine runs.

The trace is **per-cycle, not cumulative**: each cycle's report reflects what
the engine asserted *in that cycle*, so the trace answers "when did the
organism start asserting the late structure", not "when did it ever assert
it". The final indices are still computed from the last report alone, and
the trace does not change them — an internal consistency check confirms the
trace's last point equals the final DI and PI.

These are reported **separately and never averaged**, as section 3.4 requires.

### One record that was false

The results file recorded `"python_hash_seed": "0"` unconditionally — it
asserted the pinned value whether or not it was set. The protocol pins
`PYTHONHASHSEED=0`; recording the pin rather than the fact is a false record
of the run's conditions. The harness now records the **actual** value, records
whether it was pinned as required, and warns loudly when it was not.

### A pre-flight audit for the degeneracies that would still be there

Amendment 1 fixed the defects the pilot exposed. The owner's review asked for
one more thing before the long run: **a hunt for the degeneracies that were
*not* exposed.** A hidden degeneracy makes hours of compute worthless, and
the pilot already proved the class of bug is live in this project.

The pre-flight audit checks, before the campaign:

1. **The engine is deterministic for a given seed.** Without this the paired
   bootstrap over seeds is resampling noise.
2. **Different seeds give different results.** If every seed gave the same
   number there would be no seed variance to resample.
3. **Every arm has a denominator with room to spare** — the smallest
   `late_available` and `early_available` across all five arms must be large
   enough for the ratio to mean something, not 1 or 2.
4. **The V4 belief-cap pressure actually binds.** Phase G measured the belief
   pool *starved* — mean 5.17, max 6, against a cap of 15. If the pool never
   fills, V4 is an inert arm in the same way V5 was, and it must be reported
   as such rather than as a null result about the organism.
5. **The protocol's own factual claims hold** — notably "600 cycles, matching
   the Phase K K3 family", which was checked against Phase K's own
   preregistration.

### The Displacement Score: a diagnostic, added by the owner's review

The owner's second review raised the sharpest remaining scientific point:
**DI and PI are not opposites.**

| DI | PI | what it is |
|---|---|---|
| 0.8 | 0.8 | **coexistence** — the late structure was learned and the early structure was kept. That is not revision. |
| 0.8 | 0.1 | **genuine displacement** — the late structure replaced the early one. |

K3 already taught this project that **acquisition and displacement are
different phenomena**, and the two indices do not distinguish them on their
own. So a third quantity is now reported alongside them:

```
DS = DI - PI
```

**DS is a DIAGNOSTIC. It is not a primary metric, it is not a success
criterion, it enters no verdict, and it is never averaged with anything.**
It is reported per sweep point so that coexistence and displacement can be
told apart. A curve on which DS stays near zero while DI rises is a curve
showing *accumulation*, not *revision* — a distinction this phase would
otherwise blur.

### Revision latency: elevated from secondary to co-primary reporting

The owner's review also asked that the **trajectory** be taken seriously, not
just the endpoints: two organisms can end at the same DI and PI while
behaving completely differently — one crossing at cycle 170, the other at
cycle 590. Same endpoint, different developmental behaviour.

The trajectory was already being computed (see above). It is now reported at
the same level as the RT rather than as a footnote: for every sweep point,
the mean and median **revision latency** (cycles from the late group's
arrival until DI first exceeds 0.5), and how many seeds reached it at all.

**The four success criteria are unchanged.** Revision latency is a
co-primary *report*, not a new criterion: a phase that quietly added a
fifth criterion after the fact would be the same error in a different coat.

### Hysteresis: deliberately deferred to a future phase

The owner's review proposed the most interesting extension of all — **run the
axis in reverse** (late → early) and ask whether the system crosses back.
A system that crosses the threshold one way but not the other is showing
*hysteresis*, which is path-dependence, and a genuinely dynamic intelligence
might be expected to show it.

**This is not in Phase L.** It is recorded here as the natural successor
(Phase L.2), and it is deliberately not added now: adding a reverse sweep
to a protocol that has not yet run would double the campaign and change its
shape before there is any reason to. A protocol that measures one thing well
is worth more than one that measures two things imperfectly.

### Run order: the primary axis first

The owner's review noted that the support ratio carries nearly all the
theoretical weight — the hypothesis is essentially *a displacement boundary
exists* — and that V1 is the cleanest evidence of it. **The campaign runs V1
first** and the secondary arms after, so that the primary answer is available
early. This is a scheduling decision, not a protocol change: all five arms
are still declared, still run, and still reported, because the secondary arms
are what can detect H2-L³ (the operative variable is not support ratio).

### One thing deliberately NOT changed

**No more benchmarks.** The protocol's largest victory is that it stopped
caring about beating Markov or winning tasks and started caring about
characterising the organism. That is protected.

### What did not change in Amendment 2

No hypothesis, independent variable, sweep point, seed, metric definition,
baseline, success criterion or terminal outcome. The decision interval was
*corrected to match the stated procedure*, the success/failure statement was
made explicit, two declared secondary outcomes were implemented, and one
false record was fixed. **No gate was relaxed.**
