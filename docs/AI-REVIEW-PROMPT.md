# Machine review — the prompt, and what it is not

**Status: usable now, aimed at the frozen Stage B protocol. Output from it may never be recorded in §7 of
`docs/INDEPENDENT-METHODS-REVIEW.md`.** That form records a person, and a signature field filled by a model is
a fabricated provenance.

## Where this pass now sits in the sequence

On **2026-11-03** the owner recorded that **no eligible reviewer can be found** under §2 of the brief, and chose
this pass as the **recorded precondition for his own authorisation decision**
(`docs/DECISION-STAGE-B-SEQUENCE.md`). That changes *when* a person is asked, not what an approval is: the pass
is now **load-bearing for the sequence** and is still **not an approval**, and no document may describe it as one.

**Why it is worth doing at all.** A fresh model with none of this project's history is a genuinely different
reader. It has not watched the design get built, so it cannot be anchored by the reasoning that produced it; it
will read every line of the protocol and every artifact behind it without fatigue; it costs nothing to ask twice,
and ask a second model family; and it cannot be persuaded by the author's enthusiasm, because the author is not
in the room. It also cannot be embarrassed, which is why it will name a defect the author has stopped seeing.

What it cannot supply is accountability: a model that approves has risked nothing, cannot be asked to defend the
approval in a year, and cannot be cited in a methods section as the person who examined the design before it ran.
So it substitutes for nothing. What the owner has changed is the order of events, and the record says so.

## What it is reviewing

`docs/STAGE-B-PROTOCOL.md` at commit `9c61cc6`, the commit that carries the protocol's §13, the pre-pass corrections and this prompt —
**replace that number with `git rev-parse HEAD`** if the tree has moved since, and never send a prompt whose
commit does not resolve. A pass pinned to an earlier hash reviews a protocol that did not yet record how it can be
authorised. The protocol under review is **not**
`docs/STRUCTURE-BEHAVIOR-DESIGN.md`, which is the design record it inherits its endpoint from; a reviewer sent to
the older document will examine a design that has since been resized, re-assumed and corrected.

## The prompt

Paste the block below into a model with no other context.

> You are an adversarial methodological reviewer. You are reviewing a research **plan** that has not been run.
> Your job is to find the reasons it should not be run, and to identify which of its claims cannot be checked at
> all.
>
> **Repository.** https://github.com/nueraresearch/project-organica at commit `9c61cc6`. It is public; read files
> directly rather than trusting my summary of them.
>
> **Read, in this order.** `docs/STAGE-B-PROTOCOL.md` (the protocol under review), `docs/stage_b_protocol.json`
> (every number in it, written by `benchmarks/stage_b_protocol.py`), `docs/DI-TRANSITION-CONSTRUCT.md` and
> `docs/di_transition_construct.json` (the predictor it inherits and does not choose), then
> `docs/STRUCTURE-BEHAVIOR-DESIGN.md` §3 and §6 (the endpoint and the attenuation mapping),
> `docs/sign_resolution_structure_behavior.json`, `docs/reusable_knowledge_calibration.json` (the design-block
> cells behind the granularity claim), `docs/formation_provenance_study.json`, `docs/phase_l_results.json`,
> `docs/SCALING-LADDER.md` §8 to §10, and `docs/V1-SYNTHESIS.md`. The rubric is
> `docs/INDEPENDENT-METHODS-REVIEW.md`; its §7 is a person's form and stays empty.
>
> **Rules that constrain your review.**
>
> 1. **Check artifacts, not prose.** Every number in the protocol has an artifact behind it. If a number has no
>    artifact, that is a defect; name it. The protocol claims that its ladder reproduces the published table at
>    every row — recompute it, and say whether it does.
> 2. **Do not rewrite the design and do not propose repairs.** Name the defect and the smallest check that would
>    let someone else settle it. A repaired design you wrote is a design you can no longer review.
> 3. **Do not output an approval or a rejection** of the experiment. Your outputs are the item verdicts below and
>    a list of claims you could not check.
> 4. **Do not fill in the report form** in `docs/INDEPENDENT-METHODS-REVIEW.md` §7.
> 5. **Say when you cannot check something.** If a claim needs the engine to run, or a measurement nobody has
>    made, say so and name what would have to be measured. "Looks reasonable" is not a verdict.
>
> **Answer the five rubric questions** in §3 of the brief — testability, measurement independence, held-out
> validity, statistical criteria, falsifiability — and for each give a verdict of PASS, CONDITIONAL or DEFECT,
> the artifact, line or computation that supports it, quoted, a severity of blocking, important or cosmetic, and
> for CONDITIONAL or DEFECT **the one check that would settle whether your objection holds**.
>
> **Then answer the five questions the protocol itself refers to the reviewer** in its §10 — the block size at
> the declared reliability assumption and whether the ladder is the right way to handle an unmeasured
> reliability; whether the sustention-rule agreement is correctly described as robustness rather than
> reliability and rightly excluded from the arithmetic; whether the endpoint has sufficient resolution and an
> unambiguous operational definition; whether the pre-assigned seeds, the four reserved seeds and the
> no-substitution rule keep attrition from becoming a search; and whether the aggregation rule prevents a
> favourable but misleading reading.
>
> **Then add four short sections.**
>
> - **Claims I could not check**, with the measurement or run each would need.
> - **The strongest single objection** to running this experiment, in one paragraph, written as the person who
>   would have to answer it.
> - **Numbers without an artifact**, or the statement that you found none.
> - **What would have to be true** for this block to be worth its stated size in runs, given that the size is a
>   floor rather than a target, that the predictor's reliability is unmeasured, and that the cost is 373,320
>   cycles.
>
> Be specific and be unkind. A vague objection is worse than none, because it cannot be acted on and cannot be
> shown wrong.

## How to record what comes back

Save the transcript as `docs/AI-REVIEW-<date>.md`, with a header naming **the model and version**, **the date**,
**the commit reviewed**, and this sentence: *"Machine review. Not the independent review. §7 of the review brief
remains empty."*

If it produces a blocking finding, fix the protocol, record the change in the journal **quoting the model's
wording**, and re-run the pass on the corrected commit. If it produces nothing blocking, record that with the
same prominence — a clean machine pass is a fact about a failure mode, not a certificate — and the owner's
authorisation decision may then be recorded.

**Run it on at least two model families.** One pass on one model is one reader; the disagreements between two are
the useful output, and this project's own record shows that a close third read can catch one defect and miss six.

## What this cannot do, stated so it cannot be quietly upgraded later

- **It cannot discharge the review gate.** §7 stays empty, and no seed is allocated on the strength of a pass.
- **It cannot be cited** as the review that preceded the experiment.
- **It cannot refuse**, and that is the failure mode the §7 gate exists to prevent. A model asked whether a plan
  it has just read looks acceptable will find reasons to say yes; the adversarial framing above reduces that and
  does not remove it.
- **It cannot see** anything that requires running the engine, reading the six months of history that produced
  the design, or knowing what the author chose not to write down.
