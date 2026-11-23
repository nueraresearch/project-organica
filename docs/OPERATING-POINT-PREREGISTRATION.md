study: operating point between shipped decay and no decay
executions: 1
seeds: 20302401, 20302402, 20302403
arms: shipped, floor2, floor5, factor099, recency, no_decay
world: lattice_L1
arm: FULL
artifact: docs/operating_point.json
question: Q047

# Is there a viable decay operating point? — pre-registration

**Written before the run.** The machine-readable block above and sections 1–11 are the protocol;
section 12 is the outcome and is appended after the measurement. The runner records the SHA-256 of
sections 1–11 in its artifact, and the guard pins the same digest, so a later edit cannot pass as
the protocol that was committed.

## 1. The question, and why it is the next one

Q046 applied one uniform change to the temporal-decay layer, 0.95 to 0.99, across all six force-matrix
arms on the falsifier's `lattice_L1` world. Every shipped cell died at cycle **39**; every repaired
cell died at cycle **228**; every arm and seed gained exactly **189** cycles. That settled the causal
question at one interior point: the shared timing is not a retention-policy artifact, and the shared
decay layer can move it.

It did not settle the operating-point question. Q046 tested only **0.95** and **0.99**, and 0.99 still
dies at 228, before the 300-cycle horizon. The claim that decay 1.0 survives is **not established on
this world**: the only committed no-decay artifact is the degree-12 hub in
`docs/decay_attribution.json`, where the control peaked at **42**, ended at **30**, and never reached
zero. That is a different world, a different degree and a different stimulus. On `lattice_L1`, 1.0 is
unmeasured. This study measures it as an upper bound; it does not assume survival.

Q045 remains open and unrun. It asks whether the readout lever — prediction budget and ranking —
extends persistence on the degree-12 hub. This is a different lever on a different world and does not
supersede Q045.

**Q047.** Between shipped decay 0.95 and no decay 1.0, is there an operating point that materially
delays the cycle-39 theory death on `lattice_L1`, and which mechanism accounts for it?

The candidate mechanisms are separable:

- **slower global erosion** (`factor099`): raise the decay factor so high-count edges settle at a
  higher equilibrium;
- **an eligibility floor** (`floor5`): stop low-count edges from sitting below the admission threshold;
- **conditional forgetting** (`recency`): let an edge that was reinforced this cycle keep its count
  through this cycle's decay;
- **no forgetting** (`no_decay`): factor 1.0, the upper bound.

The outcomes license different decisions. A viable interior arm is a persistence candidate and earns
a capability study, not adoption. Only 1.0 surviving says the interior is empty on this world and the
next test is a finer factor sweep or a formation change, not an engine revision. Only `floor5`
surviving says the lever is eligibility, not erosion, and the arm must be described as such. A null
across every interior arm says this world has no usable operating point among the tested mechanisms.

## 2. The world and the setting

The falsifier's `lattice_L1` world, unchanged: three disjoint triangles, **300** cycles, the reference
arm **FULL**, the matrix's bootstrap and per-cycle feed, and the same cap of **40** predictions. The
shipped decay factor is **0.95**, the shipped decay floor is **1**, and the admission threshold is
`PREDICTION_MIN_COUNT = 5`.

The implementation detail that governs every arm is recorded here because it is load-bearing.
`MemoryService.decay_temporal_edges` applies

    count = MAX(min_count, CAST(ROUND(count * factor) AS INTEGER))

to every temporal edge once per sleep cycle. Counts are integers, so rounding creates fixed points:

- at **0.95**, every count from 1 to 10 is unchanged, and counts above 10 fall by one per cycle until
  they reach 10;
- at **0.99**, every count from 1 to 50 is unchanged, and counts above 50 fall to 50;
- at **1.0**, every count is unchanged.

Two consequences are part of the protocol, not commentary.

