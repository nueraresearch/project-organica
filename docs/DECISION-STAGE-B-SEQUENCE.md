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

## D9 — Option A attempted: the withheld set saturates, so the world must change (2026-11-03)

The owner took option A. Its first step — measuring the redefined endpoint on design-block cells — returned a null
that is about the endpoint rather than about the analysis: on the scale-stream family the formation window already
exhibits **every** ordered tag transition the behavioural window uses, so an absence-based withheld set is empty on
all twelve design-block cells and `held_out_next_tag` has no scored set at all
(`docs/stage_b_endpoint_scale.json`).

The consequence is structural. Withholding on this family cannot be done by scoring only unseen transitions; it has
to be **imposed** on the world by conditioned sampling, exactly as the compositional family produces its held-out
combination. That changes the stimulus, so it carries the compositional family's obligations: a withheld set
enumerated under criteria written before the enumeration, a degeneracy audit proving the set is reachable and the
axis is live, and a fresh precision measurement on design-block cells.

**No seed is allocated, no world is generated, and the run stays blocked** — now on a named piece of work rather than
on an open question. The predictor, the claim, the block and the authorisation are untouched.

## D10 — The withheld set exists, and the block moves to the predictor's side (2026-11-03)

§D9 named the work: withholding must be done by the world. `benchmarks/stage_b_stream_withholding.py` does it — one
declared directed entity transition refused by conditioned sampling while the organism is exposed, and permitted at
the test window — and the audit proves the intervention fired (82 compensations), that the scored set is absent from
formation (0 of 16 pairs) and present in the behavioural window (88), that the same pairs occur in an open world
(288), and that the configuration axis is live (late share 0.4424 to 0.5793, spread 0.1369).

The precision gate that had no basis now has one: twice the per-world standard error is 0.0019 to 0.0067
nats over 200 cluster-bootstrap replicates on twelve design-block cells, under the 0.05 gap everywhere.
`docs/stage_b_endpoint_scale.json`'s null is answered: the endpoint is measurable once the world withholds.

**The block moves, and it does not lift.** The outcome now has a world family; the predictor does not. This world is a
reconstruction of the scale family, not the frozen generator, and **no `DI` onset has been measured on it** — the
predictor's distribution across the four configurations here is unmeasured, and the behavioural window was placed at
the protocol's reported medians rather than at observed onsets. Measuring onset on this family, and showing it varies,
is the next piece of work; until it exists `status.blocked_before_run` stays true, no seed is allocated and no world
runs.

## D11 — The onset harness is built and the diagnostic measurement completed (2026-11-03)

`benchmarks/stage_b_onset_withholding.py` ran the frozen engine over the withholding world on the three consumed
design-block seeds in each configuration. The completed artifact is `docs/stage_b_onset_withholding.json`; it records
the per-cycle `DI` trajectory and applies the protocol's onset rule (first cycle of the first qualifying sustained
run), with the 5- and 20-cycle rules beside it. All **12/12** cells have a qualifying 10-cycle onset, all three
onset rules agree in every cell, and all four configurations vary across their three seeds. The configuration
medians are **2:1 530**, **3:1 309**, **4:1 276**, and **6:1 226** cycles; the within-configuration ranges are
**91**, **49**, **40**, and **14** cycles respectively. The four configuration medians span **304** cycles from
minimum to maximum.

This closes the specific measurement gap named in D10 for this reconstructed withholding world. The artifact does
not measure the Phase L onset distribution, score a behavioral outcome, or compute an onset–outcome relation. These
are consumed design-block seeds, not the confirmatory block; no Stage B seed was allocated. Therefore this result
does not itself authorize a confirmatory run, and `status.blocked_before_run` remains true for the protocol's other
open blocker(s). The earlier command-limit attempts explain why the resumable checkpoint harness was added; the
completed run resumed successfully across bounded calls. The harness and manual document that workflow.

## D12 — The remaining blockers, named rather than implied (2026-11-03)

§D11 said the onset result "does not itself authorize a confirmatory run, and `status.blocked_before_run` remains true
for the protocol's other open blocker(s)". That parenthesis was a placeholder. The blockers are now named below, and
every one of them is a decision rather than a piece of analysis:

| # | what is open | what would close it | who |
| --- | --- | --- | --- |
| 1 | **The world family.** §5a's flag resolves when a dated decision names the family the run uses. Both quantities now exist on one world: `DI` onset is measured there (all twelve design-block cells uncensored, onsets differing across seeds and configurations) and the withheld endpoint's per-world standard error is measured on the same world's cells. Nothing technical is missing. | a dated decision recording that the withholding world is the Stage B world, and what `revision_held_out` becomes in it | the owner |
| 2 | **The horizon tail.** §4 fixes the horizon at confirmation + 101, and the harness plans each world at its configuration's Phase L confirmation index. The measured onsets put most cells inside that horizon and one outside it (`2:1`, seed `20261023`), which is a question about the margin rather than a defect in the measurement; protocol §4 records the arithmetic. | a dated rule: a high quantile of onset, a per-world horizon, or an eligibility rule that excludes a truncated follow-up | the owner |
| 3 | **The granularity gate.** `resolution_confirmed` is still `false` in `docs/stage_b_protocol.json`. The method is now measured on design-block cells, and the withholding world's cells clear the assumed gap; a flag that moved because an agent decided it had been answered would be the defect this sequence exists to prevent. | the owner reads the precision measurement and records the gate's disposition, before any world runs | the owner |

