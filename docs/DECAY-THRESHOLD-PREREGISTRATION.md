study: decay threshold refinement
executions: 1
seeds: 20302701, 20302702, 20302703
candidates: 24
screen_seed: 20302701
world: lattice_L1
arm: FULL
artifact: docs/decay_threshold.json
question: Q050

# Where exactly is the decay threshold? — pre-registration

**Written before the run.** The machine-readable block above and sections 1–11 are the protocol;
section 12 is the outcome and is appended after the measurement. The runner records the SHA-256 of
sections 1–11 in its artifact, and the guard pins the same digest, so a later edit cannot pass as
the protocol that was committed.

## 1. The question, and why it is the next one

Q048 measured seven factors and found a step: 0.99 dies at cycle **228**, 0.9925 survives to
**301**, and every tested factor above 0.9925 also survives. That leaves a **0.0025-wide gap**
between the last tested death and the first tested survival. The gap contains **24 four-decimal
factors**: 0.9901 through 0.9924. The smallest surviving factor may be one of them, not 0.9925.

**Q050.** Within 0.9901–0.9924, which is the smallest four-decimal factor whose theory layer is
still alive at cycle 300 on `lattice_L1`, and is that boundary confirmed on three seeds?

The answer changes the operating point. If the boundary is near 0.9901, the threshold is much
lower than Q048's first tested survivor and the next adaptation test should move down. If it is
near 0.9924, 0.9925 is effectively the edge and the gap is a plateau. If no interior factor
survives, the threshold is between 0.9924 and 0.9925. A non-monotone screen means no point can be
chosen from this range without a different design.

## 2. The world and the setting

The falsifier's `lattice_L1` world, unchanged: three disjoint triangles, **300** cycles, reference
arm **FULL**, the matrix's bootstrap and per-cycle feed, and the cap of **40** predictions. The
shipped decay floor is **1**; the admission threshold is `PREDICTION_MIN_COUNT = 5`. No floor,
recency exemption, admission change or candidate decay is applied.

The only manipulated quantity is the temporal decay factor. The runner reuses Q048's in-process
memory subclass: the engine files are not edited, and every cell records its forced factor, row
count and temporal mass on every decay call.

## 3. The candidates

The **24 four-decimal factors** strictly between the tested endpoints:

| Range | Values |
| --- | --- |
| lower half | 0.9901, 0.9902, 0.9903, 0.9904, 0.9905, 0.9906, 0.9907, 0.9908, 0.9909, 0.9910, 0.9911, 0.9912 |
| upper half | 0.9913, 0.9914, 0.9915, 0.9916, 0.9917, 0.9918, 0.9919, 0.9920, 0.9921, 0.9922, 0.9923, 0.9924 |

The endpoints **0.99** (death 228) and **0.9925** (alive at 300) are Q048 results and are not
re-measured as candidates. If the screen finds a boundary at 0.9901 or 0.9924, the endpoint is the
neighbour used for confirmation.

## 4. The instrument

`benchmarks/decay_threshold.py`, one artifact, in-process against the pinned engine. The death
ledger's observer records theories, retained beliefs and every theory removal by mechanism each
cycle, exactly as Q042, Q046, Q047 and Q048 recorded them.

**Screen.** Every one of the 24 candidates runs on the screen seed **20302701**, 300 cycles. The
screen is an enumeration, not a verdict: it identifies the lowest candidate alive at 300 and the
highest candidate below it that is dead. A screen that is not monotone is reported as
`NON_MONOTONE`; no boundary is claimed from it.

**Confirmation.** The lowest alive candidate and its immediate four-decimal neighbours are rerun on
**20302701, 20302702 and 20302703**. The claim is the confirmed boundary, not the screen reading.
The screen's own cell is reused as the first confirmation seed.

The **primary endpoint** is the theory death cycle: one past the last cycle with at least one
theory, or **301** if the layer is alive at cycle 300. The **secondary endpoint** is stable-edge
zero, using the attribution harness's own stable-threshold definition.

## 5. Seeds

**20302701, 20302702 and 20302703**, three consecutive fresh seeds, checked against every seed
under `docs/` at freeze time and found unused. The screen uses 20302701; confirmation uses all
three. The runner refuses to start if any judged seed appears in an artifact outside its own
record.

## 6. The endpoint and the boundary

The **screen boundary** is the lowest candidate whose screen death cycle is **301**. If no
candidate is alive, the outcome is `NO_INTERIOR_SURVIVOR`; if all are alive, `BELOW_SCREEN`; if the
screen death cycles are not non-decreasing with the factor, `NON_MONOTONE`.

The **confirmed boundary** requires, on all three confirmation seeds:

- the candidate itself dies at **301**;
- the immediate lower neighbour dies before **301**;
- the immediate upper neighbour dies at **301**.

If all three hold, the candidate is the smallest confirmed survivor. If any fails, the outcome is
`CONFIRMATION_FAILED` and no boundary is claimed.

The resolution is **0.0001**. The protocol does not claim a boundary between four-decimal factors.

## 7. Gates

- **G1, the screen factor fires.** Every screen cell records its own factor on all 300 decay calls
  and updates rows on every call.
- **G2, the confirmation factor fires.** Every confirmation cell records its own factor on all 300
  calls and updates rows.
