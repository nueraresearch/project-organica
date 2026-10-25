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
| **Revision latency** | cycles from the late group's arrival until DI first exceeds 0.5 | distinguishes *never* from *slowly* |
| **Knowledge preservation** | fraction of early-group pairs still asserted at the end, across the whole run | PI at the final cycle is a snapshot; this is the trajectory |
| **Absolute late incorporation** | raw count of retained late pairs | DI is a ratio and can hide a small absolute number |

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
   over seeds has a 98.33% interval that excludes both endpoints of the sweep.

Criterion 4 is what separates a boundary from a coincidence. A crossing point
that can be anywhere on the axis is not a boundary.

**If the criteria are met, the finding is the curve and its RT** — a
characterisation, not a victory. If Organica's curve is *worse* than a
baseline's, that is a legitimate finding too, and the phase reports it.

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
| **Decision interval** | 98.33% paired percentile bootstrap (Bonferroni across the arms), 10,000 replicates |
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
   produce a different world from the plain arm; and the density arm must
   actually change the event count. A metric can be perfect and the design
   still dead, and that is exactly what the first pilot demonstrated.

All three audits are permanent, and all three run on every invocation of the
harness.

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
from a paired bootstrap over seeds has a 98.33% interval that excludes both
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

### One item for the owner to settle

Section 6 and section 8 state a **98.33%** decision interval, and gloss it as
"Bonferroni across the arms". Across five arms, Bonferroni gives
0.05/5 = 0.01, i.e. a **99%** interval; 98.33% corresponds to 0.05/3. The two
readings disagree.

The harness currently implements **98.33%**, following the number the protocol
states rather than the parenthetical gloss. **This is flagged for the owner
before the campaign runs**, because it changes which verdicts are reachable.
Nothing depends on it yet: no Phase L outcome exists.

### What did not change

No hypothesis (H-L1, H-L1a/b/c), no independent variable, no sweep point, no
seed, no metric definition, no baseline, no success criterion, and no
pre-committed terminal outcome was altered. The four defects were all in the
harness's *implementation* of the protocol as written; the corrections make
the code do what this document already said. No gate was relaxed, and one
audit was added.
