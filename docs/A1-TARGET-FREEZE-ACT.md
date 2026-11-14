# A1 Path A target-freeze act — draft

**ID:** `A1-TARGET-FREEZE-1`

**Date:** 2026-11-14

**Status:** `DRAFT — AWAITING OWNER SIGNATURE; NOT FROZEN; NO GRANT, NO RUN`

**Decision owner:** ____________________

**Signature and date:** ____________________

**This is a prepared act, not an executed freeze.** The live manifest is still `REGISTERED DESIGN — NOT FROZEN, NOT RUN, NO GRANT`, its target block is still `UNRESOLVED — MUST BE FIXED BEFORE FREEZE`, and no seed is reserved. Signing and dating this act would perform the target freeze described below. It would not issue a grant, run a cell or observe C1/C4.

## 1. What would be frozen

The act freezes **Path A** for the registered A1 attempt:

> the representative eligible pre-37 cycle-membership directed-edge effect.

It freezes the six existing target sets in [`a1_target_selection.json`](a1_target_selection.json), using the exact strings below. It does **not** regenerate targets, re-run the selector, or permit post-outcome re-selection. Path B remains unselected and is a future experiment.

The act also fixes the manifest target block and the six-seed block as the object of the attempt. It leaves `authorisation.granted` false: the execution gate still refuses before a database is opened.

**Separate C8 expansion design.** [`A1-C8-EXPANSION.md`](A1-C8-EXPANSION.md) registers `A1-C8-EXPANSION-1`, a 20-target-per-seed design with a 0.05 C8 step. This act does **not** freeze or adopt it, does not replace the four-target table below and cannot use its rows. Signing this act would still leave C8 under-resolved by the frozen N=4 block, so the executed act must carry `C8: NOT ADJUDICATED BY DESIGN`. Adopting the N=20 design requires a separate target-freeze act naming it; the prepared draft is [`A1-TARGET-FREEZE-N20-1`](A1-TARGET-FREEZE-ACT-N20.md); its C5 target-timing precondition is cleared by the cycle-4 earlier-`U` audit.

## 2. Exact target sets

| Seed | Targets | Candidates | Eligible | Selection digest |
| ---: | --- | ---: | ---: | --- |
| `20630101` | `verdant>sable`, `olive>cedar`, `fern>willow`, `yarrow>amber` | 64 | 64 | `a5961be73fd6609e` |
| `20630102` | `umber>ochre`, `verdant>teal`, `indigo>sable`, `slate>birch` | 63 | 63 | `f1ac206b15439743` |
| `20630103` | `teal>willow`, `amber>verdant`, `fern>maple`, `olive>indigo` | 64 | 64 | `e820c5ed006f1a74` |
| `20630104` | `indigo>ochre`, `teal>fern`, `willow>olive`, `birch>verdant` | 64 | 64 | `09f071131ba3c16e` |
| `20630105` | `cedar>olive`, `indigo>teal`, `verdant>maple`, `ochre>fern` | 64 | 64 | `8636d029063c254d` |
| `20630106` | `sable>maple`, `teal>umber`, `cedar>olive`, `amber>crimson` | 63 | 63 | `179290a10fc74203` |

**Target observations:** 24. **Unique target edges:** 23. The repeated edge is intentional; the unit of assignment is the seed, and each seed carries its own four-edge set.

**Selection artifact digest (SHA-256):** `c8f96ff1888d5b9ae175950cb963e16b779a8caa5ebfa73e4b425fba7bec4f5a`

## 3. Effect of signature

Signing and dating this act would, in the freeze record:

- set the manifest target block to `FIXED BEFORE FREEZE`;
- store the exact `by_seed` mapping above;
- set the manifest `frozen` flag to `true`;
- reserve the six candidate seeds as the fixed seed block;
- leave `authorisation.granted: false` and `granted_on: null`;
- leave the result absent and C1/C4 unobserved.

The act does **not**:

- issue a grant;
- open a database or run a cell;
- produce a C1 or C4 denominator;
- create a result, model label or claim;
- adopt the owner memo or the C1/C4 gate order;
- allow a second attempt or a target re-selection.