**None of the three is analysis.** Each is a sentence in a decision record, and writing it here would be the agent
choosing the experiment after the authorisation -- the defect §D8 stopped on.

**What is closed by measurement, so the record does not read as if it were still open.** The checkpoint's `rng_state`
field snapshots a generator no Stage B cell draws from: `organica/sleep.py` uses `_rng` only in the `stochastic`
retention lottery, the engine's policy is `salience`, and no Stage B module overrides it. The resume path is tested
against an uninterrupted run rather than asserted, and the equality check is shown to catch a resume that did not
restore its database. Journal §172; `tests/test_stage_b_onset_resume.py`; `tests/test_stage_b_protocol.py`.

## D13 — The three decisions, recorded (2026-11-03)

The owner approved all three actions listed in §D12. Each is recorded here with the evidence it rests on and the
number it does or does not change. None of the three allocates a seed, generates a world or starts a run.

**1. The world family: the run uses the withholding world.** `benchmarks/stage_b_stream_withholding.py` builds a
reconstruction of the scale-stream family whose declared transition `early_0 -> late_0` is refused by conditioned
sampling while the organism is exposed, and `revision_held_out` is scored there on that world's declared withheld
tag pairs at the world's own behavioural window, by the readout whose precision is measured in
`docs/stage_b_endpoint_precision.json`. Both quantities §D8 found in different worlds now exist in one: `DI`
onset is measured on it (twelve design-block cells, none censored) and the withheld endpoint's precision is
measured on it. Protocol §5a carries the closure beside the finding, which is kept as the record of why the
choice was needed. `status.blocked_before_run.blocked` is **false** in `docs/stage_b_protocol.json`, with the
world named and `still_not_runnable_because` recording that no runner exists and no seed is allocated.

**2. The horizon: an eligibility rule, not a longer block.** A world is eligible iff `onset + 101 <= its
horizon`, so its follow-up is complete inside the world built for it; a world whose onset lands later is reported
with its onset and horizon and excluded from the relation, never truncated and never scored at a boundary. On the
twelve design-block cells the rule excludes **1** (`2:1`, seed `20261023`, onset **602**, horizon **640**) and the other
**11** are eligible. **No horizon, block size, seed or total changes**, so the committed block stays at 720
worlds and 373,320 cycles. The price is stated rather than hidden: late-emerging worlds leave the relation rather
than being measured against a short follow-up, which §4 warns is the worse error, and the exclusion count is
reported per configuration. Protocol §4 carries the rule.

**3. The granularity gate: confirmed on the measured precision.** `docs/stage_b_stream_withholding.json`
measures the four claimed configurations on design-block cells with the withheld count per world and a per-world
standard error from resampling that world's withheld transitions. Twice that standard error is **0.0019 to 0.0067**
nats against the **0.05** assumed gap, in every cell, so `resolution_confirmed` is **true** and its evidence is
named beside it. The limit is recorded in protocol §3.1 rather than softened: the cells are design-block, and the
*saturated* rule still consumes the run's own realised precision.

**Runner (2026-11-03, after this decision).** `benchmarks/stage_b_runner.py` now implements the design recorded here. It refuses a pre-assigned seed until an allocation record exists, so the decision to spend the block is still the owner's, and it refuses the four spares unconditionally. Nothing in this paragraph resumes the decision or changes a number in it.

**What this does not do.** It does not allocate a seed, generate a world, write a runner, or compute any relation
between onset and behaviour. `status.seeds_allocated` and `status.worlds_run` are both 0, and allocating the
block remains the separate act §D2 describes. Journal §173.

## D14 — The `2:1` shortfall stands as a consequence of the clock (2026-11-04)

The owner's decision, recorded in their words: the `2:1` shortfall is a consequence of the planned clock and
the eligibility rule and is not something another run with the same clock could resolve; a re-centred clock
would require a new pre-registered study.

**The arithmetic it rests on.** `horizon - 101` equals the planned confirmation cycle in every configuration, so
eligibility reduces exactly to `onset <= planned confirmation`. The scoreable fraction of an arm is therefore the
fraction of its onsets that arrive by the clock the protocol set for it. `2:1`'s clock is **539** and its
131 observed onsets run 479–579 with median **547**: **47** of 180 qualified,
**84** produced an onset between 540 and 589 (observed, ineligible, unusable), and
**49** never produced a sustained onset. The other arms sit below their clocks and scored 180 of 180.

**What this decision does.** It closes the question of whether to repeat the arm. A repeat with the same clock
reproduces about 47 of 180 by construction, so no seed would buy anything; and a re-centred arm is a
different question -- a clock at 589 would score 131 of 180 at
9.9 h, with an interval shrinking only by `sqrt(47/131)`,
from 0.7227 to about 0.4329, which would still span zero around the observed
+0.1819. It would need its own pre-registration, its own prediction and its own allocation.

**What this decision does not do.** It does not re-score the block's verdict, which stands as recorded
(§D13's protocol, journal §186); it does not allocate a seed -- all 720 remain spent and the four spares
`700000721`–`700000724` remain undrawn with substitution closed; it authorises no run; and it commits to no
re-centred study. If one is wanted later, it starts at a new pre-registration, not at this record.
