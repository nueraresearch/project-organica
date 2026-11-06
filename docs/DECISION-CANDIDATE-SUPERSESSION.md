# Decision: candidate supersession — one live copy per identity

**Date:** 2026-11-06
**Status:** implemented; probe predictions recorded below **before** the run.
**Scope:** the candidate reader and the natural-selection prune path. No change to
extraction, to the confidence formula, or to the priming gate.

## 1. The defect

`organica/sleep_selection.py::_load_prior_candidates` returned **every** stored copy of
**every** candidate in the sleep window. That is the whole history of the store: a
candidate that survives is re-written every cycle (reinforced when it re-emerges, decayed
×0.8 under Law VI when it does not), so the window holds an ever-growing set of
generations of the same identity. Reading them as if each row were a candidate has three
consequences, and all three were observed in the 0.12.0 cross-context audit:

1. **Decay was unobservable to the selector.** Priming takes the maximum confidence over
   the loaded prior (`max(valid_schemas, key=confidence)` in `_build_predictions`). The
   oldest copy carries the highest confidence, because decay only ever lowers it, so the
   maximum is always the pre-decay generation. The audit found a schema whose confidence
   stayed at `1.0` through 100 distractor cycles: the copy being decayed was not the copy
   being used.
2. **Pruning was reversible.** When a decayed confidence fell below `DEATH_THRESHOLD`,
   the pass counted a prune and stored nothing. The last copy above the threshold stayed
   in the window, was loaded next cycle, decayed from the *same* value again, and was
   pruned again — forever. The candidate never died; it just stopped producing new rows.
3. **The store grew quadratically in the live set.** Each cycle wrote a decayed copy of
   every historical copy, so a fixed live population of *n* candidates produced O(n·t)
   rows after *t* cycles of absence.

The defect is attributional as well as mechanical: any measurement that counted loaded
candidates was counting *generations stored*, not *identities alive*. Rule 17(a) applies —
the quantity was misnamed at the point of reading.

## 2. Decisions

**D1 — An identity is read once, at its newest generation.** `_load_prior_candidates()`
keeps the first copy it meets per candidate id while walking the window newest-first
(`ORDER BY time DESC, rowid DESC`, so the newest cycle, and within a cycle the newest
write, wins). Older copies of the same id are superseded and are not returned. This
applies uniformly to G1–G8, because the loader is shared by every layer.

**D2 — Death is recorded, not inferred from absence.** When natural selection decays a
candidate below `DEATH_THRESHOLD`, it now stores a **death record** with the same id,
`retired: true`, and the terminal confidence. The loader stops at the newest record for an
id and yields no live candidate when that record is retired. Without this, D1 alone would
freeze every pruned candidate at the last value above the threshold and re-decay it
forever (defect 2 above); the tombstone is what makes pruning stick.

**Retirement is not permanent suppression.** A candidate that is re-extracted in a later
cycle is written after the tombstone and therefore supersedes it. Death is a statement
about the evidence that has stopped arriving, not a blacklist.

**D3 — What is deliberately unchanged.** Extraction, the confidence formula,
`DEATH_FACTOR` (0.8), `DEATH_THRESHOLD` (0.15), `STABLE_THRESHOLD` (0.3), candidate keys,
the rank-only priming contract and the polarity gate. This decision changes only *which
copies are visible* to selection and priming. It does not add, remove, or reweight a
cognitive primitive (AGENTS.md rule 2 is satisfied by recording the change, not by
widening it).

**D4 — Scope of the change.** Every consumer of `_load_prior_candidates` — natural
selection, priming, ancestry, layer inventories and the benchmark harnesses — now sees
identities rather than generations. Measurements that counted rows will move; this
document does not re-read them. In particular the earned-evidence cross-context run
(`e6d1bcc`, `docs/cross_context_reuse_benchmark_earned.json`) was executed on the pre-fix
reader and stands as measured; its "no retention claim" limit is now a statement about
that run, not about the engine.

## 3. Predictions (pre-registered before the probe ran)

The probe (`benchmarks/candidate_supersession_probe.py`) runs one deterministic world, no
random seed: ten cycles form a directional Context-A schema in world A, that schema's
stored record is copied into a **fresh store** whose world never contains A's tags, and
the schema is followed for ten distractor cycles under **both** rules applied to the same
stored rows — the pre-fix rule (maximum confidence over all copies) and the shipped rule
(newest copy per id). Copying the formed record is a fixture, and the artifact records
that the schema is re-extracted in **no** cycle, so absence holds by construction rather
than by inference.

**§3a — design correction, disclosed.** The first attempt instead reversed the flow
inside batches. That did not create absence: with twelve batches per cycle the
batch-boundary A→B transitions alone (11 × 9) kept forward flow dominant over the reverse
flow (12 × 9) once the original forward mass was added, so the schema was re-extracted
every cycle and its live confidence correctly did not decay. The run returned
`SUPERSESSION_NOT_VERIFIED` under a design in which the independent variable never varied —
an unrun manipulation, not evidence against the fix (rules 13a and 22). The predictions
below were not changed; only the manipulation was corrected, and this note is the record
of it.

