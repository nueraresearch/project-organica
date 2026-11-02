# Machine review — the prompt, and what it is not

**Status: usable now. Output from it may never be recorded in §7 of `docs/INDEPENDENT-METHODS-REVIEW.md`.**
That form records a person, and a signature field filled by a model is a fabricated provenance.

## Why a machine pass is worth doing, and what it cannot be

A fresh model with none of this project's history is a genuinely different reader. It has not watched the
design get built, so it cannot be anchored by the reasoning that produced it; it will read all 373 lines of
the protocol and every artifact behind them without fatigue; it costs nothing to ask twice; and it cannot
be persuaded by the author's enthusiasm, because the author is not in the room.

What it cannot supply is the thing the gate was built for. Independence in §2 of the review brief is not
only "was not the author" — it is **someone who can say no and is answerable for having said it**. A model
that approves has risked nothing, cannot be asked to defend the approval in a year, cannot decline to
approve, and cannot be cited in a methods section as the person who examined the design before it ran. An
approval whose cost is zero is not a constraint, and a constraint is the whole purpose.

So this is a **pre-pass**: run it, fix what it finds, then send the letter. If it finds something blocking,
that is a free win. If it finds nothing, that is not evidence the design is sound — it is evidence that a
particular failure mode did not appear.

## The prompt

Paste the block below into a model with no other context. Replace the commit only if the package names a
different one.

> You are an adversarial methodological reviewer. You are reviewing a research **plan** that has not been
> run. Your job is to find the reasons it should not be run, and to identify which of its claims cannot be
> checked at all.
>
> **Repository.** https://github.com/nueraresearch/project-organica, at commit `1051313`. It is public; read
> files directly rather than trusting my summary of them.
>
> **Read, in this order.** `docs/STRUCTURE-BEHAVIOR-DESIGN.md` (the protocol), `docs/REVIEW-PACKAGE.md` (the
> cover sheet and prior-evidence summary), then the artifacts the protocol cites — in particular
> `docs/formation_provenance_study.json`, `docs/phase_k_results.json`, `docs/sign_resolution_structure_behavior.json`
> and `docs/SCALING-LADDER.md`. The review brief and rubric are `docs/INDEPENDENT-METHODS-REVIEW.md`.
>
> **Rules that constrain your review.**
>
> 1. **Check artifacts, not prose.** Every number in the protocol has an artifact behind it. If a number has
>    no artifact, that is a defect and you should name it as one.
> 2. **Do not rewrite the design and do not propose repairs.** Name the defect and the smallest check that
>    would let someone else settle it. A repaired design you wrote is a design you can no longer review.
> 3. **Do not output an approval or a rejection of the experiment.** Those verdicts belong to a named human
>    reviewer and their report form is deliberately empty. Your outputs are the item verdicts below and a
>    list of claims you could not check.
> 4. **Say when you cannot check something.** If a claim needs the engine to run, or a measurement nobody
>    has made, say so and name what would have to be measured. "Looks reasonable" is not a verdict.
> 5. **Do not fill in the report form** in `docs/INDEPENDENT-METHODS-REVIEW.md` §7.
>
> **Answer the five rubric questions** in §3 of the brief — testability, measurement independence,
> held-out validity, statistical criteria, falsifiability — and for each give:
>
> - a verdict of PASS, CONDITIONAL or DEFECT;
> - the specific artifact, line or computation that supports it, quoted;
> - a severity: blocking, important, or cosmetic;
> - for CONDITIONAL or DEFECT, the one check that would settle whether your objection holds.
>
> **Then add three short sections.**
>
> - **Claims I could not check**, with the measurement or run each would need.
> - **The strongest single objection** to running this experiment, in one paragraph, stated as the person
>   who would have to answer it.
> - **What would have to be true** for this block to be worth its stated size in runs, given that the size
>   is a floor rather than a target and that the predictor's reliability is unmeasured.
>
> Be specific and be unkind. A vague objection is worse than none, because it cannot be acted on and cannot
> be shown wrong.

## How to record what comes back

Save the transcript as `docs/AI-REVIEW-<date>.md`, with a header naming **the model**, **the date**, **the
commit reviewed**, and this sentence: *"Machine review. Not the independent review. §7 of the review brief
remains empty."*

If it produces a blocking finding, fix the protocol and record the change in the journal **quoting the
model's wording**, so the finding and the fix stay attached to each other. If it produces nothing blocking,
record that with the same prominence — a clean machine pass is a fact about a failure mode, not a
certificate.

## What this cannot do, stated so it cannot be quietly upgraded later

- **It cannot discharge the review gate.** No seed is allocated on the strength of it.
- **It cannot be cited** as the review that preceded the experiment.
- **It cannot see** anything that requires running the engine, reading the six months of history that
  produced the design, or knowing what the author chose not to write down.
- **It cannot refuse.** A model asked whether a plan it has just read looks acceptable will find reasons to
  say yes, and that is the failure mode the human gate exists to prevent.
