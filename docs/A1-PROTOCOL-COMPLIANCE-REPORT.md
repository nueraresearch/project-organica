# A1 protocol compliance report

**ID:** `A1-PROTOCOL-COMPLIANCE-1`  
**Date:** 2026-11-14  
**Status:** `P0 PASS — FREEZE READINESS OPEN (PASS: NO); PROTOCOL COMPLIANCE; RUN NOT AUTHORISED`

**This is a compliance report, not a target freeze, a grant or an experimental result.**
No A1 cell has run; no seed is reserved; no target is fixed in the manifest.

## Scope

This report answers one question: **does the implementation execute the registered
pre-cycle-37 target-selection boundary?** It does not answer whether the target rule
is scientifically optimal, whether `N = 4` is powered, or whether C4 measures acceptable spillover.

The registered boundary is the **36th acquisition cycle**, not the engine's sleep-cycle
counter. The sleep counter can lag the acquisition index; following it allowed event
cycles 37–48 into the candidate universe during the first audit run.

## Current state

```text
P0 Protocol Compliance   PASS
        ↓
Target Feasibility       PASS
        ↓
Freeze Readiness         OPEN (PASS: NO)
        ↓
Grant Decision           OPEN
        ↓
A1 Run                   NOT STARTED
```

P0 and feasibility are demonstrated. Freeze readiness cannot move to PASS: the power review found
that four target rows make C1 effectively a 100% preservation rule; C4 non-target
rows are now instrumented, but no cell has run and the C1/C4 denominators remain unmeasured. Separately, C7 is per seed and per edge with a 0.05 A/K rate over 120 cycles, so it is rate-resolved at N=4; C8 is per seed and per target row, and the current N=4 block cannot resolve its 0.05 ceiling. The dated freeze decision is **DO NOT FREEZE (2026-11-14)**, answering the adequacy question **NO — NOT AS CURRENTLY EMITTED**. The grant decision and run remain separate acts.

## Compliance table

| Requirement | Status | Evidence |
| --- | --- | --- |
| A1 estimand path | **PATH A — RECORDED; TARGETS DRAFT** | [`A1-TARGET-SELECTION-PROTOCOL.md`](A1-TARGET-SELECTION-PROTOCOL.md) records the representative eligible pre-37 cycle-membership directed-edge effect. Path B is not selected; it would require a new selector and target artifact. No target is frozen and no cell has run. |
| Pre-37 candidate universe | **PASS** | First 36 acquisition cycles; `run_seed` truncation; audit P0 |
| Pre-sleep U sampling | **PASS** | `a1_arms.run_cell`; `test_cycle_36_u_is_sampled_before_consolidation`; audit P0 |
| Future-blindness | **PASS** | 36-cycle vs 120-cycle world; identical targets, U and digest; audit |
| Report-blindness | **PASS** | No `SleepReport` field read; audit forbidden-token check |
| Sleep-blindness | **PASS** | Stored sleep payload leaves U unchanged; audit |
| Determinism | **PASS** | Two independent passes; identical targets, U and digest; audit |
| Four-target feasibility | **PASS** | Four disjoint targets for all six provisional seeds; audit |
| Digest stability | **PASS** | Stored artifact digest checked against contents; independent pass matches |

The audit artifact is [`a1_adversarial_audit.json`](a1_adversarial_audit.json), rendered
as [`A1-ADVERSARIAL-AUDIT.md`](A1-ADVERSARIAL-AUDIT.md). The selection artifact is
[`a1_target_selection.json`](a1_target_selection.json).

## Estimand record

The selected targets are a **representative eligible pre-37 cycle-membership directed-edge sample**, not a high-`U`, hard-edge or carrier-enriched sample: 24 observations across 23 unique edges, all 382 candidates eligible, selected vs unselected cycle-36 strength p = 0.918. This is a design fact, not a P0 condition. If a high-propensity estimand is required, the selector must be redesigned before freeze; that is a different experiment.

## Sensitivity evidence

The first audit run **failed** future-blindness for seeds `20630104` and `20630106`.
The cause was not a target hash collision; it was the clock boundary. For seed 104,
sleep cycle 36 arrived at acquisition cycle 48, so the selector could see event cycles
37–48 while claiming to be a cycle-36 selector. Seed 104's selected edge `sable>olive`
was absent from the first 36 acquisition cycles.

After the boundary was corrected:

- seed 104 changed from `sable>olive` to `willow>olive`;
- all six seeds selected from exactly the first 36 acquisition cycles;
- every seed reported `event_cycles = 36`;
- the audit passed future-blindness and the remaining P0 checks.

That failure and the resulting target change are evidence that the audit is sensitive
to actual leakage, not merely confirming the implementation.

## What this report does not establish

- It does not validate target selection as a scientific result.
- It does not establish freeze readiness; the power review is in [`A1-POWER-REVIEW.md`](A1-POWER-REVIEW.md).
- It does not clear C4; A1 cell output emits target rows and a separate
  non-target neighbour stream, but no cell has run.
- It does not freeze the target sets or the manifest.
- It does not authorise a grant, a cell or a database opening.

