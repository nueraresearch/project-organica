# Ablation Study 2 — Tier-1 Matrix Pre-registration

> **Which "V2"?** This file was formerly titled *Ablation Matrix V2*. It is
> the second **research campaign** — *Ablation Study 2* — and it is not the
> package version (0.6.0, SemVer 2) and not the **architecture generation**
> (*Organica 2*, planned — see `docs/ORGANICA-V2-DESIGN-NOTES.md`). The three
> namespaces are tabulated in `CHANGELOG.md` and `docs/USER-MANUAL.md` §11.6.

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

---

## 9. Sensitivity audit and the noise floor *(added after the freeze — the frozen text above is unchanged)*

§2 froze nine metrics. A frozen metric is not the same as a metric that can
move, and the rule in §4 — "per-metric deltas smaller than seed noise are
reported as *not interpretable*" — is only usable if the noise is measured
rather than guessed. Two audits were run before the 3,000-cycle campaign so
that the result table says what it can and cannot support.

### 9.1 Which metrics can move at all

`benchmarks/metric_sensitivity.py` → `docs/metric_sensitivity.json`. Six
colonies, 300 cycles, `lattice_L1`, one seed.
`sensitivity(metric) = max − min` across the six colonies.

| Metric | Name | Spread | Relative | Verdict |
|---|---|---:|---:|---|
| M1 | Theory duty cycle | 0.0000 | 0.0% | **insensitive** |
| M2 | Question duty cycle | 0.9967 | 100.0% | **sensitive** |
| M3 | Contradiction density | 275.71 | 15.1% | **sensitive** |
| M4 | Contradiction survival | 0.1875 | 20.0% | **sensitive** |
| M5 | Development velocity | 14.666 | 50.0% | **sensitive** |
| M6 | Lineage depth | 0 | 0.0% | **insensitive** |
| M7 | Mean hypothesis lifetime | 111.53 | 38.4% | **sensitive** |
| M8 | Population stability | 0.0000 | 0.0% | **insensitive** |
| M9 | Cognitive revolutions | 0 | 0.0% | **structurally zero** |

**Five of nine can move. Three cannot. One is structurally zero.**

The three that cannot move are not broken; they are **saturated**, and the
distinction matters for how the results are read:

- **M1 (theory duty cycle)** — 0.9967 in *every* colony. A theory is present
  in 299 of 300 cycles in every arm, including `NO_QUESTIONS`. The metric
  asks *whether a theory exists*, and after the substrate fix one always
  does. There is nothing for it to distinguish. The **population mean**
  (`theories_mean`: 5.10 for FULL, 4.91 for SALIENCE) carries the signal the
  duty cycle lost, and both are reported.
- **M6 (lineage depth)** — 7 in every colony. The lineage reaches generation 7
  in all six arms. Insensitivity here is a **positive** result: it says the
  interventions do not change how deep the lineage goes.
- **M8 (population stability)** — 0.9422 in every colony. The belief
  population is equally stable in every arm. Insensitivity here means the
  interventions **do not destabilise** the population, which is itself
  informative and is reported as such rather than as a null.
- **M9 (cognitive revolutions)** — 0 in every colony, *structurally*: a
  revolution needs a dominant theory demoted by more than 50% and replaced
  within 50 cycles, and no arm demotes a dominant theory. §3 already
  anticipated this: "0 across all arms is itself a finding and is reported as
  one."

**This audit was run at 300 cycles. The campaign is 3,000.** It will be re-run
against the full artifact, and both verdicts reported.

### 9.2 The noise floor, measured two ways

**Within one process.** `benchmarks/seed_noise.py` → `docs/seed_noise.json`.
Three seeds, the same colony, the same stimulus. The spread is **exactly
0.00** for all nine metrics and all six populations. The engine is
deterministic given (stimulus, seed) inside a process.

**Between processes.** That is not the floor that binds, because the campaign
runs each colony in its own process. CPython randomises string hashing per
process unless `PYTHONHASHSEED` is pinned, and the engine's candidate
construction walks collections whose iteration order depends on a string
hash. `benchmarks/process_noise.py --sweep` → `docs/process_noise.json`
runs the **same** colony at the **same** seed in **six** processes with
`PYTHONHASHSEED` 0–5:

> **16 of 17 fields are bit-identical across all six processes.**
> **One field varies: M5, development velocity** — values 24.667 / 24.667 /
> 24.667 / 25.000 / 24.667 / 25.000, **spread 0.333, relative 1.34%**.

M5 counts *newly created* items per 100 cycles, and it is the one metric
sensitive to the order in which candidates are enumerated: a different hash
order flips whether one particular candidate is counted as new. No
population moves at all — `theories_mean` is 5.1 in all six processes,
`pre_beliefs_mean` is 17.707 in all six.

### 9.3 The protocol decision this forces

The pilot ran its six colonies as six separate processes. Unpinned, that gave
each colony a **different** hash order — so hash noise would have entered the
*between-colony* comparison, which is the only comparison this campaign
makes. That is a measurement artifact masquerading as a colony difference.

The campaign therefore runs through **`benchmarks/run_matrix.py`**, which:

1. runs the **G1 code-path verification once**, before any colony;
2. launches the six colonies in parallel as six processes, **all with the same
   `PYTHONHASHSEED=0`**, so the hash order is a fixed environmental condition
   applied identically to every arm rather than an independent draw per arm;
3. merges the six parts into one artifact and records the **provenance** —
   the hash seed used, the git commit, the branch, and the wall clock.

Pinning also makes the whole campaign **reproducible**: re-running
`run_matrix.py` on the same commit reproduces the artifact exactly.

The alternative — one process running all six colonies serially — would also
have made the hash order common-mode, but would have serialised six
20-minute colonies into two hours.

**Both floors are recorded here, and the smaller one is not the one that
binds.** A delta must beat **0.333 new-per-100-cycles on M5** to be
interpretable, and is interpretable outright on M2, M3, M4, M7 and on every
population mean.

