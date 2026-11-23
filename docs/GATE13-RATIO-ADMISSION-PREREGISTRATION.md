# Gate 13 pre-registration — the `ratio` admission arm

**Status: AUTHORISED AND RUN (2026-11-06).** Results: §8.6 of `docs/GATE13-PAIRED-CAPACITY-TEST.md`, artifact `docs/gate13_ratio_arm.json`; readings in Amendment 2 below. The status line below is kept as written before the authorisation. Nothing under `organica/` is
touched by this document or by the arm it describes. The arm would live in `benchmarks/` as an in-process
subclass, the pattern `PairedDiagnosticSleepService` already uses, and `tests/test_v1_freeze.py` would
continue to hold every frozen file byte-identical. Changing which structures win admission is a frozen
cognitive primitive (AGENTS.md rule 2), so the decision to run this is the owner's, and this document is the
thing to authorise or reject.

## 1. What is being tested, and why it is worth one experiment rather than a search

Three measurements from 2026-11-06 narrow the question.

1. **The candidate population is complete.** With the cap removed it is 240 vocabulary
   rows containing all 112 world edges (coverage ceiling 1.0000) — base rate
   0.4667. `docs/GATE13-PAIRED-CAPACITY-TEST.md` §8.4.
2. **The current admission rule is at chance, and below it at the top.** Pooled top-20 under `count` is
   20 of 100 rows against 46.67 expected (-5.35 SE), and
   `temporal_count` is degenerate: 192 of 240 rows
   (80%) share one value. §8.4–§8.5.
3. **One computable ordering beats the base rate, and the engine already stores it.** `ratio =
   count / source_freq` takes 39–48 distinct values against 9–14 for count, and its
   top-20 density is 0.5000–0.6000 against 0.4667 — pooled 1.47 SE, directional only. §8.5.

The hypothesis is therefore narrow: **does sorting admission by the field the engine already computes change
the asserted set, and in which direction?** The cap-20 baseline it would be compared against is coverage
0.5357 with 134 asserted edges and precision 0.4576.

## 2. Arms

| arm | admission ordering | everything else |
|---|---|---|
| **C** (control) | `temporal_count` — today's rule | frozen |
| **R** (treatment) | `ratio = count / max(source_freq, 1)` | identical to C in every other respect |

Implementation is a `benchmarks/` subclass overriding the sort key in `_build_predictions` only; no frozen
file is edited. `PYTHONHASHSEED=0` is pinned in **both** arms, because the count column's ties make the
control arm's small-cap behaviour hash-order dependent (§8). Primary cap 20 (the registered operating
point); secondary caps 20 / 100 / 1,000.

## 3. Frozen metrics

- **M1 asserted coverage** — world edges in the final asserted set ÷ 112 (the Gate 13 basis).
- **M2 asserted precision**, reported beside its chance baseline (asserted set size × 0.4667).
- **M3 marginal precision** — Δworld edges ÷ Δasserted edges between cap 20 and cap 1,000.
- **M4 tie diagnostics**, measured **per arm on that arm's own final pool**: distinct score values, modal
  tie share, top-20/40/80 density against that arm's own base rate.
- **M5 asserted-set size.**

## 4. Seeds

Development seeds: 20261101, 20261102, 20261103, 20261104, 20261105 — already used throughout this record
and therefore always diagnostic. Each seed is paired across arms; no substitution, and no seed may be added
after a result is seen. The confirmatory block 20261106–20261130 stays untouched and is not used by this arm
without a separate authorisation.

## 5. Predictions, frozen before the run

- **P1 — the control is at chance.** |M2 − chance baseline| ≤ 0.05 coverage at cap 20, on ≥ 4 of 5 seeds.
- **P2 — R breaks the tie.** R's distinct score values ≥ 3× C's on its own final pool, on ≥ 4 of 5 seeds.
- **P3 — the directional hypothesis.** R's paired M1 exceeds C's at cap 20 on ≥ 4 of 5 seeds.
- **P4 — precision guard.** If P3 holds, precision at fixed asserted size must not fall by more than 0.02.
  If it does, coverage was bought with noise and the arm does not establish an admission bottleneck.

## 6. Outcome table, fixed now

