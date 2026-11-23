# K2 block result — 2026-11-18

**Status:** `RUN 2026-11-18 — VOID (G4_no_pre_boundary_demotions); NO CRITERION READ`
**Grant:** [`K2-BLOCK-GRANT.json`](K2-BLOCK-GRANT.json) — `K2-BLOCK-20261118-A`, dated
2026-11-18, granted by the owner under the frozen passport.
**Attempt:** `k2-block-85a28ee5d26d0536`
**Result:** [`phase_k_k2_results.json`](phase_k_k2_results.json) ·
**Checkpoint:** [`phase_k_k2_results.ndjson`](phase_k_k2_results.ndjson) ·
**Lease:** [`phase_k_k2_block_lease.json`](phase_k_k2_block_lease.json), `CLOSED` ·
**Marker:** [`phase_k_k2_attempt.json`](phase_k_k2_attempt.json), `COMPLETE`

This is the run record. The build contract is
[`K2-BUILD-PASSPORT.md`](K2-BUILD-PASSPORT.md); the result artifact is the JSON above.
A `VOID` is not a null result: it says the block failed its own validity gate, so no
criterion is read and the block is not evidence for or against the K2 hypothesis.

## 1. What ran

One block, 20 cells: the ten K2 seeds and the same ten K1 seeds, 300 cycles at cycle
scale 1, eight workers, `PYTHONHASHSEED=0`.

| Item | Value |
|---|---|
| Families | `K1`, `K2` |
| Seeds | `20261023`–`20261032` |
| Cells | 20 completed, 0 refused |
| Checkpoint | 20 rows, 20 cells, 0 duplicate rows, 0 duplicate cells, 0 partial final row |
| Engine tree | `d4eeefcfabe6a947db7715d3c50b1053d6a4fa4f0eccfa8ad622dbfe13540711` — the pinned 0.15.0 tree |
| Lease / marker | `CLOSED` / `COMPLETE` — one block lease, one attempt marker |
| Gate verdict | `VOID`, failed gate `G4_no_pre_boundary_demotions`, `criteria_read: false`, `confirmed_families: []` |

No engine file changed. The run is the only one the grant authorises; a second block
cannot run under this grant and this attempt.

## 2. Why G4 fired

`K2PreSwitchRetentionService._natural_selection` calls `apply_demotions` on **every**
cycle, including cycles 1–199. `apply_demotions` increments `pre_boundary_demotions`
whenever a prior target-type association is in `_seen_pre_boundary` and the cycle is
before the boundary. During cycles 1–199 the service seeds `_seen_pre_boundary` from
those same prior records, so every prior target qualifies. The observed counters were
**22,007–23,837** pre-boundary demotions per K2 seed, on 10 of 10 K2 seeds.

The pre-boundary branch appends the record **unchanged** (`adjusted.append(record)`), so
no candidate was actually demoted before the boundary; the counter counts the attempt to
demote. `G4_no_pre_boundary_demotions` reads that counter, so G4 fires on every seed. **The
build as frozen cannot return a non-`VOID` result.**

The dry-run suite missed it because the K1 no-op fixture calls `apply_demotions` with
`cycle=200` (the boundary), and the test that proves the counter can fire calls the helper
directly with a pre-boundary cycle. Nothing exercised the service's own cycles 1–199, so
the branch the service always takes was never run in a passing test.

## 3. The K1 guard does not reproduce its registered pre-value

The K1 guard is the block's no-op control. Its registered pre-intervention gap is
`-0.343658`; the ten K1 cells returned **-0.623961**, an absolute change of
**0.280303** against the registration's 0.05 limit.

The no-op class is not the cause. A direct rerun on seed `20261023` of the shipped
`SleepService` and of `K2PreSwitchRetentionService(boundary_cycle=None)` produced the
**identical** 96-pair set and the same F1, **0.315789**. The drift is the engine build.
The Phase K artifact these registered values come from was committed **2026-10-24**,
before the **0.15.0** engine pin (2026-11-11); its K1 Organica score for that seed,
**0.578947**, is not reproducible on HEAD, where the same task scores **0.315789**. The
K2 registration's baseline gap, `-0.5735`, comes from the same pre-0.15.0 artifact and
has the same provenance problem.

`G-09` compares the declared `baseline_gap` and `k1_pre_value` with the registration's
constants; it cannot detect that those constants were measured on a different build. A
K1 comparator that has to detect a non-no-op must come from the same build as the block,
and taking it from the block's own K1 cells would defeat the guard. That is a
registration amendment and an owner decision, not something the block may change after
seeing its result.

## 4. Raw measurements, not a criterion reading

The gate read no criterion. The scores below are recorded so a future same-build
comparison can be made; they are **not** a pass or a fail for `CONSTRAINT-K2-1`.

| Family | n | Organica mean | Best-of-grid baseline mean | Paired gap |
|---|---|---|---|---|
| K1 (no-op) | 10 | 0.312011 | 0.935972 | -0.623961 |
| K2 (treatment) | 10 | 0.176471 | 0.984615 | -0.808144 |

The registered pre-values are `-0.343658` for K1 and `-0.5735` for K2. The K2 gap minus
the registered gap is `-0.234644`, but with a `VOID` verdict that arithmetic is not a
criterion: the comparison is against a pre-0.15.0 measurement and the block's own
validity gate failed.

## 5. What this changes

- K2 remained **`in-test`** when this record was written. The block is not a pass, a fail or
  a null result, and this record reads no criterion. K2 was retired as an invalid attempt on
  2026-11-19 (**untested, not refuted**) under
  [`CONSTRAINT-K2-RETIREMENT.md`](CONSTRAINT-K2-RETIREMENT.md); no second block is authorised.
- No engine file, version, threshold, penalty, target type or seed changed.
- The one block is spent. A second block requires a **repaired build** and a **fresh dated
  grant**.
- The repair has two parts, both owner decisions before a re-run: (a) make the
  pre-boundary path a genuine no-op, or count only actual demotions, so `G4` can pass;
  and (b) replace the K1 comparator with a same-build measurement, which amends the
  registration rather than the run.
- Do not cite this block as evidence for or against the K2 hypothesis. Rule 31: a block
  that fails its own gate is `VOID`, not a failed replication.

## 6. Files

| Path | Role |
|---|---|
| `docs/K2-BLOCK-GRANT.json` | the dated owner grant for this block |
| `docs/phase_k_k2_results.json` | the block result, including the gate verdict and the 20 records |
| `docs/phase_k_k2_results.ndjson` | the append-only checkpoint, 20 rows and 20 cells |
| `docs/phase_k_k2_block_lease.json` | the one block lease, closed |
| `docs/phase_k_k2_attempt.json` | the one attempt marker, complete |
| `docs/K2-BUILD-PASSPORT.md` | the frozen build contract and its post-run status |
