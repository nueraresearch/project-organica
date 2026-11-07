# Outreach — how and why to put this repository in front of a researcher

This note is about sending Organica to someone who does not already work on it: an
evaluation researcher, a structure-learning lab, a reviewer. It says why that is worth
doing, what to send, what to lead with, and what the record does and does not support.
It is deliberately narrow. Every number below is taken from an artifact named beside
it, and the ranking of audiences at the end is an opinion, labelled as one.

The tally of the project's questions lives in
[`docs/RESEARCH-QUESTION-REGISTRY.md`](RESEARCH-QUESTION-REGISTRY.md), generated from
`docs/research_question_registry.json`. That file is the one-page answer to "what has
this project actually settled?", and it is the best thing to attach after the papers.

## Why reach out at all

Three reasons, in order of how much they are worth.

1. **The independent review is a hard gate.** Stage B is authorised by an independent
   review, not by the owner (`docs/DECISION-STAGE-B-SEQUENCE.md`). Outreach is not
   publicity here; it is the only route to the next stage of the work. A reviewer who
   reads the protocol and finds the defect is the cheapest possible outcome, and it is
   the outcome the protocol is written to invite.
2. **The nulls are the product, and nulls need witnesses.** The strongest result in the
   repository is a well-controlled failure: a consolidated schema, fully applied, that
   still buys no acquisition latency
   (`docs/CROSS-CONTEXT-REUSE-EARNED-RESULTS.md`,
   `docs/cross_context_reuse_benchmark_earned.json`). A reader who assumes nulls are
   noise will read that as a bug. A reader who prices nulls correctly will read it as
   the interesting part.
3. **The questions are more portable than the engine.** Twenty-three questions, ten
   closed, six open, five retired, two future. Someone interested in cumulative
   knowledge acquisition does not need to adopt Organica to use the framing — and a
   reader who takes only the questions has still taken the part that generalises.

What outreach is *not* for: followers, citations, or a claim of importance. The repo
does not measure any of those and this note does not either.

## What to send

Nothing in the repository is published. [`papers/README.md`](../papers/README.md)
records eight manuscripts and zero published; the deposit (DOI) is the owner's action
and has not happened. So the sending order matters:

1. **Deposit first.** Until the papers have a DOI, a researcher cannot cite what they
   are sent, and most will not read closely something they cannot cite. Two papers have
   complete packages: Paper 01 (25 pp) and Paper 02 (14 pp). One deposited preprint is
   worth more than eight sent as attachments.
2. **Then one short note**, not the archive. The note should do three things: name the
   question, name the one result worth reading, and ask for one specific thing. For
   example:

   > I run a small developmental-architecture engine and I have been testing whether
   > developmental history turns into reusable knowledge. The controlled result is
   > negative and reproducible: a consolidated schema applied 162 times against 270
   > controls still transfers at 0.944, with no p-value and five seeds. I would value
   > a reading of the acquisition endpoint in §4 of the earned-results document —
   > specifically whether a session-level transfer ratio can carry a claim at all, or
   > whether only a rank-sensitive endpoint can.

3. **Attach [`docs/RESEARCH-QUESTION-REGISTRY.md`](RESEARCH-QUESTION-REGISTRY.md).** It
   is short, it is generated, and it lets a reader see what is closed before they
   propose it. That single gesture is the difference between a reply and silence.

Do not send the whole repository as the ask. Send one document and one question.

## The claim to lead with

Lead with the earned cross-context result, stated at its own width
(`docs/CROSS-CONTEXT-REUSE-EARNED-RESULTS.md`):

| Arm | Cycles | TR |
| --- | --- | --- |
| Treatment | 3.6 | 0.944 |
| Naïve (no prior) | 3.4 | 1.0 |
| Pruned | 3.4 | 1.0 |
| Orthogonal | 3.4 | 1.0 |

Verdict: `STRUCTURAL_PRIOR_PRESENT_NO_ACQUISITION_ADVANTAGE`. n = 5, no p-value. The
pre-registered criterion — TR > 1.25 at p < 0.01 over ten seeds — was **not met**, and
the negative is not softened by the fact that the prior demonstrably fired: it was
applied 162 times against 270 control applications and it reordered candidates, with
target ranks [7, 5, 4, 20, 7]. The manipulation ran and the effect was flat. That is
the sentence to lead with, and it is stronger than a positive would have been, because
the mechanism was verified rather than assumed.

Two supporting results travel with it, both narrower:

* **Selection cannot find the world's edges by frequency** — precision never exceeded
  0.3438 across 36 measurements under two allocation rules, coverage needs 240–244
  asserted edges at a cap of 20, about 12× the budget
  (`docs/gate13_allocation_rule.json`, `docs/GATE13-RELATION-SEPARATION.md`).
* **Excluding intra-cell rows buys precision at the sparse end** — 0.059375 against a
  pre-registered bar of 0.05, 13 of 16 seeds positive, reproduced by the second
  exposure scheme (`docs/density_interaction_a2_result.json`).

