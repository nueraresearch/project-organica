# Pre-registration — store-time role provenance on schema-primed predictions

**Date**: 2026-11-07
**Status**: PREREGISTERED — **NOT APPLIED**. No line of `organica/` changes until the entry
condition below fires, and no cell is run by this document.
**Decision it serves**: `docs/DECISION-STORE-TIME-ROLE-RECORD.md` (option B first; this is A, in reserve).
**Why it exists**: so that if the instrument build leaves a residual the record cannot repair, the
engine change that follows is already fixed — its fields, its neutrality proof, its criteria, its
falsifiers and its stop condition — and cannot be shaped around whatever the re-measurement shows.

---

## 1. Entry condition (all of it, before any edit)

This change is live **only if** the pair resolver has been built and run, and at least one of these
residuals is observed on recorded events:

| id | residual | why the record cannot repair it |
|---|---|---|
| R1 | the schema row named by `schema_prior` is absent from the snapshot | the prior names a structure that no longer exists |
| R2 | the schema row exists with role ids, but the role rows behind them are absent | the ids are sound and the content is gone |
| R3 | the schema row exists but carries no `source_role_id` / `target_role_id` | the `stable_prior` rebuild in `organica/sleep.py:268` copies exemplars and evidence, not the ids |

If none of R1-R3 appears, **this document is retired without an edit** and the engine stays 0.13.0.
The residual observed decides the field: R3 needs the ids recorded at schema build; R1 and R2 need
per-prediction provenance.

## 2. What would be recorded, exactly

For **R3**, at schema build (`organica/sleep_extraction.py:753`): nothing new — the ids are already
set at lines 759-760; the repair is the `stable_prior` rebuild in `organica/sleep.py`, which would
copy `source_role_id` and `target_role_id` alongside the exemplars it already copies.

For **R1 and R2**, on the prediction record, inside the existing congruent branch
(`sleep_extraction.py:476-478`):

- `evidence["schema_prior_roles"]` — the two-element list `[source_role_id, target_role_id]`, copied
  from the schema that licensed this prediction, present **only** when `schema_prior` is present.
- `evidence["schema_prior_role_exemplars"]` — for R2 only: the two sorted exemplar tuples, so a
  pruned role row does not destroy the content the id named.

Nothing else. `schema_prior` is unchanged; no new structure type; no change to `strength`,
`confidence`, admission or ordering.

## 3. Why it can stay inert — the consumers, enumerated

- **Identity**: `_candidate_key` for a prediction is `prediction:<source>|<target>`
  (`sleep_selection.py:265-266`), so a new evidence key cannot merge or split structures.
- **Ranking**: the prediction sort key reads `schema_prior` truthiness, `target_entropy`,
  `transition_prob`, `temporal_count`, `source`, `target` (`sleep_extraction.py:505-512`).
- **Selection and decay**: reads `observations`, `prior_confidence`, `prior_strength`,
  `strengthened`, `decayed_from`, `retired_from`, `closed`, `resolved_by`.
- **Storage**: `_store_single_candidate` serialises the whole record, so the field persists
  without a schema change.

**Forbidden after this change**: sorting, hashing or iterating `evidence` keys anywhere in the
engine, or any read of `schema_prior_roles` by `organica/`. The field is written for the trace and
for nothing else.

## 4. Neutrality criteria — the change is rejected unless all four pass

Baseline: `0.13.0` at commit `654b2cf`, 5 seeds x 40 cycles per context.

- **N1 identical structures**: the set of stored ids and the per-type counts are identical, with the
  new key present only on schema-primed predictions.
- **N2 identical order**: `report.predictions` lists the same ids in the same order, and the
  `schema_prior` value set is unchanged.
- **N3 identical admission**: the number of predictions carrying a prior is unchanged, and no
  prediction exists after the change that did not exist before — the earned-evidence contract
  (`docs/DECISION-EARNED-SCHEMA-PRIMING.md` D1) is untouched.
- **N4 the proof can fail**: a mutant that sorts predictions by `len(evidence["schema_prior_roles"])`
  must make N2 or N3 fail. If the mutant passes, the checks are decoration (rule 25) and the change
  is rejected on that ground alone, before any behavioural reading.

## 5. Trace criteria, on a calibration cell only

Seed **20261101**, 40/40 cycles — the seed the first trace measurement already used, and **not** any
seed in CCRE-2's confirmatory block, so nothing here computes a threshold for the run it will judge.

- **T1 coverage**: the field is present on **100 %** of schema-primed predictions and on **0 %** of
  the others. A misfire on either side is a defect, not a tolerance.
- **T2 resolution**: under the pair resolver, the share of transfer events resolving to a schema and
  its role pair is **at least 0.90**, and every unresolved event carries an R1-R3 reason. The 0.90 is
  the bar CCRE-2 fixed before any cell; it is carried here, not fitted.
- **T3 the instrument still fails when it should**: the always-resolved tracer must still be
  rejected (`benchmarks/transfer_provenance.py --self-test`).

## 6. Falsifiers and the rejection rule

- **Any behavioural difference** (N1-N3) rejects the change: revert, and record the rejection as the
  result — precedent: the decay fix was reverted when its own criterion missed.
- **Coverage that is not exact** rejects the change: a field that appears on non-primed predictions
  is a false provenance record and is worse than none.
- **A residual that persists after the change** rejects it: if events still fail with no named
  reason, the field does not buy the claim and must not be kept as "instrumentation".
- **A trace share below 0.90 with residuals named** is a *result*, not a rejection: it is the
  honest resolution ceiling of this record, and it fails CCRE-2's P4 — which is a protocol outcome,
  not a bug.

## 7. Stop condition, version and pin

- **Stop condition**: one patch, one test file, one neutrality artifact. No further fields, no new
  trace statuses beyond R1-R3, no second pass "while we are here". Defects may be fixed; features
  may not be added.
- **Version**: the engine moves `0.13.0` -> `0.13.1` with a changelog entry; the package version
  describes the commit it is on (rule 10).
- **Pin and freeze**: `organica/sleep_extraction.py` and `organica/sleep.py` are **not** on the
  frozen list, so `tests/test_v1_freeze.py` is unaffected; `benchmarks/engine_pin` must be
  re-recorded at the change's commit, and a substrate-equivalence test is required by rule 5.
- **Manual**: an owner row and a revision row in the same turn, with the residual that authorised
  the change named explicitly.

## 8. What this cannot establish

- A recorded role pair is **not** evidence that the organism used a role abstraction (rule 17a); it
  names what licensed the prior at store time.
- It cannot repair a transfer whose prediction row was never stored — that is
  `unresolved_missing_structure` and stays unresolved.
- It does not license a claim beyond Q028's answer tier, and it does not move Q022.
