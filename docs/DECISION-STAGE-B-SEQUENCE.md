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
