# Decision — Earned-evidence acquisition and content-sensitive schema priming

**Date**: 2026-11-05
**Status**: RECORDED, EFFECTIVE **BEFORE** THE RUN IT GOVERNS
**Required by**: `AGENTS.md` rule 2 (a cognition change needs an explicit recorded decision)
**Supersedes, for the CCRE only**: the acquisition rule in `benchmarks/cross_context_reuse_benchmark.py` as of `7becdb5`

---

## 1. Trigger

A review of `7becdb5` (the schema-layer refactor) established five facts from the committed
artifact `docs/cross_context_reuse_benchmark.json` and from direct probes of the engine:

- **F1.** `schema_6231f267` — the id produced by `_make_id("schema", "antecedent", "consequent")`
  — is **identical in Context A and Context C**. The id depends on the role *names*, not on the
  role exemplars, so every world in the experiment yields the same schema identity.
- **F2.** The treatment arm and the orthogonal (Context C) arm are **identical on four of five
  seeds**, including `persistence_cycles` (28/23/26/28/29). The whole `TR 3.200` vs `2.286` gap is
  seed `20261102`.
- **F3.** Treatment saturates the endpoint: 1.00 cycle on all five seeds is the **minimum
  attainable value**, so the endpoint cannot register an advantage among priming arms.
- **F4.** Acquisition at cycle 1 is produced by a threshold substitution, not by transfer:
  `sleep_extraction.py` raised a one-transition edge (`count = 1`) past `PREDICTION_MIN_COUNT = 5`
  using `boost = (conf / STABLE_THRESHOLD) * (PREDICTION_MIN_COUNT - 1)`, keyed only on "some
  stable schema exists" and "the edge is asymmetric". No schema content is consulted.
- **F5.** Schema identity collapsing to one key means `_natural_selection` cannot decay one
  context's schema without decaying another's, and `R4` provenance can never terminate in A.

The effect measured by `7becdb5` is therefore **a structural prior** ("this world contains
asymmetric directed transitions; expect one sooner"), not the reuse of the Context A relation.
The owner's instruction is to make acquisition require unboosted evidence, make priming
content-sensitive, and reframe the result accordingly.

---

## 2. What changes (fixed before execution)

**D1 — An edge must earn admission on its own evidence.**
A transition becomes a `PredictionCandidate` **iff** `temporal_count >= PREDICTION_MIN_COUNT`.
No prior, schema, or boost may lower that bar. The `effective_count` field is removed from the
engine: a prediction's count is its observed count.

**D2 — Priming becomes content-sensitive and rank-only.**
A consolidated schema may **reorder** admissible transition candidates; it may never admit one.
Congruence is required on the schema's sender/receiver polarity:

- schema source-role polarity = `sign(out_degree − in_degree)` from the stored
  `source_role_profile`; schema target-role polarity = `sign(in_degree − out_degree)` from
  `target_role_profile`;
- candidate source polarity = `sign(out_flow(u) − in_flow(u))`; candidate target polarity =
  `sign(in_flow(v) − out_flow(v))`;
- congruent **iff** both polarities agree with the schema's **and** neither is zero.

A congruent candidate records `evidence["schema_prior"] = <schema id>` and leads the transition
sort. A non-congruent candidate is unaffected. Because a schema can only reorder, its effect is
measurable in rank and persistence, never in acquisition latency.

**D3 — Schema identity becomes context-bearing.**
`id = _make_id("schema", "antecedent", "consequent", *sorted(source_exemplars),
*sorted(target_exemplars))`, and the natural-selection key becomes
`schema:<source exemplars>-><target exemplars>`. Two contexts can no longer share a schema
identity, so decay and provenance can be resolved per context.

**D4 — The endpoint requires raw evidence.**
`cycles_to_acquire` is the first cycle in which a `B_source → B_target` prediction exists with
`strength >= 0.5` **and** `evidence["temporal_count"] >= PREDICTION_MIN_COUNT`. The harness also
asserts on every cycle that no prediction reports an inflated count; an inflated count is a hard
failure, not a measurement.

**D5 — Diagnostics that must be reported.**
Per arm: `primed_predictions` (predictions carrying `schema_prior`) and the target edge's rank at
acquisition. These distinguish "priming never ran" from "priming ran and bought nothing".

---

## 3. Pre-specified predictions (before the run)

- **P1** — Under D1+D4, treatment is **not** faster than naïve: `TR_treatment <= 1.05`. The v1
  advantage was produced by F4, which D1 removes.
- **P2** — Orthogonal remains indistinguishable from treatment on acquisition: `|TR_ortho −
  TR_treatment| <= 0.05`. This is the same prediction the v1 data already satisfy on 4/5 seeds.
- **P3** — Priming is **active** in treatment (`primed_predictions > 0`) and **absent** in naïve
  and pruned (`= 0`). If P3 fails, D2's gate did not fire and the run is reported as an unrun
  manipulation, not as a null result (`AGENTS.md` rules 13a, 25c).
- **P4** — No prediction in any arm reports an inflated count.

A positive result (`TR_treatment > 1.25` with the orthogonal and pruned arms both below it) would
falsify P1/P2 and is reported as such; it is not excluded by this decision.

---

## 4. Pre-specified verdict labels

| Label | Condition |
|---|---|
| `TRANSFER_DEMONSTRATED_UNDER_EARNED_EVIDENCE` | `TR_t > 1.25` and `TR_t > TR_ortho` and `TR_t > TR_pruned` |
| `STRUCTURAL_PRIOR_PRESENT_NO_ACQUISITION_ADVANTAGE` | `TR_t <= 1.05` and treatment `primed_predictions > 0` |
| `NULL_UNDER_EARNED_EVIDENCE` | otherwise |

The v1 label `REUSE_DEMONSTRATED` is retired. It keyed on a threshold substitution (F4), and its
own discrimination rested on one seed (F2).

---

## 5. Supersession disclosure

`docs/cross_context_reuse_benchmark.json` (committed at `7becdb5`) is **preserved unmodified** as
the v1 record. Its `REUSE_DEMONSTRATED` verdict is reclassified by this decision as
**`STRUCTURAL_PRIOR_AT_THRESHOLD`**: it measured that the presence of any consolidated schema
lowers the evidence bar, not that the Context A relation transferred. The earned-evidence run
writes a **new** artifact, `docs/cross_context_reuse_benchmark_earned.json`, so the two are never
confused. No seed is added or removed: both runs use the pre-assigned block
`20261101–20261105` at 40/40 cycles.

---

## 6. Known limits, disclosed and not fixed here

- The pruned arm still executes `DELETE FROM precedes` **and**
  `DELETE FROM events WHERE event_type = 'sleep'`, i.e. it removes the entire candidate layer, not
  only `S_A`. Its parity with naïve is therefore near-tautological (rule 23b). Fixing it changes
  the arm's meaning and is left to a separate decision.
- `_load_prior_candidates` returns every historical copy of a candidate, so a decayed copy never
  supersedes its own original and consumers take the best-ever confidence. Retention claims based
  on that reader are not measurable until supersession is fixed.
- No p-value is computed; n = 5 with an endpoint that may floor. The preregistered
  `TR > 1.25, p < 0.01, 10 seeds` gate is **not** met by this run and is not claimed to be.
