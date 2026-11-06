# Candidate supersession — probe results

**Generated from** `docs/candidate_supersession_probe.json`. **Decision**: [`DECISION-CANDIDATE-SUPERSESSION.md`](DECISION-CANDIDATE-SUPERSESSION.md). **Freeze amendment**: [`V1-FREEZE.md`](V1-FREEZE.md) §6. **World**: 10 cycles of 'amber birch cedar' then 'delta ember flora' in world A; a prediction and a schema from that world are copied into fresh stores; 10 cycles of 4 events 'quartz tidal prism lunar', which never contain world A's tags, so neither copied key can recur. Deterministic, no randomness.

## 1. Verdict

`SUPERSESSION_VERIFIED_BOTH_GENERATIONS`

Both arms now do what Law VI specifies. The prediction formed at 1.0 and retired at cycle 9 (closed form 9); the schema formed at 0.7 and retired at cycle 7 (closed form 7). Neither is re-extracted in any cycle, and under the pre-fix rule each held its formation value throughout.

The schema arm is the case the freeze amendment changes. Before it, the schema was re-admitted into the current cycle by the carry-forward and reinforced every cycle: it rose to 1.0 and never retired, so the reader had no generation decision to display. The amendment marks carried structures, and selection and storage now ignore them as evidence.

## 2. Trajectories

`live` is the newest copy per identity; `history` is the maximum over all stored copies, which is the pre-fix rule. Neither copied key can occur in the world by construction, so neither is re-extracted in any cycle. The schema arm stays listed while its value is above the stability gate: that listing is the carry-forward view, which the amendment marks so it no longer counts as evidence — it decays while listed. The 0.3 column is the schema priming gate, reported for both arms only so the two can be compared.

### prediction arm — `pred_449365ad`

Initial value 1.0; predicted retirement at cycle 9; measured 9; outcome `SUPERSEDED_AND_RETIRED`.

| cycle | in report | live | live ≥ 0.3 (ref.) | history max | history ≥ 0.3 (ref.) | copies | retired | primed |
|---|---|---|---|---|---|---|---|---|
| 1 | no | 0.8000 | yes | 1.0000 | yes | 2 | no | 0 |
| 2 | no | 0.6400 | yes | 1.0000 | yes | 3 | no | 0 |
| 3 | no | 0.5120 | yes | 1.0000 | yes | 4 | no | 0 |
| 4 | no | 0.4096 | yes | 1.0000 | yes | 5 | no | 0 |
| 5 | no | 0.3277 | yes | 1.0000 | yes | 6 | no | 0 |
| 6 | no | 0.2622 | no | 1.0000 | yes | 7 | no | 0 |
| 7 | no | 0.2098 | no | 1.0000 | yes | 8 | no | 0 |
| 8 | no | 0.1678 | no | 1.0000 | yes | 9 | no | 0 |
| 9 | no | — | no | 1.0000 | yes | 9 | yes | 0 |
| 10 | no | — | no | 1.0000 | yes | 9 | yes | 0 |

### schema arm — `schema_a2d78326`

Initial value 0.7; predicted retirement at cycle 7; measured 7; outcome `SUPERSEDED_AND_RETIRED`.

| cycle | in report | live | live ≥ 0.3 (ref.) | history max | history ≥ 0.3 (ref.) | copies | retired | primed |
|---|---|---|---|---|---|---|---|---|
| 1 | yes | 0.5600 | yes | 0.7000 | yes | 2 | no | 0 |
| 2 | yes | 0.4480 | yes | 0.7000 | yes | 3 | no | 0 |
| 3 | yes | 0.3584 | yes | 0.7000 | yes | 4 | no | 0 |
| 4 | yes | 0.2867 | no | 0.7000 | yes | 5 | no | 0 |
| 5 | no | 0.2294 | no | 0.7000 | yes | 6 | no | 0 |
| 6 | no | 0.1835 | no | 0.7000 | yes | 7 | no | 0 |
| 7 | no | — | no | 0.7000 | yes | 7 | yes | 0 |
| 8 | no | — | no | 0.7000 | yes | 7 | yes | 0 |
| 9 | no | — | no | 0.7000 | yes | 7 | yes | 0 |
| 10 | no | — | no | 0.7000 | yes | 7 | yes | 0 |

## 3. Outcomes

| arm | initial | outcome | predicted retirement | measured retirement |
|---|---|---|---|---|
| prediction | 1.0 | `SUPERSEDED_AND_RETIRED` | 9 | 9 |
| schema | 0.7 | `SUPERSEDED_AND_RETIRED` | 7 | 7 |

## 4. What this establishes, and what it does not

**Established.** Reading the store as history made Law VI decay invisible to the selector and made pruning reversible; reading it as one live copy per identity fixes both. And the second blocker was real: the frozen carry-forward re-admitted stable G2/G3 priors as current-cycle candidates, which is why a schema could rise while nothing was producing it. With the amendment both generations now decay by ×0.8 and retire on their closed-form cycle, and neither is resurrected from history.

**Not established.** Anything about transfer: no cross-context task is run here and `docs/CROSS-CONTEXT-REUSE-EARNED-RESULTS.md` is not re-scored. Nothing statistical: n = 1 per arm, deterministic. And nothing about G4–G8, which have no carry-forward graft and were never affected by this blocker.

**Limits.** n = 1 deterministic world per arm: the trajectories are closed forms and the quantity is a selection rule, not a population, so no statistical claim is made or needed the candidates are formed by the engine in world A and evaluated in fresh stores; copying the records is a fixture, and the artifact records that neither key can occur in the world (the schema's presence in the report is the carry-forward) the pre-fix rule is reconstructed from the same stored rows; it is a counterfactual about the reader, not a second engine run (rule 17b) `STABLE_THRESHOLD` is a priming gate for schemas; for the prediction arm the same reference is reported only so the two trajectories can be compared, and no eligibility claim is made for predictions the carry-forward was removed by the recorded freeze amendment (`docs/V1-FREEZE.md` §6); this probe measures the amended engine no part of the cross-context experiment is re-scored here
