# DECISION — the route to Stage B authorisation

**Date:** 2026-11-03
**Status:** DECIDED — a sequencing decision by the owner. It is not an amendment to the science.
**Amends:** the authorisation route recorded in `docs/STAGE-B-PROTOCOL.md` §11 and
`docs/INDEPENDENT-METHODS-REVIEW.md` §6. It changes **no** hypothesis, gate, threshold, endpoint, falsifier or
seed, and it authorises no run.

## D1 — The finding

The independent review is the only thing standing between a frozen protocol and a run. §2 of the review brief
excludes the author, the owner, and anyone with a stake in the result, and requires methodological expertise in
the statistical design; that combination gives a small candidate pool, and **no eligible reviewer has been
found**. The gate has therefore become an indefinite block rather than a check.

**The owner's recorded reason, in his words:** *"No eligible reviewer can be found."*

## D2 — The decision

The sequence to authorisation is now:

| step | what is recorded | who |
| --- | --- | --- |
| 1 | a **machine pre-pass** on the frozen protocol, transcript saved and named for its model and commit | run by the owner; findings fixed and journaled |
| 2 | an **authorisation decision** by the owner, dated, citing the pre-pass transcript | the owner |
| 3 | seed ranges move from **pre-assigned** to **allocated**, and the run starts | the owner |

**§7 of `docs/INDEPENDENT-METHODS-REVIEW.md` stays empty.** It records a person, and no step above fills it. If
an eligible reviewer is found at any point, the §7 route resumes and supersedes this sequence.

## D3 — What this does not do

- It does **not** approve the design. A clean pre-pass is evidence that a failure mode did not appear, not a
  judgement that the design can support the inference.
- It does **not** make the pre-pass citable as a review, in a methods section or anywhere else.
- It does **not** allocate a seed today. Stage B remains unauthorised until step 2 is recorded.
- It does **not** touch the frozen engine, V1's records, or any published artifact.

## D4 — What is bought, and what is given up

**Bought:** the block no longer waits on a person who cannot be found, and the pass is better aimed than an
interview would be, because it reads every artifact rather than what the author remembers to say.

**Given up:** the design-level defect class the review uniquely catches — an endpoint measuring a different
quantity than the claim, an intervention that does not say what it leaves behind, a build with no stop condition
(rules 23a to 23c) — is now bought down by an instrument that **cannot refuse**, cannot be held to its judgement,
and will find reasons to approve a plan it has just read. The mitigations are the adversarial framing in
`docs/AI-REVIEW-PROMPT.md`, two independent model families, and the requirement that every number be traceable
to an artifact.

**What the record will say afterwards, either way:** if a pass finds nothing blocking, the record states that no
independent assessment preceded the run and that a machine pre-pass did, and any publication carries that
limitation explicitly rather than leaving it to be inferred. If a pass finds something blocking, it is fixed,
logged with the model's wording, and the sequence restarts from step 1.

## D5 — Step 1 is closed: three passes, two model families (2026-11-03)

Step 1 asked for a recorded machine pre-pass, with findings fixed and journaled. Three passes are now recorded,
from **two** families, which is what `docs/AI-REVIEW-PROMPT.md` requires:

| pass | family | commit reviewed | findings, and what each turned out to be |
| --- | --- | --- | --- |
| `docs/AI-REVIEW-2026-11-02.md` | Manus | `39adb24` | endpoint resolution computed on a proportion while the scorer returns log loss; a withholding pointer to the wrong selector; the ladder's Fisher-z closed form versus the percentile bootstrap. All three confirmed and fixed |
| `docs/AI-REVIEW-2026-11-03.md` | Manus | `b9c73a7`, corrections at `e6334dc` | a stale quantum left in the generator; Monte-Carlo error spanning the 90 % bar; `s/sqrt(N)` over nested cells. All three confirmed and fixed |
| `docs/AI-REVIEW-2026-11-03-chatgpt.md` | ChatGPT | `39adb24` | endpoint proportion (already fixed before this pass ran, which the pass could not see); and that the block did not establish the **all-four-configuration** result. The second was live at HEAD and is the reason the block is 180, not 120 |

Two findings were still live against the tree when they arrived: the `s/sqrt(N)` precision substitution, and the
conjunction. Both are fixed in place with the arithmetic shown in `docs/STAGE-B-PROTOCOL.md` §6.3 and §3.1.

