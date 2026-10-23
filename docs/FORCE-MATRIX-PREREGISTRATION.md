# Ablation Matrix V2 — Pre-registration

**Status: FROZEN. 2026-10-23 07:20 MDT.** This file is committed *before* the
V2 campaign runs. The metric definitions below, the gate definitions, the
colony list and the stoplight are fixed. No prediction and no metric may be
revised to fit a result. If a metric turns out to be unmeasurable, it is
reported as **not measurable** and excluded — never zeroed.

> **The gates in §1 were validated against the 11 existing V1 conditions
> before this file was frozen** (`benchmarks/gate_validation.py`,
> `benchmarks/mbsd_census.py`, journal §20). The validation changed the
> *form* of the gate, which is why it is recorded here rather than
> assumed. The metrics in §2 were frozen after the validation and have not
> been touched since.

Everything here is preceded by the V1.5 instrumentation audit
(`docs/instrumentation_audit.json`, journal §19), which changed the plan
before this file was written. The audit's findings are inputs, not
results: they are already in the record and cannot be re-litigated after the
run.

---

## 0. Why the campaign is gated

The audit measured **retention pressure** on every retained object type:

```
retention_pressure = pre_cap_pool_size / cap
```

`< 1.0` no pressure · `1–2` weak · `2–5` useful · `> 5` strong

On the current study stream the hypothesis layer's pressure is **0.35** — it
never binds — so "alphabetical" and "salience" select the same membership
in every cycle. Running the retention arm on that stimulus would compare
two identical colonies.

**The scarce resource is not vocabulary. It is competing expectations about
the same subject.** The audit measured: 42 world tags → 1 theory; 97 world
tags → 0 theories. More diversity *reduced* theory production. The resource
is *branch structure* — subjects with more than one competing successor.

### 0.1 The validated mechanism

The gate was proposed as *Multi-Belief Subject Density* and then tested
against the 11 V1 conditions that already exist. The result is stronger
than a correlation:

> **Layer 5 forms exactly one theory per subject holding >= 2 beliefs,
> capped at `MAX_THEORIES`.**
> The identity `theories == min(competing_subjects, 8)` holds in **100% of
> cycles in 9 of the 11 conditions**, 99.7% in Random Sleep, and 18.0% in
> No-Hypothesis-Layer — the one condition that bypasses Layer 4 by design
> and builds 6 theories straight from workflow components with **zero**
> competing subjects.

So the numerator of the proposed gate is not a *predictor* of theory
formation — it **is** the mechanism. Two consequences:

1. The **density ratio** adds nothing beyond the absolute count. The gate
   is stated below as a **count**, which is the form the mechanism
   supports.
2. The final-cycle cross-condition correlation is weak (0.017 including
   No-Hypothesis-Layer, 0.775 excluding it) because G5 oscillates and that
   condition is a designed exception. The per-cycle identity is the real
   result, and it is the one that generalises.

**New constraint this surfaced.** `MAX_THEORIES = 8` caps theory capacity
at 8. A stimulus producing more than 8 competing subjects would push the
excess *invisible* to M1, M8 and M9 — the same measurement blind spot as
the hypothesis cap, one layer up. The stimulus must therefore target
**5–7** competing subjects: enough for a rich theory ecology, and below the
cap so M8 and M9 stay measurable.

---

## 1. Gates (all four must pass before the campaign runs)

### Where the gates are measured, and why it matters

Every gate below is evaluated on the **pre-retention belief pool** — the
beliefs as Layer 4 formed them, *before* `MAX_HYPOTHESES` truncates them.

This was not the first choice, and the reason it changed is worth stating.
Layer 5 forms theories from the **retained** set, so the retained
competing-subject count is what actually determines the theory population.
But the retained set is a function of `HYPOTHESIS_RETENTION` — which is
one of the six arms under test. A gate that depends on the arm under test
is not a gate; it is a hypothesis wearing a gate's clothes.

The supply-side quantities (how many subjects hold competing beliefs, how
big the pool is) are policy-independent, so the gate is stated there. The
*retained* competing-subject count is still measured, every cycle, in every
arm — but as a **campaign outcome**, not as a gate. Whether the policy
changes it is precisely the P1 question.

On the study stream the two definitions coincide: the pre-cap pool peaks at
8 against a cap of 15, so retention dropped nothing and the V1 measurement
(`docs/ablation_study.json` → `observations.contradiction_history`) was
already the pre-cap quantity.

### Gate G-CS — competing-subject supply *(primary; replaces the proposed density form)*