| result | reading |
|---|---|
| P2 passes, P3 fails | a signal exists and is not operationally useful; admission is not the binding constraint at this cap |
| P3 passes, P4 passes | admission is a binding constraint and capacity is downstream (§8.2–§8.3) |
| P3 passes, P4 fails | coverage bought by asserting more noise — a trade, not a gain |
| P2 fails | the tie is not the mechanism; the §8.5 reading is wrong and must be withdrawn |

## 7. Confounds and limits, disclosed before the run

- **Hash order.** Pinned in both arms and reported; without the pin the control is not reproducible (§8).
- **The count-10 saturation** means the control arm is not a stable comparator at small caps (§8.4).
- **Each arm's pool must be re-measured on its own final table.** Reusing the control arm's pool for R would
  confound the arm with the pool; §8.4's numbers are the cap-1,000 arm only.
- 4–6 asserted edges at cap 1,000 are absent from the final `precedes` table (§8.4).
- One 2-tag compositional world family, five seeds, no confirmatory sample.
- **Cost estimate:** 30 cells (2 arms × 5 seeds × 3 caps) at the measured median 8.5 s per cell
  ≈ 4.2 min, from the runtime recorded in `docs/gate13_cap_curve_by_build.json`.

## 8. What this does not establish, whatever it finds

It cannot show that the ranking is good: `ratio` is one of six candidates and the only one above base, at
1.47 SE. It cannot generalise beyond this world family, this cap range or these five seeds. And it cannot
license an engine change on its own — a positive result is a reason to write a confirmatory block, not to
alter a frozen primitive.

Artifacts this builds on: `docs/gate13_candidate_pool_density.json`, `docs/gate13_tiebreak_tests.json`,
`docs/gate13_cap_curve_by_build.json`.

## Amendment 1 (2026-11-06, recorded before any cell ran) — arm C is not the engine's rule

Implementing the arm required reading `organica/sleep_extraction.py::_build_predictions`, and it showed
that today's admission rule for **transitions** is not raw count. It sorts by *target entropy ascending*,
then transition probability descending, then count, and then allocates half the cap to transitions and the
rest to co-occurrences. Raw-count ordering is the rule inside
`benchmarks/run_paired_capacity_test.py::PairedDiagnosticSleepService` — the harness every §5–§8 figure of
`docs/GATE13-PAIRED-CAPACITY-TEST.md` was measured under.

Three consequences, recorded before the first cell:

1. **The sentence "the admission rule sorts by count" is true of the harness, not of the engine.** §8.4 and
   §8.5 are corrected to say so, and the correction is disclosed rather than folded into the results.
2. **C stays exactly as registered** — the count-sorted harness rule — because it is the rule the existing
   record's numbers come from, and redefining the control after seeing the question would make the
   comparison incomparable with §5–§8. P1–P4 are scored on C vs R as §5 states.
3. **A third condition E is added as a reference, not as a registered comparison:** `SleepService` with
   `MAX_PREDICTIONS` set to the cap, i.e. the engine's own rule at the same budget. E is reported beside C
   and R and is not used to score any prediction; it exists so the record can say whether the registered
   comparison is measuring the engine or only the harness.

## Amendment 2 (2026-11-06) — the run, its readings, and one discarded instrument

The owner authorised the arm in the terms of §1–§7. All predictions were scored as frozen;
**P1 passes (4 of 5), P2 passes (5 of 5), P3 passes (5 of 5), P4 passes.** At cap 20 R's coverage exceeds
C's on every seed (paired deltas 0.0536 to 0.0804), and paired precision moves by -0.0031 to
0.0313. The outcome table's third row therefore applies: *admission is a binding constraint and capacity is
downstream*. Full record with the per-seed table: §8.6 of `docs/GATE13-PAIRED-CAPACITY-TEST.md`.

**Disclosure — a discarded instrument.** The first R instantiation re-sorted the parent's already-truncated
list, so seven R cells reproduced C exactly; they were dropped before any result was read, the subclass was
corrected, and no registered quantity changed. **Disclosure — a cell plan wider than §2.** P4 as written needs a
size-matched comparison, which the registered caps cannot supply because R's cap-20 asserted set is already
larger than C's; cap 10 was therefore run for C and R only, and its cells are used for that comparison and for
nothing else. E is the Amendment 1 reference and scores no prediction.

**What this does not change.** No frozen file, no seed outside 20261101–20261105, and no claim from §8. A
positive reading is an argument for a confirmatory block, not for editing `_build_predictions`.
