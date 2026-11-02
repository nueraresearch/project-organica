# The transition construct: onset of `DI` as the primary candidate predictor

**Status: exploratory construct record. No engine run, no seed allocated, no confirmatory claim.**
Stage B is not authorised. Every number here is written by `benchmarks/di_transition_construct.py` into
`docs/di_transition_construct.json`, and `tests/test_di_transition_construct.py` asserts this document against
that artifact.

The owner's decision of 2026-11-02 makes a **transition summary** the primary candidate predictor and keeps the
**settled state** as a separate, unresolved construct. This record does the audit that decision requires. It
reads no behavioural endpoint: the choice of summary is made on measurement grounds alone, before any outcome is
examined, because a summary chosen for how well it relates to behaviour would be an outcome in disguise.

---

## 1. The decision, and what it is not

| Element | Decision |
| --- | --- |
| primary candidate | a transition summary, specified in §3 |
| scientific question | does the way internal structure develops predict what the system subsequently does? |
| settled state | retained as a separate construct, **unresolved** — `docs/DI-MEASUREMENT-WINDOW.md` §3.2 shows no settled state exists in the record |
| validation | independent worlds, disjoint seeds, criteria pre-committed (Stage B, §7, **not authorised**) |
| failure | the construct is rejected if it fails validation; the claim is not reduced to fit |

This is not a repair of the settled-state measurement. The settled-state construct asked *what structure exists
at a designated time*, and that question remains open with no window attached to it. The transition construct
asks *how structure emerges*, and it is measured with a different quantity on a different grid.

---

## 2. What the three candidate summaries can actually measure here

Each candidate was computed on all 240 stored records, with no behavioural quantity read. The comparison is of
measurement properties, not of results:

| candidate | defined for | censored | unit | within-config SD (`6:1`) | within-config range (`6:1`) | within-config share of variance | rank stability at cycle 450 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **onset** | 119 / 240 records; 119 / 120 in the four configurations that produce structure | 121 | cycles | 12.4 (median 329) | 289–354 | 7.1 % | 1.000 |
| exposure | 240 / 240 | 0 | pairs | 0.44 (median 6.45) | 5.33–7.33 | 1.4 % | 0.925 |
| slope | 84 / 240 when the run is cut at 450 | 156 | pairs per 100 cycles | 0.55 | — | 65.5 % | **-0.315** |

Three properties decide it, and they are the three the owner named as the questions to ask before Stage B:

1. **Slope is not estimable from a record that may still be running.** Its rank correlation across the 240
   records falls from the full 600-cycle fit to the 450-cycle fit at **-0.315**: the ordering of worlds by rate
   *reverses* when the observation window shortens. A rate fitted over a support that is still growing is a
   function of where you stopped, and this record stops mid-transition (§4). Slope is retained as exploratory
   and is currently unusable; it becomes usable only when a run contains the end of the transition, which is
   exactly what Stage B would have to supply.
2. **Exposure is defined for every record, and depends on the integration interval by construction.** Its
   ranking is fairly stable under truncation (0.925) and it is the natural "dose" reading — how much structure
   had accumulated by the time learning begins. But its value is defined *relative to an interval*, and the
   interval's length is the one design parameter this project has not been able to fix. Keeping it as the
   primary would build the unresolved question into the predictor.
3. **Onset is measured once, at a cycle, and cannot be undone by extending the run.** An event already observed
   does not move when the run continues, so onset is the only candidate whose value is invariant to the run
   length that Stage A found to be the sticking point. It varies within a configuration by far more than its
   own resolution: SD 12.4 cycles over a range of 65 in `6:1`, on a grid of one cycle.

**Primary: onset.** Not because it relates best to behaviour — nothing here has been related to behaviour — but
because it is the only candidate that survives the two things this record has already shown to be broken: the
absent settled state, and the undetermined run length.

**The redundancy is measured, not hidden.** Among the 119 moving runs, onset and exposure rank-correlate at
**-0.932** across configurations: earlier emergence and greater accumulated stock are nearly the same ordering.
So choosing onset does not discard the dose information — it chooses the *measurable* of two nearly equivalent
orderings, and it leaves exposure available as a co-reported exploratory quantity whose interval must be declared
in advance.

---