> **At least 3 subjects hold >= 2 active beliefs**, and the count is
> **>= 5 at some point in the run**, with a target of **5–7**.

- *Why 5–7 and not 3.* 3 clears the proposed bar, but `MAX_THEORIES = 8`
  means the theory layer saturates at 8. A population of 5–7 keeps M1, M8
  and M9 sensitive to change in the theory ecology.
- *Why not the density.* Density is a ratio of two counts that the
  mechanism ties together; the absolute count is what Layer 5 consumes.

**Status on the current study stream: ❌ FAILS** — 1 competing subject
(mean 1.37, max 4; only one subject, "session", ever competes).

### Gate G-P1 — retention pressure

> `retention_pressure(hypotheses) > 1.0` — the belief pool must exceed
> `MAX_HYPOTHESES` (15), so the retention policy has something to choose
> between.

**Status on the current study stream: ❌ FAILS** (0.35; pool max 8).

### Gate G-SUP — belief supply

> `belief_pool_size > MAX_HYPOTHESES` (15) — with G-CS satisfied, the
> surplus beliefs must be spread across *different* subjects, not piled on
> one.

G-P1 and G-SUP are numerically the same inequality; they are kept separate
because they fail for different reasons and a fix for one is not a fix for
the other. A stimulus can raise G-P1 by piling more beliefs onto one
subject (leaving G-CS failing), and can satisfy G-CS with 3 subjects
holding 3 beliefs each (far short of 15). **Both are checked.**

**A stimulus that satisfies G-CS and G-P1 but pushes competing subjects
above 8 has failed anyway** — the theory layer would be saturated and M1,
M8 and M9 would be blind to the surplus.

### Gate G-EXP — theory layer unsaturated

> `max(theories over the run) < MAX_THEORIES` — so the theory population is
> never clipped by the cap, and M8/M9 can see it move.

This gate was added because the validation surfaced `MAX_THEORIES = 8` as
a second cap with the same failure mode as the hypothesis cap. It is the
same class of defect in a different layer, and it would have made the
campaign silently blind in exactly the way G-P1 exists to prevent.

It is stated on the **observed theory count** rather than on a proxy, and
it must hold in **every arm**. A gate that only the salience arm passes
would be rigging the comparison; a gate that no arm passes means the
stimulus is wrong.

### Gate G-SUS — sustained, not peaked

> G-CS, G-P1 and G-EXP hold **simultaneously in at least 60% of the tail
> cycles** (the last half of the run).

Added after the first branch stimulus was measured. It passed every other
gate *on peaks* — belief pool p95 of 17, 7 competing subjects, pressure 1.13
— while its mean belief count was 2.97 and **55% of tail cycles produced
zero beliefs at all**. A gate that passes on peaks is a measurement of luck.

The 60% floor is a working value, not a derived one. It is recorded here
before any stimulus is chosen, so it cannot be tuned to a result.

---

## 2. Metrics M1–M9 (frozen)

All metrics are computed **per cycle** from the instrumented sleep service,
then aggregated over the run.

### Population classes

| Class | Definition |
|---|---|
| **belief** | a Layer-4 hypothesis whose expectation is not `high_structural_significance` |
| **marker** | a Layer-4 hypothesis whose expectation is `high_structural_significance` — inert; Layer 5 discards it on sight |
| **theory** | a Layer-5 theory |
| **question** | a Layer-5 question |
| **dream / investigation / experiment** | Layers 6 / 7 / 8 |

> **Markers are excluded from every belief metric.** A marker is not a
> belief, so counting it would make "hypothesis density" a measurement of
> marker count rather than of belief ecology. Marker counts are reported
> separately in every run so the exclusion is auditable.

### M1 — Theory Duty Cycle

```
TDC = cycles_with_at_least_one_theory / total_cycles
```
Range 0.0–1.0. Computed over the **last 2,000 cycles** of the run and over
the whole run; both are reported.

### M2 — Question Duty Cycle

```
QDC = cycles_with_at_least_one_question / total_cycles
```
Range 0.0–1.0. Same two windows.

### M3 — Contradiction Density

```
CD(cycle) = sum(contradiction_count over active BELIEFS) / active_beliefs
```

Primary tension metric. Reported as mean, median, p95 and max over the run.

*Unit note.* `contradiction_count` is the **raw** count, retained in the
evidence dict alongside any scaled value, so M3 measures the world and not
the axis. The companion **share** form is also reported:

```
CD_share(cycle) = sum(raw_contradiction) / sum(support + raw_contradiction)
```
because the raw count is partly a measure of how much evidence a subject has
accumulated. A rise in `CD` with a flat `CD_share` means the organism is
getting more evidence, not more contested.

