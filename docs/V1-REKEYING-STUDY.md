# Would a direction-free identity have changed a carrier's fate?

**Status:** `OFFLINE COUNTERFACTUAL. Rules simulated, not run. Authorises no code, no arm, no freeze.`

**In one paragraph.** Yes, slightly, and not in the way that matters. Swapping V1's direction-bearing persistence key for a
direction-free one would have saved **19 identities** (177 to 158) and **20 retirements**, and converted
**55 orientation flips** from a restart into a reinforcement. Strength concentrates a little (mean live
strength 0.8067 to 0.8191, top-5 appearance share 0.2032 to 0.2194), and the share of identities that stay above the
stability threshold moves from 16.4% to 17.1%. That is a real but small correction — the orientation flip was never the
capability V1 lacks. The primitive specification already canonicalises direction, so this study confirms a design choice
rather than reopening it.

## 1. What was done

One replay of the measured 120-cycle world (seed recorded in the artifact), reading back every
`sleep:loop_candidate` row the engine wrote (4303 rows, 177 identities). V1's selection rules were re-implemented
offline — +0.05 on re-detection, ×0.8 on absence, retirement below 0.15 — and run twice over the same detections: once keyed
on the path in order (V1), once on the sorted tag set (the specification's `cycle3` key).

## 2. The comparison

| | Direction-bearing (V1) | Direction-free |
|---|---|---|
| Identities created | 177 | 158 |
| Retirements | 201 | 181 |
| Reinforcements | 1069 | 1091 |
| Decays | 2863 | 2600 |
| Live at the end | 29 | 27 |
| Above the stability threshold | 29 (16.4%) | 27 (17.1%) |
| Mean live strength | 0.8067 | 0.8191 |

Orientation flips observed: **55**. Each one is a cycle in which V1 retires nothing but stops reinforcing one
identity and starts another from its raw strength.

## 3. Validation, and the one gap

Identities match exactly: both are 177. Retirements do not — 186 observed against 201 simulated — because the simulator decays every identity
forever, while the engine reads only the newest 4,000 sleep events (about 24 cycles at this candidate volume) and therefore
*forgets* some identities instead of retiring them. The counterfactual is therefore a comparison of the two keys under
identical rules and perfect memory; it is not a model of the window.

That gap is itself worth noting: in V1 a carrier can disappear without a death record, so "how many carriers died" is not a
quantity the store answers exactly. 186 retirement rows are a lower bound on disappearances.

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

One seed, one world, 120 cycles; the counterfactual is rules-simulated with perfect memory, and the engine's window makes the
observed retirement count a lower bound. It measures persistence bookkeeping, not behaviour: nothing here predicts whether an
addressed composite would beat the pair-count baseline.
