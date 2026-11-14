# A1 target-selection protocol — per-seed targets and cycle-36 U

**ID:** `A1-TARGET-SELECTION-1`  
**Date:** 2026-11-14  
**Status:** `P0 PASS — SIX TARGET SETS FORMED, FREEZE READINESS OPEN, NO GRANT`
**Parent:** `A1-TWO-PATH-1`

**This is a design and implementation record, not a result, a freeze or a grant.** It defines how the A1 per-seed target sets are chosen and where the cycle-36 `U` is sampled. The selection pass has now been implemented and run; it formed four disjoint targets for all six provisional seeds and wrote `docs/a1_target_selection.json`. It has not reserved the seeds, frozen the manifest, authorised a cell or produced an A1 result. The current manifest remains `REGISTERED DESIGN — NOT FROZEN, NOT RUN, NO GRANT`, every executing path still refuses, and the selected targets are not yet entered as fixed manifest targets.

## 1. What this protocol fixes

The two-path design requires three things that the current manifest leaves open:

1. a per-seed target set that is fixed before any arm cell and applied identically to every cell of that seed;
2. a `U` measurement taken before carrier, `K` and `Y` exist;
3. a rule that prevents those choices from being revised after an outcome is seen.

This protocol fixes the selection rule, the `U` sampling point and the integrity checks. The target values were produced by the selection pass on 2026-11-14 and are recorded in the artifact; they are not frozen until the manifest freeze and the separate grant decision.

The object remains the one in [`A1-TWO-PATH-MANIFEST.md`](A1-TWO-PATH-MANIFEST.md): engine `0.15.0`, six provisional seeds `20630101–20630106`, 120 cycles, cap 40, the compositional world family and the fixed directed-edge universe. The seed block is **not** reserved by this draft.

## 2. Target-set size and the unit of assignment

The unit is a **seed**, not a cell. For each seed `s`, one set `T_s` is chosen and used unchanged in all six cells:

| Cell | Admission | Carrier | Assertion |
| --- | --- | --- | --- |
| `A+K+` | allowed | available | on |
| `A+K-` | allowed | blocked | on |
| `A-K+` | blocked | available | on |
| `A-K-` | blocked | blocked | on |
| `Y_MINUS_A+K+` | allowed | available | blocked |
| `Y_MINUS_A-K+` | blocked | available | blocked |

`T_s` contains **four directed edges**. Four is a design convention chosen before target selection, not a power estimate: it gives each seed a rate denominator while keeping the edge-level intervention sparse enough that target carriers are less likely to share structure. The final power and prevalence review before freeze may reject this protocol; it may not change the target set after an outcome is seen.

The four targets must have **disjoint endpoints**. No two targets may share a tag. This limits cross-target interference and prevents one `K−` carrier filter from removing another target's carrier. If a seed cannot supply four eligible disjoint edges, it has no admissible target set and **A1 is not run**; no smaller set, substitute edge or extra seed is permitted.

**Estimand record (2026-11-14).** As implemented, the selector samples the **representative eligible pre-37 cycle-membership directed-edge population**. The 24 selected target observations (23 unique edges across six seeds) are statistically indistinguishable from the 358 unselected candidates on cycle-36 strength (medians 16 vs 16, means 15.333 vs 15.215, permutation p = 0.918), and all 382 candidates are eligible. The estimand is therefore a representative eligible-edge effect. It is **not** a sample of high-`U` edges, hard edges or carrier-enriched anomalies. If the experiment requires high carrier propensity, the selector must be redesigned and the targets regenerated before freeze; that is a different experiment. This is a design fact, not a result; it does not resolve the C1 denominator problem recorded in [`A1-POWER-REVIEW.md`](A1-POWER-REVIEW.md).

## 3. Candidate universe

For seed `s`, build `E_s` from the **first 36 acquisition cycles only** of the world's trainable stream, using the same `_world_compositional_edges` definition on a 36-cycle world. The boundary is the acquisition cycle, not the engine's sleep counter; the sleep counter can lag while early cycles produce no candidates, and following it would let event cycles 37+ enter the candidate set. No event, transition or generator state after acquisition cycle 36 may enter the candidate set. The full 120-cycle universe is used only later for the target-in-world validation and must be a superset of `E_s`. `E_s` is derived only from the pre-37 world stream and trainable mask; no arm output, carrier, assertion, rank or `SleepReport` enters it.

Each unordered tag pair may contribute at most one directed edge. If both orientations are in `E_s`, choose the orientation deterministically:

```text
h = SHA-256("A1-TARGET-ORIENTATION-1|" + seed + "|" + min(a,b) + "|" + max(a,b))
orientation = a>b if the first hex digit of h is even, else b>a
```

If the chosen orientation is absent from `E_s`, use the other orientation. The orientation choice is recorded in the selection artifact. This avoids always selecting the lexicographically first direction.

## 4. Selection pass

Target selection uses a **36-cycle, no-arm shadow pass** on the shipped engine, stopping after the 36th acquisition cycle. It is not one of the 36 A1 cells and is not evidence. It replays the same event stream and the same sleep calls that a real cell would make through cycle 36; only the sleep reports are discarded. The pass reads the temporal graph and no `SleepReport` field at all: not `predictions`, `loops`, `dreams`, assertions, carriers, rank, or `cycle`. It does not inspect cycles 37–120, and the candidate universe is truncated at acquisition cycle 36.

Immediately after the **cycle-36 acquisition observations** have been stored and before that cycle's `run_sleep_cycle()`, the pass records for every candidate edge:

| Field | Definition |
| --- | --- |
| `direct_count` | temporal count `a → b` |
| `reverse_count` | temporal count `b → a` |
| `strength` | `direct_count + reverse_count` |
| `measured_cycle` | `36` |
| `cycle_member` | true when a path `b → a` exists in the same temporal graph, so `a → b` lies on a directed cycle |

`cycle_member` is a pre-carrier structural proxy for the carrier path. It is not a carrier observation and does not guarantee that a loop carrier forms after cycle 36. It is used because selecting edges that are not on any temporal cycle makes a `K+` denominator unlikely; the protocol does not use any post-cycle-36 carrier or assertion to make the choice.

An edge is **eligible** only when:

- it belongs to `E_s`;
- `strength > 0` at cycle 36;
- `cycle_member` is true.

The selection order is deterministic and blind to the magnitude of `U`:

```text
key(seed, edge) = SHA-256("A1-TARGET-1|" + seed + "|" + a + ">" + b)
sort eligible edges by key, then by edge string
walk the sorted list and take the first four whose endpoints are disjoint
```

The pass records the universe size, candidate count, eligible count, rejected reasons, selected edges, their `U` rows and the selection-pass digest. It must not record a served, carrier or assertion field. The selection artifact is `docs/a1_target_selection.json` and is not a result.

## 5. Cycle-36 U measurement in every cell

The `U` fields have one meaning in the selection pass and in every A1 cell:

- `direct_count`: count of the selected directed edge in `memory.temporal_edges(min_count=1)`;
- `reverse_count`: count of the opposite direction;
- `strength`: their sum, an unnormalised count;
- `measured_cycle`: `36`;
- `measured_before`: carrier, `K` and `Y`.

The sample is taken **before** the cycle-36 sleep/consolidation. The implemented sequence is:

```text
store cycle-36 observations
if acquisition_cycle == 36:
    pending = temporal counts from memory, before sleep
report = run_sleep_cycle()
if acquisition_cycle == 36:
    U = pending
```

The boundary is acquisition cycle 36. The engine's sleep counter is not used to place `U`; it can lag the acquisition count while early cycles produce no candidates, and using it would move the boundary and admit later acquisition events. The old post-sleep sampler has been removed from `benchmarks/a1_arms.py`.

`U` is never read from a `SleepReport`, never inferred from a post-outcome rank and never recomputed after carrier or assertion data exist. It is a pre-treatment covariate for C5 and for the `U`-conditional separation of `M-K` from `M-S`; it is not an outcome and not a post-treatment adjustment.

`U` is observation-only: `MemoryService.store()` excludes `event_type == "sleep"` from the temporal graph, so sleep payloads cannot enter `direct_count`, `reverse_count`, `cycle_member` or `strength`. The selection pass must prove this with the sleep-blindness test below rather than relying on the substrate comment.

Every cell of a seed must produce the same `U` and the same object fingerprint as the other cells of that seed. A mismatch is `VOID` under C9. A missing `U` field fails C5; it is **not** replaced with zero or with a later measurement.

**Runner correction implemented.** `benchmarks/a1_arms.py` captures `pending_u` after acquisition cycle 36 is stored and before `run_sleep_cycle()`; `tests/test_a1_prefreeze.py` pins the pre-sleep ordering. The selection pass uses the same acquisition-cycle boundary. No A1 cell has been run.

## 6. Adversarial checks

