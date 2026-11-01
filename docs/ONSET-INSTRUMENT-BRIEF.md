# The onset instrument — the first cycle at which the candidate populations differ

> **What this document is.** A plan, committed **before any run**, for the next
> observer in the D0 reproduction line. It is not a finding. Its only commitment
> is that the question, the predictions, the falsification criteria and the
> controls below are fixed here, in this file, before the first measurement.

**Status: PLANNED, NOT BUILT.** Nothing described here has been run. Every
statement about the record cites a committed artifact; every statement about the
engine is a reading of the frozen source at `v0.9.0`.

**Why this instrument and not another correction.** The 2026-11-01 correction
removed the observation the construction-order experiment was pre-registered to
explain: at the divergence cycle the two sides do not hold the same set of
candidates, so there are no identical pools for an in-cycle mechanism to act on.
The question that survives is smaller and is not yet measured — **when do the
pools first differ, and what step introduces the difference?**

---

## 1. The one question

**At the earliest engine cycle at which the campaign-side and current-side
candidate pools differ in membership, and what entered or left between that
cycle and the one before it?**

Not "why do identical pools admit differently" — that question lost its subject
on 2026-11-01. Not "where do the admitted streams first differ" — the
membership audit answers that analytically and `docs/DIVERGENCE-MECHANISM-RESULTS.md`
reproduces it on 8 of 8 seeds.

## 2. What is already known, and what it brackets

From `docs/divergence_cycle_capture.json` (`OBSERVER_VERSION` 3), at engine
cycle *k* = audit index + 1 and at *k−1*:

- **11 of 16 arm-pairs** hold the same set at *k−1* and a different set at *k*.
  For these, the onset lies in the half-open interval **(k−1, k]** — the pools
  first differ at the divergence cycle itself.
- **5 of 16 arm-pairs** already hold a different set at *k−1*. For these the
  onset is **at or before k−1** and is not bracketed by anything measured yet.
- **0 of 16** hold the same set at *k*.

The five unbracketed arm-pairs are T1/20261125 (both arms, k=11),
T2/20261120 (both arms, k=5) and T2/20261121 arm B (k=5). They are the reason
this instrument walks backwards rather than just reading the existing pair.

## 3. The instrument

One observer, one mode of addressing, no engine change.

**Windows.** For each arm-pair, capture the sleep window at every engine cycle
in `1 … k`, newest-first, exactly as the divergence-cycle capture does. The
existing worker already accepts a cycle list (`--cycles`); `capture_cycles()`
returns only the fixed pair `(k, k−1)`, and this instrument generalises it to a
range without changing the addressing rule.

**Addressing is witnessed, never assumed.** The engine stores one `sleep:meta`
event per cycle carrying that cycle's number, and the window is read
newest-first, so the newest marker in the *i*-th window read of an arm must
carry cycle *i*. A window whose marker does not say so is **refused**, and a
refused window is reported as **not measured** — never as an empty pool, and
never allowed to compare equal to an empty pool. This is the rule the 2026-11-01
correction produced; it is inherited unchanged and the instrument fails loudly if
it cannot address a cycle it was asked for.

**Onset rule.** The onset for an arm-pair is the smallest cycle *c* such that the
two pools at *c* differ in membership and the pools at *c−1* are identical. If
the pools differ at *c = 1*, the onset is **at or before cycle 1** and is
reported as such: there is no cycle 0 window, so the instrument cannot bound it
further, and it will not pretend otherwise.

**Transition record.** At the onset cycle the instrument records what entered
and what left (`entered_from_previous_cycle`, `left_since_previous_cycle`), by
candidate ID and type, so the difference is attributable rather than merely
counted.

## 4. Predictions, fixed in advance

**P1 — the bracket holds.** For the 11 arm-pairs bracketed at `(k−1, k]`, the
onset is exactly *k*. The membership change and the admission change are the
same event, one cycle, and the pool does not drift earlier.

**P2 — the unbracketed five are earlier.** For the 5 arm-pairs already divergent
at *k−1*, the onset is strictly less than *k−1*, and the walk-back locates it at
a specific cycle for at least 4 of the 5.

