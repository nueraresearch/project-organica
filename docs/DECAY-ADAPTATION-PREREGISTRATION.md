study: decay adaptation pilot
executions: 0
seeds: 20302601, 20302602, 20302603, 20302604, 20302605
arms: shipped, factor099, factor09925, no_decay
families: cause_mix, mapping_mix
cycles: 80
artifact: docs/decay_adaptation.json
question: Q049

# Does persistence cost adaptation? — pre-registration

**Written before the run.** The machine-readable block above and sections 1–11 are the protocol;
section 12 is the outcome and is appended after the measurement. The runner records the SHA-256 of
sections 1–11 in its artifact, and the guard pins the same digest, so a later edit cannot pass as
the protocol that was committed.

## 1. The question, and why it is the next one

Q048 found a threshold on `lattice_L1`: 0.985 dies at cycle **150**, 0.99 at **228**, and **0.9925**
through **1.0** survive the 300-cycle horizon. The smallest surviving factor is **0.9925**, not
1.0. Survival is not the same as adaptation: a system that never forgets may keep a stale mapping
after the world changes, and a system just above the persistence threshold may pay the same cost
more cheaply.

**Q049.** On the two gradual-shift families used by the Phase J adaptation campaign, do the
smallest surviving factor **0.9925** and the ceiling **1.0** have a higher final post-shift
prediction loss than shipped **0.95**, and is the cost larger at 1.0? The **0.99** arm is carried
descriptively as the point immediately below the threshold.

The outcomes license different decisions. A cost at 1.0 only says the ceiling is a persistence
control, not an operating point, and 0.9925 is the candidate. A cost at both says the threshold
buys persistence at an adaptation price and the trade must be priced before adoption. A cost at
0.9925 only says the threshold itself is the wrong point and the next test is between 0.99 and
0.9925. No detected cost says persistence did not buy adaptation loss on these families, not that
forgetting is unnecessary.

## 2. The worlds and the setting

The two Phase J gradual-transition families, reused unchanged from
`benchmarks/post_shift_adaptation.py`:

- `cause_mix`: the cause-to-outcome mapping shifts gradually from `causea` to `causeb`;
- `mapping_mix`: the context-to-outcome mapping permutes gradually.

Each world is **80** cycles, with the shift ramping over cycles **30–49** and the final rule in
force from cycle **50** onward. Each cycle has **8** trials. The protocol scores the shifted world
only; there is no stationary control, because the endpoint is the final post-shift loss rather than
a shifted-minus-stationary adaptation cost. Shifted and stationary pairings are a Phase J design,
not this pilot's.

The endpoint is the mean next-event negative log-likelihood over cycles **60–79**, using the
organism's own prediction candidates before the cycle's events are stored, exactly as Phase J
computes it. Lower is better. The loss is in nats per event.

## 3. The arms

| Arm | Decay factor | Mechanism |
| --- | --- | --- |
| `shipped` | 0.95 | the shipped decay path and the reference for every delta |
| `factor099` | 0.99 | the Q047 anchor, descriptive only |
| `factor09925` | 0.9925 | the smallest factor Q048 found alive at 300 |
| `no_decay` | 1.0 | no temporal erosion; the ceiling control |

All four arms are the unchanged engine with an in-process memory subclass that forces the factor.
No admission, formation, candidate-decay or theory-cap change is made.

## 4. The instrument

`benchmarks/decay_adaptation.py`, one run, one artifact, in-process against the pinned engine. For
each cycle the organism's current prediction candidates define a conditional distribution over the
world's tags; the cycle's events are scored before they are stored, so the score is a held-out
next-event loss rather than a fit to the events just ingested. The per-cycle losses are recorded;
the endpoint is the mean of cycles 60–79.

The memory subclass records every decay call's factor, row count and temporal mass before and
after. A cell that cannot record its own perturbation is not a null; G1 is the liveness gate and a
failed G1 is `VOID_INSTRUMENT`.

## 5. Seeds

**20302601, 20302602, 20302603, 20302604 and 20302605**, five consecutive fresh seeds, checked
against every seed under `docs/` at freeze time and found unused. Each seed is paired across the
four arms and the two families: 5 seeds × 2 families × 4 arms = **40** cells.

## 6. The endpoint, the delta and the margin

For each arm, family and seed, the final loss is the mean of cycles 60–79. The paired delta is

    delta(arm) = final_loss(arm) - final_loss(shipped)

on the same family and seed. Positive means the arm is worse after the shift; negative means it is
better.

