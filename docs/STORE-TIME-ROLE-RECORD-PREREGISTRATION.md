# Pre-registration — store-time role provenance on schema-primed predictions

**Date**: 2026-11-07
**Status**: PREREGISTERED, **SCOPED** — **NOT APPLIED**. The owner authorised scoping this as an
engine change in its own right (manual row 58); no line of `organica/` changes until its
preconditions in §1 are met, and no cell is run by this document.
**Decision it serves**: `docs/DECISION-STORE-TIME-ROLE-RECORD.md` (amended in §9 of that record).
**Supersedes**: the reserved draft of the same date, which held the change behind residuals R1–R3.
The trigger has changed from a residual to the owner's authorisation; the residual taxonomy survives
as the instrument's failure modes (§5), not as the entry condition.
**Why it exists**: so that the engine change which lets Q028's trace name a licensing role is fixed
before it is written — its fields, its neutrality proof, its trace criteria, its falsifiers, its
decision table and its stop condition — and cannot be shaped around whatever the first run shows.

```
scope: engine
applied: false
bar_share: 0.90
calibration_seed: 20261101
confirmatory_block: 20272001-20272024
```

---

## 1. Scope: what this authorises, and the preconditions it waits on

**This document authorises one engine change**: a prediction that a schema prior primed carries the
role pair that licensed it, recorded **on the prediction itself**. It authorises no second field, no
new structure type and no trace status beyond §5.

Two preconditions, both checkable, are **not** met by this document:

| id | precondition | why it must hold first |
|---|---|---|
| P0 | the pair resolver exists in `benchmarks/transfer_provenance.py` and its `--self-test` passes | the field has no reader otherwise, and a field nothing reads is instrumentation without an instrument (rule 17c) |
| P1 | the calibration cell in §5 records a non-zero count of schema-primed predictions | with an empty denominator the trace share is **not measurable**, never zero (rule 13b) |

If P0 is unmet, this change waits; it is not abandoned and its criteria do not move. If P1 is unmet
on the calibration cell, the cell is void and the change is not evaluated — a zero denominator is a
void run, not a null result (rule 13a).

## 2. What is recorded, exactly, and where

`organica/sleep_extraction.py`, inside the existing congruent branch that already sets
`evidence["schema_prior"]` (lines 476–478):

- `evidence["schema_prior_roles"]` — the two-element list `[source_role_id, target_role_id]`, copied
  from the schema row that licensed this prediction, written **only** when `schema_prior` is written.
- `evidence["schema_prior_role_exemplars"]` — the two sorted exemplar tuples, written only under R2
  (a role row pruned before the trace reads it), so a dead id does not erase the content it named.

Separately, and only if residual R3 is observed on the calibration cell, one repair in
`organica/sleep.py:268-283`: the `stable_prior` rebuild copies `source_role_id` and `target_role_id`
alongside the exemplars it already copies, so a rebuilt schema does not lose the ids it was built
from. **No other edit.** `schema_prior` is unchanged; `strength`, `confidence`, admission and
ordering are untouched.

## 3. Why it can stay inert — every consumer, enumerated

- **Identity**: `_candidate_key` for a prediction is `prediction:<source>|<target>`
  (`sleep_selection.py:265-266`); a new evidence key cannot merge or split a structure.
- **Ranking**: the prediction sort key reads `schema_prior` truthiness, `target_entropy`,
  `transition_prob`, `temporal_count`, `source`, `target` (`sleep_extraction.py:505-512`).
- **Selection and decay**: reads `observations`, `prior_confidence`, `prior_strength`,
  `strengthened`, `decayed_from`, `retired_from`, `closed`, `resolved_by`.
- **Storage**: `_store_single_candidate` serialises the whole record, so the key persists with no
  schema change.

**Forbidden after this change**: sorting, hashing or iterating `evidence` keys anywhere in
`organica/`, and any read of `schema_prior_roles` by `organica/`. The field is written for the trace
and for nothing else.

## 4. Neutrality criteria — all four, or the change is reverted

Baseline: `0.13.0` at commit `fd2b053`, 5 seeds × 40 cycles per context, the same world generator the
calibration cell uses.

- **N1 identical structures** — the set of stored ids and the per-type counts are identical, with
  the new keys present only on schema-primed predictions.