### M4 — Contradiction Survival

```
CS = (contradiction_bearing_beliefs still alive at run end)
   / (contradiction_bearing_beliefs ever created)
```

A belief is *contradiction-bearing* if it ever had `contradiction_count > 0`.
A belief is *alive* if it appears in the final cycle's belief set. This is a
survival rate over the run, not a per-cycle quantity.

### M5 — Development Velocity

```
DV = (new_beliefs + new_questions + new_dreams + new_experiments) / cycles
```
where *new* means an id not seen in any earlier cycle. Beliefs, not markers.
Reported per 100 cycles.

### M6 — Lineage Depth

```
M6  = the maximum generation number reached by any stored candidate
M6b = the maximum ancestry chain length, counting back to a Layer-1 anchor
```

M6b is supplementary and does not enter the stoplight. Both are reported
because a maximum generation number and a chain depth are different claims:
the first says the ladder was climbed, the second says the climb was real.

### M7 — Mean Hypothesis Lifetime

```
lifetime(h) = death_cycle(h) - birth_cycle(h)
M7 = mean(lifetime) over beliefs whose death was OBSERVED
```

`birth_cycle` = first cycle in which the belief id appears.
`death_cycle` = the cycle after the last cycle in which it appears.

**Censoring is disclosed, not hidden.** A belief still present in the final
cycle has an unobserved death. Those observations are **excluded from the
mean** and their count is reported alongside it as `censored`. A run in
which most beliefs are censored is reported as
`M7: not measurable (n censored = X of Y)`.

### M8 — Population Stability Index

```
PSI(class) = 1 - (stdev(per-cycle population) / mean(per-cycle population))
```

Computed separately for **beliefs**, **dreams**, **questions** and
**theories**. A class that is empty for the whole run is reported as
`not measurable`, not as 0.

### M9 — Cognitive Revolution Count

A **theory replacement event** requires all of:

