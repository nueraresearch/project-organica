# A1 pre-freeze checklist

**ID:** `A1-PRE-FREEZE-CHECKLIST-1`  
**Date:** 2026-11-14  
**Status:** `P0 PASS — FREEZE READINESS OPEN (PASS: NO); TARGET FREEZE NOT AUTHORISED; RUN NOT AUTHORISED`

**Formal compliance record:** [`A1-PROTOCOL-COMPLIANCE-REPORT.md`](A1-PROTOCOL-COMPLIANCE-REPORT.md). Power/prevalence evidence: [`A1-POWER-REVIEW.md`](A1-POWER-REVIEW.md).

**This is a compliance record, not a target freeze, a grant or a result.** The six
target sets are a feasibility artifact. They are not fixed experimental targets
until the manifest is frozen by a separate act.

## Must pass before freeze

| Check | Result | Evidence |
| --- | --- | --- |
| Cycle-36 `U` sampled before the sleep call | **PASS** | `a1_arms.run_cell`; `tests/test_a1_prefreeze.py::test_cycle_36_u_is_sampled_before_consolidation`; [audit](A1-ADVERSARIAL-AUDIT.md) P0 |
| Candidate universe restricted to the first 36 acquisition cycles | **PASS** | [selection implementation](../benchmarks/a1_target_selection.py); P0 pre-37 check |
| Future-blindness: 36-cycle vs 120-cycle world | **PASS** | [audit](A1-ADVERSARIAL-AUDIT.md) |
| Report-blindness | **PASS** | [audit](A1-ADVERSARIAL-AUDIT.md) |
| Sleep-blindness | **PASS** | [audit](A1-ADVERSARIAL-AUDIT.md) |
| Determinism | **PASS** | [audit](A1-ADVERSARIAL-AUDIT.md) |
| Six-seed feasibility: four disjoint targets per seed | **PASS** | [selection artifact](a1_target_selection.json); [audit](A1-ADVERSARIAL-AUDIT.md) |
| Selection artifact generated | **PASS** | [artifact](a1_target_selection.json); 24 selected edges |
| Selection digest stable | **PASS** | `selection_digest` checked against contents; independent determinism pass in the audit |

The audit's P0 block records all six protocol-compliance conditions as passing, and the audit now records the selection-representativeness measurement beside them.

## Selection representativeness

**Measurement (2026-11-14).**

| Measurement | Result |
| --- | ---: |
| Selected target observations | **24** |
| Unique target edges | **23** |
| Unselected candidates | **358** |
| Candidates | **382** |
| All candidates eligible | **yes** |
| Selected mean strength | **15.333** |
| Unselected mean strength | **15.215** |
| Selected median strength | **16** |
| Unselected median strength | **16** |
| Descriptive permutation p | **0.918** |

**Estimand:** a **representative eligible pre-37 cycle-membership directed-edge population**.

**Conclusion:** the selected targets are a representative eligible pre-37 sample; A1 does not estimate a high-`U`, hard-edge or carrier-enriched effect. The permutation p-value is descriptive; failure to reject a difference is not an equivalence test. The design fact is that every candidate is eligible and the hash order ignores `U`.

If a high-propensity estimand is required, the selector must be redesigned before freeze. This is a design statement, not a result and not a P0 condition.
`a1_target_selection --check` and `a1_adversarial_audit --check` are the
machine checks for the artifact and its page.

## Not yet complete

