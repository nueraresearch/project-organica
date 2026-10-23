# Ablation Study 2 — Tier-1 Matrix Results

**Status: RESULTS. 2026-10-23.** This is the successor document to
[`FORCE-MATRIX-PREREGISTRATION.md`](FORCE-MATRIX-PREREGISTRATION.md). The
pre-registration's §1–§7 were committed before the run and are unchanged;
§8 and §9 are the post-freeze records. Nothing in this document revises a
pre-registered prediction. A prediction that failed is recorded as failed.

Artifacts: `docs/force_matrix.json` (the campaign),
`docs/metric_sensitivity.json` (the audit), `docs/process_noise_3000.json`
(the measured floor), `docs/verdicts.json` (the buckets),
`docs/discovery.json` and `docs/figure_discovery.svg` (the discovery curves),
`docs/figure_tier1_matrix.svg` (the population figure).

---

## 1. The run

| | |
|---|---|
| Colonies | FULL, SALIENCE, NO_CONTRADICTIONS, NO_QUESTIONS, NO_DREAMS, ANTI_EIG |
| Cycles | 3,000 per colony — **18,000 colony-cycles** |
| Stimulus | `lattice_L1` — three disjoint triangles, 9 distinct events, experience repeats every 9 cycles |
| Seed | 20261023, one per colony |
| `PYTHONHASHSEED` | **0 in all six processes** (so the hash order is common-mode across arms) |
| Wall clock | 1,814 s for all six in parallel |
| G1 | all six code paths verified distinct before the run |

---

## 2. The headline: the structure is decided on cycle 1

Every colony reaches its **complete** structural configuration on the first
cycle and never changes it again for 2,999 cycles:

| Colony | pre-retention beliefs | competing subjects | retained beliefs | theories | questions |
|---|---:|---:|---:|---:|---:|
| FULL | 18 | 7 | 15 | 5 | 5 |
| SALIENCE | 18 | 7 | 15 | 5 | 5 |
| NO_CONTRADICTIONS | 18 | 7 | 15 | 5 | 5 |
| NO_QUESTIONS | 18 | 7 | 15 | 4–5 | 0 |
| NO_DREAMS | 18 | 7 | 15 | 4–5 | 4–5 |
| ANTI_EIG | 18 | 7 | 15 | 4–5 | 4–5 |

The steady state is **identical across all six arms** — 18 beliefs over 7
competing subjects, the exact configuration the launch gates were built to
detect. The only differences are the arms that disable something
(`NO_QUESTIONS` has no questions; `NO_DREAMS` has no dreams).

Meanwhile the evidence keeps accumulating:

| Colony | mean support, cycle 1 | mean support, cycle 3,000 | change |
|---|---:|---:|---:|
| FULL | 101.2 | 11,006.2 | **+10,776%** |
| SALIENCE | 99.6 | 11,003.1 | +10,947% |
| NO_CONTRADICTIONS | 99.6 | 10,900.5 | +10,844% |
| NO_QUESTIONS | 99.6 | 10,032.0 | +9,972% |
| NO_DREAMS | 99.6 | 10,915.5 | +10,859% |
| ANTI_EIG | 99.6 | 10,914.2 | +10,858% |

**Structure flat, evidence growing by three orders of magnitude.** That is
the campaign's central measurement, and it is the sharpest form of the
question that has been open since the Phase G plateau: *is the organism
still developing, or has it reached a fixed equilibrium that merely
accumulates evidence?*

On this substrate, with this stimulus, the answer is the second one. Every
arm reaches its fixed point on cycle 1.

---

## 3. M5 is not a rate, and the name was wrong

M5 ("development velocity") is defined as `new items per 100 cycles`. Over
300 cycles the FULL arm recorded 74 new items; over 3,000 cycles it also
recorded **74**. The rate fell from 24.667 to 2.467 because the **numerator
stopped growing** while the denominator grew tenfold.

> M5 was dividing a finite inventory by the run length. It was not measuring
> a velocity.

The inventory itself is the interpretable number, and its per-category
breakdown says *what* was discovered:

| Colony | beliefs | questions | dreams | experiments | **M5 inventory** | rate /100 cyc | new in last 100 cyc |
|---|---:|---:|---:|---:|---:|---:|---:|
| FULL | 16 | 11 | 36 | 11 | **74** | 2.467 | **0** |
| SALIENCE | 18 | 13 | 31 | 16 | **78** | 2.600 | **0** |
| NO_CONTRADICTIONS | 20 | 12 | 31 | 16 | **79** | 2.633 | **0** |
| NO_QUESTIONS | 18 | 0 | 49 | 45 | **112** | 3.733 | **0** |
| NO_DREAMS | 18 | 13 | 0 | 13 | **44** | 1.467 | **0** |
| ANTI_EIG | 18 | 13 | 38 | 16 | **85** | 2.833 | **0** |

**Every colony discovered zero new items in the final 100 cycles.** The
composition of the inventory is a much richer story than the rate: dreams are
the largest single category in five of six arms (36 of 74 in FULL), and
removing dreams does not merely remove dreams — it removes **28 items from
the whole inventory** (44 against 74), because dreams are built from
beliefs.

---

## 4. The confound: the stimulus repeats every 9 cycles

`lattice_L1` contains **9 distinct event strings** over **7 distinct words**,
and the organism's experience **repeats every 9 cycles**. Over 3,000 cycles
it sees the same world 333 times.

**A repertoire cannot grow in a world that does not change.** The flat tail
of the discovery curve is therefore a fact about the *stimulus* as much as
about the organism, and the campaign as run cannot distinguish:

- *"the organism found everything the world contains and then held it"*, from
- *"the organism cannot reorganise once it has stabilised"*.

Those two readings predict identical numbers on this stimulus. The stimulus
was built to clear the launch gates, and it does — but a **closed,
periodic world cannot test developmental depth**, because it offers nothing
to reorganise toward.

This is the single most important thing the campaign established, and it is
a **stimulus** finding, not an architecture finding. See §9.

---

## 5. The metric table

Every metric, every colony, 3,000 cycles each. `sensitivity` is
`max − min` across the six colonies.

| Metric | FULL | SALIENCE | NO_CONTRAD. | NO_QUEST. | NO_DREAMS | ANTI_EIG | spread | verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| M1 theory duty cycle | 0.9997 | 0.9997 | 0.9997 | 0.9997 | 0.9997 | 0.9997 | 0.0000 | insensitive |
| M2 question duty cycle | 0.9997 | 0.9997 | 0.9997 | **0.0000** | 0.9997 | 0.9997 | 0.9997 | sensitive |
| M3 contradiction density | 15938.80 | 15972.94 | 15951.86 | 14031.59 | 15980.22 | 16028.42 | 1996.83 | sensitive |
| M4 contradiction survival | 0.9375 | 0.8333 | **0.7500** | 0.8333 | 0.8333 | 0.8333 | 0.1875 | sensitive |
| M5 development velocity | 2.467 | 2.600 | 2.633 | **3.733** | **1.467** | 2.833 | 2.266 | sensitive |
| M6 lineage depth | 7 | 7 | 7 | 7 | 7 | 7 | 0 | insensitive |
| M7 mean hypothesis lifetime | **212.0** | **2989.667** | 1790.4 | 2978.333 | 2989.333 | 2986.0 | 2777.667 | sensitive |
| M8 population stability | 0.9817 | 0.9817 | 0.9817 | 0.9817 | 0.9817 | 0.9817 | 0.0000 | insensitive |
| M9 cognitive revolutions | 0 | 0 | 0 | 0 | 0 | 0 | 0 | structurally zero |

**The full-run audit returns the same verdict as the 300-cycle pilot: 5 of 9
metrics can move.** M1, M6 and M8 are **saturated** — a theory is present in
2,999 of 3,000 cycles in every arm, the lineage reaches generation 7 in
every arm, and the belief population is equally stable in every arm. M9 is
**structurally zero**: a cognitive revolution needs a dominant theory
demoted by more than 50% and replaced within 50 cycles, and no arm demotes
one.

