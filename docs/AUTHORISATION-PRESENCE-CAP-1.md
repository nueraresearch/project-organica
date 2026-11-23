# AUTHORISATION — PRESENCE-CAP-1 (authorised 2026-11-10)

**Status: AUTHORISED — RUN.** The block ran on 2026-11-10 and returned **`CAP LIMITING`**: the mean paired gain at cap 112 is 15.83 world edges against the 10-edge bar, the 95% paired lower bound is 8.08, and six of six seeds moved in the predicted direction. The artifact is `docs/presence_cap_run.json` and the generated page is `docs/PRESENCE-CAP-RESULT.md`. The owner's grant is recorded below and in `docs/presence_cap_prereg.json`; it covers all three frozen conversion blocks, Q1, Q2 and Q3.

Q2 had **no authorisation request before this document.** The record was frozen on 2026-11-10 with `granted: false` and no `request` pointer, so there was nothing for the owner to answer. This document therefore records two things at once and keeps them separate: the **scope** of the block, taken from the frozen record's own design, gates and decision table rather than written fresh here; and the **decision** the owner gave on 2026-11-10.

## The decision, as recorded

| Field | Value |
| --- | --- |
| Decision | authorised |
| Given by | the repository owner |
| Date | 2026-11-10 |
| Commit authorised | **none** — the worktree is uncommitted at `fb701f4`. The grant is recorded against the working tree; that limitation is stated rather than papered over with an invented hash. |
| Words, verbatim | `Authorize all runs` |
| Scope | the three frozen conversion blocks — `PRESENCE-CONSTRUCT-1` (Q1), `PRESENCE-CAP-1` (Q2) and `PRESENCE-CONVERSION-1` (Q3) — recorded, not executed |

The words were given after the three records were frozen and before any cell. They authorise the cells each record fixes and nothing wider: not an engine edit, not a mechanism, not a capability claim, and not a re-scoring of an earlier block. **A grant is not a run.** Recorded 2026-11-10 by the agent from the owner's message; the decision is the owner's, the wording of this record is not.

## The question the run would settle

The record's question, unchanged:

> With the world, presence and every non-cap parameter held fixed, does raising only the Layer-1 prediction cap add world edges to the final asserted structure?

A completed block would settle whether the admission budget limits assertion, and at what magnitude. It would not settle whether the presence/assertion gap is a defect, which structure type is responsible, whether conversion is efficient, or any capability claim; those are outside the record and named in its `not_evidence` field.

## The cells, as the record fixes them

| Field | Value |
| --- | --- |
| Engine | `0.14.0`, pin unchanged, no `organica/` edit |
| Treatment | `benchmarks.presence_cap_experiment.CapOnlySleepService`, which overrides `__init__` alone and changes one constant, `MAX_PREDICTIONS` |
| Levels | `40` (shipped control), `80`, `112`, `1000000000` (diagnostic ceiling, not a proposed setting) |
| Seeds | `20611401`–`20611406`; bootstrap `20611407` reserved and not run |
| Cells | `24` reading cells (four levels × six seeds) plus one witness cell |
| Witness | seed `20261100`, cap `40`; it must reproduce the published audit row |
| Cycles | `120` per cell, the audit's acquisition block |
| World | the Gate-13 compositional world, 16 tags, 112 derivable edges |
| Pairing | same seed and world across all four caps; only the cap differs |
| Bar | `10` asserted world edges, twice the audit's between-seed spread |
| Ceiling | `28.5` never-admitted edges per seed, the reach-limited part of the loss |
| Cost | `3,000` cycles, about four minutes sequentially on this machine |

The seeds are fresh: the record's own check scans every other `docs/` artifact for them, and the witness seed is reused only as a control.

## What a yes licenses

Only the record's decision table:

| Outcome | What it licenses |
| --- | --- |
| `CAP LIMITING` | an owner decision to change `MAX_PREDICTIONS`, with its own date and rationale; no adoption and no capability claim |
| `CAP LIMITING BELOW BAR` | nothing for the cap; the gain sits inside the seed spread, so record it and ask why admission converts at a low rate |
| `ADMISSION-ONLY BOTTLENECK` | closing the budget route; the next question is conversion, not capacity |
| `CAP NOT LIMITING` | closing the budget route; the constraint is ranking or consolidation |
| `CAP NOT BINDING` | no scaling reading; the window or the levels are wrong, and the question moves to another constraint |
| `MIXED` | no label; re-register on a fresh seed block rather than re-reading this one |
| `VOID` | nothing; the block is inadmissible and a fresh block is registered after repair |

Only the first licenses anything at all, and even that is a decision for the owner rather than an engine change made by this block.

## What the authorisation mechanically requires

1. **This document is the authorisation record.** The owner's words, the date and the commit authorised are recorded here. **No commit was authorised**: the worktree is uncommitted at `fb701f4`, so the grant names the working tree rather than a hash that does not exist.
2. **The frozen record is amended, dated.** `authorisation.granted` moves to `true` with `granted_on`, `document`, `quote`, `scope` and a `request` pointer to this file. `benchmarks.presence_cap_experiment.authorisation_problems()` accepts that amendment only when this document exists, does not still describe the block as requested rather than granted, is the document the record names, and contains the quote verbatim; a `true` field with no document, a missing quote, or a document naming another block still fails `--check-prereg` — the `presence cap prereg` gate.
3. **The runner already refuses without a grant.** `--measure` and `--finish` check `authorisation.granted` on every invocation, so recording the grant changes no behaviour and runs nothing. The record's protocol, gates, readings and decision table are untouched.

## What preceded it

The Q2 record derives from the conversion draft (`docs/PRESENCE-ASSERTION-CONVERSION-PREREGISTRATION.md` §4), the same-build audit, the ladder trace and the Gate 13 capacity diagnostic. **No independent review preceded this grant**, and no cell has been run. The bar and ceiling are derived from committed artifacts at check time, not typed.

`PRESENCE-CONSTRUCT-1` and `PRESENCE-CONVERSION-1` are separately frozen with their own authorisation records. The owner's 2026-11-10 grant covers all three blocks; each still runs only its own cells, under its own gates and its own decision table.

## What this authorisation does not do

- It does not authorise raising the cap in the engine; a `CAP LIMITING` reading licenses an owner decision, not an edit.
- It does not authorise a mechanism, a defect verdict, or any capability, transfer or generalisation claim.
- It does not authorise re-scoring the audit, the ladder or the Gate 13 capacity diagnostic.
- It does not add a level, a seed or a criterion after the first cell; the record's stop condition binds.
- It does not itself execute a cell: the grant was recorded first and the run followed as a separate, dated act, whose verdict is stated above. A `CAP LIMITING` reading licenses an owner decision, not a cap change made by this block.

## Signature block — as recorded

| Field | Value |
| --- | --- |
| Decision | authorised |
| Date | 2026-11-10 |
| Commit authorised | none; the working tree at `fb701f4` is uncommitted |
| Words, verbatim | `Authorize all runs` |
| Scope | Q1, Q2 and Q3 — all three frozen conversion blocks — recorded only |