**First, `floor5` is not a retention arm.** An edge already at or above 5 decays exactly as it does
under shipped; the floor never binds above 5. What the floor does is lift every edge with count 1–4
to **5**, so the `>= 5` admission gate stops filtering. The arm is therefore an **eligibility
expansion**, and any effect it has is attributable to the candidate pool, not to preserved strength.
It is named `floor5` for continuity with the design discussion, and the label and page must state
this mechanism.

**Second, `floor2` is a negative control, not a repair.** It lifts a count of 1 to 2 and changes
nothing else; 2 is still below the admission threshold of 5. It tests whether recording a floor at
all moves the result. A difference between `floor2` and `shipped` would be an instrument effect, not
an admission effect.

## 3. The arms

Six conditions, one world, one arm and one seed block. The five candidate conditions are the design's
five; `floor2` is the sixth cell and exists only as the negative control.

| Arm | Factor | Floor | Recency exemption | Mechanism | Prior |
| --- | --- | --- | --- | --- | --- |
| `shipped` | 0.95 | 1 | no | the shipped build | death 39, reproducing Q046 |
| `floor2` | 0.95 | 2 | no | lifts count 1 to 2; still below admission 5 | within 2 cycles of shipped |
| `floor5` | 0.95 | 5 | no | lifts every count 1–4 to 5; admission 5 stops filtering | above shipped, weakest repair |
| `factor099` | 0.99 | 1 | no | high-count erosion stops at 50 instead of 10 | above shipped, second strongest |
| `recency` | 0.95 | 1 | yes | an edge whose count rose during this cycle's ingest does not decay this cycle | above shipped, below 0.99 |
| `no_decay` | 1.0 | 1 | no | no temporal erosion | highest; survival measured, not assumed |

The `recency` exemption is observational and is defined from the engine's own state, not from
selection: before the cycle's events are stored, the temporal counts are snapshotted; after they are
stored, the edges whose counts increased are the edges observed or reinforced this cycle; those edges
are exempt from that cycle's decay. The definition has no reference to the candidate list, the
predictions or any downstream choice. Its perturbation metric is the number of exempted edges, and at
least one must be exempted in each judged seed for the arm to count as live.

All six conditions are applied in-process. The engine files are not edited and no class constant is
changed on disk; the memory subclass forces the factor, the floor or the exemption for the duration
of the cell.

## 4. The instrument

`benchmarks/operating_point.py`, one run, one artifact, in-process against the pinned engine. The
death-ledger observer records theories, retained beliefs and every theory removal by mechanism each
cycle, exactly as Q042 and Q046 recorded them. The memory subclass records every decay call's factor,
floor, row count, lifted edges and exempted edges.

The **primary endpoint** is the theory death cycle: one past the last cycle with at least one theory,
or **301** if the layer is alive at cycle 300. This is the falsifier's and Q046's definition, kept
unchanged so the cells are comparable.

The **secondary endpoint** is stable-edge zero: using the attribution harness's own definition, the
stored prediction candidates with strength at or above `STABLE_THRESHOLD`; the zero cycle is the
first cycle after the peak with no stable edge, or 301 if the stable set never empties. Peak stable
edges, final theories, peak theories and parent-loss removals are reported beside it.

A cell that cannot record its own perturbation is not a null. The liveness gate for each repair arm
is named in section 7, and a failed gate is reported as `NOT_LIVE` for that arm. The decision table
counts only live arms.

## 5. Seeds

**20302401, 20302402 and 20302403**, three consecutive fresh seeds, checked against every seed under
`docs/` at freeze time and found unused. The runner refuses to start if any judged seed appears in an
artifact outside its own record.

The neutrality control uses **20261023**, the falsifier's seed, and is not a judged cell. It must
reproduce the committed `lattice_L1` reference theories and beliefs exactly, cycle for cycle.

## 6. The endpoint and the margin

**Primary.** An arm is **viable** when its death cycle exceeds the same-seed shipped death cycle by at
least **10 cycles** on at least **2 of the 3** seeds. Ten cycles is reused unchanged from the reference
ledger and Q046; it is not rescaled to this world, so it is not computed from the run it judges. A
single seed cannot carry viability, and the median is reported beside the paired gains rather than
used alone.

