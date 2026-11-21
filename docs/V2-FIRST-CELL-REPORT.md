# V2 first cell — result report

**Outcome:** `REVERSAL`
**Protocol:** `docs/V2-FIRST-EXPERIMENT-PREREGISTRATION.md` — signed 2026-11-16
**Scorer pin:** `docs/v2_first_cell_scorer_pin.json`
**Reported:** `2026-11-19`
**Read under:** [`DECISION-V2-FIRST-CELL-INTERPRETATION`](DECISION-V2-FIRST-CELL-INTERPRETATION.md)

## 1. What ran

| | |
|---|---|
| Seeds declared | 10 (`20910101`–`20910110`) |
| Measurable | 10 |
| Excluded | 0 |
| Arms | A pair counts; B frozen membership; C maintained membership |
| Endpoint | mean paired `d = L_C − L_A`, held-out next-edge log-loss |
| Interval rule | paired bootstrap over seeds, 99%, 10,000 resamples |

## 2. Gates

| Gate | Status | Evidence |
|---|---|---|
| A1 | PASS | canonicalisation rule: 5 sample paths, 3 keys, 0 mixed keys, 0 flips changed a key; smoke seed 20911101 (120 cycles, spent dry-run seed, not a cell seed): 1216 detected paths -> 107 keys over 107 distinct node sets, 0 mixed, 0 flip failures; committed regressions 177->158 with multiplicities {1: 139, 2: 19} and 138->125 reproduce; 0 id collisions. Scope: this gate does not replay the ten cell seeds; the runner replays each cell seed and applies this canonicalisation check to the experiment's own detection stream before any arm. Cell-stream check: 10 seeds replayed at 120 blocks; 16314 detected paths -> 1126 keys over 1126 distinct node sets; 0 mixed keys and 0 direction flips changed a key. This is the experiment's own detection stream, checked before any arm. |
| A2 | PASS | I1-I5 pass on a temporary store: the id survived a version bump, a member change and a direction flip; ids came from a monotone counter (1, 2, 3, 4) and were not content-derived; retirement preserved 1 member and its id, and the next key got id 4; 5 non-integer or content addresses were rejected; an unknown id and a stale version both raised. |
| A3 | PASS | M1-M5 pass on a temporary store with a bystander: add and remove left the bystander's resolved state byte-identical; a shared atom kept version 1 and its binding; a stale version and a non-member removal were rejected without moving the version; retirement kept 3 members and refused further mutation; the store owns only atoms, composite_ids, composites, members, tombstones and the frozen-graph guard can fire. |
| A4 | PASS | reallocated base seed 20740101, 120 cycles: 115 of 158 keys admitted at m=2, 275 observed member references (the sizing model assumed 3 per composite, 345); the rebuilt store is 16 pages / 65536 bytes, at or below the 135168-byte budget; compaction reclaimed 0 atoms and left all 115 resolutions identical; tables atoms, composite_ids, composites, members, tombstones carry no history table. |
| A5 | PASS | two builds from the spent smoke stream's 96 admissions produced identical ids, keys, members and versions; retiring id 96 left a tombstone and the next registration got id 97, so allocation is monotone and retirement never frees an id; the novel key quux|zorp was absent from the stream. Scope: the smoke stream, not the held base world. |

## 3. Exclusions

None; every declared seed was measurable.

## 4. Interval

The mean paired difference is `0.004199` with a 99% interval `[0.003617, 0.004890]`
(10,000 resamples). The interval lies entirely above zero, so the label is `REVERSAL`.

## 5. Beta selections

| Seed | Arm B | Arm C |
|---|---|---|
| 20910101 | 1 | 1 |
| 20910102 | 1 | 1 |
| 20910103 | 1 | 1 |
| 20910104 | 1 | 1 |
| 20910105 | 1 | 1 |
| 20910106 | 1 | 1 |
| 20910107 | 1 | 1 |
| 20910108 | 1 | 1 |
| 20910109 | 1 | 1 |
| 20910110 | 1 | 1 |

Arm A selects no beta.

## 6. Decomposition

| Quantity | Value |
|---|---|
| Mean `d_C − d_A` | `0.004199` |
| Mean `d_B − d_A` | `0.010937` |
| Revision effect `d_C − d_B` | `-0.006739` |

`d_B` is the frozen-membership arm's difference from the baseline. The decomposition is
descriptive; `d_B` is not a second criterion.

## 7. Selection comparison

The committed matched controls are `-0.000497` at equal mass and key count on the null worlds and `+0.002091` on the planted world — `4.05%` of its `0.051685` gain (`-0.000460` at equal mass alone). The cell's cost, `0.004199`, is larger than the matched null cost; either way the charter fails and the comparison is a diagnostic, not a rescue.

## 8. Control arm (`M1`)

| | |
|---|---|
| Seed | 20910101 |
| Target | `not-run-target` — remove `not-run-edge` |
| Bystander | `not-run-bystander` |
| Metric | not measured |
| Status | NOT RUN |

Not run: no section 8 control record was supplied; the arm is secondary. No M1 claim is made from this arm; it is secondary and does not change the charter outcome.

## 9. What this authorises

> REVERSAL authorises the report that maintained membership cost held-out prediction, which is a failure and is not evidence that selection found signal with the wrong sign.

## 10. What this does not authorise

No relabelling as a near pass or as signal found backwards; no retune, feature or second run. The block is spent.

## 11. Not evidence

One cell, one world family, ten paired seeds, one readout. The charter's answer is scoped to that; it is not a capability, transfer or G4 result, and no V1 result is V2 evidence.
