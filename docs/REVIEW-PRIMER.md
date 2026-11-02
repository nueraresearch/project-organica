# Review primer — the protocol in plain language

**For a reviewer who is not in this field, or is in it and short of time.** Five minutes, then the protocol
itself. Nothing here replaces an artifact: where a number appears, the artifact that owns it is named.

## What the project is

A program grows knowledge structures from a stream of events. It does this in sessions — take events in,
then consolidate — and between sessions some structures survive and others die. The project's question is
whether what survived is related to what the program can later do.

Two numbers carry the whole design, and neither is exotic:

- **`DI`** — of the structures the world made available late in a session, what fraction survived. A ratio
  between 0 and 1. Read it as *how much of the late material stuck*.
- **`revision_held_out`** — how well the same program predicts the next tag on transitions it was never
  shown, in a later session. Read it as *how well it does on material it could not have memorized*. It is
  scored on 98–110 such transitions per run, not on a handful.

## The claim being tested

> In one setup, a run that kept more of the late structure later predicts held-out transitions better — and
> that relation holds, weakens, disappears, or reverses when the setup changes.

That is a **prediction** claim. It is not a claim that structure *causes* behavior, and the protocol forbids
the causal wording. Proving causation needs an experiment that changes the structure on purpose, which is a
later and larger thing.

## What would count against it

- Absent in every setup: unsupported.
- Pointing the other way: reversed, which is a stronger statement than unsupported.
- Explained by a plain "how much structure is there" baseline: a size effect — quantity, not content.
- The permutation control returning a signal: the design is broken and **no result is reported**.

The protocol states these in advance, which is what stops them from being chosen later.

## Two things a reviewer should look hardest at

**1. One instrument produces both numbers.** `DI` counts what the program's readout got right; the outcome
scores what that same readout predicts. Disjoint material does not make them independent, because the
measuring device is shared. The design bounds that explanation with a size baseline and a permutation
control, and discloses the limit rather than claiming to have removed it.

**2. How many runs it takes, and why that is awkward.** To detect a relation of size 0.50 with the
protocol's own decision rule takes **48 runs per setup** at the 0.90 bar
(p ≈ 0.902). That number is a **floor, not a target**: if `DI` is measured noisily the observed
relation shrinks and more runs are needed — at 0.80 reliability it is
79 runs per setup. Nobody has measured that reliability yet, so the true
requirement is unknown and at least 48. Three setups is **144 runs at best**.

## What you are being asked

Not whether the topic is interesting. Whether this plan can support the sentence it wants to write, and
whether it is worth what it costs. Three answers are allowed, and **"no" is one of them** — it is a finding,
not a failure of the review.

## What is most useful to say

- A defect you can name, with the line or artifact behind it.
- A claim that cannot be checked at all, and what would have to be measured to check it.
- If the honest answer is that it should not run, say so plainly and stop; nobody will argue with it in
  the record.

## Words this document uses, defined once

| Term | Means |
| --- | --- |
| run / world / seed | one execution of the program on one synthetic world. The protocol says "world" for the unit and "setup" for a family of worlds |
| held out | never shown during either learning session, so it can only be predicted, not memorized |
| permutation control | shuffle the labels so any real relation must vanish; if it does not, the measurement is broken |
| sign resolution | the chance that a block of runs reports the direction of a relation correctly, computed before the runs happen |
| floor (of a size) | the least number of runs that could work. Noise and dependence can only raise it |

## Reading order

1. This page.
2. `docs/STRUCTURE-BEHAVIOR-DESIGN.md` — the protocol. Read §1 and §3 first; they define the claim and the
   measurement. §6 is the statistics, §10 is what outcome licenses which sentence.
3. `docs/REVIEW-PACKAGE.md` — what the project has and has not established, with the artifact behind each
   row.
4. `docs/INDEPENDENT-METHODS-REVIEW.md` §3 and §5 — the five questions and the marks they take.