**P0 — Protocol compliance (2026-11-14): PASS.** Before treating target generation as usable, the implementation must execute the registered boundary. [`A1-ADVERSARIAL-AUDIT.md`](A1-ADVERSARIAL-AUDIT.md) records all six P0 conditions as passing: `U` sampled before the cycle-36 sleep call, candidate universe restricted to the first 36 acquisition cycles, future-blindness, report-blindness, sleep-blindness and determinism. This is a compliance gate, not a result; the manifest remains unfrozen, the [power review](A1-POWER-REVIEW.md) records C1 denominator fragility; C4 non-target rows are implemented but no cell has run.

The selection rule must survive these checks before it can be frozen. They are design checks, not A1
cells; none opens a database for an arm or records a result.

| Check | Test | If it fails |
| --- | --- | --- |
| **Future-blindness** | Run the selector on a 36-cycle world and on a 120-cycle world, using only the first 36 cycles of each. The selected targets and `U` at cycle 36 must be identical. Replacing cycles 37–120 with arbitrary events must not change the selection. | The rule uses later world structure; reject the rule. |
| **Report-blindness** | Make `predictions`, `loops`, `dreams` and assertion fields unavailable to the selection pass, or inject a failure if they are read. The pass must still produce the same targets. | Carrier or assertion information leaked into selection; reject the rule. |
| **Sleep-blindness** | Store a synthetic `event_type="sleep"` payload and verify the `precedes` graph and selected targets do not change. | Sleep output entered `U`; reject the rule. |
| **Determinism** | Two independent selection passes on the same seed and build produce the same orientation, targets, `U` rows and digest. | The rule is not reproducible; no freeze. |
| **Magnitude-blindness** | Increase or decrease positive `U` counts without changing zero/non-zero status or cycle membership; the selected set must not change. | The rule ranks by `U`; reject the rule or declare the ranking deliberately. |
| **Feasibility** | All six candidate seeds must yield exactly four eligible, disjoint targets. | No run for a failing seed; no smaller set and no substitute seed. |
| **No all-or-none** | The selector must return exactly four targets or none. It may not select the whole universe or an empty set. | The rule collapses; reject it. |
| **No post-output tuning** | After the six sets are produced, no change to `N`, hash salt, orientation salt, cycle rule or edge filter is allowed. The artifact is frozen before the manifest. | The selection is not preregistered; no freeze. |

The future-blindness check is the one that answers the review question directly: **the target must be
selectable from information available before cycle 37.** A rule that needs a cycle-50 world edge, a
sleep report, a carrier or an assertion is not an A1 target rule.

**Implementation status (2026-11-14).** P0 passes in the six-seed audit: the selector self-test covers determinism, magnitude-blindness, the four-disjoint rule, the no-all-or-none rule and the cycle/U definitions; the six-seed pass formed four targets for every seed. [`A1-ADVERSARIAL-AUDIT.md`](A1-ADVERSARIAL-AUDIT.md) records future-blindness, determinism, feasibility, report-blindness and sleep-blindness; all pass. The target sets are implemented and audited but not frozen; the power review is recorded and C4 non-target rows are implemented but not run.

Cycle membership is a pre-treatment eligibility criterion, not an outcome. It nevertheless narrows
the A1 estimand to target edges lying on a cycle-36 temporal cycle with a positive pre-37 count.
The verdict is scoped to that target population; it does not generalize to every world edge.

## 7. Integrity checks before freeze


The target set is admissible only when all of the following hold:

- exactly four targets for every seed;
- every target is in `E_s`;
- no two targets share an endpoint;
- every target has a cycle-36 `U` row with `strength > 0`, `measured_cycle == 36`, and `cycle_member == true`;
- the selection artifact's stored digest matches its contents (a fresh pass is still required before freeze);
- the same target strings are stored in the manifest's `targets.by_seed`;
- the six candidate seeds are unchanged and the seed-freshness scan is empty;
- the engine is still the shipped `0.15.0`;
- `U` is marked as measured before carrier, `K` and `Y`.

`a1_two_path.preflight` now checks four targets per seed, disjoint endpoints, world-universe membership, the selection-artifact path, the artifact's own selection checks and digest, and equality between `targets.by_seed` and the artifact. The manifest targets are still `UNRESOLVED`, so these checks run only when a fixed target block is supplied (the self-test exercises that path). A target-looking list is still not a frozen target set.

When the checks pass, the manifest's target block changes from `UNRESOLVED — MUST BE FIXED BEFORE FREEZE` to `FIXED BEFORE FREEZE`, with the per-seed strings and the selection-artifact path. Freezing the manifest, reserving the seeds and issuing a grant remain separate acts.

## 8. Failure and stop conditions

