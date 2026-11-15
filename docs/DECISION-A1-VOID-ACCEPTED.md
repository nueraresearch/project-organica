# `DECISION-A1-VOID-ACCEPTED` — the A1 block is VOID, and it is not rescored

**Status:** `ADOPTED BY OWNER 2026-11-15 — THE A1 BLOCK IS VOID ON C4; NOT RESCORED; SCORER REPAIR AUTHORISED FOR FUTURE RUNS ONLY`

**Decision ID:** `DECISION-A1-VOID-ACCEPTED-1` · **Date:** 2026-11-15 · **Record:** this document

## The choice

The A1 block ran once under the grant and assembled to **`VOID`** — `VOID gates: C4_no_interference`, reason `C4_DELTA`.
That assembly is accepted as the study's outcome. **It is not rescued, re-scored or re-read.**

1. **The `VOID` stands as the result of the study.** C1 passed; C4 failed on 510 of 2,785 non-target rows against a 0.05
   tolerance, with max K/Y delta 0.575 and no A-path violation. The finding is about the intervention, not the analysis:
   blocking carrier removal for the target edges also removes carriers of non-target edges, because carriers are
   multi-edge paths.
2. **The completed run is not rescored.** The five structural gates (C2, C3, C5, C7, C9) failed because
   `registered_target_map()` built its expected target lists from the representative block rather than the competent one.
   That defect is real and is recorded — and repairing it would change five gate outcomes *after* the cells were seen.
   The repaired scorer is therefore used only for runs authorised after this decision.
3. **The scorer repair is authorised under a disclosed re-pin**, with the pre-repair digests preserved in the run record
   and the repaired digests recorded in `docs/a1_scorer_pin.json`. The repair changes which committed artifact supplies
   the expectation; it changes no threshold, formula, tolerance or gate. The scorer repair is authorised under a
   disclosed re-pin; the pre-repair digests are preserved in the run record.
4. **No effect estimate, C8 assertion or competence claim is reported** from this block, and none may be derived from it
   later by re-assembly. No effect estimate, C8 assertion or competence claim is reported from this block, and none
   may be derived from it by re-assembly.

## The decision in four sentences

The A1 assembly is accepted as the study's outcome: VOID on C4_no_interference, reason C4_DELTA.
The completed run is not rescored; the repaired scorer applies only to runs authorised after this decision.
The scorer repair is authorised under a disclosed re-pin, with the pre-repair digests preserved in the run record.
No effect estimate, C8 assertion or competence claim is reported from this block, and none is derived from it by re-assembly.

## Rejected alternatives

**Fix the scorer and re-assemble the same cells.** It would change five gate outcomes after the cells were seen, which is
the adjustment the pin exists to prevent.

**Relax the C4 tolerance or redefine the non-target denominator.** The interference is 0.575 against 0.05 and sits
entirely in the K-blocked cells; a tolerance that admits it would stop C4 detecting anything.

**Report the C1 pass as a positive result.** C1 passing is a precondition, not the estimand; with C4 VOID the block
cannot adjudicate the effect C1 was protecting.

## What this decision deliberately leaves open

Whether the next effort is to **park A1** as failed under its declared protocol, or to **design A2** with a carrier
intervention that does not collapse neighbouring carrier structure. That is a separate owner decision and is not
pre-empted here.

## Why it is written down

A `VOID` that is quietly followed by a repaired scorer is indistinguishable, in the record, from a `VOID` that was
repaired until it passed. The whole point of the pin, the grant and the gate order is that the inconvenient reading is
the one that survives. This document is what makes "we accepted it" checkable rather than remembered.

## Evidence

- [`A1-RUN`](A1-RUN.md) — what ran, the C1/C4 numbers, the coverage defect and the scorer history
- `docs/a1_two_path_result.json` — the assembly as produced by the pre-repair pinned scorer
- `docs/a1_scorer_pin.json` — the pin before and after the authorised repair
