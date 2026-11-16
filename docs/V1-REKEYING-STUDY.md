# Would a direction-free identity have changed a carrier's fate?

**Status:** `OFFLINE COUNTERFACTUAL. Rules simulated, not run. Authorises no code, no arm, no freeze.`

**In one paragraph.** Yes, slightly, and not in the way that matters. Swapping V1's direction-bearing persistence key for a
direction-free one would have saved **19 identities** (177 to 158) and **16 retirements**, and converted
**55 orientation flips** from a restart into a reinforcement. Strength moves a little (mean live
strength 0.8043 to 0.816, top-5 appearance share 0.2032 to 0.2194), and the share of identities that stay above the
stability threshold moves from 16.4% to 17.1%. That is a real but small correction — the orientation flip was never the
capability V1 lacks. The primitive specification already canonicalises direction, so this study confirms a design choice
rather than reopening it.

## 1. What was done

One replay of the measured 120-cycle world (92 of its blocks ran a sleep cycle), reading back every
`sleep:loop_candidate` row the engine wrote (4,303 rows, 177 identities). V1's selection rules were re-implemented
offline — +0.05 on the fresh detection, ×0.8 on absence, retirement below 0.15 — and run twice over the same detections:
once keyed on the path in order (V1), once on the sorted tag set (the specification's `cycle3` key).

## 2. The comparison

| | Direction-bearing (V1) | Direction-free |
|---|---|---|
| Identities created | 177 | 158 |
| Retirement rows | 186 | 170 |
| Reinforcements | 1083 | 1101 |
| Decays | 3004 | 2735 |
| Live at the end | 30 | 28 |
| Above the stability threshold | 29 (16.4%) | 27 (17.1%) |
| Mean live strength | 0.8043 | 0.816 |

Orientation flips observed: **55**. Each one is a cycle in which V1 retires nothing but stops reinforcing one
identity and starts another from its raw strength.

Loop `strength` is the engine's raw transition count (`min(counts)`), not a probability, so values above 1.0 are expected and
are not a defect.

## 3. Validation

Both checks pass: 177 identities and all 186 retirement rows are reproduced by the direction-bearing simulation
before the key is swapped.

An earlier version of this page reported 201 retirements and blamed the 4,000-event prior window for the gap. That was
wrong, and the correction matters. The simulator reinforced from the prior's strength (`prior + 0.05`); the engine reinforces
the fresh detection (`detection + 0.05`, `_reinforce_current`). With that one rule fixed the simulation matches the store
exactly, and a separate boundary measurement — [`V1-CARRIER-FORGETTING`](V1-CARRIER-FORGETTING.md) — found that the window never
forgot a live carrier in this world: a lapsed carrier decays below the death threshold in at most nine cycles, inside the
window's ~18-cycle span. The counterfactual below is therefore pure rules, not a memory model.

## 4. The cases that changed

| Node set | Appearances | Orientations | Flips |
|---|---|---|---|
| `maple/sable/slate` | 60 | 2 | 13 |
| `maple/sable/willow` | 56 | 2 | 11 |
| `amber/maple/slate` | 9 | 2 | 4 |
| `cedar/maple/sable` | 28 | 2 | 4 |
| `amber/birch/cedar` | 4 | 2 | 3 |

These are the identities a direction-free key would have merged; each flip is a reinforcement V1 spent as a restart. The
largest, `maple/sable/slate`, appears 60 times with 13 flips — meaning that under a direction-free key it would have
been one continuously reinforced object rather than two alternating ones.

## 5. What it means for the primitive

- The specification's `cycle3` canonicalisation is **confirmed**, not reopened: the measured benefit is the one it was designed
  for, and it is modest.
- The gap the code reading found is untouched by re-keying: **no consumer reads a carrier's cycle** and **no code path mutates
  a path**. A direction-free id gives an object a longer life, not a use.
- So the ordering of the primitive's work does not change: content-free id, membership mutation, consumer. This study retires
  the first item's open question ("would a direction-free identity have mattered?") with a quantified yes, and leaves the
  other two where they were.

## 6. Limits

One seed, one world, 92 sleep cycles; the counterfactual is rules-simulated over the store's detections, not run. Where
both orientations of a node set appear in one cycle the free key keeps the last detection's strength, since a merged
identity has only one; that choice is arbitrary and not measured. The study measures persistence bookkeeping, not
behaviour: nothing here predicts whether an addressed composite would beat the pair-count baseline.

The direction was replicated on a second world: see [`V1-REKEYING-TWO-SEEDS`](V1-REKEYING-TWO-SEEDS.md).