| Item | State | Consequence |
| --- | --- | --- |
| Power/prevalence review for `N = 4` | **DONE — FREEZE READINESS OPEN** | [`A1-POWER-REVIEW.md`](A1-POWER-REVIEW.md) finds C1 denominator fragility: four target rows make the 0.95 floor effectively 100%; C4 planning raises this to 63–64 C1 rows per seed (59–60 non-target plus four target rows; 3 allowed losses), but no denominator has been observed. |
| C1 power curve | **RECORDED — REFERENCE ONLY** | [`A1-POWER-REVIEW.md`](A1-POWER-REVIEW.md) reports C1 pass probabilities at assumed retention `.95`, `.97`, `.98` and `1.00` for denominators `4, 20, 56, 59, 60, 63, 64`. At `q=.95, n=63`, one arm passes at **0.613**, one seed at **0.376**, all six seeds at **0.003**; at `q=.98`, all six pass at **0.632**. These are assumptions, not measurements. |
| Denominator-resolution audit | **FLAGGED — 3 SCENARIOS** | [`A1-DENOMINATOR-RESOLUTION.md`](A1-DENOMINATOR-RESOLUTION.md): C1 target-only fallback (1/4 = 0.25), C7 (1/8 = 0.125) and C8 (1/4 = 0.25) are finer than their margins; expanded C1 (1/63 ≈ 0.016) and C4 (1/59 ≈ 0.017) are not. This is a planned-denominator audit, not a measurement. |
| C4 gate order | **POST-FREEZE VOID GATE (2026-11-14)** | C4 is not a pre-freeze admissibility gate. Freeze targets, grant the run, then assemble C1/C4; a C4 failure or unmeasurable non-target stream makes the run **VOID**. This decision does not freeze, reserve a seed, grant or run. [`A1-C4-GATE-ORDER.md`](A1-C4-GATE-ORDER.md). |
| C4 non-target neighbour rows | **IMPLEMENTED — NOT RUN** | A1 cell output now emits `neighbor_rows` for every non-target edge, with A/K/Y availability rates; `attach_neighbor_deltas` joins them to the seed’s A+K+ control, `c1_rows` includes baseline-available non-target edges in the C1 denominator, and `score_c1` recomputes C1 from the assembled parts; `a1_result.assemble` joins C1 and C4 into one PASS/FAIL report with per-seed and per-neighbour detail. C4 would contribute 59–60 non-target rows per seed, bringing the planned C1 denominator to 63–64; no cell has run, so C4 is not cleared and C1/C4 are not measured. |
| C1/C4 observed assembly | **IMPLEMENTED — NOT RUN** | `python -m benchmarks.a1_result --parts` reads the actual cell files in `.scratch/a1_two_path/parts` and reports the observed C1 A−/K− denominators and C4 row counts before scoring. With no parts it reports **NOT RUN** and exits 2, rather than presenting an empty denominator as a result. No cell has run. |
| C1/C4 VOID-gate draft | **DRAFT — NOT DECIDED** | [`A1-C1-C4-VOID-GATE.md`](A1-C1-C4-VOID-GATE.md) proposes that either C1 or C4 failing or being unmeasurable makes the run **VOID**, not `NOT IDENTIFIED` / `UNSATISFIABLE`. The current C4-only decision remains in force. No cell has run. |
| Freeze decision | **DO NOT FREEZE (2026-11-14)** | The dated record in [`A1-POWER-REVIEW.md`](A1-POWER-REVIEW.md) answers the freeze question **NO — NOT AS CURRENTLY EMITTED**; this is not an owner grant. |
| Freeze readiness PASS? | **NO — OPEN** | C4 is a post-freeze result gate, so it no longer blocks target freeze. The targets remain draft and unfrozen because no separate owner target-freeze act has been recorded; the review still records `can_move_now: false`. |
| Target sets worth freezing? | **NO — HOLD AS DRAFT; TARGET FREEZE NOT AUTHORIZED** | The selected edges are compliant and representative, but no separate target freeze has been performed. C4 is a post-freeze void gate, so C1/C4 cannot be a pre-freeze condition. Regenerate targets only if Path B is chosen. |
| Manifest freeze | **NOT DONE** | The target block remains `UNRESOLVED`; `a1_two_path --check` still refuses. |
| Dated owner grant | **NOT DONE** | No cell may open a database. |

## What the evidence does and does not mean

It means the selector can produce four disjoint targets for all six provisional
seeds from information available before acquisition cycle 37, and that the
implementation passes the blindness and determinism checks recorded in the audit.
It does **not** validate target selection as a scientific result, establish power,
clear C4, freeze the targets or authorise a run.

**Not evidence:** A compliance gate and a feasibility artifact. No A1 cell has
run; no target is frozen; no seed is reserved; no result exists.
