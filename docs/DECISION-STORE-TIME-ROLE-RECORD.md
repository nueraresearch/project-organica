# Decision — record the licensing role at store time?

**Date**: 2026-11-07
**Status**: DECIDED — **no engine change yet**. *Amended 2026-11-07 (§9)*: the pre-registered
change is now **scoped as a live engine change under its own pre-registration**
(`docs/STORE-TIME-ROLE-RECORD-PREREGISTRATION.md`), held behind that document's preconditions P0-P1
rather than behind a residual.
**Question**: should `organica/sleep_extraction.py` record, on every schema-primed prediction,
which role licensed the prior — so Q028's trace can resolve a transfer to a role?
**Answer**: not yet, and probably never. The role is already recorded, twice. The zero
the question was asked about is a property of the trace's resolver, not of the engine.

---

## 1. What the record already holds

| what | field | where | what it carries |
|---|---|---|---|
| the schema's antecedent role | `source_role_id` | `organica/candidates.py:153`, set at `sleep_extraction.py:759` | the `RoleCandidate.id` whose exemplars are the antecedent set |
| the schema's consequent role | `target_role_id` | `organica/candidates.py:154`, set at `sleep_extraction.py:760` | the `RoleCandidate.id` whose exemplars are the consequent set |
| the priming link | `evidence["schema_prior"]` | `organica/sleep_extraction.py:477` | the schema id that licensed this prediction |
| the same link, as lineage | `parent_ids[0]` | `organica/sleep_extraction.py:471` | the schema id, ahead of the supporting event ids |
| role content | `exemplars` | stored role rows | the tags the role was built from |

Both paths are stored state, written by the engine at build time and persisted by
`_store_single_candidate` (`sleep_selection.py:445`), which serialises the whole record.

## 2. What the trace demanded, and why that demand cannot be met

`trace_transfer` (`benchmarks/transfer_provenance.py:81`) resolves a transfer through
`role_match(pair, roles)`, which returns the first role whose **exemplars contain both tags**
of the predicted pair (line 94, line 49). If no such role exists, the event is
`unresolved_no_role`.

**A schema relates two roles, and the two sets are disjoint by construction.** The schema id is
`_make_id("schema", "antecedent", "consequent", *sorted(r_a.exemplars), *sorted(r_b.exemplars))`
(`sleep_extraction.py:741`), its parents are `[r_a.id, r_b.id]` (line 747), and its gate is
directional flow **from** set A **to** set B. A pair that a schema licenses is therefore one tag
from A and one tag from B; requiring a single role to contain both is requiring the antecedent and
the consequent to be the same role. Under the schema gate that is contradictory, so the resolver
returns `unresolved_no_role` for every schema-primed transfer **whatever the organism does**.

That is exactly the measured pattern: **14 transfer events, 0 resolved, all `unresolved_no_role`,
0 of 14 prior ids shared with Context A** (`docs/transfer_provenance.json`).

**Consequence for reading the zero.** Rule 13(b) says an unmeasurable quantity is never reported as
zero. This is the same defect one step earlier: a predicate that cannot be satisfied by the
design's own structure was reported as a measured absence of roles. The falsifiable prediction of
this reading is that a resolver following `schema_prior -> schema row -> source_role_id,
target_role_id` will return a **different status distribution** on the same events. Reading the code
is not running it; that prediction is the first check of the build in §5, and if it fails, this
decision is wrong and the reserved change becomes live.

## 3. The three candidate answers

| option | what it costs | what it buys |
|---|---|---|
| **A. Record the role on the prediction now** | an engine edit on the build path, a neutrality proof, a re-pin, a patch version | nothing, while the resolver demands one role for a two-role schema: the new field would be recorded and then ignored by the same unsatisfiable predicate |
| **B. Fix the resolver to follow the schema's role pair** | one instrument change in `benchmarks/`, no engine change, no pin | resolution of the events the record already describes |
| **C. Drop Q028 from the licence** | the answer tier loses a question | removes a claim that cannot be resolved — premature while B is untested and cheap |

## 4. Decision

**B first. No engine change (A), and no withdrawal of Q028 (C).**

1. **The data is already there.** An engine change cannot be justified by a field that exists under
   another name; adding `schema_prior_roles` to the prediction would duplicate `schema_prior`
   plus the schema row.
2. **Instrumentation must not be added to satisfy a broken predicate** (rule 17(c): prefer assembly
   over instrumentation). The failure is in the reader; the writer is faithful.
3. **Cognition changes need a decision, and this change would not even be a cognition change** —
   it would be a provenance field read by nothing. That is the cheapest kind of engine edit and
   still not free: it moves the version, re-pins the engine and needs a neutrality proof. Spending
   that to work around a resolver defect inverts the cost order.

## 5. The build this decision selects, and its stop condition

The build is **B**: a pair resolver in `benchmarks/transfer_provenance.py` that resolves
`schema_prior` to the stored schema row, then to `source_role_id` and `target_role_id`, then to the
stored role rows, and reports the **role pair** — with the same unresolved taxonomy plus the two
residuals named in the reserved pre-registration. It carries **three criteria**:

- **B1 coverage** — every schema-primed transfer in the measurement cell resolves to a schema row or
  reports a named missing structure; no event is dropped from the denominator.
- **B2 the status distribution changes** — the reading in §2 predicts it does. If 14 of 14 remain
  `unresolved_no_role` under a pair resolver, this decision is falsified and the reserved change
  becomes live.
- **B3 the claim is narrowed to what resolves** — if the pair resolves, the claim is *"resolved to the
  schema's role pair"*, not *"resolved to a role"*. Q028's wording and CCRE-2's P4 are then
  **amended by appending a dated row**, never edited in place (rule 14).

**Stop condition**: one resolver, its tests, and one re-measurement on the calibration seed already
used (20261101). No new trace statuses beyond the residual taxonomy. No engine edit in this build.

## 6. When this decision reverses

The reserved pre-registration (`docs/STORE-TIME-ROLE-RECORD-PREREGISTRATION.md`) is **live only if
the pair resolver leaves at least one of these residuals**, each of which the record cannot repair:

- **R1 the schema row is gone.** The schema was pruned before the trace read it, so `schema_prior`
  names nothing. The prediction's own `parent_ids[0]` also names a dead row.
- **R2 the role rows are gone.** The schema survives with role ids, but both role rows were pruned,
  so the exemplars behind the ids are unrecoverable.
- **R3 the schema row lacks role ids.** A schema carried forward or reconstructed without
  `source_role_id` / `target_role_id` — possible through the `stable_prior` rebuild in
  `organica/sleep.py:268-283`, which copies exemplars and evidence but **not** the two role ids.

Residual **R3 is the one worth watching**: it is a real asymmetry in the current record, and if the
pair resolver hits it on live events, the decision reverses — but R3 argues for recording the ids
on the *schema* at build time, not for a new prediction field, so even the reversal is narrower
than the question supposed.

## 7. What this leaves behind

- **No engine change**, no version bump, no re-pin; the engine stays 0.13.0 and frozen files are
  untouched.
- **Q028 stays open**, with a diagnosis instead of a zero: the instrument could not resolve a pair
  that spans two roles.
- **CCRE-2 stays blocked**, but its C7 precondition is now an **instrument build**, not an engine
  decision — the cheaper of the two, and it does not need the owner to authorise a cognition change.
- **A recorded role pair is still not a claim about the organism** (rule 17a): it names what licensed
  the prior at store time, not that the organism used a role abstraction.

## 8. What this decision cannot say

- It does **not** show that the trace resolves — only that the current resolver could not have
  resolved a two-role schema. Code reading is not a measurement, and §2's prediction is the test.
- It does **not** establish that role abstraction is doing work in the transfer. It removes one
  explanation for the zero; it adds no positive evidence.
- It does **not** settle whether the organism should record more. It says the record already holds
  what the question needs, on the paths named in §1.

## 9. Amended 2026-11-07 — the engine change is scoped, and still not applied

The owner authorised scoping option **A as an engine change in its own right** (manual row 58), so
that Q028's trace can name a licensing role without depending on a schema row and two role rows
surviving to the moment the trace reads them. This amends §4's "not yet" and §6's residual trigger;
it does not rewrite them. What changed:

- **The trigger is the authorisation, not a residual.** The change is live behind two preconditions
  in its pre-registration: **P0** the pair resolver exists and its self-test passes (the field must
  have a reader), and **P1** the calibration cell records a non-zero count of schema-primed
  predictions (an empty denominator voids the cell, rule 13a).
- **The residual taxonomy survives as the instrument's failure modes**, not as the entry condition:
  R1 schema row absent, R2 role rows absent, R3 schema row without role ids.
- **Everything that could be fitted is frozen before the edit**: the neutrality criteria N1-N4
  (N4 is a mutation control that must fail), the trace criteria T1-T4, CCRE-2's P4 bar **0.90**
  carried rather than chosen here, and the calibration seed **20261101**, outside CCRE-2's
  confirmatory block `20272001-20272024` (rule 19).
- **T4 is the only thing this change buys that the instrument cannot**: with the schema row and both
  role rows deleted from a copy of the snapshot, the trace must still name the recorded pair. Without
  T4 the field would be a second copy that dies with the original.
- **Nothing is applied.** The engine stays `0.13.0`; applying the change would move it to `0.13.1`,
  re-record `engine_pin` and require a substrate-equivalence test (rule 5).
- **The scope is guarded mechanically**: `benchmarks/store_time_role_prereg.py --check` fails if the
  document is un-scoped, if the bar or the confirmatory block moves, if a criterion loses its
  control, if two decision buckets reach one decision, or if the engine carries
  `schema_prior_roles` while the scope block still says `applied: false`.

This amendment adds no evidence and answers nothing: Q028 stays **open**, and CCRE-2's C7 stays
blocked until the change is applied and its criteria pass.

