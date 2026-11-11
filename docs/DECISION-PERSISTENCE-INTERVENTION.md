# Decision: the persistence intervention is carry counts, with an explicit boundary reset

Dated 2026-11-11. Recorded against Q055 and the zero-cell diagnostic that explains the
persistence-off zeros. The diagnostic is a replay of committed worlds, not a new cell; this
decision chooses the arm that follows from T1b, and authorises no run.

## The decision

Carry counts across cycles is the persistence intervention; the floor and the event lookback stay fixed.

The arm that follows is PERSISTENCE-CARRY-1, a clean carry-versus-reset block at cap 112.

The carry arm is the shipped cross-cycle accumulation. The comparator is the same memory
with an explicit reset at every cycle boundary, including a cycle whose last event is
withheld. That explicit reset closes the boundary leak in T1b's implementation, where
`on_cycle()` did not fire when the eighth event was skipped and the treatment therefore
carried counts it was supposed to remove.

**Status.** The choice is recorded; the carry arm is not in force and no cell has run.

## What the zero-cell finding changes

The zero cells are not a ranking or assertion loss. They are a candidate-generation
threshold loss: after the reset, no world edge reaches `PREDICTION_MIN_COUNT = 5`, so no
world edge becomes a prediction candidate and `S_ever` is zero. The ceiling is **3–4** on the
five zero cells, not because the cap is binding, but because no tag repeats five times in a
cycle and the 3-event window exposes only a few source-target overlaps.

The diagnostic also shows the limit is not a universal 4→5 cliff. At the 3-event lookback:

| Floor | Local admissible world edges on the five zero cells |
|---:|---|
| 5 | 0, 0, 0, 0, 0 |
| 4 | 1, 0, 0, 0, 1 |
| 3 | 8, 22, 18, 10, 12 |
| 2 | 91, 91, 85, 89, 87 |
| 1 | 112, 112, 112, 112, 112 |

The five zero cells are T1 20612204 and 20612205, and T1b 20612208, 20612210 and
20612212. The figures are admissibility ceilings, not served or asserted counts. The
full zero-cell replay and its serving controls are in
`docs/persistence_zero_served_diagnostic.json` and `docs/PERSISTENCE-ZERO-SERVED-NOTE.md`.

## The three alternatives

| Alternative | What it changes | Why it is not the intervention |
| --- | --- | --- |
| Lower `PREDICTION_MIN_COUNT` | A global admission threshold | It admits edges that never crossed the persistence threshold. At 4 it leaves three of the five zero cells at zero; at 2 or 1 it makes almost every world edge admissible, so the result cannot be attributed to persistence. |
| Extend `_record_temporal_edges` lookback | The event graph used to build all temporal counts | It changes the graph globally. Event rows persist across the cycle reset, so a longer lookback also reintroduces cross-cycle context; at 8 it admits 86–93 edges from the carried replay. That is a carry channel in disguise, not a read-floor fix. |
| Carry counts across cycles | The treatment itself | It is the only alternative that leaves the floor and the event graph fixed and makes cross-cycle accumulation the variable. T1b's shipped-versus-off contrast is the direct precedent. |

**Lower PREDICTION_MIN_COUNT from 5 to 4, 3, 2 or 1.** It changes a global admission threshold and admits edges that never crossed the persistence threshold; at 4 it leaves three of the five zero cells at zero, and at 2 or 1 it makes almost every world edge admissible, so it cannot isolate persistence.

**Extend the temporal event lookback from 3 to 4, 6, 8 or 16.** It changes the event graph globally and, because event rows persist across the reset, it reintroduces cross-cycle context through the lookback; at 8 it admits 86-93 edges from the carried replay, so it is a carry channel in disguise.

**Amend PERSISTENCE-MECHANISM-1 to add a lookback arm.** The frozen 2x2 remains unrun and is not amended; a lookback arm is a separate treatment and would confound its decay and floor contrasts.

**Promote the zero-cell diagnostic to a capability finding.** The diagnostic explains a ceiling on five seeds; it is not a new cell and cannot support a capability, retention or transfer claim.

## The arm

`PERSISTENCE-CARRY-1` is a two-arm, within-process block on the shipped 0.15.0 build at
cap 112:

- **carry** — the shipped cross-cycle temporal count, decayed at `0.95` per cycle;
- **explicit_reset** — the same engine and memory, with every `precedes` count set to zero
  at each cycle boundary, including boundaries whose last event is not trainable.

The reset is a boundary hook, not an `on_cycle()` callback that can be skipped. The floor
stays at **5**, the event lookback stays at **3**, and no engine file changes.

The block has six fresh seeds, 120 cycles and **12 cells** plus a determinism rerun. The
primary endpoint is `S_ever`; `A_W` is secondary. The gates are the T1b family:

- G1: one 0.15.0 build at cap 112, no engine edit;
- G2: one world per seed, identical across arms;
- G3: explicit reset live on every cycle, including skipped-boundary cycles; a carry arm
  never resets;
- G4: P is the denominator, a zero `S_ever` is measured, and zero P is VOID;
- G5: a live seed axis;
- G6: determinism rerun;
- G7: exactly 12 cells.

The decision rule is the T1b rule: a paired gain of at least **10** edges on at least
**5 of 6** seeds with a positive paired lower bound reads `CARRY CARRIES PERSISTENCE`;
anything else reads `CARRY NOT LIMITING` or `VOID`. The point is replication with a clean
reset, not a new effect-size claim.

## Status and authority

The decision is **PENDING**. No arm is built, no grant is recorded, no cell has run and
`PERSISTENCE-MECHANISM-1` remains frozen and unrun. This record does not amend that 2x2, does
not change the engine, and does not authorise a run. A dated grant and a preregistration for
`PERSISTENCE-CARRY-1` are required before the first cell.

## Open question

Does an explicitly reset cycle-boundary carry arm preserve the T1b direction while closing the skipped-reset leak?

## Why this follows from T1b

T1b returned `PERSISTENCE CONTRIBUTES`: on six fresh seeds the shipped arm served 101, 95,
100, 103, 98 and 99 world edges while persistence-off served 0, 1, 0, 3, 0 and 3. The
zero-cell diagnostic explains the zero tail as a threshold consequence, not a missing
measurement. The next intervention should therefore preserve the variable that created the
tail—cross-cycle accumulation—while removing the boundary ambiguity. Lowering the floor or
extending the lookback would change the conditions under which the threshold is read; they
would not test the carry mechanism T1b identified.

## Evidence

`docs/t1b_persistence_off_run.json`, `docs/T1B-PERSISTENCE-OFF-RESULT.md`,
`docs/persistence_zero_served_diagnostic.json`, `docs/PERSISTENCE-ZERO-SERVED-NOTE.md`,
`docs/persistence_mechanism_prereg.json`, `docs/PERSISTENCE-MECHANISM-PREREGISTRATION.md`.

## What this does not cover

It does not establish that carry is sufficient for every seed, that the floor or lookback
are scientifically wrong, or that the zero-cell diagnostic is a result. It does not fix the
boundary-reset leak in the T1/T1b artifacts, re-score T1b, or adjudicate Q2, Q4, the
admission decision or the transfer result. The carry arm's six fresh seeds and any run date
belong to its preregistration, not to this decision.