| Condition | Disposition |
| --- | --- |
| Fewer than four eligible disjoint targets for a seed | `A1 TARGET SET NOT FORMED`; A1 is not run. No substitute edge, lower N or extra seed. |
| Selection pass and cell `U` disagree | `VOID` under C9; no run is interpreted. |
| A target is missing from `E_s` or is not disjoint | No freeze; the selection is invalid. |
| A target has no `K+` denominator after the run | The relevant C1/C2/T2 gate fails as `VOID` or `NOT IDENTIFIED`; no re-selection. |
| `U` is absent or measured after carrier/`K`/`Y` | C5 fails; no re-selection and no substitute measurement. |

A1 has one registered attempt. A failed or unmeasurable gate is terminal, as recorded in [`A1-GATE-READINESS.md`](A1-GATE-READINESS.md); a new target rule or new run requires a new registered design, not a quiet retry.

If the target set cannot be formed, the parked record must say so: **`A1 PARKED — TARGET SET NOT FORMED`** (fewer than four eligible disjoint targets) or **`A1 PARKED — NO ADMISSIBLE TARGET RULE`** (the rule cannot be expressed from pre-37 observables). If four targets exist but the owner does not grant the run, the record is **`A1 PARKED — NO GRANT`**. Those are different lessons and require different revisit conditions; "no grant by the deadline" is not a substitute for a protocol failure.

## 9. What this protocol does not do

- It does not freeze the selected four edges into the manifest; the artifact records them, but the manifest target block remains unresolved.
- It does not reserve seeds `20630101–20630106`, freeze the manifest or authorise any cell.
- It does not issue an owner grant, change an engine file, clear C1–C9 or create a result.
- It does not by itself establish C4. The A1 cell output now emits a separate `neighbor_rows` stream with raw A/K/Y rates; `attach_neighbor_deltas` joins it to the A+K+ control, and `c1_rows` includes baseline-available non-target edges in the C1 denominator. No cell has run, so C4 is not cleared.
- It does not complete the power/prevalence review. `N = 4` is a design convention, not a power calculation. The dated freeze decision is **DO NOT FREEZE (2026-11-14)**, answering the adequacy question **NO — NOT AS CURRENTLY EMITTED**.

## 10. Pre-freeze checklist

The formal compliance record is [`A1-PROTOCOL-COMPLIANCE-REPORT.md`](A1-PROTOCOL-COMPLIANCE-REPORT.md); [`A1-PRE-FREEZE-CHECKLIST.md`](A1-PRE-FREEZE-CHECKLIST.md) is the working checklist. It separates the P0 conditions that gate target freeze from the unrun C4/C1 measurements, freeze and grant; the power review is recorded.

0. **Done — P0 PASS.** The cycle-36 `U` sample is captured after the 36th acquisition cycle is stored and before `run_sleep_cycle()`; the pre-sleep ordering is tested. The pre-37 universe, future-, report- and sleep-blindness and determinism checks all pass in [`A1-ADVERSARIAL-AUDIT.md`](A1-ADVERSARIAL-AUDIT.md).
1. **Done.** The cycle-36 `U` sample is captured after the 36th acquisition cycle is stored and before `run_sleep_cycle()`; the pre-sleep ordering is tested.
2. **Done.** `benchmarks/a1_target_selection.py` implements the no-arm pass, artifact schema, digest and self-test. The pass reads the temporal graph and no report field.
3. **Done.** `a1_two_path.preflight` checks four-per-seed, disjoint endpoints, universe membership, artifact equality and the artifact's selection digest. The manifest is still unresolved.
4. **Implemented — not run.** A1 cell output emits a separate `neighbor_rows` stream for every non-target edge, with A/K/Y availability rates; `attach_neighbor_deltas` joins it to the seed’s A+K+ control, and `c1_rows` includes baseline-available non-target edges in the C1 denominator. No cell has run, so C4 is not cleared and must not be claimed.
5. **Done.** Determinism, magnitude-blindness, feasibility, no-all-or-none, future-blindness, report-blindness and sleep-blindness pass in [`A1-ADVERSARIAL-AUDIT.md`](A1-ADVERSARIAL-AUDIT.md).
6. **Done — freeze still open.** [`A1-POWER-REVIEW.md`](A1-POWER-REVIEW.md) finds that four target rows make the 0.95 C1 floor effectively 100%; C4 non-target rows are now instrumented, but C1 and C4 still require a run. The targets must not be frozen.
7. **Not done.** Freezing the target sets/manifest and the dated owner grant remain separate acts. The manifest gate still refuses.

**Not evidence:** A selection rule, a sampling contract, a P0 compliance audit and a draft six-seed target artifact. The targets are not frozen, no seed is reserved, no A1 cell is authorised and no result exists.