With the extraction formula `min(0.75, 0.4 + 0.05·min(ratio, 6))` and a contingency ratio
≥ 6, the formation confidence is `c₀ = 0.70`, so the closed form predicts
`⌈ln(0.3/0.70)/ln 0.8⌉ = 4` cycles to fall below `STABLE_THRESHOLD` and
`⌈ln(0.15/0.70)/ln 0.8⌉ = 7` cycles to fall below `DEATH_THRESHOLD`. The engine rounds to
four decimals per step, so each prediction is accepted within **one cycle** of the closed
form.

- **P1 (old rule, same rows):** the maximum confidence over stored copies stays at `c₀`
  for every distractor cycle, and the schema remains priming-eligible (≥ 0.3) throughout.
  *This is the defect; it is predicted to reproduce on the untouched rule.*
- **P2 (shipped rule):** live confidence falls by ×0.8 per cycle, crossing below
  `STABLE_THRESHOLD` at the 4th distractor cycle and below `DEATH_THRESHOLD` at the 7th,
  each within one cycle of the closed form.
- **P3:** once retired, the id is absent from `_load_prior_candidates()` in every
  subsequent cycle, and no further decay copy of it is written.
- **P4 (falsifier):** no prediction reports `schema_prior` for an id whose live
  confidence is below `STABLE_THRESHOLD`. In this world the reverse-direction schema is
  the highest-confidence valid prior, so the A schema would rarely be selected anyway —
  P4 can fire but is unlikely to be exercised. It is stated so that a regression to
  "ineligible priors still apply" cannot pass silently.

**Verdict labels.** `SUPERSESSION_VERIFIED` — P1–P4 met within tolerance.
`SUPERSESSION_PARTIAL` — the loader fixes decay but retirement or eligibility does not
follow. `SUPERSESSION_NOT_VERIFIED` — the live trajectory does not decline.

## 4. Known limits, stated up front

- The probe is **n = 1 and deterministic**. It makes no statistical claim and needs none:
  the trajectory is a closed form, and the quantity under test is a selection rule, not a
  population.
- **The selector still prefers the highest confidence**, and the newest generation is now
  the highest available. A schema that is re-extracted after death restarts at the
  extraction confidence rather than resuming its pre-death value. That is a real behaviour
  change of *resurrection*, and it is the honest one: the evidence that killed the schema
  has decayed away, and the new copy carries only its own evidence.
- **Ancestry can stop at a retired parent** (`found: false`). A dead ancestor is gone from
  the live prior, so a lineage that runs through it terminates there. That is truthful
  under rule 22(b): the parent no longer exists in the organism's state.
- This decision does **not** re-run the cross-context experiment, and does not re-score
  any published result. Whether the corrected reader changes the transfer measurement is
  an open question, listed in the manual's action list rather than answered here.
- `_load_prior_candidates` is a shared entry point used by many harnesses. Their counts
  will move; each is checked by its own test, and this document claims nothing about them
  beyond the fact that they now count identities.

## 5. Probe outcome, and the second mechanism this decision does not remove

The probe has two arms, both deterministic. A **prediction** (G1) and a **schema** (G3)
are each formed by the engine in world A, copied into a fresh store whose world never
contains world A's tags, and followed for ten cycles under both rules.

- The prediction arm behaves as D1/D2 predict: one live copy, ×0.8 per cycle, retired on
the closed-form cycle. The reader fix is what makes this visible — the pre-fix rule keeps
the formation value above `DEATH_THRESHOLD` in every cycle.
- The schema arm does **not** decay, and its live value *rises* by the reinforcement
increment every cycle. The cause is upstream of this decision: the frozen
`organica/sleep.py` re-admits every stable prior G2/G3 structure into the current cycle's
candidate list before natural selection runs (`all_schemas`, `all_metas`,
`all_processes`, `all_roles`, `all_workflows`). Selection therefore sees the schema as
re-emerging every cycle, reinforces it, and never reaches the decay path. The reader can
only display a generation decision that selection never makes.

This is the honest boundary of the fix. D1/D2 are implemented and tested where the engine
does not re-admit a prior (G1). For G2/G3, retention is still blocked, and the blocker is
a line of frozen code: `organica/sleep.py` is frozen under rule 12, and the carry-forward
cannot be changed without the owner's decision.

**Amendment executed (2026-11-06, owner-authorised).** Option (a) was chosen. The five
carry-forward grafts in `organica/sleep.py` now mark the re-admitted object
`carried_forward=True`; `_natural_selection` excludes carried structures from the
current-cycle key set, `_store_candidates` does not re-write them, and the marker is
stripped before storage so no stored record carries it. The structures remain in the
report for downstream layers and telemetry — the graft keeps its purpose — while no longer
counting as evidence. The amendment is recorded in `docs/V1-FREEZE.md` §6, and the re-run
probe now shows both arms decaying by ×0.8 and retiring on their closed-form cycles.

**Measured effect on the frozen engine (2026-11-06).** The amendment is not measurement-neutral:
Gate 13's asserted basis moves from 0.2321 to 0.3036 of the world's 112 edges on the
harness's default seed — the supersession reader alone measures 0.1964 — which is still far
below the 0.50 threshold, so the gate still fires and no acquisition verdict changes. Gate 13
artifacts produced before the amendment are labelled pre-amendment measurements in
`docs/V1-FREEZE.md` §6. Artifact: `docs/candidate_supersession_gate13_effect.json`.
