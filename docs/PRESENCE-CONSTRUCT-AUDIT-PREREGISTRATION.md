# Presence to assertion: the construct audit (PRESENCE-CONSTRUCT-1)

Generated from `docs/presence_construct_audit_prereg.json` by `python -m benchmarks.presence_construct_audit --render-prereg`. Do not edit by hand.

**Status: FROZEN, RUN. Authorised 2026-11-10 and run.** The verdict is `CONSTRUCT VALID`; the artifact is `docs/presence_construct_audit_run.json` and the result page is `docs/PRESENCE-CONSTRUCT-AUDIT-RESULT.md`.

Question 1 of the conversion program (`docs/PRESENCE-ASSERTION-CONVERSION-PREREGISTRATION.md`), frozen on its own. This is Q1 of the draft program, frozen on its own so the program's construct stage is a record rather than a draft. It uses the draft's Q1 quantities, its six audit seeds, its 120-cycle window and its C1-C8 gates without renaming them, and adds C9 so that the reused seeds are checked against the published audit rather than assumed. It does not wait for Q2 or Q3 and it does not use their cells. If Q2 or Q3 later changes a definition, this block is not re-scored; if this block finds the construct unsound, both later blocks must say so in their own records.

## The question

On the shipped 0.14.0 engine at the shipped cap, are presence, admitted and asserted measured as comparable quantities on the same world edges, the same build and the same observation window, so that a conversion or cap reading rests on an edge-level measurement rather than on a count difference?

## The hypothesis, stated before any cell

The published audit reports two endpoints on one build but not the edges between them: it has no per-edge presence, no union of admitted predictions, no surviving admitted set and no bypass. If the quantities are comparable, every asserted world edge is also present, every seed's world and presence are the audit's own, and the six seeds produce more than one stage fingerprint; if they are not, an asserted world edge can be absent from raw presence, which is an object mismatch rather than a conversion result.

**Prediction.** On every seed, `A_W` is a subset of `P`, `P` equals the audit's present count and digest-bearing membership, each cell reproduces its audit row, at least two distinct `(P, S_ever, A_W)` fingerprints appear across the six seeds, and a fresh-process rerun reproduces its seed's stage fingerprints.

**Falsifier.** Any seed on which an asserted world edge is absent from `P`, or on which `P`, `S_ever` or `A_W` has a zero denominator, or on which the cell does not reproduce the published audit row.

**Alternative.** The quantities may be comparable in principle and still collapse in this window — for example if `S_ever` or `A_W` is empty, if all six seeds produce one fingerprint, or if a rerun changes a fingerprint. Those outcomes are reported as `NOT MEASURABLE` or `VOID`, not as a construct pass.

## Why Q1 exists

The published audit (`docs/presence_assertion_audit_0.14.0.json`) is count-only: it reports 112 world edges, 112 present and 34-47 asserted across its six seeds, with no per-edge membership, no `S_ever`, no `S_final`, no `A_pred` and no bypass. Q1 adds that edge-level table on the same build, world and window, and checks that presence, admission and assertion are the same object before either later block reads a conversion or cap result.

## The design

| Field | Value |
| --- | --- |
| Engine | `0.14.0`, pinned, no `organica/` edit |
| Build | recorded on `0.14.0` at cap `40`; superseded by `0.15.0` at cap `112` on 2026-11-11 |
| Treatment | none: the shipped `organica.sleep.SleepService`, no subclass and no observer |
| Seeds | `20261100`, `20261101`, `20261102`, `20261103`, `20261104`, `20261105` |
| Control | seed `20261100`, fresh-process rerun; a control, not a reading |
| Cycles | `120` per cell, the audit's acquisition block |
| Cells | `6` readings plus the control rerun |
| Cap | `40`, the shipped cap; no cap level is varied |
| World | the Gate-13 compositional world (16 tags, 112 derivable edges), 120 cycles covering warmup and acquisition, the same world and window as the published audit |
| Pairing | one cell per audit seed; each cell is paired with its own published audit row, so the comparison is per seed and never pooled |

