# Context — the facts that were held in conversation rather than in an artifact

This document adds **no measurements**. It is a register of the facts that were being
carried in conversation and in the owner's head: what the owner can actually afford to
run, who the work is addressed to, and what the project explicitly does **not** claim.

Every row carries a provenance marker, and the marker is the point:

| Marker | Means |
| --- | --- |
| `repo` | already recorded in an artifact, which is cited in the row |
| `owner-reported` | stated by the owner to an agent, recorded here as testimony, not evidence |
| `unknown` | nobody has recorded it; the row says what would settle it |

A row may move from `owner-reported` to `repo` when it lands in an artifact that owns
it, and from `unknown` to either when someone measures or states it. It may never move
in the other direction quietly. `tests/test_context_doc.py` asserts that every row in a
provenance table carries exactly one marker, that the Stage B compute figure agrees with
`docs/stage_b_cost_estimate.json`, and that every "would be licensed by" cell in §3
names something that exists.

---

## 1. Owner capacity and constraints

What the project can afford is a scientific constraint, not a personal detail: it decides
which of the 23 questions in `docs/RESEARCH-QUESTION-REGISTRY.md` is affordable at all.

| Fact | What is recorded | Provenance | Why it matters |
| --- | --- | --- | --- |
| Who writes, runs and analyses the work | One person writes the engine code, the protocols, the analyses and the documents; the review letter is written in the first person singular (`docs/REVIEW-REQUEST.md`) | `repo` | Every dependency chain in the action list assumes one pair of hands, so a question costing 30 seeds queues behind everything else |
| Institutional affiliation | No affiliation appears on any artifact, citation record or letter; the letter describes the codebase as independent (`docs/REVIEW-REQUEST.md`) | `unknown` | "No affiliation stated" is not the same as "none"; an external reviewer will ask, and no artifact can answer yet |
| Hours available per week | Nothing. The action list is sequenced by dependency, never by hours | `unknown` | Without it the registry's "future" section cannot be priced, and the Stage B decision is a schedule decision as much as an evidence one |
| Machine the studies run on | Nothing. No artifact names a host, a core count or a memory ceiling; the only machine facts are timings measured from runs (next row) | `unknown` | A 29-hour single-pass estimate is cheap on one machine and impossible on another, and the difference is invisible in every document |
| Measured cost of one Stage B pass | About 29 hours of single-core-equivalent compute: 720 worlds, 366,120 cycles at 0.2865 s/cycle mean. The artifact is explicit that this is a planning estimate with no seed allocated (`docs/stage_b_cost_estimate.json`) | `repo` | This is the only quantified capacity fact in the repository, and it is derived rather than declared |
| Funding received | Nothing is recorded, and none is claimed anywhere | `unknown` | The project has no funding row to point at; if a reader assumes one, nothing corrects them |
| Commercial track | Unresolved and owned by the owner, not by the code: entity, IP ownership, open-source licence position and the authorisation memo all require counsel (`docs/GATE-BOARD.md` item 9, `docs/FACTS-SHEET.md` §G6) | `repo` | The repository deliberately holds no counsel advice, customer identities or pricing; do not add them here either |
| Calendar and deadline | Nothing. No date is committed to anywhere except the deposit sequencing in `docs/OUTREACH.md` | `unknown` | A deadline changes what is worth starting; nothing in the record currently reflects one |
| Who may release | Release tags, deposits and publication are the owner's alone; commits and pushes are authorised as a standing arrangement (`AGENTS.md` rule 6, `papers/README.md`) | `repo` | An agent may prepare a release but may not cut or publish one, so "why isn't this on a preprint server" has a written answer |
| Who may authorise Stage B | Nobody inside the project. The independent review is the gate (`docs/DECISION-STAGE-B-SEQUENCE.md`) | `repo` | The owner cannot self-authorise the next stage, which makes outreach a dependency rather than a preference |
| What is asked of a reviewer | Two to four hours inside a stated window, with a written verdict (`docs/REVIEW-REQUEST.md`) | `repo` | It sets the size of the ask; a request for a week of someone's time would not be sent |

The honest reading of that table is that the project's **evidence** is documented to a
standard its **capacity** is not. The rows marked `unknown` are there because nobody
wrote them down, not because they do not exist.

## 2. Audience and why

| Reader | Why this project, in one line | Provenance | Why it matters |
| --- | --- | --- | --- |
| An independent methodological reviewer | The review happens before the run and asks whether it should run at all (`docs/INDEPENDENT-METHODS-REVIEW.md`) | `repo` | This is the only audience with a defined action that unblocks work, and the only one that is a gate rather than a hope |
| Evaluation-focused researchers | The strongest asset is a verified manipulation that produced no effect, and the strongest liability is scale | `owner-reported` | The owner asked for outreach material addressed to external research readers on 2026-11-07; the ranking of audiences is opinion, and `docs/OUTREACH.md` labels it as such |
| Structure-learning and transfer researchers | The schema-priming null is the interesting object, not the engine | `owner-reported` | Same request, same date; a reader who wants a new architecture will be disappointed by a result about one |
| Large evaluation labs, named as METR-type and FAIR-type | Named as an aspiration in the owner's note; no contact, application, invitation or reply is recorded anywhere in the repository | `owner-reported` | Naming an organisation is not a relationship; a stored expectation about a lab's interest is exactly the kind of fact that rots |
| Any reader, in fact | Written, not sent: five bracketed fields must be filled by the sender, and no reviewer has been approached (`docs/REVIEW-REQUEST.md`) | `repo` | The repository's own status line settles it, so nobody has to infer outreach progress from documents that describe intent |
| Audience size, citation interest, reply rates | Not measured, not estimated, not tracked | `unknown` | The repository contains no analytics, no correspondence and no acceptance; any claim about reach is the speaker's, and must be labelled |