**Do not send the withdrawn v1 transfer number.** The v1 run reported a TR of 3.2 for
the orthogonal arm and 1.4 for pruning, and both are withdrawn: the advantage came from
a confidence boost keyed on the mere existence of a schema, which lifted a
one-transition edge past the prediction threshold. Remove that substitution and every
arm sits at 3.4 / TR 1.0. The comparison table in §3 of
`docs/CROSS-CONTEXT-REUSE-EARNED-RESULTS.md` is the artifact that proves it, and it is
the only place those numbers may appear. An outreach note that quotes them without the
word "withdrawn" is the single most damaging thing that could be sent from this
repository.

## What is established, what is open, what is not demonstrated

Keep these three lists separate in any note. The first is safe to assert; the second is
what makes the work interesting; the third is what keeps it honest.

| Claim | Status | Where it is bounded |
| --- | --- | --- |
| Developmental structure forms and persists | Established within the tested protocol | `docs/V1-SYNTHESIS.md` |
| A frequency-ranked selector cannot find the world's edges at the cap | Established on the Gate 13 family | `docs/gate13_allocation_rule.json` |
| Excluding intra-cell rows raises precision at the sparse end | Established at cap 20 | `docs/density_interaction_a2_result.json` |
| Whole-cycle padding explains the ladder's dip | Half confirmed, half not: −0.0344 residual remains unattributed | `docs/density_padding_result.json` |
| Internal structure improves held-out prediction | Not found at the confirmatory endpoint (interval crosses zero; 0.005647 nats headroom) | `docs/functional_structure_confirmatory.json` |
| A consolidated schema buys acquisition latency | No gain detected at this endpoint | `docs/CROSS-CONTEXT-REUSE-EARNED-RESULTS.md` |
| The architecture's motivational mechanisms drive development as predicted | Three of five reversed in the developmental direction | `papers/07_architecture_predictions_reversed.md` |
| Role abstraction removes the orthogonal dependence | Open — RoleCandidate is unvalidated | `docs/RESEARCH-QUESTION-REGISTRY.md` |
| A rank-sensitive endpoint rewards the prior | Open — no cells | `docs/RESEARCH-QUESTION-REGISTRY.md` |
| Developmental history becomes reusable knowledge | Open — untested as a joint claim | `docs/RESEARCH-QUESTION-REGISTRY.md` |
| AGI, or general capability of any kind | Not demonstrated, and not measured by anything here | — |

## What it can be built into — conditional, not evidence

The previous section is the current state. This one is the potential state, and the
difference matters enough that it should be labelled in any note: **the chain below is
a research programme, not a finding.** No experiment in this repository estimates the
probability that any link holds.

```
RoleCandidate validated
  → role satisfaction explains the orthogonal dependence
    → role representations transfer across domains
      → developmental history becomes reusable knowledge
        → transfer improves future transfer
```

Each arrow is a question with an id in the registry: Q012 is the first link, Q022 the
third, Q023 the fourth. Only Q012 has any evidence at all, and that evidence is that
the current mechanism does not yet exist. If the first two links fell, the repository
would stop being a developmental-architecture study and become a study of cumulative
knowledge acquisition — which is a different and much larger claim, and one that would
need its own controls, its own nulls and its own review before anyone said it out loud.

So: "Organica is a testbed for developmental structure formation and transfer" is a
statement about what exists. "Organica could become a transfer-learning research
platform" is a statement about a plan that depends on Q012 resolving favourably. Both
are true; only the first is evidence. Say which one you mean, every time.

## Who to send it to, and in what order

This ranking is the author's opinion, not a result, and nothing in the repository
measures audiences.

1. **Evaluation-focused researchers** whose published work is about what fails and why
   under controlled conditions. The fit is direct: the repo's strongest asset is a
   verified manipulation that produced no effect, and its weakest asset is scale.
2. **Structure-learning and transfer researchers** who would care about the negative
   on schema priming. Expect the first question to be "why five seeds?", which the
   earned-results document answers rather than dodges.
3. **Independent reviewers for Stage B.** The one audience with a defined action to
   take. Reach them with the protocol, not the papers.
4. **Large industrial labs.** Long shot, and worth one attempt after the deposit exists.
   The honest pitch is "here is a small, fully instrumented negative result", not
   "here is an architecture".

Anything said about specific funding programmes, fellowship calendars or lab intake is
outside this repository's evidence. If a note makes such a claim, it is the author's
opinion and must be labelled as such; the record contains no application, no
correspondence and no acceptance.

## What not to say

* Not AGI. Not "on the path to AGI". Not "general capability".
* Not "transfer demonstrated". The transfer arms are flat; the schema prior is present
  and buys nothing at the acquisition endpoint.
* Not the v1 numbers. Not 3.2, not 1.4, not 2.286, except as explicit withdrawals with
  the artifact that withdraws them.
* Not a claim wider than its check. Cap 20 is cap 20; one world family is one world
  family; five seeds is five seeds.
* Not the future chain as if it were the present state.

The registry exists so that the first three of those are checkable by the recipient
without trusting the sender.
