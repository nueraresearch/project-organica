# AUTHORISATION — PRESENCE-CONSTRUCT-1 (authorised 2026-11-10)

**Status: AUTHORISED — RUN.** The block ran on 2026-11-10 and returned **`CONSTRUCT VALID`**; the artifact is `docs/presence_construct_audit_run.json` and the generated page is `docs/PRESENCE-CONSTRUCT-AUDIT-RESULT.md`. The owner's grant is recorded below and in `docs/presence_construct_audit_prereg.json`; it covers all three frozen conversion blocks, Q1, Q2 and Q3.

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

## The decision requested

Authorise the **six reading cells** of `PRESENCE-CONSTRUCT-1` and the `C8` determinism control — a fresh-process rerun of seed `20261100` that is a control rather than a seventh reading — on the shipped `0.14.0` engine, at the shipped cap of `40`, under gates `C1`–`C9` exactly as frozen, with no engine change, and with no seed, stage, gate or criterion added after the first cell.

## The question the run would settle

The record's question, unchanged:

> On the shipped 0.14.0 engine at the shipped cap, are presence, admitted and asserted measured as comparable quantities on the same world edges, the same build and the same observation window, so that a conversion or cap reading rests on an edge-level measurement rather than on a count difference?

A completed block would settle only these things:

1. whether every asserted world edge is also present (`A_W ⊆ P`), and whether an asserted edge outside presence is an `OBJECT MISMATCH` rather than a conversion result;
2. whether each seed's `W`, `P` and `A_W` reproduce the published audit row, so that the comparison is against the audit and not against a different world;
3. whether the six seeds produce more than one `(P, S_ever, A_W)` fingerprint, and whether the fresh-process control reproduces its seed's stage fingerprints and ordered admission window.

It would not settle whether the cap causes the presence/assertion gap, whether conversion is efficient or defective, which mechanism is responsible, or any capability claim. Those are outside the record and are named as such in its `not_evidence` field.

## The cells, as the record fixes them

| Field | Value |
| --- | --- |
| Engine | `0.14.0`, pin unchanged, no `organica/` edit |
| Treatment | the shipped `organica.sleep.SleepService`; no subclass and no observer |
| Seeds | `20261100`, `20261101`, `20261102`, `20261103`, `20261104`, `20261105` |
| Control | seed `20261100`, fresh-process rerun; a control, not a reading |
| Cells | `6` reading cells plus `1` control rerun |
| Cycles | `120` per cell, the audit's acquisition block |
| Cap | `40`, the shipped cap; no cap level is varied |
| World | the Gate-13 compositional world, 112 derivable edges, warmup and acquisition as in the audit |
| Pairing | one cell per audit seed, compared with that seed's published audit row |
| Cost | `6 × 120` reading cycles and `120` control cycles. Wall clock is **not measured**: the record says so and this request does not invent an estimate |

The seed block is **not fresh**. These are the audit's six historical seeds, reused so that the block can compare against the audit row itself; the record discloses the reuse, makes no freshness claim, and `C9` checks it. A grant authorises the reuse, not a new seed axis.

## What a yes licenses

Only the record's decision table:

| Outcome | What it licenses |
| --- | --- |
| `CONSTRUCT VALID` | the later blocks may treat their per-edge readings as measurements of the same object; no conversion, cap, defect, mechanism or capability claim |
| `OBJECT MISMATCH` | nothing about conversion or capacity; it reports that the quantities are not the same object, and later blocks must not read their stages as same-object measurements |
| `NOT MEASURABLE` | nothing; the empty stage is named and not reported as `0.0` |
| `VOID` | nothing; the block is inadmissible and a fresh block is registered after repair |

Every outcome closes Q1. A pass is a measurement precondition, not a finding about the organism, and it does not authorise Q2 or Q3.

## What the authorisation mechanically requires

1. **This document is the authorisation record.** The owner's words, date and the commit authorised are recorded here; the scope above is the record's own checklist, not something added afterwards. **No commit was authorised**: the worktree is uncommitted at `fb701f4`, so the grant names the working tree rather than a hash that does not exist.
2. **The frozen record is amended, dated.** `authorisation.granted` moves to `true` with `granted_on`, the owner's quote and a pointer to this file. `benchmarks.presence_construct_audit.authorisation_problems()` accepts that amendment only when this document exists, no longer describes the block as requested rather than granted, is the document the record names, and contains the quote verbatim; a `true` field with no document, a missing quote, or a document naming another block still fails `--check-prereg` — the `construct audit prereg` gate.
3. **The runner is installed.** `benchmarks/presence_construct_audit.py` already adds `--measure`, `--cell`, `--finish` and `--check`: `--measure` runs the six reading cells and the `C8` control as separate processes under `PYTHONHASHSEED=0`, writing one stamped part per cell; `--finish` assembles the artifact and the result page; `--check` recomputes the verdict from the artifact and fails on a stale page. Every entry point refuses while `granted` is false, so the runner's existence does not let a cell run early. The record's protocol, gates and decision table are untouched.

Steps 1 and 2 are now done. Step 3 needed nothing further: the runner was built before the grant and every entry point checks the grant itself, so the recorded authorisation changes no behaviour and runs nothing until `--measure` is invoked as a separate, dated act.

## What preceded it

The Q1 record derives from the conversion draft (`docs/PRESENCE-ASSERTION-CONVERSION-PREREGISTRATION.md` §3), the same-build audit and the ladder trace. **No independent review preceded this request.** The audit reports counts only, so the per-edge table this block would produce does not exist yet; the runner reuses the audit's own pipeline rather than introducing a second instrument, which is why `C9` can require each cell to reproduce its audit row.

`PRESENCE-CAP-1` and `PRESENCE-CONVERSION-1` are separately frozen with their own authorisation records. The owner's 2026-11-10 grant covers all three blocks; each still runs only its own cells, under its own gates and its own decision table.

## What would justify declining or narrowing

- **Run Q3 first.** Q3's stage table does not depend on Q1, and it was frozen separately so that observing `C`, `E` and `R` could proceed without a construct pass. Running Q3 first costs Q1 nothing; any later cross-question reading that treats its stages as the same object still needs Q1.
- **Run the cap block first.** `PRESENCE-CAP-1` already has a runner and its own authorisation request. Q1 does not depend on its result, so ordering it first is a scheduling choice rather than a scientific one.
- **Accept that the construct may fail.** `OBJECT MISMATCH` is a legitimate and informative outcome: it would stop later blocks from reading a count difference as a conversion or cap result. The owner should authorise knowing that the most useful first result could be that the endpoints are not the same object.
- **Narrow the block.** The scope may be narrowed before the run — for example to fewer seeds — but a narrowed block is a different block and needs its own record; it may not be widened after the first cell.

## What this authorisation does not do

- It does not authorise a mechanism, an engine edit, or any capability, transfer or generalisation claim.
- It does not authorise re-reading the audit, the ladder or either other frozen block.
- It does not add a seed, stage, gate or criterion after the first cell; the record's stop condition binds.
- It does not estimate a cost it has not measured.
- It does not itself execute a cell: the grant was recorded first and the run followed as a separate, dated act, whose verdict is stated above.

## Signature block — as recorded

| Field | Value |
| --- | --- |
| Decision | authorised |
| Date | 2026-11-10 |
| Commit authorised | none; the working tree at `fb701f4` is uncommitted |
| Words, verbatim | `Authorize all runs` |
| Scope | Q1, Q2 and Q3 — all three frozen conversion blocks — recorded only |