1. theory `t` was the **dominant** theory in some cycle (highest confidence
   among that cycle's theories);
2. its confidence later **falls by more than 50%** of its dominant-cycle
   value;
3. a **different** theory becomes dominant within **50 cycles** of that
   fall.

Each demoted theory counts at most once. The count is reported together
with the number of demotions that failed condition 3, so the difference
between "theories fell" and "theories were replaced" stays visible.

### Metrics excluded, and why

| Metric | Status | Reason |
|---|---|---|
| `cy` (questions resolved ÷ generated) | **not measurable** | No experiment executor exists; no question is ever resolved, so it is identically 0 for every condition. Excluded, never zeroed. |
| `eig_star` (entropy removed by an experiment) | **not measurable** | Experiments are generated but never executed. |
| `dpf` (designer surprise) | **pending owner protocol** | Requires the owner to record predictions before the run. |

Zeroing these would deflate every score by roughly 30% and would look like
a measurement. They are excluded, and the exclusion is stated every time
the aggregate is reported.

---

## 3. Stoplight

| Metric | Good signal | Note |
|---|---|---|
| M1 Theory Duty Cycle | **Up** | vs the FULL arm |
| M2 Question Duty Cycle | **Stable / Up** | a collapse to 0 is a failure, not a neutral result |
| M3 Contradiction Density | **Non-zero** | non-zero in *every* arm is the precondition; the comparison is between arms |
| M4 Contradiction Survival | **Up** | |
| M5 Development Velocity | **Up** | |
| M6 Lineage Depth | **Up** | |
| M7 Mean Hypothesis Lifetime | **Balanced** | neither "0" (nothing survives) nor unbounded |
| M8 Population Stability | **Up** | per class; report all four |
| M9 Cognitive Revolution Count | **> 0 eventually** | 0 across all arms is itself a finding and is reported as one |

The stoplight is a **reading guide, not a pass/fail**. The primary result
is the per-metric delta table plus the population table, exactly as in V1:
the aggregate `es` index counts structures, not beliefs, and an ablation
can remove most of the organism and still score "cosmetic".

---

## 4. The colonies (six)

| Code | Colony | What it changes |
|---|---|---|
| `FULL` | Full system, **alphabetical** retention | the reference arm |
| `SALIENCE` | Salience retention | the P1 arm — which beliefs survive |
| `NO_CONTRADICTIONS` | `CONTRADICTION_SCALE = 0` | is contradiction fuel or bookkeeping? |
| `NO_QUESTIONS` | Question creation disabled | is curiosity gated on explicit questions? |
| `NO_DREAMS` | Dream generation disabled | do analogies contribute to trajectory? |
| `ANTI_EIG` | experiments selected by **lowest** EIG | does anything break if selection is actively bad? |

3,000 cycles each, full stream, 8 events per cycle (the daemon's cadence),
cold start per colony, one fixed seed per colony, applied **in-process** by
subclassing — the engine source is never edited for a campaign.

**Seed discipline:** one seed per colony, so per-metric deltas smaller than
seed noise are reported as *not interpretable*, not as findings. This
limitation was disclosed in V1 and carries forward.

---

## 5. Order of operations

1. **Freeze this file.** ✔ committed before any run.
2. **Design the branch-structured stimulus** and measure it against the
   three gates.
3. **Re-run the gates** on the chosen stimulus.
4. **Only then** run the six colonies at 3,000 cycles.

If step 3 fails for the chosen stimulus, step 2 is revisited — a *new
stimulus*, with the measurement reported. No gate is relaxed to make a
campaign runnable, and no campaign is run with a failed gate and reported
as if it had passed.

---

## 6. What would falsify this campaign

| Prediction | Falsified if |
|---|---|
| Retention policy affects development | `FULL` and `SALIENCE` agree on every M1–M9 metric, *and* the gates passed |
| Contradiction is developmental fuel | `NO_CONTRADICTIONS` matches `FULL` on M1, M5, M6 |
| Curiosity needs explicit questions | `NO_QUESTIONS` collapses M1 and M5 |
| Dreams contribute to trajectory | `NO_DREAMS` leaves M1/M5/M6 unchanged |
| EIG is orthogonal | `ANTI_EIG` matches `FULL` on M1–M9 |

A falsified prediction is recorded as falsified in this file's successor and
in the journal. It is not revised.

---

## 7. Disclosure

Two instrumentation defects were found during V1.5 and are disclosed here
because they shape how these numbers must be read:

1. **The archived contradiction series was `null`, not zero.** The archive
   read a log key the daemon never writes. The true final value is 400,550.
   The archive is now a committed tool that re-derives it.
2. **A measurement in the first audit read the wrong report attribute** and
   reported a working layer as dead. Fixed; the parameter map was re-run
   and the verdicts were unchanged.

Any further defect found during this campaign is disclosed **in place**, in
this file, before the results are interpreted.

---

## 8. Gate re-run record *(added after the freeze — the frozen text above is unchanged)*

§1–§7 were committed before any stimulus was chosen. Nothing in them has
been edited to fit a result. This section is the record of §5 step 3.

**The gate re-run found a defect in the substrate, not in the stimulus.**
`MemoryService.store()` builds the co-occurrence and temporal graphs from
world events only, but the tag-frequency counter was maintained over *all*
stored events — including the organism's own sleep payloads — and that
counter is the **denominator** of the Layer-1 edge strength
(`ratio = count / source_freq`, where `count` is a world edge count). The
two sides of the ratio measured different populations, and the survival
filter discarded the world's own structure. Measured: 4 surviving edges,
0 processes, 0 workflows, 0 beliefs.

The counter is now scoped to world events, like the graph it normalises.
The correction is applied **identically to all six colonies**, so it is not
a confound within the campaign; it is a change of substrate before it,
which is what a pre-registration is for. Full disclosure in journal §21.8.

**Result** (`benchmarks/gate_check.py` → `docs/gate_check.json`, 300 cycles,
gates evaluated on the pre-retention pool):

| stimulus | belief pool mean/max | subjects ≥2 mean/max | theories mean/max | tail cycles passing every gate |
|---|---|---|---|---:|
| study stream *(control)* | 5.17 / 6 | 1.00 / 1 | 1.06 / 3 | 0% |
| `branch_r4` | 18.00 / 18 | 7.00 / 7 | 5.41 / 6 | **100%** |
| **`lattice_L1`** | **17.99 / 18** | **6.99 / 7** | 4.91 / 5 | **100%** |
| `lattice_L3` | 16.00 / 16 | 6.00 / 6 | 4.98 / 5 | **100%** |

**G-CS ✅ · G-P1 ✅ · G-SUP ✅ · G-EXP ✅ · G-SUS ✅.**

**The chosen stimulus is `lattice_L1`** — three disjoint triangles, seven
subjects, eighteen beliefs. It is chosen over `branch_r4` because its
vocabulary is nine tags instead of twelve, so the *same* belief supply is
carried by fewer words, and because `branch_r4` reaches **8** competing
subjects at peak, which touches `MAX_THEORIES = 8`; `lattice_L1` peaks at 7
and its theory population at 5.

**The campaign is now unblocked. §1–§7 stand as frozen.**