**Survival** is reported separately: death cycle 301 means the theory layer was still live at cycle
300. Survival is not required for viability, and viability is not adoption.

**Secondary.** Stable-edge zero, peak stable edges, final theory count, peak theory count, and the
parent-loss share of theory removals. Stable-edge gains are not prediction quality.

## 7. Gates

- **G1, the neutral observer.** `shipped` at control seed 20261023 reproduces the committed falsifier
  reference theories and beliefs exactly, cycle for cycle.
- **G2, the baseline.** `shipped` dies at cycle 39 in all three judged seeds, reproducing Q046's
  shipped cells.
- **G3, the floor arms fire.** `floor2` and `floor5` record the forced floor on every decay call, and
  each lifts at least one edge in every judged seed. A floor that never binds is not a null.
- **G4, the factor arm fires.** `factor099` records factor 0.99 on every decay call and updates rows
  on every cycle.
- **G5, the recency arm fires.** `recency` exempts at least one edge on at least one cycle of every
  judged seed, and the exempted edge's count is restored after the decay call.
- **G6, the no-decay arm fires.** `no_decay` records factor 1.0 on every decay call and leaves the
  temporal count mass unchanged across every call.
- **G7, the denominator exists.** Every cell has 300 cycles and at least 10 cycles with a live theory
  layer.
- **G8, the seeds are fresh.** No judged seed appears under `docs/` outside this protocol.

G1, G2, G7 or G8 failing makes the run `VOID_INSTRUMENT` or `BASELINE_NOT_REPRODUCED`: no verdict.
G3–G6 failing is a named `NOT_LIVE` outcome for the arm it names, not a void and not a null.

## 8. Pre-committed predictions

These are predictions, not descriptions; each can fail.

| Prediction | Condition |
| --- | --- |
| P1 | `shipped` dies at cycle 39 in all three judged seeds |
| P2 | `no_decay` has the highest median death cycle of the six arms, whether or not it reaches 301 |
| P3 | `factor099` is viable and its median death is below `no_decay`'s |
| P4 | `recency` is viable and its median death is below `factor099`'s |
| P5 | `floor5` has a higher median death than `shipped` and a lower one than `recency` |
| P6 | `floor2` is within 2 cycles of `shipped` in every judged seed |
| P7 | the floor arms lift at least one edge in every seed and `recency` exempts at least one edge in every seed |
| P8 | the median ordering is `no_decay` at least `factor099` above `recency` above `floor5` above `floor2`, with `floor2` at or near `shipped` |
| P9 | `factor099` and `no_decay` reach stable-edge zero later than `shipped` in at least 2 of 3 seeds |

P5 is deliberately weaker than P3 and P4: the design's prior is that `floor5` is the weakest repair and
may not clear the viability margin. P6 is the negative-control prediction; a large `floor2` effect
would mean the floor's bookkeeping, not admission, moved the result.

## 9. Decision table

Committed before the run. Exactly one label is applied. A void takes precedence over every other
bucket; a not-live arm is reported and excluded from the viability count.

| Label | Condition | Decision |
| --- | --- | --- |
| `VOID_INSTRUMENT` | G1, G7 or G8 fails | no verdict; repair the instrument first and keep Q047 open |
| `BASELINE_NOT_REPRODUCED` | G2 fails | do not interpret any arm; the shipped baseline is not the committed one |
| `NO_REPAIR_ARM_LIVE` | every repair arm fails its liveness gate | the question is unrun, not null; fix the perturbations and do not report a null |
| `NO_OPERATING_POINT` | no live arm is viable, including `no_decay` | no tested mechanism buys the margin on this world; report the null and move to a finer factor sweep or a formation change |
| `NO_DECAY_ONLY` | only `no_decay` is viable among live arms | no tested interior point works; 1.0 is an upper bound, not an adoption candidate; the next test is a finer factor sweep or a formation change |
| `MONOTONE_LADDER` | P8 holds and `factor099`, `recency` and `floor5` are all viable | the predicted ladder is real; `factor099` is the first viable point and earns a capability study before any adoption |
| `PARTIAL_LADDER` | at least two repair arms are viable but P8 fails | a viable point exists, but the mechanism ranking is wrong; test the best arm's capability and record the failed ordering |
| `FACTOR_ONLY` | only `factor099` is viable among live interior arms | global slowing is the lever; test 0.99's capability effects before adoption |
| `FLOOR_ONLY` | only `floor5` is viable among live interior arms | eligibility, not erosion, is the lever; test `floor5`'s capability effects and state that the admission threshold became non-binding |
| `RECENCY_ONLY` | only `recency` is viable among live interior arms | conditional forgetting is the lever; test `recency`'s capability effects before adoption |

