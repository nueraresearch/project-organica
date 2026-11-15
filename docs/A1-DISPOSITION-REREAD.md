# A1 disposition, re-read with C1 removed as a blocker

**Date:** 2026-11-15

**Status:** `RE-READ — ANALYSIS FOR OWNER DECISION; DISPOSITION UNCHANGED; NO RUN AUTHORISED`

**Scope:** this document re-reads an existing decision against a changed factual premise. It is not a new disposition, does not amend [`DECISION-A1-DISPOSITION`](DECISION-A1-DISPOSITION.md), assigns no seed, freezes nothing, authorises no cell and records no result. Its only claim is that the *reason* the disposition was adopted has changed, so the disposition should be re-decided rather than inherited.

## The premise that changed

The park recommendation in the A1 disposition rested, in part, on C1 being unreachable at the registered design. That reading came from a denominator that was never the operative one. Under the adopted convention — protocol denominator authoritative, the 63–64 figure a planning quantity, the recorded cell row operative (`DECISION-A1-C1-DENOMINATOR-1`, owner-confirmed 2026-11-15) — the same measurements read differently (`A1-DESIGN-VIABILITY-1`, reconciled in `90ed636`):

- **directed rows clear the floor**: `2063` reads 70/59/69/58/72/72 at N=4 and 79/64/79/74/72/74 at N=6 against a 95% floor of 60 and 57;
- **relation-level reads do not**: 31–51, clearing nothing.

So "C1 unreachable" was an artefact of reading a relation-level quantity against a directed-row floor. The premise is not merely weakened; under the adopted convention it is **false**. Two consequences follow immediately, and only one of them is comfortable: C1 is no longer the binding constraint, and the disposition was adopted on a factual basis that no longer holds.

## What remains once C1 is removed

Two unresolved items, neither of which is a measurement the project can take before running:

**C2/C8 competence.** As of [`A1-COMPETENCE-FILTER-DRAFT-1`](A1-COMPETENCE-FILTER-DRAFT.md), a competent N=20 block forms on **4 of 6** adopted seeds — one seed impossible by exhaustion, one undecided — so the adjudication contract in [`A1-C2-C8-COMPETENCE-RULE`](A1-C2-C8-COMPETENCE-RULE.md) would return **C8 VOID on the adopted block today**. That is a property of the design and the endpoint cap, not of any treatment.

**C4 exposure burden.** 108 non-target rows per seed at N=4 and 92 at N=20, set by N and the stream, **not by target identity**. The competence filter therefore buys no C4 relief: narrowing which rows are targets does not narrow the neighbour set the no-interference margin is read over.

Note what is *not* on this list. C7 is unchanged and readable; C6 is satisfied; C1 is now readable on directed rows; the manifest, freeze and grant remain separate acts. The disposition's own revisit condition — "the target-selection protocol and per-seed target sets being ready for a freeze review" — is now close to met, which is exactly why the disposition must be re-decided instead of lapsing into the park default by inaction.

## The re-read question, stated as the owner asked it

Assume the C1 floor is reachable. Given only that C2/C8 is unresolved and C4's burden is unresolved, should Path A **continue**, be **redesigned**, or be **parked**?

### Continue

Commit to the preparation path with two recorded limitations: C8 is adjudicated only if the owner also declares the cap or rule change that lets twenty competent rows form on every seed — otherwise C8 is recorded as not adjudicable on this design — and C4's 108-row burden is accepted as the margin's exposure. What it buys: C1, C7 and C4 become measurable on a design that already has arms, gates and a reproducibility path, and C8 stops being an unowned unknown and becomes a recorded limitation.

### Redesign

Change the universe — raise A∩K per seed, or raise tag count so the endpoint cap binds less — and re-derive targets, thresholds and exposure before any run. What it buys: the possibility of all four gates being adjudicable. What it costs: the same work again at a new universe, with no guarantee the cap stops binding, and a new pre-commitment clock.

### Park

Stop A1 and record why. What it buys: honesty about the fact that six weeks of preparation have produced a design whose central gate cannot currently be adjudicated. What it costs: the evidence C1, C7 and C4 could still yield is forgone, and the mechanism-discrimination question stays open with no registered test able to close it.

## Re-read finding, marked as analysis

The disposition's justification was C1-unreachable, and that justification is gone. But replacing it with "C2/C8 unresolved" does not restore the same conclusion, because the two items differ in kind: C1's unreachability was a fact about whether the *experiment* could work, whereas C8's unavailability is a fact about whether *one gate* can be scored — and the experiment's discriminating power does not rest on C8 alone. C1, C7 and C4 remain readable, and C8's absence is a declared limitation rather than a failed manipulation.

On that reading the **continue** branch is the one the evidence supports, conditional on C8 being answered explicitly rather than left ambiguous — either a declared cap/rule change that makes twenty competent rows form on every seed, or a recorded "not adjudicable on this design". Continuing while C8 stays unowned is the one branch this re-read does not support, because it reproduces the failure mode the project has hit repeatedly: an interesting result that cannot be adjudicated against its gate.

**This is analysis, not the decision.** The disposition stays `ADOPTED — COMMITTED TO TARGET RESOLUTION`, its 2026-12-14 lapse clock keeps running, and the choice among the three branches is the owner's.

## Update — 2026-11-15: the C8 condition this re-read named has been satisfied

The finding above made continuing conditional on C8 being answered explicitly. It has been:
[`DECISION-A1-C8-NMIN-1`](DECISION-A1-C8-NMIN.md) sets the floor at 17 competent rows and makes C8
adjudicable on **all six seeds**, so the condition is met and the **continue** branch no longer carries a
C8 carve-out.

What remains of the branch question is therefore only C4's posture. The distinction the re-read drew
still holds — C1's unreachability was about whether the *experiment* could work, C8's unavailability was
about whether *one gate* could be scored — and the second has now been resolved in the design's favour
rather than merely declared. The disposition itself is unchanged and still the owner's to amend; the
lapse clock still runs.

## What the re-read does not do

It does not amend the disposition, does not lift any blocker, does not re-date the lapse clock, does not claim C1 is satisfied (it is readable, which is different from measured), and does not resolve C8 or C4. It records that the disposition's stated basis is no longer true, and sets out what the owner would be choosing between.

## Reproduce

```bash
python -m benchmarks.a1_design_viability --check     # the reconciled C1 reading
python -m benchmarks.a1_competence_filter_draft --check   # the C8 coverage figures
```

Both read committed no-arm artifacts and run no engine.

## Closure

The owner answers the three-branch question and, if the answer is **continue**, answers the five competence questions in the rule draft. This document is then superseded by the amended disposition rather than left standing beside it.