**One limit of this record, stated rather than hidden.** The ChatGPT transcript was supplied from a path outside
this repository and is not committed. Its record says so and quotes nothing from it; every finding in it was
checked against the code before a change was made. Committing the transcript beside the record would let a reader
check the summary against the source.

## D6 — What step 2 must record, and what only the owner can write

Step 2 is now the **only** open step. It is the owner's, and the remaining work on this repository is waiting on
it rather than on any further analysis. It must record, in the owner's own words:

- the **date** and the named **commit** being authorised — `3847637` or a later one, never an earlier one, because
  earlier commits carry the 104- and 120-world blocks;
- that the evidence preceding the run is **three machine passes from two model families, and no independent human
  review**, with §7 of the brief still empty;
- the **block**: 180 worlds per configuration, 720 worlds, 373,320 cycles, seeds `700000001`–`700000720` with four
  reserved at `700000721`–`700000724`;
- the **two gates that stay open regardless of authorisation**: the endpoint's per-world precision gate
  (`resolution_confirmed: false`) is answered by the pre-run enumeration for the four configurations, and the
  eligibility rule decides per configuration. Authorising the run does not pre-answer either;
- an acknowledgement that the endpoint's effect gap is a **model** (linear in standardised units, across-world SD
  0.05) rather than an identity, per §3.1.

**A step-2 record that omits any of these is not the authorisation this sequence describes**, and no later edit may
add them retroactively.

## D7 — Step 2 is recorded, so the sequence is spent up to step 3 (2026-11-03)

The owner authorised Stage B on 2026-11-03 against commit `d16d8ae`, in reply to the statement that step 2 was the
only open step and his alone. The statement, the scope, and what the authorisation does **not** do are in
[`docs/AUTHORISATION-STAGE-B.md`](AUTHORISATION-STAGE-B.md). Step 2 of the table in §D2 is complete.

**Step 3 has not happened.** No seed is allocated, no world exists, and there is no Stage B harness to run: the
sequence ends here until one is written. That is a real boundary and not a formality — the protocol specifies 720
worlds and 373,320 cycles, and no code in this repository can produce a single one of them yet.

Nothing in this section re-reads the science. The hypothesis, predictor, endpoint, falsifiers, outcomes, ladder and
seed block are exactly as they were at `d16d8ae`; what changed is that the run is permitted, which is a fact about
permission and not about evidence.

## D8 — A blocking finding after authorisation: the run has no world (2026-11-03)

Attempting to build the runner surfaced a defect that authorisation cannot fix and code must not paper over. The
predictor `DI` is defined only in the Phase L **scale-stream** family — it is `late_retained / late_available` against
a late gold set, which needs an early and a late group — and the outcome `revision_held_out` is defined only in the
**compositional cell** family, on cycles 250–299 of a 300-cycle world. **No world carries both**, and no document names
the family a Stage B world belongs to: the design record names the compositional family as primary while this
protocol's four configurations and their onset medians come from the scale family.

The clock settles it arithmetically: the behavioural window is confirmation + 1 to + 100, and §2's own table gives
median onsets of 539, 404, 362 and 329 on a world that ends at 300. The run as specified would not return a null
result; it would return no observation.

**This is recorded, not resolved.** `docs/STAGE-B-PROTOCOL.md` §5a carries the finding and the two repairs;
`docs/stage_b_protocol.json` carries `status.blocked_before_run`; the authorisation record carries a post-authorisation
note. Nothing is withdrawn: the hypothesis, the endpoint's definition, the falsifiers, the 720-world block and the
owner's authorisation all stand, and **no seed is allocated**.

**Step 2 remains complete and step 3 remains unstarted.** The open item is a new decision, and it belongs one level up
from the runner:

| option | what survives | what it costs |
| --- | --- | --- |
| **A — keep the predictor** | `DI` onset, its eligibility table, the block's derivation | the endpoint becomes a new held-out definition on the scale stream, which has never been validated and needs its own resolution check |
| **B — keep the endpoint** | `revision_held_out`, the compositional world, the law rotation | `DI`, §2's eligibility table and the Phase L onset medians all go; the block must be re-derived for a predictor with no measured distribution |

Writing either default into a harness would choose the experiment after the authorisation. That is the defect this
project has spent months removing from its own numbers, and it is why the sequence stops here rather than proceeding
on the more convenient option.
