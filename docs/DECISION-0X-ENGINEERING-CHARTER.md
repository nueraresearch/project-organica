# Decision: Adopt the 0.x engineering charter

**Date:** 2026-11-14

**Status:** `ADOPTED — IN FORCE`

**Decision ID:** `DECISION-0X-ENGINEERING-CHARTER`

## Decision

The 0.x engineering charter is adopted as the dated engineering boundary for the 0.x line. The adopted document is [0X-ENGINEERING-CHARTER.md](0X-ENGINEERING-CHARTER.md); its Category A–F allowed changes, version and release rules, guard budget, A1 experimental boundary and stop conditions are in force from this date.

This adoption is a planning and engineering decision, not a scientific result. It changes no engine file, package version, pin, canary, seed, cell, threshold, result or verdict.

## Why

The project has a green suite, repaired decision and registry records, working A1 gates and a bounded set of engineering controls. The remaining critical path is whether A1 can produce an admissible target set. The charter keeps 0.x work from silently becoming a V2 redesign, an experiment authorisation or an open-ended guard program, while leaving the A1 target-selection and grant decisions in their proper places.

## Scope

- The charter applies to package versions `0.x.y`; the current build remains **0.15.0 (unreleased)**.
- Category C may build target-selection machinery, the cycle-36 `U` sampler and preflight checks. It may not choose the target values, freeze the manifest, issue a grant or run a cell.
- Category D requires a separate dated decision, version bump, pin and canary record; this adoption does not authorise an engine behavior change.
- V2 remains reserved for a mechanism-driven redesign after M1 and G4. G9 remains locked.
- The charter does not create 0.16.0 or pre-allocate 0.16–0.20.

## What this does not do

It does not freeze or grant A1, select a target, reserve a seed, authorise a cell, change an engine file or create a claim. A1 remains `REGISTERED DESIGN — NOT FROZEN, NOT RUN, NO GRANT`, with no target set and no cell.

## Revisit

The charter is reviewed at the earlier of **2026-12-14**, the A1 disposition's default revisit point, the A1 freeze/grant/run/park decision, or the first Category D proposal. An amendment or withdrawal is a new dated decision; silence does not amend it.

If A1 is parked, the charter remains in force for the remaining 0.x record and publication work. The parked record must name its reason, including **`A1 PARKED — TARGET SET NOT FORMED`**, **`A1 PARKED — NO ADMISSIBLE TARGET RULE`**, **`A1 PARKED — NO GRANT`** or **`A1 PARKED — CAPACITY`**.

## Rejected alternatives

- **Adopt a fixed 0.16–0.20 version schedule.** Rejected: version numbers should describe actual changes, not anticipated milestones.
- **Treat this charter as a scientific decision or an A1 authorisation.** Rejected: it bounds engineering work; it does not select targets, freeze a manifest, issue a grant or produce evidence.
- **Leave the charter as a permanent draft.** Rejected: the owner has adopted it, and a draft cannot bind the work it is meant to bound.
