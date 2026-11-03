# AUTHORISATION — Stage B (2026-11-03)

**Decision:** Stage B is authorised.
**Given by:** the repository owner.
**Date:** 2026-11-03.
**Commit authorised:** `d16d8ae`.
**Recorded by:** the agent, from the owner's message. The decision is the owner's; the wording of this record is not.

## The statement

> i authorize it

It was given in reply to a message that ended: "Stage B remains unauthorised: step 2 is still the only open step
and still yours." The record is written against that referent and nothing wider.

## What is authorised

The confirmatory run exactly as specified at `d16d8ae`, which carries the protocol and the arithmetic artifact
unchanged from `9c61cc6` — the only difference between those two commits is the review prompt's pin:

- **four configurations** — `2:1`, `3:1`, `4:1`, `6:1` — **180 worlds each, 720 worlds**, at **373,320 cycles**;
- **seeds `700000001`–`700000720`**, pre-assigned 180 per configuration; **`700000721`–`700000724` never drawn**;
  substitution prohibited, and a censored world does not release its seed to another world;
- the **predictor** (confirmed DI onset), the **endpoint** (`revision_held_out`, averaged pairwise log loss on
  transitions withheld from both windows), the **four falsifiers**, the **outcomes table** and the **analysis**
  (Spearman within configuration, percentile bootstrap, slope beside it) exactly as committed at this commit;
- the **claim** that the predicted relation holds **in every configuration**, which is why the block is sized on the
  conjunction rather than on one configuration's share.

## What preceded it

Three machine passes from **two model families** — Manus at `39adb24`, Manus at `b9c73a7`, ChatGPT at `39adb24` —
recorded in `docs/AI-REVIEW-2026-11-02.md`, `docs/AI-REVIEW-2026-11-03.md` and
`docs/AI-REVIEW-2026-11-03-chatgpt.md`, with the closure in §D5 of `docs/DECISION-STAGE-B-SEQUENCE.md` and the
findings' dispositions in each record. **No independent human review preceded this run.** §7 of
`docs/INDEPENDENT-METHODS-REVIEW.md` remains empty, and no machine pass may be described as an approval.

## What it does not do

- **It allocates nothing.** Authorisation is a decision; allocation is the act of running, and no world exists.
- **It does not answer the precision gate.** `resolution_confirmed` stays `false`: the endpoint's per-world
  standard error is undetermined until a withheld set exists, and the run must report it before its interval is read.
- **It does not decide eligibility.** A configuration whose onset is mostly undefined is decided by the rule at run
  time, not in advance and not by the owner's signature.
- **It does not make the 0.05 gap an identity.** The effect gap is a linear model in standardised units (§3.1).
- **It does not retroactively bless anything.** No earlier document, result or claim is validated by this record.

## On the scope of a two-word authorisation

The statement is two words. The scope above is the protocol's own checklist from §D6 of
`docs/DECISION-STAGE-B-SEQUENCE.md`, not something the agent added to it; the alternative — recording "authorised"
with no scope at all — leaves the next reader to guess what was decided. **This record may be narrowed before the
run by a dated amendment in this file. It may not be widened by a later edit**, and it does not authorise anything
that is not named above.

## Step 3, and why the sequence stops here

No Stage B harness exists at this commit: `benchmarks/` holds the protocol generator, the resolution simulation and
the endpoint-precision probe, and nothing that generates a world or scores an endpoint. So **no seed is allocated and
no world has run**, and the run cannot start until that harness is written and audited. Writing it allocates nothing
by itself; the allocation happens when it first runs, against the seeds named above and no others.
