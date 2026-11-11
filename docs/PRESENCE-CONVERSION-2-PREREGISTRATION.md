# PRESENCE-CONVERSION-2 — the repaired conversion observer, frozen

**Status: FROZEN, RUN. The campaign has run.** Frozen 2026-11-10; the record is
`docs/presence_conversion_repair_prereg.json` and this page is rendered from it. Authorisation: granted 2026-11-11.

## 1. Why this block exists

This block is Q4, frozen on its own and it does not wait for Q1, Q2 or Q3. It re-asks Q3's question with an instrument that returns the engine's own shipped-cap list untouched and records the pre-cap universe with a second call, because MAX_PREDICTIONS is a quota split rather than a truncation. It supersedes no verdict: Q3's OBSERVER NOT NEUTRAL stands and is not re-scored, and neither Q1's CONSTRUCT VALID nor Q2's CAP LIMITING is re-read by this block.

## 2. The question

Once the observer provably does not change what the engine admits, where do world edges leave the path between raw presence and final assertion on the compositional world family?

**Hypothesis.** With a behaviour-neutral observer the loss chain W -> P -> C -> S_cycle -> S_ever -> A_pred can be measured without the instrument contributing to it, and the dominant step can be named from the record rather than from a lifted-cap reconstruction.

**Prediction.** P equals W (presence is not the loss); C is at least P (every present edge is constructible above the prediction minimum), and the dominant loss sits between C and S_ever, at the admission step.

**Falsifier.** A stage table in which C < P for reasons other than the prediction minimum, or in which the dominant loss sits at S_ever -> A_pred, contradicts the prediction and is reported as it stands.

## 3. The repair

MAX_PREDICTIONS is a quota split, not a truncation: `half_cap = MAX_PREDICTIONS // 2` transitions are served first (ranked by schema prior, target entropy, transition probability, count), then `remaining_budget = MAX_PREDICTIONS - len(selected_transitions)` count-ranked cooccurrences, then leftovers are refilled with more transitions and the list is cut at the cap. Lifting the cap therefore changes which candidates are served, not only how many.

- served: the engine's own list from a call at the shipped cap, returned untouched
- observed: a second call at the diagnostic ceiling, recorded only and never served
- ceiling `1000000000`, shipped cap `40`.

## 4. Design

| | |
|---|---|
| Arms | off / on |
| Seeds | 20611601, 20611602, 20611603, 20611604, 20611605, 20611606 (bootstrap 20611607) |
| Cycles | 120 |
| Design cells | 12 |
| Witness cell | seed 20261100 |

## 5. Gates

**`N1_served_is_engine`** — for every seed and cycle the on arm's served window is identical, in order, to a plain SleepService run on the same world and cap; one difference is SERVED NOT ENGINE

**`N2_observation_cannot_leak`** — the observation is behaviour-neutral in the sense the project's rule 17(c) requires, in three parts: (a) the served window equals a plain engine run's, in order; (b) the next cycle's state is identical with and without the observation — same served window, same asserted set, same memory rows and counters; and (c) the pre-cap diagnostic universe is nevertheless available and complete enough to rank every served edge. Served equality alone is close to automatic under this construction; (b) and (c) are the claims that can fail. The check is built to fail and a test proves it fires

**`N3_allocation_recorded`** — every served row carries whether it is a transition or a cooccurrence, and every cycle records how many of each were served with the two counts summing to the window size; this is the split the previous record's rows did not preserve, which is why its diagnosis needed source inspection rather than its own artifact

**`N4_stage_complete`** — every present world edge is classified as constructed, below the prediction minimum, or unexplained; no unobserved edge is imputed and no denominator is zero

**`N5_witness_reproduces_audit`** — the observer-off witness cell reproduces the published audit row at cap 40: presence, asserted count and asserted fingerprint

**`N6_seed_axis`** — the six seeds and the bootstrap are fresh against every committed artifact, and W is identical across the two arms of each seed

**`N7_determinism`** — the first seed rerun in a fresh process reproduces the on arm's served fingerprints exactly

## 6. Decision table

| Condition | Verdict | Reading | Decision |
|---|---|---|---|
| N1 fails on any seed: the served window differs from a plain engine run | `SERVED NOT ENGINE` | the wiring is not what this record claims and nothing about conversion is measured | void the block; fix the wiring and register a new block, never re-read this one |
| N2 fails: mutating or disabling the observation changes the served window | `OBSERVATION LEAKS` | the double-call construction is not observation-only, so the pre-cap universe cannot be recorded without changing the engine | void the block; the repair route is closed and conversion needs a different instrument, never re-read this one |
| any other gate fails (N3-N7) | `VOID` | the record is incomplete or non-reproducible and no stage table is read | none; fix the harness and register a new block |
| all gates pass and A_pred < S_ever | `CONVERSION STAGE MEASURED` | the stage table locates the loss on these seeds; this is a measurement of the path, not a capability result | report the stage table; the next step is an owner decision on the named step, with no engine change implied |
| all gates pass and A_pred == S_ever | `CONVERSION STAGE MEASURED` | no world edge that was admitted was lost before assertion on these seeds, so conversion is closed as a loss route | close the conversion stage route and move the line to formation or to reach |

## 7. What this block does not license

This record is a protocol, not a result. It measures where world edges leave the conversion path on one world family; it does not measure intelligence, does not license a capability claim, and cannot re-score PRESENCE-CONVERSION-1's OBSERVER NOT NEUTRAL, which stands.

## 8. Stop condition

The block closes when the fourteen planned runs have produced their parts, N1-N7 have been scored once in the frozen order, and the verdict is recorded. No feature may be added afterwards; a defect is fixed and disclosed, never extended.

## 9. Runner

The harness is built at `benchmarks/presence_conversion_repair_runner.py`: twelve design cells, the cap-40 witness and the fresh-process rerun, plus six plain N1 references. The fourteen planned runs executed on 2026-11-11 and N1-N7 were scored once in the frozen order.