## 4. Preconditions

The act may be signed only while all of the following remain true:

| Precondition | State |
| --- | --- |
| P0 protocol compliance | **PASS** |
| Six target sets formed | **PASS** |
| Four disjoint targets per seed | **PASS** |
| Target edges in the pre-37 universe | **PASS** |
| Earlier `U` measured before carrier, K and Y | **PASS** — fixed cycle-4 `U`; earliest current carrier cycle 5 ([audit](A1-C5-TARGET-TIMING.md)) |
| Selection artifact internally consistent | **PASS** |
| Path A recorded as the estimand | **PASS** |
| C1 acceptance rule | **RECORDED — BINDING FOR A1** |
| C1/C4 gate order and 60-row floor | **ADOPTED — BINDING FOR A1 (2026-11-14)** |
| C7/C8 denominator unit | **ADOPTED — C7 PER-EDGE RATE; C8 UNDER-RESOLVED BY THIS N=4 ACT; N=20 DESIGN REGISTERED BUT NOT ADOPTED** |
| Grant | **NOT ISSUED** |
| Run | **NOT STARTED** |

The freeze does not wait for C1/C4. Those are post-freeze validity gates, already **ADOPTED — BINDING FOR A1** in [`A1-C1-C4-VOID-GATE.md`](A1-C1-C4-VOID-GATE.md). Signing this act does not resolve or re-open the C1/C4 ordering; it only fixes target identity. The provisional-freeze wrapper remains a separate draft.

The C7/C8 unit is also already decided: both gates are **per seed**, and pooled rows are rejected in [`A1-C7-C8-DENOMINATOR.md`](A1-C7-C8-DENOMINATOR.md). C7 is rate-resolved at 1/120 = 0.008333 because its 0.05 margin is an A/K rate over 120 cycles per edge; C8 is a per-target row rate and the current N=4 block cannot resolve its 0.05 ceiling. This act therefore cannot claim that the frozen design can adjudicate C8; the registered N=20 design is a separate, unfrozen record and is not used here. If this act is signed, it must carry the explicit limitation **`C8: NOT ADJUDICATED BY DESIGN`**, and that limitation must appear before any result. C7 remains an unrun gate. It does not relax either gate, change either threshold or authorise a run.

## 5. What does not change

- The live manifest remains **NOT FROZEN** until this act is signed and the change is applied.
- The target artifact remains **DRAFT, NOT FROZEN, NOT A RESULT** until the act records its use.
- The six candidate seeds remain **PROVISIONAL CANDIDATES** until the act reserves them.
- No target is re-selected, regenerated or altered.
- No cell is authorised.
- The 60-row denominator floor and the C1/C4 post-freeze VOID gate are **ADOPTED — BINDING FOR A1**.
- C7/C8 classification remains unmeasured. C7 is rate-resolved but unrun; C8 is under-resolved by the current N=4 block. The separate N=20 design is registered but not adopted or frozen. A signed freeze must record **`C8: NOT ADJUDICATED BY DESIGN`** unless a revised act adopts the N=20 design first.

## 6. After signature

The next governance acts are separate:

1. **Grant:** record the dated run-authorising grant in the manifest, with its document and quote.
2. **Run:** execute only the planned cells.
3. **Measure:** assemble C1/C4 and read `PASS` or `VOID`.

Until step 1, the execution gate must refuse. Until step 2, there are no cell parts and no observed C1/C4.

## 7. Checks

- `python -m benchmarks.a1_target_selection --check`
- `python -m benchmarks.a1_c8_target_selection --check`
- `python -m benchmarks.a1_adversarial_audit --check`
- `python -m benchmarks.a1_two_path --check`
- `python -m benchmarks.a1_two_path --self-test`

The target-set check for this act was run against the artifact with the manifest target status set to `FIXED BEFORE FREEZE`; it returned no problems. No cell or database was opened.

**Not evidence:** A prepared freeze act. It freezes nothing until signed, issues no grant, runs no cell and makes no causal, capability or transfer claim.