## 3. Onset: definition, scope and limits

**Definition.** Onset is the first cycle from which **10 consecutive** cycles report a non-zero `DI`. The
constant (10), the arrival cycle (150) and the record length are declared in the artifact. A single-cycle
non-zero reading does not constitute onset, which is why the four one-cycle arrival blips in the `1:x` arms do
not produce one.

| configuration | runs with an onset | median onset | SD | range | exposure, mean ± SD (pairs) |
| --- | --- | --- | --- | --- | --- |
| `6:1` | 30 | 329 | 12.4 | 289–354 | 6.45 ± 0.44 |
| `4:1` | 30 | 362 | 19.3 | 310–391 | 5.29 ± 0.40 |
| `3:1` | 30 | 404 | 25.1 | 342–445 | 3.65 ± 0.57 |
| `2:1` | 29 | 539 | 27.3 | 475–589 | 0.31 ± 0.25 |
| `1:1`–`1:4` | 0 | — | — | — | 0.00 ± 0.00 |

**Scope.** Onset is defined in the four configurations where the late structure is expressed at all — 119 of
their 120 runs. In `1:1`–`1:4` it is not undefined because data is missing; it is undefined because the
manipulated quantity produces no sustained `DI` in those worlds, which is the project's AGENTS 13a condition in
its exact form. Those four configurations are **out of scope for this construct**, and a run of them is a
statement about the world, not a null result about the organism.

**Limits, stated before any use:**

1. **The sustention rule is part of the measure.** Ten cycles is a declared constant, not a natural boundary;
   changing it shifts every onset. Stage B must freeze it, report it beside every onset value, and treat a
   world whose onset sits on the rule's boundary as unresolved rather than as a precise number.
2. **Onset is a timing, so it is confounded with the pace of the arm.** It can only be interpreted *within* a
   configuration, where the pace is held fixed. A pooled relation between onset and behaviour would restate the
   fact that the arms differ, which is why §5's fourth falsifier exists.
3. **Onset says nothing about how much structure is present.** A world can emerge early and plateau low. That
   is exposure's question, and it is why exposure is retained as exploratory rather than dropped.
4. **The within-configuration share of variance is 7.1 %** — the remaining 92.9 % is between configurations. That
   is not disqualifying for a within-configuration test: the arm is held constant by design, and the within-arm
   spread is 65 cycles wide. It does mean that no pooled coefficient should ever be reported as the finding.

---

## 4. Settling, separated into the three criteria it had been conflating

The project had been using a single statistic — "the last cycle at which the run's value differs from its own
final value by a whole pair" — and reading it as evidence that the state had settled. Those are three different
criteria, and only the third speaks to whether the trajectory would keep moving. Among the 119 runs with a
sustained onset:

| criterion | statistic | result |
| --- | --- | --- |
| (a) entry into a one-pair band around the final value | median entry cycle | **587** of 600 (max 599) |
| (b) remaining in that band for a stated duration | median persistence | **13 cycles**; 37 runs ≥ 30, 17 ≥ 50, **4 ≥ 100** |
| (c) no meaningful remaining trend | change over the last 100 cycles | median **2.0 pairs**, range -4.0 to +9.0; **23** runs below half a pair, **96** at two pairs or more |

**Nothing in this record is a settled state.** Criterion (a) is retrospective — it uses the run's own final
value, which is simply where the observation stopped — and its median of 13 cycles of persistence is a quiet
patch, not a plateau. Criterion (c) is the one that could support an asymptote claim, and it fails for 96 of the
119 runs: they moved by at least two pairs over the final 100 cycles, and none moved by a quantity between half
a pair and two pairs. Only **4 of 119** runs satisfy (b) at 50 cycles and (c) together.

**Consequences, applied:**

- No asymptote is claimed for this record. The word **asymptote** is retired from the design documents. A
  future run may claim one only if (b) and (c) are both declared before it runs and both met afterwards, with
  their parameters stated.
- A stopping criterion is now a **pair** of conditions — persistence in a one-pair band over a stated number of
  cycles, and no remaining trend over a stated span — not a single last-change cycle.
- The Stage A figure of **586** and this record's **587** measure the same statistic on different populations:
  586 pools all 123 runs that ever move, including the four one-cycle arrival blips; 587 uses the 119 runs with
  a sustained onset. The difference is one cycle, and it changes none of the conclusions above.