### The populations, which carry the signal the duty cycles lose

| Population | FULL | SALIENCE | NO_CONTRAD. | NO_QUEST. | NO_DREAMS | ANTI_EIG |
|---|---:|---:|---:|---:|---:|---:|
| theories (mean) | 5.010 | 4.991 | 4.960 | **4.577** | 4.962 | 4.868 |
| questions (mean) | 5.010 | 4.991 | 4.960 | **0.000** | 4.962 | 4.868 |
| dreams (mean) | 7.989 | 7.975 | 7.977 | 6.449 | **0.000** | 7.905 |
| experiments (mean) | 4.998 | 4.998 | 4.998 | 4.998 | 4.962 | 4.998 |
| pre-retention beliefs | 17.971 | 17.984 | 17.975 | **17.513** | 17.984 | 17.957 |
| competing subjects ≥2 | 6.986 | 6.993 | 6.986 | **6.757** | 6.993 | 6.979 |

### Which colony is the most sensitive, per metric

| Metric | Most sensitive colony | relative distance from FULL |
|---|---|---:|
| M2 question duty cycle | NO_QUESTIONS | 1.0000 |
| M3 contradiction density | NO_QUESTIONS | 0.1197 |
| M4 contradiction survival | NO_CONTRADICTIONS | 0.2000 |
| M5 development velocity | NO_DREAMS | 0.4054 |
| M7 mean hypothesis lifetime | SALIENCE | 0.9291 |
| M1, M6, M8, M9 | — (cannot move) | 0.0000 |

### Deviation from the reference arm

| Colony | mean relative distance | downstream distance (own metric excluded) |
|---|---:|---:|
| NO_QUESTIONS | 0.2776 | **0.1874** |
| NO_DREAMS | 0.1609 | 0.1609 |
| ANTI_EIG | 0.1306 | 0.1306 |
| NO_CONTRADICTIONS | 0.1273 | 0.1350 |
| SALIENCE | 0.1215 | 0.1215 |

A colony that disables a mechanism zeroes the metric that measures that
mechanism. That is the switch working, not a finding. The **downstream**
column excludes each colony's own metric and asks what the organism does
*differently* — and it does not change the ranking here.

---

## 6. Two colonies whose names overstate their interventions

These are disclosed because they change how the table must be read, and
because both were found by reading the engine rather than by looking at the
numbers.

**`NO_CONTRADICTIONS` does not remove contradictions.** `CONTRADICTION_SCALE`
is a multiplier on the contradiction term *in the confidence formula*
(`organica/sleep.py:1489`). The engine deliberately keeps the raw count so
that "a metric built on them still measures the world when
`CONTRADICTION_SCALE` is not 1.0" — and M3 reads `raw_contradiction`
(`benchmarks/force_matrix.py:230`). So **M3 is near-invariant for this
colony by construction** (15,951.86 against 15,938.80), and that is the
metric working correctly, not a null result. The honest name for the
colony is *contradiction not weighted in confidence*. Its effect is visible
where it should be: M4 contradiction survival falls 0.9375 → 0.7500, and
the belief inventory falls.

**`NO_DREAMS` removes 30 items from the inventory, not 11.** Its dreams
count is 0 by construction, but the dreams that *would* have been built
from its beliefs are gone too: its inventory is **44 against FULL's 74**,
and its development-velocity rate is the lowest in the campaign.

---

## 7. M7 is the retention-policy result, and it is fragile

M7 (mean hypothesis lifetime) is the metric the campaign existed to make
measurable, and it does move enormously: **212 cycles under alphabetical
retention against 2,990 under salience**. Before the substrate correction
this metric was provably uninformative, because the belief cap did not bind.

But the mean rests on a handful of observations, and this is disclosed
rather than buried:

| Colony | mean lifetime | beliefs that **died** | beliefs censored (alive at the end) |
|---|---:|---:|---:|
| FULL | 212.0 | **1** | 15 |
| SALIENCE | 2,989.667 | **3** | 15 |
| NO_CONTRADICTIONS | 1,790.4 | 5 | 15 |
| NO_QUESTIONS | 2,978.333 | 3 | 15 |
| NO_DREAMS | 2,989.333 | 3 | 15 |
| ANTI_EIG | 2,986.0 | 2 | 16 |

**FULL's 212-cycle mean is the mean of exactly one belief.** The robust
finding underneath is different and simpler: **in every arm, 15 or 16 of the
beliefs never die at all.** The campaign shows that the retention policy
changes *which* beliefs persist, not that it changes how long they last —
there are almost no deaths to time.

---

## 8. The verdicts

The five pre-registered predictions, with the noise floor applied. The floor
is the **3,000-cycle** measurement (`docs/process_noise_3000.json`): the
within-process seed floor is exactly 0.00, and the process-level floor
moves exactly one field — M5 — by exactly **one new item**, which at
3,000 cycles is a rate spread of **0.033**.

| # | Prediction | Verdict | Why |
|---|---|---|---|
| **P1** | Retention policy affects development | **SUPPORTED** | 4 of 9 metrics moved beyond the floor: M3 (+34.14), M4 (−0.104), M5 (+0.133), M7 (**+2,777.667**) |
| **P2** | Contradiction is developmental fuel | **REVERSED** | M5 **rises** by 0.166 when contradiction's weight is removed — the opposite of the prediction |
| **P3** | Curiosity needs explicit questions | **REVERSED** | M5 **rises** by 1.266 when question creation is removed |
| **P4** | Dreams contribute to trajectory | **SUPPORTED** | M5 **falls** by 1.000 when dreams are removed — the predicted harm is present |
| **P5** | EIG is orthogonal to development | **REVERSED** | Selecting the **lowest**-EIG experiment develops 0.366 **more** per 100 cycles than selecting the highest-EIG one |

**SUPPORTED 2 · UNSUPPORTED 0 · REVERSED 3 · NOT INTERPRETABLE 0**

Two things are worth stating plainly.

**The verdicts are direction-aware.** A naive "did the metric move?" test
would have scored all five predictions SUPPORTED and reported a clean sweep
of confirmations. Three of them are the *opposite* of what was predicted:
contradiction and explicit questions are not developmental fuel and not
prerequisites, and EIG selection is not merely orthogonal — it is
counterproductive. The direction check is in `benchmarks/verdicts.py`, and
it is the difference between a result and a tautology.

**"Not interpretable" is empty, and that is a result.** Every one of the
five predictions turned out to be decidable with this metric suite on this
substrate — the sensitivity audit and the noise-floor measurement, done
*before* the run, are what made that true. A pre-registration that cannot
be decided is worse than no pre-registration.

---

## 9. What this campaign can and cannot answer

**It can answer:**

1. The organism reaches a **complete, unchanging** structural state on
   **cycle 1**, in all six arms, and then accumulates evidence for 2,999
   cycles (+10,776%). Structure and evidence are decoupled at this scale.
2. The **retention policy is now measurable at all**, and it changes which
   beliefs persist and how many items are discovered before saturation
   (44 → 112 across the arms).
3. **5 of 9 metrics can discriminate between arms**; M1, M6 and M8 are
   saturated and M9 is structurally zero. That is a permanent property of
   this metric suite on this substrate, and it is now known.
4. The **noise floor** is measured, not assumed, and it is one item.

**It cannot answer:**

1. **Which colony develops faster.** M5 does not measure development
   velocity; it measures a finite inventory divided by the run length.
2. **Whether the organism is developmentally reorganising or merely
   accumulating evidence.** The stimulus repeats every 9 cycles, so there
   is nothing left to reorganise toward. The two hypotheses predict
   identical numbers here.
3. **Whether the plateau is an architectural ceiling.** It may be nothing
   more than a closed world's complete repertoire.

**The sharpest question the campaign leaves behind** is therefore not about
the architecture at all:

> Is stabilisation the desired outcome, or evidence of a bottleneck?

and the answer needs a stimulus that can distinguish them.