The **pooled** delta is the mean of the ten paired deltas (5 seeds × 2 families), with a **97.5%**
paired percentile bootstrap interval over those ten values, 10,000 replicates, seed **20261023**.
The per-family deltas are reported beside it and are not used to rescue a pooled null.

**Cost** means the pooled delta is at least **0.05** nats per event and the interval's lower bound
is above zero. **Better** means the pooled delta is at most **-0.05** and the interval's upper bound
is below zero. Otherwise the arm is **no detected difference**. The 0.05 margin is fixed here,
before the run, and is not computed from the cells it judges.

## 7. Gates

- **G1, the factor fires.** Every cell records its own factor on all 80 decay calls; a factor below
  1.0 updates at least one row on every cycle, and 1.0 leaves the temporal mass unchanged on every
  call.
- **G2, the denominator exists.** Every cell has 80 cycles, 80 finite per-cycle losses, and at least
  one prediction distribution with a non-zero probability for each scored event.
- **G3, the seeds are fresh.** No judged seed appears under `docs/` outside this protocol.
- **G4, the design is complete.** All 40 cells exist: 4 arms × 2 families × 5 seeds, with every
  arm/family/seed cell present exactly once.
- **G5, the perturbation changes mass.** Shipped 0.95's temporal mass declines on at least one
  decay call in every cell, and 1.0's mass is unchanged in every cell. An arm whose factor never
  took effect is an unrun experiment, not a null.

G1, G2, G4 or G5 failing makes the run `VOID_INSTRUMENT`: no verdict. G3 failing also voids the run.

## 8. Pre-committed predictions

These are predictions, not descriptions; each can fail.

| Prediction | Condition |
| --- | --- |
| P1 | `no_decay` leaves the temporal mass unchanged on every decay call in every cell |
| P2 | `shipped` temporal mass declines on at least one call in every cell |
| P3 | `no_decay` has a positive pooled delta on `mapping_mix` |
| P4 | `factor09925`'s pooled delta is no larger than `no_decay`'s |
| P5 | at least one of `factor09925` and `no_decay` meets the 0.05 pooled cost bar |
| P6 | `factor099` is not better than shipped by the 0.05 bar |

P3 is the stale-knowledge prediction: the no-decay arm should be worst where a mapping permutes.
P4 is the operating-point prediction: the smallest survivor should pay no more than the ceiling.
P5 is the user's question stated as a claim that can fail.

## 9. Decision table

Committed before the run. Exactly one label is applied. A void takes precedence over every other
bucket.

| Label | Condition | Decision |
| --- | --- | --- |
| `VOID_INSTRUMENT` | G1, G2, G3, G4 or G5 fails | no verdict; repair the instrument first and keep Q049 open |
| `BOTH_COST` | `factor09925` and `no_decay` both meet the cost bar | persistence carries an adaptation price at the threshold and at the ceiling; price the trade before adopting either |
| `NO_DECAY_ONLY_COST` | only `no_decay` meets the cost bar | 1.0 is a persistence control, not an operating point; `factor09925` is the adaptation candidate and earns a capability study |
| `OPERATING_ONLY_COST` | only `factor09925` meets the cost bar | the threshold itself is the wrong point; test the interval between 0.99 and 0.9925 |
| `ARM_BETTER` | at least one of `factor09925` and `no_decay` meets the better bar, and neither meets the cost bar | persistence improved post-shift loss on these families; report it as a pilot result, not a general advantage |
| `NO_COST_DETECTED` | neither arm meets the cost or better bar | no adaptation cost was detected on these families; persistence is still not an adoption decision |

## 10. What this cannot establish

- Five seeds and two synthetic gradual-shift families. This is a pilot, not a Phase J verdict, and
  it does not generalize to other generators or natural environments.
- The endpoint is online next-event NLL, not causal recovery or theory identity. A lower loss does
  not show that the organism learned the right structure.
- The shifted worlds have no stationary control, so the endpoint is final post-shift loss, not the
  Phase J shifted-minus-stationary adaptation cost.
- Only two persistence points are tested against shipped. The interval between 0.99 and 0.9925 is
  not resolved.
- No capability, held-out prediction, revision or transfer task is scored. A no-cost result does
  not make 1.0 or 0.9925 an adoption recommendation.
- The 0.99 arm is descriptive and is not part of the primary cost decision.

## 11. Stop condition and freeze

The study is closed when the artifact exists, the page is generated from it, one label from section
9 is recorded with its conditions, and every gate is reported. No instrumentation may be added
afterwards; a new question gets a new protocol. A correction is a dated amendment appended after
section 12, never an edit in place.

## 12. Outcome

**Not yet written.** No cell has run.