- **G3, the denominator exists.** Every screen and confirmation cell has 300 cycles and at least one
  cycle with a live theory layer.
- **G4, the seeds are fresh.** No judged seed appears under `docs/` outside this protocol.
- **G5, the screen is complete.** All 24 candidates have a 300-cycle screen cell.
- **G6, the confirmation is complete.** When a boundary is confirmed, all three factors have all
  three seed cells.

G1, G2, G3, G4, G5 or G6 failing makes the run `VOID_INSTRUMENT`: no verdict.

## 8. Pre-committed predictions

These are predictions, not descriptions; each can fail.

| Prediction | Condition |
| --- | --- |
| P1 | the screen death cycle is non-decreasing from 0.9901 to 0.9924 |
| P2 | at least one interior candidate survives to 301 |
| P3 | the smallest surviving candidate is below 0.9925 |
| P4 | the confirmed boundary survives to 301 on all three seeds |
| P5 | the confirmed lower neighbour dies before 301 on all three seeds |
| P6 | the confirmed upper neighbour survives to 301 on all three seeds |

P1 is the monotonicity assumption behind a threshold, tested rather than assumed. P3 is the user's
point: 0.9925 may not be the smallest survivor.

## 9. Decision table

Committed before the run. Exactly one label is applied. A void takes precedence over every other
bucket.

| Label | Condition | Decision |
| --- | --- | --- |
| `VOID_INSTRUMENT` | any gate fails | no verdict; repair the instrument first and keep Q050 open |
| `NON_MONOTONE` | the screen death cycle decreases at any step | no threshold claim; the range needs a different design |
| `NO_INTERIOR_SURVIVOR` | every screen candidate dies before 301 | the threshold is between 0.9924 and 0.9925; 0.9925 remains the first tested survivor |
| `BELOW_SCREEN` | every screen candidate survives to 301 | the threshold is at or below 0.9901; the next sweep goes below 0.99 |
| `CONFIRMATION_FAILED` | the screen boundary or a neighbour does not behave on three seeds | no boundary claim; the screen boundary is seed-sensitive and needs a larger block |
| `THRESHOLD_FOUND` | the boundary and both neighbours behave as required on three seeds | that candidate is the smallest confirmed survivor at 0.0001 resolution; the adaptation and capability tests move to it |

## 10. What this cannot establish

- One world, one degree, one arm and three seeds. The screen is one seed; the confirmation is three.
- The resolution is 0.0001. The boundary may lie between two candidates.
- Survival is theory-layer presence, not theory identity. A layer that replaces its theories every
  cycle counts as live.
- Stable-edge presence is not prediction quality. No held-out prediction, revision or adaptation
  task is scored.
- The endpoints 0.99 and 0.9925 are Q048 results measured on a different seed block, not fresh
  cells here.
- No capability or adoption claim follows; a lower boundary earns the same adaptation and capability
  tests as 0.9925.

## 11. Stop condition and freeze

The study is closed when the artifact exists, the page is generated from it, one label from section
9 is recorded with its conditions, and every gate is reported. No instrumentation may be added
afterwards; a new question gets a new protocol. A correction is a dated amendment appended after
section 12, never an edit in place.

## 12. Outcome

**`NO_INTERIOR_SURVIVOR`.** All 24 candidates were screened on seed 20302701. The death cycle rises
monotonically from **231** at 0.9901 to **300** at 0.9923 and 0.9924; no candidate reaches **301**.
Because no interior candidate survived, the pre-registered confirmation step did not fire: there
is no boundary to confirm. At 0.0001 resolution the threshold lies between **0.9924 and 0.9925**;
0.9925 remains Q048's first confirmed survivor on three seeds, while the 0.9924 cell is one screen
seed.

All six gates passed. P1 held; P2 (an interior survivor), P3 (a survivor below 0.9925), and P4-P6
(confirmation predictions) failed. The negative is a screen-level result: 0.9924 dies at 300 on
seed 20302701, one cycle before survival, and no three-seed confirmation was pre-registered for the
no-survivor branch.


## 13. Post-screen edge check (2026-11-07)

**Requested after Q050's outcome; written before the two edge cells ran.** Q050's no-survivor
branch did not pre-register confirmation. This amendment tests only whether the 0.9924 screen
death is seed-stable. It does not change the Q050 label and it is not a new threshold.

**Check.** Rerun 0.9924 on seeds **20302702** and **20302703** (20302701 is the existing screen
cell), 300 cycles, same `lattice_L1` world, arm and runner. A seed is `DEAD` if its theory death
cycle is at most 300; it is `ALIVE` if the death cycle is 301.

**Decision.** `EDGE_CONFIRMED` if all three seeds are dead; `EDGE_NOT_CONFIRMED` if any seed is
alive at 301; `VOID` if the factor or denominator gates fail.

**Prediction.** All three seeds are dead, matching the screen. This is a robustness check, not a
new threshold, and Q050 remains `NO_INTERIOR_SURVIVOR`.

**Outcome.** **`EDGE_CONFIRMED`.** Seed 20302701 dies at 300 (screen cell), 20302702 at 300, and
20302703 at 300; all three seeds are dead. The prediction held. Q050 remains
`NO_INTERIOR_SURVIVOR`; this check hardens the 0.9924 edge but does not turn it into a new
threshold claim.