## The seeds are the audit's, not a fresh block

The six seeds are the published audit's own seeds, not a fresh block. Reuse is deliberate: Q1 asks whether the quantities are comparable on the same build, the same world and the same window as the audit, and a fresh seed block could not be compared with it. This record therefore makes no freshness claim and no claim of a new world axis; C9 turns the reuse into a check rather than a convenience.

## What Q1 measures, and what it does not

| Stage | Meaning |
| --- | --- |
| `W` | the world's derivable edges from the training stream |
| `P` | world edges present in raw temporal memory at the end of the run (`temporal_edges(min_count=1)`), before any cap |
| `S_cycle` | the prediction edges the engine returned from one sleep cycle, read from the `SleepReport` the public API already returns |
| `S_ever` | the union of `S_cycle` over the run; a union, not a retention step |
| `S_final` | the admitted prediction edges still present in the surviving candidate snapshots |
| `A` | the final asserted structure over all six structure types (`structure_edges`) |
| `A_W` | `A` intersected with `W`, the assertion endpoint |
| `A_pred` | `A_W` intersected with `S_ever`: world edges asserted and ever admitted |
| `A_other` | `A_W` minus `S_ever`: world edges asserted without ever being admitted, the bypass |

`C` (constructed), `E` (eligibility reason), `R` (rank) and `U` (readout use) are **not measured** here. They are defined by the draft so that a later record cannot silently collapse them; this block imputes no count for any of them.

## Gates

| Gate | Requirement |
| --- | --- |
| `C1_build` | one build, the exact digest, the pin's `head_at_pin` commit, every module in `docs/engine_pin.json` unchanged; no `organica/` module differs from the pin |
| `C2_world` | one `W` per seed; no perturbation of event order or training window |
| `C3_presence` | `P` is a set, not a count; its digest and per-edge membership are recorded |
| `C4_denominator` | `W`, `P` and `S_ever` are non-empty in every cell; a zero denominator is not measurable |
| `C5_object` | `A_W` is a subset of `P`; a failure is `OBJECT MISMATCH` |
| `C6_witnesses` | at least one positive `A_W` edge and one negative `P` minus `A_W` edge per seed |
| `C7_seed_axis` | at least two distinct `(P, S_ever, A_W)` fingerprints across the six seeds |
| `C8_determinism` | a fresh-process rerun of the declared control seed reproduces its stage fingerprints and its ordered admission window |
| `C9_audit_row_reproduced` | every cell reproduces its published audit row: world edges, present edges, asserted world edges and asserted fingerprint |

**C9 fingerprint basis.** C9 compares the audit's `asserted_fingerprint`, which the harness computes over the whole asserted set of all six structure types (`asserted_pairs`), not over the 40-edge `A_W` subset. Q1 calls `benchmarks.acquisition_harness.asserted_fingerprint`, the same function the audit gate uses, so the rule cannot drift from the audit, and compares `asserted_world_edges` separately, so a cell that fingerprinted only `A_W` would fail C9 rather than pass it. The basis was checked against the harness that produced the audit on 2026-11-10, before any grant.

**Audit-row preflight.** On 2026-11-10, before any cell, Q1 added an audit-row preflight that runs immediately after the record's own validation and before a granted run can launch a cell. It requires the comparator audit to have exactly one row per frozen seed, and every row to carry a lowercase 16-hex `asserted_fingerprint`. A row that is missing the field, carries a non-hex or wrong-length value, or a comparator whose row count differs from the six frozen seeds is REFUSED before `--measure` or `--cell` can run. Tests mutate the comparator's fingerprint and row count independently and prove the grant is refused with no cell attempted. No seed, gate, endpoint, verdict or authorisation changed.

The gates are evaluated in the record's declared order: `C1_build` -> `C8_determinism` -> `C5_object` -> `C4_denominator` -> `C2_world` -> `C3_presence` -> `C6_witnesses` -> `C7_seed_axis` -> `C9_audit_row_reproduced`. The first failure names the verdict; a later gate cannot override it.

