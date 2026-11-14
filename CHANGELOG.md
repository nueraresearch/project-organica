# Changelog

All notable changes to Project Organica are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project follows [Semantic Versioning 2.0.0](https://semver.org/).

## Versioning in this repository — three separate namespaces

The words "v1" and "v2" appear in this project in three different senses.
They are deliberately distinct, and they are what the version number
*does not* refer to.

| Namespace | Form | Meaning | Current |
|---|---|---|---|
| **Package version** | `0.x.y` (SemVer 2) | the released, installable, citable artifact | **0.15.0** (unreleased) · 0.12.0 cut 2026-11-06 · v0.10.0 is the previous tag · v0.9.0 the latest published release |
| **Architecture generation** | *Organica 1*, *Organica 2* | a generation of the eight-layer engine. Organica 1 is frozen; Organica 2 is planned | **Organica 1** |
| **Research campaign** | *Ablation Study 1*, *Ablation Study 2* | the experimental series. Study 1 is the eleven-condition ablation; Study 2 is the six-colony Tier-1 matrix | **Study 2 in flight** |

The package version is **pre-1.0**, which is the honest state: the public
API is not declared stable, and the MINOR/PATCH numbers carry the
meaning instead. `tests/test_versioning.py` asserts that the three
declarations — `organica.__version__`, `pyproject.toml` and `CITATION.cff`
— never drift apart, and that the version describes *this* commit: if a
tag for the version exists, it must point here. A version whose changelog
entry is marked `(unreleased)` is allowed to have no tag yet, because
there is nothing to check out.

---

## [0.15.0] — (unreleased)

### Addendum — A1 K dilution: more edges did not buy more K (2026-11-14)

- **The larger-universe failure is a supply problem, not an edge-count problem.** `A1-K-DILUTION-1` compares the fresh 16-tag block with the 28-tag larger universe. Candidate edges rose **383 → 1000** (**+161.1%**), A-available rows rose **279 → 353** (**+26.5%**), but K-available rows rose only **242 → 244** (**+0.8%**); K density fell **63.2% → 24.4%**. By transition type, K rows stayed at **145 → 146** (flip-P) and **97 → 98** (flip-Q) while edge counts roughly doubled. The old-old family was not protected: its K density fell **63.2% → 18.9%**, while old-new was **26.4%** and new-new **27.7%**, so the new tags are not the sole cause. The U gradient survives but Q4 K density falls **91.6% → 48.8%**, about **20 K rows/seed**. The redesign target is **K-capable edges**, not independent edges; more edges alone is not a repair. No target, threshold, freeze, grant or run. `benchmarks/a1_k_dilution.py`, `tests/test_a1_k_dilution.py`, `docs/A1-K-DILUTION.md`, `docs/a1_k_dilution.json`, `docs/A1-PARK-RECOMMENDATION.md`, `docs/A1-DISPOSITION-MEMO.md`, `docs/A1-REDESIGN-REQUIREMENTS.md`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Addendum — A1 park recommendation (2026-11-14)

- **The evidence now supports parking the current A1 design, subject to the owner's decision.** `A1-PARK-RECOMMENDATION-1` records the current control, the fresh block and the 28-tag larger universe all failing C1 **0/6**. The larger universe reaches **158–172** independent edges but K dilutes to **23–55**; its best C1 is **55**. The recommendation preserves A1 as **not run / not identified under the current design**, freezes no target, reserves no seed, grants nothing and runs nothing. It is not a treatment result and does not close the question in principle; reopening requires a new predeclared construction that clears the preflight without selecting on K. `docs/A1-PARK-RECOMMENDATION.md`, `tests/test_a1_park_recommendation.py`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-DISPOSITION-MEMO.md`, `docs/A1-REDESIGN-REQUIREMENTS.md`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Addendum — A1 larger-universe candidate fails through K dilution (2026-11-14)

- **A larger universe is not automatically a viable one.** `A1-LARGER-UNIVERSE-CANDIDATE-1` predeclares a **28-tag**, 7-tags-per-cell world, chosen by structural edge count after 24 tags yielded only 127–136 independent edges. The 28-tag candidate has **158–172** independent edges, but K falls to **23–55** and C1 to **23, 40, 42, 55, 47, 37**; the 20-row matching is **18, 15, 16, 26, 26, 18**. This construction fails **0/6**. It does not prove every larger world fails, but it removes “just add tags” as an assumed repair. No target is selected, frozen or run. `benchmarks/a1_larger_universe.py`, `tests/test_a1_larger_universe.py`, `docs/A1-LARGER-UNIVERSE-CANDIDATE.md`, `docs/a1_larger_universe_candidate.json`, `docs/A1-LARGER-UNIVERSE-PREFLIGHT.md`, `docs/a1_larger_universe_preflight.json`, `docs/A1-REDESIGN-REQUIREMENTS.md`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-DISPOSITION-MEMO.md`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Addendum — A1 successor candidate schema and validator (2026-11-14)

- **The refusal list is now machine-checkable.** `docs/a1_successor_candidate.schema.json` is the external contract for a candidate package; `benchmarks/a1_successor_schema.py` adds the cross-row and governance checks JSON Schema cannot express: fresh seeds, K-screening and prior-exposure disclosure, duplicate/reverse-duplicate/self-loop rejection, target-selection claims, universe consistency, preflight requirement, and freeze/grant/run claims. It then runs the existing no-arm preflight as a separate gate. The live candidate is **schema-clean** but **gate-fail** at C1 **40, 37, 46, 42, 31, 38**; `--check` accepts the structural record while `--validate` is strict. No target is selected, frozen or run. `benchmarks/a1_successor_schema.py`, `tests/test_a1_successor_schema.py`, `docs/a1_successor_candidate.schema.json`, `docs/A1-SUCCESSOR-SCHEMA.md`, `docs/A1-REDESIGN-REQUIREMENTS.md`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Addendum — A1 successor requirements checklist (2026-11-14)

- **The front door for a second candidate is now one page of hard constraints.** `A1-REDESIGN-REQUIREMENTS-1` fixes the candidate-spec fields, the **≥60 independent/C1** gate, duplicate and reverse-duplicate rejection, the **20-row** A+K matching condition when C2/C8 are in scope, one-universe consistency, preflight-before-freeze and the explicit refusal list. It records the fresh block's **0/6** failure at C1 **40, 37, 46, 42, 31, 38** and identifies a larger independent universe as the only untested redesign route. It is a reference page only: no target, seed, freeze, grant or run. `docs/A1-REDESIGN-REQUIREMENTS.md`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Addendum — A1 fresh-seed successor candidate fails the no-arm preflight (2026-11-14)

- **A predeclared fresh block is packaged as a candidate and tested, not adopted.** `A1-SUCCESSOR-CANDIDATE-1` fixes six contiguous seeds `20650101–20650106` without K screening; a one-seed timing probe did not alter the block, and it is not selected on high K. Each seed uses the same 16-tag compositional world and the same first-36-cycle candidate universe, then a 120-cycle no-A/K/Y baseline. The candidate fails **0/6**: independent edges are **64, 64, 64, 64, 63, 64**, K-available rows are **40, 37, 46, 42, 39, 38**, and C1 ceilings are **40, 37, 46, 42, 31, 38**; the best seed is still **14** rows short of 60. The 20-row A+K matching is feasible on **6/6** but does not repair C1. K is lower on five seeds; A is lower on `20650105` (31 vs 39), so the failure is C1 availability, not one path on every seed. The candidate uses an opt-in boundary-safe cycle correction; the registered selector and its artifacts are unchanged. No target is selected, frozen or run, no seed is reserved and no grant is issued. `benchmarks/a1_successor_candidate.py`, `tests/test_a1_successor_candidate.py`, `docs/A1-SUCCESSOR-CANDIDATE.md`, `docs/a1_successor_candidate.json`, `docs/A1-SUCCESSOR-PREFLIGHT.md`, `docs/a1_successor_preflight.json`, `docs/A1-DISPOSITION-MEMO.md`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Addendum — A1 successor preflight harness (2026-11-14)

- **The ≥60 K gate now has a fail-closed harness.** `A1-SUCCESSOR-PREFLIGHT-1` accepts a candidate successor universe or fresh seed block as a JSON spec with no-arm A/K rows, rejects duplicate or reverse-duplicate streams, and checks **≥60 independent edges and `min(A,K)` C1 ceiling per seed**, plus a **20-row** capacity-respecting A+K matching when C2/C8 are in scope. The no-candidate path still reports **NOT RUN** and does not substitute the current universe; the first supplied candidate is recorded in the addendum above. The current six-seed universe is included only as a **negative control**: **0/6** seeds pass, C1 ceilings **44, 31, 39, 35, 43, 36**, matching **32, 23, 36, 27, 35, 33**. A `PASS` would not freeze or authorise a run; a new protocol, freeze, seed reservation, grant and run remain separate acts. No target is selected, frozen or run. `benchmarks/a1_successor_preflight.py`, `tests/test_a1_successor_preflight.py`, `docs/A1-SUCCESSOR-PREFLIGHT.md`, `docs/a1_successor_preflight.json`, `docs/A1-DISPOSITION-MEMO.md`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Addendum — A1 disposition memo: redesign vs park (2026-11-14)

- **The fork is recorded with explicit requirements on both sides.** `A1-DISPOSITION-1` compares a successor protocol against parking the current branch. Redesign requires a no-arm preflight with **≥60 K-available independent rows per seed**, a consistent universe/scorer, a new pre-registration and — if C2/C8 remain in scope — **20 competent targets per seed**. At 63–64 edges that needs **93.8–95.2% K**; a larger universe lowers the required rate. Park is indicated if no fresh universe or seed block clears the floor without selecting on the same no-arm baseline, or if the only route is changing the estimator/floor without independent justification. The memo does not choose, signs nothing and leaves A1 unfrozen, ungranted and unrun; the current default is **hold**. `docs/A1-DISPOSITION-MEMO.md`, `tests/test_a1_disposition_memo.py`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Addendum — A1 K-availability decomposition (2026-11-14)

- **The K shortage is broad, pair-level and concentrated in low-U edges, not in a few tags or orientations.** `A1-K-DECOMPOSITION-1` reads the six no-arm baselines and the 382 candidate edges: A is available on **281/382** rows and K on **228/382**; **95** rows have A without K, **42** have K without A and **59** have neither. K is lower on five seeds and tied on `20630101`; the remaining shortfall to the 60-row floor is **16–29 rows** per seed. K availability rises across pooled cycle-36 U quartiles from **31.8%** to **89.1%**, but the high-U half contains only **28–31** edges per seed. K is mostly absent rather than late: **154/382** rows never form K in 120 cycles, and only **28/228** available rows first form it after cycle 60. Tag rates span **44.7–77.1%** pooled but swing from **0% to 100%** by seed, so no tag is consistently missing; **278/286** candidate/reverse pairs agree on K (**97.2%**), and the candidate universe is near-regular, so orientation and local degree are not levers. Consequence: at 63–64 edges a successor needs a **93.8–95.2%** K rate, or a larger independent universe; U enrichment alone cannot produce 60 rows. Descriptive only — no arm, no threshold, no target, no freeze, no grant, no run. `benchmarks/a1_k_decomposition.py`, `tests/test_a1_k_decomposition.py`, `docs/A1-K-DECOMPOSITION.md`, `docs/a1_k_decomposition.json`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Addendum — A1 N=20 competent target-selection rule, pre-registered draft (2026-11-14)

- **A fixed rule, not a selected target block.** `A1-N20-COMPETENT-1` retains the current N4 targets that pass a baseline A/K screen, fills to 20 in a fixed hash order with a three-edge endpoint cap, and fails the seed rather than fall back to a non-competent row. A capacity-respecting b-matching with the current competent N4 rows forced reaches **23–36 rows** on the six seeds, so **6/6** are feasible, but the current N4 block contributes only **12/24** rows; the **12/24** carrier- or admission-missing rows are deliberately dropped. This is a replacement estimand, not a repair of the representative target set. The screen uses the 120-cycle no-arm baseline, so it is pre-treatment but not future-blind; C1 remains 31–44. No target was selected, frozen or run. `benchmarks/a1_n20_competent_selection.py`, `tests/test_a1_n20_competent_selection.py`, `docs/A1-N20-COMPETENT-SELECTION.md`, `docs/a1_n20_competent_selection_prereg.json`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Addendum — A1 cell-stream dedupe and competent N20 pool (2026-11-14)

- **The apparent cell-stream C1 pass is reverse-orientation duplication.** The 112-row cell stream contains **382 candidate rows + 286 reverse orientations + 4 extra orientations**; it collapses to **384 unique undirected edges**, 64 per seed. Every candidate edge is present. On unique edges the C1 ceiling remains **31–44** against the 60-row floor, so the four-seed 112-row pass is not a second universe. The candidate pool also contains **23–36 A&K-available edges per seed**, enough to construct a 20-row competent N20 block; the current N20 selection has only 5–12 clean rows, so C2/C8 is a selection problem rather than a supply problem. C1 remains unresolved. `benchmarks/a1_design_viability.py`, `tests/test_a1_design_viability.py`, `docs/A1-DESIGN-VIABILITY.md`, `docs/a1_design_viability.json`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Implemented — A1 design-viability report: C1 ceiling and conditional C2/C8 (2026-11-14)

- **The current A1 design is not C1-capable.** `benchmarks/a1_design_viability.py` records the C1 ceiling proof: on the 63–64-edge candidate stream, the largest denominator any target selection can produce is **44, 31, 39, 35, 43, 36** per seed against the **60-row floor**, so all six seeds are unreachable even if every candidate is selected. The 112-edge cell stream reaches the floor on four seeds but not on `20630102` (59) or `20630104` (58). Target selection cannot repair C1; a new universe, seed block or C1 estimator is required. It also records the **conditional** C2/C8 target-competence result: under a baseline A/K competence reading, N4 has at most **3** clean rows per seed for a 4-row block and N20 at most **12** for a 20-row block. That is a target-selection incompatibility, not a proof that C2 or C8 must fail; C2 is a treatment gate and the no-arm baseline cannot decide whether an unblocked arm induces the missing path. The report does not freeze, grant, run or change a threshold. `benchmarks/a1_design_viability.py`, `tests/test_a1_design_viability.py`, `docs/A1-DESIGN-VIABILITY.md`, `docs/a1_design_viability.json`, `benchmarks/a1_two_path.py`, `tests/test_a1_prefreeze.py`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Implemented — N4/N20 target-viability report for C2 (2026-11-14)

- **N20 does not repair C2 target viability.** `benchmarks/a1_target_viability.py` joins the committed N4/N20 target sets to the no-arm carrier-timing and baseline-availability artifacts. N4 has **10/24** carrier-missing target rows (41.7%); N20 has **52/120** (43.3%). N20 adds 96 rows, of which **42** lack a carrier, retains all 10 N4 missing rows, and leaves **0/6** C2-viable seeds in both designs. Applying C2's exact predicates, N4 has **38/96** structurally failing target cell-rows (39.6%) and N20 has **202/480** (42.1%); only 12 N4 and 54 N20 rows have both A and K and are fully C2-viable. The report records C2 as not adjudicable under either target set, keeps the N=20 freeze act on hold, and does not run, freeze, grant or score anything. `benchmarks/a1_target_viability.py`, `tests/test_a1_target_viability.py`, `docs/A1-TARGET-VIABILITY.md`, `docs/a1_target_viability.json`, `benchmarks/a1_two_path.py`, `tests/test_a1_prefreeze.py`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Implemented — no-arm baseline-availability audit for C1/C4 (2026-11-14)

- **The observed C1 denominator and C4 non-target rows are now measured before freeze, and the design fails the denominator floor.** `benchmarks/a1_baseline_availability.py` replays all six registered worlds at 120 cycles with `A1ArmSleepService`, no treatment, cap 40, and records A/K/Y for every edge in the cell stream. On the candidate-protocol stream used by target selection (64/63 edges), the C1 A−/K− denominators are **44/44, 31/44, 39/52, 35/43, 43/49 and 36/49**, so the per-seed minimum is **31–52**, below the adopted 60-row floor on all six seeds; C4 non-target rows are the planned **59–60** at N=4 and **43–44** at N=20. On the current `a1_arms.run_cell` stream (112 directed edges), the minimum is **58** with seeds `20630102` and `20630104` below 60, and C4 would emit **108** N=4 and **92** N=20 non-target rows per seed. The 290-edge gap is a **design inconsistency**: the runner uses the full 120-cycle directed universe while the plan is the one-orientation, first-36-cycle candidate set. No target is frozen, no grant exists and no A1 cell has run. The N=20 freeze act is on hold. `benchmarks/a1_baseline_availability.py`, `tests/test_a1_baseline_availability.py`, `benchmarks/a1_two_path.py`, `tests/test_a1_prefreeze.py`, `docs/A1-BASELINE-AVAILABILITY.md`, `docs/a1_baseline_availability.json`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Resolved — C5 target timing with a fixed earlier-U sample (2026-11-14)

- **C5 no longer uses the cycle-36 target-selection sample.** A no-arm replay found target carriers beginning at cycle 5, so the cycle-36 sample was post-carrier for the current targets. `A1-C5-TARGET-TIMING-1` fixes C5 at cycle 4, after the cycle-4 observations and before that sleep call; it preserves all four current targets and records no current carrier before cycle 4; 10 of 24 current observations form no carrier by cycle 120, which is left to the structural gates rather than counted as a timing failure. Cycle 36 remains the target-selection diagnostic. `a1_two_path` records both cycles, `a1_arms` samples at the earlier cycle, and `gate_c5` treats an absent carrier/K/Y as no timing violation while rejecting malformed or preceding cycles. The N=20 act is ready for signature but unsigned; the live manifest remains N=4, unresolved, unfrozen and unauthorised, and no cell has run. `benchmarks/a1_c5_target_timing.py`, `docs/A1-C5-TARGET-TIMING.md`, `benchmarks/a1_arms.py`, `benchmarks/a1_two_path.py`, `benchmarks/a1_gate_readiness.py`, `tests/test_a1_c5_target_timing.py`, `docs/A1-TARGET-FREEZE-ACT-N20.md`, `docs/A1-TARGET-SELECTION-PROTOCOL.md`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Implemented — complete-coverage scoring for C2, C3, C5, C7 and C9 (2026-11-14)

- **The five structural A1 gates now have complete-coverage score wrappers rather than row-local checks.** `a1_arms.score_complete_gates` requires all six seeds, each gate's required cells and every expected target row; a missing cell or target row is a coverage failure, not a pass. C2 is evaluated per seed and checks both Y− cells' A/K paths; C3 requires the expected target universe across all six cells; C5 returns a failure instead of raising when a carrier/K/Y cycle is missing; C7 checks each Y− cell separately against its paired control (`Y_MINUS_A+K+` against `A+K+`, `Y_MINUS_A−K+` against `A−K+`) so one failed cell cannot be averaged away; C9 requires all six cells and one fingerprint per seed. `a1_result.assemble` adds these scores when cell parts carry target lists, using the registered N=20 target map by default. The live manifest remains N=4, unresolved and unfrozen, C5 target timing remains unresolved, and no cell has run. `benchmarks/a1_arms.py`, `benchmarks/a1_gate_readiness.py`, `benchmarks/a1_result.py`, `tests/test_a1_complete_gates.py`, `docs/A1-GATE-READINESS.md`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Implemented — N=20 target validation in the A1 manifest gate (2026-11-14)

- **`a1_two_path` now validates the N=20 target profile as well as the existing N=4 profile.** The validator selects the profile from `targets.n_per_seed`: N=4 still requires four disjoint targets, while N=20 requires 20 unique targets per seed, permits endpoint overlap with each endpoint capped at degree 3, requires the `A1-C8-EXPANSION-1` protocol and validates the block against `docs/a1_c8_target_selection.json`. The N=20 path also rejects duplicates, malformed edges, out-of-universe targets and target sets that do not match the C8 selection artifact. The live manifest remains N=4, unresolved and unfrozen; no target is frozen, no seed is reserved and no grant exists. The `A1-TARGET-FREEZE-N20-1` target block now passes `target_set_problems`; C5 target timing remains its only blocking precondition. `benchmarks/a1_two_path.py`, `tests/test_a1_prefreeze.py`, `docs/A1-TARGET-FREEZE-ACT-N20.md`, `docs/a1_target_freeze_act_n20.json`, `docs/A1-C8-EXPANSION.md`, `docs/A1-TARGET-FREEZE-ACT.md`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Recorded — C1 denominator-feasibility risk as an upper bound (2026-11-14)

- **C1's 63–64 planning figure is now recorded as an upper bound, not a baseline-availability estimate.** The figure is the candidate-universe count and assumes every candidate edge is available in the paired A+K+ control; the observed denominator can be lower and may fall below the adopted 60-row floor, which would make the run **VOID — `C1_DENOMINATOR_BELOW_FLOOR`**. The power review adds a dedicated risk note and a machine-readable `c1_denominator_feasibility` block. C6's K/Y_ind rates (602/672 and 586/672) and A0's hard-edge rate are explicitly labelled as observations from different seed blocks/worlds and **not** baseline-availability proxies; no unrelated percentage may estimate, bound or certify the C1 denominator. The C1 power curve is also labelled as scenario sizes, not observed availability. No threshold changed, no target is frozen, no seed reserved, no grant exists and no A1 cell has run. `benchmarks/a1_power_review.py`, `tests/test_a1_prefreeze.py`, `docs/A1-POWER-REVIEW.md`, `docs/a1_power_review.json`, `docs/A1-DENOMINATOR-RESOLUTION.md`, `docs/a1_denominator_resolution.json`, `docs/DECISION-A1-PATH-A-C1-RULE.md`, `docs/a1_path_a_c1_rule.json`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `docs/A1-C1-C4-VOID-GATE.md`, `docs/A1-C7-C8-DENOMINATOR.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Recorded — C8 N=20 superset and C1 per-seed availability budget (2026-11-14)

- **The registered C8 N=20 design now records that the live N=4 targets are a strict subset of the expansion in every seed.** The read-only comparison of `docs/a1_target_selection.json` and `docs/a1_c8_target_selection.json` finds four retained targets and 16 new rows per seed, for 20 total. The design record and machine-readable JSON carry the per-seed comparison; adopting N=20 would preserve the current target identity while moving the C4 non-target split from 59–60 to 43–44. The C1 total upper bound stays 63–64, and C1 target-only remains 20 rows, below the 60-row floor.
- **The power review now records the per-seed C1 availability budget implied by the adopted 60-row floor.** At 64 candidate rows, at most **4** may be baseline-unavailable (required availability **93.75%**); at 63, at most **3** (required availability **95.24%**). These are floor-arithmetic limits on the candidate-count upper bound, not observed or estimated availability rates, and they do not change the VOID disposition below the floor. `benchmarks/a1_power_review.py`, `tests/test_a1_prefreeze.py`, `tests/test_a1_c8_target_selection.py`, `docs/A1-POWER-REVIEW.md`, `docs/a1_power_review.json`, `docs/A1-C8-EXPANSION.md`, `docs/a1_c8_expansion.json`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Drafted — N=20 target-freeze act preserving the current targets (2026-11-14)

- **`A1-TARGET-FREEZE-N20-1` is drafted as the separate act that would adopt `A1-C8-EXPANSION-1` while preserving all four current Path A targets in every seed.** It records the exact 20 targets per seed from `docs/a1_c8_target_selection.json`: 120 observations, 104 unique target edges, four retained and 16 new per seed, with maximum endpoint degree 3. Signing would set the manifest target block to `FIXED BEFORE FREEZE`, set `n_per_seed` to 20 and make C8 evaluable at `1/20 = 0.05` without changing the 0.05 ceiling. C1 target-only remains 20 rows, below the 60-row floor; C4 has 43–44 non-target rows and the C1 total upper bound remains 63–64.
- **The act is explicitly not signable yet.** C5 is unresolved: 15 of 24 current target observations have a carrier before the cycle-36 `U` sample, so the preserved four targets and the expansion rows are not C5-admissible without a registered target screen/regeneration or an earlier-`U` protocol. The live `a1_two_path` validator also still requires N=4 disjoint targets and rejects the N=20 degree-3 set. The draft records both as blocking preconditions; it freezes nothing, issues no grant, runs no cell and makes no C8 measurement. **Superseded later on 2026-11-14:** C5 target timing is cleared by the cycle-4 earlier-`U` protocol; the N=20 act is ready for signature but remains unsigned. `docs/A1-TARGET-FREEZE-ACT-N20.md`, `docs/a1_target_freeze_act_n20.json`, `docs/A1-C8-EXPANSION.md`, `docs/A1-TARGET-FREEZE-ACT.md`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `tests/test_a1_prefreeze.py`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Registered — C8 N=20 expansion target design (2026-11-14)

- **A separate N=20 target design now resolves C8's per-seed denominator without changing the 0.05 ceiling.** `A1-C8-EXPANSION-1` selects **20 A−K− target rows per seed** from the same pre-36 acquisition universe, positive-strength/cycle-member eligibility and hash order as the four-target Path A design. Twenty disjoint edges cannot fit on 16 tags, so the design permits limited endpoint overlap while capping each tag at **three** selected targets; no target edge is repeated. The per-seed C8 step is `1/20 = 0.05`, which is not finer than the ceiling. The no-arm selection pass formed 20 rows for all six provisional seeds (maximum endpoint degree 3) and wrote `docs/a1_c8_target_selection.json` with the selected cycle-36 `U` rows and digests. The design is **REGISTERED — NOT FROZEN, NOT RUN, NO GRANT**; it does not alter the live N=4 manifest, the current four-target artifact or the C7 per-edge rate, and it does not by itself meet the 60-row C1 floor. Adopting it requires a separate target-freeze act. The audit now records the registered N=20 scenario as passing while the current N=4/N=8 scenarios remain flagged. `benchmarks/a1_target_selection.py`, `benchmarks/a1_c8_target_selection.py`, `benchmarks/a1_two_path.py`, `benchmarks/a1_denominator_audit.py`, `benchmarks/a1_gate_readiness.py`, `tests/test_a1_c8_target_selection.py`, `docs/A1-C8-EXPANSION.md`, `docs/a1_c8_expansion.json`, `docs/A1-C8-TARGET-SELECTION.md`, `docs/a1_c8_target_selection.json`, `docs/A1-C7-C8-DENOMINATOR.md`, `docs/a1_c7_c8_denominator.json`, `docs/A1-TARGET-SELECTION-PROTOCOL.md`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `docs/A1-TARGET-FREEZE-ACT.md`, `docs/a1_target_freeze_act.json`, `docs/A1-DENOMINATOR-RESOLUTION.md`, `docs/a1_denominator_resolution.json`, `docs/A1-GATE-READINESS.md`, `docs/a1_gate_readiness.json`, `ROADMAP.md`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.


### Adopted — C7/C8 per-seed denominator unit (2026-11-14)

- **C7 and C8 are evaluated per seed; C8 is the remaining design under-resolution.** `A1-C7-C8-DENOMINATOR-1` resolves the unit mismatch between the denominator audit, which applied `1/n` to each seed's own C7/C8 rows, and the readiness contracts, which pooled those rows across seeds. Pooling is rejected: one seed's 1/4 A−K− assertion rate would pool to 1/24 and appear to pass, hiding exactly the per-seed third route C8 exists to detect. C7's 0.05 margin is an A/K rate over the **120 cycles on each paired target edge** (1/120 = 0.008333), so C7 is **RESOLVED** at N=4; the 2N Y− rows are for cell completeness and the assertion-order check, not the rate denominator. C8's 0.05 ceiling is a per-target assertion rate: 4 rows at N=4 (0.25) and 8 at the N=8 maximum (0.125); C8 needs N≥20 for one-step resolution, above the 16-vertex, eight-target maximum, so C8 remains **UNDER-RESOLVED**. `gate_c7` and `gate_c8` require every seed to pass on its own rows; a seed missing either Y− cell, a paired edge or the A−K− cell is not measurable, not a pass. Target rows now emit A/K/Y cycle counts and rates; `gate_c7` computes the per-edge delta from those rates when `delta_from_baseline` is absent, so the contract can read a real cell rather than only its synthetic fixture. The audit and gate-readiness artifacts record the per-seed units and the rejected pooled counts. No threshold changed, no target is frozen, no seed is reserved, no grant exists and no cell has run. `benchmarks/a1_gate_readiness.py`, `benchmarks/a1_denominator_audit.py`, `benchmarks/a1_arms.py`, `tests/test_a1_denominator_audit.py`, `docs/A1-C7-C8-DENOMINATOR.md`, `docs/a1_c7_c8_denominator.json`, `docs/A1-GATE-READINESS.md`, `docs/a1_gate_readiness.json`, `docs/A1-DENOMINATOR-RESOLUTION.md`, `docs/a1_denominator_resolution.json`, `docs/A1-PRECOMMITTED-THRESHOLDS.md`, `docs/a1_precommitted_thresholds.json`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `docs/A1-TARGET-FREEZE-ACT.md`, `docs/a1_target_freeze_act.json`, `ROADMAP.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

### Recorded — Path A estimand and C1 acceptance rule (2026-11-14)

- **Path A is the recorded A1 estimand and the C1 rule is now binding:** minimum **60** paired-control available rows across all six seeds and both A−/K− paths, **three allowed losses at 60–64**, and **`VOID — C1_DENOMINATOR_BELOW_FLOOR`** at 1–59 rows, even at 59/59. Zero rows is `C1_NO_DENOMINATOR`; above 64 is a design inconsistency. The rule does not freeze targets, reserve seeds, grant a run or observe C1/C4. `benchmarks/a1_power_review.py`, `docs/A1-POWER-REVIEW.md`, `docs/a1_power_review.json`, `docs/DECISION-A1-PATH-A-C1-RULE.md`, `docs/a1_path_a_c1_rule.json`, `docs/A1-C1-C4-VOID-GATE.md`, `docs/a1_c1_c4_void_gate.json`, `docs/DECISION-A1-PATH-A-C1-C4.md`, `docs/a1_owner_decision_memo.json`, `docs/A1-PROVISIONAL-FREEZE-GATE-ORDER.md`, `docs/a1_provisional_freeze_gate_order.json`, `docs/A1-TARGET-FREEZE-ACT.md`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `tests/test_a1_prefreeze.py`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Prepared — Path A target-freeze act (2026-11-14)

- **A separate unsigned target-freeze act now records the exact six Path A target sets without freezing the live manifest.** The act fixes 24 observations across 23 unique edges, the per-seed selection digests and the artifact SHA-256; on signature it would set the manifest target block to `FIXED BEFORE FREEZE`, freeze the manifest and reserve the six-seed block. It does not issue a grant, open a database or run a cell, and C1/C4 remain unobserved. The live manifest is unchanged: **NOT FROZEN**, targets **UNRESOLVED**, seeds **PROVISIONAL**, authorisation false. `benchmarks/a1_power_review.py`, `docs/A1-POWER-REVIEW.md`, `docs/a1_power_review.json`, `docs/A1-TARGET-FREEZE-ACT.md`, `docs/a1_target_freeze_act.json`, `docs/A1-TARGET-SELECTION-PROTOCOL.md`, `docs/DECISION-A1-PATH-A-C1-C4.md`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `tests/test_a1_prefreeze.py`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Drafted — single owner memo for Path A and C1/C4 ordering (2026-11-14)

- **One unsigned owner decision memo now records Path A and resolves C1/C4 as post-freeze VOID gates.** The memo fixes the order freeze → grant → run → measure C1/C4 → PASS or VOID, rejects pre-freeze admissibility because it would require circularity, an unregistered diagnostic or an assumed denominator, and defines what a VOID run means: no model, no M1 branch, no capability/transfer claim, C7/C8 not adjudicated, seeds/cells consumed, no rescue or retry. It remains **DRAFT — AWAITING OWNER SIGNATURE**; the targets remain draft, no freeze, seed reservation, grant or run is recorded, and the 60-row floor remains a separate **PROPOSED — NOT ADOPTED** rule. `benchmarks/a1_power_review.py`, `docs/A1-POWER-REVIEW.md`, `docs/a1_power_review.json`, `docs/DECISION-A1-PATH-A-C1-C4.md`, `docs/a1_owner_decision_memo.json`, `docs/A1-PROVISIONAL-FREEZE-GATE-ORDER.md`, `docs/A1-C1-C4-VOID-GATE.md`, `docs/A1-C4-GATE-ORDER.md`, `docs/A1-TARGET-SELECTION-PROTOCOL.md`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `tests/test_a1_prefreeze.py`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Drafted — provisional freeze and C1/C4 gate order (2026-11-14)

- **A draft decision now sets out a provisional Path A target freeze followed by a post-freeze C1/C4 VOID gate.** “Provisional” describes the result's evidentiary status, not revocable target identity: the targets are fixed before the grant, and a C1/C4 failure VOIDs the run without unfreezing them or licensing re-selection. The draft defines the gate order, the six C1/C4 VOID conditions, and what a VOID run means — no model label, no M1 branch, no capability/transfer/generalization claim, C7/C8 not adjudicated, seeds and cells consumed, no rescue or retry. It remains **DRAFT — NOT DECIDED**; the current `DO NOT FREEZE`, C4-only gate order and draft targets remain in force, and no seed, grant or cell is authorised. The 60-row denominator floor remains a separate **PROPOSED — NOT ADOPTED** companion rule. `benchmarks/a1_power_review.py`, `docs/A1-POWER-REVIEW.md`, `docs/a1_power_review.json`, `docs/A1-PROVISIONAL-FREEZE-GATE-ORDER.md`, `docs/a1_provisional_freeze_gate_order.json`, `docs/A1-C1-C4-VOID-GATE.md`, `docs/A1-C4-GATE-ORDER.md`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `tests/test_a1_prefreeze.py`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Recorded — Path A A1 estimand (2026-11-14)

- **The A1 target-selection protocol and freeze-decision log now record Path A.** Path A is the representative eligible pre-37 cycle-membership directed-edge effect already implemented by the selector. Path B — the high-carrier-propensity, hard-edge or carrier-enriched effect — is not selected and would require a new selector, target artifact and registered design. Recording Path A does not regenerate targets, freeze the manifest, reserve a seed, issue a grant or authorise a cell; the six existing target sets remain **DRAFT — NOT FROZEN**, and the freeze decision remains **DO NOT FREEZE (2026-11-14)**. `benchmarks/a1_power_review.py`, `docs/a1_power_review.json`, `docs/A1-POWER-REVIEW.md`, `docs/A1-TARGET-SELECTION-PROTOCOL.md`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

### Proposed — C1 60-row denominator floor (2026-11-14)

- **The power review now turns the 59→60 cliff into a proposed pre-run decision rule.** The rule uses the minimum paired-control available denominator across all six seeds and both `A−` and `K−` paths. At 60–64 rows the C1 gate may be read with three allowed losses; at 20–59 rows the run is **VOID — `C1_DENOMINATOR_BELOW_FLOOR`**, even if every available row is retained; at 0 rows it is `C1_NO_DENOMINATOR`; and above 64 is a design inconsistency. The rule is **PROPOSED — NOT ADOPTED**: no target is frozen, no grant exists and no cell has run. It is linked to the C1/C4 VOID-gate draft and would need a dated owner adoption before target freeze. `benchmarks/a1_power_review.py`, `docs/a1_power_review.json`, `docs/A1-POWER-REVIEW.md`, `docs/A1-C1-C4-VOID-GATE.md`, `docs/a1_c1_c4_void_gate.json`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

### Added — C1 denominator impact and required-retention scenarios (2026-11-14)

- **The C1 power review now shows the denominator-impact table, the 60-row cliff and the retention required for stated all-six-seed power.** At `q=.95`, the all-six probability is **0.000039** at 59 rows and **0.005409** at 60 rows, a **138.69x** step. The step comes from the loss boundary: 59 rows allow 2 losses at an effective floor of 0.9661, while 60 rows allow 3 losses at 0.95. The table also shows that 63 and 64 rows give 0.002807 and 0.002239 at `q=.95`. Required-retention scenarios for all-six power of 50%, 80%, 90% and 95% are recorded for every denominator; at 63 rows, 80% power needs `q=.984017` and 50% needs `q=.977154`. These are reference calculations under independent Bernoulli retention, not observed rates. No cell has run and the freeze decision is unchanged. `benchmarks/a1_power_review.py`, `docs/a1_power_review.json`, `docs/A1-POWER-REVIEW.md`, `tests/test_a1_prefreeze.py`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

### Adopted — 60-row C1 floor and C1/C4 VOID gate (2026-11-14)

- **The 60-row denominator floor and the C1/C4 post-freeze VOID gate are now one dated owner decision.** `A1-C1-C4-VOID-GATE-1` is **ADOPTED — BINDING FOR A1**. C1 and C4 are one validity test: either failing or being unmeasurable makes the run **`A1 VOID — C1/C4`** with reason codes, before any model is read. The readiness contract now classifies C1 failure and unmeasurability as **VOID**, and `a1_result.assemble` returns **PASS/VOID**, carrying `void_gates` and `reason_codes`. The target freeze, seed reservation, grant and run remain separate owner acts; no cell has run. `benchmarks/a1_gate_readiness.py`, `benchmarks/a1_result.py`, `docs/A1-C1-C4-VOID-GATE.md`, `docs/a1_c1_c4_void_gate.json`, `docs/DECISION-A1-PATH-A-C1-RULE.md`, `docs/a1_path_a_c1_rule.json`, `docs/A1-C4-GATE-ORDER.md`, `docs/a1_c4_gate_order.json`, `docs/DECISION-A1-PATH-A-C1-C4.md`, `docs/a1_owner_decision_memo.json`, `docs/A1-PROVISIONAL-FREEZE-GATE-ORDER.md`, `docs/A1-GATE-READINESS.md`, `docs/a1_gate_readiness.json`, `tests/test_a1_c4.py`, `tests/test_a1_prefreeze.py`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

### Added — 80% C1 power-design criterion (2026-11-14)

- **C1 now records an 80% all-six-seed power target and its required retention.** At the planned 63-row denominator, the independent Bernoulli model needs a common retention of **q=0.984017** for 80% all-six power; at 64 rows it needs **0.984271**, and at the 60-row floor **0.983204**. The criterion is recorded in `DECISION-A1-PATH-A-C1-RULE.md` and the power review, is not an observed retention, and is not a second post-run acceptance gate. The 0.95 preservation rule and 60-row floor are unchanged; no freeze, grant, seed reservation or cell. `benchmarks/a1_power_review.py`, `docs/a1_power_review.json`, `docs/A1-POWER-REVIEW.md`, `docs/DECISION-A1-PATH-A-C1-RULE.md`, `docs/a1_path_a_c1_rule.json`, `tests/test_a1_prefreeze.py`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

### Added — C1 correlation sensitivity (2026-11-14)

- **The C1 power curve now includes correlated A/K paths and correlated seeds as sensitivity scenarios.** The independent Bernoulli curve remains the baseline; a Gaussian copula joins the A- and K- pass indicators within a seed at `rho_paths`, and a one-factor Gaussian copula joins the six seed-pass indicators at `rho_seeds`. At `n=63, q=.95`, independent paths and seeds give per-seed **0.375577** and all-six **0.002807**; A/K path correlation `.5` raises per-seed to **0.453562**; seed correlation `.5` raises all-six to **0.073188**; both at `.5` give **0.113341**. Positive seed correlation raises all-six because the seeds share a fate, while also raising the chance that none pass. The correlations are sensitivity settings, not estimates from A1; no cell has run and the freeze decision is unchanged. `benchmarks/a1_power_review.py`, `docs/a1_power_review.json`, `docs/A1-POWER-REVIEW.md`, `tests/test_a1_prefreeze.py`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

### Added — C1 power curve in the A1 power review (2026-11-14)

- **The power review now shows C1 pass probability against the denominator, with the assumed retention rate stated for every curve.** The generated review records a reference curve for `n = 4, 20, 56, 59, 60, 63, 64` at `q = 0.95, 0.97, 0.98, 1.00` under independent Bernoulli retention. It reports one-arm, one-seed and all-six-seed probabilities; the all-six column is the actual gate shape because C1 must pass on every seed. At `q = 0.95, n = 63`, one arm passes with probability **0.613**, both arms on one seed **0.376**, and all six seeds **0.003**; at `q = 0.98`, the all-six probability is **0.632**. The target-only four-row fallback is **0.085** at `q = 0.95` and **0.379** at `q = 0.98`. A denominator of 20 is the smallest listed value that can still pass with one loss. These are **assumed** retention rates, not A1 measurements; no cell has run and the observed denominator remains unknown. The curve does not change the freeze decision, the planned 63–64 rows, or the C4 gate order. `benchmarks/a1_power_review.py`, `docs/a1_power_review.json`, `docs/A1-POWER-REVIEW.md`, `tests/test_a1_prefreeze.py`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

### Drafted — C1/C4 post-freeze VOID gate (2026-11-14)

- **A draft decision would make either C1 or C4 failing or unmeasurable void the whole A1 run.** `docs/A1-C1-C4-VOID-GATE.md` proposes one post-freeze result-validity test: freeze targets, grant the run, execute the planned cells, then assemble C1 and C4 from actual parts. C1 failure is no longer `NOT IDENTIFIED`, and C1/C4 unmeasurability is no longer `UNSATISFIABLE`; either becomes `A1 VOID — C1/C4` with explicit reason codes (`C1_NO_DENOMINATOR`, `C1_THRESHOLD`, `C4_UNMEASURABLE`, `C4_DELTA`, `C1_C4_INCOMPLETE`). A VOID run selects no model, assigns no M1 branch, makes no negative or capability claim, does not adjudicate C7/C8, consumes the seeds and cells, and cannot be rescued by a passing gate or a post-hoc denominator expansion. The record is **DRAFT — NOT DECIDED**; the current C4-only decision and C1 result-gate disposition remain in force until a dated owner adoption. No target is frozen, no seed reserved, no grant exists and no cell has run. `docs/A1-C1-C4-VOID-GATE.md`, `docs/a1_c1_c4_void_gate.json`, `docs/A1-C4-GATE-ORDER.md`, `docs/a1_c4_gate_order.json`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

### Added — observed C1/C4 denominator assembly (2026-11-14)

- **`a1_result --parts` now reads actual A1 cell files and reports the denominator it actually observed.** The command loads every `a1_two_path_cell` part in the parts directory, excluding controls, and prints the observed C1 A- and K- row counts and the C4 row/measured counts before the PASS/FAIL detail. The assembly object gains `observed_denominator` with the part, seed and cell coverage plus per-seed C1 counts. An empty or missing parts directory now prints **NOT RUN — no cell parts** and exits 2 instead of rendering a zero-row PASS/FAIL; `--parts` with no path uses `a1_arms.PARTS`, and the synthetic fixture still reports its 20/20 C1 and 48-row C4 denominators. No cell has run, so the observed A1 denominator remains unknown; this is a read-only assembly command, not a result. `benchmarks/a1_result.py`, `tests/test_a1_c4.py`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

### Adopted — the 0.x engineering charter is in force (2026-11-14)

- **The owner adopted the bounded 0.x engineering charter as a dated decision.** `docs/DECISION-0X-ENGINEERING-CHARTER.md` records **ADOPTED — IN FORCE** and adopts `docs/0X-ENGINEERING-CHARTER.md`; its Category A–F changes, version rules, one-guard-per-failure budget, A1 boundary and stop conditions now apply to 0.x work. The decision does not bump 0.15.0, pre-allocate 0.16–0.20, change an engine file, select an A1 target, freeze the manifest, issue a grant or create a claim. A1 remains unrun and every experiment state is unchanged. `docs/DECISION-0X-ENGINEERING-CHARTER.md`, `docs/0X-ENGINEERING-CHARTER.md`, `docs/decisions.json`, `docs/DECISIONS.md`, `docs/research_question_registry.json`, `docs/RESEARCH-QUESTION-REGISTRY.md`, `ROADMAP.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

### Drafted — bounded 0.x engineering charter (2026-11-14)

- **The 0.x line now has a proposed engineering boundary, not an adopted policy.** `docs/0X-ENGINEERING-CHARTER.md` separates record, test/CI, instrumentation, engine-behavior, packaging and publication changes; requires a named failure or scheduled experiment before adding a guard; limits a release to one primary objective; forbids post-outcome threshold, target, endpoint or seed changes; and records stop conditions for V2, G9, release, A1 and live-database work. It keeps A1 target selection, freeze and grant as separate experimental acts, and it explicitly does not pre-allocate 0.16–0.20. The charter is **DRAFT — NOT ADOPTED, NOT IN FORCE**, creates no version, engine change, seed, cell, grant or claim, and leaves 0.15.0 and every experiment state unchanged. `docs/0X-ENGINEERING-CHARTER.md`, `ROADMAP.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

### Recorded — A1 freeze readiness remains OPEN, PASS: NO (2026-11-14)

- **The N = 4 review records that freeze readiness cannot move from OPEN to PASS.** C6 prevalence is adequate at **602/672 K** and **586/672 Y_ind**, but four target rows make the precommitted 0.95 C1 floor a 100% rule; C4 non-target rows are instrumented, yet no cell has run. The review artifact records `freeze_readiness.status = OPEN`, `pass = false`, `can_move_now = false`, blocking gate `C1_path_separation`, and the three conditions needed for PASS: run the cells with the C4 stream, attach paired deltas and score C1/C4, and show C1 at or above 0.95 with a denominator larger than four and C4 at or below 0.05. The checklist, compliance report, roadmap and manual carry the same status. **No target is frozen, no seed is reserved, no grant exists and no A1 cell has run.** `docs/A1-POWER-REVIEW.md`, `docs/a1_power_review.json`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `ROADMAP.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

### Reviewed — A1 audit and power review rerun with the planned C4 denominator (2026-11-14)

- **The power review now uses the A1 candidate counts, not the larger C6 world, to size the planned C1 denominator.** The six A1 candidate universes contain 63–64 edges; after removing four target rows, C4 would contribute **59–60 non-target rows per seed** and **358 total**; adding the four target rows gives a planned **C1 denominator of 63–64 per seed** and **382 total**. At the 0.95 floor that permits **3 losses per seed** (`floor(63 × 0.05) = 3`, `floor(64 × 0.05) = 3`), not the zero losses of the four-row design. This is a **planned** denominator: only baseline-available edges enter C1, so the observed denominator will be at most 63–64 and cannot be known until cells run. The review still records **FREEZE READINESS OPEN**, `can_move_now: false`, **DO NOT FREEZE**, and **NO — HOLD AS DRAFT UNTIL C1/C4 ARE MEASURED**. The six-seed adversarial audit was re-run and remains **P0 PASS — SIX-SEED FEASIBILITY AND BLINDNESS**; it does not measure C1 and its artifact is unchanged. No target is frozen, no seed is reserved, no grant exists and no cell has run. `benchmarks/a1_power_review.py`, `docs/a1_power_review.json`, `docs/A1-POWER-REVIEW.md`, `benchmarks/a1_adversarial_audit.py`, `docs/a1_adversarial_audit.json`, `docs/A1-ADVERSARIAL-AUDIT.md`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

### Audited — A1 denominator resolution (2026-11-14)

- **A new read-only audit flags every A1 gate whose 0.05-scale threshold is finer than its planned denominator.** The rule is `1/n` versus the gate margin: for a 0.95 floor the margin is 0.05, and for a 0.05 ceiling the margin is 0.05. The target-only C1 fallback (4 rows), C7 (8 Y− rows) and C8 (4 A−K− rows) are flagged; the expanded C1 denominator (63–64 planned rows) and the C4 non-target denominator (59–60) pass the resolution test. C2, C3, C5, C6 and C9 are structural checks without a numeric threshold. The audit records the planned values only; the observed baseline-available C1 denominator is still unknown and no cell has run. `benchmarks/a1_denominator_audit.py`, `tests/test_a1_denominator_audit.py`, `docs/a1_denominator_resolution.json`, `docs/A1-DENOMINATOR-RESOLUTION.md`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

- **The denominator-resolution audit now adds an N=8 maximum-feasibility scenario.** Eight disjoint targets use all 16 tag vertices and are feasible in every seed. At that maximum, C7 becomes **16 Y− rows** (step **1/16 = 0.0625**) and C8 becomes **8 A−K− rows** (step **1/8 = 0.125**); both remain above the 0.05 margin, so **C7/C8 remain under-resolved**. C1 target-only at 8 rows is also flagged (7/8 = 0.875); expanded C1 at 63–64 rows and C4 at 55–56 rows still pass. The audit remains read-only and records planned denominators only; it measures neither C7 nor C8 and no cell has run. `benchmarks/a1_denominator_audit.py`, `tests/test_a1_denominator_audit.py`, `docs/a1_denominator_resolution.json`, `docs/A1-DENOMINATOR-RESOLUTION.md`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

- **The denominator-resolution audit now has a post-run update from actual A1 parts.** `python -m benchmarks.a1_denominator_audit --parts [DIR]` loads cell files through the existing `a1_result` loader and recomputes the observed C1 paired-control denominator, C4 distinct non-target edges, C7 Y− blocked rows and C8 A−K− rows. It writes separate `A1-DENOMINATOR-RESOLUTION-OBSERVED.md` and `a1_denominator_resolution_observed.json` records, never overwriting the planned audit. The minimum observed denominator per gate is used; unavailable values are **UNMEASURED**, not zero; partial planned-cell coverage is labelled; an empty parts directory is **NOT RUN**, exit 2. The observed record is a denominator statement, not a C7/C8 verdict or an A1 PASS/FAIL, and C1's separate 60-row floor still applies. No A1 parts exist in the repository, so the observed record is not generated here. `benchmarks/a1_denominator_audit.py`, `tests/test_a1_denominator_audit.py`, `docs/A1-DENOMINATOR-RESOLUTION.md`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

### Decided — C4 is a post-freeze VOID gate (2026-11-14)

- **C4 was removed from the pre-freeze admissibility set and recorded as a post-freeze VOID gate.** C4 is an interference check on executed edge-level arms, not a property of the target set; requiring it before freeze would either force a circular freeze or an unregistered diagnostic run. The decision records the sequence: freeze the representative targets separately, record the dated grant, run the planned cells, then `a1_result.assemble` C1/C4. A measurable non-target A/K/Y delta above **0.05**, or an unmeasurable non-target stream, makes the A1 run **VOID**. C1 is scored in the same post-freeze assembly and uses the C4 denominator. The decision **does not** freeze the targets, reserve a seed, grant a run or produce evidence; the targets remain draft and the manifest unfrozen. `docs/A1-C4-GATE-ORDER.md`, `docs/a1_c4_gate_order.json`, `benchmarks/a1_gate_readiness.py`, `docs/a1_gate_readiness.json`, `docs/A1-GATE-READINESS.md`, `benchmarks/a1_power_review.py`, `docs/a1_power_review.json`, `docs/A1-POWER-REVIEW.md`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

### Implemented — A1 C1/C4 result assembly (2026-11-14)

- **C1 and C4 now assemble into one decision object, with exact PASS/FAIL detail.** `benchmarks/a1_result.assemble` scores the C1 stream and the C4 stream together and returns the per-seed A−/K− denominators, the maximum A/K/Y neighbour delta, and every violating or unmeasured non-target row. A synthetic three-cell fixture with 20 paired C1 rows passes with A− **19/20 = 0.950**, K− **20/20 = 1.000**, and C4 max deltas **A 0.01, K 0.01, Y 0.04** against a **0.05** tolerance. A second fixture sets one Y delta to **0.06**, producing `FAIL` with `seed=1 cell=A-K+ edge=n0>m0 path=Y delta=0.06` while C1 remains `PASS`. The assembly opens no database and runs no cell; the fixtures are assembly controls, not A1 evidence. `benchmarks/a1_result.py`, `benchmarks/a1_arms.py`, `tests/test_a1_c4.py`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `docs/A1-TARGET-SELECTION-PROTOCOL.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

### Implemented — A1 C4 non-target neighbour rows (2026-11-14)

- **The A1 cell output now carries a separate non-target stream for C4.** `benchmarks/a1_arms.run_cell` emits `neighbor_rows` for every edge in the candidate universe that is not a target, with per-edge A/K/Y cycle counts, availability rates, relation and object fingerprint. `attach_neighbor_deltas` joins each row to the same seed’s `A+K+` control and computes the absolute A/K/Y `neighbor_delta`; `c4_neighbor_rows` flattens the stream for `gate_c4`, and `c1_rows` includes baseline-available non-target edges in C1 so the denominator can exceed four, and `score_c1` recomputes C1 from assembled parts (with `score_c4` for the non-target deltas). The stream is deliberately separate from `rows` because mixing it into the target list would make C2 see non-target edges in the manipulated cells and C3 require all four treatment cells for every non-target edge. Four focused tests cover row construction, paired deltas, the missing-control state and a C1 denominator larger than four. **No cell has run:** C4 and C1 remain unmeasured, the target sets remain draft, and no freeze or grant exists. `benchmarks/a1_arms.py`, `tests/test_a1_c4.py`, `docs/A1-TARGET-SELECTION-PROTOCOL.md`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `docs/A1-POWER-REVIEW.md`, `ROADMAP.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

### Measured — A1 power review finds C1 denominator fragility (2026-11-14)

- **A read-only power/prevalence review says the current four-target rows are too narrow for C1, so freeze readiness stays open.** [`A1-POWER-REVIEW.md`](docs/A1-POWER-REVIEW.md) uses only existing selection, C6 and A0 records. The 24 selected targets are statistically indistinguishable from the 358 unselected candidates on cycle-36 strength (medians 16, means 15.333 vs 15.215, 20,000-draw permutation p = 0.918), and every candidate is eligible, so the target set is a random eligible sample rather than a high-`U` set. C6 supplies 602/672 K and 586/672 Y_ind in its own world, but only 53 target-edge overlaps; A0's hard-edge rate is 26/672 (3.9%). The decisive finding is arithmetic: with four target rows per seed, the precommitted 0.95 C1 floor passes only at 4/4 (3/4 = 0.75). C4 non-target rows are therefore required to enlarge the C1 denominator, not merely to improve output. The review records the dated freeze decision **DO NOT FREEZE (2026-11-14)**, answers the worth-freezing question **NO — HOLD AS DRAFT UNTIL C4** (the selected edges are compliant and representative; the denominator is the blocker), and records the estimand explicitly: the targets are a **representative eligible pre-37 cycle-membership sample**, not a high-`U`, hard-edge or carrier-enriched sample, and the binary freeze answer is **NO — NOT AS CURRENTLY EMITTED** because C6 prevalence is a different-seed observation and not a C1 baseline-availability proxy, while the four-row C1 denominator is too narrow. No target is frozen and no cell has run. `benchmarks/a1_power_review.py`, `docs/a1_power_review.json`, `docs/A1-POWER-REVIEW.md`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `ROADMAP.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

- **The six-seed audit now records the representativeness measurement, not only the blindness checks.** `docs/A1-ADVERSARIAL-AUDIT.md` adds selected/unselected means **15.333 vs 15.215**, medians **16 vs 16**, **24** observations across **23** unique edges, **358** unselected of **382** candidates, all-candidates-eligible and a descriptive permutation **p = 0.918**, with the conclusion that the targets are a representative eligible pre-37 sample and not a high-`U`, hard-edge or carrier-enriched sample. The pre-freeze checklist carries the same table and conclusion; the p-value is explicitly descriptive, not an equivalence test. No target is frozen, no seed is reserved and no cell has run. `benchmarks/a1_adversarial_audit.py`, `docs/a1_adversarial_audit.json`, `docs/A1-ADVERSARIAL-AUDIT.md`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

### Implemented — A1 pre-freeze machinery and six target sets formed (2026-11-14)

- **The A1 pre-freeze path now runs end to end as a selection pass, and it formed four disjoint targets for every provisional seed, without freezing or granting anything.** `benchmarks/a1_arms.py` captures the cycle-36 `U` after the 36th acquisition cycle is stored and before `run_sleep_cycle()`; this replaces the post-sleep sampler. The selector uses the same acquisition-cycle boundary and no report field. `benchmarks/a1_target_selection.py` streams each seed to that boundary, builds the candidate universe from the events stored before it, selects by a hash order rather than `U` magnitude, requires cycle membership and positive pre-37 strength, and writes the digest-checked draft artifact `docs/a1_target_selection.json`. All six seeds formed four targets (candidate counts 63–64; 24 selected edges total). The first audit failed for two seeds because the engine sleep counter lagged the acquisition index and let event cycles 37–48 into the candidate universe; the boundary was corrected to acquisition cycle 36. The regenerated audit records **P0 PASS**: U before the cycle-36 sleep call, first-36-cycle universe, future-blindness, report-blindness, sleep-blindness and determinism, with feasibility passing for all six seeds. [`A1-ADVERSARIAL-AUDIT.md`](docs/A1-ADVERSARIAL-AUDIT.md) records the passing six-seed feasibility, future-blindness, determinism, report-blindness and sleep-blindness checks. `a1_two_path.preflight` now checks four-per-seed, disjoint endpoints, world-universe membership, artifact equality and the selection digest, and allows the selection artifact as a seed-bearing record. `tests/test_a1_prefreeze.py` adds ten tests for pre-sleep ordering, the `U` fields, deterministic magnitude-blind selection, the four-disjoint rule, target-set failures, the selector self-test and artifact consistency. **No target is frozen into the manifest, no seed is reserved, no grant exists and no A1 cell has run.** The [power/prevalence review](docs/A1-POWER-REVIEW.md) finds that four target rows make the 0.95 C1 floor effectively 100%; C4 non-target rows are needed to enlarge the denominator. No freeze follows. The separate [pre-freeze checklist](docs/A1-PRE-FREEZE-CHECKLIST.md) and [protocol compliance report](docs/A1-PROTOCOL-COMPLIANCE-REPORT.md) record the nine must-pass P0 conditions as passing and keep freeze and grant explicitly open. The roadmap and report now state the chain directly: **P0 PASS → target feasibility PASS → freeze readiness OPEN → grant OPEN → run NOT STARTED**. Separately, the generated Stage B protocol record now reports 1,656 consumed seeds across 214 artifacts; the scan grew because the A1 audit and manifest are seed-bearing. No Stage B world ran. Verification: 91 targeted A1, documentation and Stage B tests passed, along with the selector, preflight, audit and gate checks; the full suite was not re-recorded because it exceeds the five-minute command window in this environment. `benchmarks/a1_arms.py`, `benchmarks/a1_target_selection.py`, `benchmarks/a1_adversarial_audit.py`, `benchmarks/a1_two_path.py`, `tests/test_a1_prefreeze.py`, `docs/a1_target_selection.json`, `docs/a1_adversarial_audit.json`, `docs/A1-TARGET-SELECTION.md`, `docs/A1-ADVERSARIAL-AUDIT.md`, `docs/A1-TARGET-SELECTION-PROTOCOL.md`, `docs/A1-PROTOCOL-COMPLIANCE-REPORT.md`, `docs/A1-PRE-FREEZE-CHECKLIST.md`, `docs/a1_two_path_manifest.json`, `docs/A1-TWO-PATH-MANIFEST.md`, `ROADMAP.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

### Drafted — A1 target-selection protocol with cycle-36 U sampling (2026-11-14)

- **The missing per-seed target rule is now a protocol, not a frozen target set.** `docs/A1-TARGET-SELECTION-PROTOCOL.md` fixes four disjoint target edges per seed, chosen from the pre-cycle-37 world universe by an outcome-blind hash order, with cycle membership in the cycle-36 temporal graph as a pre-carrier eligibility proxy. It defines `U` as direct count, reverse count and strength, sampled before the cycle-36 sleep/consolidation so it is before carrier, `K` and `Y`; it also records that `benchmarks/a1_arms.py` currently samples after sleep and must be corrected before freeze. The protocol selects no edge, reserves no seed, freezes no manifest, authorises no cell and records no result. Remaining pre-freeze work: the corrected sampler, the no-arm selection pass and artifact, the future/report/sleep-blindness and feasibility checks, extended `preflight` checks, C4 non-target rows, and a power/prevalence review for `N = 4`. `docs/A1-TARGET-SELECTION-PROTOCOL.md`, `ROADMAP.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

### Recorded — A1 is committed to target resolution, not authorised to run (2026-11-14)

- **A1 leaves the permanent "registered but unfrozen, ungranted, unexecuted" state by committing to a target-resolution path, without opening a cell.** `docs/DECISION-A1-DISPOSITION.md` records the dated program disposition: produce and review a pre-outcome target-selection protocol, fix the per-seed target edges, freeze the manifest against them, and then put a dated run-authorising grant decision to the owner. It explicitly does not freeze the manifest, reserve seeds 20630101–20630106, authorise a cell, issue a grant, clear C1–C9 or record a result; the gate must still refuse. If no protocol and dated grant decision are recorded by **2026-12-14**, the disposition lapses to **A1 PARKED** by default, with the reason naming whether the target set was not formed, no admissible rule existed, or no grant was made. `docs/decisions.json` indexes it as **ADOPTED** under Q054, and the decision page, registry page, roadmap, manual and changelog carry the same disposition. No engine, cell, seed, grant, verdict or result changed. `docs/DECISION-A1-DISPOSITION.md`, `docs/decisions.json`, `docs/DECISIONS.md`, `docs/research_question_registry.json`, `docs/RESEARCH-QUESTION-REGISTRY.md`, `ROADMAP.md`, `docs/USER-MANUAL.md`, `CHANGELOG.md`.

### Built — self-testing CI guard for the G9 validator step (2026-11-14)

- **The G9 stage-ledger validator step can no longer be silently removed or weakened.** `benchmarks/g9_ci_guard.py` finds the exact `G9 stage-ledger validator and six-class self-test` step in `.github/workflows/tests.yml`, requires both `python -m benchmarks.g9_stage_ledger --check` and `--self-test` as exact commands, and rejects a missing, duplicated, renamed, disabled, comment-only or fail-open step without a run block. Its `--self-test` proves each rejection fires. The workflow runs the guard before the validator step, and `tests/test_g9_ci_guard.py` runs both guard commands in the local pytest suite as well. The full suite is re-recorded at **2,281 passed, 19 skipped, 0 failed of 2,300 collected (2026-11-14)**. No engine, cell, seed, grant, verdict or result changed. `benchmarks/g9_ci_guard.py`, `tests/test_g9_ci_guard.py`, `.github/workflows/tests.yml`, `docs/test_count.json`, `docs/USER-MANUAL.md`.

### Built — the A1 readiness CI guard also runs in pytest (2026-11-14)

- **The A1 workflow guard is now exercised by the local suite, not only by GitHub Actions.** `tests/test_a1_ci_guard.py` invokes `benchmarks.a1_ci_guard --check` against the committed workflow and `--self-test` against every tamper shape, so a local `pytest` run fails if the A1 readiness step is removed, renamed, disabled, made fail-open or stripped of either exact command. The workflow steps are unchanged. The full suite is re-recorded at **2,279 passed, 19 skipped, 0 failed of 2,298 collected (2026-11-14)**. No engine, cell, seed, grant, verdict or result changed. `tests/test_a1_ci_guard.py`, `docs/test_count.json`, `docs/USER-MANUAL.md`.

### Repaired — the decision graph covers the progression decision and its registry counts are current (2026-11-14)

- **The unindexed G8→G9 progression decision is now in the decision graph, and the registry's current 54/25 counts are pinned.** `docs/decisions.json` gains `DECISION-PROGRESSION-BEYOND-G8` as **ADOPTED**, quoting the document's own status, chosen actions and evidence. `benchmarks/decision_graph.py` now treats a `future` question as live while a named prerequisite is live, so a deferred question does not falsely orphan its decision; a retired-only decision still fails. The 0.13.0 changelog's 53/24 count is retained as the historical value and the current 54/25 count is stated beside it, with the guard re-pinned. The same repair rebuilt the derived registry views: `docs/question_survival.json` and its page, `docs/RESEARCH-DASHBOARD.md`, `docs/RERUN-CAMPAIGN-PLAN.md` (25 first answers, 6 gated, 54 registry questions), `docs/ACTION-PLAN.md` (37 reviewed, 6 prerequisite-gated), and the Stage B artifact and page (214 scanned artifacts). The full suite is re-recorded at **2,277 passed, 19 skipped, 0 failed of 2,296 collected (2026-11-14)**. No engine, cell, seed, grant, verdict or result changed. `docs/decisions.json`, `docs/DECISIONS.md`, `benchmarks/decision_graph.py`, `tests/test_decision_graph.py`, `tests/test_changelog_figures.py`, `CHANGELOG.md`, `docs/USER-MANUAL.md`.

### Wired — G9 stage-ledger validator and six-class self-test run in CI (2026-11-14)

- **The G9 stage-ledger validator now runs in CI next to the A1 readiness checks.** `.github/workflows/tests.yml` runs `python -m benchmarks.g9_stage_ledger --check` and `python -m benchmarks.g9_stage_ledger --self-test` immediately after the A1 gate-readiness step and before pytest. `--check` verifies the committed six-row fixture, the generated validator page and one-row-per-class coverage; `--self-test` independently exercises every class and every invariant. The validator still creates no real ledger, runs no engine, assigns no seed and authorises no G9 design. `benchmarks/g9_stage_ledger.py`, `.github/workflows/tests.yml`, `docs/G9-STAGE-LEDGER-VALIDATOR.md`, `docs/USER-MANUAL.md`.

### Recorded — V2 is reserved for a mechanism-driven architectural redesign (2026-11-14)

- **The roadmap now fixes the version boundary: V2 is reserved for a mechanism-driven architectural redesign, and current work is 0.x.** The dated planning decision records that instrumentation, governance, preregistration, measurement, audit and record repair — including A1, M1 and the G9/activation framing — must not be named, versioned or scoped as V2. V2 becomes eligible only after M1 routes a mechanism-bearing branch (M1-C, M1-A, M1-CC or M1-RO) and G4 passes with a named architectural target; M1-X and M1-V license no V2. The decision creates no V2 design, version, feature, claim, seed, cell, grant or result, does not move package 0.15.0, and does not re-score any verdict. `ROADMAP.md`, `docs/USER-MANUAL.md`.

### Built — self-testing guard for the A1 readiness CI step (2026-11-14)

- **The A1 readiness step can no longer be silently deleted or weakened without failing CI.** `benchmarks/a1_ci_guard.py` finds the exact `A1 gate readiness and stop conditions` block in `.github/workflows/tests.yml` and requires both `python -m benchmarks.a1_gate_readiness --check` and `--self-test` as exact commands. It rejects a missing or duplicated step, a renamed step, a comment-only command, `if: false`, `continue-on-error: true` and a missing run block. Its `--self-test` proves each rejection fires. The workflow runs the guard before the A1 step, so removing that step leaves the guard in place to fail the job. No engine, cell, seed, grant, verdict or result changed. `benchmarks/a1_ci_guard.py`, `.github/workflows/tests.yml`, `docs/USER-MANUAL.md`.

### Built — A-/K-/Y- treatments behind the A1 freeze, target and grant gate (2026-11-14)

- **The A-/K-/Y- arms are implemented, but the current manifest still refuses every cell.** `benchmarks/a1_arms.py` subclasses the shipped `SleepService` without editing an engine file. `A−` filters only the target edge from `report.predictions`; `K−` filters only loops/dreams carrying the target from the structure-to-assertion readout; `Y−` masks the target's assertion row while leaving admission and carrier formation untouched. `A−K−` applies both filters as the third-route control. The runner checks the dated grant, freeze status, planned cell, fixed target set and target-in-world before `_make_scratch_db`; the manifest now records target edges as **unresolved** and `U` at cycle 36. `--self-test` proves each filter removes its target and preserves the other path. No target edge, cell, seed, engine file, verdict or result changed. `benchmarks/a1_arms.py`, `benchmarks/a1_two_path.py`, `docs/A1-TWO-PATH-MANIFEST.md`, `docs/a1_two_path_manifest.json`, `ROADMAP.md`, `docs/TWO-PATH-ADMISSION-CARRIER-DESIGN.md`, `docs/USER-MANUAL.md`.

### Built — G9 stage-ledger validator with six-class synthetic fixtures (2026-11-14)

- **The six-class stage ledger is now executable and fail-closed.** `benchmarks/g9_stage_ledger.py` validates unique `(seed, edge)` coverage of the fixed universe, present cycles as integers in `1..cycles`, a formed stage on every row, served-implies-admitted, `served >= admitted` and `asserted >= formed`, and per-stage `observed` provenance so a final assertion cannot fill a missing service cycle. Its committed six-row fixture has exactly one row in each of A–F; the self-test proves every class is classified and every invariant rejects a targeted defect. The validator does not create a real ledger, run a cell, assign a seed or authorise G9. `benchmarks/g9_stage_ledger.py`, `docs/G9-STAGE-LEDGER-VALIDATOR.md`, `docs/g9_stage_ledger_fixtures.json`, `docs/G9-ACTIVATION-DESIGN.md`.

### Wired — A1 readiness and stop-condition self-test run in CI (2026-11-14)

- **A stale A1 readiness record or a missing terminal stop condition now fails CI.** `.github/workflows/tests.yml` runs `python -m benchmarks.a1_gate_readiness --check` and `python -m benchmarks.a1_gate_readiness --self-test` after the C6 guard and before pytest. `--check` verifies the readiness and threshold artifacts are current; `--self-test` proves every contract accepts its fixture and rejects its targeted defect, and that a missing or multi-attempt bound is refused. A second step checks that the A1 block itself remains in the workflow, so deleting it fails CI. The step is separate from pytest so the failure names the A1 gate. No engine, cell, seed, grant, verdict or result changed. `.github/workflows/tests.yml`, `docs/USER-MANUAL.md`.

### Built — A1 two-path dry-run manifest and fail-closed grant gate (2026-11-14)

- **The A-/K-/Y- cells now have a manifest and a gate; at that point they had no grant or arm.** **Superseded later on 2026-11-14:** the treatments are now implemented in `benchmarks/a1_arms.py`; there is still no grant and the target edges remain unresolved. `benchmarks/a1_two_path.py` fixes six seeds × six cells (`A+K+`, `A+K-`, `A-K+`, `A-K-`, `Y−` at `A+K+` and `A−K+`) plus a fresh-process determinism control: 36 cells + 1 control, 120 cycles, cap 40. `--dry-run` prints 37 commands without opening a database. `--cell` and `--measure` call `refuse()` before any database and exit 2: no dated grant is recorded and the arms are not implemented. The gate also checks the shipped build, planned cells, U-before-carrier/K/Y, the object fingerprint and seed freshness. Candidate seeds 20630101–20630106 are explicitly not reserved or frozen. `benchmarks/a1_two_path.py`, `docs/A1-TWO-PATH-MANIFEST.md`, `docs/a1_two_path_manifest.json`, `ROADMAP.md`, `docs/USER-MANUAL.md`. No cell, seed, engine file, verdict or result changed.


### Recorded — G9 has outcome criteria and a six-class activation ledger, not a G9 design (2026-11-14)

- **The G9 question is now defined by falsifiable outcomes rather than architecture.** `docs/G9-ACTIVATION-DESIGN.md` fixes four conjunctive criteria: **G9-A** activation control, **G9-B** development-dependent behaviour, **G9-C** self-modification of future development, and **G9-D** external relevance. It adds an edge-level stage ledger over formation, admission, service, assertion and carrier timing, with **six classes A–F**; classes E and F preserve the admitted-but-latent and served-but-not-asserted cases a four-class table would hide. The ladder is map → classify → one intervention, and each phase has a stop condition. G9 remains locked until X1 and all four criteria pass, and passing them still requires a separate G9 design and owner decision. No seed, cell, engine file, verdict or result changed. `docs/G9-ACTIVATION-DESIGN.md`, `docs/DECISION-PROGRESSION-BEYOND-G8.md`, `ROADMAP.md`, `docs/GATE-BOARD.md`, `docs/research_question_registry.json`, `docs/RESEARCH-QUESTION-REGISTRY.md`, `docs/USER-MANUAL.md`. No engine, cell, seed or verdict changed.


### Recorded — Progression beyond G8 is gated on activation, not a G9 design (2026-11-14)

- **The next objective is activation/use, not unlocking Generation 9.** `docs/DECISION-PROGRESSION-BEYOND-G8.md` separates formation, admission, service, assertion and activation/use; records that the formation-utilization campaign mapped the gap to the use path while the follow-up use-path diagnostic failed its D0 gate and cannot identify retrieval, activation or readout; and makes `X1 — External activation` the G8 → G9 gate. X1 requires A1/M1 routing, an A3 external endpoint, ablation that removes the advantage, and independent replication. A negative, `VOID` or non-ablating A3 reads `EXTERNAL ACTIVATION NOT ESTABLISHED` and closes the path; no G9 design, extra endpoint or instrumentation loop. Generation 9 remains locked. The roadmap date and suite count are corrected in the same edit. Q056 registers the activation question as future, blocked by Q054; the tally is now 15 closed, 31 open, 2 retired and 6 future from 54 questions. No seed, cell, engine file, verdict or result changed. `docs/DECISION-PROGRESSION-BEYOND-G8.md`, `ROADMAP.md`, `docs/GATE-BOARD.md`, `docs/research_question_registry.json`, `docs/RESEARCH-QUESTION-REGISTRY.md`, `docs/USER-MANUAL.md`. No engine, cell, seed or verdict changed.


### Recorded — Every open A1 gate has a one-attempt stop condition (2026-11-14)

- **The admissibility layer now has a terminal outcome, not only another instrumentation round.** `docs/A1-GATE-READINESS.md` records for C1-C5 and C7-C9 one implementation/run attempt, the success rule, the failure disposition and the unmeasurable disposition. A failed or unmeasurable gate closes A1 as `NOT IDENTIFIED`, `VOID`, `THIRD ROUTE PRESENT`, `SHARED CAUSE / NO CARRIER RELATION NOT SEPARATED` or `UNSATISFIABLE`; no A1 patch, threshold change, extra cell or rerun is permitted, and a new registered design is required. `benchmarks/a1_gate_readiness.py` refuses to write an unbounded record, and its self-test proves a missing or multi-attempt bound is caught. C6 remains the only satisfied gate; no grant exists and no cell ran. `benchmarks/a1_gate_readiness.py`, `docs/A1-GATE-READINESS.md`, `docs/a1_gate_readiness.json`, `docs/C1-C9-PREFLIGHT.md`, `ROADMAP.md`, `docs/research_question_registry.json`, `docs/RESEARCH-QUESTION-REGISTRY.md`, `docs/USER-MANUAL.md`. No engine, cell, seed or verdict changed.


### Recorded — A1 manipulation and completeness thresholds are precommitted (2026-11-14)

- **The A1 gaps that could be closed without a run are closed.** `docs/A1-PRECOMMITTED-THRESHOLDS.md` fixes C1 at **0.95 preservation** of the other path on every seed, measured on the paired control's available edges; C4 and C7 at a **0.05 absolute-rate margin**; and C8 at a **0.05 assertion ceiling** in `A-K-`. The values were fixed before any A1 cell and are not estimated from A0 or any run; a descriptive sensitivity at 0 and 0.10 may be reported but cannot change the gate. The same constants live in `benchmarks/a1_gate_readiness.py`, so the contracts, the readiness record and the threshold record cannot drift. C6 remains the only satisfied gate; the other eight remain **`CONTRACT BUILT, NOT RUN`**, no grant exists and no cell ran. `benchmarks/a1_gate_readiness.py`, `docs/A1-PRECOMMITTED-THRESHOLDS.md`, `docs/a1_precommitted_thresholds.json`, `docs/A1-GATE-READINESS.md`, `docs/TWO-PATH-ADMISSION-CARRIER-DESIGN.md`, `docs/C1-C9-PREFLIGHT.md`, `ROADMAP.md`, `docs/research_question_registry.json`, `docs/RESEARCH-QUESTION-REGISTRY.md`, `docs/USER-MANUAL.md`. No engine, cell, seed or verdict changed.


### Recorded — A1 C1-C5 and C7-C9 have executable gate contracts, not clearance (2026-11-14)

- **The remaining A1 gates are now machine-checkable but still unrun.** `benchmarks/a1_gate_readiness.py` defines contracts for path separation, treatment consistency, positivity, no interference, pre-outcome `U`, assertion blockade, the `A-K-` ceiling and same-object pairing. Its `--self-test` builds a passing six-cell fixture and a targeted defect for every gate, and proves a missing C1/C4/C7 tolerance or C8 ceiling fails. C6 stays satisfied by `C6-TIMING-1`; the other eight are **`CONTRACT BUILT, NOT RUN`** because the committed records contain only the 26-row `A-K+` slice, no arm artifact and no paired cells. The design remains **not admissible**. `docs/A1-GATE-READINESS.md`, `docs/a1_gate_readiness.json`, `docs/C1-C9-PREFLIGHT.md`, `ROADMAP.md`, `docs/USER-MANUAL.md`. No engine, cell, seed or verdict changed.


### Recorded — Cap-112 run provenance is reclassified provisional (2026-11-14)

- **The two cap-112 run records are provisional and not owner-authorised.** `docs/AUTHORISATION-PROVENANCE-AUDIT.md` found that `PRESENCE-COMPARATOR-112` (7 cells, `PRESENCE NOT ASSERTION`) and `PRESENCE-CAP-1-112` (25 cells, `CAP LIMITING`) cite an instruction to write the grant document, not an owner authorisation to run cells. No run-authorising quote is recorded, and none was invented. `docs/CAP-112-PROVENANCE-DISPOSITION.md` reclassifies both runs as **provisional and not owner-authorised**: their numerical results, gates, statuses, seeds and artifacts stand unchanged, but they are not confirmatory. The stale `not_evidence` text was replaced in both records and their result pages, and the shared grant document carries a dated correction. `PRESENCE-CONSTRUCT-1-112` remains unrun under the preparation-only quote. The authorisation guard still reports both records by design; B0 closes through the explicit-disposition branch. `docs/presence_comparator_112_prereg.json`, `docs/presence_cap_1_112_prereg.json`, `docs/presence_comparator_112_run.json`, `docs/presence_cap_1_112_run.json`, `docs/PRESENCE-COMPARATOR-112-RESULT.md`, `docs/PRESENCE-CAP-1-112-RESULT.md`, `docs/AUTHORISATION-PRESENCE-CAP-112.md`, `docs/AUTHORISATION-PROVENANCE-AUDIT.md`, `ROADMAP.md`, `docs/PROJECT-REPORT.md`, `docs/RESEARCH-HIERARCHY.md`, `docs/USER-MANUAL.md`. No cell was rerun and no verdict moved.


### Audited — Cap-112 run records cite a preparation-only authorisation quote (2026-11-13)

- **Two `FROZEN, RUN` records do not contain the owner's run words.** `docs/AUTHORISATION-PROVENANCE-AUDIT.md` audits 14 `docs/AUTHORISATION-*.md` documents and 21 records with an `authorisation` block. `PRESENCE-COMPARATOR-112` (7 cells, `PRESENCE NOT ASSERTION`) and `PRESENCE-CAP-1-112` (25 cells, `CAP LIMITING`) cite "Write the dated cap-112 authorisation document ... recording the owner's grant", which authorises preparation, not a run. `PRESENCE-CONSTRUCT-1-112` is `FROZEN, NOT RUN` under the same quote. `PRESENCE-BAND-3` is preparation-only but correctly unrun. The two cap-112 run records also retain stale `not_evidence` text saying no cell has executed. No gate, coefficient, status or result was changed; no quote was invented and no cell was rerun. `docs/AUTHORISATION-PROVENANCE-AUDIT.md`, `docs/RESEARCH-HIERARCHY.md`, `docs/USER-MANUAL.md`. Stage B is unchanged at **1644** consumed seeds across **209** artifacts.

### Built — The entry-transition runner captures full appearance cycles and refuses without a grant (2026-11-13)

- **The runner is built; no grant or cell exists.** `benchmarks/retention_entry_transition.py` replays each of the 24 planned seeds, captures every never-served world edge's complete sorted structure-appearance list across all 120 cycles, and defines the event as the first sustained two-cycle entry at `f + 40` or later after a structure-free interval through `f + 39`. `--dry-run` prints the 24 commands without opening a database; `--cell`, `--measure` and `--finish` call `refuse()` before a scratch database and exit 2 while the dated grant is missing. `--finish` applies D1-D10 and P1-P4, with final presence at cycle 120 descriptive only. The pre-finish loader rejects parts with incomplete 120-cycle capture, non-integer row appearance cycles, row appearance cycles outside 1..120, duplicate row edges within a seed, row seeds that differ from their part, duplicate planned seeds, and an empty planned seed block. `tests/test_retention_entry_transition.py` proves the dry-run opens no database, the ungranted paths refuse before one, and one-cycle flickers, re-entries and early presence are not counted. The record moves to `runner.built: true`, `cells_run: 0`; it remains `FROZEN, NOT RUN` with no grant and no result. `docs/retention_entry_transition_prereg.json`, `docs/RETENTION-ENTRY-TRANSITION-PREREGISTRATION.md`, `docs/RETENTION-ENTRY-TRANSITION-DESIGN.md`, `docs/RESEARCH-HIERARCHY.md`, `docs/USER-MANUAL.md`. Stage B is unchanged at **1644** consumed seeds across **209** artifacts.

### Guarded — A true first structure entry is distinguished from a re-entry (2026-11-13)

- **New captures record `first_structure_cycle`, and eligibility rejects a pre-landmark presence when that field is present.** The old `assertion_cycle` helper only looked after the landmark, so an edge present before it and returning later could count as a first assertion. Legacy parts have no `first_structure_cycle`; they still adjudicate to **172** eligible edges and **70** events, so the recorded result and verdict are unchanged. A regression test proves a true first entry is admitted while a re-entry with the same post-landmark assertion cycle is not. `benchmarks/retention_formation_anchored.py`, `tests/test_retention_formation_anchored.py`, `docs/USER-MANUAL.md`. Stage B is unchanged at **1644** consumed seeds across **209** artifacts.

### Frozen — The entry-transition preregistration is frozen with 24 seeds and D1-D10 (2026-11-13)

- **`CONFIRMATORY-RETENTION-ENTRY-TRANSITION-1` is frozen before any cell.** `docs/retention_entry_transition_prereg.json` and `docs/RETENTION-ENTRY-TRANSITION-PREREGISTRATION.md` fix 24 fresh seeds (`20620101-20620124`), 120 cycles, cap 40, a structure-free interval through `f + 39`, and a two-cycle sustained entry at `f + 40` or later. Early retention (`f..f+19`) and proximal retention (`f+20..f+39`) are both measured before the outcome; the primary joint model tests early retention beyond proximal retention, rank, count, strength and follow-up. The record is `FROZEN, NOT RUN`: no grant, part or result exists, and `cells_run` is 0. **Runner built later on 2026-11-13:** see the Built entry above. `benchmarks/retention_entry_transition_prereg.py`, `tests/test_retention_entry_transition_prereg.py`, `docs/RETENTION-ENTRY-TRANSITION-DESIGN.md`, `docs/RESEARCH-HIERARCHY.md`, `docs/USER-MANUAL.md`. Stage B moved to **1644** consumed seeds across **209** artifacts.

### Corrected — The grant provenance quotes the actual run authorisation (2026-11-13)

- **The preregistration no longer presents the preparation instruction as the run grant.** `docs/retention_formation_anchored_prereg.json` now quotes the actual authorisation, "Fix the post-landmark assertion cycle and rerun the twelve cells", and retains the earlier preparation instruction as `preparation_quote` only. The grant document and generated preregistration page show both the document's origin and the run authorisation. `docs/AUTHORISATION-RETENTION-FORMATION-ANCHORED-1.md`, `docs/RETENTION-FORMATION-ANCHORED-PREREGISTRATION.md`, `benchmarks/retention_formation_anchored_prereg.py`, `tests/test_retention_formation_anchored_prereg.py`, `docs/USER-MANUAL.md`. No cell, seed, gate or verdict changed; Stage B is unchanged at **1620** consumed seeds across **208** artifacts.

### Audited — The reverse retention model is stable to the follow-up control but is a boundary contrast (2026-11-13)

- **The reverse OR is not a follow-up collinearity artifact.** On the 166 fitted cases in `docs/retention_formation_anchored.json`, `late_retention` and `followup` correlate at Pearson **−0.298** (seed-residual **−0.323**); pairwise VIF is **1.097**, late multivariate VIF **1.199**. Dropping follow-up leaves the late OR at **33.50** (9.05–124.03) versus **32.83** (8.66–124.44), and a raw late count gives **31.43** (9.15–107.87).
- **The coefficient is a boundary contrast, not a dose-response.** **11/11** edges at `late_retention = 1.0` are asserted, against **1/55** at **0.0** and **58/100** in between. Report those counts beside the OR. The verdict remains `CONFIRMED, TEMPORALLY AMBIGUOUS`; no cell, seed, gate or coefficient was changed. `docs/RETENTION-REVERSE-OVERLAP-AUDIT.md`, `docs/RESEARCH-HIERARCHY.md`, `docs/USER-MANUAL.md`. Stage B is unchanged at **1620** consumed seeds across **208** artifacts.

### Guarded — Retention preflights reject preparation-only quotes (2026-11-13)

- **A preparation instruction cannot pass as a run authorisation.** `benchmarks/authorisation_guard.py` classifies a quote as preparation-only when it contains preparation language such as `without running`, `before running`, `write the dated` or `record its grant`, and contains no run/authorise/execute word. A `FROZEN, RUN` record with such a quote is rejected. The guard is wired into the retention formation, entry-transition and incremental preflights. The recorded formation run quote (`Fix the post-landmark assertion cycle and rerun the twelve cells`) passes; the cap-112 preparation quote does not. `tests/test_authorisation_guard.py` proves both, and `scan()` flags the two known cap-112 run records without changing their status, results or gates. `docs/AUTHORISATION-PROVENANCE-AUDIT.md`, `docs/USER-MANUAL.md`. Stage B is unchanged at **1644** consumed seeds across **209** artifacts.
- **The guard has a check mode.** `python -m benchmarks.authorisation_guard --check` prints every violation and exits `1`; it currently reports the two known cap-112 records. The clean path exits `0`. `tests/test_authorisation_guard.py` covers both paths.

### Reported — The reverse boundary now carries the middle group (2026-11-13)

- **The boundary table now reports zero, middle and ceiling groups.** `docs/retention_formation_anchored.json` adds `late_mid_edges: 100` and `late_mid_events: 58`; `docs/RETENTION-FORMATION-ANCHORED.md` renders **1/55** at 0.0, **58/100** in between, **11/11** at 1.0. The counts are recomputed from the existing 166 fitted rows and add no cell, seed or gate. `docs/RETENTION-REVERSE-OVERLAP-AUDIT.md`, `docs/RESEARCH-HIERARCHY.md`, `docs/USER-MANUAL.md`. Stage B is unchanged at **1644** consumed seeds across **209** artifacts.

### Designed — A retention follow-up uses a distinct structure-entry transition (2026-11-13)

- **The next retention block targets a transition, not a snapshot.** `docs/RETENTION-ENTRY-TRANSITION-DESIGN.md` proposes `PROPOSED-RETENTION-ENTRY-TRANSITION-1` on 24 fresh seeds (`20620101-20620124`). An eligible edge must be structure-free through `f + 39`; the event is the first two-cycle structure entry at `f + 40` or later. Early retention (`f..f+19`) and proximal retention (`f+20..f+39`) are both measured before the outcome, and the primary joint model tests early retention beyond proximal retention, rank, count, strength and follow-up. The design was `DESIGN, NOT FROZEN`: no grant, runner, cell or result existed, and the prior block is not re-scored. `docs/RETENTION-ENTRY-TRANSITION-DESIGN.md`, `docs/RESEARCH-HIERARCHY.md`, `docs/USER-MANUAL.md`. Stage B was then unchanged at **1620** consumed seeds across **208** artifacts. **Frozen later on 2026-11-13:** the design became `CONFIRMATORY-RETENTION-ENTRY-TRANSITION-1` with 24 seeds and D1-D10; see the frozen entry above and Stage B **1644** seeds across **209** artifacts.

### Repaired and tested — Formation-anchored retention is confirmed but temporally ambiguous (2026-11-12)

- **The runner now uses the frozen post-landmark onset.** The first version took the first structure appearance over all cycles; the preregistration defines `assertion_cycle` as the first appearance strictly after the edge's landmark. The corrected helper enforces that, and the invalid pre-fix parts and result are preserved under `.scratch/retention_formation_anchored/invalid_pre_fix/`.
- **All twelve cells were rerun at 120 cycles.** The corrected collection found **434** never-served edges, **180** loop-forming edges, **172** eligible edges and **70 asserted events**; the late cohort had **36** edges and **18** events. All nine gates pass.
- **Early retention is positive, but late retention is stronger.** The primary early-retention OR is **2.09** per SD (**1.36–3.23**); the reverse post-landmark OR is **32.83** (**8.66–124.44**). P1–P3 pass and R1 fails, so the frozen verdict is **`CONFIRMED, TEMPORALLY AMBIGUOUS`**: the block does not establish that early retention precedes assertion. The late-cohort early-retention OR is **2.14** (**0.60–7.59**). `benchmarks/retention_formation_anchored.py`, `docs/retention_formation_anchored.json`, `docs/RETENTION-FORMATION-ANCHORED.md`, `tests/test_retention_formation_anchored.py`. Stage B is **1620** consumed seeds across **208** artifacts.

### Authorised — The formation-anchored block has a dated grant and remains unrun (2026-11-12)

- **The owner's dated grant is recorded.** `docs/AUTHORISATION-RETENTION-FORMATION-ANCHORED-1.md` records the grant for the twelve frozen cells (seeds `20619101-20619112`, 120 cycles, cap 40), the per-edge 20-cycle window, the single `followup` horizon control, gates M1-M9 and criteria P1-P3/R1. The owner's instruction is quoted verbatim.
- **The grant document does not run a cell.** The record moves to `GRANTED, NOT RUN`; `authorisation.granted` is true, `runner.built` is true and `cells_run` is 0. No part, result, gate or verdict exists, and execution remains a separate action under the grant.
- **The model amendment precedes the grant.** `formation` is descriptive and `followup` is the single fitted horizon control; the `model-identification` amendment is dated 2026-11-12 and marked `before_grant: true`. `docs/AUTHORISATION-RETENTION-FORMATION-ANCHORED-1.md`, `docs/retention_formation_anchored_prereg.json`, `docs/RETENTION-FORMATION-ANCHORED-PREREGISTRATION.md`, `tests/test_retention_formation_anchored_prereg.py`. Stage B is **1620** consumed seeds across **207** artifacts.

### Built — The formation-anchored retention block has a grant-gated runner (2026-11-12)

- **The runner collects the per-edge window, not a calendar landmark.** `python -m benchmarks.retention_formation_anchored --dry-run` prints the twelve frozen commands without opening a database. `--cell SEED` and `--measure` call the grant gate before `_make_scratch_db`, so the ungranted block cannot spend a seed.
- **The model uses one horizon control.** `formation` and `followup` are exact affine transforms; before any grant or seed replay, `formation` was removed from the fitted predictors and `followup` became the single horizon control. The amendment is recorded in the preregistration.
- **A granted cell would capture the first twenty cycles from formation.** It records `rank20`, `count20`, `strength20`, early retention, post-landmark retention, follow-up horizon, the first assertion cycle and the final assertion label. `--finish` fits the Firth primary and reverse models with twelve seed fixed effects, applies M1-M9 and P1-P3/R1, and writes `docs/retention_formation_anchored.json` and `docs/RETENTION-FORMATION-ANCHORED.md`. It marks the record `FROZEN, RUN` only after all twelve parts exist.
- **No grant, seed or result.** The record stays `FROZEN, NOT RUN`, `authorisation.granted` is false, `runner.built` is true and `cells_run` is 0. `--check` reports the runner ready and the missing grant; no part or result exists. `benchmarks/retention_formation_anchored.py`, `tests/test_retention_formation_anchored.py`, `benchmarks/retention_formation_anchored_prereg.py`, `docs/retention_formation_anchored_prereg.json`, `docs/RETENTION-FORMATION-ANCHORED-PREREGISTRATION.md`. Stage B is **1620** consumed seeds across **207** artifacts.

### Registered — A formation-anchored retention follow-up admits late-forming loop edges (2026-11-12)

- **The cycle-60 failure is answered with a per-edge window, not a re-score.** `CONFIRMATORY-RETENTION-FORMATION-ANCHORED-1` uses fresh seeds `20619101-20619112`, 120 cycles and cap 40. Every eligible edge gets the same **20-cycle** predictor window from its own first loop, through `formation + 19`; the population admits loop-forming never-served edges with `formation_cycle <= 90` that were not asserted in that window.
- **Late-forming edges are a named part of the claim.** Edges with `formation_cycle > 60` form the late cohort. Gate **M9** requires at least **10** eligible late edges and **3** asserted late events; if it fails, the block is `VOID` and no late-forming claim is read. A `followup/120` control accounts for the shorter outcome horizon of late edges.
- **The primary is all-cohort early retention, with the late cohort reported separately.** The model is Firth logistic with seed fixed effects and rank20, count20, strength20 and the follow-up horizon control; formation is descriptive. The reverse-time model uses post-landmark late retention; a positive late result makes the verdict `CONFIRMED, TEMPORALLY AMBIGUOUS`.
- **No grant or result.** The block is `FROZEN, NOT RUN`, `authorisation.granted` is false, `runner.built` is true and `cells_run` is 0. It spends no seed and makes no claim. `benchmarks/retention_formation_anchored_prereg.py`, `docs/retention_formation_anchored_prereg.json`, `docs/RETENTION-FORMATION-ANCHORED-PREREGISTRATION.md`, `tests/test_retention_formation_anchored_prereg.py`. Stage B is **1620** consumed seeds across **207** artifacts.

### Tested — Retention incremental is VOID at the cycle-60 landmark (2026-11-12)

- **Twelve cells ran under the owner's dated grant.** `CONFIRMATORY-RETENTION-INCREMENTAL-1` ran seeds `20618101-20618112` for 120 cycles at cap 40, authorised in `docs/AUTHORISATION-RETENTION-INCREMENTAL-1.md`, and adjudicated with its frozen `--finish`.
- **The landmark population has 103 edges but no asserted events.** The twelve parts contain **399** never-served world edges, **181** loop-forming edges and **103** edges that formed by cycle 60 and were not asserted at the landmark. **0** of those 103 were asserted by cycle 120. The **16** late assertions in the whole never-served set all formed after cycle 60.
- **M1 population fails, so no coefficient is read.** The block required at least 60 eligible edges and 20 asserted events; the edge count passes and the event count is zero. The verdict is **`VOID`**, the criteria are marked not read, and no retention, temporal-order, capability, causal or general engine claim follows from the fitted numbers.
- **A preliminary collection was discarded before adjudication.** Seven seeds initially stopped at 88-92 cycles because a withheld acquisition event at a block boundary skipped that sleep. The boundary handling was fixed, all twelve parts were regenerated at 120 cycles, and no preliminary part entered the result. `benchmarks/retention_incremental.py`, `docs/retention_incremental.json`, `docs/RETENTION-INCREMENTAL.md`, `docs/AUTHORISATION-RETENTION-INCREMENTAL-1.md`, `tests/test_retention_incremental.py`. Stage B is **1608** consumed seeds across **206** artifacts.

### Tested — The core+band guarantee is non-binding at 112, but cold-start gates make the block VOID (2026-11-12)

- **Twelve cells on six fresh seeds, `20617101-20617106`, at cap 112.** `CORE-BAND-ADMISSION-1` compared the normal cap-112 window with a guarantee that the rank-1-20 core and rank-21-40 band are served. The tier had **22,753** available edge-slots per arm; both arms served **22,753** of them (**1.0000** coverage), made **zero replacements**, and produced identical per-cycle window digests on every seed. The false-admission rate was **0.7016** in both arms, a difference of **0.0000**.
- **The block is `VOID`, not a recovery verdict.** Gates C3 and C4 fail on cold-start cycles: C3 requires a positive tier in every cycle, while the first cycles have none, and C4 requires every served window to contain 112 rows, while early windows are shorter as the engine fills its candidate pool. Every full window contained 112 rows and no window exceeded 112, but the frozen table does not permit a gate repair after the run.
- **The descriptive reading is that the rule is non-binding at this ceiling.** The normal cap-112 window already contained the whole core+band tier on all 720 cycles; a separate guarantee changed nothing. That observation is not a confirmed effect and is not read through the failed gates.
- **No engine edit.** The 12 cells used the shipped 0.15.0 build and one fresh six-seed block. `benchmarks/core_band_admission.py`, `benchmarks/core_band_admission_prereg.py`, `docs/core_band_admission_prereg.json`, `docs/core_band_admission.json`, `docs/CORE-BAND-ADMISSION.md`, `tests/test_core_band_admission.py`. Stage B is **1596** consumed seeds across **204** artifacts.

### Changed — The cap ladder has a real cell runner behind the grant check (2026-11-12)

- **The 24 `--cell SEED CAP` commands now execute a cell when authorised.** `PRESENCE-CAP-LADDER-1` was a dry-run planner with a refusal stub. `--cell` now checks the frozen record's `FROZEN, NOT RUN` status, a dated grant (`granted`, ISO date, document and quote), the 0.15.0 build, the shipped cap of 112 and the built runner before opening a database.
- **No grant is recorded and no cell has run.** Without one, `--cell` still exits 2 before any database. The record now says `runner.built = true`, the grant stays false and `cells_run` stays 0. `--dry-run` prints the same 24 commands.
- **An authorised cell would write one part per cell.** It replays the seed's 120-cycle world through the repaired observer at the requested cap and writes `.scratch/presence_cap_ladder/parts/{seed}-{cap}.json`, carrying the served windows, world windows, present and asserted edges, universe, allocation and engine stamps. Unplanned cells and existing parts refuse before a database; `--force` permits a deliberate rerun.
- **The refusal paths are proved, not asserted.** Tests use a synthetic grant and a stubbed cell, and patch `sqlite3.connect` to fail on the un-granted, unplanned and existing-part paths. No seed, cap, gate, verdict or grant changed. `benchmarks/presence_cap_ladder_arm.py`, `benchmarks/presence_cap_ladder_prereg.py`, `docs/presence_cap_ladder_prereg.json`, `tests/test_presence_cap_ladder_arm.py`, `tests/test_presence_cap_ladder_prereg.py`. Stage B is **1590** consumed seeds across **202** artifacts.

### Measured — A per-source top-20 cap buys one asserted edge on one seed (2026-11-12)

- **The uncapped per-seed top 20 already recovers 18 of the 26 asserted never-served edges.** `POST-HOC-SOURCE-DIVERSIFIED-TOP20-1` reads the 212 never-served edges from the six-seed replication (**26** asserted). Each seed is ranked separately by observed minimum pre-cap rank and its top 20 is taken, giving **120** seats. The cap limits how many of those 20 seats may share a source tag.
- **A cap of three recovers 19 of 26, but the gain is one edge on one seed.** It displaces **8** baseline seats, **all non-asserted**, and adds **8** seats, **one asserted**. The entire gain is seed `20613101`, which moves from **0 / 1** to **1 / 1**. Cap 4 and cap 5 reproduce the uncapped **18 / 26**. Cap 2 also recovers **18** but loses three asserted baseline seats, and cap 1 cannot fill a 20-seat window on any seed.
- **The gain does not survive a change of rank field.** With median rank, the uncapped list recovers **25 / 26** and cap 3 recovers **23**, displacing three positives; with final rank it is **24** and **23**, also displacing three. Only the minimum-rank ordering shows a gain, and only by one.
- **This is a post-hoc re-ranking, not an engine arm.** It does not show that source diversification changes the served window, assertion, acquisition, transfer or capability. No engine cell ran and no fresh seed was spent. `benchmarks/source_diversified_top20.py`, `docs/source_diversified_top20.json`, `docs/SOURCE-DIVERSIFIED-TOP20.md`, `tests/test_source_diversified_top20.py`. Stage B is **1590** consumed seeds across **202** artifacts.

### Measured — A stored strength tie-break reorders a few windows but changes no top-20 seat (2026-11-12)

- **Replacing the source/target tie-break with the stored strength field changes no served top-20 membership.** `POST-HOC-STORED-FIELD-TIEBREAK-1` reads the same six consumed schema-prime seeds (`20611601-20611606`, 120 cycles each): **111,275** candidate rows, **701** nonempty cycles and **13,604** top-20 seats. The baseline ends in `source, target`; the alternative ends in stored `strength` descending, then `source, target`. Stored strength is **`min(1, ratio)`**, where ratio is count divided by source frequency.
- **The served set is identical.** Zero of the 13,604 seats change, zero of the 701 windows change and zero edge-seed pairs are gained or lost; the unique edge-seed set stays at **848** pairs. The stored field engages only inside primary ties: **12** windows reorder **37** top-20 positions, with mean absolute shift **1.19** and maximum **2**.
- **The boundary ties are already resolved before the stored field.** **120** of 701 windows (**17.12%**) have a primary tie at the top-20 cutoff, and every one has the same stored strength on both sides. **24** of those cutoff ties have both strengths saturated at 1.0, so an exact uncapped ratio could still separate them; that comparison is not available from the cached rows. The null therefore says the stored capped ratio is redundant at this boundary, not that ratio is irrelevant to ranking.
- **This is candidate ordering only.** No engine cell ran, no fresh seed was spent and no served prediction, assertion, transfer or capability claim follows. `benchmarks/stored_field_tiebreak.py`, `docs/stored_field_tiebreak.json`, `docs/STORED-FIELD-TIEBREAK.md`, `tests/test_stored_field_tiebreak.py`. Stage B is **1590** consumed seeds across **201** artifacts.

### Tested — A support-gated schema priority removes weak jumps and keeps every strong seat (2026-11-12)

- **The ungated schema priority reproduces the earlier priming result exactly.** On the six consumed schema-prime seeds (`20611601-20611606`), 120 cycles each, the cached ranking features contain **111,275** candidate rows and **1,816** schema rows across **701** nonempty cycles. The engine's schema-first order puts all **1,816** schema rows in the top 20 — **13.35%** of the **13,604** seats — and **1,434** of those seats are attributable to schema priority. **563** schema seats are weak (temporal count below 10), **395** of them priority seats.
- **The gate is temporal count >= 10, twice the admission floor of 5.** A schema edge below 10 is not removed; it loses the priority flag and ranks on target entropy, transition probability, count and edge like every other transition. The gated top 20 has **1,400** schema seats (**10.29%**), **1,039** priority seats, **zero** weak priority seats and **zero** strong schema seats lost. The **416** weak schema seats that leave are replaced by **416** non-schema seats; **147** weak schema rows remain only because they were already in the no-priority top 20 on their own ordering. **832** seats change across **135** cycles.
- **The controls prove the gate can move and can be disabled.** A gate at 5 reproduces the ungated top-20 list exactly; a gate at 999 reproduces the no-priority list exactly. The threshold sweep at 5, 8, 10, 12, 15, 20 and 999 gives schema priority seats **1,434, 1,206, 1,039, 885, 703, 435 and 0**; the count-10 rung is the first with no weak priority and all strong priority retained.
- **This is a candidate-ordering diagnostic, not a behavior result.** It measures top-20 composition only, runs no engine cell, spends no fresh seed and does not establish that gated priority improves served predictions, assertion, transfer or capability. A weak schema edge can still enter the top 20 on its own merits; the gate governs the jump, not admissibility. `benchmarks/schema_priority_gate.py`, `docs/schema_priority_gate.json`, `docs/SCHEMA-PRIORITY-GATE.md`, `tests/test_schema_priority_gate.py`. Stage B is **1590** consumed seeds across **200** artifacts.

### Measured — The loop count association reverses when retention, strength and formation timing enter (2026-11-12)

- **The confirmed count association is not robust to how long or how strongly the loop was present.** `POSTHOC-LOOP-PERSISTENCE-1` extends the loop-only model on the same twelve consumed seeds and the same **177** never-served loop-forming edges (**77** asserted). Retention is the observed loop span divided by the cycles available after first detection; strength is the maximum within-loop `min_edge_count` over loops containing the edge. Both are measured from a replay that reproduces every seed's loop edge set, loop cycles and assertion labels.
- **The count coefficient changes sign.** The baseline rank + count model reproduces the confirmed count OR **2.69** (95% CI **1.77-4.07**). Adding retention and strength moves the adjusted count OR to **0.61** (**0.29-1.27**), a **150.1%** change in the count log-odds coefficient, while the adjusted interval includes 1. The post-hoc readout is `COUNT ATTENUATES AND REVERSES`; there is no confirmatory verdict.
- **Persistence carries the association.** Retention OR is **8.02** per SD (**2.57-25.02**) and strength OR is **2031.58** per SD (**38.71-106621.84**; about **2.08** per raw strength unit); strength is close to separating, with **0/44** asserted in its lowest quartile and **44/45** in its highest. In-sample AUC rises from **0.801** to **0.992** and Brier falls from **0.180** to **0.036**. Leave-one-seed-out keeps the adjusted count beta at **-0.644 to -0.348**, retention at **1.77-2.62** and strength at **6.43-8.63**.
- **A formation-cycle control does not explain retention away.** Adding the first loop cycle (as a fraction of the 120-cycle run) to the persistence model moves the retention OR from **8.02** to **14.68** per SD (**3.68-58.64**, p **1.43e-04**), not toward 1. The controlled formation OR is **6.25** (**1.17-33.54**) and the controlled count OR is **0.71** (**0.33-1.53**); leave-one-seed-out keeps controlled retention at **2.12-4.62** and controlled formation at **1.11-3.69**. In this sample timing and retention carry separate information. The control is linear in first-detection timing, measured rather than assigned, and does not identify a causal onset effect.
- **This is a proxy reading, not a mediation result.** Count correlates with strength at **0.484** and with retention at **0.450**; retention and strength correlate at **0.718**. The predictors are measured, not manipulated, the seeds are reused, the world family is synthetic and the model is observational. The formation control is described above. No engine edit. `benchmarks/loop_persistence_assertion_model.py`, `docs/loop_persistence_assertion_model.json`, `docs/LOOP-PERSISTENCE-ASSERTION-MODEL.md`, `tests/test_loop_persistence_assertion_model.py`. Stage B is **1590** consumed seeds across **200** artifacts after the schema-priority gate landed.

### Measured — The loop-only assertion model confirmed the count association (2026-11-12)

- **The count association confirmed inside the loop-forming subgroup.** `CONFIRMATORY-LOOP-ONLY-ASSERTION-1` replayed twelve fresh seeds (`20616101-20616112`) at 120 cycles and cap 40. Among **177** never-served edges that ever formed a loop, **77** were asserted. The Firth model with standardized log2 rank, standardized direct count and twelve seed fixed effects gives count OR **2.69** (95% CI **1.77-4.07**, p **3.1e-06**), rank OR **1.19** (**0.82-1.72**), AUC **0.801**, Brier **0.180**. The count AME is **+0.188** probability per 1 SD.
- **The pre-specified verdict is `CONFIRMED`.** C1 count direction, C2 count interval and C3 gates all pass; all seven gates pass and every seed contributes. Leave-one-seed-out keeps the count beta at **0.882-1.200** and rank at **0.070-0.293**. This is stronger than the exploratory Q4 subgroup, whose count OR was **1.69** (**0.85-3.36**) with rank **1.09** (**0.62-1.90**).
- **It is still a subgroup model, not a mechanism.** The population conditions on loop formation, so this does not test whether loops cause assertion or whether retention matters. Rank remains null. No causal, capability, retention or transfer claim follows.
- **No engine edit.** Artifacts `docs/loop_only_assertion_model_prereg.json`, `docs/loop_only_assertion_model.json`, page `docs/LOOP-ONLY-ASSERTION-MODEL.md`. Stage B is **1590** consumed seeds across **198** artifacts.

### Measured — The never-served assertion model replicated on the provenance block (2026-11-12)

- **The loop split replicated on the six provenance seeds, not just the original Q4 block.** `NEVER-SERVED-ASSERTION-MODEL-REPLICATION-1` replayed `20613101-20613106` at 120 cycles and cap 40 with the repaired full-universe observer. All **212** never-served world edges had a finite rank; **26** were asserted. Firth logistic with seed fixed effects gives loop OR **134.78** (95% CI **8.09-2246.62**), rank OR **0.91** (**0.48-1.73**) and count OR **1.26** (**0.70-2.24**). The no-loop cell is again **0/124** asserted, against **26/62** in the loop cell; apparent AUC **0.928**, Brier **0.0664**.
- **The pre-specified verdict is `REPLICATED`.** The loop OR exceeds 1, its interval excludes 1, both loop levels are present, and all seven gates pass. The replay reproduces the provenance artifact's per-seed asserted and never-served-asserted counts exactly. Rank and count do not add a positive association here: both intervals include 1 and the rank point estimate is below 1.
- **The loop coefficient is still quasi-separated, so this is a replicated structural split, not a precise effect.** Leave-one-seed-out keeps the loop beta at **3.86-5.01**, rank between **-0.321 and 0.154**, and count between **0.079 and 0.323**. The six seeds already carried the provenance replication; this is a replication on that existing fresh block, not a new independent draw, and no causal, retention or capability claim follows.
- **The count association does not gain support when source and target identity are held fixed.** A post-hoc extension adds 15 source and 15 target fixed effects to the same Firth model: **39** parameters for **212** rows and **26** events. Count OR moves from **1.26 (0.70-2.24)** to **1.39 (0.61-3.19)**; the point estimate is not attenuated, but the interval still includes 1. Loop attenuates from **134.78** to **24.58 (3.72-162.63)** but remains positive, and rank remains null. The identity model is saturated in sample (AUC **1.000**), so this is a robustness check, not a predictive result. Post hoc, not preregistered; no verdict changed.

- **No engine edit.** Artifacts `docs/never_served_assertion_model_replication_prereg.json`, `docs/never_served_assertion_model_replication.json`, page `docs/NEVER-SERVED-ASSERTION-MODEL-REPLICATION.md`. Stage B is **1578** consumed seeds across **196** artifacts. **Superseded later on 2026-11-12:** Stage B moved to **1590** consumed seeds across **198** artifacts after the loop-only confirmatory block landed; see the entry above.

### Measured — The matched carrier contrast replicated on fresh seeds (2026-11-12)

- **The twofold loop enrichment replicated on a clean block after a voided first attempt.** `MATCHED-CARRIER-REPLICATION-2` replayed six fresh seeds (`20615201-20615206`) at 120 cycles and cap 40. Cases are asserted world edges with zero direct served windows; controls are same-seed edges that are neither served nor asserted, matched 1:1 by the final temporal count with edge as the tie-break. **29/29** cases ever formed a reported loop against **11/29** controls: **+62.1 pp** (seed-cluster 95% CI **[38.5, 85.2]**), risk ratio **2.64**, exact McNemar **p = 7.6e-06**.
- **The pre-specified verdict is `REPLICATED`.** R1 direction, R2 exact McNemar and R3 cluster interval above zero all pass. The original +50 pp lies inside the fresh interval, so the block is compatible with the original magnitude and point-estimates stronger; it does not establish that the true effect is exactly twofold.
- **A first block was voided before interpretation, not quietly re-scored.** `MATCHED-CARRIER-REPLICATION-1` on `20615101-20615106` populated the matching covariate from served-window counts; every never-served edge therefore had count zero and controls were chosen by edge alone. That is not the census's direct temporal count. The void is recorded in `.scratch/matched_carrier_replication_1_void.json`; its seeds are not reused, and only block 2 is read. The matcher reproduces the original Q4 contrast (26 pairs, 13/26 control loops) when applied to the census.
- **No engine edit; this is not a retention, causal or capability claim.** Artifacts `docs/matched_carrier_replication_2_prereg.json`, `docs/matched_carrier_replication_2.json`, page `docs/MATCHED-CARRIER-REPLICATION-2.md`. Stage B is **1578** consumed seeds across **194** artifacts after the voided block-1 docs are removed. **Superseded later on 2026-11-12:** Stage B moved to **1578** consumed seeds across **196** artifacts after the never-served assertion model replication landed; see the entry above. **Superseded again on 2026-11-12:** Stage B moved to **1590** consumed seeds across **198** artifacts after the loop-only confirmatory block landed; see the entry above.

### Added — The 3-4 ceiling is localized to candidate formation, not fully explained (2026-11-11)

- **`benchmarks/ceiling_diagnostic.py` replays the five zero cells and all seven controls.** The five zero-S_ever persistence-off cells are T1 `20612204`, `20612205` and T1b `20612208`, `20612210`, `20612212`; the seven controls are the remaining off cells. The replay preserves the engine's persistent event rows across cycle boundaries and the cell loop's processed reset boundaries, which is what makes the control maxima 5-6 rather than 4.
- **The exact replay reproduces every committed source maximum.** Zero-cell maxima are 4, 3, 4, 3 and 4; control maxima are 6, 6, 5, 6, 5, 6 and 5, matching `docs/persistence_zero_served_diagnostic.json`. The zero cells remain below floor 5 at the engine's 3-event window.
- **The record localizes the zero, but does not explain the mechanism.** The zero is created before ranking, admission or assertion: no world-edge candidate exists. The exact contribution of the read floor, lookback horizon, cycle-boundary reset behavior and world structure remains unresolved. PersistenceOff means **no carried support conditional on cycle completion**, not a perfect no-memory condition.
- **The window sweep is a counterfactual, not a clean treatment.** At window 6 the zero cells reach 8-9 on their best edge and 61-69 edges at floor 5; 1,000 fixed-seed within-cycle order permutations put the observed maxima below the null p95 (5-6). An engine lookback extension is different because persistent event rows reintroduce cross-cycle context, so it needs its own preregistration. The verdict is **LOCALIZED (window-sensitive)**, not `WINDOW-BOUND`.
- **This is a `not_a_result` diagnostic.** It runs no engine cell, consumes no fresh seed, writes no treatment partcache, and adjudicates no block. T1 stays VOID, T1b stays `PERSISTENCE CONTRIBUTES`, and Stage B stays at **188** artifacts. The artifact and page are `docs/ceiling_diagnostic.json` and `docs/CEILING-DIAGNOSTIC.md`.

- **Q055 carries the localization, not only the diagnostic page.** The registry answer and scope now separate candidate formation from the unresolved floor/horizon/boundary/world-structure decomposition, record `PersistenceOff` as no carried support conditional on cycle completion, and link the ceiling artifact. `docs/FINDINGS-LEDGER.md` is the durable, not-a-result synthesis for the current persistence chain, the 26 asserted-but-never-served edges, BAND-5's class-level scope, the working mechanism map and the information-gain ordering. The generated findings page, question registry and dashboard were regenerated; no cell ran and no verdict moved.

### Changed — BAND-5 ran on fresh worlds and confirmed the allocation-law band (2026-11-11)

- **`PRESENCE-BAND-5` returned `CONFIRMED`.** Six fresh seeds (20612601-20612606), twelve cells at 40 and 112, and one determinism rerun produced `docs/presence_band_rank_5_run.json`. All **89** measured rank-21-40 edges (18, 14, 19, 11, 11, 16 per seed) are served at 112 and none at 40; B1-B8 pass, with 64-68 transitions and 48 cooccurrences on every full cap-112 window.
- **B5 is the BAND-4 allocation law, not a fit to 64-69.** A full window needs `transitions + cooccurrences = 112`, `transitions >= 56` and `cooccurrences <= 56`. The dated grant `docs/AUTHORISATION-PRESENCE-BAND-5.md` preceded the arm and every cell.
- **This is a fresh block, not a re-score.** BAND-1 stays VOID; BAND-2/BAND-3/BAND-4 stay unrun. The per-edge ledger and page are `docs/presence_band_rank_5_run.json` and `docs/PRESENCE-BAND-RANK-5-RESULT.md`. Stage B now quotes **188** artifacts and **1,554** consumed seeds.
- **The admission decision records the verdict without moving its status.** BAND-5 is class-level mechanism evidence on fresh worlds, but it does not re-score BAND-1's 62 named Q4 edges. The decision stays **PENDING**, and its named-edge mechanism condition stays **unadjudicated**.

### Changed — The layer-1 cap is 112, and the canaries say so (2026-11-11)

- **The cap moved from 40 to 112, and only the cap moved.** `SleepService.MAX_PREDICTIONS` is
  `112`; no other engine constant, method or ordering was touched, and the E1 allocation
  (`returned_budget`, `transition_budget`, `cooccurrence_budget`) is unchanged. The level change
  is `DECISION-CAP-LEVEL` choice C, which stays PENDING: landing the cap does not promote the
  decision, and no lineage link is recorded for it.
- **The canary digests moved because the cap is inside the cell, not because of E1.** On the
  re-recorded build `PRESENCE-CONSTRUCT-1` is `8ffefa8d1ec7957ebe82124225648a95ab350fcc07e2b93bffd81736d9a06486` and `PRESENCE-CONVERSION-1` is
  `3d8d83ed6f723c81573525778cb44d9d9816ea0aec7c2056937657c170dc965f`; both changed, and the changelog attributes the change to the level, not to the
  E1 allocation whose proof is preserved unchanged in `docs/block_canaries_0.14.0_e1.json`.
- **Two frozen cells did not move, and the checklist's blanket rule is wrong about them.**
  `PRESENCE-CAP-1` stays `a32ae3bc3d00dd4fc54a39f3a5629d1f237b900944c9a96e32a2685ad2b70f8d` because its cell passes an explicit `cap: 40` arm — the level is
  pinned inside the cell, so the shipped constant cannot reach it. `PRESENCE-CONVERSION-2` stays
  `f8ead12b63221c9db5b261b7969f8797b4ceb4ad1b44d67cce415b8036972aca` because it is a refusal canary: it records that a cell is refused, and no cap is
  read. Unchanged is the correct reading for both, and is disclosed rather than restamped.
- **The 0.14.0 equivalence link is retired, not carried.** A cap change is a behaviour change, so
  no lineage link can join the two builds; `docs/engine_lineage.json` now carries no links and the
  E1 link is kept as the historical `docs/engine_lineage_0.14.0.json`. The cap-40 records
  (`PRESENCE-CONSTRUCT-1`, `PRESENCE-CAP-1`, `PRESENCE-CONVERSION-1`) keep their status and
  verdicts and gain a dated `build_superseded` disclosure naming the build they measured; their
  checks accept that build explicitly instead of the shipped one.
- **The cap-112 records are the live design, not a re-score.** The comparator, Q1 and Q2 records
  at cap 112 remain `FROZEN, NOT RUN` with their runners built and gated; landing makes them
  runnable without running a cell. `python -m benchmarks.presence_cap112_prereg --check` is the
  record check.
- **Version and pin move together:** the package is `0.15.0` in the three declarations,
- **The band-identifiable arm is frozen, not run.** `PRESENCE-BAND-1`
  (`docs/presence_band_rank_prereg.json`, `docs/PRESENCE-BAND-RANK-PREREGISTRATION.md`)
  names the 62 Q4 rank-21–40 transition edges by identity and fixes a 40-versus-112
  per-edge arm on Q4's six worlds: twelve cells, gates B1–B8, the admission decision's
  acceptance condition quoted verbatim. It is the instrument Q2's count-only payload lacked,
  not a re-read of Q2. Its runner was built at `benchmarks/presence_band_rank_arm.py`, and the
  block later ran under a dated grant (the next entry).
  `docs/engine_pin.json` re-pins fourteen files at 0.15.0, and no tag is cut.
- **The band arm ran under a dated grant and returned `VOID` on B5 (2026-11-11).**
  `docs/AUTHORISATION-PRESENCE-BAND-1.md` records the instruction; the twelve cells and the
  determinism rerun produced `docs/presence_band_rank_run.json`. All **62** named edges were
  served at 112 (12, 9, 16, 9, 14, 2) and **0** at 40, but **B5** failed on every seed: the
  cap-112 transition allocation is 64-69, not the frozen **56**, and the rank comparison read
  no served edge. Seven of eight gates pass, so the frozen table reads **VOID** and the
  acceptance stays **unadjudicated**; the decision stays **PENDING**. Two harness defects
  (`dict & set` in B4 and character tuples in `_served`) were fixed after the cells ran; no
  cell re-ran and no gate was rescored. Stage B now quotes **180** artifacts.
- **BAND-2 is frozen with a corrected B5 and a fixed rank reading, before any cell (2026-11-11).**
  `docs/presence_band_rank_2_prereg.json` and `docs/PRESENCE-BAND-RANK-2-PREREGISTRATION.md`
  keep BAND-1's 62 Q4 rank-21-40 edges and six worlds but correct the two harness defects.
  B5 now reads **56** as the engine's floor (`MAX_PREDICTIONS // 2`) and allows the cooccurrence
  backfill, so the observed 64-69 is no longer a gate failure; the rank reader splits
  `source>target` at exactly one `>` into two non-empty tags, takes the minimum recorded rank
  for that exact edge, and fails a served edge with no rank rather than contributing 0. BAND-2
  is a new, unrun block, not a re-score: BAND-1 stays VOID, no arm is built, no grant is
  recorded, and no cell has run. Stage B now quotes **183** artifacts.
- **BAND-3 repairs the band block with fresh seeds and a B5 that can fail (2026-11-11).**
  `PRESENCE-BAND-3` uses six unused seeds (20612401-20612406), 12 cells at 40 and 112,
  and a band measured per fresh world: every present transition at block rank 21-40 in
  the cap-112 ceiling universe. It keeps BAND-2's strict `source>target` parser and the
  corrected `>= 56` floor, but B5 is a live cap test rather than a restatement of the
  band: a 20-transition fixture, a maximum served rank of 40, an unranked served edge and
  a malformed edge must all fail. The grant is recorded before the arm or any cell;
  `runner.built` is false, `cells_run` is 0, and no result exists. BAND-1 stays VOID and
  BAND-2 stays unrun. Stage B now quotes **186** artifacts.
- **Q055 states the eligibility mechanism behind the persistence result (2026-11-11).**
  The finding now says what the zero-S_ever replay actually established: with cross-cycle
  counts reset, the five zero seeds never reach `PREDICTION_MIN_COUNT = 5` inside a cycle
  (maximum 3-4), so no world-edge transition candidate is built, none can be served, and
  the full observer/sleep path reproduces 0 served edges; the controls serve 3 and 9. It
  does not claim that threshold 5 is wrong. Why those seeds top out at 3-4 is recorded as
  the next question, and lowering the floor is a separate intervention. The mechanism is
  scoped to the five zero seeds; ranking, admission, assertion and service remain candidate
  mechanisms on the non-zero seeds.
- **BAND-4 is a confirmatory allocation block with two independent failure modes (2026-11-11).**
  `PRESENCE-BAND-4` replaces the exact-56 reading with the engine's full-window
  law: at cap 112 a full window has `transitions + cooccurrences = 112`, with
  `transitions >= 56` and `cooccurrences <= 56`; 64-69 is the floor plus backfill,
  not a threshold. The block uses six fresh seeds (20612501-20612506), 12 cells,
  and a B5 fixture that passes 64+48 and 56+56 but fails 56+0, 20+20, a bad sum,
  an over-ceiling cooccurrence count, a rank ceiling at 40, an unranked edge and
  a malformed edge. Acceptance is co-primary: perfect band service cannot rescue
  a failed allocation law, and a perfect allocation cannot rescue an unserved
  band edge. It is frozen with no grant, arm, cell or result. Stage B now quotes
  **186** artifacts.
- **The 56-transition budget is reconciled with the 112 cap allocation (2026-11-11).**
  The engine's `transition_budget = returned_budget // 2` is a guaranteed floor, and
  `_build_predictions` backfills unused cooccurrence slots with further transitions. At 112 the
  floor is **56**, while BAND-1's cells served **64-69**; its exact-56 gate was therefore a gate
  defect. `docs/CAP-DECISION-BRIEF.md`, `docs/DECISION-ADMISSION-STEP.md`,
  `docs/DECISION-CAP-SEMANTICS.md` and the decision index now say this, and BAND-1 carries a dated
  `budget-reconciled` disclosure without changing its gates or VOID verdict. BAND-2 freezes the
  corrected `>= 56` condition and remains unrun. The cap, Q2's `CAP LIMITING`, Q4's
  `CONVERSION STAGE MEASURED`, the decision's PENDING status and its acceptance condition are
  unchanged; no cell re-ran.
- **The persistence intervention is chosen: carry counts, not a lower floor or a longer lookback (2026-11-11).**
  `docs/DECISION-PERSISTENCE-INTERVENTION.md` follows Q055/T1b and records the intervention as
  cross-cycle carry, with the floor at **5** and the event lookback at **3** fixed. Lowering the
  floor is rejected: floor 4 leaves three of the five zero cells at zero, while floor 2 or 1
  admits almost every world edge; extending the lookback is rejected because event rows persist
  across the reset, so a longer window reintroduces cross-cycle context and is a carry channel in
  disguise. The follow-up arm is **`PERSISTENCE-CARRY-1`**: carry versus an explicit reset at
  every cycle boundary, 12 cells on six fresh seeds at cap 112, with a clean reset that closes
  T1b's skipped-boundary leak. The decision is **PENDING**; no grant, arm, runner or cell exists,
  and `PERSISTENCE-MECHANISM-1` remains frozen and unrun.
- **The persistence-mechanism follow-up is frozen before any cell (2026-11-11).**
  `PERSISTENCE-MECHANISM-1` (`docs/persistence_mechanism_prereg.json` and
  `docs/PERSISTENCE-MECHANISM-PREREGISTRATION.md`) follows T1b's decision to pursue the
  persistence mechanism (decay, floor, denominator) with a 2 x 2 at cap 112 on 0.15.0:
  decay **0.95** versus no decay **1.0**, and read floor **5** versus **1**. It plans
  **24** cells (4 arms x 6 fresh seeds, 20612301-20612306) at 120 cycles, with G1-G7
  fixing the build, world, live treatments, denominator, seed axis, determinism and cell
  count. No grant is recorded, no runner is built, no result exists and `cells_run` is 0;
  T1 and T1b are not re-read. Stage B now quotes **186** artifacts.
- **The T1b persistence result is now an established finding (2026-11-11).**
  `docs/RESEARCH-FINDINGS.md` gains **Q055**, sourced from the registry rather than edited by
  hand. At cap 112, T1b's six fresh seeds show shipped `S_ever` 101, 95, 100, 103, 98 and 99
  against persistence-off 0, 1, 0, 3, 0 and 3; the paired differences are 101, 94, 100, 100,
  98 and 96 (mean **98.167**, 95% interval **[96, 100]**), all six above the margin of 10, with
  all seven gates passing and three zero `S_ever` cells read as measured zeros. The finding
  carries its scope — one build, one cap, one world family, six seeds, one no-carry
  intervention; a direction, not an effect size — and the prior T1 context: T1 is VOID on G4
  because its frozen rule treated zero `S_ever` as unmeasurable, its computed mean is not
  adjudicated, and T1b changed only that reading before any cell. No verdict, gate, cap,
  engine byte or seed moved. The registry held **53** questions at that point; it now holds **54**, with **25** in neither reopening list (19 open, 6 future) and 17 kept-closed rows.
- **T1b ran with a zero-admitting denominator gate and returned `PERSISTENCE CONTRIBUTES` (2026-11-11).**
  `docs/AUTHORISATION-T1B-PERSISTENCE-OFF.md` records the instruction; the twelve cells and the
  rerun on six fresh seeds produced `docs/t1b_persistence_off_run.json`. G4 now treats P as the
  denominator and S_ever as a measured count: P = 112 in every cell, three persistence-off cells
  served zero world edges and are reported as zeros, and all seven gates pass. The paired
  differences are 101, 94, 100, 100, 98 and 96 (mean **98.167**, 95% interval **[96, 100]**),
  positive on 6 of 6 seeds against the margin of 10. T1 remains VOID on its own G4 and is not
  re-read. Stage B now quotes **182** artifacts.
- **The zero-S_ever persistence-off cells are explained by the prediction floor (2026-11-11).**
  `benchmarks/persistence_zero_diagnostic.py` replays the committed T1 and T1b store sequences
  and runs the full observer/sleep path on the five zero cells plus two controls. The reset leaves only within-cycle counts, and `_build_predictions`
  admits a transition only at `PREDICTION_MIN_COUNT = 5`. The five zero cells (T1 20612204 and
  20612205; T1b 20612208, 20612210 and 20612212) never let a world edge reach 5 inside a cycle
  (max 3 or 4), so 0 world edges are admissible and the full path serves 0 on all five. The
  seven non-zero off cells' ceilings equal their `S_ever` exactly; the controls serve 9 and 3, and
  the shipped arm stays at or below its ceiling. No verdict moved:
  T1 stays VOID and T1b stays `PERSISTENCE CONTRIBUTES`. Stage B stays at **182** artifacts: the diagnostic is marked not-a-result and does not count as a consumed seed.

- **The admission decision's open question is carried into the next-work views (2026-11-11).**
  `python -m benchmarks.research_accountability` renders a **Next work — open question**
  section from `docs/decisions.json`, quoting the `open_question` of every PENDING
  decision; `python -m benchmarks.research_trace --next` prints the same quote under its
  pending-decision row. The admission decision stays PENDING and its acceptance condition
  stays unadjudicated; the views add no decision and change no status.

## [0.14.0] — (unreleased)

### Changed — the prediction budget is an allocation, and a recorded lineage carries behaviour-identical builds (2026-11-11)

- **The owner's E1 is in force.** `MAX_PREDICTIONS` is the returned prediction window; inside
  `_build_predictions` it is named `returned_budget` and split into `transition_budget`
  (`returned_budget // 2`) and `cooccurrence_budget` (the remainder after transitions are served).
  Every override that moves the cap moves all three, because they are derived, not stored.
  `docs/DECISION-CAP-SEMANTICS.md` records the decision; the four block-canary digests in
  `docs/block_canaries.json` are unchanged, which is the proof that no served row moved.
- **A behaviour-preserving edit can now land without restamping a measurement.**
  `docs/engine_lineage.json` records a link from the build the canaries were recorded on to the
  split build, authorised by that decision and proving the recorded digests;
  `benchmarks.engine_lineage.same_build` is the build check for the block canaries, the assertion
  audit, the construct audit and the cap block. `block_canaries --check` re-runs the cells on the
  successor, so a link cannot bless a build that serves different rows, and no frozen verdict was
  re-derived.

### Changed — D3's matched-frequency persistence repair is promoted into the engine (2026-11-10)

- **The owner adopted the repair after the seed-varying confirmation.** `D3-PERSISTENCE-2` produced
  six distinct preflight treatment trajectories, all six alive through the 3,000-cycle horizon,
  with the L3 witness at 39 of 40 cycles and peak 6 and the early-recall median gap at 0.0 against
  the -0.01 bar. The preserved `D3-PERSISTENCE-1` single-world record keeps its effective-n = 1
  caveat and is not rewritten.
- **The engine now decays the source-frequency denominator.** Each sleep cycle maintains a per-tag
  denominator `D = 0.95 * D_previous + delta`, where `delta` is the increase in
  `MemoryService.tag_frequencies()` since the previous cycle; prediction strength divides the
  temporal count by `max(D, 1)`. The temporal decay constant, death threshold, stable threshold,
  candidate decay, admission floor, caps, retention policy and candidate set are unchanged.
  `benchmarks/d3_persistence_arm.py` is now a compatibility name only; it no longer overrides
  engine behavior.
- **D2's pre-flight passes on the promoted build.** The 2026-11-10 run returns `PASSES`: the
  reference arm holds 39 of 40 witness cycles at peak 6, both negative controls stay at zero, and
  the campaign stimulus has no first zero through the 3,000-cycle horizon. The campaign has since run on the promoted engine; its result is recorded in
  `docs/FORCE-MATRIX-0.14.0-RESULTS.md` and `docs/force_matrix_0.14.0.json`. Record: `docs/tier1_preflight.json`, page `docs/TIER1-PREFLIGHT.md`.
- **The promotion is a recorded release-boundary change.** The package version is `0.14.0` in the
  three declarations, `docs/engine_pin.json` is re-pinned over the promoted bytes, and the owner
  decision is recorded in `docs/DECISION-G1-WITNESS.md` §9. No published result artifact was
  rebuilt.

## [0.13.0] — (unreleased)

### Changed — D3's persistence repair survives six distinct seed-varying worlds (2026-11-10)

- **The first D3 block varied the service seed but not the world.** The fixed lattice stimulus was
  identical across its six seeds, so the block returned one trajectory six times and effective
  n = 1. The result page and decision record already carry that caveat; the prior artifact is not
  rewritten.
- **The seed-varying confirmation reran the same 24 cells on six distinct schedules.** Each seed
  shuffles the design's triangle order and rotates the resulting 216-event stream; pre-committed
  gate G8 voids the block if the treatment trajectory repeats. All six preflight treatment
  trajectories differ, all six stay alive through the 3,000-cycle horizon, the witness holds
  39 of 40 cycles and peak 6 on every seed, and the early-recall median gap is 0.0 against the
  -0.01 bar. Verdict: `PERSISTENCE REPAIRED`, effective n = 6.
- **Nothing is promoted.** The arm remains an in-process subclass, no engine file changed, and
  adoption still requires a recorded owner decision and an engine re-pin. New record
  `docs/d3_persistence_seed_varying_run.json`, page
  `docs/D3-PERSISTENCE-SEED-VARYING-RESULT.md`.
- **A degenerate seed axis is now refused at the runner.** Both D3 result writers call a shared
  guard before writing: more than one seed with fewer than two distinct preflight treatment
  trajectories raises `SeedAxisDegenerate` and writes no artifact or page. The preserved D3-1
  record keeps its caveat; the guard stops a new single-world pass from being reported as six
  confirmations.

### Changed — The release gate records that master is published at `747d3dd` (2026-11-09)

- **The gate record named a remote tip that had stopped being true.** Sections 3a and 3b of
  `docs/RELEASE-GATE-0.13.0.md` were read when `refs/heads/master` was `1f9f713`; the three 0.13.0
  commits were then pushed through the environment's branch-scoped authenticated path, so the remote
  now carries `747d3dd` (`747d3dd1083368753970bc41840d33f21cd34db5`). A dated section 3c records the
  push, its receipt `1f9f713..747d3dd` and the three commits, and 3a and 3b point at it rather than
  having their readings rewritten.
- **It does not clear a gate.** `git ls-remote --tags origin` still returns `v0.6.0`-`v0.10.0` plus
  `audit-trace-v1` and no `v0.12.0`, so the missing ref is still the tag alone; `clone_check` was not
  re-run, so its recorded result stands as the last measurement, and gate 3 stays unsettled with it.
  No tag, version bump, re-pin, artifact regeneration or deposit change was made, and the 0.13.0
  heading still says `(unreleased)`.
- **A branch push moves every count taken from HEAD**, and the amendment records the ones it moved:
  **67** commits after the pin `6e0ff24` with **0** of them touching `organica/`, and **126** commits
  after `v0.12.0` against the gate's **123**. The pin check still reports fourteen files at 0.13.0.

### Changed — The reopening tally closed around Q052, and the rerun plan landed with its guards (2026-11-09)

- **The partition omitted one question.** Q052 was closed before the 2026-11-08 reopening pass and
  appeared in neither `reopened` nor `kept_closed`, so the kept-closed count was short by one and the
  entry above it had said twelve. It is now in `kept_closed` with its artifact evidence. Q052's
  closure left the reopened side one row larger than it is now: Q006 has since moved to
  `kept_closed`, so the current partition is **12** reopened + **16** kept closed + **24** never
  closed over **52** questions; Q054, the Q4 conversion-repair protocol, is the twenty-fourth never-closed row and joined as a first answer on 2026-11-10. Three tests in `tests/test_research_registry.py` check that every
  closed or retired question is classified, that the three groups partition the registry with
  reopened answers open, and that removing Q052 fires the check.
- **The Stage B block follows the artifact that landed.** The seed scan covers **214** artifacts, up from the **180** artifacts it held after the band run (amended 2026-11-10, and again when the three conversion blocks wrote their run artifacts: the D3 seed-varying, engine-replication, G1-recalibrated-preregistration and run, the presence/assertion audit, the presence-to-assertion ladder, the construct-audit and cap preregistrations, and Tier-1 records raised the count from 157; the count moves as records land: the pruning-reachability, pruning-by-type, temporal-presence, question-survival, pre-flight and Q006 records were added that day, and the construct-audit, cap and conversion-observer run artifacts took it from 169 to 173, the presence band arm's frozen record carried one, and its run artifact the next, and BAND-2's frozen record, and PERSISTENCE-MECHANISM-1's frozen record, and BAND-3's frozen record after it, and BAND-5's record and run artifact after that, the fresh-block provenance replication, and the never-served assertion model's preregistration and result after that, and the matched carrier replication's preregistration and result after that, and the never-served assertion model replication's preregistration and result after that, the loop-only assertion model's preregistration and result after that, the loop persistence extension after that, the schema-priority gate after that, the stored-field tie-break after that, the source-diversified top-20 diagnostic after that, the core+band block after that, the retention preregistration, the retention run result, the formation-anchored retention preregistration, its run result, and the entry-transition preregistration after that) with
  **0** overlap against the candidate block, **54** more than the **146** it recorded before
  `docs/ablation_study_0.13.0.json` existed, and the stored artifact and the quoted block are rebuilt
  together so they describe the same state.
- **`docs/RERUN-CAMPAIGN-PLAN.md` splits the registry into two halves and runs nothing:** after
  Q006 and Q021 closed, **12** re-derivations remain with a comparator and **23** first answers
  have none, **18** of the first answers runnable now. `tests/test_rerun_plan.py` recomputes every
  count from the registry, and
  `tests/test_rule30.py` checks that each campaign row and judged decision table names a different
  decision per outcome, with a control that fires on a "do it again" branch.

### Added — Every 0.13.0 entry is pinned to its artifact, and every ablation override is invoked (2026-11-09)

- **The section's figures are checked rather than transcribed.** `tests/test_changelog_figures.py`
  requires each quoted figure to occur in the section and the artifact behind it to round to exactly
  that string at the quoted precision. All **42** entries present at `3c9948e` are classified, **0**
  are left uncovered, and a control changes the ablation entry's ES band and asserts the checker
  reports the drift, so a rename or a new entry cannot slip past unseen.
- **Figures with no artifact behind them are declared, not given provenance:** the aborted run's
  four conditions, the superseded registry tallies, and the cap-slot shares another test recomputes.
  A figure that merely begins with the same digits is not accepted as the number either, because the
  check reads each artifact by field path rather than searching the section for a value.
- **The ablation guard invokes the overrides instead of only binding them.** The union of the
  arguments `organica/*.py` supplies at every call site is passed to every override on every arm
  against a probe whose `self` answers any attribute, so a body that accepts the call but forwards a
  stale argument set to `super()` fails in the suite rather than after four conditions of an ablation
  run; a narrow-override control proves the invocation path fires.

### Fixed — The ablation harness runs all eleven conditions on 0.13.0 (2026-11-09)

- **The failure was a signature, not a result.** Condition D's override spelled the five G1
  arguments and did not accept the `meta_concepts` keyword the engine now passes, so the
  2026-11-09 verification run stopped after four conditions and wrote nothing. The override now
  accepts the engine's G1-G8 keyword set, re-stores the non-current composite generations
  untouched under `no_extinction`, and builds both sides of the identity comparison with
  `_candidate_key`, so the arm still measures "no extinction" rather than "no selection at all".
- **All eleven conditions run and the artifact names its engine.** `--cycles 300` exits 0 with
  11 of 11 conditions and writes `docs/ablation_study_0.13.0.json`, stamped
  `engine_version 0.13.0`, `engine_commit 6e0ff24d84d3`, `engine_sha256 ed0851d1...` and
  generated 2026-11-09T03:01:52Z. The pre-0.13.0 `docs/ablation_study.json` was not touched.
- **The measured result, not a re-scoring.** `O_FULL` is ES 59.440. A (No Sleep) and J
  (Memory Without Structure) are **existential** at 59.440 and 59.440; I (Random Sleep) is
  **important** at 15.180; and B-H are **cosmetic** at 0.000, 0.084, 2.504, -0.574, -0.876,
  0.193 and -0.224. The bands are the artifact's own.
- **A control pins the contract.** `tests/test_ablation_arm_signatures.py` reads every
  `self.<method>(...)` call in `organica/*.py` and binds each arm override to the arguments that
  call passes; its second test reproduces the pre-repair signature and asserts the checker fires.
  No engine file changed.

### Changed — The version statements were swept and six stale ones corrected (2026-11-09)

- **Six current-state claims disagreed with the repository.** The manual's Git row named `0.12.1` and
  a version-gated skip that was removed on 2026-11-08; the `0.12.1` changelog heading was not marked
  superseded; and four places still said the package version stays untagged after `v0.10.0` and
  `v0.12.0` were tagged.
- **Dated records that were true when written are disclosed, not rewritten.** The sweep note
  `docs/VERSION-STATE-SWEEP-2026-11-09.md` records each correction with its old and new text, and the
  facts sheet gains AA27.
- **A Git row cannot describe a guard that no longer exists.** It now names `0.13.0` and the per-file
  content pin, which has no version-gated skip.

### Changed — A re-run that reproduces a recorded result keeps its recorded date (2026-11-09)

- **The test-count recorder stamped today's date on every run**, so re-running the suite on a new day
  dirtied `docs/test_count.json` and both documents that restate it without reporting anything new.
- **The date now means when the recorded result was established:** an identical result keeps the
  existing date, and only a different result takes the day it ran. The count was re-recorded for the
  three tests that pin the rule.

### Changed — The two superseded stashes were inventoried, disclosed and dropped (2026-11-09)

- **Both held only the version-guard test change plus release-state prose**, and the test change is
  byte-identical to the committed one, so disposing of them lost nothing.
- **`docs/SUPERSEDED-STASHES-2026-11-09.md` records the inventory and the evidence**, including a
  corrected attribution: the pre-carried-forward engine snapshot belongs to the dangling WIP commit
  `08f3cb1`, not to either stash.

### Measured — The burst deaths were matched against lattice deaths at the same age (2026-11-08)

- **A2's label carried a death-age confound:** the burst cells die at cycles 131-134 and the lattice
  control at 300. The addendum fixed its reading rule before measuring — a lattice death within 10
  cycles is age-matched, and a 0.10 ratio difference means age explains the gap — then measured six
  lattice factors.
- **No lattice death falls within the tolerance** (the nearest are 112 and 150), so the label is
  `AGE_MATCH_UNAVAILABLE`. The cohort ratio is flat across lattice deaths (0.578-0.610, spread 0.032),
  and bracketing the burst ages gives 0.582 against the burst cells' 0.308, 0.315 and 0.034, with
  live cycles at those ages retaining 0.9998 and 0.934.
- **The mass gap is not an age artifact**, and A2's classification stands unchanged.

### Added — Q053 was narrowed to one mechanism and preregistered on the lattice evidence (2026-11-08)

- **The design fixes the measured boundary at loss of competing hypotheses**, names five candidate
  interventions without choosing one, and specifies shipped 0.95 against 0.95 plus one mechanism. No
  engine change, seed or cell is allocated.
- **Q053 was then narrowed to the best-supported hypothesis and Q052's framing ordered first**, because
  competition preservation is the most promising unexplored direction rather than the proven next
  move: the boundary is measured, but the preserve-to-capability link is not.
- **One mechanism is preregistered** (`benchmarks/q053_mechanism_prereg.py`,
  `docs/Q053-MECHANISM-PREREGISTRATION.md`) on the lattice evidence, with no cell run.

### Added — Q052's census ran on burst_L1, returned VOID, and was completed by a disclosed amendment (2026-11-08)

- **The framing design pre-committed five labels** over the existing competition-probe fields plus an
  edge-mass ratio, with their precedence stated before any cell, and recorded that the shipped 0.95
  arm is alive at 300, so the intervention contrast has no dying control on that family. No seed was
  allocated and no engine file changed.
- **The first census is VOID on its own control.** The lattice control reproduced the committed census
  exactly — 299 live, 300 dead, `bravo` 866 = 433 + 433, empty competing census at death — but its
  mass ratio is 0.578 against an uncalibrated floor of 0.90, and edge mass sums every retained
  hypothesis, so the competitors pruned at death sit inside the drop. Design section 3 stops the
  framing as VOID, no label was read, and the capture window was widened to the whole run before any
  label was read (amendment A1).
- **Amendment A2 changed only the census arithmetic:** the mass is the support mass of the pairs
  retained at the last live cycle, tracked through death, and the floor is calibrated on committed
  lattice cells with the control's seed excluded. The control passes at 0.578; three burst seeds give
  0.308, 0.315 and 0.034 with no competing census at death, which classifies as
  `DIFFERENT_SUPPORT_COLLAPSE` and keeps Q053 on `lattice_L1`.
- **Two limits are recorded rather than smoothed over:** the calibration has no spread, so the
  admissibility gate cannot fire, and the burst deaths are not matched to the control's death age, so
  the signature differs but the reason is not identified. The separate age-match addendum is the
  follow-up, and it leaves the label standing.

### Changed — Fourteen closed answers that never named their build were reopened (2026-11-08)

- **The criterion is mechanical:** an answer is reopened when no artifact it rests on records the
  release pinned now (`0.13.0`, whose fourteen files the pin check verifies against the current tree).
  Thirteen closed questions qualified: Q004, Q005, Q006, Q017, Q024, Q029-Q032, Q036, Q043, Q044
  and Q051. Q021 was reopened in the same pass but closed on 2026-11-09 by its pinned 40-cell
  re-derivation; Q006 closed on the same date by its pinned 16-cell block, so both now sit in
  `kept_closed` and the current partition is **12** reopened + **16** kept closed. Twelve closed
  questions remain open today.
- **Thirteen kept closed with reasons** — nine because their evidence does name the pinned release
  (including **Q052**, which the first pass omitted), and four because those closures were governance
  or design decisions rather than measurements. This entry first said twelve: Q052 was closed before
  the pass and was missed, so the count was short by one and is corrected here rather than edited
  silently.
- **Q002 was open at this pass and closed on 2026-11-09**, after its 0.13.0 presence
  re-measurement (112 of 112 on six seeds). It is now classified kept closed, so the record holds
  **16** kept closed, **23** first answers and **18** runnable cells.
- **The cross-layer rule then did its job:** C004 was a SUPPORTED claim resting on Q004, so it is
  downgraded to HYPOTHESIS with the reason recorded rather than the rule being relaxed. The suite
  asserts that no reopened question's evidence names the pinned release.

- **The historical negative re-derived on the pinned bytes.** A fresh eight-seed, sixteen-cell
  two-arm block on 0.13.0 returned `NO GAIN ON THIS LAYER`: mean paired coverage gain
  `-0.069197`, 95% interval `[-0.095982, -0.043527]`, **0** of **8** seeds positive, and mean
  precision difference `-0.075631`; all six gates passed and the determinism re-run matched. The
  filter changes what is admitted, but it does not cover more of the world on this layer, so the
  answer survives and Q006 moves to `kept_closed` instead of joining the pending campaign.
- **The old record was compared, not re-scored.** `docs/admission_two_arm_result.json` remains the
  historical comparator, with its unattributed build and consumed seed block recorded as such; the
  fresh block is frozen in `docs/q006_admission_rederivation_prereg.json`, the result is stamped in
  `docs/q006_admission_rederivation.json`, and `tests/test_q006_admission_rederivation.py` guards the
  cells, gates, page and seed freshness.

### Added — Every run artifact now names the engine's bytes and the writer (2026-11-08)

- **`engine_version` and the pinned commit are not a build.** `benchmarks/engine_stamp.py` adds
  `engine_sha256` — one digest over the pin's file map, checkable against `docs/engine_pin.json` with
  no git — and `runner`, the calling module read from the stack. Both are computed inside `stamp`, so
  a writer cannot omit them by forgetting a call site.
- **`--check` fails when an artifact writer never stamps, when an artifact names a version and no
  commit, or when a commit field is not a sha.** Writers are found from the syntax tree, so printing
  or round-tripping `json.dumps` is not mistaken for an artifact, and a row-at-a-time JSONL write is a
  data stream rather than a result.
- **Two cases needed care rather than a blanket wrap:** a sealed calibration now hashes the stamped
  record, because a seal must cover what is written, and a disposable cache cell is left unstamped
  because it is compared field for field on reload. Artifacts stamped before the rule are grandfathered
  from the list the audit already records, so no published artifact was edited.
- **`protocol_digest` was deliberately left out:** most artifacts are governed by no preregistration,
  and a field that is empty for most of them is the null-record defect the version audit found. The
  owner's three-track roadmap is recorded in the manual's action list, with decay-factor tuning stopped
  at the characterised operating point.

### Added — The sleep-path split is proven behaviour-preserving (2026-11-08)

- **A refactor is a claim about behaviour, and a diff cannot support it:** `7becdb5` removed 2,400
  lines from `sleep.py` and added 2,313 across four sleep modules and `candidates.py`, and a moved
  line looks exactly like a rewritten one.
- **`tests/test_sleep_split_equivalence.py` extracts `organica/` at `7becdb5^` and at `7becdb5` with
  `git archive`**, runs both on the same twelve cycles of the study stream in isolated processes with
  `PYTHONHASHSEED` pinned, and compares every `SleepReport` field and every substrate row. Wall-clock
  fields (including `ran_at` inside sleep payloads) and the store's per-row event handle are excluded;
  everything else must match.
- **The comparison is controlled so equality means something:** the same variant must agree with itself
  across two processes, and one extra stream word must produce a different fingerprint.

### Changed — The engine guard was unlocked, consolidated and re-baselined on the shipped engine (2026-11-08)

- **The guard skipped every engine-file comparison at version 0.12.0 and above**, so it reported
  success without looking. It now compares the guarded files against the content pin and fails on an
  unrecorded change, with the diff in the message.
- **A second guard — a reference commit plus `git` blob comparison — was added and deleted the same
  day.** Two pins with different file sets and different failure messages are worse than either alone:
  the per-file hash pin enforces identity by content, works in a shallow clone, and has no
  version-gated skip.
- **`tests/test_v1_freeze.py` keeps the published-artifact comparison** while asserting the pin still
  covers the seven frozen files and can still report a changed one. One accountability test built its
  precondition implicitly and is fixed to construct it; another required the guard to keep containing
  the 0.12.0 skip, which pinned the defect in place, and now requires the opposite.
- **The documents that described the old enforcement were corrected:** `AGENTS.md` rule 12, the facts
  sheet's U1/U2, manual section 8.7, the README's package version (which still said 0.12.1) and the
  audit, whose own no-version list contradicted its scan.

### Added — The engine-version audit found that the record could not name its engine (2026-11-08)

- **The freeze narrative assumed one engine and many measurements, but 20 commits since `v0.9.0`
  changed `organica/` by +3,043/-1,791 lines across nine files**, including two of the seven frozen
  ones, and `tests/test_v1_freeze.py` had skipped every engine comparison since 0.12.0.
- **The audit maps every artifact to a build** and reopens Q001, Q002, Q003, Q007, Q008 and Q018,
  whose evidence predates the rework; C001-C003 drop to HYPOTHESIS, because a load-bearing claim may
  not cite an open question.
- **Prior outcomes are kept and labelled as measurements of their own build.** No engine file changed
  and no cell ran.

### Added — Q051's long-delay capability protocol was frozen, run and refused (2026-11-08)

- **The protocol is frozen around recall@5:** 0.9925 against the shipped 0.95 on a seed-varying
  stable-law world, with fresh design and confirmatory blocks, recall@5 as the primary endpoint and log
  loss secondary. The two-seed pilot is disclosed and its seeds are excluded; the question is
  registered as Q051.
- **The design block passed all seven gates and fixed the late bar at 0.0412.** Five design seeds gave
  a late-gap median of +0.0477 with sd 0.0275, one seed reversed, and an early median already outside
  the 0.010 equivalence margin, so P1 was at risk before confirmation. The seed guard now checks only
  the confirmatory block, since the design seeds are consumed by construction.
- **The confirmatory block returned INCONCLUSIVE.** Ten seeds put the late recall@5 median at +0.0265
  against the 0.0412 bar, with 9 of 10 seeds positive; the early median is +0.0119 and growth holds in
  6 of 10. All seven gates pass, but P2, P1 and P3 fail, so no capability claim follows.
- **The `burst_L1` family was added to test whether the arm pair transfers.** At 300 cycles 0.95 and
  1.0 retain theories while 0.99 and 0.9925 do not, so it does not; Q052 records the open question.
  The decision is to keep 0.95: action 50 authorises no engine change and sets a
  competition-preserving intervention and preregistration as the next step.

### Measured — The decay threshold's edge is a competition boundary, not a support floor (2026-11-08)

- **The 24-factor screen found no interior survivor.** Every four-decimal factor from 0.9901 to 0.9924
  dies before cycle 301; 0.9923 and 0.9924 reach 300, so 0.9925 remains the first survivor. The screen
  is one seed and no confirmation branch fired.
- **0.9924 dies at 300 on all three threshold seeds** (20302701-20302703), so the screen's upper edge
  is not a seed accident; Q050 keeps `NO_INTERIOR_SURVIVOR`, and this is a post-screen robustness check
  rather than a new threshold.
- **The support probe corrected the earlier 49-count inference.** 0.9924's last live theory is `bravo`
  at 866 = 433 + 433 at cycle 299, and 0.9925's top theory is `alpha` at 1309 = 438 + 438 + 433 at
  cycle 300, so the edge is a competition/retention boundary, not a support-count floor.
- **The paired bracket ruled out a seed-block effect:** 0.9925 is alive at 301 where 0.9924 dies at
  300, on the same three seeds.
- **The collapse signature is one competing hypothesis per subject at cycle 300**, so no theory forms;
  0.9924's last live cycle is 299 on all three seeds, with `bravo` holding the final pair at 866. The
  engine drops the `high_structural_significance` marker before grouping, which section 15.1 records
  as a correction to the first pass.

### Added — The four remaining decay questions are registered and scoped (2026-11-07)

- **Q033, Q034, Q035 and Q037 are now registry questions** with the owner's wording; the frozen
  replication protocol gains a dated **section 11 amendment**, written before any cell and pinned by
  its own SHA-256, carrying Q033, Q034 and Q037 and three added predictions.
- **Six secondary characterizations** with distinct decisions: `CORE_SURVIVES`/`FULL_COLLAPSE`,
  `COLLAPSE_SCHEDULED`/`COLLAPSE_SEEDED`, `DECAY_DOMINANT`/`THRESHOLD_DOMINANT`. They cannot move the
  primary label.
- **Q035 is deliberately out of scope:** budget independence needs at least three budget arms crossed
  with a seed block, which this run's fixed budget cannot supply.
- **Q043 records the store-time role closure:** 405 of 405 schema-primed predictions recoverable
  across 16,962 rows, zero R1/R2/R3 residuals, so no engine change was needed. Registry: 41
  questions, 18 closed, 12 open, 6 retired, 5 future.

### Added — The decay-attribution replication is pre-registered (2026-11-07)

- **`docs/DECAY-ATTRIBUTION-STUDY-PREREGISTRATION.md`** freezes one instrumented run before it
  exists: seeds **20301201-20301212** (verified unused against 2,609 seeds under `docs/`), 2 arms x
  12 seeds = 24 cells, 300 cycles, degree 12.
- **Six replication targets** are fixed in advance and labelled as restatements of the first study's
  values, not new predictions; **six gates** separate `VOID_INSTRUMENT` (G1, G2, G5, G6) from the
  scientific result `NOT_REPLICATED` (G3, G4), per `docs/DECISION-UNCERTIFIED-RUN.md`.
- **`benchmarks/decay_attribution_study_prereg.py`** pins sections 1-9 by SHA-256 and rejects a
  protocol that records an execution, cites a moved seed block, or whose artifact already exists.
  The runner is not written yet, so this is a pre-registration, not a result.
- **Scope stated, not widened:** Q029-Q032 and Q036 carry the protocol and keep their closed status;
  Q033, Q034, Q035 and Q037 are not in the registry, and the protocol says so instead of inventing
  them. No engine change, no version move.

### Changed — An uncertified falsifier run is void, not a verdict (2026-11-07)

- **The rule:** when the harness refuses to certify a run, the falsifier records the run as
  **void** and reports no scientific verdict. The reading the series still supports is kept as
  an **observation** that cannot close a question, enter a claim, or be counted by an aggregate
  (`docs/DECISION-UNCERTIFIED-RUN.md`, tallied by Q041).
- **Enforced, not asserted:** `benchmarks/verdict_policy.py` holds `certificate`/`decide`/`check`/
  `scientific`; `benchmarks/decay_falsifier.py` now writes its record through `decide` and its
  `--check` rejects a verdict on an uncertified run **and** a void on a certified run.
- **The live record keeps both true statements in different fields:** `certified: false`,
  `verdict: VOID_REFERENCE_DEAD`, `observation: REPRODUCES` — the dead reference arm is the
  finding, and the series is kept beside it rather than promoted over it.
- **Controls:** `tests/test_verdict_policy.py` mutates a passing record in every direction and
  proves the checker fires. No engine change, no version move.

### Changed — The Q028 trace resolves through the schema's role pair (2026-11-07)

- **P0 is built.** `benchmarks/transfer_provenance.py` follows `schema_prior` to the stored schema
  row, reads `source_role_id` and `target_role_id`, loads both stored role rows, and resolves when
  the pair spans the schema's direction and the prediction's `parent_ids` name stored events.
- **Re-measured on seed 20261101 (40 + 40 cycles): 8 of 14 transfers resolve** (share 0.5714),
  against 0 of 14 under the single-role reading. The other six are `unresolved_pair_not_in_roles`:
  the prior licensed them by polarity agreement, not by role membership. R1/R2/R3 are all zero.
- **The event leg was corrected before the result was read**: a single event containing both tags
  is unsatisfiable for a cross-event temporal pair, so the leg now uses the engine's own lineage.
- **Q028 stays open** with the claim narrowed to "resolved to the schema's role pair"
  (`docs/DECISION-STORE-TIME-ROLE-RECORD.md` §11). No engine change, no version move.

### Added — Decay attribution on the degree-12 hub (2026-11-07)

- **The collapse is attributed, not assumed.** `benchmarks/decay_attribution.py` re-runs the budget
  ceiling's own world with a per-cycle ledger and one causal control (temporal edge decay off). The
  engine peaks at **35** edges at cycle **15**, first falls at cycle **16**, is at half by cycle
  **80**, and reaches zero at **173**; the control peaks at **42** and still holds **30** at cycle
  300. Verdict **`TEMPORAL_EDGE_DECAY`**.
- **The mechanism is measured from the engine's own quantities.** Strength is
  `temporal_count / source_frequency`; the median ratio falls from **1.25** to **0.375** while the
  hub's frequency grows 18x and the graph's total grows 1.8x. 31.03% of deaths are re-emitted below
  0.30, 68.97% miss re-emission and die by the x0.8 candidate decay.
- **The protocol's failures are reported as failures.** Three pre-committed predictions failed —
  edges fall *before* the theory layer dies (16 vs 28), the control's first fall is a dip, and the
  strength rule is the smaller half of the loss. Registry: Q029-Q031, Q036 closed SUPPORTED, Q032
  closed UNSUPPORTED.

### Changed — A dead reference arm voids the decay falsifier's verdict (2026-11-07)

- **The gate now precedes every scientific bucket.** When the harness's own reference-arm check
  fails, `benchmarks/decay_falsifier.py` records **`VOID_REFERENCE_DEAD`** and keeps the series
  reading in its own field (`series_verdict`, `REPRODUCES` here). The artifact check rejects either
  direction of disagreement: a failed arm with a scientific verdict, or a void verdict without a
  failed arm.
- **The registry now carries the questions the result opened**: **Q040** closed `SUPPORTED` (0.13.0
  reproduces the death: theories in 37 of 300 cycles, last at cycle 38, none at the end), **Q041**
  closed `UNSUPPORTED` (the falsifier cannot be interpreted with a dead reference arm), and **Q042**
  open (is reference-arm death the dominant failure mode of 0.13.0?), whose why-open names the
  missing per-cycle attribution rather than asserting the mechanism.

### Decided — The engine records no licensing role at store time; the record already survives (2026-11-07)

- **Measured rather than argued.** `benchmarks/store_time_role_durability.py` joins every
  schema-primed prediction of the trace's calibration cell (seed **20261101**, 40 + 40 cycles) to
  the schema row it names and both role rows behind it, reading **16,962** stored sleep rows with
  an unwindowed scan: **405** primed predictions, **405** recoverable, and zero R1/R2/R3.
- **Decision: no engine change.** A `schema_prior_roles` field would be a second copy of what the
  record already holds, bought with a version bump, a re-pin and a neutrality proof. Q028's
  remaining fix is the pair resolver, which is instrument-side.
- **The scoped pre-registration is retired unapplied**
  (`docs/STORE-TIME-ROLE-RECORD-PREREGISTRATION.md`), its criteria kept only as the condition for
  reopening on a cell that prunes beyond 80 cycles. The scope guard now requires the retired status
  to match the evidence artifact's own decision.
- **Nothing about the engine changed**: it stays `0.13.0`, Q028 stays open, CCRE-2's C7 is still
  the resolver.

### Measured — The decay falsifier's artifact now carries an attributable exit status (2026-11-07)

- **The harness persists its own verdict.** `benchmarks/force_matrix.py` writes
  `reference_arm.problems` into the run artifact before it exits, so a non-zero status names its
  reason in the artifact rather than only in console text.
- **The falsifier records the status verbatim.** `benchmarks/decay_falsifier.py` re-ran under the
  fail-closed build and now records `harness_exit_code` **1**, `harness_mode` `fail-closed`, and
  the harness's own reason (`FULL held no theory in its final tenth of cycles`). Its artifact
  check accepts a non-zero status only when it is attributed **and** the series it judges ends at
  zero; an unexplained failure — or an explained one that disagrees with the series — is still
  refused.
- **The verdict is unchanged**: `REPRODUCES` — theories present in **37** of 300 cycles, last at
  cycle **38**, none at the end. What changed is the evidence behind the status: the previous
  exit 0 was written by the fail-open build and could not distinguish an alive arm from a warned
  one.

### Scoped — The store-time role record is an engine change with its own pre-registration (2026-11-07)

- **`docs/STORE-TIME-ROLE-RECORD-PREREGISTRATION.md`** is now a scoped, live pre-registration
  rather than a draft held behind residuals: one field pair written on schema-primed predictions
  (`schema_prior_roles`, plus role exemplars under R2), at most one `sleep.py` repair so a rebuilt
  schema keeps its role ids (R3), and nothing else.
- **Everything that could be fitted is frozen before the edit**: neutrality N1–N4 with N4 a
  mutation control that must fail, trace criteria T1–T4 (T1 exact coverage, T2 carries CCRE-2's
  P4 bar **0.90**, T4 durability under a pruned schema and role rows), a four-bucket decision
  table whose buckets reach four different decisions, and calibration seed **20261101** outside
  CCRE-2's confirmatory block `20272001-20272024`.
- **`benchmarks/store_time_role_prereg.py --check`** guards the scope, including that the engine
  does not carry `schema_prior_roles` while the scope block says `applied: false`.
- **Nothing is applied**: the engine stays `0.13.0`, Q028 stays open, and CCRE-2's C7 stays
  blocked until the pair resolver (P0) exists and the change passes its criteria.

### Measured — The degree-12 coverage ceiling is 0.58 at every theory budget (2026-11-07)

- **`benchmarks/theory_budget_ceiling.py`** measures the quantity the next bar is about: the
  share of a degree-12 hub's world (60 edges) that the engine's stable predictions cover, at the
  shipped theory budget and at two larger ones, recording the **peak** inside the run and the
  **final-cycle** value separately.
- **The result**: peak coverage **0.5833** (35 of 60 edges) at caps 8/15, **identical** at 16/30
  and 64/128; final-cycle coverage **0.00** at all three. Theories reach 7 at the shipped budget
  and 12 at the larger ones, and the theory cap never bound, so **the budget is not the
  constraint** — decay is.
- **Verdict `DECAY_DOMINATED`**, and the next bar is recorded with its endpoint: **0.58 on peak
  coverage**, at most **0.00 on final-cycle coverage** on this build.
- **The recorded 0.40 was not this engine's ceiling**: it came from the lift build that was
  reverted, which is why a bar could not have been set from it.

### Changed — The decay runner trusts the harness exit status (2026-11-07)

- **`benchmarks/decay_falsifier.py`** no longer greps the harness output for
  `produced no theories`. It records `exit_code`, derives `reference_arm_failed` from that
  status, and keeps the last twelve lines as an uninterpreted `tail`.
- **The trusted signal is enforced**: `problems()` rejects an artifact summarised from a
  non-zero exit, and a failure flag that disagrees with the status.
- **Regenerated artifacts**: `docs/decay_falsifier.json` and `docs/DECAY-FALSIFIER-RESULT.md`
  carry `harness_reference_arm_failed` and `harness_tail` in place of
  `harness_reference_arm_warning`, and the page states that this artifact's exit 0 predates
  the fail-closed harness and is not evidence the reference arm was alive.
- **Four tests** prove both directions: a silent failure is recorded as failed, the warning
  printed on a zero exit is not, the summary derives the flag from the status, and the
  artifact check rejects a non-zero status or a contradictory flag.

### Decided — the licensing role is not recorded, because it is already recorded (2026-11-07)

- **The decision**: no engine change. `organica/sleep_extraction.py` already writes
  `source_role_id` and `target_role_id` on every schema (`:762-763`) and `schema_prior` on every
  primed prediction (`:480`), so the role behind a transfer is already stored twice.
- **Why the trace read zero**: `role_match` in `benchmarks/transfer_provenance.py` resolves a pair
  through *one* role whose exemplars contain **both** tags, while a schema is built from two
  **disjoint** role sets and gated on flow from A to B. The predicate was unsatisfiable by
  construction, so `unresolved_no_role` was guaranteed for all 14 events regardless of behaviour.
- **What is built instead**: a pair resolver in the instrument (no engine change, no re-pin), with
  three criteria - full coverage, a status distribution that must change, and the claim narrowed
  from "resolved to a role" to "resolved to the schema's role pair".
- **Reserved, not applied**: `docs/STORE-TIME-ROLE-RECORD-PREREGISTRATION.md` fixes the engine
  change that would follow residuals R1-R3, with four neutrality criteria, a mutation control that
  must be able to fail, exact coverage T1 and the 0.90 trace bar carried from CCRE-2.

### Added — The second cross-context run is preregistered and blocked (2026-11-07)

- **`docs/CROSS-CONTEXT-REUSE-2-PREREGISTRATION.md`** fixes, before any cell: five arms
  (treatment, naive, pruned, orthogonal and a **shuffled-prior** attribution control), 60 cells
  at 40/40 cycles, a fresh 24-seed block with 12 reserve never drawn, and every comparator with
  its swept grid - including a decayed bigram over Context B's own events as the strongest
  simple learner.
- **Four criteria, judged together.** Transfer ratio at least 1.25 with its lower bound above
  1.00; at least 0.10 above both the orthogonal and shuffled arms; rank at acquisition at least
  2 positions better than naive; and Q028's trace resolving at least 0.90 of transfer events with
  no unexplained unresolved transfer. **P4 can fail the protocol even when the behaviour is
  right** (rule 18).
- **Three void conditions and seven controls**, including endpoint saturation, a fail-closed
  reference arm, the trace instrument's own self-test, and provenance pinning.
- **It cannot start yet:** the trace resolves 0 of 14 transfers because the engine records no
  role per prediction (C7), and `force_matrix --verify-only` exits 1 on the dead reference arm.
  The licensing record now names this protocol.

### Added — Q028's transfer-provenance trace exists and can fail (2026-11-07)

- **`benchmarks/transfer_provenance.py` traces a transfer event to a role satisfaction from
  recorded state only**: the role whose exemplars contain the transferred pair, at least one
  recorded event asserting it, and the schema prior the engine wrote on the prediction. Each
  missing leg is its own status, and the share is reported with its denominator; a zero
  denominator is `null` and not measurable (AGENTS rule 13b).
- **It is proved able to fail before it measures.** Five known-answer fixtures, three flips that
  remove one leg at a time, and a comparator pointed at a tracer that always answers "resolved"
  all run first; `--self-test` exits non-zero if any fails, and a test substitutes the broken
  tracer to check the exit status changes.
- **The pre-run measurement recorded 14 transfer events and resolved 0**, all
  `unresolved_no_role`, with 0 of the 14 prior ids also seen in context A: Q028's own
  `not_answered_if` outcome. The first definition (an identical tag pair) was replaced before it
  produced a denominator, because disjoint context vocabularies make it unfireable.
- **Artifacts:** `docs/transfer_provenance.json`, `docs/TRANSFER-PROVENANCE.md`,
  `tests/test_transfer_provenance.py`.

### Fixed — The campaign fails closed on a dead reference arm (2026-11-07)

- **`benchmarks/force_matrix.py` now exits non-zero when the reference arm is dead.** The G1
  check already detected it and printed `FULL produced no theories -- the reference arm is
  broken`; the process exited 0, so a caller reading the status saw success (row 40). G1 now
  returns its problem list, the measured-campaign path and `--merge` check the `FULL` row's own
  theory trace for an arm that dies in its final tenth of cycles, and every one of those paths
  exits 1. The artifact is still written, so the failure has a record.
- **`benchmarks/run_matrix.py` refuses to launch on a G1 problem** and fails after merging a
  dead `FULL` row, instead of reporting a campaign whose comparison arm is empty.
- **On the current build `--verify-only` exits 1**, because the reference arm is still dead at
  G1: the campaign stays blocked until the decay rule is fixed, which is what fail-closed means.
  `tests/test_force_matrix_exit.py` covers the dead, missing, late-dead and live cases.

### Added — The next cross-context run is licensed question by question (2026-11-07)

- **`docs/ccre_question_licensing.json`** with its rendered `docs/CCRE-QUESTION-LICENSING.md`:
  every question the campaign may touch is tiered *answers*, *moves* or *records*, and the
  questions the design cannot adjudicate are refused with a reason. Seven licensed (two answered,
  two moved, three recorded), five refused. Q028 is the trace-derived diagnostic rule 18 requires.
- **Three rules are checks, not prose.** `benchmarks/ccre_licensing.py` fails if no licensed
  question is trace-derived, if a closed or retired registry question is licensed as unsettled,
  or if an answered-tier row has one decision or two that agree (rule 30). `--check` also
  compares the page against a fresh render and writes nothing.
- **Q022 is licensed to move, not to answer**, because the registry asks about transfer across
  domains while this design varies context inside one world family; the record states the gap
  rather than letting a summary close it (rule 24).
- **Four questions were registered to make the licence checkable** — Q025 to Q028, all open or
  future with prerequisites named, taking the registry to 28. The fraction question arrived
  labelled Q024, which is the retired admission question; the record discloses the renumbering.
- **It sets no bar and authorises no run.** No threshold, sample size or measured figure appears
  in the record; the campaign has no preregistration on disk and the page says nothing may run.
### Added — The decay falsifier ran first, and it blocks the campaign (2026-11-07)

- **`benchmarks/decay_falsifier.py`** runs the change map's M04 falsifier on the pinned engine
  (`FULL`, 300 cycles, seed `20261023`, `PYTHONHASHSEED=0`) and derives the verdict from the
  series rather than recording one. Result: **REPRODUCES** — a theory is present in 37 of 300
  cycles and last at cycle 38, a belief in 112 and last at 113, the same cycles the 0.12.0
  reference reported over 3,000. The falsifier's condition (a live theory throughout) did not
  hold, so decay-to-death survives and the campaign stays blocked until the decay rule is fixed.
- **The harness is fail-open and the runner says so.** `force_matrix.py` prints that the reference
  arm is broken and exits 0; the runner records the warning and the exit code as separate fields,
  because a check that reads only the status inherits the bug it is checking for.
- **`docs/decay_falsifier.json`, `docs/DECAY-FALSIFIER-RESULT.md`**, the harness report and the raw
  series are generated by that command; `--check` re-derives the counts from the raw series,
  re-derives the verdict, and compares the page against a fresh render without writing.
- **The map now carries its first measured row.** A row's `result` names an artifact and a verdict,
  never a number, and the validator rejects a result with no artifact, a result pointing at the
  pre-change artifact, or a result on a row not measured on that build.
- **Stage B's consumed-seed scan counts the new artifact:** 1366 seeds across 122 artifacts, up
  from 121; no seed is newly consumed and the candidate block's overlap stays empty.
### Added — The density interaction: registered, frozen, unrun (2026-11-07)

- **`docs/density_interaction_prereg.json`** with its rendered `docs/DENSITY-INTERACTION-PREREGISTRATION.md`:
  160 judged cells over fresh seeds 20330101–20330108 (2 arms × 2 caps × 5 densities × 2
  exposure schemes), two bars of 0.08, gates G0–G6, the rho = 1 identity fixture and the
  decision table, all committed before the first cell.
- **`benchmarks/density_worlds.py`** builds the declared ladder: 16 tags in four cells, W
  drawn from the 192 cross-cell pairs only, so no intra-cell row can be a world edge, and
  the within-cell filler's share falls with density. `--self-test` audits the grid, the
  generator, the arms' liveness, the identity fixture and seed freshness with no engine.
- **The endpoint is precision at a fixed cap**, not coverage: coverage divides by |W|,
  which grows 24→192 across the ladder, so a coverage difference is forced by arithmetic
  — the defect that withdrew the ordering block's M2. The criterion is the interaction on
  precision, judged whole.
- **Amendment A1 (pre-run):** the design record's registered *decline* was contradicted by
  its own designed pools, which measure the advantage rising from 0.075 at rho 0.1 to 0.350
  at 0.8. The mechanism is that the freed budget is bounded by the number of world rows
  available to fill it. The original prediction is retained in the design record and marked
  superseded there; the criterion tests the corrected direction.
- **`benchmarks/run_density_interaction.py`** runs the block (sliced and appendable, refusing
  to overwrite a cell) and **`benchmarks/score_density_interaction.py`** is the frozen
  analysis path, importing nothing from the engine. No arm has run.
- `docs/bottleneck_map.json` and the map's row now name the registration and its allocation
  (8 seeds, 160 cells, 2 thresholds, 2 bars), with `run: false` beside it. The design record
  still allocates nothing.

### Changed — The density ladder's mid-ladder dip is attributed to the primary scheme's padding (2026-11-07)

- **`docs/DECISION-DENSITY-EXCLUSION.md` section 2 now explains the non-monotonicity instead of only
  reporting it.** Total exposure is fixed at 400 events while the base grows as 2|W| + 24, so the final
  partial pass ends in the world-edge head at rho 0.1–0.6 and in the filler tail only at 0.8; with the
  engine's 0.95-per-cycle decay the freshest cycle holds the top of the ranking, so the intra-cell class
  the exclusion removes is de-exposed at mid density by construction.
- **Measured, not inferred:** the primary control spends 0.88 of its 20 cap slots on intra-cell rows at
  0.4 (sensitivity: 3.75) and 5.00 on cross-cell rows no exclusion can remove (sensitivity: 1.75), so
  Delta is 0.0281 there instead of 0.1469. The schemes agree at 0.1 and 0.8, where the criterion is read.
- **No verdict, criterion or artifact changed.** The table is recomputed from the run by
  `tests/test_decision_density_exclusion.py`, which also checks the generator's ending class at every
  density.

### Added — The engine-change audit, and the freeze finding it produced (2026-11-07)

`docs/ENGINE-CHANGE-AUDIT.md` inventories what changed in the engine after the archival freeze:
**20** commits touching `organica/` between 2026-10-25 and 2026-11-07, five new modules, a raised
prediction cap, a lookback-contamination fix and a submodule split. Its central finding is that
**none of the recorded failures was measured on the engine at HEAD**, so a rerun campaign is a
different experiment rather than a replication.

It also records that the freeze no longer checks the engine: all seven
`test_engine_file_is_unchanged_since_the_freeze` cases **skip** at package versions at or above
0.12.0, while the eight published-artifact checks in the same file pass. The skip is a version
gate, not an unreadable tag, and `docs/V1-FREEZE.md` §6 states it — so the freeze is documentary
from 0.12.0 onward and nothing compares the live engine against `v0.9.0`. A campaign that pins an
engine needs its own identity check, built to fail.

The audit also corrects a carried-forward status: **C1 failed as pre-registered** (P2 not met),
and H2 is untested in an admissible form because F2 fired first. `tests/test_engine_change_audit.py`
recomputes the commit count, the pinned commits and the frozen-file list rather than trusting them.

### Added — The context that was held in conversation is now a labelled register (2026-11-07)

`docs/CONTEXT.md` records three kinds of fact that existed only in conversation: what the owner
can afford to run, who the work is addressed to, and what the project explicitly does **not**
claim. Every row carries one of three provenance markers — `repo` (already in an artifact, cited),
`owner-reported` (testimony, dated) or `unknown` (nobody has recorded it) — so a fact stated in
passing cannot later be read as a measurement. The `unknown` rows are the finding: hours per week,
the host machine, funding, any deadline and any institutional affiliation are unrecorded, while the
one quantified capacity fact is derived from `docs/stage_b_cost_estimate.json` (about 29 hours of
single-core-equivalent compute for one Stage B pass) and `tests/test_context_doc.py` recomputes it
rather than trusting the prose. The not-claimed table gives each denial a licence condition — what
result would force the claim to be made — instead of a disclaimer that no check can fail.

### Added — The project's questions are a generated registry, and outreach has its own note (2026-11-07)

`docs/research_question_registry.json` records **23** questions — **10** closed, **6** open, **5**
retired, **2** future — with the answer, the scope, the evidence and the decision record behind each.
`benchmarks/research_registry.py` validates it and renders `docs/RESEARCH-QUESTION-REGISTRY.md`,
refusing to render when a `docs/DECISION-*.md` is untallied, a bottleneck-map row is unclaimed, a
closed or retired question cites a document that is missing, or a future question names a
prerequisite that does not exist. `tests/test_research_registry.py` holds the rendered document equal
to a fresh render, so a stale tally fails the suite.

`docs/OUTREACH.md` says why the repository should be put in front of a researcher — the independent
Stage B review is a hard gate, and the strongest result here is a verified negative that needs a
reader who prices nulls correctly — what to send (deposit first: `papers/README.md` records eight
manuscripts and zero published, and Papers 01 and 02 carry complete packages), and what to lead with:
the earned cross-context result, TR **0.944** against **3.4** cycles naive over five seeds with no
p-value, verdict `STRUCTURAL_PRIOR_PRESENT_NO_ACQUISITION_ADVANTAGE`. It gives the rule for the
withdrawn v1 numbers (they appear only beside the word *withdrawn*), keeps established, open and
not-demonstrated claims in separate tables, and labels the role, cross-domain, reusable-knowledge
chain as a research programme rather than a finding. AGI is recorded as not demonstrated.

### Added — A third exposure scheme tested the padding attribution and only half confirmed it (2026-11-07)

- **`DENSITY-PADDING-1`** registers `whole_cycle`: the base stream repeated a whole number of times,
  so every base position is exposed equally and every stream ends on the filler tail. Seeds and
  densities are inherited by reference from A2; the A2 block, its criteria and its artifacts are not
  amended, and the scheme is an additive branch in `benchmarks/density_worlds.py`.
- **The phase gate held and can fire:** every base occurrence is emitted exactly `passes` times at
  every density, every stream ends on a filler event, and the primary stream fails the same check.
- **Result: `WHOLE-CYCLE PADDING DOES NOT RESTORE A MONOTONE LADDER`** — 0.0531, 0.0719, 0.0844,
  0.0500, 0.1500, with the 0.4 → 0.6 step at −0.0344, so P1 and P2 both fail; the negative control
  confirms P1 fires on the A2 primary profile.
- **The earlier attribution is narrowed.** The padding phase accounts for about half of the 0.4 gap
  between the primary and per-edge readings (0.0562 of 0.1188) and no longer for the whole
  mid-ladder shape; the residual is recorded as measured but unattributed, coinciding with the
  control's intra-cell slots falling from 2.44 to 1.06 between 0.4 and 0.6.

### Changed — Intra-cell exclusion adopted as an allocation change, and not implemented (2026-11-07)

- **`docs/DECISION-DENSITY-EXCLUSION.md`** records the owner's decision: rows whose two tags sit in
  one cell are not eligible to occupy a fixed selection budget, and the same count ordering applies
  to the eligible rows. It is dated, it names the evidence artifact, and its scope is the share of a
  fixed budget spent on world edges — one world family, cap 20, both exposure schemes.
- **The evidence is the A2 verdict, quoted from the artifact**: sparse-end level 0.059375 with
  interval 0.040625–0.078125 against the 0.05 bar, 13 of 16 seeds positive, reproduced by the
  sensitivity scheme. The slope is explicitly excluded as a reason: descriptive, dense end pinned at
  0.150, primary-scheme middle non-monotone.
- **Nothing is implemented.** No engine file changed; the record states that going live needs its own
  implementation record and a behaviour-preserving test, and that absence of a behavioural gain is a
  limit rather than a reversal. `tests/test_decision_density_exclusion.py` re-checks every quoted
  figure against `docs/density_interaction_a2_result.json`.

### Added — The density block A2 ran and returned its positive branch (2026-11-07)

- **All 640 registered cells executed** on seeds 20330201–20330216 with `PYTHONHASHSEED=0`,
  as a detached process sliced into three runs and appended; every gate passed.
- **Verdict: EXCLUSION PAYS AT SPARSE DENSITY AND GROWS WITH DENSITY.** The sparse-end
  precision level was **0.059**, 95 percent interval **0.041–0.078**, against the **0.05** bar,
  with **13 of 16** seeds positive; the sensitivity scheme reproduced the sparse end exactly
  (0.059, 11 of 16) and both schemes read **0.150** at the dense end.
- **The slope is descriptive, as registered:** +**0.091** (0.072–0.109) is reported and placed
  by the decision table, not scored, because the dense end is pinned by the pool's
  composition. The verdict licenses an allocation change on this layer and no behavioural
  claim; `docs/density_interaction_a2_result.json` holds it and §9 of the rendered
  registration states it.

### Changed — The density block is held before the run: its dense end has no headroom (2026-11-07)

- **A pre-run review, on five unregistered seeds, found the registered criterion cannot be
  satisfied by this world.** At rho_world 0.8 under fixed total exposure the pool is 240 rows
  of which 192 are world edges, so a count-ranked top-20 is all world edges: control and
  treatment both score precision 1.000 on every seed, Delta(0.8) = 0, and the interaction is
  −0.06. Under fixed exposure per edge Delta(0.8) = 0.200, so the schemes disagree in sign —
  the design record's own definition of an exposure artifact. No judged cell ran.
- **Five harness defects fixed:** the rho = 1 identity fixture selected the whole pool and so
  could not fail; G0 compared stored order instead of selected sets; the world description
  claimed the filler's share was (1 − rho) when only its count is proportional; two event
  totals were hardcoded instead of read from the world module.
- **The design record's precision bound was false and is corrected.** "Precision cannot exceed
  rho_rank" fails whenever the ranker prefers world rows; the control measured 1.000 against a
  rho_rank of 0.800. The bound is min(1, |W ∩ P_rank| / k). The registration never gated on it.
- **The registration is HELD, not scored.** A2 needs a budget that is a fixed fraction of |W|
  (cap = |W|/4 gives 6 slots at 0.1 and 48 at 0.8) or an interaction anchored where the control
  is below the ceiling. `docs/DENSITY-INTERACTION-REVIEW.md`, `docs/density_interaction_review.json`.

### Added — The density interaction, block A2: held A1 replaced by a runnable registration (2026-11-07)

- **`docs/density_interaction_a2_prereg.json`** with its rendered
  `docs/DENSITY-INTERACTION-A2-PREREGISTRATION.md`: 320 judged cells plus 320 exposure-check
  cells (2 arms × 2 caps × 5 densities × 16 fresh seeds), one bar of 0.05, gates G0–G6 and a
  seven-row decision table, all committed before the first cell. A1 is retained, HELD and unrun.
- **The world's filler family is now constant**: a fixed within-cell event mass at every
  density, so the ineligible class competes for the ranking budget across the whole ladder.
  The proportional family is A1's and is not run.
- **The judged criterion is the sparse-end precision level**, not the interaction. With cap 20
  at or below the world-edge count at every density, the treatment removes a class that is
  never a world edge, so it is perfect whenever the pool holds ≥ 20 world rows: the pilot
  measured Δ(0.8) = 0.150 with zero spread on eight unregistered seeds. The slope is reported
  with its interval and its per-seed values and placed by the decision table, but it is not
  scored — an interaction criterion there would be arithmetic.
- **The bar is 0.05, calibrated on seeds 992001–992008**, which this block does not judge: the
  sparse-end mean there was 0.094 with sd 0.062, so the level is powered (~0.8) at sixteen
  seeds. The runner gained `--prereg`; it accepts any contiguous block of at least eight seeds
  and derives the cell count from the registration rather than a literal.
- **`benchmarks/score_density_interaction_a2.py`** is A2's frozen analysis path and
  **`benchmarks/write_density_a2_prereg.py`** renders its document; `tests/test_density_interaction_a2.py`
  shows every pole reachable, every gate able to void the block, and the document equal to the
  artifact.

### Changed — diversity-first admission, adopted, measured and withdrawn (2026-11-07)

- **`organica/admission.py`** carried the adopted admission rule (removed at withdrawal,
  below): each budget slot takes the eligible prediction whose source tag owns the fewest
  already-admitted outgoing edges, ties
  broken on count and then on the stable key. `COUNT` is the confirmatory block's control
  ordering and is retained beside it; the adopted service's `COUNT` arm delegates to the
  engine and returns its admission unchanged.
- **The budget floor is a floor, not an increase.** Under the adopted rule the cap is
  `max(cap, eligible source tags)`, which is inert at the engine's own caps in a 16-source world
  and binds only where a caller sets a cap below the source count.
- **`DiversityFirstSleepService`** (removed at withdrawal) was a `SleepService` subclass that
  overrode `_build_predictions` and nothing else. Under `COUNT` it delegated to the engine and
  returned its admission unchanged; under `DIVERSITY` it ranked the eligible pool, which
  superseded the engine's
  stratified transition/co-occurrence quota (disclosed in the decision record). `organica/sleep.py` is not edited: the frozen engine keeps the frozen rule,
  and every published count-basis measurement stays reproducible.
- **The decision is recorded before the code**: `docs/DECISION-ADMISSION-RULE.md`, with
  `docs/V1-FREEZE.md` §7 carrying the amendment. Coverage is not behaviour, and the record says so.
- **Withdrawn the same day, on that measurement.** A rule its own measurement closed is not a
  policy an engine version should carry, so the adoption was reversed rather than left standing as
  a non-default arm: `organica/admission.py` and `tests/test_admission_rule.py` are deleted, and
  `SleepService` is again the only admission path in the package. The decision record is
  `docs/DECISION-ADMISSION-RULE.md` — §6 keeps the measured outcome exactly as the frozen analysis
  returned it, §7 records the withdrawal — and `docs/V1-FREEZE.md` §7 carries the reversal, with
  §1 untouched at every step. The block stays reproducible from **`a82e890`**, the last commit that
  contained the adopted arm; `benchmarks/run_admission_two_arm.py` resolves both arms lazily and
  stops with that commit's name instead of an `ImportError`.
- **Measured outcome (2026-11-07): the adopted order loses on the prediction layer.** The
  pre-registered two-arm comparison returned `NO GAIN ON THIS LAYER`: mean paired coverage
  gain -0.077009 over its interval, 0 of 8 seeds positive, precision also down. The pooled-edge
  gain does not transfer; the layer is closed to this rule, the service was withdrawn (above), and
  `docs/DECISION-ADMISSION-RULE.md` §6 records the outcome.
- **`tests/test_admission_rule.py`** (removed at withdrawal) proved the count arm reproduces
  `SleepService`, that the adopted arm differs where one source is crowded, that the floor is
  inert at the engine's caps and binds below them, and that no frozen engine file is modified.

## [0.12.1] — (unreleased; superseded by 0.13.0)

### Added — The temporal-decay confirmation harness and its pre-registration (2026-11-06)

- **`benchmarks/decay_confirmation.py`** implements the pre-registered confirmation of the
  transition-probability strength: a measured-degree world audit, a threshold calibrated on a
  separate seed block and sealed with a sha256, held-out stationary/shift/task cells, and a
  conjunctive analysis that returns a named rejection instead of a weak pass.
  `tests/test_decay_confirmation.py` produces every rejection label, so no gate is decoration.
- **`analyze` refuses an artifact it cannot honestly score.** A missing, malformed or
  cell-less held-out file is a usage error with a message, not a `FileNotFoundError`
  traceback, and a held-out run whose recorded `calibration_sha256` is not the calibration
  passed to `analyze` is refused, so cells produced under one threshold pair cannot be
  scored against another. Five CLI tests drive the real parser, seal and seed guard.
- **`docs/DECAY-FIX-CONFIRMATION-PREREGISTRATION.md`** fixes the protocol before any cell,
  with five dated pre-run amendments: the shipped arm's closed-form `1/N` ceiling at degree
  4 and above, the measured even degree ladder (2/4/6/12) with scan-chosen seed blocks, and
  non-inferiority to the strongest simple baseline on the task endpoint, a ratio-strength
  threshold-control arm calibrated on the same seeds, and an explicit definition of a
  boundary selection at 0.075.
- The four-option decay measurement (`docs/DECAY-FIX-OPTIONS.md`,
  `docs/prediction-decay-options.json`), the 0.9.0/0.12.0 comparison pre-registration, the
  0.12.0 engine identity record and its test are recorded alongside it.
- **The engine is unchanged.** Option 2r remains a lead candidate, not an adopted fix, and no
  paper result is updated; the version moves only because `v0.12.0` is tagged at `5804e60`
  and master must not drift past a release it still declares.
- **The pre-registered calibration ran and selected no threshold, so the campaign stopped and nothing was adopted.** 448 cells on `0.12.0` (`5804e60`) with the harness at `841e3ff`: the degree audit passed and the seal verified, but for both the transition arm and the ratio control no threshold in the grid was live on every cell while keeping precision at or above 0.95 on every cell, so both recorded the pre-committed `no global threshold clears all degree regimes`. No held-out cell was run. The artifact is on the owner's machine, not in this tree; the record is §18 of the preregistration.
- **`docs/DECAY-OPERABILITY-PROPOSAL.md` records the recommended next direction and authorises nothing.** No threshold is chosen or searched for; a decay-off version is the pragmatic route with `0.12.0` immutable, and restoration is not release-ready until long-run liveness and edge growth are checked. The seed block, the horizons and the edge-growth criterion are the owner's and left unset.
- **`benchmarks/decay_operability.py` measures decay-on against decay-off on the matrix's own stimulus, seed and 3,000-cycle horizon.** Two arms differing in one class attribute, per-cycle theories, beliefs, stable predictions, temporal-edge rows and mass, and database bytes; a protocol artifact only at the matrix settings with `PYTHONHASHSEED=0`, pilots under `.scratch/` and marked. Growth is reported, not judged, and no engine file changes.
- **`docs/DECAY-TUNING-CYCLE.md` separates exploratory tuning from confirmation, and fixes fresh seed blocks in `docs/decay_tuning_cycle.json`.** The 448 cells bound the tested grid and rule only; a tuned rule is frozen on development seeds and adopted only on a new confirmatory block. No cell ran, no rule exists, and no old cell becomes confirmatory.
- **`docs/DECAY-NULL-SCOPE.md` bounds the 448-cell null to its grid, gates and selection rule.** The design is 7 thresholds x 4 degrees x 8 seeds x 2 calibrated arms, the rule is a per-cell conjunction, and for the transition arm every tested threshold fails at least one gate — so the conjunction is not the cause. One five-hundredths-wide interval is untested; its resolution needs the sealed artifact, which is not in this worktree. No verdict was re-scored and nothing was adopted.
- **`docs/WORLD-DENSITY-DESIGN.md` records world-edge density as an untested hypothesis.** The variable is |W|/|C|, not an edge count: 16 tags give 240 directed pairs, and 500 edges needs at least 23 tags at density 0.988. The exposure tradeoff is an explicit choice, the claim is an interaction between the ranking intervention and density, and no seed, cell, threshold or bar is allocated. The 448-cell null is not offered as evidence.
- **`docs/DECAY-NULL-SCOPE.md` corrected: the untested threshold interval is one grid step, not two.** Against the verified artifact the transition arm is liveness-rejected already at 0.15 and precision-rejected at 0.10 and below, and the ratio arm at 0.20 and above forms no stable predictions at all, so its precision is `None` in every cell. Adjacent rejections for opposite reasons is where grid resolution decides the answer, so the null is either structural or a resolution artifact. The verdict and the adoption status are unchanged.
- **`docs/WORLD-DENSITY-DESIGN.md` separates `P_world` from `P_rank` and registers a direction.** The manipulated quantity is `rho_world` = |W|/|P_world|; the ranker's own population `P_rank` is measured per cell, and selection precision cannot exceed its true-edge share — a bound the study checks rather than assumes. The treatment is intra-cell-excluded ranking against the engine's global count-ranked top-k, and the prediction is that the advantage declines with density and vanishes at rho = 1. Still no seed, cell, threshold or bar allocated.

- **The 3,000-cycle decay-operability run is recorded as liveness, not as soundness.** The decay-off arm holds theories and beliefs through the matrix's full horizon while edge mass grows 1,819 -> 197,753 (×108.715; ×3.838 at 80 cycles). The mass is `SUM(precedes.count)` — accumulated transition weight, not a row count — and no growth bound was pre-committed, so the result is reported and explicitly not judged. Values come from `docs/decay_operability_record.json`, not from prose.

- **The bottleneck map is recorded as a claim-status artifact.** Eight candidate explanations each carry one of the four statuses, the check behind them and what the status does not say. Writing it corrected two rows: decay necessity is *unresolved* rather than *not supported*, and selection/allocation is a demonstrated constraint on coverage whose effect on behavior is untested rather than a demonstrated contributor. Only the density interaction is a specified experiment, and it allocates nothing. `docs/BOTTLENECK-MAP.md`, `docs/bottleneck_map.json`.

## [0.12.0] — (2026-11-06)

### Changed — The release identity is settled: v0.12.0 is the deposit object (2026-11-06)

- **One version names the deposited software.** Package, `pyproject.toml`, `CITATION.cff`,
  README, changelog and both Zenodo records say **0.12.0**; `v0.9.0` stays the archival
  reference for the frozen engine and `v0.10.0` is the previous cut tag. The `v0.12.0` tag is
  cut at this commit, and `CITATION.cff` carries the tag date rather than another version's.
- **The deposit descriptions are true of the commit.** The old
  `zenodo/software-v0.11.0.json` claimed `organica/` was byte-identical to `v0.9.0` and that
  the freeze test fails on any difference; the engine differs across nine files and the test
  skips its engine checks at `>= 0.12.0`. The record is renamed
  `zenodo/software-v0.12.0.json`, and both it and `.zenodo.json` now state that the engine
  advanced past the freeze, name `v0.9.0` as the archival reference, and link the record to
  the repository as part of it rather than claiming identity.

### Changed — Built paper artifacts are kept out of the repository (2026-11-06)

- **The rendered PDFs and deposit zips are release payloads, not repository files.**
  `artifacts/` carried two manuscript PDFs and two deposit zips (1.9 MB) that no script writes
  at that path and no document references, while `benchmarks/deposit_bundle.py` builds the
  deposit into `.scratch/deposit/` with a `MANIFEST.json` and `SHA256SUMS` per record. Every
  manuscript, figure and cited artifact the bundles are built from is tracked, so the directory
  is now gitignored and a second copy cannot drift from its sources. The bundles are attached to
  the release/Zenodo record when the version is cut. `docs/figure_p0*.pdf` remain tracked because
  the manuscripts cite those figures and `benchmarks/figure_papers.py` regenerates them.

### Added — Paper 07: the architecture's five predictions, three reversed (2026-11-06)

- **The Tier-1 matrix and the Phase K ablations are written up as a manuscript.**
  `papers/07_architecture_predictions_reversed.md` reports the five preregistered architecture
  predictions direction-aware: P1 (retention) and P4 (dreams) supported; P2 (contradiction's
  weight), P3 (question generation) and P5 (EIG) reversed. The contradiction colony is disclosed
  as de-weighting rather than removing, M5 is named as a finite inventory over run length rather
  than a velocity, and Phase K's three matched ablations all contain zero.
- **The tables are checked, not typed.** `tests/test_reversals_paper_numbers.py` rebuilds the
  verdict and Phase K rows from `docs/verdicts.json` and `docs/phase_k_results.json` and is itself
  exercised against fabricated deltas, bounds and verdict labels.
- **The manuscript inventory moves from seven files to eight, still with no DOI.** The count is
  updated in `papers/README.md`, `README.md`, `docs/USER-MANUAL.md` (finding 30), `docs/FACTS-SHEET.md`
  (AD2) and Paper 00's companion note; the draft is not in the deposit queue.

### Changed — Papers 03 and 04 reconciled with Paper 07 (2026-11-06)

- **Both mechanism papers now cite the ablation their own "next test" sections asked for, and say which
  conditions it meets.** Paper 03 records the Tier-1 matrix against its five conditions: the exact quantity,
  a mechanism-off control and equal budgets are met; an external outcome is not; the decision rule is met
  only as a direction rule against a measured floor, since there is one seed per colony and one world.
  Paper 04 records the matched no-dream arm against its evaluation list: equal-budget dream-on/off is met,
  while the random-candidate control, the external outcome and the provenance split are not.
- **The restated effect sizes are guarded.** +0.166, +1.266, +0.366 and -1.000 are checked against
  `docs/verdicts.json` by `tests/test_reversals_paper_numbers.py`, which also asserts that both papers
  cite Paper 07.

### Fixed — Reproducibility repairs (2026-11-06)

- **The three DI artifacts record a portable source path.** `di_construct_audit.json`,
  `di_window_design.json` and `di_transition_construct.json` stored `str(Path)` as
  `docs\phase_l_results.json` (Windows separators) together with a sha256 taken before the
  source file's last edit, so `test_the_stored_artifact_is_current` failed on any other
  host. The builders now record `as_posix()` and each artifact was regenerated; a
  leaf-level comparison confirms only `source.path` and `source.sha256` changed — no
  measurement moved.
- **The tied-window tests no longer assume one SQLite tie order.** The window-rotation
  wrapper rotated unconditionally, which displaces the stored row only when the build
  sorts it first; on a build that sorts it last the manipulation silently stopped firing
  and the test failed. It now displaces the stored row only when it is first, so the
  rotated window always starts with an older tied row. The companion test no longer
  asserts that the build's first row agreed with the stored row — an implementation
  observation its own docstring disclaimed, not the claim under test; the per-store target
  identity remains asserted.

### Changed — Freeze amendment: carried-forward structures are not current-cycle evidence (2026-11-06)

- **Owner-authorised amendment to the Organica 1 freeze.** `organica/sleep.py` re-admitted
  every stable G2/G3 prior into the current cycle before natural selection, so a structure
  that had stopped being produced was counted as re-emerging, reinforced +0.05 per cycle and
  never decayed. The five carry-forward grafts now mark the re-admitted object
  `carried_forward=True` (a transient field on the five dataclasses in
  `organica/candidates.py`), and `organica/sleep_selection.py` excludes such structures from
  the current-cycle key set and from re-storage. They remain in the report for downstream
  layers and telemetry; the marker never reaches the store. Recorded in
  `docs/V1-FREEZE.md` §6.
- **Measured consequence.** Both arms of `benchmarks/candidate_supersession_probe.py` now
  decay by ×0.8 and retire on their closed-form cycle, where the schema arm previously rose
  to 1.0 and never retired.
- The engine-file identity check already skips at package version ≥ 0.12.0, so no pin was
  changed: the amendment is recorded, not enforced by editing the mechanism.
- **Measured consequence on the frozen engine's own Gate 13.** Gate 13 reads its asserted
  basis off the surviving candidate set, so the amendment moves that figure. On the harness's
  default seed at 112 world edges: `e6d1bcc` 0.2321, the supersession reader alone
  0.1964, the reader plus this amendment 0.3036 — raw temporal coverage is
  112/112 in all three, and the gate still fires because 0.3036 is far below the 0.50
  threshold. Every Gate 13 figure recorded before this amendment therefore describes the
  pre-amendment engine; they are labelled as such in `docs/V1-FREEZE.md` §6 and are not
  re-scored. Artifact: `docs/candidate_supersession_gate13_effect.json`.
- **A harness bound restated as a claim rather than an absolute.**
  `tests/test_acquisition_harness.py` asserted `asserted_coverage < 0.3` — a number tuned to the
  pre-amendment build, which the amended engine clears. It now asserts that raw coverage
  exceeds 0.9, that the asserted reading is below the gate's own 0.50 threshold, and that the
  raw reading holds more than twice the world edges the assertions do.
- **The Gate 13 cap-20 pilot range does not reproduce on later builds.** Re-running the paired
  capacity test's control arm (`run_paired_condition`, `max_predictions=20`, the same five
  diagnostic seeds and 112 world edges): as recorded on `89b0744` (2026-10-28)
  0.0000–0.0268 with 0 of 5 seeds passing Gate 13; at `e6d1bcc`
  0.6607–0.8125 with 5 of 5 passing; on the amended engine
  0.4821–0.7500 with 4 of 5 passing. Bisected on seed `20261101`, the
  first build off the recorded band is `9f2c8e1` (2026-11-04) — so the move predates the freeze
  amendment, and the amendment's own effect on this basis is to lower the range by 0.06–0.18. Runs are
  deterministic within a build and hash-seed independent. The re-check of `89b0744` covers one seed,
  where it reads 1 of 112 against 0 of 112 recorded, and the cap-1000 treatment arm was not
  re-run. Correction and the list of documents still quoting the old range:
  `docs/GATE13-PAIRED-CAPACITY-TEST.md` §5; artifact `docs/gate13_cap20_build_comparison.json`.
- **The cap-1,000 treatment arm still holds, and the paired margin is narrower than the record
  implies.** Re-running the treatment arm on the same five diagnostic seeds: recorded `89b0744`
  0.9821–1.0000, `e6d1bcc` 1.0000–1.0000, amended engine 1.0000–1.0000 (5 of 5 pass, all at
  112 of 112 world edges) — so 98.2–100 % is superseded upward to 100 % and the capacity account
  survives the amendment. Against the amended control arm (0.4821–0.7500) the contrast is no longer
  near-zero-to-full. The measurement sits at the metric's ceiling, so it says nothing about precision
  (the 0.3438 ceiling is untouched) and covers five diagnostic seeds only.
  `docs/GATE13-PAIRED-CAPACITY-TEST.md` §6; artifact `docs/gate13_cap1000_build_comparison.json`.
- **Precision measured at both caps, so the coverage ceiling cannot hide a quality change.** On the
  final asserted set (`covered / asserted`, world vocabulary only): every arm on a later build sits
  between 0.4155 and 0.4746, with amended medians of 0.4576 at cap 20 and 0.4571 at cap 1,000 against
  0.4602 at `e6d1bcc`/cap 20 — flat, while recall rises from 0.4821–0.7500 to 1.0000. So the amendment
  changes which structures are asserted and how many, not how often an asserted edge is real. This
  quantity is not the 0.3438 Layer-1 selection-precision ceiling and is not comparable to it.
  `docs/GATE13-PAIRED-CAPACITY-TEST.md` §7; artifact `docs/gate13_asserted_precision.json`.
- **The capacity curve is swept, and the amendment's effect is a smaller asserted set, not a better
  one.** Caps 1–1,000 on `89b0744`, `e6d1bcc` and the amended engine. Precision is flat across the
  whole curve on both later builds (spans 0.0087 and 0.0118); the recorded build's
  step is a step in asserted-set size (30–40 edges out to cap 50, then 68/128/243),
  where its precision is a measurable zero because nothing world-aligned is asserted. Against
  `e6d1bcc` the amendment lowers recall at every cap below 500 (0.5089 against 0.7143 at cap 1, 0.5357 against
  0.7768 at cap 20) on a smaller asserted set (129 against 173 edges) with precision unchanged — so the
  carried-forward copies included world edges, and the amendment is a scoring correction, not a
  coverage gain. Against `89b0744` it is still a large gain at small caps (0.0000 to 0.5089 at
  cap 1). New artifact `docs/gate13_cap_curve_by_build.json` and figure `docs/figure_gate13_capacity_curve_by_build.svg`; the Measured as difference ratios rather than as medians, the edges the cap adds are asserted at nearly the initial set's hit rate (marginal precision 0.4483 against 0.4651 on the amended engine; 0.4600 against 0.4591 at `e6d1bcc`), and the 190 edges the amendment drops at cap 1 include 87 world edges (pooled 0.4579 against 0.4651 retained) — it removes a sample of edges, not a sample of noise. `docs/GATE13-PAIRED-CAPACITY-TEST.md` §8.3. The population it ranks is 240 vocabulary rows containing all 112 world edges (base rate 0.4667); 192 of 240 rows tie at count 10, and against a random draw of the same size the asserted set is at chance, so the plateau is the pool's composition and the constraint is rankability. `docs/GATE13-PAIRED-CAPACITY-TEST.md` §8.4. Of six computable orderings only the stored `ratio` beats that base rate at top-20 (0.5000–0.6000, 1.47 SE, directional) and breaks the count tie; the engine's raw-count admission rule is -5.35 SE below chance. §8.5; `docs/gate13_tiebreak_tests.json`.
- **Pre-registered, not authorised: the `ratio` admission arm.** `docs/GATE13-RATIO-ADMISSION-PREREGISTRATION.md` freezes arms, metrics M1–M5, seeds, predictions P1–P4 and the outcome table before any cell runs; no engine file is touched and no cell has run.
  measurement document gains §8. The committed seed-keyed sweep `docs/gate13_capacity_sweep.json` is untouched.

### Fixed — Candidate supersession (2026-11-06)

- **`_load_prior_candidates` returns one live copy per identity.** The sleep rows are a
  history — every surviving candidate is re-written each cycle — and the old reader
  returned every copy, so the selector's maximum-value rule always picked the oldest
  generation and Law VI decay could never be seen. The newest copy per id now supersedes
  its predecessors (`organica/sleep_selection.py`).
- **A prune writes a death record.** Natural selection stores a `retired: true` record with
  the same id when a candidate falls below `DEATH_THRESHOLD`, so a pruned candidate stops
  being loaded instead of being reloaded and re-decayed forever. Re-extraction still
  supersedes the tombstone.
- **Disclosed, not fixed:** the frozen `organica/sleep.py` re-admits stable G2/G3 priors
  into the current cycle before selection, so those structures are reinforced every cycle
  and still never decay. G1 candidates (concepts, phrases, loops, predictions) now do.
  Decision `docs/DECISION-CANDIDATE-SUPERSESSION.md`; probe
  `docs/candidate_supersession_probe.json`; manual §8.24.

### Measured — the `ratio` admission arm: ordering, not capacity, is binding (2026-11-06)

- The pre-registered arm ran 55 cells (three conditions, five diagnostic seeds, caps 10/20/100/1,000,
  `PYTHONHASHSEED=0`). **P1, P2, P3 and P4 all pass**: at cap 20 the stored-`ratio` ordering beats the count
  control's coverage on every seed (+0.0536 to +0.0804) while paired precision moves by
  -0.0031 to 0.0313, and the largest tie falls from 0.8625 to
  0.1375 of the pool.
- Registered reading: admission is a binding constraint and capacity is downstream. Marginal precision runs
  *lower* for the ratio arm (0.4444 against 0.4627 from cap 20 to
  1,000) because it front-loads the pool; the saturated endpoint is identical.
- Two corrections recorded: §8.4–§8.5's "the admission rule sorts by count" is the harness's rule, not the
  engine's (`_build_predictions` sorts by target entropy first, then transition probability, then count) — the
  engine's own rule at cap 100 is worse than count on both metrics; and seven treatment cells that reproduced
  the control exactly were discarded as an ineffective instrument before any result was read.
- No engine file, threshold, seed or prior claim changed. `docs/GATE13-PAIRED-CAPACITY-TEST.md` §8.6,
  `docs/GATE13-RATIO-ADMISSION-PREREGISTRATION.md` Amendment 2, `docs/gate13_ratio_arm.json`.

### Proposed — confirmatory pre-registration for the `ratio` arm, with one open decision (2026-11-06)

- `docs/GATE13-RATIO-CONFIRMATORY-PREREGISTRATION.md` fixes the arm exactly as run: 275 cells
  (C/R at caps 10/20/100/1,000, E at 20/100/1,000), 25 seeds, `PYTHONHASHSEED=0`, and a liveness control that
  voids the block if the treatment stops differing from the control.
- Four predictions with thresholds fixed by the null, not by the development result: the directional count is
  the exact one-sided sign-test threshold (21 of 25, p = 0.00046).
- The requested range 20261106–20261130 is **not fresh**: all 25 seeds are named in 63 committed
  files and it is the acquisition experiment's reserved confirmatory sample. Allocation B
  (20270602–20270626) is verified unused across 440 scanned files and is pre-registered as the
  default; the choice is recorded as the owner's decision.
- Nothing ran, no seed is spent, no engine file changed.

### Recorded — the `ratio` confirmatory block: treatment reproduces, control's chance premise does not (2026-11-06)

- Ran on **allocation B** (20270602–20270626), the 25-seed range with zero occurrences across the 440 files
  scanned, on the owner's ruling. 275 cells, arm unchanged, `PYTHONHASHSEED=0`.
- **Verdict PARTIAL / NOT COMPARABLE** — the frozen table's last row, not a confirmation. C0, C2, C3, C4 pass; **C1 fails**:
  the count-sorted control is below the frozen 0.4667 base rate on 22/25 seeds (median 0.4348),
  so the development block's "count is at chance" reading is seed-dependent rather than a property of the
  ranking. The treatment contrast itself reproduces: coverage up on 24/25 (median +0.0446, exact
  one-sided p = 7.7e-07), tie broken 24/25, precision median +0.0128 and worst -0.0084.
- No engine file, threshold or seed outside the block changed; the not-comparable verdict is reported as the
  pre-registration required rather than re-read as a win. `docs/GATE13-PAIRED-CAPACITY-TEST.md` §8.7.

### Recorded — C1 failed on its own band: structural comparator, under-powered criterion (2026-11-06)

- Diagnostic, **not confirmatory**: 200 seeds (20270701–20270900) on arm C at cap 20 only, through the
  registered `run_cell` imported rather than reimplemented. Artifact `docs/gate13_control_precision_sweep.json`.
- The frozen comparator is exact by construction: 240 pool rows containing 112 world edges on every seed, so
  0.4667 is the pool's composition and not a development-block accident.
- The control is mildly anti-selective rather than at chance: precision mean 0.4449 (CI 0.4397–0.4500), sd 0.0376,
  below base on 71.0% of seeds (offset -0.0218, t -8.2).
- ±0.05 covers 81.5% of seeds, so C1's 21-of-25 bar had a 49.7% chance of passing on a matching population;
  the block's 18/25 is z -1.2 (P = 0.17) and its mean sits at the 32.0th percentile. The §8.7 verdict is unchanged —
  the characterisation sits beside it, per the rule that a verdict and a characterisation are separate artifacts.

### Recorded — C1 re-specified as a calibrated equivalence test (2026-11-06)

- Amendment 1 to `docs/GATE13-RATIO-CONFIRMATORY-PREREGISTRATION.md`: C1 becomes an equivalence test on the
  block mean — pass iff mean cap-20 control precision over 25 seeds is within δ = 0.032 of the structural 0.4667
  (band [0.4347, 0.4987]) — instead of a per-seed ±0.05 band on 21 of 25, which §8.8 showed passes 49.7% of the time
  on a matching population.
- δ is fixed from the 200-seed sweep alone: the smallest 0.001-grid margin with ≥90% bootstrap coverage
  (90.8%; closed form 0.0315), stable at 0.0269–0.0367 under resampling of the calibration data.
- Costs and blind spots are stated in the amendment rather than left implicit: 0.0102 of systematic shortfall is
  absorbed (1.4 se, pass < 50% at a -0.011 shift), and the criterion is blind to dispersion. Prospective only;
  the confirmatory verdict is untouched. `benchmarks/derive_c1_respecification.py`, `docs/gate13_c1_respecification.json`.

### Recorded — block 2: first comparable block, treatment not reproduced (2026-11-06)

- Pre-registered before the first cell on fresh seeds 20270901-20270925 (275 cells, C1′ frozen at δ = 0.032).
- C1′ **passes** for the first time: mean cap-20 control precision 0.4530, -0.0137 from 0.4667, inside
  [0.4347, 0.4987] — the control behaves like the calibrated population, so the treatment comparison is interpretable.
- **C3 fails at 20/25** (exact one-sided p = 0.002, median Δ +0.0535) against the 21-of-25 bar;
  C0 and C2 pass (22/25 at ≥3×), C4 passes thresholds but its median collapses to +0.0003 from +0.0128.
- Verdict **TREATMENT NOT REPRODUCED**, decisive per the owner's authorisation and not re-scored; the nominal p-value is
  reported beside the miss, not in place of it. Cap-1,000 coverage short of the full pool on 4 seeds (disclosed).
  `docs/GATE13-RATIO-BLOCK2-PREREGISTRATION.md`, `docs/gate13_ratio_block2.json`, `benchmarks/score_ratio_block2.py`.

### Analysed — the 20/5 split is not a pool-structure effect (2026-11-06)

- Block 2's five non-improving seeds are indistinguishable from the twenty that improved on every pool property measured:
  tie-block rows (201 vs 202, p =
  0.9016), distinct ratio values (41 vs
  44, p = 0.9674), ratio-to-count distinct ratio
  (3.42 vs 3.64, p =
  0.4518) and control precision (0.4625 vs
  0.4357, p = 0.3582).
- Top-20 density uplift does differ (0.25 vs 0.10, p =
  0.0558) and correlates weakly with the coverage delta (pooled r = 0.362,
  r² = 0.131; block 2 alone 0.297, interval spanning zero) — but
  2 of the five failures still got a denser top-20, and the largest loss (20270921,
  -0.0446) got no uplift at all. A better ranking is necessary-looking and not sufficient.
- The only variable that separates at conventional levels, the ratio arm's asserted-set size (p =
  0.0333), is downstream of the outcome rather than a property of the pool, so it explains nothing.
- Explicitly exploratory: groups defined by the outcome, n = 5 failures, no pre-registered criterion, no verdict re-scored.
  Confirming a moderator needs a fresh allocation and a bar fixed in advance.
  `benchmarks/diagnose_ratio_seed_split.py`, `docs/gate13_ratio_seed_split.json`.

### Analysed — a verified replay finds no admission-side difference in the 20/5 split (2026-11-06)

- The cap-20 cells for the five non-improving seeds and five uplift-matched improving seeds were replayed with every
  per-cycle admission window recorded; **all 20 replays reproduce** the stored asserted set, covered count and
  digest, so the traces are the cells that were scored.
- The ratio window is about 1.7× as often a world edge per cycle as the count window, but it reaches
  26-41 distinct edges against 76-87: it
  trades exploration for repetition (about 4.2× per edge) instead of finding more.
- Failing and improving seeds do not differ on admissions (802.4 vs
  732.4), distinct window edges (30.6 vs
  33.8) or asserted rows (123.0 vs 151.2); the failing seeds
  repeat world edges slightly more and end with fewer covered edges (55.2 vs 70.6).
  The cap is not where the 20/5 difference lives.
- Coverage exceeds window reach in 10 of 10 ratio cells
  (62.9 covered, 41.3 outside any window) against 1 of
  10 for the count arm (60.2, 12.4), because `structure_edges` aggregates all six
  structure types and the window touches only some — a resolution boundary, recorded rather than bridged.
- Exploratory: no pre-registered criterion, no verdict re-scored. The remaining question moves downstream of admission,
  to how repeated assertions are consolidated. `benchmarks/diagnose_assertion_path.py`,
  `benchmarks/analyze_assertion_path.py`, `docs/gate13_assertion_path.json`.

### Analysed — loops carry the coverage, the ratio effect is temporal, and the 20/5 split is redundancy (2026-11-06)

- A store-time observer captured every `event_type="sleep"` payload as written and attributed each covered world edge to
  the structure type(s) asserting it; **all 20 cells verify** against the stored digest, against `structure_edges` on the
  database's own candidate list, and against every per-edge weight.
- `loop_candidate` carries 27-89 of the covered edges and is **identical across arms on all
  10 seeds** (max difference 0) — loops are built from the stream and are not what the cap ranks.
- The whole treatment effect is `prediction_candidate`: 6.2 to
  11.8 in failing seeds, 8.2 to
  13.6 in improving ones. What separates them is redundancy: loop/prediction overlap rises
  1.4 to 8.8 where seeds fail and falls 5.2 to
  3.6 where they improve.
- This closes §8.12's boundary: coverage outside the admission window is loop coverage, and loops are not the object the
  window ranks. Admission is a conditional bottleneck — worth something when the temporal edges it selects are not
  already in the loops.
- Recorded wording defect, not a code change: `structure_edges` documents "six structure types" but has eight branches
  (`concept_candidate` and `phrase_candidate` share one).
- Exploratory, final-set composition rather than time order, no criterion and no verdict re-scored.
  `benchmarks/diagnose_structure_provenance.py`, `docs/gate13_structure_provenance.json`.

### Pre-registered — loop-redundancy moderator block (frozen, unrun) (2026-11-06)

- Block 3 freezes the §8.13 mechanism as a prediction about *which seeds* the ratio arm should help: pre-treatment loop
  coverage of the world (`r_s`, the share of the world's edges the control's loop candidates already assert) should predict
  the gain. Seeds 20271101-20271200 (100 seeds, zero occurrences in the tree; 20271001 onward rejected for
  2 pre-existing hits), C and R at cap 20, 200 cells, nothing run.
- Threshold 0.509 and all bars are fixed from the 10 calibration seeds, which the block does not contain. Gates: arm
  liveness, C1′ comparability, and loop invariance across arms (a failed gate voids rather than negatives the block).
- Power is published **before** the data: 0.327 joint for M1 and M2 against a mechanism-sized moderator,
  0.002 at no association. The decision table therefore reads a pass as strong evidence and a miss as weak
  evidence against the mechanism — and the document says so in those words.
- Disclosed honestly: on the 10 calibration seeds the covariate's association is **+0.22**, the wrong sign
  for the mechanism. The block tests the proxy against that hint rather than with it.
- `benchmarks/run_redundancy_block.py` self-tested on the excluded seed 20270901 and reproduces block 2's asserted sets,
  coverages and digests for both arms before the freeze.
- `docs/GATE13-RATIO-REDUNDANCY-PREREGISTRATION.md`, `benchmarks/run_redundancy_block.py`,
  `benchmarks/calibrate_redundancy_moderator.py`, `docs/gate13_redundancy_moderator_calibration.json`.

### Gate 13 block 3 run (2026-11-06) — redundancy moderator retired

- **Scored once, exactly as pre-registered.** 200 cells on the first unused 100-seed run (20271101-20271200), C and R
  at cap 20, bars and threshold (0.509) fixed before the first cell, `loop_hash` recorded under Amendment 1
  so G2 could compare loop attribution across arms rather than by count.
- **Gates held.** Arms differed on 100/100 seeds, mean control precision 0.4444 sat
  inside the C1′ band [0.4347, 0.4987], loop edge sets were identical on
  100/100 seeds.
- **Verdict: MODERATOR NOT SUPPORTED.** M3 passed — 88/100 seeds gain, mean 0.0442 coverage — so the effect
  replicates for the third time, but M1 failed in the registered direction (0.0357 low vs
  0.0536 high redundancy, bar +0.03) and M2 failed (Spearman -0.02,
  CI [-0.243, 0.185], bar -0.25 outside it). Pre-run loop redundancy is not the moderator, and the
  20/5 split is open again to a different covariate; no earlier verdict moved.
- `benchmarks/score_redundancy_block.py`, `benchmarks/write_redundancy_block3_record.py`,
  `docs/gate13_redundancy_block3.json`, §8.14 capacity record, §12-§13 pre-registration.

### Gate 13 block 4 run (2026-11-06) — voided by measurability

- **Pre-registered, run once, voided by its own gate.** Covariate `o_s` = share of the control's world-covered temporal
  edges that its loops already assert (the §8.13 overlap pattern, which block 3's total-loop-count proxy did not test).
  200 cells on fresh seeds 20271202-20271301, threshold 0.3095, bars and power fixed before the first cell.
- **G0 and G1 pass; G2 fails at 87/100 measurable.** The denominator can be absent — the control
  asserted fewer than 3 temporal world edges on 13 seeds — so the share is undefined there and saturated elsewhere
  (0.7191 mean, 78 of 87 above threshold). Excluded rather than imputed, which left
  too few seeds to test the registered split.
- **Verdict VOID / NOT COMPARABLE; no criterion read.** The positive association on measurable seeds (Spearman 0.389, mean gain
  0.0494, 81/87 positive) is recorded as descriptive only, not as support.
- The lesson is about design: a covariate expressed as a share needs its denominator proven non-degenerate before the
  freeze. `benchmarks/run_temporal_redundancy_block.py`, `benchmarks/score_temporal_redundancy_block.py`,
  `docs/gate13_temporal_redundancy_block4.json`, §8.15 capacity record, §12 pre-registration.

### Gate 13 block 5 run (2026-11-06) — the repaired covariate gets a verdict

- **The block-4 covariate, specified properly.** `o_s` = share of the control's world-covered temporal edges its loops
  already assert, with the measurability floor lowered from 3 to 1 and the cut chosen by a balance rule over 110
  non-judged cells rather than the median of ten seeds. Cut 0.75, calibration halves 53/56, fresh seeds 20271403-20271502,
  200 cells, pre-registered with a new G3 gate that block 4 needed and lacked.
- **Gates: all four pass.** G2 measures 99/100 defined at
  floor 1, against 87/100 at floor 3; G3 splits 42/57, against 9/78.
- **Verdict DIRECTIONAL ONLY.** M2 Spearman 0.407 (CI [0.219, 0.576], bar 0.25); M1 +0.0268 on
  42/57 (bar 0.03); M3 88/99. M1's low power
  (0.283 at the calibrated effect) is published in §8 of the
  pre-registration, not discovered after the fact.
- **A rejected candidate, on the record.** The count `|L ∩ P ∩ W|` — §8.15's recommendation — is always defined but
  associates at 0.241 with an expected half-split gap of 0.015, so it was rejected at calibration rather than frozen into
  a null.
- `benchmarks/calibrate_temporal_redundancy_b5.py`, `benchmarks/write_temporal_redundancy_b5_prereg.py`,
  `benchmarks/score_temporal_redundancy_b5.py`, `docs/gate13_temporal_redundancy_block5.json`, §8.16 capacity record.

### Gate 13 block 6 run (2026-11-06) — the moderator question becomes an intervention

- **The arm §10 named, run once.** Y is R at the same construction, cap, world and readout, with one extra admission
  step: a candidate whose edge a loop asserts that cycle sorts after one that no loop asserts. 300 cells,
  seeds 20271614-20271713, arms C, R, Y.
- **Dose finding, before the freeze.** Reordering (X) and reserving the cap (Y) produced identical effects on all ten
  calibration seeds — with ≥20 non-loop candidates the two are the same function — so the block tested the strongest
  form of the preference, not a weak one.
- **Criterion chosen from the calibration, disclosed.** The effect is zero on half the seeds and 0.027–0.063 on the
  rest, so median and sign criteria were near-blind (~3% power); the primary criterion is the paired mean, bar 0.01
  (one fifth of R's gain over C), sitting 2.46 standard errors below the calibrated mean with 0.997
  power.
- **Gates: G0 failed.** G0 62/100 Y≠R, G0b
  100/100 C≠R, G1 0.4441 in band, G2 100/100
  displaced.
- **Verdict VOID / NOT COMPARABLE.** Mean Y − R 0.0095 (CI [0.00679, 0.0124]), median 0.0000,
  43/100 positive; M2 novel +1.0 (CI [0.75, 1.36]), loop-covered change
  +0.02. Coverage over C: 0.0481 (R) → 0.0576 (Y).
- `benchmarks/run_loop_free_admission_block.py`, `benchmarks/score_loop_free_block6.py`,
  `docs/gate13_loop_free_block6.json`, §8.17 capacity record.

### Gate 13 block 7 run (2026-11-06) — the same arm, a gate that can fire

- **Only G0 changed.** Block 6's void was a bar its own calibration could not reach (96/100 against a 6/10 rate); block
  7 sets G0 to 50/100, calibrated to the pooled liveness 0.6182 over 110 non-judged pairs,
  and keeps the arm, world, cap, readout, C1′ band, G2, M1's 0.01 bar and M2 unchanged.
- **300 cells on fresh seeds 20271715-20271814.** G0 72/100, G0b
  100/100, G1 0.4427 in band, G2 100/100:
  all pass.
- **Verdict INTERVENTION SUPPORTED.** Mean Y − R 0.0127 (CI [0.0092, 0.01652]); M2 novel +1.4 (CI [0.98, 1.8]).
  M1's low power was pre-registered (pooled mean 0.0100 against the 0.01 bar) rather than
  discovered after the fact.
- `benchmarks/score_loop_free_block7.py`, `docs/gate13_loop_free_block7.json`, §8.18 capacity record.

### Gate 13 block 8 run (2026-11-06) — does the gain scale with the cap?

- **Arms R and Y at caps 40 and 100**, 100 fresh seeds (20271826-20271925), 400 cells.
  The runner gained a `--caps` option; the cap-20 self-test and a replayed cap-20 cell were checked to be identical to
  block 7 before the run.
- **Gates:** G0 liveness 86/100 and 100/100 (bar 50), G1 perturbation 100/100 and 100/100 (bar 96), G2 axis live
  0.0942 (0.0867, 0.1023): all pass.
- **Verdict SCALING SUPPORTED.** M1 mean DiD 0.0240 (0.0196, 0.0285) against
  0.0100; M2 positive at both caps: cap 40: 0.0179 (interval 0.0144 to 0.0218), cap 100: 0.0420 (interval 0.0369 to 0.0472).
- **Disclosed launcher defect:** the run also executed arm C, which the design excludes. Those cells are unregistered and unjudged, kept apart, and the scored grid is exactly the 400 registered R/Y cells.
- `benchmarks/score_loop_free_cap.py`, `docs/gate13_loop_free_cap.json`, §8.19 capacity record.

### Changed — Organica engine development on master (2026-11-04)

### Added — Relational Schema Layer & Role Abstraction (2026-11-04 / 2026-11-05)

- **Layer 2b: Evidence-Derived Structural Roles (`RoleCandidate`)**:
  - Introduced `RoleCandidate` (Generation 2) encapsulating empirical topological
    properties (internal cohesion density, out-degree, in-degree, retention, directional flow bias).
  - Hub-aware community discovery filters high-degree bridge nodes (degree >= 5) so true
    functional clusters separate cleanly into distinct structural roles.
- **Layer 3b: Relational Schemas (`SchemaCandidate`)**:
  - Introduced `SchemaCandidate` (Generation 3) representing invariant transition
    patterns across structural roles (`Role_0 -> Role_1`).
  - Transition contingency gating evaluates event-level sequence transitions
    ($P(	ext{target} \mid 	ext{source}) / P(	ext{source} \mid 	ext{source}) \ge 2.0$)
    and directional flow asymmetry, establishing content-sensitive role satisfaction.
  - RS0 Orthogonal Rejection Gate verified: flat random noise worlds ($p=0.50$) fail
    contingency criteria and form zero schemas, eliminating spurious top-down priming.
- **Top-Down Structural Candidate Priming**:
  - `SleepService._build_predictions` uses stable prior schemas to provide effective count
    boosts for embryonic cross-cluster transitions in new contexts, accelerating acquisition
    without waiting for high bottom-up observation volume (`PREDICTION_MIN_COUNT = 5`).
  - Lineage grounding: primed predictions carry direct `parent_ids` linking to guiding schemas
    and empirical source events.
- **Cross-Context Structural Reuse Experiment (CCRE)**:
  - The v1 five-seed run's `REUSE_DEMONSTRATED` label is **withdrawn**. Its speedup came from a
    confidence-derived boost that pushed a one-transition edge past `PREDICTION_MIN_COUNT`, and
    its schema identity ignored the role exemplars, so the orthogonal Context C produced the same
    schema id as Context A and the two arms matched on four of five seeds — persistence included.
    The v1 artifact is preserved unmodified as the record of that measurement.

### Changed — Earned-evidence acquisition and content-sensitive schema priming (2026-11-05)

- `_build_predictions` no longer inflates a prediction's count from a prior: an edge is admitted
  iff `temporal_count >= PREDICTION_MIN_COUNT`. A schema prior now only **reorders** admissible
  candidates (`evidence["schema_prior"]`) and only when its stored sender/receiver polarity agrees
  with the edge's own flow polarity (`role_polarity_match`).
- Schema identity is content-bearing: `_make_id` includes the role exemplars and the
  natural-selection key is `schema:<source exemplars>-><target exemplars>`, so two contexts can no
  longer collapse to one schema (which also made per-context decay impossible).
- The CCRE harness scores arrival on unboosted evidence, asserts on every cycle that no prediction
  reports an unaudited count, and records `primed_predictions` and the target edge's rank at
  acquisition.
- Earned-evidence five-seed rerun: all four arms within 3.4–3.6 cycles, verdict
  `STRUCTURAL_PRIOR_PRESENT_NO_ACQUISITION_ADVANTAGE`. Records:
  `docs/CROSS-CONTEXT-REUSE-EARNED-RESULTS.md`, `docs/DECISION-EARNED-SCHEMA-PRIMING.md`.


- **Unfrozen for Direct Engine Development**: With the measurement reasons
  for the historical freeze fulfilled and documented, active development of
  Organica proceeds directly in `organica/` on master.
- **Fixed Lookback Contamination (D2)**: `MemoryService._record_temporal_edges`
  now strictly filters on `event_type != 'sleep'` when constructing lookback
  windows. Internal sleep reflections can no longer pollute the precedence matrix.
- **Cognitive & Substrate Determinism**:
  - `MemoryService.temporal_edges` now applies canonical secondary ordering
    `ORDER BY count DESC, tag_from ASC, tag_to ASC`.
  - `MemoryService.recent` includes `rowid DESC` tie-breaking.
  - Candidate builders (`_score_tags`, `_build_predictions`, `_build_loops`,
    `_build_anomalies`, `_compose_meta_concepts`, `_compose_processes`) iterate
    and sort collections deterministically, eliminating hash-seed jitter across
    subprocesses.
- **Relation-Family Stratification & Transition Predictive Information Ranking**:
  - `SleepService._build_predictions` partitions candidates into co-occurrence
    pairs versus true temporal transitions using the co-occurrence graph (`cooc`).
  - True transitions are ranked by predictive information (conditional transition
    probability $P(\text{target} \mid \text{source}) = \text{count} / \sum \text{counts}(\text{source} \to \cdot)$),
    prioritizing structural transitions over intra-cell co-occurrences.
  - Stratified allocation reserves 50% of the candidate prediction budget
    specifically for transitions.
- **Architectural Generation Index Alignment (Defect D4)**:
  - Aligned candidate generation fields across `SleepService` to strictly match
    the canonical layering in `docs/architecture.md`: G2 (meta-concepts,
    processes), G3 (workflows), G4 (hypotheses), G5 (theories, questions),
    G6 (dreams), G7 (investigations), and G8 (experiments). Fixed 1-off generation
    offsets throughout candidate synthesis.
- **Layer 1 Event Grounding (Defect D3)**:
  - `SleepService.run()` builds a `tag_events` index from the recent empirical
    observation window, populated into `self._current_tag_events`.
  - `_build_concepts`, `_build_phrases`, `_build_loops`, and `_build_predictions`
    all now populate `parent_ids` with the supporting empirical event UUIDs,
    completing the unbroken causal audit trail from G0 through G8.
- **Conditional Entropy Predictive Ranking**:
  - `_build_predictions` computes `H(T|source) = -sum P(v|u) log P(v|u)` for
    each transition source. Low-entropy (deterministic) transitions rank first;
    diffuse co-occurrences rank last. `target_entropy` stored in evidence dict.
- **Experiment Execution Hook (Law IV)**:
  - `SleepService.execute_experiments()` evaluates proposed experiments against
    `memory.recent(50, event_type="observe")` by matching subject tag and
    expected outcomes. Outcomes (`"validated"` / `"refuted"`) are persisted as
    `experiment_result` events in MemoryService.
- **Concept Clustering Threshold Re-tuning**:
  - `CONCEPT_MAX_CLUSTERING = 1.0` (from `0.4`) so tightly-bound cliques in
    dense co-occurrence environments form valid concept candidates.
- **Law V EIG Formula Correction**:
  - Dream investigations now use the canonical `EIG = uncertainty * (1.0 + novelty)`,
    matching the formula applied to question investigations. Fixes a silent
    inversion that systematically under-ranked high-novelty dream paths (Fact AD5).
- **Universal Natural Selection Decay — G2–G8 (Fact AA21)**:
  - `_candidate_key` extended to return content-identity keys for all candidate
    types: meta_concept, process, workflow, hypothesis, theory, question, dream,
    investigation, and experiment.
  - `_natural_selection` accepts optional G2–G8 candidate lists and builds the
    full current-key set across all generations. A second decay pass runs after
    all composite layers are formed, so higher-order structures age and are pruned
    when no longer regenerated — matching biological memory at all cognitive levels.
- **Experiment Validation → Hypothesis Promotion Loop (Law IV completion)**:
  - `execute_experiments` increments `support_count` / `contradiction_count` on
    matching hypotheses after validation / refutation, closing the
    predict→test→update loop.
  - Validated dream experiments promote the dream into a new grounded G4
    `HypothesisCandidate` with parent lineage to both the source dream and the
    experiment.
- **Temporal Precedence Edge Decay (World-Adaptation)**:
  - `MemoryService.decay_temporal_edges(factor, min_count)` applies exponential
    moving-average decay to all `precedes` edge counts each sleep cycle.
  - `SleepService.TEMPORAL_DECAY_FACTOR = 0.95` (5% per cycle). Early-regime
    transitional counts fade over ~20 cycles, enabling regime shifts and transfer.
  - `ObservingMemoryService.decay_temporal_edges` is a no-op in the audit probe,
    preserving the A7 invariant (`attributed == count`). `run_invariance` uses a
    `NoDecayMemoryService` for both branches so A4 compares observer presence only.
- **Capacity Bottleneck Relieved (P1 / FACTS-SHEET D3)**:
  - `MAX_PREDICTIONS` raised from 20 to 40. Relieves the severe over-truncation
    at Layer 1 identified in the instrumentation audit, un-starving downstream
    process, workflow, and belief formation.
- **Structural Entropy Ranking for Loops & Anomalies (P2, P4)**:
  - `_build_loops` computes path minimum target entropy $H(T \mid \text{source})$
    and sorts deterministic, low-entropy cycles ahead of diffuse transitions.
  - `_build_anomalies` ranks anomalies with low context target entropy first,
    filtering out background noise in diffuse graphs.
- **Loop Rotation Normalization (P7)**:
  - Directed 3-cycles are canonicalized to their lexicographically minimal
    rotation, guaranteeing that cycle permutations do not produce divergent candidate
    IDs or cause artificial natural-selection decay.
- **M3 Contradiction Density Added to SleepReport (P3 / FACTS-SHEET G3)**:
  - Added `contradiction_density` metric to `SleepReport`, exposing real evidence
    accumulation and tension flow independently of static population counts.
- **Question Closure on Experiment Validation (P5 / Law IV)**:
  - `execute_experiments` marks validated questions as closed and records their
    resolving experiment; `_form_theories_and_questions` and `_rank_investigations`
    skip closed questions to focus curiosity on open questions.
- **Architectural Performance & Database Optimization (13× Speedup)**:
  - `MemoryService`: Enabled SQLite WAL mode (`PRAGMA journal_mode = WAL`),
    `synchronous = NORMAL`, in-memory temporary storage, and a 64MB cache.
  - Replaced individual row inserts in `_record_cooccurrences` and `_record_temporal_edges`
    with `collections.Counter` aggregation and `executemany` batch execution,
    slashing Python-SQLite roundtrip overhead.
  - Refactored `SleepService._natural_selection` to run as a single unified pass
    across all generations ($G_1–G_8$) within one transaction, eliminating the
    double-decay bug and redundant SQLite candidate writes.
  - Added cycle-scoped prior candidate caching (`_prior_cache`) in `SleepService`,
    eliminating redundant JSON deserialization of up to 4,000 candidates across
    hypotheses, queries, and experiments.
  - Batched experiment execution and hoisted observation and prior candidate queries
    outside the evaluation loop in `execute_experiments`.
  - Result: 38-test integration suite execution time dropped from ~70s to 5.2s
    (>13× speedup) while preserving 100% architectural and substrate equivalence.
- **Active Environment Execution & Law IV Empirical Dispatcher (Option B)**:
  - `organica/environment.py` orchestrates the perceive -> consolidate -> intervene cycle
    via `ActiveInquiryLoop` and `ReactiveWorld`.
  - Head-to-head empirical benchmark (`benchmarks/active_inquiry_benchmark.py` over 150 cycles)
    demonstrated a **+120.9% cumulative structure inventory expansion** (129 -> 285)
    with 735 interventions executed, confirming that active intervention unlocks higher cognitive
    layers (theories and questions emerge from interventions) beyond passive observation limits.
- **Hypothesis Retention Pressure Audit (Gate G-P1)**:
  - `benchmarks/retention_pressure_audit.py` evaluated belief pool dynamics over 300 cycles across
    `confidence`, `contradiction`, and `shannon_entropy` retention policies; determined mean
    pre-cap belief pool is 3.82 (max 13), demonstrating that `MAX_HYPOTHESES = 15` is non-binding
    under natural passive observation.
- **Shannon-Entropy Hypothesis Retention**:
  - Added `"shannon_entropy"` to `VALID_RETENTION_POLICIES` and `_retain_hypotheses` in `SleepService`,
    prioritizing hypotheses with maximal outgoing temporal flow uncertainty to maximize pool epistemic diversity.
- **Semantic Tag Sanitization**:
  - `MemoryService._extract_tags` strips hex UUID strings before token extraction, preventing
    random hex substrings (e.g. `ebef`, `fade`) from polluting the organism's tag vocabulary
    and eliminating cross-run fingerprint jitter.

---

## [0.11.0] — (unreleased; superseded by 0.12.0)

### Recorded — the deposit package is decided, bundled, and not deposited (2026-10-31)

- **The owner's direction:** *"do not deposit yet; use your best judgement on
  the rest"*. So every decision the deposit checklist left open is now made,
  and **nothing has been uploaded**. Publishing is still the owner's action
  alone.
- **The papers' licence: CC-BY-4.0.** Zenodo's default for a textual work and
  the expected licence for a preprint. The engine stays Apache-2.0.
- **The route: manual deposit** through the Zenodo web form. Two facts were
  verified live and both bear on it: the repository has **zero webhooks**, so
  Zenodo's GitHub app is **not authorised** and nothing would be minted
  automatically; and there is **no v0.10.0 GitHub release** —
  `gh release list` shows releases only for v0.6.0 to v0.9.0. Standing the
  app up would create an automatic minting pipeline nobody asked for.
- **No GitHub release is cut for v0.10.0.** It is the owner's act and one
  step from publishing.
- **The order: the papers first**, so their DOIs exist before the software
  record links to them.
- **The bundles are built.** `benchmarks/deposit_bundle.py` writes
  `.scratch/deposit/`: the source tree at `v0.10.0` as one archive for the
  software record, and for each paper the manuscript as PDF and Markdown with
  its figures as vector PDF — each with `SHA256SUMS` and a
  `DEPOSIT-MANIFEST.json`.
- **The file list is checked against the manuscripts.**
  `benchmarks/deposit_bundle.py --check` parses both manuscripts for the
  `docs/` artifacts they name and asks whether each is inside the tree the
  software record carries: **36 cited, 36 present.** A manuscript cannot cite
  evidence the deposit does not carry.
- **Still the owner's:** publish, and update the ORCID record's GitHub URL
  (`github.com/nuerainc` → `github.com/nueraresearch`). Nothing in this
  repository can change an ORCID record.
- **Added** — `benchmarks/deposit_bundle.py`,
  `tests/test_deposit_bundle.py`; `docs/ZENODO-DEPOSIT.md` rewritten with the
  decisions, the verified states, the file lists and the reduced checklist.


### Recorded — the project's objective, in the README (2026-10-31)

- **What changed.** The README now carries a **What this project is for**
  section above the architecture it describes. It states the objective
  plainly: **explainable AI, in three layers — decisions, knowledge,
  cognition** — and it says what that means in testable terms. A decision is
  a recorded object, not a summary of one. A belief carries a lineage back to
  the evidence that produced it, and the lineage is checkable rather than
  asserted. A change in the mind is a difference you can point to in the
  record, not a claim about what "learned".
- **What did not change.** The headline stays. "A Developmental Machine
  Intelligence" names the architecture the papers are about and the name is
  load-bearing. What changes is that the section above it now says the
  architecture is **the bet, not the claim**, and that the repository makes
  **no general-intelligence claim** — an outside reader had taken the
  headline for one.
- **The wording is the project's own.** It is re-voiced in the register the
  repository already uses. The objective is the owner's; the phrasing here is
  this project's, and it cites no borrowed text.
- **`CITATION.cff` loses a keyword.** `artificial general intelligence` was
  asserted there as a search term for a claim this repository does not make.
  It is replaced by `explainable ai`, which is what the project is for.

### Corrected — both divergence instruments read the audit's cycle base one cycle early (2026-11-01)

- **What was wrong.** `candidate_membership_audit.first_divergence()` sets
  `first_cycle = index` over `c_cycle_digests`, a **zero-based** list. Both
  instruments that consume it number cycles from one, and both, as first
  shipped, read that index as a cycle. `benchmarks/divergence_cycle_capture.py`
  (2026-10-31) therefore captured the window one cycle **before** the
  divergence and labelled it with the divergence cycle's number;
  `benchmarks/divergence_mechanism.py` (2026-11-01) inherited the same base and
  reported a "+1 systematic offset" between the instruments.
- **The field that could not be false.** `admitted_same_at_divergence` read
  `admitted[cycle - 1]` — the cycle the audit *defines* as the divergence — so
  it was true on every seed by construction. Deleted, and replaced by
  `audit_cycle_reproduced`, which compares the fresh capture's one-based
  first-difference cycle with `index + 1` and can return `False`.
- **What changed in the record.** The mechanism report and journal §74 now
  state **reproduction** of the audit's cycle on 8 of 8 seeds — analytical
  reproduction, not independent replication — and **no delay** between
  construction order and admission is claimed in either direction. Journal §74
  keeps the false claim, why it was wrong, how the correction was derived and
  what remains.
- **The capture re-measured.** `OBSERVER_VERSION` 2 → 3 (the cache keys on that
  field alone), windows read at `(index + 1, index)` instead of
  `(index, index - 1)`, so the report now covers the cycle before the
  divergence cycle and the cycle before it, and the transition between them. A window the capture refuses is
  reported as **not measured**, never as an empty pool: `pool_identity` returns
  `None` and the table says so, where the old code would have compared two
  empty lists and printed "identical".
- **The measurement changed the finding, not only the label.** At the divergence
  cycle the two sides hold the **same set** of candidate IDs in **0 of 16**
  arm-pairs and the **same order** in **0 of 16**: membership differs
  everywhere. The 2026-10-31 table (11 of 16 the same set; 3 seeds identical in
  set *and* order while the admitted stream differed) is what the **preceding**
  cycle shows, so journal §72's order-only reading and §73's premise that the
  difference arose *inside* the cycle are withdrawn. The renderer was repaired
  in the same pass: its zero-identical-pairs branch printed an empty seed list
  and still attributed the divergence to identical pools, and its provenance
  line printed the parent process's counters (0 runs, 16 parts current) as the
  work done.
- **Nothing else moved.** No engine file was touched (`git diff -- organica/`
  is empty), the 36 mechanism parts were reused (0 new runs), C1, H2, Arm B and
  the frozen engine keep their previous status, and no verdict, criterion or
  pre-registered hypothesis was re-read.

### Measured — the membership onset, and a control that could not fire (2026-11-01)

- **What ran.** The experiment pre-registered in `docs/ONSET-INSTRUMENT-BRIEF.md`
  and journal §75: `benchmarks/divergence_onset.py` captures cycles `1…k` per arm
  with the corrected capture's worker and its marker-witnessed addressing rule,
  and reports the first cycle at which the two candidate pools differ in
  membership. **18 runs, 0 cached. No engine file changed.**
- **What it found.** Every one of the 16 located onsets is an **insertion**:
  zero candidates left a pool at the cycle it first differed, and the pools
  diverge by gaining candidates (70, 47, 62 at the T1 transitions; 2–32 across
  T2). Onsets are at cycles 3–6. Four of the five search arm-pairs reach onset
  strictly before `k-1` — T1/20261125 at cycle 3 against `k` = 12, T2/20261120
  at cycle 4 against `k` = 6 — and the fifth at `k-1` itself, so P2's "at least
  4 of 5" holds while its blanket "strictly before" does not. P3 is met.
- **F1 passed.** Cycles `k` and `k-1` reproduce the corrected capture's
  `set_identical` values and pool IDs on **16 of 16** arm-pairs.
- **C1 is void, and that is a defect in the protocol as executed.** The audit
  records the control seed's campaign and baseline hash seeds as **0 and 0**, so
  the two control runs are one configuration: the comparison is a run against
  itself, cannot fail, and returned "identical in 24 of 24 cycles" as it must.
  **F2 is not adjudicated** and the onsets are a characterisation, not yet a
  divergence-specific result. The report now says so instead of claiming the
  gauge holds.
- **The control was then re-run at seeds 0 and 1, and it fired against the
  result.** 2 runs, 0 cached, with the pair declared before the run. The control
  seed's own pools **differ** — 3 of 24 measured cycles, arm B, cycles 10–12 — so
  **F2 fires and the instrument is inadmissible by its own pre-registration**:
  the onsets and the insertion observation are facts about pools under two hash
  seeds, and may not be attributed to the D0 divergence. The residual difference
  in pattern (control at 10–12 on one arm, failing seeds at 3–6 on both) is
  recorded as a hypothesis for a new pre-registration and was not used to rescue
  the result.

### Measured — the construction-order experiment, and a control that stopped it (2026-11-01)

- **What ran.** Arm A (observational) and Arm B (interventional) of the experiment
  pre-registered in `docs/DIVERGENCE-MECHANISM-BRIEF.md` and journal §73, on the
  eight failing seeds plus the control seed, at each seed's campaign-side and
  pinned-baseline hash seeds. **No engine file was modified**: the observer and
  the intervention are subclasses in `benchmarks/divergence_mechanism.py`.
- **Arm A.** The first builder whose assembled sequence differs between hash
  seeds is `_score_tags`, at **cycle 1**, on **8 of 8** seeds — and on the
  control too. That is set iteration order, not the divergence site.
- **The divergence.** The admitted prediction streams first differ at the
  membership audit's divergence cycle **+1** on 8 of 8 seeds, so the two
  instruments' cycle numbering is one apart.
- **Arm B.** P3 **not met** (0 of 8 seeds became hash-seed invariant), **F1
  fired**, and **F2 fired** — the canonicalisation changed the control seed's
  builder sequences at a fixed hash seed. By the pre-registration F2 takes
  precedence, so **no conclusion may be drawn from Arm B** and H2 remains
  untested in an admissible form. The cause is identified: the intervention
  canonicalised the temporal graph and the composites, while the first order
  channel is `_score_tags`, upstream of both.
- **C1 failed, and that is now stated where it was reported as held.** The brief's control required the control seed's *assembled lists* to be identical at every hash seed (P2); the artifact records `P2.met: false`. The admitted stream is identical across hash seeds, which the report had named C1 and called its sharpest positive result; that is a different quantity, read after the criterion failed, and it is now recorded as a post-hoc observation on one seed. No measurement changed.
- **Added** — `benchmarks/divergence_mechanism.py`, `docs/divergence_mechanism.json`
  (36 parts with checksums), `docs/DIVERGENCE-MECHANISM-RESULTS.md`, journal §74,
  manual finding 44.

### Corrected — the release guard compared a tag object to a commit (2026-11-01)

- **What was wrong.** `test_a_released_version_is_checkable` asks the remote
  which commit a release tag names, and it asked with
  `git ls-remote --tags origin v0.10.0`. Against an **annotated** tag that
  query returns **one** line — the tag object — and omits the peeled `^{}`
  line, so the parser could only ever return the tag object (`843247b`)
  while the comparison it feeds is against a commit. On a correct release
  the check therefore had a wrong answer available to it in the
  shallow-clone path: two different kinds of object compared to each other.
- **The fix.** The query uses a `*` pattern, which makes git emit both
  lines, and a pure `_parse_tag_refs` prefers the peeled commit and matches
  names exactly, so a prefix neighbour cannot be admitted. Measured on this
  repository on 2026-11-01: the bare form returns one line, the pattern form
  returns two, and `_remote_ref("v0.10.0")` now returns `f3a42a7` — the
  commit — rather than `843247b`, the tag object.
- **Proof it can still fire.** Five tests: peeled preference, a lightweight
  tag, an absent tag beside a prefix neighbour, the bare-query output
  reproduced as the defect it was, and a monkeypatched run in which the tag
  is behind master and the real test body must fail.
- **Also.** `.venv/` is now ignored: a checkout may create one to run the
  tests, and `git add -A` would otherwise stage it.

### Corrected — the release statement named a tag as a release (2026-10-31)

- **What was wrong.** The README said "0.10.0 is the latest release" and
  `CITATION.cff` carried the comment "0.10.0 is NOT yet published; 0.9.0 is
  the latest release". Neither was true: `v0.10.0` **is** tagged and pushed,
  and `v0.10.0` has **no GitHub release page** — `gh release list` shows
  releases only for v0.6.0 to v0.9.0, and v0.9.0 is still the latest
  published one. The two statements disagreed with each other and with the
  repository.
- **What it is now.** The README and `CITATION.cff` say which one they mean:
  **0.10.0 is the latest cut version** — dated, tagged and pushed — and
  **v0.9.0 is the latest published release**, because v0.10.0 has no release
  page yet. `CITATION.cff`'s `date-released` moves from 2026-10-24 to
  2026-10-31, the day the last cut version was tagged.
- **Not done, and deliberately.** Cutting a GitHub release for v0.10.0 is the
  owner's act, and it is one step from publishing, so it was not done here.
  The repository now says the true thing either way.

### Planned — the next instrument, and its pre-registered falsification criteria (2026-10-31)

- **The brief.** `docs/DIVERGENCE-MECHANISM-BRIEF.md` plans the next
  observer in the D0 reproduction line: **at the cycle where the two admitted
  streams first differ, where in the engine's candidate construction do they
  first differ — in which type, in which builder, and is the difference in
  the order, in the membership, or in a candidate's content?**
- **Why now.** The capture established that on three seeds the pool at the
  divergence cycle is identical **in set and in order** and the admitted
  stream still differs — so the difference arose inside the cycle, in a step
  nobody has looked at.
- **What the source shows.** Four order-dependent sites in the construction:
  `_score_tags` iterates a set of strings and stable-sorts on a tying integer
  (`organica/sleep.py:904-920`); the temporal graph is read with `ORDER BY
  count DESC` and no tiebreak over a table with no index on `count`
  (`organica/memory.py:379-385`); `_build_predictions` stable-sorts on
  `temporal_count` alone (`organica/sleep.py:1139-1160`); and
  `_build_anomalies` picks the anomaly's expected tag among equal counts by
  graph order, so that one changes a candidate's **content**
  (`organica/sleep.py:1167`).
- **What does not bind.** The harness overrides the predictions cap only
  (`CAP_A = 20`, `CAP_B = 1_000`), so the `MAX_PREDICTIONS = 20` truncation
  **does not bind** in the campaign's arms. The eight failing seeds are not
  eight seeds whose predictions were cut at twenty.
- **Pre-registered, before any run.** H1 (the divergence enters through
  order-sensitive construction), H2 (canonicalising the order removes it),
  three predictions (P1-P3), three falsification criteria (F1-F3) and four
  controls (C1-C4) are committed in the brief and in journal §73, so that
  they can be checked against what the instrument actually found. A
  refutation is a result.
- **Scope.** No engine file changes, no D0 re-scoring, no V2, no acquisition
  cells, and Organica 1 stays frozen.

### Measured — the candidate pool at the divergence cycle (2026-10-31)

- **Why.** The candidate-membership audit found *where* the campaign's
  candidate population and the current reconstruction's part company — sleep
  cycles 2 to 11, depending on the seed — and named the candidate IDs that
  differ. It could not say *what was in the pool at that cycle*, because the
  engine's 4,000-row sleep window is a snapshot of the read-back near the
  arm's snapshot point, two or three cycles before the end of the run.
- **The instrument.** `benchmarks/divergence_cycle_capture.py` captures the
  window at the divergence cycle itself.
- **The addressing is proved, not assumed.** The engine stores one
  `sleep:meta` event per cycle carrying that cycle's number, and the window
  is read newest-first, so the newest marker in the i-th window read of an arm
  must carry cycle *i*. The instrument refuses to report a window whose
  marker does not say so. **16 of 16** captured window pairs are addressed by
  their own marker.
- **The pool at the divergence cycle.** Across the 16 arm-pairs, the two
  sides hold the **same set** of candidate IDs in **11** and the **same
  order** in only **3**; in **8** the candidates are identical and the
  order is not. The divergence is mostly a difference in the order the
  candidates were read in, not in which candidates existed.
- **Where the order parts company.** The reordering coincides with the
  divergence in **6** of the 16 arm-pairs: the two sides' pools were
  identical in set and order at the cycle before, and identical in set but
  different in order at the divergence cycle.
- **A negative result about the pool, and a localisation.** For **T2 / 20261118, T2 / 20261123, T2 / 20261130** in
  arm C the two sides' pools at the divergence cycle are identical
  candidate-for-candidate *and* in the same sequence, and arm C's admitted
  stream still differs there. For those the divergence cannot be attributed
  to the pool at all; it arose inside the cycle.
- **The engine.** The pool is read back by timestamp with no rowid tiebreak
  (`organica/memory.py:390`) and the candidate list is assembled from sets
  of strings (`organica/sleep.py:1201`, `:1223`) — both hash-seed sensitive.
- **The capture reproduces.** Its sixteen parts were written twice by two
  independent processes at the same hash seeds and compared field by field:
  16 of 16 identical.
- **Two limits, stated.** Where the window had already reached the engine's
  4,000-row cap, the pool is a truncated view of the candidate history rather
  than the whole of it, and the artifact records which. And a pool is the
  **input** to the decision: this names what the organism had in front of it
  when the two populations parted company, and does not decompose the ranking
  that turned that pool into an admitted set.
  - `T1 / 20261125` — divergence cycle **11**; campaign pool 260, current pool 255, 252 on both sides; **8** campaign-only, **3** current-only; same set: **no**, same order: **no**
  - `T1 / 20261128` — divergence cycle **3**; campaign pool 37, current pool 37, 37 on both sides; **0** campaign-only, **0** current-only; same set: **yes**, same order: **no**
  - `T1 / 20261129` — divergence cycle **2**; campaign pool 39, current pool 39, 39 on both sides; **0** campaign-only, **0** current-only; same set: **yes**, same order: **no**
  - `T2 / 20261118` — divergence cycle **5**; campaign pool 8, current pool 8, 8 on both sides; **0** campaign-only, **0** current-only; same set: **yes**, same order: **yes**
  - `T2 / 20261120` — divergence cycle **5**; campaign pool 23, current pool 22, 22 on both sides; **1** campaign-only, **0** current-only; same set: **no**, same order: **no**
  - `T2 / 20261121` — divergence cycle **5**; campaign pool 18, current pool 18, 18 on both sides; **0** campaign-only, **0** current-only; same set: **yes**, same order: **no**
  - `T2 / 20261123` — divergence cycle **5**; campaign pool 4, current pool 4, 4 on both sides; **0** campaign-only, **0** current-only; same set: **yes**, same order: **yes**
  - `T2 / 20261130` — divergence cycle **5**; campaign pool 10, current pool 10, 10 on both sides; **0** campaign-only, **0** current-only; same set: **yes**, same order: **yes**
- **Added** — `benchmarks/divergence_cycle_capture.py`,
  `docs/divergence_cycle_capture.json`,
  `docs/DIVERGENCE-CYCLE-CAPTURE.md`,
  `tests/test_divergence_cycle_capture.py`; manual finding 42 and a
  revision-log row; `docs/FACTS-SHEET.md` AD12; journal §72.


### Fixed — the README described the repository's release state incorrectly (2026-10-31)

The v0.10.0 tag was cut after the README was written, which left three
statements false: that 0.10.0 was "cut on `master` and not yet tagged", that
"0.9.0 is the latest release", and that "0.10.0 has not been published yet.
Its tag is the archival reference for the frozen Organica 1 engine". The last
of those was wrong in a second way: **v0.9.0 is the archival reference for the
frozen engine**, and under v0.10.0 the engine is byte-identical to it apart
from the package version string. The README now says so, and the package
version was 0.11.0 with 0.10.0 as the latest cut release.

### Recorded — the candidate-membership milestone, in the README (2026-10-31)

The use-path reproduction audit returned AUDIT REQUIRED on eight seeds. The
README now says what the candidate-membership audit found, because it is the
most recent substantive result and it is what a reader assessing the
repository's reproducibility needs: the eight failing seeds are a **hash-order
artifact**, not a failure of the code or of the architecture.

## [0.10.0] — 2026-10-31

### Measured — the candidate-membership audit: the eight failing seeds are a hash-order artifact (2026-10-31)

- **The question.** The use-path diagnostic returned AUDIT REQUIRED; D0 failed
  on 18 seed-limbs across eight seeds. The candidate **counts** were known;
  the candidate **identity** was not. This is the identity, per seed.
- **The pivotal unknown, settled.** The campaign artifact carries no candidate
  ID — `docs/formation_utilization.json` records a per-type table of
  `unique_count` and `edge_weight` and nothing else — so the campaign side
  had to be regenerated. The harness is re-run under each `PYTHONHASHSEED`
  and the run whose fingerprint equals the campaign's IS the campaign's
  population.
- **The code is excluded.** `git diff a95305d HEAD -- organica/` is empty: the
  engine is byte-identical to the state the campaign ran against. Every file
  the harness executes was last modified before the campaign ran, and the one
  whose campaign-time state is unpinned — `benchmarks/
  formation_utilization.py`, committed 89 minutes after the campaign finished
  — is closed by measurement: the committed code reproduces the campaign's
  own table exactly once the hash seed is varied.
- **The environment is responsible.** The engine iterates sets of strings and
  CPython randomises string hashing per process unless `PYTHONHASHSEED` is
  pinned. The audit and the diagnostic pinned `PYTHONHASHSEED=0`; the campaign
  ran with `--workers 10`, so each of its ten worker processes carried its own
  hash seed. The campaign's per-type table is reproduced exactly on **8 of
  8** failing seeds by varying only the hash seed; the control seed's
  population is identical at all 16 hash seeds swept.
- **The membership.** **252** candidate IDs are the campaign's and absent from
  the current reconstruction; **288** are the reconstruction's and absent from
  the campaign; **1804** are on both sides. The IDs are named in
  `docs/candidate_membership_audit.json`.
  - `T1 / 20261125` — 254 both, **35** missing, **65** added; first differing cycle **11**
  - `T1 / 20261128` — 234 both, **63** missing, **75** added; first differing cycle **3**
  - `T1 / 20261129` — 231 both, **62** missing, **64** added; first differing cycle **2**
  - `T2 / 20261118` — 227 both, **9** missing, **7** added; first differing cycle **5**
  - `T2 / 20261120` — 215 both, **21** missing, **11** added; first differing cycle **5**
  - `T2 / 20261121` — 210 both, **32** missing, **36** added; first differing cycle **5**
  - `T2 / 20261123` — 212 both, **20** missing, **14** added; first differing cycle **5**
  - `T2 / 20261130` — 221 both, **10** missing, **16** added; first differing cycle **5**
- **The controls.** The baseline at the pinned hash seed reproduces the
  use-path audit's recorded reconstruction on every type of every seed; the
  control seed's population is identical at every hash seed swept, with no
  membership difference at all; and the runs that reproduce the campaign agree
  with one another on the candidate IDs, so the membership is determined by
  the artifact rather than by a guess.
- **A correction to the earlier reading.** One cached run from an earlier sweep
  carried the campaign's per-type table instead of a measurement; recomputed,
  it agrees with the use-path audit's independently recorded reconstruction and
  not with the earlier reading. The rebuilt artifact supersedes the earlier
  one.
- **What this does not do.** It does not re-score D0 and does not change the
  campaign's verdict. It names where the two populations came from.
- **Added** — `benchmarks/candidate_membership_audit.py`,
  `docs/candidate_membership_audit.json`,
  `docs/CANDIDATE-MEMBERSHIP-AUDIT.md`; manual finding 41 and a revision-log
  row; `docs/FACTS-SHEET.md` AD11; journal §71.


### Corrected — the Gate 13 precision ceiling was 0.3438, not 0.3443 (2026-10-31)

- **The artifact.** `docs/gate13_allocation_rule.json` measures precision for
  both allocation rules across three seeds and every budget — **36**
  measurements — and the maximum is **0.3438** (seed `20261101`, global
  rule, `k=160`, coverage **0.4911**). The string `0.3443` occurs in **no**
  Gate 13 artifact.
- **Where the wrong number had spread.** The formation-utilization campaign
  artifact's own A3 blocks (30 units' prose and 30 derived `band_upper`
  values), `benchmarks/formation_utilization.py`'s `PRECISION_CEILING`,
  `benchmarks/formation_utilization_results.py`,
  `benchmarks/figure_papers.py`'s Figure 5 caption,
  `tests/test_formation_utilization.py`, and **fourteen documents**:
  `AGENTS.md`, `CHANGELOG.md`, `docs/USER-MANUAL.md`, `docs/FACTS-SHEET.md`,
  `docs/GATE13-CAUSAL-ACCOUNT.md`, `docs/GATE13-RELATION-SEPARATION.md`,
  `docs/ACQUISITION-ENDPOINT-AUDIT.md`, `docs/ORGANICA-V2-DESIGN-BRIEF.md`,
  `docs/V2-CAPACITY-DESIGN-BRIEF.md`,
  `docs/FORMATION-UTILIZATION-PREREGISTRATION.md`,
  `docs/formation_utilization_results.md`, `docs/formation_utilization_timing.md`,
  `papers/01_developmental_structure_formation.md` and
  `research-journal/phase_g_findings_20261021.md`.
- **No verdict moved.** Audit A3 holds arm B's Layer-1 precision to
  `ceiling ± 0.01`; the highest arm-B Layer-1 precision across all **30**
  T2 campaign units is **0.3394**, below the lower edge under either
  constant. The campaign's verdicts stand unchanged.
- **The obvious repair would have corrupted measurements.** `0.3343` is both
  the derived lower band edge and the *measured* Layer-1 precision of four
  units; six further measurements merely begin with `0.3443` (`0.344397`,
  `0.344345`, `0.344324`, `0.344364`) or `0.3543` (`0.354312`). The result
  artifacts were corrected **by field path**, the originals preserved beside
  them as `docs/formation_utilization_pre_correction.json` and
  `docs/formation_utilization_timing_pre_correction.json` with a
  `correction_note`, and every measurement compared before and after.
  `docs/formation_utilization_timing_pre_amendment.json` and its rendered
  document were left as the historical record they are.
- **Added** — `AGENTS.md` rule 29; manual finding 40 and a revision-log
  row; `docs/FACTS-SHEET.md` AD10; journal §70.
### Corrected — three Phase L adjacent-difference intervals in Paper 01 were stale (2026-10-31)

- **Paper 01's §4.3 quoted three intervals that `docs/phase_l_results.json`
  does not support.** The artifact's n=30 values are `+0.204 [+0.150, +0.261]`
  (DI, 1:1 → 2:1), `+0.502 [+0.441, +0.557]` (DI, 2:1 → 3:1) and
  `−0.039 [−0.061, −0.020]` (PI, 3:1 → 4:1); the manuscript
  quoted `[+0.148, +0.261]`, `[+0.443, +0.559]` and `[−0.059, −0.020]`.
- **The quoted means were already correct, and so is every conclusion.** All
  three steps still exclude zero, and the plateau edges still contain zero.
  The 4:1 → 6:1 DI (`−0.007 [−0.037, +0.022]`) and the 1:4 →
  1:3 PI (`+0.011 [−0.026, +0.044]`) were already right.
- **Why it happened.** The intervals were transcribed by hand from the
  artifact's six-decimal values and rounded inconsistently.
  `tests/test_paper_numbers.py` resolves every interval the manuscripts quote
  back to its artifact entry by parsing the manuscripts' own quoted steps, so
  the next drift fails a test rather than a reader.


### Decided — Phase K H2 remains binding; one bounded Gate 13 diagnostic is authorized (2026-10-30)

Phase K's terminal outcome **H2** ("the search failed; do not design V2") and the Gate 13 causal account had been read as if both were binding on everything, which left the project auditing a defect it had already localized. They scope different things and the decision is now recorded: **H2 binds V2 design** — no architecture redesign, no frozen-file change, no capability claim — and it does **not** bind one **diagnostic** arm, **G13-D**, which removes the two confounds it can remove (**capacity** and **provenance**) on the five seeds already classified diagnostic, in-process, and scored end-to-end against the declared baselines. The readout is held at its calibrated `alpha = 256.0` in both arms; it is a constant, not an intervention. Relation-family separation and a non-frequency ranking are out of scope: building them is design, which D1 forbids. The current 10-cell runner lacks both intervention hooks; a small adapter and dated diagnostic plan are required before execution. See [`docs/DECISION-V2-SCOPE.md`](docs/DECISION-V2-SCOPE.md) and manual decision 14. No preregistration, threshold, verdict, frozen engine, published result, or confirmatory seed is changed.

**Organica 1 is frozen, and Phase L opens as a measurement phase rather than
another benchmark hunt.**

### Corrected — the cold-start table no longer reproduced, and was re-measured (2026-10-30)

- **`docs/cold_start.json` (2026-10-21) no longer reproduces on any engine retrievable from
  this repository.** On `v0.6.0` (2026-10-23), `v0.9.0` and `HEAD`, the `cold_start`
  condition (no seed, 1 event/cycle) reaches **G5 at cycle 10**; the artifact recorded no G5
  for that condition at all.
- **Every alternative explanation was checked and ruled out:** `--cycles`, `events_per_cycle`,
  seededness, the 48-event stream, the benchmark schema (identical key sets), repeated runs
  (**0** structural differences), `PYTHONHASHSEED` (one non-emergence leaf), and the
  interpreter (3.13.15 vs 3.14.7, identical emergence keys). **The freeze is ruled out too:**
  `v0.6.0` predates it and already shows the current profile.
- **The transition cannot be bisected.** The 2026-10-21 → 2026-10-23 commits are not
  published — `master` history was rewritten on 2026-10-29 — so whether the old measurement
  was correct for a then-current engine, or was itself anomalous, cannot be decided from the
  surviving evidence. Both readings remain open in the record.
- **`docs/g5_gap_diagnostic.json` was re-measured as well**; its conclusion is unchanged (the
  G5 gate is a property of the study stream, not the engine).
- **Regenerated from the artifacts:** manual §8.1's table, its headline, decision 4's control
  claim, finding 10, `docs/FACTS-SHEET.md` B1 and `docs/GATE-BOARD.md`. **Two claims were
  narrowed:** `real_git_history` does reach G2 processes and G3 workflows (cycle 14) and G4
  (cycle 6), so "G2, G3 and G5 never emerge unassisted" is false; and `no_dev_stopwords` is no
  longer byte-identical to baseline (1 theory / 1 question against 2 / 2).
- **`benchmarks/clone_check.py` now fetches the `v0.9.0` tag into its depth-1 clone**, so the
  fifteen freeze checks run instead of skipping; its pytest line reports **159 passed, 0
  skipped**, not 144 passed / 15 skipped.
- **New `tests/test_manual_cold_start.py`** derives the §8.1 table from the artifact and fails
  on drift, with a proof-of-firing.
- **`AGENTS.md`'s test count corrected** (69 → 164, after the new guard file). No engine change; no verdict re-read.

### Added — Paper 01's citations, and the lesson that carries none (2026-10-30)

- **Paper 01's citations are closed.** §4.1's curriculum-sensitivity framing and §5.4's
  four methodological lessons now carry inline `(Author, year)` markers, and the manuscript
  carries a **References** section with **seven** sources, each retrieved and read on
  2026-10-30: Bengio et al. (2009), Wang, Chen & Zhu (2021), Button et al. (2013),
  Simmons et al. (2011), Jacobs & Wallach (2021), Davis & Goadrich (2006), and
  Saito & Rehmsmeier (2015).
- **One lesson carries no citation, by design.** The second methodological lesson —
  compare against the strongest simple baseline and take the headroom from the ceiling —
  is the project's own rule and reports only Organica 1's own numbers, so it is stated as
  such rather than given a borrowed reference. The judgment is recorded in the source notes
  instead of being left silent.
- **The limit on what was read is written down.** Two sources were reachable only as their
  authors' abstracts, because the ACM Digital Library's full text is not retrievable in this
  environment; they are cited only for what those abstracts state.
- **A correction to a cited source was read and disclosed.** An erratum to Button et al.
  was published in *Nature Reviews Neuroscience* 14(6):451 (15 April 2013); it corrects the
  definition of *R* on page 366 and does not affect the power conclusions cited here.

### Corrected — the first world edge was reported without the distribution beside it (2026-10-30)

The owner reviewed the project's own reporting of the Gate 13 ranking failure and found one
claim that was true but incomplete in a way that mattered.

- **The rank of the first world edge is correct** — **31** in the 1-tag stimulus, **30 / 18 /
  53** in the 2-tag seeds, **16 / 8 / 8** after the LIMIT-4 separation — and it was reported on
  its own. A first edge appearing early in a frequency ordering reads as though the world's
  relations were nearly reachable by raising a budget.
- **They are not.** Under the engine's own global count-ranked selection the world's 112 edges
  are **spread through the table, not clustered at its top**: the top 20 recovers **0–1** of
  them, the top 40 **0–2**, the top 80 **8–16**, the top 160 **36–55**, and the top **320** —
  about **16×** the engine's budget — **106–109** (`docs/gate13_allocation_rule.json`, 3
  seeds). The five-seed capacity sweep puts cap 40 at **1–8 of 112** and the frozen cap of 20
  at **0–3 of 112** (`docs/gate13_capacity_sweep.json`).
- **A quoted figure did not survive contact with the artifact.** *"Cap 40 recovers 4–8 of
  112"* was carried in correspondence; the artifact gives **1–8 of 112** (per seed: 4, 7, 1, 2,
  8). The numbers above are read from the artifacts.
- **No measurement changes**, and the conclusion is unchanged — now stated with its
  distribution: **no frequency-based selection can find the world's relations**, because they
  are a third of the rows and are not clustered at the top of any frequency ordering.
- **Law II — the owner's ruling, 2026-10-30.** Keep the discrepancy disclosed and **do not
  amend the law yet**. The amendment waits on the owner's question: *is Law II a design
  requirement, or a description of V1's actual behavior?* Rewriting the law to match the
  frozen engine would erase the distinction that makes the discrepancy meaningful.
  `docs/DESIGN_LAWS.md` is not edited; the disclosure stays where the audit put it.

**A first edge at rank *N* is one edge arriving, not a set arriving.** A threshold, a first case
and a headline statistic are all single points, and the set is the claim.

→ `docs/GATE13-RELATION-SEPARATION.md`; `research-journal/phase_g_findings_20261021.md` §54
and §62; `docs/USER-MANUAL.md` findings 27 and 36; `docs/FACTS-SHEET.md` AD8;
`papers/README.md`

### Corrected — a hand-transcribed table had drifted from its artifact, and the first repair was defective too (2026-10-30)

The publication pass on Papers 01 and 02 turned up a defect in the record itself: the Pilot-0
score matrix in `docs/PILOT-0-INSTRUMENTATION-AUDIT.md` §2 declares
`docs/acquisition_single_seed_pilot.json` as its artifact, but **18 of its 36 values disagreed
with that artifact** in the fourth and fifth decimal of log-loss (largest gap **6.7×10⁻⁵**).

- **The artifact never changed.** The same values are present in both commits that carry it
  (`89b0744`, 2026-10-28; `4ceeab4`, 2026-10-29), verified by extracting them at each revision.
  The drift was in the **transcription**.
- **Six of the drifted values had been inherited** by
  `papers/01_developmental_structure_formation.md` §4.7, and six more each by the five-row
  summaries in `docs/ACQUISITION-ENDPOINT-AUDIT.md`, `docs/ORGANICA-V2-DESIGN-BRIEF.md`,
  `docs/FACTS-SHEET.md` (AC7), `research-journal/phase_g_findings_20261021.md` and
  `research-journal/_journal_entry_51.md`.
- **The first repair made it worse, differently.** The hand-written repair **replaced the two
  reference rows** (Bayes ceiling, base rate) with **duplicate copies of cells 7 and 8**. The
  defect is invisible to review — the table still had the right shape and the right-looking
  numbers — and was caught only by running the table against the artifact mechanically. The table
  is now **regenerated from the artifact** rather than patched.
- **The check is now permanent.** The new `tests/test_readout_tables.py` asserts every document
  that restates this readout against the artifact, and includes four assertions that the checker
  itself can fail.
- **No conclusion changes.** Organica's readout still loses to both baselines, the E-rem floor is
  still **0.403045**, the acquisition gate still fails, and transfer is still *not measurable*.
- **A second, pre-existing defect was caught by the test suite**: journal §59's Law V formula had
  its LaTeX escapes written in as **literal tab characters** rather than as `\t`, so the
  expression rendered as broken text and read as unsubstituted template placeholders. The
  committed record was red on `master` — `tests/test_doc_placeholders.py` failed at `67a7565`.
  The escapes are restored and the repair is noted in place; **no claim changes**.

**A table transcribed from an artifact is a new claim and needs a mechanical check against that
artifact** — and a repair written by hand is another hand transcription, and fails the same way.
The prior verification script reported "0 failures" because it never covered these cells.

### Added — Paper 02's citations, and eight figures that have to be able to fail (2026-10-30)

Papers 01 and 02 were brought to academic grade.

- **Paper 02's §2 now carries inline `(Author, year)` citations and a five-source References
  section**, every source read against a primary source on 2026-10-29: ACM Publications'
  *Artifact Review and Badging* v1.1 (including the Publications Board's 2020 interchange of the
  *Results Reproduced* / *Results Replicated* definitions), Bau, Liu, Wang, Zhu & Torralba's
  *Rewriting a Deep Generative Model* (ECCV 2020, oral), Elhage, Nanda, Olsson et al.'s *A
  Mathematical Framework for Transformer Circuits* (Anthropic, 2021), the W3C *PROV-DM*
  Recommendation (Moreau & Missier, eds., 2013), and Shumailov, Shumaylov, Zhao, Papernot,
  Anderson & Gal (*Nature* 631(8022):755–759, 2024) **with its 2025 Author Correction**
  disclosed — a notation typo, and no change to the cited empirical claim.
- **One candidate citation was dropped**: the Elhage paper's *faithful versus sufficient*
  distinction could not be verified from any readable copy, so it is not cited. **Cite only what
  was read.**
- **Eight dependency-free SVG figures** were added for Papers 01 and 02, generated by the new
  stdlib-only `benchmarks/figure_papers.py`. The generator **asserts every value it draws
  against the committed artifact**, bounds-checks its canvas, checks for text overflow, and
  **parses its own XML before writing** — added because an early build emitted a malformed
  attribute and the renderer silently stopped after the first bar. **A figure is a program that
  draws a claim, so it must be able to fail.**

→ `papers/01_developmental_structure_formation.md`;
`papers/02_persistent_structural_provenance.md`; `benchmarks/figure_papers.py`;
`docs/figure_p*.svg`; `tests/test_readout_tables.py`

### Corrected — the acquisition endpoint, the benchmark that replaced it, and the campaign that stopped at its gate (2026-10-28)

A review of the acquisition experiment found its **endpoint** could not measure
what the study claims. Every one of the five objections was checked against the
code and the frozen generator, and **every one was confirmed**; two further
defects were found that the review did not raise; and a third was found in the
redesign, which changed the study's structure. **No acquisition cell had been
run when the corrections were made.**

- **Seven defects, confirmed against the code.** (a) The task and the readout
  described **different relations** — the frozen generator draws each event's
  cause independently, and the gold relation is a within-event co-occurrence
  that does not predict the next event. (b) **F1@0.5 was degenerate**: the
  Bayes-optimal model scored **0.0000**, exactly like the model that knows
  nothing. (c) The projection was **directional** where the gold relation was
  undirected — 10 of 12 gold pairs appeared in one direction only. (d) The
  "fixed-rule ceiling" was a **relation oracle**, not a prediction ceiling.
  (e) **Retention and transfer were one number with two names.** (f) The
  engine's taxonomy has **no category for a tight group** — `_classify` needs
  clustering ≤ 0.4 and a co-occurrence-defined group has clustering
  **1.000**, so all 12 tags classified `unclassified` and **zero** concepts
  formed. (g) The generator's regime switch is **relation-invariant**.
- **The probe's headroom check was against the wrong comparator.** It compared
  the Bayes ceiling with a **base rate** — the weakest possible comparator.
  Against the **strongest** simple baseline (tuned bigram, decayed bigram,
  cell counter) the headroom was **0.005647** nats against the base rate's
  **0.105032**: the world's law is **first-order Markov**, so a bigram table
  is its natural learner and "understood the law" and "counted transitions"
  are not separable by a next-event score alone. That world was reclassified
  **CALIBRATION / CONTROL**.
- **Added — a compositional task that withholds a *combination* of familiar
  elements.** Four cells in a 2 × 2 grid of two latent factors; the
  tag-to-cell mapping is randomised per world; one held cell per world has its
  transitions removed from the training stream only. Its gate passes on **30
  independent worlds**: gap **+0.1035 nats**, 99 % interval **[+0.0996,
  +0.1074]** against the strongest simple baseline, with the held cell's gap
  **4.6×** the rest so the headroom is *generalization* headroom. Gates G1–G7,
  each with a proof-of-firing.
- **The campaign stopped at the preregistered acquisition gate.** The frozen
  engine asserted **0–3 of 112** world edges while its raw memory held
  **112 / 112 (100 %)**. The cause is one named bound — `MAX_PREDICTIONS = 20`
  — and raising **only** that cap restores **98.2 %–100 %**. Organica's
  readout scored **0.453018** against a replay learner's **0.347521**.
  **Transfer was not measured, and it is not a transfer failure**; the 600-cell
  factorial did not run.
- **Fixed — a gate that could not fire.** The harness and the runner each
  implemented "Gate 13" under one name: the harness on the raw-temporal basis
  (**100 %**, passed) and the runner on the asserted basis (**0.0 %**, failed),
  on the same seed and the same world. The harness now implements the
  pre-registration's dual accounting, gates on the asserted figure, exposes
  the cap-raised treatment so the failure is attributable, and its test asserts
  that Gate 13 **fails** on the frozen engine and **passes** under the
  treatment.
- **Added** — `docs/ACQUISITION-ENDPOINT-AUDIT.md` (the audit record),
  `docs/ORGANICA-V2-DESIGN-BRIEF.md`, `docs/V2-CAPACITY-DESIGN-BRIEF.md`;
  **updated** — the pre-registration (Revision 3, Amendment 3), the user
  manual (§8.19, finding 25), the facts sheet (§AC), `AGENTS.md` (rule 25),
  the README framing, and journal §51.

### Measured — the relation separation is real, oracle-free, and NOT sufficient (2026-10-29)

The sharpest open question after the causal account was: *can world relations
be separated from engine-generated relations, without modifying the frozen
engine?* It has now been measured. **All seeds are diagnostic
(`20261101`–`20261103`); the confirmatory sample (`20261106`–`20261130`, 25
seeds) is untouched.**

- **The mechanism, located.** `memory.py:261` gates the **trigger** of edge
  recording (`if event_type != "sleep"`), but `memory.py:332` does **not** gate
  the **lookback window** (`SELECT tags FROM events ORDER BY time DESC LIMIT ?`),
  so a world event can take its `tag_from` from a **sleep row**. This is
  **D2** in the audit-trace spec — disclosed, never quantified.
- **The substrate is 99.5 % the engine's own output** — **756–772 world events
  against 152,186–263,533 sleep events** (**201×–341×**). The engine stores one
  sleep event per candidate per cycle, so after 110 cycles it has written two
  to three hundred times as many rows about its own thinking as about the
  world.
- **The separation removes 35.7 %–40.7 % of the relation table, and 100.0 % of
  the removed rows have a sleep-sourced `tag_from`** — the D2 mechanism,
  confirmed exactly. It uses `event_type`, which the engine already records, so
  it is **not an oracle** (unlike the world-vocabulary filter of the previous
  entry).
- **And it is not sufficient.** With every contaminated row removed, coverage
  at the frozen cap of 20 is still **0.0000–0.0446**, and the top 20 is still
  **75–100 % intra-cell**. The separation *does* move the world's edges up
  sharply (first world edge from rank 30 / 18 / 53 to **16 / 8 / 8**), and that
  is still not enough to clear the gate.
- **Two distinct crowding mechanisms were in play.** In the **1-tag** stimulus
  the crowding is the engine's own vocabulary — first world edge at **rank
  31**, the top 30 rows all `internal→world`, verified independently. In the
  **2-tag** stimulus, once that is removed, the crowding is the **world's own
  co-occurrence**: intra-cell pairs out-count the law's transitions by roughly
  an order of magnitude, and a global count-ranked cut of 20 is consumed by
  them entirely.
- **The V2 requirement list is now three, not two:** provenance separation,
  relation-family separation, and **a ranking that is not raw frequency**. The
  third is the hard one, and the capacity sweep showed it cannot be bought
  with budget — precision never exceeds 0.3438 at any budget under either
  allocation rule.
- **Added** — `docs/GATE13-RELATION-SEPARATION.md`,
  `benchmarks/probe_relation_separation.py`,
  `docs/gate13_relation_separation.json`; **updated** —
  `docs/GATE13-CAUSAL-ACCOUNT.md`, `docs/V2-CAPACITY-DESIGN-BRIEF.md` (second
  addendum), `docs/USER-MANUAL.md` (finding 27, revision-log row),
  `docs/FACTS-SHEET.md` AC14, journal §54.
- **No V2 build is authorised.**

### Measured — the ranking requirement: every criterion the engine already stores fails (2026-10-29)

The third of the three V2 requirements — *a ranking that is not raw frequency* —
had been called the hard one, with no precedent in the engine. **It turned out to
have a precedent, and the precedent is the finding.** **All seeds are diagnostic
(`20261101`–`20261103`); the confirmatory sample (`20261106`–`20261130`, 25 seeds)
is untouched.**

- **The engine already computes the criterion.** `sleep.py:1139-1160` computes
  `ratio = count / max(source_freq, 1)`, stores it in every candidate's evidence,
  uses it for **survival**, and then sorts by **raw `temporal_count`** for
  **admission** — so every criterion the probe tested uses fields the engine
  **already stores**.
- **The grid.** 2 tables x 2 frequency scopes x 5 criteria x 3 seeds = **60 cells**,
  over `temporal_count`, `source_frequency`, `target_frequency` and `ratio`. The
  offline reconstruction of the raw table had to match the engine's own table
  exactly or the probe would refuse to report; it did, on every seed.
- **The best cell in the entire grid reaches coverage 0.0804 at precision 0.4500.
  The gate is 0.50** — six times short. Everything else is worse.
- **Neither fix works alone (0.0089). Together** they take coverage from
  **0.0000 to 0.0804** and precision from **0.0000 to 0.4500**, and flip the
  intra/inter balance from 20 / 0 to roughly 8–15 / 5–13 — the world's cross-cell
  relations enter the selection for the first time in meaningful numbers.
- **The engine's own normalized criterion is actively harmful here.** On the raw
  table under the engine's own scope, `ratio`, `cosine` and `pmi` each select
  **20 engine-vocabulary edges and 0 world edges** on every seed.
- **The mechanism is measured, not inferred.** `_record_tag_counts` sits inside the
  `if event_type != "sleep":` block, so **`tag_counts` is world-scoped** and the
  engine's own words have **no frequency entry** — `freqs.get(tag_from, 1)` returns
  1, so `ratio = count / 1 = count`, the maximum possible for that count.
- **A self-inclusive scope flips the failure the other way.** The engine's sleep
  output **names the world's tags** (`sable` 2,601 times, `olive` 7,753, `maple`
  35,986, `cedar` 52,070), so world tags acquire enormous denominators and are
  penalised, and the engine's *rare* metadata words win — best world edge
  `sable` -> `fern` at ratio **0.0177**, against `mutation` -> `cedar` at
  **0.1654**. **The world's vocabulary and the engine's own vocabulary are not
  separable by frequency in either direction**, so the discriminator cannot be a
  per-tag statistic; it must be a **relation-level** property — *which event the
  relation came from*.
- **Added** — `docs/GATE13-RANKING-CRITERION.md`,
  `benchmarks/probe_ranking_criterion.py`, `benchmarks/probe_ranking_mechanism.py`,
  `docs/gate13_ranking_criterion.json`; **updated** — `docs/USER-MANUAL.md`
  (finding 28, revision-log row), `docs/FACTS-SHEET.md` AC15, journal §55,
  `docs/ORGANICA-V2-DESIGN-BRIEF.md` §9.7.
- **No V2 build is authorised.**


### Changed — the historical record normalized to American English, with the change proven (2026-10-29)

The owner confirmed that the frozen records stay right under a spelling normalization — spelling
is not a claim, so no number, verdict, method, seed or decision rule is touched — and authorized
closing that gap.

- **234 words across 25 files** normalized, including the preregistrations
  (`ABLATION-PREREGISTRATION`, `ACQUISITION-EXPERIMENT-PREREGISTRATION`,
  `PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION`, `WORLD-SCALE-PREREGISTRATION`), the audit-trace
  specification, the measurement records and the frozen journal sections.
- **Three proofs, run against `HEAD` for every changed file**: non-target content byte-identical;
  the sequence of numeric literals identical; structure identical (headings, table rows, list
  items, lines). All three pass on all 23 changed files. Inline code spans were never rewritten,
  so **no identifier, file path, tag, test name or constant changed**.
- **A bug worth recording.** The first pass reported *"remaining: 0"* and was wrong by 88
  occurrences: the sweep and its check shared a document-wide code-span regex that mis-aligns on
  unbalanced backticks, so prose was skipped and then not counted. The bug surfaced only because
  a **second, differently implemented** check — a raw-text scan with no span logic — disagreed
  with the first. **A verifier that reuses the writer's parser inherits the writer's bug; a check
  that cannot disagree with its own writer is not a check.**
- **Every number, claim, verdict, date, method, seed and decision rule in the repository is
  unchanged.** The frozen engine is untouched.

### Corrected — Paper 00's audit completed: the constitution, measured against the code (2026-10-29)

The owner asked for the audit of Paper 00's broad claims to be *finished*, not just the two
defects that happened to be noticed. It was finished, by reading the six laws in
`docs/DESIGN_LAWS.md` against the frozen engine and the V1 record.

- **Two of the six architectural laws are contradicted by the implementation.**
  - **Law III (Cognitive Isolation) is violated in exactly the way it was written to prevent.**
    The design law requires that *"temporal precedes matrices are strictly computed on non-sleep
    events"*; `memory.py` gates the **trigger** on `event_type != "sleep"` but not the **lookback
    window**, so sleep output re-enters `precedes` at **201×–341×** the world's own event count
    (D2). **This is the same defect that contradicts Paper 05's "zero self-contamination"
    guarantee.**
  - **Law V (EIG Attention) is wrong twice.** Formally, the engine applies
    `uncertainty * (1.0 + novelty)` to questions and `uncertainty * novelty` to dreams, so the
    law's single expression is not what it computes for half its cases. Empirically, the
    pre-registered prediction that development is EIG-orthogonal came back **REVERSED** —
    selecting the *lowest*-EIG experiment develops **more** than the highest-EIG one.
- **Law IV (Grounded Dreaming) is mixed.** The confidence baseline **holds** (dreams are created
  at **0.04–0.06**, matching the design law), but the law's operative clause — a dream becomes a
  belief only if an external experiment generates the confirming events — is **never exercised**,
  because the engine generates experiments and never executes them, so no question can ever
  close.
- **Law VI holds** (thresholds **0.3** / **0.15**); **Law I was not separately audited** and is
  reported as such rather than assumed.
- **Also corrected:** the abstract's *"unbroken lineage to the raw experience"* is false (D3);
  *"causal predictions"* overstates the engine's own words — `memory.py` calls the temporal edges
  *"the organism's first approximation of causality"* — so the abstract now says **temporal
  predictions**; and the reference list's stale titles and its false *"Associated pre-prints"*
  label (seven manuscript files, **zero published**).
- **D4, a new disclosed defect.** The engine's stored `generation` field agrees with
  `docs/architecture.md` for **G1** and is **one lower for every primitive from G2 upward**
  (meta-concepts and processes `1`, workflows `2`, hypotheses `3`, theories and questions `4`,
  dreams `5`, investigations `6`, experiments `7`), and no document states the field's mapping —
  an undocumented offset, not a violated claim. The audit-trace specification is frozen at
  `audit-trace-v1` and was **not** edited to carry it; the disclosure lives in `docs/FACTS-SHEET.md`
  AD5 and manual finding 33.
- **Added** — manual finding 33 and a revision-log row; `docs/FACTS-SHEET.md` AD5; journal §59.

**A constitution that has never been audited against its implementation is a description of an
unimplemented architecture.** Every one of these was found by *writing the auditor*, not by
arguing — the strongest evidence this program has produced for its own thesis, and invisible to
any review that read the laws and the code side by side without measuring the code's behavior.

**Paper 00 is now accurate and still not ready to circulate**: it is not yet the recast position
paper the project needs, and its literature engagement is absent.

### Corrected — the first audit of Paper 00 and Paper 05 (2026-10-29)

The owner's publication framing put Paper 00 and Paper 05 outside the active submission
queue pending review. The first pass of that review found two verified factual defects and
one contradicted guarantee.

- **Paper 00's generation count was wrong against itself.** It said *"this hierarchy spans
  eight generations"* and then listed **nine** rows (G0–G8). `docs/architecture.md` names
  it correctly: *"The 8 Generational Primitives"*, with **G0: Experience** as the substrate
  and G1–G8 as the primitives. Paper 01's first draft made the same error and was
  corrected in the same pass.
- **Paper 00's Law II is stated without the project's own disclosure.** The manuscript
  calls it inviolable — *"Every structure carries explicit, verified `parent_ids` traceable
  to G0 events"* — but the frozen engine's chain **terminates at Layer 1**, because
  concepts, phrases, loops and predictions are built from tags and the structure→event
  link exists only as counts. This is **D3**, already disclosed in the audit-trace
  specification and left open because the frozen engine's constitution is the owner's
  decision. Corrected in place, with the disclosure carried inline.
- **Paper 00's abstract claims efficacy the record does not support.** The *forms* of
  curiosity, dreaming and inquiry exist (G5–G8); the *efficacy* does not — Phase K's
  matched mechanism ablations all came back empty (`NO_QUESTIONS` −0.0095 [−0.0328,
  +0.0140]; `NO_FALSIFICATION` +0.0241 [−0.0048, +0.0495]; `NO_DREAMS` +0.0000 [0.0000,
  +0.0000], all three intervals containing zero), and **Law IV is never exercised** —
  experiments are generated, every consumer only prints them, and no Question can ever
  close. **Paper 00's remaining broad claims and its literature framing are still
  unaudited**, and the manuscript is **not ready to circulate**.
- **Paper 05's core guarantee is contradicted by the measurement.** Its claim that the
  strict partition *"ensures zero synthetic self-contamination across indefinite life
  cycles"* does not survive contact with the record: **17.9%** of the distinct supporting
  transitions behind reported beliefs (802 of 4,481) are self-sourced, and **43.2%** of all
  distinct transitions recorded (5,436 of 12,583) are the organism's own output, entering
  the temporal substrate through the unfiltered lookback window (D2). The repair is a
  **new thesis** — *the limits of cognitive isolation in Organica V1* — not a revision.
- **Added** — manual finding 31; `docs/FACTS-SHEET.md` AD3; journal §57.

**A position paper is audited against the code, not against the prose.** The two documents
most likely to be circulated are the two least checked against the engine, because neither
is a measurement record and so neither is covered by the harness.

### Changed — the publication framing moved into the rule file; living guidance set to American English (2026-10-29)

The publication map was settled in conversation and recorded in `papers/README.md`, but a
framing that lives in one document is a preference rather than a constraint. It now also
lives in the rule file.

- **`AGENTS.md` rule 26** states two disciplines: **research-program structure is not
  publication structure** (the corpus is organized as a research-program map and a
  publication map kept side by side, so the layer map orients a reader without pressing
  every old manuscript or lab artifact into a paper), and **a claim's status names its
  scope** (four statuses — *supported within the tested scope*, *mixed / context-limited*,
  *reversed*, *not established / not measured* — with **not established is not refuted**,
  and a compound status required where the evidence splits).
- **`AGENTS.md`, `README.md` and `ROADMAP.md` set to American English.** Code spans and
  identifiers were protected, so no file path, tag, test name or constant was altered;
  the diff is prose only.
- **The historical research record was deliberately not rewritten.** Preregistrations,
  measurement records and the frozen journal sections are committed records whose value
  depends on having been written as they were; normalizing them is the owner's decision,
  not a cleanup.
- Manual revision-log row added, per the standing obligation that any change the manual
  describes is recorded in the same turn.

No measurement changed. The frozen engine is untouched — the only difference from `v0.9.0`
is the version string in `organica/__init__.py`, which is not in the frozen file set — and
the live study remains paused at 5,396 sleep cycles with no `organica.log`.

### Corrected — the audit build's closure was recorded in six places, and two documents still said the opposite (2026-10-29)

The owner read the paper directory and the V2 design brief and found two documents
still asserting that the audit build was unfinished, after it had closed, frozen and
been tagged on 2026-10-28.

- **Paper 02 contradicted itself.** Its abstract ended *"A5 field honesty and A6
  separation of trace from counterfactual remain pending; the audit instrumentation is
  not yet frozen"* and its §3 was titled *"Remaining acceptance work"* — while its own
  draft-status line said *"A5/A6 closed and the audit layer frozen at `audit-trace-v1`
  on 2026-10-28"* and its conclusion said the same.
- **The V2 design brief's §4.3 was headed *"The audit build is nearly, but not fully
  closed"*** and listed A5 and A6 as *"Still open"*. Five further passages carried the
  same state: build gate 4 was unmarked, the gate-5 annotation said *"gates 4 (A5/A6)
  and the study itself remain open"*, the §10 corrections table said A5/A6 *"remain
  open"*, the §11 table treated their closure as a future event, and the superseded
  banners in `ROADMAP.md` and `docs/V1-SYNTHESIS.md` described the audit build as
  unfinished and the pre-registration as Revision 2.
- **Eleven passages across four documents** corrected. The closure had been recorded in
  **six** places; six agreeing places do not compensate for two disagreeing ones, and a
  self-contradicting document is worse than a merely out-of-date one, because it
  teaches the reader that its own sentences cannot be relied on. The sweep criterion
  was **one status, stated in every document that states it**.

### Changed — the papers are the publication surface (2026-10-29)

The repository is a research program whose codebase is one component, and the
owner set the near-term publication sequence. It is now recorded in
[`papers/README.md`](../papers/README.md) so it is not re-derived. **The accurate
next milestone is making the first two manuscripts submission-ready — not publishing
them as they stand.**

- **Paper 01** — rewritten at academic grade as the honest empirical V1 account:
  methods and results reconciled to the committed record, with the negative
  external-task findings and the acquisition campaign retained rather than smoothed.
  Renamed to `01_developmental_structure_formation.md` to match its revised title
  (nothing referenced the old filename).
- **Paper 02** — revised at academic grade: Introduction, Positioning, Methods
  (observer, the two graphs, the three arms, every measured quantity **with its
  population**, the acceptance criteria with their proof-of-firing tests, and
  reproduction), Results (selection reconstruction, event-level attribution, ancestry
  honesty, behavioral invariance and the 1.7-cycle window boundary), Discussion,
  expanded Limitations, and data/code availability. The non-vacuity argument is now
  explicit: the default arm's candidate cap never bound, so the stress arm — in which
  403 candidates lost on rank — carries the selection test.
- **Paper 01's headline finding kept in its own words**: the **+0.1035 nats** is the
  *benchmark's headroom*, not a margin any learner achieved, and the transfer question
  is **not measurable** rather than answered.
- **House style set to American English** (`behavior`, `program`, `analyze`, `center`).
- **Two maps, kept side by side.** The corpus is organized as a **research-program
  map** (theory / proposed mechanisms / empirical findings) and a **publication map**
  (which manuscript can make a coherent, evidence-backed contribution now), so the
  three-layer view orients a reader without pressing every old manuscript or lab
  artifact into a paper.
- **Claims now carry one of four statuses**: *supported within this scope*, *mixed /
  context-limited*, *reversed*, and *not established / not measured*. **Not
  established is not refuted**, and *reversed* is a stronger statement than merely
  unsupported. Paper 01's central question was narrowed to match and no longer covers
  every probe.
- **Paper 05 might instead become a paper about the limits or failure of cognitive
  isolation** — a new thesis, not a revision of the existing one.
- **Held or reclassified**: Paper 00 is a separate position paper, to be developed only
  after its broad claims and literature framing are audited; Papers 03 and 04 are
  mechanism *proposals*, not demonstrated-efficacy results; Papers 05 and 06 stay
  historical until their claims are rechecked, and **no claim in either is currently
  strengthened by recent work — neither should be described as if it were**: Paper 05
  **cannot** be presented as evidence that the system prevents self-contamination, because
  its strict-firewall claim conflicts with the measured sleep-sourced relations, and
  Paper 06's major lifecycle, stability and lineage claims remain unverified against the
  current evidence.
- **The Phase L characterization, the V1 synthesis and the audit artifacts are research
  records, not manuscripts.** They are not additional papers in `papers/`, and the
  inventory stays **seven manuscript files, zero published**.

**No measurement changed.** The six negative task families, the Phase L verdict
`H3-L — INCONCLUSIVE`, the acquisition gate failure and the transfer result of *not
measurable* all stand as recorded; every seed used in the mechanism probes remains
diagnostic; the frozen engine is untouched.

### The audit build is CLOSED, TAGGED and FROZEN (2026-10-28)

The audit build's stop condition is met and has been executed. **A1–A7 are all
met**, the three probe arms (default, stress, forced-tie) are regenerated, and
the instrumentation is **tagged `audit-trace-v1`**.

- **A5 closed** — field honesty enforced; records verified to contain zero
  mislabelled count fields, and proved to fail if competing flow is mislabelled
  as contradictory observations.
- **A6 closed** — counterfactual separation enforced; trace records and schema
  verified to contain zero counterfactual claims, and proved to fail on
  counterfactual injection.

**From that tag, no feature may be added to the instrumentation.** It may still
be *fixed* if it is found to be wrong, but not *extended*; a new requirement
goes to the study's wish-list instead.

**The package version was left untagged at that freeze.** `audit-trace-v1` marks the
*instrumentation*, not a release of the package — which keeps the three version
namespaces (package version, architecture generation, research campaign) separate
as this changelog requires. (Corrected 2026-11-09: the package version that freeze
left untagged, 0.10.0, was tagged on 2026-10-31, and 0.12.0 was tagged on
2026-11-06. What the tag marks is unchanged: the instrumentation, not a release.)

Verification at the freeze: **128 tests pass** · 83 anchors / 0 broken · 1,142
document paths all exist · the live study untouched at **5,396** sleep cycles
with no `organica.log`.

### Corrected — "bottleneck" is not "deepest cause": the acquisition failure is a PRECISION limit, not a capacity limit (2026-10-28)

The parallel session's Gate 13 write-up named **`MAX_PREDICTIONS = 20`** as the
cause of the acquisition failure, on the evidence that raising the cap to
1,000 restored coverage to 98.2 %–100 %. That was sound on its own evidence,
but it left **three probes written and uncommitted** that ask whether there is
a better fix than a bigger budget. Running them, and adding a fourth, changes
the answer. **All seeds used are diagnostic (`20261100`–`20261105`); the
confirmatory sample (`20261106`–`20261130`, 25 seeds) is untouched.**

- **The world's relations are in memory.** Raw temporal coverage is
  **0.97–1.00** on every seed and both stimulus shapes (**1.0000** on all six
  2-tag seeds) — the same figure the pilot recorded.
- **But they are a minority of the candidate space, and they are not the
  high-count rows.** The `precedes` table has **366–518 rows** for a 16-tag
  world; only **232–240** are world-tag pairs; the world's 112 edges are about
  a third of what any selection must retain. **Precision never exceeds
  0.3438** at any budget under either allocation rule.
- **A 1-tag stimulus does not rescue it** — it removes the within-cell pairs by
  construction, quintuples coverage to **0.1719–0.1953**, and still fails
  **0 of 6** seeds. The top of the table is internal vocabulary
  (`type -> olive`, `generation -> olive`).
- **The capacity sweep is a steep monotone dose-response**: **0.0000–0.0268**
  at cap 20, **0.0089–0.0714** at 40, **0.0893–0.1786** at 80,
  **0.9911–1.0000** uncapped — needing **240–244** asserted edges, about
  **12×** the budget. At the frozen cap the law-bearing **inter-cell** edges
  are **0–3** while intra-cell edges are **28–39**: the engine formed the
  world's partition and none of its transitions.
- **A per-source allocation rule is NOT the fix** — this refutes the
  hypothesis the observation-protocol probe suggested. Per-source K=10 retains
  **258–286** edges for coverage **0.72–0.77**, where the global rule reaches
  **0.95–0.97** at 320.
- **So the deepest cause is PRECISION.** In a candidate space where the signal
  is a third of the rows and is not clustered at the top of any frequency
  ordering, **no frequency-based selection can find it**. The specific
  pollution is **internal vocabulary**: **27–34** distinct sources for a
  16-tag world.
- **Three things are called "Gate 13"** and they disagree — the protocol's
  (asserted structure, global top-20: FAIL), the capacity sweep's (global
  top-K: dose-response), and the observation probe's (`precedes` table,
  per-source top-20: PASS). The third is a different *selection rule over the
  same table*, and the whole FAIL/PASS difference is that rule. The filter in
  that probe selects on the world's own tag list and is therefore an
  **oracle**, not an organism-side fix.
- **Added** — `docs/GATE13-CAUSAL-ACCOUNT.md`,
  `benchmarks/probe_allocation_rule.py`, `docs/gate13_capacity_sweep.json`,
  `docs/gate13_allocation_rule.json`; **updated** —
  `docs/V2-CAPACITY-DESIGN-BRIEF.md` (the brief's premise was measured and it
  does not hold; two of its design objectives are refuted),
  `docs/ORGANICA-V2-DESIGN-BRIEF.md` §9.7, `docs/ACQUISITION-ENDPOINT-AUDIT.md`
  §8.3, `docs/USER-MANUAL.md` §8.19, `docs/FACTS-SHEET.md` AC11–AC13,
  `AGENTS.md` rule 25(d), journal §52.
- **No V2 build is authorised.** The V2 question is narrower and sharper: can
  the organism identify which of its vocabulary items are its own, and can it
  rank candidates by something other than raw frequency?

### Corrected — five claims in the project's own summary, narrowed (2026-10-26)

A review of the project's *summary* — not of its measurements — found five
sentences that were wider than the checks behind them. All five were
corrected, and the corrections were made **before the acquisition experiment
ran**, so the next study does not inherit an overstatement from the previous
one. **No number was recomputed, no artifact re-read, and no criterion
reinterpreted.** The protocol verdict `H3-L — INCONCLUSIVE` stands, the Phase L
characterization stands, and the six negative task families stand.

1. **"Revision exists" → "structural displacement exists."** Phase L's
   `DI`/`PI` are structure-retention indices — they measure whether later
   *structure* displaces earlier *structure*, not whether a *belief* was
   corrected against ground truth. Belief revision is a separate capability
   question, and the one head-to-head measurement of it was a clean loss:
   Organica **0.4111** vs the best simple baseline **0.9846**, difference
   **−0.5735**, 98.33% interval **[−0.6162, −0.5309]**, **REVERSED**.
2. **The 3:1 crossing is robust *within this defined experiment* — this
   engine, this world family, this support-ratio axis.** The eight alternative
   bootstrap seeds test **resampling stability, not new worlds**; they re-draw
   from the same measured seeds. **3:1 is not a general threshold for
   Organica.**
3. **Path dependence is supported; strict order dependence is not tested.** The
   curriculum and history comparisons vary the event **multiset and the order
   together**, so they cannot separate "order matters" from "content matters".
   Isolating order requires the multiset held fixed — that comparison has not
   been run.
4. **Transfer: no positive transfer has been demonstrated, and the measured
   cross-domain result was negative** — **−0.4863** across **12 domain pairs**,
   mean shared vocabulary **0.17 tags**. Other forms of transfer remain
   untested.
5. **"Independently auditable" means independently *reconstructed from the
   engine's state*, not independently *replicated by another lab*.** The trace
   also covers the organism's **surviving, current** structures rather than
   their full past, and the audit layer is **now complete** — A1–A7 all met,
   tagged and frozen at `audit-trace-v1` (2026-10-28).

The project now leads with the compressed state: *Organica demonstrably
changes its internal structure as experience and curriculum change. Under one
tested pressure axis, later structures can abruptly displace earlier ones. The
project has built a strong instrument for auditing surviving state and
implemented decisions. It has not yet shown that these structures yield useful
knowledge or positive transfer; the acquisition experiment could address that,
and its metric and memory-removal conditions are now pinned — it is
pre-registered and not yet run.*

The lesson is recorded as `AGENTS.md` rule 24: **a claim must be no wider than
the check behind it, and the summary is where the widening happens.** The
measurements were right and the *headlines* were wrong, and a wrong headline is
invisible in a diff — it looks exactly like a right one. Propagated to the
README, the Phase L synthesis (§2.2, §2.3a, §3.3, §8), the V1 synthesis
(§2.2, §3, §5, §9), the audit-trace specification (§10, §11), the emergence
criteria (§4), the manual (§2, §8.18, finding 24, six common misreadings), the
facts sheet (§AB1–§AB7) and the journal (§50).

### Result — Phase L primary axis (V1): a reproducible crossing, and a criterion that did not pass

The Phase L campaign ran its primary axis to completion: **80 of 80 cells**,
8,057.8 s wall clock, 10 seeds per sweep point, `PYTHONHASHSEED=0` pinned and
recorded as the *actual* value, 99.00% decision interval, 10,000 bootstrap
replicates, against the frozen `v0.9.0` engine (verified unchanged by the
freeze test). **All four instrument audits passed on the live run**, and **no
cell was unmeasurable** — nothing was excluded and nothing was zeroed.

**Verdict: `H3-L — INCONCLUSIVE`.** The protocol's remedy for that verdict is
*raise n; conclude nothing*, and **no Phase L outcome authorises a V2** — the
secondary arms V2–V5 were deliberately not run.

| Label | DI (sd) | PI (sd) | DS | Latency | Seeds reaching DI > 0.5 |
|---|---|---|---|---|---|
| 1:4 | 0.000 (0.000) | 0.789 (0.078) | −0.789 | — | 0/10 |
| 1:3 | 0.000 (0.000) | 0.794 (0.070) | −0.794 | — | 0/10 |
| 1:2 | 0.000 (0.000) | 0.783 (0.096) | −0.783 | — | 0/10 |
| 1:1 | 0.000 (0.000) | 0.728 (0.055) | −0.728 | — | 0/10 |
| 2:1 | 0.283 (0.124) | 0.600 (0.122) | −0.317 | — | 0/10 |
| 3:1 | 0.722 (0.037) | 0.022 (0.039) | +0.700 | 347 | 10/10 |
| 4:1 | 0.739 (0.064) | 0.000 (0.000) | +0.739 | 285 | 10/10 |
| 6:1 | 0.750 (0.029) | 0.000 (0.000) | +0.750 | 236 | 10/10 |

**Three of the four pre-committed criteria are met.** DI is monotone increasing
with range 0.750; the curves cross at **3:1**, interior to the sweep; and the
crossing is reproducible under a paired bootstrap over seeds — interval
**[5.0, 5.0]**, **10,000 of 10,000** replicates finding a crossing, eight
alternative bootstrap seeds all `INTERIOR`, leave-one-seed-out 3:1 in **10 of
10** folds.

**Criterion 2 — *PI is monotone decreasing* — was not met.** Mean PI rises
0.789 → 0.794 between 1:4 and 1:3 (+0.005, against a per-point standard
deviation of 0.070) before falling monotonically through the rest of the
sweep. The criterion has no noise clause: it is evaluated on the mean curve,
and the mean curve rises. It was evaluated once by the committed code and it
failed; it was **not** re-read, relaxed, or reinterpreted afterwards, and the
stable RT was not allowed to stand in for the criterion that failed.

**A wording defect in the protocol is recorded rather than exploited.** The
`H3-L` bucket is described as *"intervals too wide to place RT"*, which is not
what happened — the RT interval is the narrowest possible and criterion 4
passed comfortably. The verdict is INCONCLUSIVE because criterion 2 failed, not
because the threshold could not be located. The next phase must say what
"inconclusive" means when the interval is narrow and a different criterion
failed.

**Established:** the instrument works and the pilot's flat line was an
artifact; the organism sits at the preservation pole (DI exactly 0.000, PI ≈
0.79) under low displacement pressure; on this axis DI and PI cross at 3:1 and
the crossing is highly reproducible. **Not established:** a boundary in the
`H2-L` sense, PI's monotone decrease, anything about capability, and anything
about the support ratio being *the* operative variable beyond this axis on
this engine.

Added `docs/phase_l_results.md` and the artifacts `docs/phase_l_results.json`
and `docs/phase_l_results.ndjson`. Journal §38, facts sheet §X, manual §8.10
and finding 15.

### Result — Phase L raise-n (n=30): the verdict stands, and the reason is now visible

The raise-n campaign finished: **240 of 240 cells**, 30 seeds per point,
12,738.1 s, `PYTHONHASHSEED=0` pinned and recorded as the actual value,
99.00% decision interval, against the frozen `v0.9.0` engine. All four
instrument audits passed on the live run and **no cell was unmeasurable**. It
is a strict **superset** of the n=10 run — the original ten seeds are the
first ten of the new list, so the 80 original cells were **reused, not
recomputed** — and the reuse was verified: all 80 are byte-identical in the
merged file.

**Verdict: `H3-L — INCONCLUSIVE`, unchanged — and now with TWO of the four
criteria unmet.**

| Criterion | n = 10 | n = 30 |
|---|---|---|
| 1. DI monotone increasing | **met** | **not met** |
| 2. PI monotone decreasing | not met | not met |
| 3. DI range ≥ 0.25, crossing interior | met | met |
| 4. RT interval excludes both endpoints | met | met |

**The Revision Threshold did not move:** still 3:1, interval **[5.0, 5.0]**,
**10,000 of 10,000** replicates finding a crossing, eight alternative
bootstrap seeds all `INTERIOR`, leave-one-seed-out at 3:1 in **30 of 30**
folds. Tripling n did not move the one quantity the phase set out to locate.

**The curve is a step function, not a ramp.** DI is **exactly 0.000** at
1:4–1:1 for all 30 seeds; **PI is exactly 0.000** at 4:1 and 6:1; DI ≈ 0.71
across the top; two sharp transitions in between. Revision latency goes from
**0/30** seeds reaching DI > 0.5 at 2:1 to **30/30** at 3:1 (mean 356 cycles,
median 351).

**Both failing criteria fail on steps whose 99% paired interval contains
zero** — +0.011 [−0.026, +0.044] at 1:4 → 1:3, and −0.007 [−0.037, +0.022] at
4:1 → 6:1 — while every step whose interval excludes zero is a real
transition. **A criterion that flips when n changes is measuring the draw,
not the organism:** resampling the 30 measured seeds, criteria 3 and 3b hold
in **100%** of random subsets, criterion 1 in 19.3% / 16.1% / 0%, criterion 2
in 12.0% / 6.6% / 0%, and **all four together in 2.9% / 1.2% / 0%**. Strict
monotonicity is not a property this organism's displacement curve has at any
practical n, and more seeds cannot turn a plateau into a ramp — so "raise n"
is exhausted as a route to satisfying criteria 1 and 2. **This does not
re-score the protocol:** the verdict stands, no boundary is claimed, and the
four criteria stand as written.

**The added seeds moved the curve more than resampling should allow** — DI at
6:1 0.750 → 0.697 (p = 0.0022) and DI at 2:1 0.283 → 0.164 (p = 0.0103)
against random 10-vs-20 splits — so a **seed-exchangeability audit** with 30
fresh, non-consecutive, pre-declared seeds was run to tell non-exchangeability
from an unlucky draw. It is an instrument audit and produces no experimental
claim. **The seeds are exchangeable**: the fresh scattered set gave DI 0.7241
at 6:1 against the campaign's own 0.7148 (30 seeds) and 0.7500 (its original
ten) — a difference of +0.0093, **p = 0.60** against random 30/30 splits of
all 60 measured values — and its own arbitrary half-split gap of **−0.0407**
has the opposite sign to the campaign's +0.0528 at similar magnitude. **The
original ten seeds were an unlucky high draw, not a seed-block artifact**, so
the paired bootstrap over seeds is sound.

`docs/phase_l_results.md` is rewritten for the raise-n result; journal §39,
facts sheet §Y, manual §8.11 and finding 16.

### Result — Phase L characterization: regime behavior, and a verdict that did not move

The raise-n result has been read and **published as a characterization**:
[`docs/PHASE-L-SYNTHESIS.md`](docs/PHASE-L-SYNTHESIS.md). The protocol verdict
is **unchanged** — `H3-L — INCONCLUSIVE` — and the two are deliberately kept
as separate artifacts, the measurement record and the synthesis, neither
re-scoring the other.

> *Organica 1 does not appear to exhibit a continuous coherence–plasticity
> trade-off. It appears to exhibit regime behavior separated by a
> reproducible transition region.*

**What survived increasing n:** the preservation plateau (**DI exactly 0.000**
for all 30 seeds across 1:4–1:1), the transition region, the crossing at
**3:1**, the reproducible RT (**[5.0, 5.0]**, 10,000/10,000 replicates,
leave-one-seed-out 3:1 in **30 of 30**), and the abrupt latency shift
(**0/30 → 30/30** seeds reaching DI > 0.5 between 2:1 and 3:1). **What did not
survive:** strict monotonicity, which got *weaker* as n grew — exactly as
expected if it was never a property of the organism.

**Raising n is exhausted on this axis and will not be repeated.** The reason to
raise n was to distinguish *the tiny PI reversal is noise around an otherwise
monotone curve* from *the curve is genuinely step-shaped* — worlds that predict
differently. n=30 distinguished them: the low-end steps are each consistent
with zero, the plateaus are exact across all 30 seeds, and the monotonicity
criteria fail *more* firmly. The campaign was not failing for want of
precision; it was failing because the curve is not the curve the protocol
expected.

**The dangerous question, answered.** *A stable, reproducible threshold at 3:1
— that is a boundary, isn't it?* **It is not.** A threshold divides a continuum
only if the trade-off is a continuum; here the curve is flat on both sides of
the crossing, and the crossing is stable because the organism **switches
regimes**. That is a real property of the measured system, and it is not the
property the protocol asked for.

**What comes next.** **V2–V5 remain unrun** — no Phase L outcome authorises a
V2. The secondary axes are now a more specific question than the one Phase L
was written to ask: not *which variable moves a smooth boundary*, but **why is
the curve step-shaped** — what sets the width and location of the transition
region.

Added `docs/PHASE-L-SYNTHESIS.md`; manual §8.12 and finding 17; facts sheet
§Z; journal §40.

### Added — the development audit trace specification (Phase M groundwork)

The specification for a **developmental auditability** record: the artifact
that would let an investigator reconstruct *why* a structure survived — what
evidence was used, how the claim was formed, what the competing candidates were
— **without asking the system**. Written against the frozen engine's **actual**
report fields and persistence limits, source-read on 2026-10-25.

**Level 1 (provenance) is available.** `get_ancestry()` reads parent links that
are already stored; the limits are depth 7 and the 4,000-event window, and a
parent outside the window means *not found in window*, never *no parent*.

**Level 2 (evidence) is available, with one correction.** `support_count` counts
**temporal transitions**, and `contradiction_count` is the subject's **competing
flow** — not a count of observations that contradicted the claim. The record
format as first proposed ("12 supporting observations, 4 contradictory
observations") would have put a false claim at the center of the audit and is
corrected in the spec.

**Level 3 (selection) is available without instrumenting the engine.** The
report contains only survivors, but under the default `salience` policy the
whole contest — including candidates culled by the confidence rule and
candidates that lost on rank — is reconstructible from the report's own Layer-2/3
outputs plus the persisted priors. The plan is therefore **assembly, not
instrumentation**; a labeled observer build is the fallback, and it must prove
that recording the trace leaves the engine's outputs unchanged.

**Counterfactuals live behind a wall.** *"Candidate B would have survived
without A"* is a **replay**, not a trace: a separate run, a separate artifact,
its own label.

**Six acceptance criteria** for the eventual build, each able to fail:
evidence-replay exactness, selection-reconstruction exactness, ancestry honesty,
behavior invariance, field-honesty, and trace/counterfactual separation.

**Two defects disclosed, neither patched** (Organica 1 is frozen):
`contradiction_count` is easy to misread, and the temporal graph's lookback
window has **no `event_type` filter**, so a supporting transition can originate
from the organism's own previous sleep payload while co-occurrence and
tag-frequency edges are world-scoped.

Added `docs/AUDIT-TRACE-SPEC.md`; manual §8.13 and finding 18; facts sheet §AA;
journal §41; AGENTS.md rule 17.

**And the specification's load-bearing claim was tested.** `benchmarks/audit_trace_probe.py`
is an **instrument probe, not an experiment about the organism**: it runs the frozen engine on
the frozen cause-world generator and, at every cycle, rebuilds the selection contest from
the report and the substrate and compares. **Default arm** (the engine's own belief cap of
15): **120 cycles, 1,412 beliefs checked, A1 evidence replay 0 failures, A2 selection
reconstruction 120/120 cycles.** **Stress arm** (cap 5, so the cap binds): **60 cycles, 290
beliefs checked, A1 0 failures, A2 60/60 cycles, 403 candidates lost on rank.** The default
arm alone was a weak test — its pool peaked at 12 against a cap of 15, so the
*lost-on-rank* branch never fired — which is why the stress arm exists and why the write-up
says so. **The checks can fail:** `tests/test_audit_trace_probe.py` breaks the auditor on
purpose and requires A1 and A2 to go red, and they do. **So the selection contest needs no
hook inside the engine** — assembly, not instrumentation. What is *not* established:
generality, the `stochastic` policy, the four remaining acceptance criteria, or anything
about learning.

Added `benchmarks/audit_trace_probe.py`, `tests/test_audit_trace_probe.py`, and the artifacts
`docs/audit_trace_probe.json` and `docs/audit_trace_probe_stress.json`; spec §10; facts sheet
§AA8.

### Added — the rule that keeps the audit trace from becoming a second inventory

An audit layer is attractive, and attractive things become projects. The trace
could have been built, extended and admired without ever adjudicating a question
the project wanted answered — which would make it a *second* inventory
("how many events resolve?"), and would swap one measurement habit for another.

**So the rule is pre-committed, not aspirational:** the next protocol's success
criteria must contain at least one **trace-derived diagnostic**, and a result
that fails it **fails the protocol even if the headline behavior is correct.**

**The first instance is a disqualifier: *a predicted-correct result whose
supporting evidence is self-sourced is not a transfer result.*** The trace
reports the world/self split of every belief's support, because the temporal
graph's lookback window has no `event_type` filter and a supporting transition
can originate from the organism's own previous sleep payload (D2). That is
D2's first concrete use, and it turns a disclosed defect into a **live
scientific instrument** — a defect that can defeat a claim is worth more than a
defect that is merely recorded.

**Second guard:** the trace's own metrics — evidence-trace completeness,
lineage completeness, selection reproducibility — are **diagnostics of the
instrument**: reported, never criteria. An audit layer earns its keep by
adjudicating a live question, not by accumulating completeness.

Added spec §11; AGENTS.md rule 18; manual §8.14 and finding 19; facts sheet
§AA9; journal §42.

### Corrected — the audit-trace probe's headline, and three errors in the specification

The probe's first version reconciled the **aggregate** `precedes` table against
the engine's reported support counts. That demonstrates the auditor reproduces
Organica's *counts* and its *selection decisions*; it does **not** demonstrate
that it can identify the individual experiences behind a count. The
specification claimed the stronger thing, and is now corrected to say exactly
what was measured: **aggregate evidence reconciliation and selection
reconstruction passed.** Event-level attribution is now its own acceptance
criterion (**A7**), measured with a passive store-time observer.

**Three corrections to the specification, each verified against the source
before being written down:**

1. A cycle returns **14** candidate lists, not 13.
2. The engine's lookback window **includes the event being stored** —
   `store()` inserts the row before recording edges — so the window is the
   event itself plus two others, and **within-event tag pairs also become
   temporal edges**. The first replay rule was wrong.
3. **A post-hoc replay from the final log cannot reconstruct the window**: the
   engine's query has no `rowid` tiebreak, and sleep-candidate rows are
   pruned. Event-level attribution therefore **requires** a passive
   store-time observer, whose guard must mirror the engine's own
   `event_type != "sleep"` rule.

**Results.** Default arm: A1 1,412 beliefs / 0 failures, A2
120/120 cycles, A7 1,412 beliefs / 0 failures with 244 aggregate
edges reconciling exactly. Stress arm: A1 290, A2 60/60, A7 290, **403 candidates lost on rank**. A4
behavior invariance passes — observer on and off produce byte-identical
reports apart from `ran_at`.

**D2 is now measured: 53,980 of 307,857 attributed support transitions (17.5%) are
self-sourced** — the prior event was the organism's own sleep payload. Roughly
one belief-support transition in six rests on the organism's own output. That
is the baseline the pre-committed disqualifier is read against.

**The probe found two defects in itself** — an observer that attributed
sleep-event transitions the engine never makes, and an invariance check that
compared a wall-clock timestamp — both caught by the checks rather than by
inspection. The generalisable lesson is now **AGENTS.md rule 17(d): an
aggregate is not an attribution; name the resolution of every check.**

### Corrected — the self-sourced figure's denominator, and the forced-tie arm

The probe's most quoted number — the share of self-sourced support — was
measured against the wrong denominator. It pooled the support of every reported
belief across every cycle in which that belief was reported; because a belief's
support count is **cumulative**, a transition that occurred early is counted
again in every later cycle where the belief survives. That pooled number counts
**support references**, not distinct evidence.

**Three views, kept apart** (default arm): **distinct evidence behind reported
beliefs** 802/4,481 = **17.9%** self-sourced — the disqualifier's figure;
**pooled support references** 53,980/307,857 = 17.5%; **all distinct transitions recorded**
5,436/12,583 = **43.2%**, including edges no reported belief ever rested on. Correcting
the denominator moved the headline only slightly (17.5% → 17.9%), and that agreement is worth
stating — but it surfaced a separate and much larger number: **43.2% of the organism's entire
distinct transition surface is its own sleep output**, against 17.9% of the evidence actually behind its
claims.

**The forced-tie arm is now run.** The engine's lookback query has no
tie-breaker, so the schema does not determine which rows a tied window selects.
The clock is patched so every four consecutive stores share a timestamp,
producing **479 stores with a genuinely tied window**; the observer reproduces the engine's
choice anyway and **A7 stays exact**. The honest statement: the *implementation*
is deterministic for identical queries over identical data, while the *schema*
still does not determine the window under a tie — the observer is the reason,
not a proof about the engine.

Added `docs/audit_trace_probe_tie.json`; the probe gained a `--force-tie` arm
and a distinct-evidence view; a seventh test requires the two views to stay
apart. Recorded in spec §3.3, §6, §10, §11; facts sheet §AA11; journal §44.

### Changed — the figure's population, and the disqualifier as a per-claim rule

**The 17.9% is a share of the union of the unique evidence transitions behind beliefs reported during
the run** — deduplicated, restricted to the edges those beliefs rested on. It is **not** a per-claim
share, and it is **not** evidence that self-sourced support caused an incorrect prediction.

**A run-level share cannot carry a per-claim claim**, so the disqualifier is now written against the
claim itself, in four conditions fixed in advance: report the world/self split for the **claim's own**
support; a **majority** of it must be world-derived; its self-sourced share must be **no higher than the
run's baseline rate** for beliefs; and the comparison is against the claim, never the organism in
general, with a failed condition **failing the protocol even if the prediction was correct**.

**The rule is conservative, and says so.** The contamination is **measured, not shown to be
consequential** — nothing yet shows that a self-sourced transition caused a wrong answer — so the
disqualifier is a statement about *what counts as evidence of transfer*, not a claim that the organism
is damaged by its own output. That is also why it is pre-committed: a criterion that only bites once
the harm is demonstrated would never bite at all. **Whether self-sourced support *hurts* is now a
measurable question**, and the trace is the first instrument that can ask it.

**The observer's window match is an implementation match, not a schema guarantee.** The engine runs
`SELECT tags FROM events ORDER BY time DESC LIMIT 3`; the observer runs the same ordering clause with a
wider projection, so the two are not byte-identical SQL. The match is empirical on the tested SQLite
implementation, and the evidence for it is **A7's exactness** — a window mismatch on any store would
have broken the reconciliation. The 60-cycle forced-tie artifact is committed as
`docs/audit_trace_probe_tie.json` (60 cycles, 479 tied windows, 0 mismatches).

Recorded in spec §3.3, §10, §11; facts sheet §AA12, §AA13; journal §45.

### Fixed — the acquisition pre-registration, after a review found five defects

**The pre-registration is now Revision 2**, committed before any cell is run. Five
defects in Revision 1 were found and corrected:

1. **The endpoint was the wrong metric.** Task support was scored with Phase L's
   `DI` — `late_structure_retained / late_structure_available` — which measures
   **structural displacement, not prediction**. Now a **ground-truth prediction
   score** on a fixed label set, with the exact predictions named, F1 at 0.5
   primary and balanced accuracy and Brier co-reported.
2. **"Source experiences removed" did not say what derived memory survived.**
   Ingest also accumulates `cooccurrences` and `tag_counts` (`memory.py:282`,
   `306`), which outlive the event rows. The condition is now named **"episode
   removal with learned graph retained"**, the retained set is listed, and **the
   same rows are removed from every learner's store** — which is what makes the
   comparison about reconstruction versus replay rather than about unequal
   access to evidence.
3. **The cell matrix was not specified.** Now **one complete table with the
   exact number of runs — 10 per seed, 30 seeds, 180 engine runs** — and a
   prediction for every cell, with `P-none × E-pres` stated as the untreated
   baseline rather than an extra cell on top of six.
4. **It was not an executable plan.** Now pinned: the generator and its
   parameters, the target relation, the phase boundaries (the regime switch lands
   exactly on the follow-up boundary), the seeds and sample size, the
   quantitative decision rule, and both baselines' algorithms, tuning grids,
   memory accounting and test-time procedures. **"Same memory budget", defined:**
   identical raw rows and identical removal for every learner, with derived
   state deliberately *not* equalised because derived state **is** the mechanism
   under test — and in the `E-pres` cells the comparison learners have strictly
   *more* usable access than Organica, so a win for Organica is conservative.
5. **The audit build had no stop condition.** Now explicit: **close A5 and A6
   only** (A1, A2, A3, A4 and A7 are closed and are not reopened), then **tag,
   freeze and stop** — no feature may be added to the instrumentation afterwards.

**Drift fixed in the same pass.** The README claimed every abstract structure
keeps parent links *"down to raw experience events"* — **the engine has never
done that**: the `parent_ids` chain terminates at Layer 1, and the
structure→event link is a count, not a pointer. The README's restatement was
corrected; **Law II of `docs/DESIGN_LAWS.md` is left as written** with the
discrepancy disclosed in the audit-trace specification as **D3**, because the
frozen engine's constitution is the owner's decision. Also fixed: the
specification's *"all six"* acceptance criteria where the table lists seven; the
manual's status table dated 2026-10-23 while the file recorded 2026-10-26 work;
and the missing **dated supersessions** in the README, `ROADMAP.md` and the V1
synthesis.

**The owner's standing decisions are recorded:** V2 **not cut**, live study **not
restarted**, V2–V5 **not run**, no further open-ended audit work. Sequence:
**finish the audit build → freeze it → run the acquisition experiment → compare
against the replay learner → publish whatever happens → only then discuss V2.**

### Added — the acquisition experiment pre-registration, and two diagnostics that changed its questions

The blank-slate question is now **can experience create a structure that
remains useful after the originating experience is gone?** — and **does the
organism carry structure forward, reconstruct it from evidence, or do both
under different conditions?**

**Two read-only diagnostics, run before the design was written, and
quarantined in the pre-registration as design inputs rather than
predictions:**

- A surviving structure's parent set is identical in **94.5%** of 3,883 structure-cycles.
- **But 87.2% of all 8,416 lineage links point at structures re-derived in that same
  cycle** (12.8% carried) — so the lineage is **re-derived, not carried**. This corrects
  an earlier reading of mine that called the identical sets "carried forward"; the
  link-state measurement is the discriminating evidence.

**The engine's survival rule is asymmetric across layers**, and this is the fact the
design rests on: `_natural_selection` (`sleep.py:1752-1802`) decays and prunes **Layer 1
only** — `_candidate_key` returns `""` for every other type — so Layer 1 survives only
if current experience keeps producing its content key, while Layers 2–4 are never
decayed and persist as rows with re-derived edges. **"Persistent reconstruction" is
accurate for Layer 1 and misleading for the rest.**

**The trace shows the present lineage, not the historical one**: a candidate's identity
is a content hash that does **not** include the parent set, and parents are recomputed
each cycle, so the same content identity can carry a different lineage later.

**The design:** six cells (parent {removed, not} × source experiences {removed, not} ×
removal applied to the **observer** or the **organism**, because removing a parent from
the auditor's reconstruction tests the trace and removing it from the organism's state
tests the maintenance mechanism). **Q1 (internal persistence) and Q2 (external
provenance) scored separately.** Three outcomes tracked separately and per cycle, so a
crossover is detectable. **The sharpest prediction is computed from the source, not
fitted**: pruning after `⌈log(0.15/c)/log(0.8)⌉` cycles — 4 from c=0.3, 6 from c=0.5. And
the decisive control is a **replay learner** that stores episodes verbatim and
regenerates nothing: if continuity is reconstruction rather than recall, perfect recall
is the *harder* baseline.

Added `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md`; manual §8.16 and finding 22;
facts sheet §AA20–§AA22; journal §48; AGENTS.md rule 22.

### Added — A3: the ancestry measurement, and a correction it forced on the specification

**A3 is met.** An ancestry auditor walks each cycle's reported structures' parent
chains against the engine's own cognition window and classifies every branch
that fails to resolve. **Lineage reachability 1.000** (8,061 of 8,061
structures resolve back to Layer 1 within depth 7), **evidence linkage 1.000**
(1,412 of 1,412 claims resolve to event ids with a world/self split), **zero
honesty errors**, and an empty structure-level truncation split — while the
branch-level count shows **105 aged-out branches**, because every structure
resolves through at least one branch still inside the window. The stress arm
(3,240 structures) and the forced-tie arm (3,988 structures) both return 1.000.

**The correction.** Spec §12 said the window was "the more likely binding
constraint", because it spans only 1.7 cycles. **That was wrong.** Surviving
candidates are re-stored every cycle, so a live ancestor stays in the window
however old it is — **a lineage's depth is bounded by the death of an ancestor,
not by the window's recency.** Measured: the window holds 3,998 candidates, the
oldest last stored 1 cycle ago, content spanning 2 cycles. The correction is
recorded in place, not quietly fixed.

**The answer to A3's key question.** The observer's limit and the architecture's
limit are the same limit: **the engine's cognition window IS its memory.** An
investigator cannot recover more developmental history than Organica retains,
because there is no more to recover. That is good news for the trace and a hard
ceiling on the project's distinguishing property.

**Two sweeps prove the truncation categories are reachable rather than inert:**
the window sweep falls from 1.000 at the engine's window to 0.000 at 25–50
candidates (68 aged out); the depth sweep falls from 1.000 at depth 7 to 0.221
at depth 1 (53 depth-truncated) — so **the engine's depth limit of 7 is not
binding; the chains are shorter than it.**

**Two defects the build caught in itself**, both found by the checks rather than
by inspection: the observer matched `sleep:meta_concept` with a prefix test
that excluded every meta candidate (the engine uses an exact comparison), which
produced spurious "missing record" verdicts; and the window sweep sliced the
wrong end of a newest-first list. Both fixed, and the ordering is now pinned by
a test.

Added `A3_ancestry_honesty` to the probe's artifact; spec §13 and the §12
correction; manual §8.15 and finding 21; facts sheet §AA18–§AA19; journal §47;
AGENTS.md rule 21; `tests/test_audit_ancestry.py` (7 tests, four of them
proof-of-firing).

### Fixed — a threshold that judged its own data, and a window span that was wrong by an order of magnitude

**The transfer rule's reference rate is now frozen.** The third condition read
*"no higher than the run's baseline rate"* — circular, because a threshold
computed on the same data it judges relaxes whenever that run's beliefs happen
to be unusually self-sourced. The reference rate is now **17.9%**, fixed from
the calibration probe, **not recomputed on the evaluated run**, re-calibratable
only on data that is not being judged, and labeled a **provisional calibration
value, not a precise universal cutoff** (one run, one world, one policy).

**The window span was wrong by more than an order of magnitude, and is now
measured.** This project asserted the 4,000-event cognition window spanned
"roughly 40–130 cycles". That was a guess. **Measured: the engine stores 2,374.68 sleep events per
cycle, so the window spans 1.7 cycles.** The correction is recorded rather than quietly fixed. A lineage that keeps
being produced stays inside the window (candidates are re-stored every cycle);
one that stopped being produced is gone within about 1.7 cycles.

**A3's definition is fixed in advance**, reporting three things separately:
*lineage reachability* (extant structures resolving back to Layer 1 within
depth 7), *evidence linkage* (extant claims whose support resolves to event
ids with a world/self split), and a *truncation split* — **aged out** (a
persistence problem) / **depth-truncated** (a representation problem) / *no
parent* / **missing record** (a data defect). Level 1 (developmental lineage)
and Level 2 (evidential linkage) stay separate: **success in one cannot stand
in for success in the other.**

**And the boundary A3 cannot cross: fidelity is not sufficiency.** Reproducing
the implemented rule — exactly, and under a binding cap — does not establish
that the reconstruction is a uniquely correct account of *why* a belief arose.

Added spec §12; facts sheet §AA14–§AA16; journal §46; AGENTS.md rule 19; the
probe now reports `A7_event_level_attribution.cognition_window`.

**Fixed — seven literal template placeholders in the specification.** `{ties}`,
`{t_dist:,}`, `{t_edges}`, `{t_cycles}`, `{t_a1:,}`, `{t_a2}` (committed in the second
and third review rounds) and `{share:.1f}` (introduced by this round's script and
caught before commit) had shipped inside sentences that assert results. Corrected
in place from the artifacts: 479 tied windows, 2,589 distinct transitions, 241
aggregate edges, 60 cycles, 692 A1 beliefs, 60 A2 cycles, 692 A7 beliefs, 17.9%
reference rate. A placeholder is **silent** — it reads as a sentence in a diff —
so it is now caught by a standing guard — `tests/test_doc_placeholders.py` — rather
than by another careful read. Facts sheet §AA17; journal §46; AGENTS.md rule 20.

### Amendment 3 — the raise-n campaign on the primary axis

The n=10 run produced `H3-L — INCONCLUSIVE`, whose protocol-specified remedy
is *"raise n; conclude nothing"*. The owner took that remedy literally and on
the primary axis: **same sweep, same protocol, same criteria, no edits.**
Seeds per point go **10 → 30** (the original 10 plus 20 new), so the campaign
is a strict **superset** — the 80 original cells are reused, not recomputed,
and 160 new cells are added. Sweep points, independent variable, metrics,
decision interval, the four success criteria, the four terminal outcomes and
the frozen engine are **unchanged**; the secondary arms V2–V5 remain unrun.

**A real defect was found while preparing the run.** The preregistration says
criterion 4 is a *paired* bootstrap over seeds, but the implementation paired
by **position in the records list** — and the records arrive in completion
order, which differs from label to label. Position-pairing therefore paired
unrelated seeds across labels: an unpaired resample wearing the word
"paired" on it. Each label now contributes a `{seed: value}` map and every
label is evaluated on the same drawn set of seeds. **The fix does not change
the n=10 result** — RT 3:1, interval `[5.0, 5.0]`, 10,000/10,000 replicates,
eight alternative bootstrap seeds `INTERIOR`, leave-one-seed-out 3:1 in
10/10, the same four criteria, the same verdict — so the n=10 record is kept
as `docs/phase_l_results_n10.json` / `.ndjson`.

**A new diagnostic: the adjacent paired differences.** The monotone criteria
are evaluated on the **mean** curve and therefore test the **sign** of an
adjacent difference; if the underlying curve is flat at one end of the sweep,
that sign is a coin flip at any n. More seeds settle the **effect size**. So
each adjacent pair now reports its paired difference with a 99% paired
interval. It is a diagnostic only — not a metric, not a criterion, in no
verdict.

**The analysis is committed code.** `benchmarks/phase_l_analyze.py` replaces
the uncommitted scratch script that produced the reported numbers.

Amendment 3 was committed **before the raise-n run existed**. 69 tests pass;
the four instrument audits pass.

### The freeze

**Organica 1 is frozen as of the `v0.9.0` tag.** Not abandoned, and not
"no more commits" — **no more architectural modifications to the engine.**
The engine becomes a fixed reference object: everything afterwards *measures*
it, and nothing afterwards *quietly changes* it.

Frozen: `organica/sleep.py`, `memory.py`, `paths.py`, `streams.py`,
`branch_streams.py`, `scale_streams.py`, `ground_truth_worlds.py`, and the
published result artifacts. Still free: benchmarks, harnesses, all
documentation, the action list, and tests for new instrumentation. The one
boundary rule: nothing may change the **behavior** of the frozen engine.

**The freeze is enforced, not declared.** `tests/test_v1_freeze.py` reads the
frozen files out of the `v0.9.0` tag and compares them against the working
tree, failing and naming the difference if one differs, and skipping honestly
when the tag is not reachable. It was proved to fire by temporarily modifying
a frozen file and watching it fail. See `docs/V1-FREEZE.md`.

### Added — Phase L: Plasticity–Coherence Measurement

Phase L is not a benchmark hunt. Every previous phase asked *"can Organica do
X?"*; this one asks **how much pressure is required for new structure to
displace old structure?**

The protocol is frozen in
[`docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md`](docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md)
and was committed **before any Phase L outcome was generated**.

| | |
|---|---|
| **Hypothesis** | Organica 1 exhibits a measurable coherence–plasticity boundary; revision occurs only after a displacement threshold |
| **Primary axis** | support ratio (late : early), 8 points — the axis the K3 2×2 already located |
| **Secondary axes** | arrival timing, novelty density, belief-cap pressure, contradiction pressure — each swept **one at a time** |
| **Displacement Index** | `late_structure_retained / late_structure_available` |
| **Preservation Index** | `early_structure_retained / early_structure_original` |
| **Revision Threshold** | the pressure at which DI crosses PI — the headline quantity |
| **Success criterion** | a **reproducible displacement curve**, not a win: DI monotone up, PI monotone down, an interior crossing, and a bootstrap interval excluding both endpoints |
| **Terminal outcomes** | four, pre-committed — **none of them authorises a V2** |

The instrument audits are permanent and required. A **discrimination control**
must show that first-seen-wins scores DI ≈ 0 / PI ≈ 1 and last-seen-wins
scores DI ≈ 1 / PI ≈ 0, so the metric can tell "never revises" from
"always revises". An **endpoint ceiling check** must show a perfect model
scoring 1.0 on both indices. A **degeneracy audit** must show the design
itself is live: that every cell has a denominator to measure against, that
the support ratio actually changes the early/late event mix, that the
contradiction arm produces a different world from the plain arm, and that the
density arm actually changes the event count. The campaign does not run if any
of them fails.

**Launch is not run.** The protocol is written, the harness is built and
validated, and the protocol is reviewed before the campaign executes.

### Fixed — four harness defects found by the Phase L pilot

The reduced-scale pilot returned `DI = 0.000` at **every** point of the
support-ratio sweep — a clean-looking negative result that was in fact an
artifact. The support ratio was not varying anything. Four defects, all in
the harness's implementation of the protocol as written:

1. **The late group arrived after the run ended.** The arrival cycle was
   absolute rather than a fraction of the run, so at reduced scale the late
   group never became active and the late structure was never available to
   measure. Arrival is now proportional.
2. **An unmeasurable index was reported as `0.0`.** A ratio with a zero
   denominator was reported as "nothing was retained" for conditions in which
   nothing was available to retain. Undefined ratios are now `None`,
   excluded from the curve, and counted — never zeroed.
3. **The contradiction arm was a no-op.** It shared a feature of the late
   group with itself, producing a byte-identical world with the arm on and
   off. The shared feature now comes from the early group, so the two groups
   actually compete for the same subject.
4. **The density arm fed the engine only part of the world.** The event
   stream was chunked at a fixed rate while the density arm varies it, so at
   density 4.0 the engine saw 7,200 of 28,800 events while the harness
   reported a complete run. The world's own event rate is now used.

Also corrected: the Revision Threshold bootstrap was resampling the DI−PI gap
rather than the **crossing location** that criterion 4 is about, and was
reporting a min/max rather than the preregistered percentile interval. Seeds
are now resampled paired across labels, and "excludes both endpoints" is
tested directly against the sweep.

Recorded as **Amendment 1** in the preregistration, made before any Phase L
outcome existed. No hypothesis, variable, metric, baseline, success criterion
or terminal outcome was changed, and no gate was relaxed — one audit was
added.

### Changed — the Phase L decision interval is 99%, not 98.33%

The Phase L protocol stated a **98.33%** decision interval and glossed it as
"Bonferroni across the arms". Those disagree: across five arms Bonferroni
gives 0.05/5 = 0.01, i.e. a **99%** interval, while 98.33% corresponds to
0.05/3 — Phase K's correction factor, carried over by accident.

**The owner's ruling, made before any Phase L outcome existed: the intent
governs and the stray percentage is the accidental constant.** The procedure
is preserved and the number is corrected to 99%. Phase K's own 98.33%
figures are unaffected — that protocol had three families and 0.05/3 was
correct there. Recorded as **Amendment 2**.

Amendment 2 also adds a plain statement of what success and failure look
like (preregistration §6.1): success is a stable displacement curve with an
interior, reproducible crossing; failure is a flat DI, a flat PI and no
crossing — a characterization, and a publishable one. **The campaign must be
able to fail.**

### Added — the two preregistered secondary outcomes the harness was missing

The protocol declares three secondary outcomes. The harness computed only
"absolute late incorporation"; **revision latency** and the **knowledge
preservation trajectory** are now computed from a per-cycle DI/PI trace taken
as the engine runs. The trace is per-cycle rather than cumulative, so it
answers *when did the organism start asserting the late structure*; the final
indices are still computed from the last report alone and the trace does not
change them.

### Fixed — a false record in the results file

The results file recorded `"python_hash_seed": "0"` unconditionally, asserting
the pinned value whether or not it was set. It now records the **actual**
value, records whether the pin was met, and warns loudly when it was not.

---

## [0.9.0] — 2026-10-24

**The project question changed: from *can we make a developmental
architecture?* to *what class of problems benefits from one?* Phase K opens
the search for that task.**

### The reasoning

Phases H, I and J were three preregistered attempts to show an external
advantage and all three were negative. That is not the same statement as
*V1 failed*:

> V1 develops interesting internal structure. We do not yet know what
> problem that structure solves.

Three tasks were negative; an infinite number of tasks were not tested. So
**no V2** — the design of a successor architecture cannot be justified while
the advantage it would provide is unknown. Designing V2 first would make V2
guesswork.

### Added — Phase K: Comparative Advantage Search

A **search**, not a test. The question is *what is Organica uniquely good
at?* Three candidate task families, each derived from a mechanism the
project has actually measured, each scored against the strongest simple
baseline that could plausibly solve it.

| Family | Mechanism it targets | The baseline that could beat it |
|---|---|---|
| **K1 — Incremental world modeling** | question generation drives novelty assimilation | online co-occurrence, which won Phase H at 0.8000 vs 0.7041 |
| **K2 — Belief revision** | falsification and contradiction drive revision | change-point detection plus wholesale relearning, with a forgetting window |
| **K3 — Longitudinal knowledge integration** | dreams integrate beliefs into coherent structure (P4, SUPPORTED) | sliding-window co-occurrence, which must trade retention against acquisition |

The protocol is frozen in [`docs/PHASE-K-PREREGISTRATION.md`](docs/PHASE-K-PREREGISTRATION.md)
and was committed **before any Phase K outcome was generated**. Three things
in it keep the phase honest:

1. **The baselines get the tuning advantage.** Every simple baseline is swept
   over a declared grid and its *best* score is the number used. A strawman
   baseline is the most likely way to manufacture a false positive, and it is
   impossible by construction.
2. **The harness is validated before the campaign runs.** The Phase H
   held-out task is rerun through the same code, where Organica's loss is
   already known (0.412605 vs 0.504039). If the harness reports a win
   there, the campaign does not run.
3. **"No family confirmed" is a pre-committed terminal outcome.** Three more
   families ruled out is a publishable result, and it does not authorise a
   V2.

Decision rule: paired percentile bootstrap over ten seeds, **98.33%**
interval (Bonferroni across the three families), SUPPORTED only when the
interval for Organica − best simple baseline lies wholly above zero.
Attribution — whether the hypothesised mechanism is actually implicated — is
reported from a matched within-architecture ablation and is kept separate
from the success criterion.

**The pilot, disclosed.** The harness was run once at one seed and one tenth
of every cycle count before the protocol was frozen. Organica was behind the
baseline in all three families. That is one seed at ten per cent of the
protocol and it is **not evidence**; it is recorded in the preregistration
so it cannot later be mistaken for a result.

### The result — the search failed, and that was pre-committed

The campaign ran to completion: **ten seeds per family**, thirty in total. All
three families came back **REVERSED**.

| Family | Organica | Best simple baseline | Paired difference | 98.33% interval | Verdict |
|---|---|---|---|---|---|
| K1 — incremental world modeling | 0.5923 | 0.9360 | −0.3437 | [−0.3773, −0.3123] | **REVERSED** |
| K2 — belief revision | 0.4111 | 0.9846 | −0.5735 | [−0.6162, −0.5309] | **REVERSED** |
| K3 — longitudinal integration | 0.0000 | 0.8578 | −0.8578 | [−0.8598, −0.8571] | **REVERSED** |

No family is SUPPORTED and none is INCONCLUSIVE: every decision interval lies
wholly below zero, so these are clean losses rather than ambiguous ones. Every
verdict survives eight different bootstrap seeds and both leave-one-out
checks. The **H2** terminal outcome fired exactly as written down before the
run: three more task families are ruled out, the negative-results map grows,
and **no V2 is designed**.

**The ablations came back empty — a negative attribution.** `NO_QUESTIONS`
(K1) −0.0095 [−0.0328, +0.0140]; `NO_FALSIFICATION` (K2) +0.0241 [−0.0048,
+0.0495]; `NO_DREAMS` (K3) +0.0000 [0.0000, 0.0000]. All three intervals
contain zero, so the three mechanisms the families were built around are not
load-bearing for the tasks they were meant to carry. This is within one
implementation on synthetic worlds, and it does not say the mechanisms are
inert in general.

**The K3 zero was root-caused, not assumed.** Organica scored exactly 0.000
on late incorporation on all ten seeds while a trivial co-occurrence counter
reached 0.857, so three artifacts were checked — each capable of failing.
The late structure appears in **zero of 150 cycles**, so it is not an artifact
of reading only the final cycle. Every candidate type except `anomaly` mentions
**zero of 12** late tags, so no late structure was left unread by the edge
extractor. And a 2×2 control across five seeds shows the late group is
incorporated **only when it is strictly stronger** than the group that arrived
first — so the exclusion is a salience/priority competition under a bounded
belief pool, not a blanket inability to learn late structure. This is the risk
§6 of the preregistration named before the run.

### Added
- **Change-to-failure map.** `docs/ENGINE-CHANGE-FAILURE-MAP.md` is generated from `docs/engine_change_failure_map.json`, one row per post-freeze change group with a mechanism, a falsifier, observables and two differing decisions; rows with no failure and rows whose two outcomes agree are excluded by the validator, and commit coverage is recomputed from git.
- **The engine is pinned by per-file hash.** `docs/engine_pin.json` records a SHA-256 for every module under `organica/` with its version, and `python -m benchmarks.engine_pin --check` fails when one is added, removed or changed -- distinguishing a move without a version bump from a pin that a bump has outdated -- with the check also run from `tests/test_engine_pin.py`.
- **The published test count is generated from a real suite run.** `benchmarks/test_count.py` runs the suite, records the result in `docs/test_count.json` and writes one marked region of `AGENTS.md` and the manual; `--check` fails when a document disagrees with the record or the record with a fresh collection, so a new test cannot leave a stale count behind.
- **`--check` is now a complete pre-commit gate.** `python -m benchmarks.research_registry --check` fails when `docs/RESEARCH-QUESTION-REGISTRY.md` no longer matches a fresh render, and `python -m benchmarks.research_accountability --check` checks its three pages plus the registry page; neither writes while checking, so the gate cannot repair the document it is judging.
- **Research accountability system.** `docs/research_question_registry.json` now records an outcome per question, independent of status, and every public claim lives in `docs/claim_ledger.json`; `benchmarks/research_accountability.py` generates `docs/CLAIM-LEDGER.md`, `docs/RESEARCH-DASHBOARD.md` and `docs/RESEARCH-FINDINGS.md` from the two records and fails on a load-bearing claim that cites a closed but unsupported question, a claim with no scope limitation, a withdrawn claim with no reason, or a stale page.

- `docs/V1-SYNTHESIS.md` — **the formal synthesis of V1.** What the project established, what it did not, the distinction between the two goals it could serve, the danger of reading six negative task families as a verdict rather than a map, and the question the evidence leaves open: *what properties must a developmental intelligence have to remain adaptable without losing coherence?* It adds no new evidence — it is a reading of the record, and every claim in it cites a committed artifact.
- `docs/phase_k_results.md` — the Phase K write-up: results, robustness, the
  K3 root cause, and what it changes.
- `docs/phase_k_results.json` — the campaign artifact: protocol block, the K0
  control, the ceiling check, all thirty per-seed records with every model's
  score and configuration, and the per-family summaries.
- `docs/phase_k_results.ndjson` — the live recording, one line per completed
  seed, appended and flushed.
- `benchmarks/phase_k_diagnose.py` — the K3 root-cause diagnostics: the
  per-cycle check, the under-read check, and the arrival-order × strength 2×2
  control.

### Changed

- The package version is **0.9.0**, cut on master; **0.8.0 is the latest
  release**. 0.8.0 was a research-integrity release: corrected clone
  verification, corrected version/tag semantics, the missing campaign
  artifacts regenerated, the cycle-1 fixation claim corrected (journal
  §31), the negative external-validity results recorded, and the
  documentation synchronised with the measurements.
- Journal §32 records the strategic shift and the negative-results map;
  **§33 records the Phase K result**, its robustness, and the K3 root cause.
- Facts sheet **§T** records the result in the one-fact-per-line form.
- The manual's status row for Phase K, its command list, its file map and its
  revision log are updated in the same turn as the change they describe.

---

## [0.8.0] — 2026-10-24

**The external-validity arc: three preregistered campaigns asking whether
Organica's structure buys anything over trivial baselines. The honest
answer recorded here is negative.**

Full detail in research journal §24–§30 and in
`docs/PHASE-H-PREREGISTRATION.md`, `docs/REGIME-SHIFT-PREREGISTRATION.md`,
`docs/PHASE-J-ADAPTATION-PREREGISTRATION.md`.

### Corrected — the structural plateau is dominant, not perfect

**0.7.0 said "the structure is decided on cycle 1" and that every colony
"holds that configuration for 2,999 cycles". The first half is right; the
second was an overstatement, and it is corrected here.**

Regenerating the Tier-1 artifact to produce `docs/discovery.json` meant
checking every published claim against the regenerated file. Measured cycle by
cycle:

| Colony | cycles at 18 beliefs / 7 subjects | of the tail half | last excursion |
|---|---:|---:|---:|
| FULL | 2,964 / 2,999 (98.8%) | 100% | cycle 212 |
| SALIENCE | 2,984 / 2,999 (99.5%) | 100% | cycle 221 |
| NO_CONTRADICTIONS | 2,957 / 2,999 (98.6%) | 100% | cycle 163 |
| **NO_QUESTIONS** | **2,277 / 2,999 (75.9%)** | **95.1%** | **cycle 2,738** |
| NO_DREAMS | 2,984 / 2,999 (99.5%) | 100% | cycle 185 |
| ANTI_EIG | 2,943 / 2,999 (98.1%) | 100% | cycle 539 |

The **retained** belief count is exactly 15 in every one of the 2,999 cycles of
every colony. The **pre-retention pool** is modal, not constant: it dips to 16
beliefs over 6 competing subjects and returns. The excursions are brief — 1–17
cycles in five arms, all over by cycle 539 — and they are real substrate
states, not a recording artifact.

**No launch gate is affected.** G-CS, G-P1, G-SUP and G-EXP hold in 100% of
cycles in all six colonies and G-SUS is 100% in every tail half, re-verified
from the regenerated artifact. G-P1/G-SUP need the pool to *exceed* 15, and 16
does. The verdicts, the noise floor, the inventory totals and the +10,776%
support growth stand as published.

The exception is the interesting part: **`NO_QUESTIONS` is also the arm that
discovers the most** (112 items; 95% of them by cycle 977, 99% by cycle 2,167)
and the only arm still finding new items deep into the run. The five arms
whose structure stops moving are the five that stop discovering; the one arm
that kept discovering kept moving. One arm in one run — a correlation, not a
cause — but it points the same way as H24.

Full record: journal §31, facts sheet §S, `docs/FORCE-MATRIX-RESULTS.md` §2.

### The position this leaves

**No external-validity task tested has produced a win for Organica.** Being
precise about what that means:

- **Held-out prediction** — beaten by both baselines (0.4126 against 0.5040
  and 0.4851).
- **Structure recovery** — beats the temporal-transition-graph baseline in
  the clean and overlapping worlds, **loses to it in the stress world**, and
  loses to plain same-event co-occurrence in all three.
- **Regime-shift detection** — no family met its preregistered success rule;
  the cause-mixture comparison was inconclusive.
- **Post-shift adaptation** — both gates failed in both families, against
  baselines with far lower predictive loss.

That is not the same statement as *the architecture has been shown useless*.
These tasks score next-event prediction, detection delay, structure recovery
and adaptation cost, and none of them is what the eight-layer engine was
designed to win. But it is the honest reading of the evidence so far, and it
is recorded **before** any redesign rather than after one.

### Added — Phase H: external validity (preregistered)

Held-out next-event prediction, F1 on known training tags:

| Model | F1 |
|---|---|
| Organica (Generation-1 prediction candidates) | **0.4126** |
| First-order Markov | **0.5040** |
| Decayed temporal association | **0.4851** |

**Disclosure:** the prediction curriculum is deterministic and identical across
seeds, so Organica's F1 is exactly 0.4126 and the Markov baseline's exactly
0.5040 in all ten seeds. The intervals there are degenerate, and they are
reported as degenerate rather than smoothed into significance.

Structure recovery against hidden cause-pair ground truth, mean F1 over the
ten seeds (range in brackets):

| World | Organica | Same-event co-occurrence | Temporal transition graph |
|---|---|---|---|
| clean | **0.7041** [0.667–0.750] | 0.8000 | 0.1482 |
| overlapping | **0.5469** [0.449–0.628] | 0.7642 | 0.2199 |
| stress | **0.1091** [0.097–0.159] | 0.7959 | 0.2803 |

Organica beats the temporal-graph baseline in the clean and overlapping
worlds and **loses to it in the stress world** — 0.1091 against 0.2803. It
loses to plain same-event co-occurrence in all three. The league is a
three-level stress test, and Organica degrades faster than either baseline
does.

### Added — Phase I: preregistered regime-shift detection

No primary success rule was met in either generator family.

- **cause-mix** — Organica's mean detection delay was **2.55** cycles,
  against **2.80** for the Markov baseline and **4.25** for decayed
  association. The paired advantage for the Markov baseline is 0.25
  cycles, 97.5% CI **[−0.25, 0.75]** — inconclusive. Organica's
  false-alarm rate is **0.0**.
- **mapping-swap** — the baselines are **faster** (Markov **1.25**,
  decayed **1.20**, against Organica **2.65**), and their **15%**
  false-alarm rate breaks the 10% gate while Organica's is **0%**. The
  benchmark is flagged invalid for this family, and the comparison is
  reported with that caveat attached.

### Added — Phase J: gradual post-shift adaptation

Both gates failed in both families.

| Family | Organica adaptation cost | Markov | Decayed |
|---|---|---|---|
| cause-mix | **2.497** | 0.178 | 0.122 |
| mapping-mix | **2.727** | 0.442 | 0.276 |

Final-stable NLL gap: **+4.478** / **+4.500** (cause-mix) and **+3.617** /
**+3.796** (mapping-mix). A clean negative result.

### Added — extended burst horizons, and the scaffold ladder

The burst curriculum was carried to longer horizons:

| Horizon | Baseline inventory | Burst inventory | Bursts delivered | Assimilation efficiency |
|---|---|---|---|---|
| 600 cycles | 91 | **119** | 19 | 1.474 |
| 1,200 cycles | 91 | **128** | 39 | 0.949 |

**Assimilation efficiency decays** — 2.44 → 1.474 → 0.949 items per burst —
so the mechanism's yield falls as the run lengthens even while the
cumulative total still climbs. At 1,200 cycles the burst arm added 8 items
between cycles 601 and 1200 and 2 in its final 100 cycles, reaching 128
against a preregistered 140+ progressive-expansion band. Neither unbounded
expansion nor a stable attractor is established; the reading is recorded as
*intermediate*.

The 300-cycle scaffold ladder, at 91 for the repeating baseline, gives 94 /
93 / 95 for the slow / medium / fast scaffold variants over 24 / 51 / 186
distinct event strings — scaffolding holds the inventory roughly flat
where uniform scaling collapses it.

### Changed

- **The live study is PAUSED** at the owner's direction, after continuous-run
  cycle 1032 (global `sleep_cycle` 5396). The pause marker is in the
  append-only log, the `INTERVAL` override was removed, and there is no
  scheduled restart. The organism did not experience the missing wall-clock
  time, and the write-up says so.
- The package version is **0.8.0**, and this release is the one that
  carries it. Master had drifted past the `v0.7.0` tag while still
  declaring 0.7.0, so the version number was naming a release that master
  was not.

### Fixed

- `tests/test_versioning.py` failed in a **fresh clone**. `clone_check.py`
  clones with `--depth 1`, which fetches only the tags pointing at the
  commit it fetched, so a release tag on an ancestor commit was absent
  locally and the test asserted against an empty tag list. The check now
  consults the remote when the checkout is shallow, and a full checkout
  with no tag still fails exactly as before.
- The version test now also fails when the version describes a commit the
  tag does not cover, which is the drift that let master sit past
  `v0.7.0` while still claiming 0.7.0.
- The local `master` branch had not actually been advanced past the
  overnight merges: a fast-forward had landed on a since-deleted PR branch
  instead, leaving `master` 13 commits behind its remote while the working
  tree still looked current. `master` is fast-forwarded and the three
  orphaned branches are gone.

### Known limitations

- Phase H's **prediction** scores are identical across all ten seeds, because
  the curriculum is deterministic; those intervals carry no information about
  seed variance. The **recovery** task does vary across seeds, and Organica's
  recovery F1 falls to 0.1091 in the stress world, below the temporal-graph
  baseline's 0.2803.
- Phase I and Phase J generalize only to their two predefined synthetic
  generator families, and Phase J's settling time is self-referenced to
  each model's own final stable loss, so it is descriptive, not
  confirmatory.
- Phase I's mapping-swap family has an **invalid benchmark** — the
  baselines' false-alarm rate is above the gate.
- The live study is paused and no restart is scheduled.

---

## [0.7.0] — 2026-10-23

**Ablation Study 2 — the Tier-1 matrix ran, and what it actually measured.**

18,000 colony-cycles: six colonies × 3,000 cycles, on the fixed substrate,
under a protocol whose metrics, gates, noise floor and sensitivity were all
fixed and committed *before* the run. The results are a scientific finding in
their own right and are published in `docs/FORCE-MATRIX-RESULTS.md` and
journal §23.

### The headline

**The structure is decided on cycle 1.** Every colony reaches 18
pre-retention beliefs, 7 competing subjects and 15 retained beliefs on the
first cycle and holds that configuration for 2,999 cycles, while mean support
grows **+10,776%**. All six arms converge to the *same* attractor despite
six different interventions. Structure flat, evidence growing by three orders
of magnitude.

> *Corrected in 0.8.0 — journal §31. "Holds that configuration for 2,999
> cycles" was an overstatement: the retained belief count is exactly 15 in
> every cycle, but the pre-retention pool is modal rather than constant
> (98.1–99.5% of cycles for five arms, 75.9% for `NO_QUESTIONS`). No launch
> gate, verdict, inventory total or noise-floor number changes.*

### The verdicts

**2 SUPPORTED · 3 REVERSED · 0 UNSUPPORTED · 0 NOT INTERPRETABLE**

| # | Prediction | Verdict |
|---|---|---|
| P1 | Retention policy affects development | **SUPPORTED** (M7: 212 vs 2,990 cycles) |
| P2 | Contradiction is developmental fuel | **REVERSED** — removing it *raises* development |
| P3 | Curiosity needs explicit questions | **REVERSED** — removing questions *raises* development |
| P4 | Dreams contribute to trajectory | **SUPPORTED** — removing them lowers it |
| P5 | EIG is orthogonal to development | **REVERSED** — lowest-EIG develops *more* than highest-EIG |

The verdicts are **direction-aware**. A naive "did the metric move?" test
would have scored all five as confirmed.

### A metric that was not a metric

M5 ("development velocity") is `new items ÷ run length`. The reference arm
discovered **74** items over 300 cycles and **74** over 3,000; the rate fell
from 24.667 to 2.467 because the numerator stopped growing. Every colony
discovered **zero** new items in its final 100 cycles. The inventory, broken
down by category, is the interpretable number: FULL 74 (16 beliefs, 11
questions, 36 dreams, 11 experiments) · SALIENCE 78 · NO_CONTRADICTIONS 79 ·
NO_QUESTIONS 112 · NO_DREAMS 44 · ANTI_EIG 85.

### A confound, disclosed

The stimulus **repeats every 9 cycles** — 9 distinct events over 7 distinct
words, seen 333 times. A repertoire cannot grow in a world that does not
change, so the plateau is consistent with *the organism exhausted the
environment*, which is not the same statement as *the organism cannot
develop*. The campaign cannot separate the two.

### The hypothesis this produced

**H24: Organica's apparent developmental plateau is primarily constrained by
environmental information content rather than by architectural inability to
reorganise.** Stated with the evidence on both sides and its falsification
criteria before the experiment that tests it. The next experiment is a
**world-complexity ladder** — a stimulus change, not an architecture change.

### The World-Scale Ladder & Burst Assimilation Findings (2026-10-23)

Immediate experimental testing of H24 during the 0.7.0 cycle revealed three
successive mechanistic insights that redefined the developmental narrative:

1. **Uniform scaling causes dilution collapse**: Multiplying distinct world
   triangles by 16× (3 → 12 → 48) collapsed inventory (91 → 66 → 56) and
   theories (10 → 4) due to frequency dilution in the `MAX_PREDICTIONS = 20`
   window.
2. **Scaffolding prevents collapse**: Maintaining a 3-triangle core scaffold
   prevented multi-layer degradation, preserving theories at 13–14 and
   stabilizing beliefs at 18.
3. **Burst reinforcement enables developmental assimilation**: Novelty requires
   local reinforcement to survive early-stage filters (`PREDICTION_MIN_COUNT = 5`,
   `STABLE_THRESHOLD = 0.3`). Introducing novelty in concentrated bursts
   drove cumulative inventory to **113 items (+24.2%)** across 300 cycles, with
   active discoveries continuing through epochs 2–5 (88, 10, 7, 2, 6, 0).
4. **Conclusion frozen**: *Organica's developmental capacity is not a fixed
   architectural constant. It is strongly dependent on the structure and
   presentation schedule of novelty.* Prior candidate ceilings (74, 91) were
   constrained measurements of environmental bottlenecks rather than hard
   architectural limits.

### Added

- `docs/FORCE-MATRIX-RESULTS.md` — the results, the verdicts, what the
  campaign can and cannot answer, and H24.
- `benchmarks/run_matrix.py` — the campaign launcher. Runs the G1
  verification once, launches the six colonies in parallel with the **same**
  `PYTHONHASHSEED=0`, and records the hash seed, git commit and wall clock
  in the artifact.
- `benchmarks/verdicts.py` — every pre-registered prediction forced into
  SUPPORTED / UNSUPPORTED / REVERSED / NOT INTERPRETABLE, direction-aware.
- `benchmarks/discovery_report.py` — the inventory breakdown and the
  cumulative discovery curves, plus the stimulus's own measured periodicity.
- `benchmarks/process_noise.py` — the process-level noise floor, with a
  parallel sweep and the scale-invariant item-count form.
- `organica/scale_streams.py` — worlds of increasing information content for
  the H24 ladder.
- `benchmarks/scale_ladder.py` — the ladder runner.
- `benchmarks/hub_degree_probe.py` — measures the Layer-1 survival threshold
  against hub degree.
- `docs/force_matrix.json`, `docs/discovery.json`, `docs/verdicts.json`,
  `docs/process_noise_3000.json`, `docs/figure_tier1_matrix.svg`,
  `docs/figure_discovery.svg`.
- Facts sheet §I (matrix results) and §J (H24).
- `docs/ORGANICA-V2-DESIGN-NOTES.md` §7–§10 rewritten with the matrix's
  answers and the new stimulus requirement.

### Changed

- `benchmarks/force_matrix.py` now records the per-cycle **discovery
  history** — new items and cumulative distinct items per category — so the
  inventory can be measured directly rather than inferred from a rate.
- `benchmarks/metric_sensitivity.py` gains the per-metric most-sensitive-
  colony ranking and a **downstream** deviation ranking that excludes each
  colony's own intervention metric.
- `benchmarks/v1_impact.py` excludes `None` metrics rather than zeroing
  them. The harness reports "n/a" for lineage completeness when a condition
  has no lineage; that is *not measurable*, not zero, and zeroing it would
  have been the same class of error as the scope defect the tool documents.
- The README now carries the research findings, the verdicts, and H24.

### Fixed

- `benchmarks/seed_noise.py` overclaimed: it measures the **within-process**
  seed floor (exactly 0.00), not the floor that binds. Disclosed in place.
- `benchmarks/figure_campaign.py` failed with a raw `KeyError` on an
  artifact predating the per-cycle series capture; it now says so.
- `benchmarks/run_matrix.py` and `force_matrix.py` print the G1 header even
  when verification is skipped.
- `organica/scale_streams.py` numbered its leaf tags (`ta0`), and the engine
  only extracts words of **four or more letters** — every leaf was silently
  invisible and the ladder measured nothing. The leaves are now spelled in
  letters.

### Known limitations

- The stimulus's 9-cycle period means the campaign cannot separate
  "exhausted the environment" from "cannot reorganise". H24 is untested.
- M7's spread rests on very few observations: the reference arm's
  212-cycle mean is the mean of **one** belief death. Reported as such.
- `NO_CONTRADICTIONS` removes contradiction's **weight in the confidence
  formula**, not contradictions. M3 is near-invariant for it by
  construction. The colony's name overstates the intervention; disclosed in
  the results document and the facts sheet.

---

## [0.6.0] — 2026-10-23

> **0.6.0 is the first release of this repository to carry a git tag.**
> The versions below were published to this repository without tags, so they
> are recorded here as history but cannot be checked out as named commits.
> The tag convention starts here: releases are tagged `v<version>`, and
> `tests/test_versioning.py` fails the build if the version has no tag.

**Milestone M0.5 — mechanism closure, and a substrate correction.**

This release changes the organism's behavior. It is a pre-1.0 release
because the public API is not stable, but the behavioral change is
real and is disclosed in full in `research-journal/phase_g_findings_20261021.md`
§21.8 and `docs/USER-MANUAL.md` §8.4.

### Changed — substrate

- **The tag-frequency counter is now scoped to world events.** It was
  maintained over every stored event, including the organism's own sleep
  payloads, while the co-occurrence and temporal graphs it normalises are
  built from world events only. The counter is the *denominator* of the
  Layer-1 edge strength (`ratio = count / source_freq`), so the two sides
  of the ratio measured different populations and the survival filter
  discarded the world's own structure. Measured: 4 surviving edges, 0
  processes, 0 workflows, 0 beliefs.
- A `meta` table records the scope the counters were built with, so a
  database written by an older build rebuilds its counter exactly once
  instead of mixing two populations in one table.

### Added

- `docs/FORCE-MATRIX-PREREGISTRATION.md` — M1–M9 frozen, plus the launch
  gates G-CS, G-P1, G-SUP, G-EXP and G-SUS.
- `docs/ORGANICA-V2-DESIGN-NOTES.md` — planning only: what survived
  scrutiny, what failed, what turned out inert, what turned out essential,
  what became a bottleneck, and the open questions.
- `docs/gate_validation.json`, `docs/mbsd_census.json`,
  `docs/mbsd_census_postfix.json`, `docs/gate_check.json`,
  `docs/freq_scope_probe.json`, `docs/metric_sensitivity.json`,
  `docs/force_matrix_pilot.json`.
- `organica/branch_streams.py` — branch-structured stimuli built from
  triangles, derived from the measured mechanism.
- Benchmarks: `gate_validation.py`, `mbsd_census.py`, `branch_sweep.py`,
  `branch_sweep2.py`, `branch_diag.py`, `branch_diag2.py`,
  `freq_scope_probe.py`, `gate_check.py`, `force_matrix.py`,
  `metric_sensitivity.py`, `seed_noise.py`, `v1_impact.py`,
  `figure_campaign.py`.
- `tests/test_substrate_equivalence.py` — a scope-consistency regression
  test: a sleep payload must change neither the temporal graph nor the
  frequency counter that normalises it.
- `tests/test_versioning.py` — the version declarations must agree, must
  be SemVer 2, must be pre-1.0, and must have a git tag and a changelog
  entry.
- `run_continuous.py` writes `freq_scope=world` in its build marker, so
  the append-only log says which substrate produced which cycles.

### Changed — research findings

- **The proposed Multi-Belief Subject Density gate is structural, not
  predictive.** Layer 5 forms exactly one theory per subject holding ≥ 2
  beliefs; the identity `theories == min(competing_subjects, MAX_THEORIES)`
  holds in 100% of cycles in 9 of the 11 conditions. The gate is restated
  as an absolute count.
- **The `r=4 / r=6 / r=10` "phase transition" was an instrumentation
  artifact.** With the counter scoped correctly, all three repeat counts
  behave identically: a full prediction window, a belief pool of 18, seven
  competing subjects, and 100% of tail cycles passing every gate.
- **"No Falsification freezes the organism" is withdrawn.** Post-fix it is
  the best-supplied condition in the study: 18 beliefs, 6 of 6 subjects
  competing, MBSD 1.000.
- **"The organism is supply-limited, not selection-limited" is withdrawn as
  a general statement.** It was true of the study stream on the old
  substrate; on a branch-structured stimulus the cap binds and the
  retention policy changes the population.
- Facts sheet D8b is **corrected in place**; D8c–D8e are added.

### Fixed

- The G1–G4 perturbation ladder caught a measurement reading the wrong
  report attribute and reporting a working layer as dead (previously
  corrected, recorded here for the release history).
- The campaign runner instantiated the instrument instead of the colony
  subclass, which made every colony run the default service and produced
  a byte-identical FULL and SALIENCE. The runner now asserts G1 — that
  each colony's intervention is in the code path — before running a
  colony.

### Known limitations

- The ablation study in `docs/ablation_study.json` was produced on the
  **pre-fix** substrate. Every condition ran on the same substrate, so
  the comparisons stand, but the absolute densities are not comparable to
  post-fix numbers. `benchmarks/v1_impact.py` produces the before/after
  audit (`docs/v1_impact.json`).
- One seed per colony. Deltas smaller than the measured seed-noise floor
  are reported as *not interpretable*. The floor is measured by
  `benchmarks/seed_noise.py`.

---

## 0.5.0 — 2026-10-21

- Phase G endurance work: monotonic sleep-cycle counter in the database,
  bounded candidate retention, the tag-frequency counter moved from a
  full-table scan to an incremental counter.
- `docs/USER-MANUAL.md` rewritten with 18 sections.
- `docs/FACTS-SHEET.md` — facts with provenance, separated from assumptions.
- `docs/GATE-BOARD.md` — what is demonstrated versus assumed.
- `benchmarks/clone_check.py` and a passing fresh-clone check.

## 0.4.0 — 2026-10-20

- Observation pipeline repaired; `MemoryService.batch()` added after
  profiling found one fsync per candidate dominated the cycle
  (1,023 commits = 3.0 s of a 4.5 s cycle).
- `benchmarks/cold_start.py` — the eight assistance levels.

## 0.3.0 — 2026-10-20

- The eight-layer engine, the four reproduction domains, the reproduction
  pack and the growth benchmarks.

## 0.2.0 — 2026-10-19

- The study daemon, the append-only log format, and the snapshot writers.

## 0.1.0 — 2026-10-19

- First public release of the substrate and the sleep pipeline.

[0.10.0]: https://github.com/nueraresearch/project-organica/releases/tag/v0.10.0
[0.9.0]: https://github.com/nueraresearch/project-organica/releases/tag/v0.9.0
[0.8.0]: https://github.com/nueraresearch/project-organica/releases/tag/v0.8.0
[0.7.0]: https://github.com/nueraresearch/project-organica/releases/tag/v0.7.0
[0.6.0]: https://github.com/nueraresearch/project-organica/releases/tag/v0.6.0