## 10. What this cannot establish

- One world, one degree, one arm and three seeds. Three seeds test seed sensitivity, not new worlds
  or new degrees.
- `factor099` is one interior point, not the curve. A null at 0.99 does not close 0.97 or 0.98, and a
  success at 0.99 does not locate the threshold.
- `floor5` makes the admission threshold non-binding. It is an eligibility intervention, not a
  retention intervention, and a result from it cannot be reported as preserved strength.
- `recency` exempts only edges whose counts rose in the current cycle. It does not test longer
  reinforcement windows or a recency-weighted decay rule.
- The endpoint is theory-layer presence, not theory identity. A layer that replaces its theories
  every cycle counts as live.
- No held-out prediction, revision or adaptation task is scored. A viable arm is a persistence
  result, not evidence of capability, and adoption requires a separate capability study and an owner
  decision.
- The no-decay arm is measured here for the first time on this world. The degree-12 hub's survival is
  not transferable evidence for `lattice_L1`.
- No formation, admission, candidate-decay or theory-cap change is made. The study varies the
  temporal decay path only.

## 11. Stop condition and freeze

The study is closed when the artifact exists, the page is generated from it, one label from section 9
is recorded with its conditions, and every gate is reported. No instrumentation may be added
afterwards; a new question gets a new protocol. A correction is a dated amendment appended after
section 12, never an edit in place.

Sections 1–11 are hashed and pinned in `benchmarks/operating_point_prereg.py`. A one-byte edit to the
frozen text fails the guard.

## 12. Outcome

**Measured 2026-11-07: `PARTIAL_LADDER`.** 18 cells (six conditions x seeds 20302401-20302403), 300
cycles each, reference arm FULL on the falsifier's `lattice_L1` world. Shipped, `floor2` and
`floor5` all died at cycle **39**; `factor099` died at **228**; `recency` died at **76**; `no_decay`
was alive at cycle **300** (death cycle 301). The artifact is `docs/operating_point.json`, the page
is `docs/OPERATING-POINT.md`, and the digest of sections 1-11 is
`3efa163f8aa90d48eaa675c5b4330e96f26f0f03285275e80b8513d5fb146463`.

- **The floor arms did not fire.** No temporal edge had a count below 5 before decay in any seed, so
  `floor2` and `floor5` lifted **0** edges. They are reported `NOT_LIVE`; the floor mechanism is
  **unrun** on this world, not a null.
- `factor099` reproduces Q046 (228; **+189**) and `recency` extends by **37** cycles; both clear the
  10-cycle margin on all three seeds. `no_decay` is the upper bound and survives to 301, the first
  measurement of 1.0 on this world.
- Gates G1, G2, G4, G5, G6, G7 and G8 passed; **G3 failed** because the floor arms lifted no edge.
- Predictions P1-P4, P6 and P9 held. P5 failed because `floor5` did not move; P7 failed only on the
  floor half (`recency` exempted 3,200 edges); P8 failed because `floor5` was not live. The label is
  `PARTIAL_LADDER`: a viable interior exists, but the predicted ordering could not be completed.
- **Decision.** `factor099` is the strongest tested interior point and `recency` is a second viable
  point; both are persistence candidates and neither is an adoption recommendation. The floor
  mechanism needs a world with sub-5 edges before it can be tested.
