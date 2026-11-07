study: decay factor sweep
executions: 0
seeds: 20302501, 20302502, 20302503
arms: 0.985, 0.99, 0.9925, 0.995, 0.9975, 0.999, 1.0
world: lattice_L1
arm: FULL
artifact: docs/decay_sweep.json
question: Q048

# Is survival a smooth function of the decay factor? — pre-registration

**Written before the run.** The machine-readable block above and sections 1–11 are the protocol;
section 12 is the outcome and is appended after the measurement. The runner records the SHA-256 of
sections 1–11 in its artifact, and the guard pins the same digest, so a later edit cannot pass as
the protocol that was committed.

## 1. The question, and why it is the next one

Q047 measured three decay points on the falsifier's `lattice_L1` world: shipped **0.95** dies at
cycle **39**, `factor099` dies at **228**, and `no_decay` **1.0** is still alive at cycle **300**.
Q046 had already shown that 0.95 to 0.99 moves all six force-matrix arms by exactly the same 189
cycles, so the shared decay layer is the lever.

Those three points do not establish the shape of the curve. Two interior points can describe a
smooth gradient, a threshold, or a step. The user's proposal is to sweep **0.985–0.999**, plot
survival against the factor, and use 1.0 as the ceiling control. This study does exactly that; it
does not assume that 1.0 is desirable.

The figures **42** and **30** quoted for 1.0 in the design discussion are the degree-12 hub's no-decay
arm in `docs/decay_attribution.json`, not `lattice_L1`. Q047's `lattice_L1` `no_decay` arm has a
stable-edge peak of **21** and never reaches stable-edge zero. The two worlds are not interchangeable,
and this protocol uses `lattice_L1` only.

**Q048.** Between 0.985 and 1.0, is the theory-death cycle a smooth function of the temporal decay
factor, a threshold, or a flat range; and what is the smallest factor in the range that keeps the
theory layer alive at cycle 300?

The outcomes license different decisions. A **step** says the operating point is a threshold; the
next study tests adaptation at the lowest surviving factor and at the factor immediately below it. A
**smooth** curve says a gradient exists; the lowest surviving factor is a candidate operating point
and earns a capability and adaptation study, not adoption. **Only 1.0 surviving** says the interior
of this range is empty and the next sweep must go lower. **No effect in range** says the range is
above the active region and must move downward. A **non-monotone** result says the seed or world
interaction dominates and no point should be chosen from this run.

## 2. The world and the setting

The falsifier's `lattice_L1` world, unchanged: three disjoint triangles, **300** cycles, the reference
arm **FULL**, the matrix's bootstrap and per-cycle feed, and the same cap of **40** predictions. The
shipped decay factor is **0.95** and the admission threshold is `PREDICTION_MIN_COUNT = 5`. No floor,
recency exemption, admission change or candidate decay is applied.

The only manipulated quantity is `MemoryService.decay_temporal_edges`'s `factor`. The memory subclass
forces the factor for the duration of the cell, records every call's factor, row count and temporal
mass before and after, and restores the engine on close. The engine files are not edited.

## 3. The factors

| Factor | Role | Why it is in the sweep |
| --- | --- | --- |
| 0.985 | lower interior | the lowest factor the design discussion proposed |
| 0.99 | anchor | must reproduce Q047's 228 on the fresh block |
| 0.9925 | interior | halfway between the anchor and 0.995 |
| 0.995 | interior | the first candidate the user named as a usable point |
| 0.9975 | interior | halfway between 0.995 and 0.999 |
| 0.999 | interior | the highest factor below no decay |
| 1.0 | ceiling control | no temporal erosion; the upper bound, not an adoption candidate |

The factors are applied in-process to the same world and seed block. Counts are integers, so the
rounding fixed point differs by factor: at 0.985 every count up to about 67 is unchanged; at 0.99 it
is about 50; at 0.995 it is about 200; at 0.999 it is about 1,000. The sweep therefore tests whether
the theory layer's lifetime tracks those fixed points continuously or jumps between them.

## 4. The instrument

`benchmarks/decay_sweep.py`, one run, one artifact, in-process against the pinned engine. The
death-ledger observer records theories, retained beliefs and every theory removal by mechanism each
cycle, exactly as Q042, Q046 and Q047 recorded them. The memory subclass records every decay call's
factor, row count and temporal mass.

The **primary endpoint** is the theory death cycle: one past the last cycle with at least one theory,
or **301** if the layer is alive at cycle 300. This is the falsifier's, Q046's and Q047's definition,
kept unchanged so the cells are comparable.

The **secondary endpoint** is stable-edge zero: the stored prediction candidates with strength at or
above `STABLE_THRESHOLD`; the zero cycle is the first cycle after the peak with no stable edge, or
**301** if the stable set never empties. Peak stable edges and final stable edges are reported beside
it. Stable-edge presence is not prediction quality.

A cell that cannot record its own perturbation is not a null. G3 is the liveness gate, and a failed
G3 is `VOID_INSTRUMENT`, not a zero.

## 5. Seeds

**20302501, 20302502 and 20302503**, three consecutive fresh seeds, checked against every seed under
`docs/` at freeze time and found unused. The runner refuses to start if any judged seed appears in an
artifact outside its own record.

The neutrality control uses **20261023**, the falsifier's seed, at the shipped factor 0.95, and is
not a judged cell. It must reproduce the committed `lattice_L1` reference theories and beliefs
exactly, cycle for cycle.

