# 0.x engineering charter — allowed changes and stop conditions

**ID:** `CHARTER-0X-1`  
**Date:** 2026-11-14  
**Status:** `ADOPTED — IN FORCE`  
**Adopted:** 2026-11-14 by [`DECISION-0X-ENGINEERING-CHARTER.md`](DECISION-0X-ENGINEERING-CHARTER.md)  
**Applies to:** package versions `0.x.y`; current build **0.15.0 (unreleased)**

**This is the adopted engineering boundary for the 0.x line, not a research result, a release, a grant or a V2 design.** It does not authorise an engine change, a cell, a seed allocation, a publication or a version bump. It does not select an A1 target, freeze the manifest or authorise a run.

## 1. Purpose

The 0.x line is for **understanding and hardening V1 and producing registered evidence about it**. It is not a route to a new architecture.

The boundary follows the adopted V2 reservation in [`ROADMAP.md`](../ROADMAP.md):

- **0.x** may build instrumentation, measurement harnesses, preregistrations, audit records, tests, CI, governance and bounded engineering repairs.
- **V2** is a mechanism-driven architectural redesign, eligible only after **M1** routes a mechanism-bearing branch and **G4** passes. Nothing in 0.x may be called, versioned or scoped as V2.
- **G9** remains locked until X1 and G9-A–D pass, and even then requires a separate design and owner decision.

Engineering work is not evidence. A green suite, a merged guard, a repaired record or a new harness establishes no scientific claim; claims come only from frozen runs and their adjudication.

## 2. Allowed changes

Every 0.x change must fit one of these categories. A change that fits none is out of scope.

| Category | Allowed work | Required proof | Version effect |
| --- | --- | --- | --- |
| **A — Record** | Documentation, decision/registry records, derived pages, manual and changelog repairs | Generated pages match their source; links resolve; no verdict, threshold, seed or frozen artifact re-scored | No bump required; changelog entry still required |
| **B — Test or CI** | A test, validator, guard or workflow step that protects a named failure mode | The check can fail; its self-test proves the failure; no duplicate of an existing guard; failure names the cause | Patch or no bump; no behavior change |
| **C — Instrument or harness** | Benchmark, measurement harness, observer, extractor, target-selection support, preflight or analysis tool | A control or self-test; no engine semantics changed; artifacts stamped and old artifacts preserved; no claim wider than the run | Patch for a repair; minor for a new runnable capability |
| **D — Engine behavior or public API** | A change to what `organica/` computes or exposes | A dated owner decision; a single named variable; version bump; engine pin and canaries re-recorded; equivalence or behavior test; no live or frozen experiment disrupted | Minor (`0.MINOR.0`) |
| **E — Packaging or release** | Version declarations, tag, changelog, citation and deposit metadata | Version describes the commit; suite and pin pass; no unpublished behavior; owner authorises the release | Patch or minor as the change requires |
| **F — Publication** | Paper, deposit or public statement | Every claim traced to a frozen artifact and no wider than its check; separate owner act | No package version change by itself |

Category **C** is the normal home for A1 target selection, U sampling, preflight checks and measurement repairs. It may implement the machinery; it may not choose the target values as an engineering act, freeze the manifest, issue a grant or run a cell.

Category **D** is deliberately narrow. A bug fix that changes behavior is still a behavior change. “The test passes” is not a substitute for the recorded decision, version bump, pin and canary record.

## 3. Forbidden changes

The following are out of scope for 0.x, even when they are small, convenient or green:

- designing, implementing or naming a V2 architecture, mechanism or version;
- implementing Generation 9 self-modelling;
- changing what the engine computes in order to make a result, gate or narrative come out differently;
- changing a precommitted threshold, target set, seed block, endpoint or decision table after its outcome is seen;
- replacing a failed target, seed, cell or gate with a substitute and calling the result the same experiment;
- overwriting a published result artifact or re-scoring a verdict without a new record;
- adding a third-party runtime dependency to the frozen core;
- writing to the live `memory.db` or restarting the live study without an explicit owner decision;
- adding open-ended instrumentation after a block's build has closed;
- adding a guard solely because another guard could be added;
- treating a green suite, a merged guard or a record repair as evidence for a scientific claim;
- declaring a release, tag or publication from an uncommitted or failing tree.

## 4. Version and release boundaries

The package remains **pre-1.0** and follows Semantic Versioning for the 0.x line:

- `0.MINOR.0` is earned by a behavior or public-API change, or by a new runnable experimental capability that changes what the project can measure.
- `0.MINOR.PATCH` is for a defect repair or packaging correction that does not change behavior.
- Documentation, derived records, tests and harness-only repairs do **not** require a version bump; they still require a changelog entry when they change the operational record.
- A version number is not a schedule. **0.16.0 through 0.20.0 are not pre-allocated**; each number is assigned only when its actual change exists.
- A version must describe the commit it is on. A tag is a release act, not an engineering completion marker.
- One release has **one primary objective**. Adjacent cleanup is either part of that objective or deferred; it is not used to inflate a release.

The current build is **0.15.0**, unreleased. No 0.x release may contain both a behavior-changing engine edit and the first run of a new experimental block unless the engine edit is that block's registered subject and the block is frozen separately.