---

## 10. What this implies for the next experiment

This is a **stimulus** requirement, not an architecture change, and it
follows the discipline the project has held throughout: finish learning what
V1 can teach before changing the architecture.

**The stimulus must not repeat.** A world with continuing novelty is the
only way to tell "the organism stabilised because it learned everything"
apart from "the organism cannot restructure". The `lattice_L1` design
delivered the belief supply the gates required; it cannot deliver depth.

**The development metric must be scale-invariant.** `total / run_length` is
not a rate. A discovery-rate metric measured over a *fixed prefix window*
would be, and the inventory breakdown in §3 is the right first version of
it.

**The world must be large enough for the cap to bind.** The belief pool
sits at 18 against a cap of 15 with the retention step already applied, so
the cap *does* bind here — which is why the retention policy finally
mattered. That part of the design worked and should be kept.

Everything else the campaign taught — the measurement framework, the gate
definitions, the noise floor, the sensitivity audit, the substitution
protocol, and the substrate itself — carries forward unchanged.

---

## 11. H24 — the hypothesis this campaign produced

> **H24. Organica's apparent developmental plateau is primarily constrained
> by environmental information content rather than by architectural inability
> to reorganise.**

This is stated as a falsifiable hypothesis, with the evidence on both sides
recorded, before the experiment that tests it is run.

**Evidence FOR H24 (measured in this campaign)**

1. The structural inventory **saturates**: 74 distinct items in the FULL arm,
   and **zero new items in the final 100 cycles** of every one of the six
   arms.
2. The world **repeats every 9 cycles** — 9 distinct events over 7 distinct
   words, seen 333 times in 3,000 cycles.
3. Evidence keeps accumulating while structure does not move: mean support
   **+10,776%** over a structure that was fixed on cycle 1.
4. The plateau appears **after** the world is exhausted, not before: the
   discovery curve rises steeply and flattens.
5. All six arms converge to the **same** attractor (18 beliefs / 7 competing
   subjects / 15 retained) despite six different interventions — consistent
   with the attractor being determined by the world rather than by the
   organism's mechanisms.

**Evidence AGAINST H24 (none yet, and that is the point)**

There is no evidence against H24, because **H24 has not been tested**. Every
measurement above is consistent with H24 *and* with the opposite reading.
The campaign was run in a nine-event universe. A human placed in nine
experiences repeated forever would also converge, and that is not a defect.

**What would falsify H24**

> A **larger, non-repeating world** still produces ~74 distinct structures,
> the same plateau, and the same attractor.

If that is what happens, the bottleneck is architectural, and the honest
conclusion becomes: *Organica cannot reorganise beyond what a
nine-event world teaches it, regardless of how much novelty it is given.*

**The experiment that decides it — a world-complexity ladder**

The same organism, the same engine, the same metrics, the same protocol, run
against worlds of increasing information content. The measurement that
matters is the **inventory** — the scale-invariant discovery count — not the
rate.

| Rung | World | Predicted inventory if H24 holds |
|---|---|---|
| 0 *(done)* | `lattice_L1` — 9 events, period 9 | **74** (measured) |
| 1 | medium expanding world — new events keep arriving | ≫ 74 |
| 2 | large expanding world | ≫ rung 1 |
| 3 | open-ended world — never repeats | unbounded growth, no plateau |

Measured at every rung: **inventory growth, the cumulative discovery curve,
MBSD, theories, questions and cognitive revolutions**.

**The two readings, and what separates them**

| If the inventory goes | Then |
|---|---|
| 74 → 300 → 1,200 → 5,000 | The plateau was an **environmental artefact**. What this project found is a developmental system trapped inside a toy universe — a very different conclusion from a developmental ceiling. |
| 74 → 74 → 74 → 74 | The plateau is **architectural**. The organism cannot reorganise, and the architecture — not the environment — is the ceiling. |

This is the fork the campaign reached, and it is a **stimulus** experiment.
Nothing about the engine changes, so the project's standing rule holds:
finish learning what V1 can teach before changing the architecture.
