# AUTHORISATION — PRESENCE-CONVERSION-1 (authorised 2026-11-10)

**Status: AUTHORISED — RUN.** The block ran on 2026-11-10 and returned **`OBSERVER NOT NEUTRAL`**: the observer-on arm differed from the observer-off arm on every seed, so its own neutrality gate failed. The artifact is `docs/presence_conversion_observer_run.json` and the generated page is `docs/PRESENCE-CONVERSION-OBSERVER-RESULT.md`; the stage table in it is not a conversion result. The owner's grant is recorded below and in `docs/presence_conversion_observer_prereg.json`; it covers all three frozen conversion blocks, Q1, Q2 and Q3.

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

Authorise the **thirteen reading runs** of `PRESENCE-CONVERSION-1` — the record's twelve design cells plus its observer-off witness cell — and the `X7` determinism control, a fresh-process rerun of the first seed's observer-on cell that is a control rather than a reading — on the shipped `0.14.0` engine, at the shipped cap, under gates `X1`–`X8` exactly as frozen, with no engine change, and with no seed, arm, level or criterion added after the first cell.

## The question the run would settle

The record's question, unchanged:

> On the shipped engine at the shipped cap, where do world edges leave the conversion path between raw presence and final assertion — and which observed stage is the first dominant loss, with `C` (constructed candidates), `E` (eligibility reason) and `R` (rank) recorded rather than inferred?

A completed block would settle three things and nothing more:

1. whether `C`, `E` and `R` can be recorded inside a shipped run without changing that run (`X1`), and whether the observer-on arm is the shipped build at all (`X8` reproduces the published audit row);
2. the per-seed retained chain and the first dominant loss among the observed stages, with ties to the earlier stage and a bypass reported separately;
3. the route split between prediction-route assertion (`A_pred`) and assertion that never passed admission (`A_other`).

It would not settle which mechanism is responsible, whether any stage is a defect, whether the cap causes the gap, or whether raising it would help. Those are outside the record and are named as such in its `not_evidence` field.

## The cells, as the record fixes them

| Field | Value |
| --- | --- |
| Engine | `0.14.0`, pin unchanged, no `organica/` edit |
| Arms | observer off (shipped `SleepService`), observer on (`StageObserverSleepService`) |
| Seeds | `20611501`, `20611502`, `20611503`, `20611504`, `20611505`, `20611506` |
| Bootstrap | `20611507`, reserved and not run |
| Witness cell | seed `20261100`, observer off; it must reproduce the published audit row |
| Cycles | `120` per run, the audit's acquisition block |
| Design cells | `12` (two arms × six seeds) |
| Runs authorised | `13` reading runs (twelve design cells plus the witness) and one `X7` control rerun |
| World | the Gate-13 compositional world, warmup and acquisition as in the audit |
| Pairing | same seed, same world, same cap; only the observer differs |
| Cost | `13 × 120` cycles, plus the `120`-cycle control. Wall clock is **not measured**: the record says so and this request does not invent an estimate |

The seeds are fresh — they appear in no other `docs/` artifact, and the record's own check scans for that — and the witness seed is reused only as a control, not as a reading cell.

## What a yes licenses

Only the record's decision table:

| Outcome | What it licenses |
| --- | --- |
| `CONVERSION OBSERVED` | a target for a separate mechanism preregistration, with its own control and withdrawal rule |
| `PARTIAL OBSERVATION` | a narrower target; no loss assigned to an unobserved stage |
| `OBSERVER NOT NEUTRAL` | nothing about conversion; the instrument is fixed and a new block is registered |
| `VOID` | nothing; the block is inadmissible |

Every outcome closes Q3. Only the first produces a target, and even that is not an engine change.

## What the authorisation mechanically requires

1. **This document is the authorisation record.** The owner's words, date and the commit authorised are recorded here; the scope above is the record's own checklist, not something added afterwards. **No commit was authorised**: the worktree is uncommitted at `fb701f4`, so the grant names the working tree rather than a hash that does not exist.
2. **The frozen record is amended, dated.** `authorisation.granted` moves to `true` with `granted_on`, the owner's quote and a pointer to this file. `benchmarks/presence_conversion_observer.authorisation_problems()` now accepts that amendment only when this document exists, no longer describes the block as requested rather than granted, is the document the record names, and contains the quote verbatim; a `true` field with no document, a missing quote, or a document naming another block still fails `--check-prereg` — the `conversion observer prereg` gate.
3. **The runner is installed.** `measure()` now runs the twelve design cells, the witness and the `X7` control as separate processes under `PYTHONHASHSEED=0`, writing one stamped part per cell; `--finish` assembles the artifact and the result page; `--check` recomputes the verdict from the artifact and fails on a stale page. Every entry point refuses while `granted` is false, so the runner's existence does not let a cell run early. The record's protocol, gates and decision table are untouched.

Steps 1 and 2 are now done, and step 3 was already built. The recorded authorisation changes no behaviour and runs nothing until `--measure` is invoked as a separate, dated act.

## What preceded it

The Q3 record derives from the conversion draft (`docs/PRESENCE-ASSERTION-CONVERSION-PREREGISTRATION.md` §5), the same-build audit, the ladder trace and the cap preregistration. **No independent review preceded this request**, and the draft's freeze checklist records the instrument-level proof only: the observer's neutrality comparator is shown to fire on altered arms, but neutrality on real cells is `X1`, which is exactly what the authorised run would measure.

`PRESENCE-CAP-1` remains separately frozen with its own authorisation record. The owner's 2026-11-10 grant covers all three blocks; each still runs only its own cells, under its own gates and its own decision table.

## What would justify declining or narrowing

- **Narrow to Q1 first.** Q1's construct audit is now frozen as `PRESENCE-CONSTRUCT-1` and is separately unauthorised; at the time it had no runner yet. **Superseded later on 2026-11-10:** Q1 now has a runner and its own request, `docs/AUTHORISATION-PRESENCE-CONSTRUCT-1.md`; both blocks are covered by the owner's 2026-11-10 grant. Running Q1 before Q3 is coherent — Q3's stage table does not depend on it, but any later cross-question reading does — and costs Q3 nothing.
- **Prefer the cap block first.** `PRESENCE-CAP-1` already has a runner and twenty-four cells; Q3 does not depend on its result, so ordering it first is a scheduling choice, not a scientific one.
- **Accept that the first result may be an instrument failure.** `OBSERVER NOT NEUTRAL` is a legitimate outcome and the record treats it as one. The owner should authorise the block knowing that the most informative first result could be "the instrument does not work", which spends the cells and settles nothing about conversion.

## What this authorisation does not do

- It does not authorise a mechanism, an engine edit, or any capability, transfer or generalisation claim.
- It does not authorise re-reading the audit, the ladder or the cap preregistration.
- It does not add a seed, arm, level, criterion or analysis after the first cell; the record's stop condition binds.
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