---

## 5. What the construct claims, and what would falsify it

**Claim, in the form Stage B would test:** *within a generating configuration, worlds whose internal structure
emerges earlier behave differently afterwards from worlds whose structure emerges later — in the direction that
structure available earlier supports later revision.*

Pre-committed falsifiers, written before any behavioural endpoint is read:

1. **Absence.** A within-configuration interval for the relation that contains zero → the construct is not
   supported. It is not "weakly supported", and it is not rescued by the pooled relation.
2. **Reversal.** A relation of the opposite sign → recorded as reversed, which is a stronger statement than
   unsupported and must be reported as such.
3. **Dead configuration.** A configuration in which onset is undefined in most runs → out of scope for the
   construct, reported as a world property, never as a null.
4. **Pooled only.** A relation that appears across configurations but not inside one → the construct is not
   supported for the protocol's question, because the protocol's question is within a configuration.

---

## 6. The temporal boundary

The ordering the owner required — structural measurement, then held-out behavioural observation — is preserved
by construction here, and the boundary is stricter than a window's:

- Onset is a **cycle index**, and its sustention rule means the measurement is not complete until 10 cycles
  after it. So the run must extend at least 10 cycles past onset, then the protocol's 50-cycle learning and
  50-cycle test — the same ordering as before, with the measurement point set by the organism rather than by a
  constant.
- **No behavioural cycle may contribute to onset.** Onset is derived from the structural trajectory up to its
  own event; the behavioural limb begins afterwards and its test set is withheld.
- If exposure is co-reported, its integration interval **must be declared in advance and must end before
  learning begins.** An interval chosen after seeing the behaviour would make the dose a function of the
  outcome.
- The late-pair overlap measured for the settled-state window is not the binding overlap for onset — onset is
  not computed from a pair set — but any pair contributing to *any* predictor in the run must be withheld from
  the behavioural test set, and that requirement is unchanged.

---

## 7. Stage B: what validating this construct would require, and why it is not authorised

Fresh methodology worlds from the frozen engine, on seeds disjoint from every Phase L seed and from every
confirmatory block; the sustention rule, the stopping criterion and the integration interval declared before any
world is generated; the relation estimated **within** configuration with the predictor's spread reported beside
it.

The four Stage B criteria carry over, with the resolution criterion restated for a cycle-valued predictor:

1. **Non-degenerate.** Onset is defined in at least 90 % of the runs of each configuration the construct claims.
2. **Resolution.** Within-configuration SD of onset is at least 3 cycles, so the ordering is not being set by
   the sustention rule's own boundary.
3. **Consistency.** The stopping criterion of §4 — persistence plus no remaining trend — is met in every
   configuration claimed, with its parameters declared in advance.
4. **Ordering.** Onset and the sustention window complete strictly before revision learning begins, and no
   behavioural cycle contributes to any predictor.

**Failure rule unchanged:** if any criterion fails, the construct is rejected and no confirmatory seed is
allocated. A rejection is the design's result and is not renegotiated into a smaller claim.

**Cost.** Stage B spends methodology seeds, so it is **not authorised here**: no seed is allocated, no world is
generated, and the owner decides whether and when to run it. Nothing in this document commits the project to it.

---

## 8. What is preserved

- The 240 Phase L records, untouched: same file, same seeds, same values.
- The protocol's window (110–150), still written and still flagged as contested and unresolved.
- The construct audit's verdict on `DI` as a state at a designated time, untouched. This record adds a second
  construct beside it rather than reinterpreting it.
- V1 and its results, untouched. The sample-size discussion remains paused, and the attenuation curve will need
  re-deriving for whatever predictor is finally validated.

---

## 9. Verification

```bash
./.venv/bin/python -m benchmarks.di_transition_construct        # writes docs/di_transition_construct.json
./.venv/bin/python -m pytest tests/test_di_transition_construct.py -q
```

The test recomputes the artifact, asserts every number quoted here against it, asserts that onset is the named
primary with exposure and slope labelled exploratory, and asserts that the artifact records no behavioural
correlation — the guarantee that the construct was not chosen on an outcome.