**P3 — the onset is not cycle 1 for most seeds.** More than half the arm-pairs
reach onset at a cycle later than 1, so the divergence is developmental rather
than an artifact of the first cycle's construction order.

## 5. Falsification criteria

**F1 — the instrument disagrees with the corrected capture.** If re-capturing
cycles *k* and *k−1* does not reproduce the `set_identical` values already in
`docs/divergence_cycle_capture.json` on all 16 arm-pairs, the instrument is not
admissible and no onset may be reported from it. This is checked before any
walk-back result is read.

**F2 — the control seed diverges.** On the control seed the two hash-seed runs
must hold identical pools at every cycle. If they do not, the membership
difference is generic to hash-seeded construction and carries no information
about the D0 divergence; the instrument is inadmissible.

**F3 — an unaddressable window is reported as divergence.** If any window used
to place an onset fails its marker check, that arm-pair's onset is reported as
**not measured**. A refused window may never be counted as a differing pool.

**F4 — the onset cannot be attributed to a step.** If the onset cycle's
transition record is empty (no candidate entered or left) while the sets are
reported as differing, the membership comparison and the transition record
disagree; the finding is withdrawn rather than explained.

## 6. Controls

- **C1 — control seed.** Seed `20261101` (T1), both arms, every cycle: pools
  identical in membership, and the onset reported as *none*. A harness that
  cannot pass this has no gauge.
- **C2 — addressing.** Every window used is recorded with the marker it carried
  and the cycle it was used as; the count of `addressed: true` windows must equal
  the count of windows used.
- **C3 — determinism.** The parts are written twice by two independent processes
  at the same hash seeds and compared field by field, with the observer-version
  field set aside, as the divergence-cycle capture already does.
- **C4 — gauge equivalence.** The cycle *k* and *k−1* pools this instrument
  captures must equal the ones in the existing artifact byte-for-byte on IDs, not
  merely on counts.

## 7. What this will and will not establish

**Will.** For each of the 16 arm-pairs (or the subset it can address): the first
cycle at which the candidate populations differ, and which candidates entered
and left at that cycle. That converts "the populations have diverged" into "the
divergence appears here, through these candidates".

**Will not.** It will not identify the *operation* that introduces the
difference. Membership is an output of ingest and of the cycle's writes; a
candidate entering the pool at cycle *c* is evidence that the upstream write
changed at *c*, not that a named function is responsible. Locating the operation
is a separate observer and is not attempted here.

It does not re-score D0, does not change any verdict, does not test H2, does not
reopen the mechanism experiment, and does not change a single engine file.

## 8. Cost and order of work

| Step | Cost |
|---|---|
| Build the range capture and its guards | One benchmark, standard library only, no engine change |
| Run: 8 seeds × 2 hash seeds | 16 runs. Each run captures up to *k* windows instead of two, so expect **longer than the capture's 846 s**; budget 25–35 minutes at 4 workers. Part caches key on the observer version, so a new version regenerates all 16. |
| Verification | F1 and C4 are checked first and must pass before an onset is read |
| Write-up | Journal §75, a manual finding, a facts-sheet row, a CHANGELOG entry, the artifact and its generated report |

Order matters: **F1 and C1 before any onset is reported.** An instrument that
cannot reproduce the measurement it generalises is measuring itself.

## 9. What was read, and how far

Read on 2026-11-01: `docs/divergence_cycle_capture.json` in full (the bracket in
§2 is computed from its `set_identical` fields), `docs/DIVERGENCE-CYCLE-CAPTURE.md`,
journal §72 and §74, `docs/DIVERGENCE-MECHANISM-RESULTS.md`, and
`benchmarks/divergence_cycle_capture.py` (`capture_cycles`, `pool_identity`, the
worker's marker guard and the renderer). No engine file was read for this plan
beyond the `sleep:meta` marker and `ORDER BY time DESC` behaviour already cited
in the capture's own record.

---

→ `docs/divergence_cycle_capture.json`; `docs/DIVERGENCE-CYCLE-CAPTURE.md`;
`benchmarks/divergence_cycle_capture.py`; journal §72; journal §74;
`docs/DIVERGENCE-MECHANISM-RESULTS.md`.