## 6. The endpoint, the step and the smallest survivor

**Primary.** The death cycle is reported per factor and per seed. **Survival** means death cycle
**301**: the theory layer was still live at cycle 300. The survival fraction is the number of judged
seeds alive at 300, out of three.

**Smallest survivor.** The smallest factor in the sweep whose three judged seeds all survive to 301.
If no factor below 1.0 survives, the answer is **none in range**, and 1.0 remains a ceiling control.

**Step size.** The largest absolute difference between adjacent factors' median death cycles. A step
of at least **50 cycles** is the pre-committed threshold for a step rather than a smooth gradient.
The threshold is fixed here, before the run, and is not computed from the curve it judges.

**Secondary.** Stable-edge zero, peak stable edges, final stable edges, peak theory count and the
parent-loss share of theory removals.

## 7. Gates

- **G1, the neutral observer.** Shipped 0.95 at control seed 20261023 reproduces the committed
  falsifier reference theories and beliefs exactly, cycle for cycle.
- **G2, the anchor.** The 0.99 cell dies at cycle 228 in all three judged seeds, reproducing Q047's
  `factor099` cells. A different anchor means the fresh block or the instrument is not the committed
  one, and the sweep is not interpretable against Q047.
- **G3, the factor fires.** Every cell records its own factor on every decay call, makes 300 calls,
  and updates at least one row on every cycle when the factor is below 1.0; at 1.0 the temporal mass
  is unchanged across every call.
- **G4, the denominator exists.** Every cell has 300 cycles and at least one cycle with a live theory
  layer.
- **G5, the seeds are fresh.** No judged seed appears under `docs/` outside this protocol.

G1, G3, G4 or G5 failing makes the run `VOID_INSTRUMENT`: no verdict. G2 failing makes the run
`ANCHOR_NOT_REPRODUCED`: no factor may be compared to Q047.

## 8. Pre-committed predictions

These are predictions, not descriptions; each can fail.

| Prediction | Condition |
| --- | --- |
| P1 | 0.99 dies at 228 in all three judged seeds |
| P2 | median death is non-decreasing as the factor rises from 0.985 to 1.0 |
| P3 | 0.985 dies before 0.99 |
| P4 | 1.0 survives to 301 in all three judged seeds |
| P5 | at least one adjacent pair differs by 50 or more cycles, so the range is not a smooth ramp |
| P6 | stable-edge zero is non-decreasing as the factor rises |
| P7 | at least one factor below 1.0 survives to 301 |

P5 is the user's continuity question stated as a falsifiable claim: if every adjacent gain is below
50 cycles, the curve is a gradient on this range and P5 fails. P7 is the engineering question: if it
fails, the interior is empty and 1.0 is the only survivor in range.

## 9. Decision table

Committed before the run. Exactly one label is applied. A void takes precedence over every other
bucket.

| Label | Condition | Decision |
| --- | --- | --- |
| `VOID_INSTRUMENT` | G1, G3, G4 or G5 fails | no verdict; repair the instrument first and keep Q048 open |
| `ANCHOR_NOT_REPRODUCED` | G2 fails | do not compare any factor to Q047; fix the fresh block or the instrument |
| `NON_MONOTONE` | a higher factor has a lower median death than a lower one | seed or world interaction dominates; do not choose a point from this run |
| `ONLY_1_0_SURVIVES` | no factor below 1.0 survives to 301 | the interior of 0.985–0.999 is empty; the next sweep must go lower, and 1.0 remains a ceiling control |
| `NO_EFFECT_IN_RANGE` | every factor has the same median death | the range is above or below the active region; move the sweep, do not report a null |
| `STEP` | death is monotone and the largest adjacent step is at least 50 cycles | the operating point is a threshold; test adaptation at the lowest survivor and at the factor immediately below it |
| `SMOOTH` | death is monotone, at least two distinct values, and every adjacent step is below 50 cycles | a gradient exists; the lowest survivor is an operating-point candidate and earns a capability and adaptation study, not adoption |

## 10. What this cannot establish

- One world, one degree, one arm and three seeds. Three seeds test seed sensitivity, not new worlds
  or new degrees.
- The sweep is one narrow band, 0.985–1.0. It does not locate a threshold below 0.985.
- The factor is one decay path. Admission, candidate decay, formation and the theory cap are
  unchanged, so a result cannot be attributed to them.
- Survival is theory-layer presence, not theory identity. A layer that replaces its theories every
  cycle counts as live.
- Stable-edge presence is not prediction quality, and this protocol scores no held-out prediction,
  revision or adaptation task.
- The 1.0 arm is an upper bound. Survival at 1.0 does not establish that forgetting is unnecessary,
  and this protocol cannot test stale knowledge or adaptation.
- The 42 and 30 figures from the degree-12 hub are not evidence for this world and are not used.
- No capability or adoption claim follows. A viable factor earns a separate capability and
  adaptation study and an owner decision.

## 11. Stop condition and freeze

The study is closed when the artifact exists, the page with the plot is generated from it, one label
from section 9 is recorded with its conditions, and every gate is reported. No instrumentation may
be added afterwards; a new question gets a new protocol. A correction is a dated amendment appended
after section 12, never an edit in place.

## 12. Outcome

**Not yet written.** No cell has run.
