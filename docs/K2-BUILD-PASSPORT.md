# K2 Build Passport

**Status:** `FROZEN — NO JUDGED CELL, NO RESULT, NO GRANT`
**Registration:** `CONSTRAINT-K2-1` in
[`constraint_registrations/K2-belief-revision.json`](constraint_registrations/K2-belief-revision.json)
**Freeze date:** 2026-11-17
**Scope:** the K2 build and its dry-run gates only. This passport does not
allocate a seed, cell, lease, grant or result. The one-block run needs a
separate dated owner grant.

This passport is the build contract. It points at the treatment module, the
refusal gates and the exact paths the one authorized block would use. It is
not a result record and it must not be cited as one.

## 1. What is frozen

The K2 hypothesis is *pre-boundary associations retain priority after the
revision boundary, so new evidence cannot displace them*. The intervention is
one variable, applied in process:

| Arm | Wiring | Role |
|---|---|---|
| K2 primary | `K2PreSwitchRetentionService(boundary_cycle=200)` | treatment |
| K1 control | `K2PreSwitchRetentionService(boundary_cycle=None)` | no-op guard |

Both arms use the same class, the same seeds and the same campaign code. The
K1 arm is a guard, not a second K2 experiment.

Fixed parameters:

- boundary cycle: `200`;
- penalty: `0.5`;
- target types: `loop_candidate`, `prediction_candidate`, `hypothesis`;
- no other target type is touched;
- no engine file is edited; the treatment is an in-process subclass, exactly
  as the existing Phase K ablations are.

The treatment tracks pre-boundary association keys in its own instance state
because the frozen engine has no first-seen-cycle field. It records the keys
it observes before cycle 200 and, after the boundary, adjusts only copies of
prior candidates carrying those keys. It never writes memory. If the
pre-boundary age cannot be tracked without an engine change, the build
refuses.

## 2. Files

| Path | Purpose |
|---|---|
| `benchmarks/k2_pre_switch_retention.py` | treatment class, K1 no-op, pure demotion helpers and evidence record |
| `benchmarks/k2_gate.py` | preflight, signature check, validation, decision rule and refusal receipts |
| `benchmarks/k2_block.py` | the one-block runner: dated-grant refusal, one block lease, one attempt marker, the campaign's K1/K2 factories, the gate-shaped result and `validate_result` |
| `tests/test_phase_k_k2_gate.py` | the 16 consolidated rows with passing twins; static/dry-run only |
| `tests/test_phase_k_k2_runner.py` | the runner's grant, gate, lease, marker, resume and reclaim paths; dry-run only, no judged cell |
| `benchmarks/phase_k_campaign.py` | optional `primary_factory` plumbing for `task_k1` and `task_k2`; historical defaults unchanged |
| `docs/phase_k_k2_results.json` | the only result path for the one block; does not exist yet |
| `docs/phase_k_k2_results.ndjson` | the only checkpoint path for the one block |
| `docs/phase_k_k2_block_lease.json` | one block lease covering K1 and K2 |
| `docs/phase_k_k2_attempt.json` | one attempt marker for the block |

`docs/phase_k_results.json` is the historical Phase K result and is never
read, resumed or overwritten by this build. Per-seed leases and per-seed
attempt markers are forbidden.

## 3. Refusal matrix

The consolidated matrix has 9 preflight rows, 4 void rows and 3 audit rows.
Every row has a passing twin in `tests/test_phase_k_k2_gate.py`.

### Preflight (G)

| ID | Condition | Refusal |
|---|---|---|
| G-01 | output destination | frozen path, existing file, symlink or unregistered path |
| G-02 | block identity | wrong seed set, family set, scale other than `1`, or smoke mode |
| G-03 | exclusivity | active block lease, completed attempt, duplicate attempt record or per-seed lease |
| G-04 | arm wiring | missing primary, primary not the treatment, missing K1 no-op, K1 boundary not `None`, or a K1 fixture that is missing, whose fixture hashes differ, whose selection digest differs between the shipped path and the no-op (that digest carries the call's effective argument set, so the argument set is a named detail of the same check, never a separate refusal), whose candidate object is not shared, whose no-op manipulation record is not empty, or which cannot discriminate (nothing would be demoted at the boundary) |
| G-05 | signature | more than one engine override, extra local method, wrong signature, missing `super()` call, forbidden write/engine-constant write, or no pre-boundary tracking source |
| G-06 | freeze | engine pin mismatch, or boundary/penalty/type drift |
| G-07 | determinism | `PYTHONHASHSEED` not `0`, or bootstrap seed not the stable registration-derived seed |
| G-08 | resume | attempt id, arm signature, seed block or checkpoint provenance mismatch |
| G-09 | provenance | baseline gap or K1 pre-intervention value not the registered value |

### Void (V)

| ID | Condition | Gate |
|---|---|---|
| V-01 | no K2 manipulation occurred | `G3_manipulation_occurred` |
| V-02 | demotion happened before the boundary | `G4_no_pre_boundary_demotions` |
| V-03 | a target outside the fixed three types was counted | `G5_target_scope` |
| V-04 | missing or duplicate cell, unsupported label, or engine drift | `G6`, `G7` or `G8` |

### Audit stop (A)

| ID | Condition | Gate |
|---|---|---|
| A-01 | required evidence missing or arithmetically inconsistent | `A1_evidence_complete` |
| A-02 | K1 guard not computable or not a no-op | `A2_k1_guard_computable` |
| A-03 | arm class hash not the frozen treatment | `A3_provenance` |

A `VOID` is not a null result. An `A` stop is `INCONCLUSIVE`, not a pass or a
loss.

## 4. Decision rule

The registration's rule is authoritative:

- **PASS:** K2 paired difference improves by at least `0.10` relative to the
  `-0.5735` baseline gap, and K1's absolute paired difference changes by no
  more than `0.05`.
- **FAIL:** K2 improvement is less than `0.05`, or K1's absolute change is
  more than `0.05`.
- **INCONCLUSIVE:** K2 improvement is between `0.05` and `0.10`, or an audit
  or validity condition fails.

The build must not tune the penalty, target types, seeds or thresholds after
seeing any result.

## 5. What must be true before a block may run

1. The dry-run suite for this passport passes.
2. `benchmarks.test_layers --check` reports no layer violation.
3. `signature_problems(K2PreSwitchRetentionService)` is empty.
4. The K1 no-op fixture compares the shipped K1 path and the no-op arm on the
   same candidates: the fixture digests are identical, both paths receive the
   same candidate object, the two returned selection digests match, the no-op
   records no manipulation, and the same candidates *are* demoted when the
   boundary is live, so the fixture can discriminate. The returned selection
   digest is the digest of that call's effective argument set (defaults
   included), so the argument set is checked as a named detail of the one
   selection-digest check rather than as a condition of its own. A missing
   fixture, differing hashes or a non-empty no-op record is a refusal.