- **N2 identical order** — `report.predictions` lists the same ids in the same order, and the
  `schema_prior` value set is unchanged.
- **N3 identical admission** — the number of predictions carrying a prior is unchanged, and no
  prediction exists after the change that did not exist before; the earned-evidence contract
  (`docs/DECISION-EARNED-SCHEMA-PRIMING.md` D1) is untouched.
- **N4 the proof can fail** — a mutant that sorts predictions by `len(evidence["schema_prior_roles"])`
  must make N2 or N3 fail. If the mutant passes, the checks are decoration (rule 25) and the change
  is rejected on that ground alone, before any behavioural reading.

## 5. Trace criteria, on one calibration cell

Seed **20261101**, 40/40 cycles — the seed the first trace measurement already used, and **outside**
CCRE-2's confirmatory block (`20272001-20272024`), so nothing here computes a threshold for the run
it will judge (rule 19). The bar is CCRE-2's P4 bar, **carried**, not fitted here.

- **T1 coverage, exact** — the field is present on **100 %** of schema-primed predictions and on
  **0 %** of the others. A misfire on either side is a defect, not a tolerance.
- **T2 resolution** — under the pair resolver, the share of transfer events resolving to a schema's
  **role pair** is at least **0.90**, and every unresolved event carries a named reason.
- **T3 the instrument still fails when it should** — the always-resolved tracer is still rejected by
  `benchmarks/transfer_provenance.py --self-test`, and the trace's status distribution is not a
  constant across the residual fixtures.
- **T4 durability, which is the only thing this change alone buys** — with the schema row and both
  role rows deleted from a copy of the snapshot, the trace must still name the recorded role pair;
  the pre-change record returns `unresolved_missing_structure` on the same copy. Pass proves the
  record survives pruning; fail means the field is a second copy that dies with the original.

The residual taxonomy the trace must report: **R1** schema row absent, **R2** role rows absent, **R3**
schema row present without role ids.

## 6. Falsifiers and the decision table

| bucket | condition | decision |
|---|---|---|
| `APPLIES` | N1–N4 pass and T1–T4 pass | apply as `0.13.1`, re-record `engine_pin`, Q028 answerable inside CCRE-2 |
| `NEUTRAL_BUT_UNDURABLE` | N1–N3 pass, T4 fails | revert the prediction field, keep only the R3 rebuild repair if that leg passes alone, Q028 stays blocked on the instrument |
| `BEHAVIOUR_CHANGED` | any of N1–N3 fails | revert entirely and record the rejection; the change is behavioural and needs its own cognition decision (rule 2) |
| `COVERAGE_MISFIRE` | T1 is not exact in both directions | revert; a provenance field on a non-primed prediction is a false record and is worse than none |

**Void conditions**: P0 unmet, P1 unmet, or N4's mutant passing. A void cell is reported as void,
never as a failed criterion.

## 7. Stop condition, version and pin

- **Stop condition**: one patch, one test file, one neutrality artifact, one calibration cell. No
  further fields, no statuses beyond R1–R3, no second pass "while we are here". Defects may be
  fixed; features may not be added (rule 23c).
- **Version**: `0.13.0` → `0.13.1` with a changelog entry when applied (rule 10). This document
  changes no version, because it applies nothing.
- **Pin and freeze**: `organica/sleep_extraction.py` and `organica/sleep.py` are not on the frozen
  list, so `tests/test_v1_freeze.py` is unaffected; `benchmarks.engine_pin` is re-recorded at the
  change's commit, and a substrate-equivalence test is required (rule 5).
- **Manual**: an owner row and a revision row in the same turn as the change, naming the residual
  observed and the criteria that passed.

## 8. What this cannot establish

- A recorded role pair is **not** evidence that the organism used a role abstraction (rule 17a): it
  names what licensed the prior at store time.
- It cannot resolve a transfer whose prediction row was never stored — that stays
  `unresolved_missing_structure`.
- It cannot make Q022 move: this is a context variation inside one world family, not cross-domain
  transfer, and Q028's answer does not widen to domains (rule 24b).
- It does not license a transfer claim beyond Q028's answer tier, and it computes no threshold from
  the cell it is judged on.