The why, in one paragraph, because it is easy to lose among the rows: the record is
large enough to be unreadable without an entry point, its most valuable single result is
a negative that a careless reader will mistake for a bug, and its questions travel
further than its engine. None of that is an argument that anyone *will* read it — only
that there is a reason to ask.

## 3. Not claimed — and what would license each claim

This is the list that goes missing from repositories, because a claim's absence is
silent. It is written as "not claimed **because** X, and would be licensed by Y" so that
each row has a test attached rather than a mood.

| Not claimed | Because | Would be licensed by | Provenance |
| --- | --- | --- | --- |
| AGI, or general capability of any kind | Nothing here measures it; the registry's two largest questions are marked future and have never been run | A benchmark outside this repository, an independent replication, and a claim registered before the run; `docs/EMERGENCE-CRITERIA.md` records which levels this project can currently evidence | `repo` |
| Any positive transfer effect | The earned run returns TR 0.944 with the prior applied 162 times against 270, over five seeds and no p-value (`docs/CROSS-CONTEXT-REUSE-EARNED-RESULTS.md`) | TR above 1.25 at p below 0.01 over ten seeds with the prior demonstrably applied — question Q011 | `repo` |
| That internal structure improves held-out prediction | The confirmatory test found none, with an interval crossing zero and 0.005647 nats of headroom over the strongest simple baseline (`docs/functional_structure_confirmatory.json`) | A headroom whose lower interval bound clears zero against that same baseline on the audited endpoint `docs/ACQUISITION-ENDPOINT-AUDIT.md` | `repo` |
| That the density ladder is monotone | The padding scheme moves the dip by half and leaves the 0.4-to-0.6 step at −0.0344 with both criteria failing (`docs/density_padding_result.json`) | A scheme that moves that step without changing total exposure, judged against the two criteria registered in `docs/DENSITY-PADDING-PREREGISTRATION.md` | `repo` |
| That any of this generalises beyond one world family at cap 20 | Every result is scoped to the family and cap in its own artifact (`docs/GATE13-RELATION-SEPARATION.md`) | The same verdict on a second family, registered before the run; `docs/GATE13-RELATION-SEPARATION.md` covers the first family only | `repo` |
| Independent replication | The audit layer is independently *reconstructed* from engine state, which is a different claim (`docs/AUDIT-TRACE-SPEC.md`) | A second lab reproducing a verdict from the commit, under the reconstruction protocol in `docs/AUDIT-TRACE-SPEC.md` | `repo` |
| That a consolidated schema speeds acquisition | The acquisition endpoint shows no gain and does not score rank (`docs/DECISION-EARNED-SCHEMA-PRIMING.md`) | A rank-sensitive endpoint that rewards the reordering — question Q014 | `repo` |
| Role abstraction, or reusable knowledge from developmental history | RoleCandidate is unvalidated; the chain is a programme, not a finding (`docs/RESEARCH-QUESTION-REGISTRY.md`) | RoleCandidate validated on the single boundary it was proposed for — question Q012 | `repo` |
| That these are the right questions, or that anyone wants them | A registry of questions is a hypothesis about relevance, not a measurement of it | A reader's reply or a reviewer's verdict; `docs/REVIEW-REQUEST.md` is written and unsent, and nothing in the repository forecasts either | `repo` |
| Any safety, alignment or controllability property | Nothing is measured on that axis, and nothing in the protocol claims it | Its own protocol with its own control; no question in `docs/RESEARCH-QUESTION-REGISTRY.md` covers that axis | `repo` |
| That a summary outranks the artifact behind it | The artifacts own the numbers; where a document disagreed with one it was corrected to it (`docs/FACTS-SHEET.md` §E) | Regeneration from the artifact, never restatement; the pattern is `docs/FACTS-SHEET.md` §E | `repo` |

## 4. What this document is not

It is not evidence, not a summary of results, and not a plan. It does not license a
number: every quantity named here is either quoted from an artifact or explicitly marked
unknown, and the artifact outranks this page in every case.

Its purpose is narrower and it is worth stating plainly: **the `unknown` rows are the
deliverable.** They are the facts that would change which question is affordable, and
they were previously held only in conversation, where they could not be argued with. A
reader who wants to know what this project cannot currently afford should read §1; a
reader who wants to know what it does not claim should read §3 and then check that the
list is still true.