5. A synthetic candidate fixture proves at least one post-boundary demotion
   and zero pre-boundary demotions.
6. The target-type scope is exact.
7. The bootstrap seed is stable across two processes.
8. The output path, block lease, attempt marker and resume guards all refuse
   their forged cases.
9. The engine pin matches; no file under `organica/` has changed.

If any check fails, stop. Do not patch `organica/` to make the treatment
work. Do not open the lease and do not run a seed.

## 6. Run record shape (runner built, no grant)

The one block, if granted, writes exactly one result at
`docs/phase_k_k2_results.json`, one checkpoint at
`docs/phase_k_k2_results.ndjson`, one block lease at
`docs/phase_k_k2_block_lease.json`, and one attempt marker at
`docs/phase_k_k2_attempt.json`. The block covers the ten K2 seeds and the same
ten K1 seeds; no per-seed lease, no smoke run and no extra seed is allowed.
Each seed carries its own `manipulation` evidence. The result is scored by
`k2_gate.validate_result`, not by reading its own label.

`benchmarks/k2_block.py` is the only entry point for that record:

```
PYTHONHASHSEED=0 python benchmarks/k2_block.py --grant docs/K2-BLOCK-GRANT.json
```

It refuses before any file is written unless a dated owner grant exists. The
grant is one JSON object:

| Field | Value |
|---|---|
| `kind` | `k2_block_grant` |
| `grant_id` | the owner's identifier for this block |
| `granted_on` | an ISO date, not in the future |
| `granted_by` | `owner` |
| `authorizes` | `k2-block` |
| `block.families` | `["K1", "K2"]` |
| `block.seeds` | `20261023`-`20261032` |
| `block.cycles` | `300` |
| `block.scale` | `1` |
| `block.workers` | the fixed worker count |

Every other value is refused as `GRANT_BLOCK_MISMATCH`; a missing grant is
`GRANT_MISSING`, an undated one `GRANT_UNDATED` and one dated after the run
`GRANT_NOT_YET_VALID`. After the grant, the gate runs, then exactly one lease is
created exclusively, then exactly one attempt marker. `--resume` continues an
interrupted attempt under the same attempt id, lease and marker; `--reclaim`
closes an `ACTIVE` lease only when it names this attempt and its recorded
process is gone. Neither flag can create a second lease or a second marker.

The checkpoint is read back to assemble the result and to decide what a resume
may keep, so its reader tolerates exactly the two states an append-only writer
can leave without a bug, and nothing else. A partially written **final** row is
dropped and, on resume, truncated back to the last complete row before the
campaign appends past it; a repeated cell is kept as one record, later row
winning, and must agree on its measured fields because the same seed under the
same arm is deterministic. An unreadable or non-cell row before the last line is
`CHECKPOINT_CORRUPT`, and two rows for one cell that disagree are
`CHECKPOINT_DUPLICATE_DISAGREES`: both refuse after preflight and before the
lease, because skipping either would silently drop or silently choose a
completed cell's measurement. The receipt reports the recording's `rows`,
`cells`, `duplicate_rows`, `duplicate_cells` and `partial_final_row`.

The campaign's own `--resume` reads the same recording through the same reader
(`phase_k_campaign.read_checkpoint_report`, which this block delegates to), so
the two consumers of one file cannot disagree about what it holds. A resume
truncates a torn final line before it appends, keeps one row per repeated cell,
and refuses interior corruption or a disagreeing duplicate instead of skipping
it. Only an unparseable final line is tolerated, because a torn write is
exactly a line that does not parse; a complete final row that is not a cell is
`CHECKPOINT_CORRUPT` for both readers.

Phase L's own `--resume` reads its recording through that same reader with its
own key fields (`arm`, `label`, `seed`) and measurement fields (`params`,
`results`), so the reader's rules travel to the other harness rather than being
re-implemented there. It reads the recording on every resume, not only when
falling back, because that run appends to it: a torn tail is cut back before
the next cell is appended, and a corrupt recording refuses either way. Phase L
keeps its documented priority for the records themselves -- the results file
wins when it is readable, and a missing or unreadable one still rebuilds from
the recording.

## 7. What this passport does not authorise

It does not authorise a judged cell, a seed, a grant, a result, a lease, an
engine change, a version bump, a commit, or a retirement of the K2 ledger
row. K2 stays `in-test` until its result and architectural decision exist.
No new constraint row may be added before then.