The target sets are a feasibility artifact. They are not fixed experimental targets
until the manifest is frozen by a separate act.

## Remaining gates

| Gate | State |
| --- | --- |
| Power/prevalence review for `N = 4` | **DONE — C1 DENOMINATOR FRAGILITY**; C4 contributes 59–60 non-target rows/seed, so planned C1 is 63–64, unmeasured ([review](A1-POWER-REVIEW.md)) |
| C1 denominator floor | **ADOPTED — BINDING FOR A1** with the C1/C4 VOID gate; minimum 60 paired-control rows; 60–64 may be read with three losses; below 60 is **VOID — `C1_DENOMINATOR_BELOW_FLOOR`**, even at 59/59 |
| C1 denominator impact | **RECORDED — REFERENCE ONLY**; 59→60 rows at `q=.95` is **0.000039 → 0.005409**, a loss-boundary step; required-retention scenarios cover 50–95% power |
| C1 power-design target | **RECORDED — DESIGN CRITERION**; 80% all-six-seed power at 63 rows requires **q=0.984017** under the independent model (0.984271 at 64; 0.983204 at 60); not an observed retention or a second acceptance gate |
| C1 power curve | **RECORDED — REFERENCE ONLY**; at assumed `q=.95, n=63`, all six seeds pass at **0.003**; at `q=.98` at **0.632**. Correlation sensitivity at the same point: path rho=.5 per-seed **0.454**; seed rho=.5 all-six **0.073**; both .5 all-six **0.113**. These are sensitivity assumptions, not estimated correlations ([review](A1-POWER-REVIEW.md)) |
| C7/C8 denominator unit | **ADOPTED — C7 PER-EDGE RATE; C8 PER-TARGET ROW; C8 UNDER-RESOLVED**; both gates are per seed and pooled rows are rejected. C7 has 8 Y- rows at N=4 for completeness/order, but its 0.05 margin is an A/K rate over 120 cycles per edge (1/120 = 0.008333), so C7 is **RESOLVED** at N=4. C8 has 4 A-K- target rows (1/4 = 0.25); at the N=8 maximum, 8 (1/8 = 0.125). C8 needs N≥20 for one-step resolution, above the 16-vertex maximum; C8 is the pre-freeze design blocker ([record](A1-C7-C8-DENOMINATOR.md)) |
| Denominator-resolution audit | **FLAGGED — 4 SCENARIOS**; C1 target-only at 4 and N=8, C8 at 4 and N=8 (8 rows, 1/8 = 0.125); C7 is rate-resolved at 1/120 = 0.008333 and is not flagged; expanded C1 and C4 pass ([audit](A1-DENOMINATOR-RESOLUTION.md)); `--parts` recomputes these from actual cells once parts exist, with no parts yet |
| C1/C4 gate order | **ADOPTED — ONE POST-FREEZE VOID GATE (2026-11-14)**; C1 or C4 failure/unmeasurability VOIDs the result; the 60-row floor is part of the same decision ([record](A1-C1-C4-VOID-GATE.md)) |
| C4 non-target neighbour rows | **IMPLEMENTED — NOT RUN**; `c1_rows`/`score_c1` can include baseline-available non-target edges in C1; `a1_result.assemble` reports C1 and C4 together |
| C1/C4 observed assembly | **IMPLEMENTED — NOT RUN**; `python -m benchmarks.a1_result --parts` reads actual cell files and reports the observed denominators; an empty directory is **NOT RUN**, exit 2 |
| C1/C4 VOID gate | **ADOPTED — BINDING FOR A1**; a single post-freeze validity test where either C1 or C4 failure/unmeasurability makes the run **VOID**; the 60-row floor is adopted with it |
| Target-freeze act | **DRAFT — AWAITING OWNER SIGNATURE; NOT FROZEN**; exact six target sets prepared for a separate freeze; no grant or run |
| Owner decision memo | **DRAFT — C1/C4 ADOPTED ELSEWHERE**; remains for remaining Path A confirmation and provisional freeze; C1/C4 gate and floor are adopted separately; no freeze, grant or run |
| Provisional-freeze gate order | **DRAFT — PROVISIONAL FREEZE ONLY**; drafts a provisional Path A target freeze; the post-freeze C1/C4 VOID gate and 60-row floor are **ADOPTED — BINDING FOR A1**; provisional means conditional evidentiary status, not revocable target identity; no freeze, grant or run |
| Manifest freeze | **NOT DONE** |
| Dated owner grant | **NOT DONE** |
| A1 run | **NOT AUTHORISED** |

## Checks

```bash
python -m benchmarks.a1_target_selection --check
python -m benchmarks.a1_adversarial_audit --check
python -m benchmarks.a1_two_path --self-test
python -m pytest -q tests/test_a1_prefreeze.py
```

All four checks pass on the working tree that produced this report. The A1 gate still
refuses because the manifest is unfrozen, no grant exists and the target block is
unresolved.

**Not evidence:** A protocol-compliance report. It records that the implementation
matches the registered boundary; it creates no target freeze, grant, cell or result.