## Verdicts

- **VOID**: C1 fails: a cell is built by an engine that is not the pinned build
  - Decision: no reading is made; repair the build and register a fresh block
  - Licences: nothing; a mixed-build cell is inadmissible
- **VOID**: C8 fails: a fresh-process rerun changes a stage fingerprint
  - Decision: no reading is made; repair the instrument and register a fresh block
  - Licences: nothing; a non-deterministic measurement is not a construct result
- **OBJECT MISMATCH**: C5 fails: an asserted world edge is not in `P`
  - Decision: stop the program's construct reading; repair the definition or the measurement and register a new block
  - Licences: nothing about conversion or capacity; it reports that the quantities are not the same object
- **NOT MEASURABLE**: C4 fails: `W`, `P` or `S_ever` has a zero denominator
  - Decision: report the empty stage and make no construct reading; do not report the ratio as 0.0
  - Licences: nothing; the empty stage is named, not smoothed
- **VOID**: C2, C3, C6, C7 or C9 fails
  - Decision: no reading is made; repair the harness and register a fresh block
  - Licences: nothing; a world that moves, a count without membership, a missing witness, a single fingerprint or a cell that does not reproduce its audit row is inadmissible
- **CONSTRUCT VALID**: every C gate passes
  - Decision: publish the per-edge table and let the later blocks read their own stage tables as same-object measurements
  - Licences: the program's construct step only: no conversion, cap, defect, mechanism or capability claim, and no authorisation of Q2 or Q3

## What a pass does and does not buy

Only `CONSTRUCT VALID` licenses anything, and what it licenses is that the later blocks may treat their per-edge readings as measurements of the same object. It does not license an engine change, a mechanism, a defect verdict, a capability claim or a run of Q2 or Q3. No cell in this block edits `organica/`.

**Withdrawal.** A construct reading is withdrawn if a cell stops reproducing its audit row, if the engine pin moves without a version bump, if a rerun changes a stage fingerprint, or if a later block finds `A_W` was not a subset of `P`. A withdrawn reading is recorded, not deleted.

## Runner

**Status: built.** A granted record with a dated authorisation document can run the six cells and the control; without a grant, or with a grant whose document, quote or date is missing, --measure and --cell refuse. A --dry-run mode prints the seven cell commands and target part paths without running a cell or requiring a grant.

## Authorisation

**Record:** `docs/AUTHORISATION-PRESENCE-CONSTRUCT-1.md`.

The draft program's freeze checklist requires the owner's authorisation before a run, and the owner gave it on 2026-11-10: `Authorize all runs`, covering all three frozen conversion blocks. The grant is recorded in `docs/AUTHORISATION-PRESENCE-CONSTRUCT-1.md` and quoted there; the record stays FROZEN, NOT RUN and no cell has run. `--measure` and `--cell` still validate the grant on every invocation. A grant is not a run: executing the first cell is a separate, dated act.

## Stop condition

One block, six audit seeds, one control rerun, one per-edge table, no engine change. When it is analysed, the construct question is closed in one of the four verdicts above. A follow-up may read these cells at a different resolution; it may not add a seed, a stage, a gate or a criterion after the first cell, and it may not re-score the audit, the ladder or either frozen block. Q2 and Q3 remain separate records with their own authorisation.

## What this is not evidence for

This block does not show that the cap causes the presence/assertion gap, that conversion is efficient or defective, or that any mechanism is responsible. It does not measure `C`, `E`, `R` or `U`, and it does not establish a conversion rate beyond these six historical seeds. It may show only whether the endpoints are the same object on the same world, build and window; a `CONSTRUCT VALID` result is a measurement precondition, not a finding about the organism.

## Cost

`6` reading cells and `1` control rerun at `120` cycles each (`840` cycles in total). Wall clock: not measured; the record does not invent an estimate, and the owner should treat the cost as unknown until the first authorised run reports it

The comparator row used above is seed `20261100`: 112 world edges, 112 present, 40 asserted.
