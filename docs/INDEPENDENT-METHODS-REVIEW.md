# Independent Methods Review — record, brief and rubric

**Status: OPEN. No reviewer has been appointed, no seed has been allocated, and no result from this design
exists.** This document is the brief a reviewer receives and the rubric their assessment is recorded
against. Section 7 is empty because the review has not happened; §7 is filled only by the reviewer.

A review is not a formality and not a letter of support. Its purpose is to let someone outside this project
examine the reasoning and try to break it before any confirmatory seed is opened.

## 1. What is under review

One hypothesis, at **Level 2 (prediction, not causation)**, stated in
[`docs/STRUCTURE-BEHAVIOR-DESIGN.md`](STRUCTURE-BEHAVIOR-DESIGN.md):

> Within one generating configuration, the organism's displacement index at the end of formation predicts
> its prediction score on held-out transitions later in the same run — and that relation persists, weakens,
> disappears, or reverses when the generating configuration changes.

The design measures `DI` over cycles 110–150, scores `revision_held_out` over cycles 250–300 on
transitions withheld from both exposure windows, refuses causal language, and pre-commits four outcomes.

## 2. Who may review, and who may not

**Eligible.** A reviewer who satisfies all five:

1. has not designed the Organica architecture or its measurement instruments;
2. has not selected the historical results used to motivate the hypothesis;
3. has the methodological expertise to challenge the statistical design;
4. has no stake in a positive result;
5. is willing to give a written assessment including objections.

**Not eligible.** The agent that wrote the design record — independence is not a matter of care, it is a
matter of authorship. The project owner may commission and receive the review but cannot stand in for it;
the owner chose the hypothesis, and a reviewer who chose the hypothesis is reviewing their own judgement.
Anyone who wrote `benchmarks/reusable_knowledge.py`, the Phase L index, or the provenance harness is
ineligible for item 2 below, because those instruments are what that item interrogates.

**Declared in the record before the review begins:** affiliation, funding, authorship of any cited work,
and any prior public position on this project. A conflict is not disqualifying; an undeclared one is.

## 3. The five questions, and where the design answers each

| # | Question | Where it is answered | What counts as a defect |
| --- | --- | --- | --- |
| 1 | Is the hypothesis genuinely testable? | §1 states the level; §6 gives the estimand, null and four outcomes | the estimand is undefined for some worlds, or every outcome is compatible with the hypothesis |
| 2 | Are the measurements independent? | §4 pair guard and size baseline; §6 permutation control; §7 shared-instrument limit | `DI` and the outcome share pairs, the size baseline is absent, or the control cannot return a null |
| 3 | Is the held-out design valid? | §4 temporal order, withhold from both windows, measured disjointness | any scored pair appears in formation or revision learning, or `DI` is computed after the outcome |
| 4 | Are the statistical criteria defensible? | §6 null, intervals, permutation; §5 declared deviation and sign-resolution requirement | the threshold is chosen after seeing data, the reference rule is unnamed, or no interval is reported |
| 5 | Can the experiment falsify the hypothesis? | §6 falsifier A, falsifier B, four pre-committed outcomes | no result would count against it, including the sign-flip case |

## 4. What the reviewer receives

| Artifact | Why it is in the package |
| --- | --- |
| `docs/STRUCTURE-BEHAVIOR-DESIGN.md` | the proposal under review: hypothesis, level, predictor, outcome, guards, falsifiers |
| `docs/formation_provenance_study.json` | the one confirmatory structure-to-outcome result, with its arms, interval and gates |
| `docs/FORMATION-PROVENANCE-PREREGISTRATION.md` | what that study predicted before it ran, to check the record against the promise |
| `docs/FORMATION-PROVENANCE-STUDY.md` | its generated report, including the `does_not_establish` list |
| `docs/FORMATION-PROVENANCE-ROBUSTNESS.md` | whether the association survives leave-one-seed-out and stratified resampling |
| `docs/phase_k_results.json` | the K3 displacement-priority evidence the design leans on for its predictor |
| `docs/V1-SYNTHESIS.md` | the negative behavioural results the hypothesis must live beside |
| `docs/SCALING-LADDER.md` | the sign-resolution estimator and the 100-cycle convention this design deviates from |
| `docs/V1-FREEZE.md` | what may not change, so the reviewer knows the design's degrees of freedom |

Read the design record first. The package is the minimum, not the maximum: the reviewer may ask for any
artifact in the repository, and should be given it. No artifact in the package is a summary of another —
where a document restates a result, the result's own artifact is included so the restatement can be checked.

## 5. The rubric

Each of the five items is marked **PASS**, **CONDITIONAL** or **DEFECT**, with one paragraph of reasoning and
a pointer to the artifact that supports the judgement. A CONDITIONAL must be written as a change specific
enough to be re-reviewed — "make the control stronger" is not a condition; "report the size baseline beside
the main slope and require the main slope's interval to exclude the baseline's" is.

The overall outcome is one of:

| Outcome | Meaning | Consequence |
| --- | --- | --- |
| **Approved** | the design can support the inference as written | seeds may be named, subject to §6 |
| **Approved with conditions** | specific changes are required first | the same reviewer re-assesses the changed items; seeds are named only after that re-assessment is recorded |
| **Rejected** | the experiment cannot support the proposed inference in its current form | no seed is named for this design; a new design record is required, and this record stays as written |

A rejection is recorded verbatim and is not edited later. A rejected design may be replaced; it cannot be argued into an approval in the record.

## 6. The safeguard

**The review happens before any new experimental result exists.** The reviewer is shown no data produced by
this design, because none exists and none may be produced until the outcome is recorded. If an item cannot be
assessed without data, the reviewer receives **design-block** data only, declared as such, and never the
confirmatory block. No seed may be named, and no run started, until §7 carries an outcome.

Two further gates sit outside this review and are not discharged by it: the endpoint-specific
sign-resolution computation the 100-cycle deviation requires (§5 of the design record), and the
withheld-transition enumeration for whichever secondary configurations survive their own criteria.

## 7. The record to be filled by the reviewer

| Field | Value |
| --- | --- |
| Reviewer | *(to be completed)* |
| Affiliation and contact | *(to be completed)* |
| Declared conflicts | *(to be completed)* |
| Date received / date reported | *(to be completed)* |
| Item 1 — testability | *(PASS / CONDITIONAL / DEFECT + reasoning)* |
| Item 2 — measurement independence | *(to be completed)* |
| Item 3 — held-out validity | *(to be completed)* |
| Item 4 — statistical criteria | *(to be completed)* |
| Item 5 — falsifiability | *(to be completed)* |
| Overall outcome | *(Approved / Approved with conditions / Rejected)* |
| Conditions (if any) | *(specific, re-reviewable)* |
| What was not reviewed | *(to be completed)* |
| Signature | *(to be completed)* |

## 8. What this review cannot do

- **It cannot substitute for the endpoint sign-resolution computation.** A methodologically sound design on
  an underpowered endpoint is still underpowered, and the reviewer is asked to say so if that is what they
  find.
- **It cannot be conducted by the author of the design record.** That is the whole of §2.
- **It is not peer review of conclusions.** There are no conclusions yet; the review is of a plan.
- **It cannot be waived for schedule.** An unrecorded review is an absent one.
