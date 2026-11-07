# Decision — intra-cell exclusion is adopted as an allocation change

**Date**: 2026-11-07
**Status**: RECORDED. The allocation change is licensed; it is **NOT IMPLEMENTED** by this record.
**Decision**: owner.
**Required by**: `AGENTS.md` rule 2 (a cognition change needs an explicit recorded decision) and
rule 30 (a diagnostic is worth its cost only if a named decision follows from its outcome).
**Evidence**: `docs/density_interaction_a2_result.json` (verdict), `docs/density_interaction_a2_run.json`
(the 640 cells), `docs/DENSITY-INTERACTION-A2-PREREGISTRATION.md` (registration and its section 9).

---

## 1. The decision

**Intra-cell exclusion is adopted as an allocation change on the selection layer.** When a fixed
selection budget is spent over a ranked candidate pool, candidate rows whose two tags sit inside the
same world cell are **not eligible** to occupy that budget; the same count ordering is then applied to
the eligible rows. No change is made to the engine, the ordering key, the cap, the scoring window or
any cognitive primitive.

This is the arm the density block measured as `intra_cell_excluded`. The decision adopts the
**allocation rule**, not a claim about the organism.

The artifact's verdict token is quoted in full for honesty about what is being split:

> EXCLUSION PAYS AT SPARSE DENSITY AND GROWS WITH DENSITY

with the artifact's own decision line, "adopt intra-cell exclusion as an allocation change behind a
recorded owner decision; no behavioural claim". **This record adopts the first clause as the
decision and refuses the second as a mechanism claim.** The growth is a descriptive interval that
lies above zero; the pre-registration did not judge it and section 2 explains why it cannot be.

## 2. Scope — what this decision does and does not cover

**It covers** the share of a fixed budget spent on world edges, on this world family, at cap 20, under
both registered exposure schemes.

**It does not cover**, and may not be quoted as covering:

- **Behaviour.** No cell in the block measures prediction, revision, retention, or any downstream
  gain from a better-ranked allocation. The verdict is a selection reading.
- **A density mechanism.** The density slope is **descriptive** and was registered as not judged:
  the dense end is pinned by the pool's composition at 0.150 under both schemes, and the primary
  scheme's middle is **not monotone** (0.059 at 0.1, 0.028 at 0.4, 0.150 at 0.8). The decision does
  not rest on the slope and must not be read as one.
- **Generality.** One world family, sixteen tags in four cells, one vocabulary, cap 20. A different
  candidate space is out of scope until measured.
- **The withdrawn admission rule.** `docs/DECISION-ADMISSION-RULE.md` was withdrawn after its gain
  failed to transfer to the engine's prediction layer. This decision is a different intervention on
  a different layer and does not revive it.
- **A1.** `DENSITY-INTERACTION-1` stays held and unrun; this record does not lift that hold.

## 3. The evidence it rests on

All figures below are generated from `docs/density_interaction_a2_result.json` and re-checked against
it by `tests/test_decision_density_exclusion.py`.

- **Cells:** 640 executed on the sixteen pre-registered seeds with `PYTHONHASHSEED=0`; every gate
  passed (G0 liveness 16 of 16, G1 presence 1.0, G2 arithmetic, G3 axis live, G4 control at the sparse
  end below its ceiling, G5 identity, G6 no coverage loss).
- **Judged criterion C1, the sparse-end level:** mean **0.059375**, 95 percent interval
  **0.040625 to 0.078125**, against the pre-registered bar of **0.05**, with **13 of 16** seeds
  positive. Passed. The bar was calibrated before the run on eight unregistered seeds (992001-992008),
  where the sparse-end mean was 0.094 with a per-seed sd of 0.062, so it is not computed from the
  cells it judges.
- **Exposure check:** the sensitivity scheme reproduces the sparse end at **0.059375**, 11 of 16 seeds
  positive, so the level is not an artifact of the primary exposure scheme.
- **Descriptive slope (not judged):** dense-minus-sparse **0.090625**, interval
  **0.071875 to 0.109375**. Reported because the registration requires it; it is not the reason for
  this decision.
- **The dense end:** 0.150 under both schemes, with the control at 0.850 and the treatment at 1.000.
  That is a property of the pool's composition, not a measured advantage. It is what the verdict
  token's "GROWS WITH DENSITY" clause describes, which is why that clause is reported here and not
  adopted above.

## 4. Why the level and not the slope

The registration fixed the criterion before any cell and the scorer read it once. The slope cannot be
a second criterion here: cap 20 is at or below the world-edge count at every density, and the
treatment removes a class that is never a world edge, so the treated arm is perfect whenever the pool
holds at least 20 world rows. The dense end is therefore pinned, and a criterion there would be
arithmetic rather than evidence. The level is the quantity that could fail, and it did not.

## 5. Implementation status

**No code changed with this record.** The engine is frozen (`docs/V1-FREEZE.md`), and this decision
does not edit it. Turning the allocation rule into a live change is a separate step: it needs its own
implementation record, a behaviour-preserving test in the pattern of
`tests/test_substrate_equivalence.py`, and a statement of what it leaves behind on the engine's own
prediction layer — which is exactly what the withdrawn admission rule got wrong.

## 6. What would reverse this decision

- A rank-sensitive or behavioural endpoint on the engine's own layer in which excluding intra-cell
  rows **loses** against the count-ranked control.
- A different candidate space in which the exclusion is a no-op or is dominated by a cheaper rule.
- Evidence that the sparse-end level was an instrument artifact — for example a replication on fresh
  seeds whose interval contains zero.

Absence of a behavioural gain is not a reversal of an allocation decision; it is the limit already
recorded in section 2.

## 7. Provenance

- Registration: `docs/density_interaction_a2_prereg.json`, rendered at
  `docs/DENSITY-INTERACTION-A2-PREREGISTRATION.md`.
- Cells: `docs/density_interaction_a2_run.json`. Verdict: `docs/density_interaction_a2_result.json`.
- Held predecessor: `docs/DENSITY-INTERACTION-REVIEW.md`.
- Manual: action 38 and section 8.