## 5. Change budget and the governance stop

A 0.x change is bounded before it starts. Its proposal must name:

1. the observed defect or scheduled experiment it protects;
2. the check that will show it worked;
3. the stop condition that says “do not continue”;
4. the rollback or preservation rule for any artifact it touches.

The governance budget is deliberately small:

- **One guard per named failure mode.** A second guard for the same failure is a defect, not extra safety.
- **No guard without a protected object.** If no live or scheduled experiment is blocked and no observed failure is unprotected, do not add the guard.
- **No guard-only release after a green suite** unless it closes a named unprotected failure. The next release must close an experiment decision or be explicitly a maintenance release with no new guard.
- **No open-ended instrumentation.** When a block's build closes, the next requirement goes to the wish-list; the block may be fixed if wrong, not extended.
- **No consecutive governance expansion without a decision point.** A second consecutive governance-only change requires an explicit owner decision naming the experiment or failure it protects.

The stop is not “governance is bad.” It is “a guard must buy a decision or prevent a named failure.” When it buys neither, stop and return to the experiment path.

## 6. Experimental boundary

0.x engineering may prepare the A1 intervention; it cannot become the intervention's authorisation.

- Target-selection code, the cycle-36 `U` sampler, preflight invariants and C4 non-target rows are Category C work.
- The actual target set, manifest freeze, seed reservation and owner grant are separate experimental acts.
- A1 has **one registered attempt**. A failed or unmeasurable gate closes it; no 0.x patch, threshold change, target substitution or extra cell may reopen it.
- If fewer than four eligible disjoint targets exist for a seed, **A1 is not run**. No smaller set or substitute edge.
- The A1 disposition lapses to **A1 PARKED** on **2026-12-14** if no target-selection protocol and dated grant decision are recorded. Parking is a program decision, not an engineering failure.
- If A1 is parked, the record must name the condition that fired: **`A1 PARKED — TARGET SET NOT FORMED`** (no four eligible disjoint targets), **`A1 PARKED — NO ADMISSIBLE TARGET RULE`** (the protocol cannot select from information available before cycle 37), **`A1 PARKED — NO GRANT`** (the owner declined or did not decide), or **`A1 PARKED — CAPACITY`** (resources or risk). "No grant by the deadline" may not stand in for a design failure.
- A3 may be designed only around the target M1 routes. M1-X and M1-V route nowhere.
- V2 work may begin only after M1 and G4; G9 remains locked.

## 7. Stop conditions

| Trigger | Required stop |
| --- | --- |
| A change would alter engine behavior but has no Category D decision, version bump, pin and canary record | Stop; do not merge. Return with a registered decision or classify the work as measurement-only. |
| A proposed guard protects no named failure or scheduled experiment | Stop; do not add it. |
| A guard duplicates an existing guard or cannot fail | Stop; fix or remove the duplicate. |
| A block's build has closed and the proposal adds a new feature to it | Stop; record it as a wish-list item for a new block. |
| A threshold, target, seed, endpoint or decision rule would change after an outcome | Stop; the result is not re-scored. A new design is required. |
| A target set has fewer than four disjoint eligible edges | Stop A1; no run, no substitute. |
| A target set fails the four-edge rule or the pre-37 compliance checks | Stop A1 and record **`A1 PARKED — TARGET SET NOT FORMED`** or **`A1 PARKED — NO ADMISSIBLE TARGET RULE`**; do not substitute a target, seed or smaller N. |
| A1 has a defensible target set but no grant by its recorded decision point | Stop and record **`A1 PARKED — NO GRANT`** with a revisit condition; do not keep the manifest in permanent limbo. |
| An engine pin or canary changes without the expected recorded change | Stop the release; restore the pin or record a new Category D decision. |
| The suite is red, the tree is dirty or a version/tag check fails | Stop the release. |
| M1 has not routed a mechanism branch, or G4 has not passed | Stop V2 work; remain 0.x. |
| G9, X1 or G9-A–D has not passed | Stop G9 work; it remains locked. |
| A public claim is wider than its frozen artifact or check | Stop publication; narrow the claim or remove it. |
| The work would write the live database, restart the study or change the frozen engine without a decision | Stop; ask the owner. |

## 8. Review and expiry

This charter is reviewed at the earlier of:

- **2026-12-14**, the A1 disposition's default revisit point; or
- the date A1 is frozen, granted, run or explicitly parked; or
- the first proposal to change engine behavior under Category D.

This charter was adopted on **2026-11-14** under `DECISION-0X-ENGINEERING-CHARTER`. At review the owner records one of: **AMENDED** or **WITHDRAWN**; silence does not amend it.

If A1 is parked, the charter still bounds the remaining 0.x record and publication work; it does not authorise a substitute experiment. If A1 runs, the charter is amended to name the post-run decision point rather than extended by another governance layer.

## 9. What this charter does not do

- It does not bump the package, create 0.16.0 or pre-allocate later versions.
- It does not change an engine file, pin, canary, seed, cell, threshold, result or verdict.
- It does not freeze, grant, park or run A1.
- It does not authorise V2, G9 or a publication.
- It does not turn a green suite into evidence.

**Adopted 2026-11-14:** The 0.x engineering boundary is in force. The current build and all experiment states are unchanged.
