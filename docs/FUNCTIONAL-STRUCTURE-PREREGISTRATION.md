# Functional structure — pre-registration (V1)

**Status: committed before any cell had run under it; both blocks have since run once.**
The scoring layer of §11.2–§11.3 and the engine binding of §10 are built and gated, the design
block passed every gate (§10.1), and the confirmatory block ran once (§10.4). When the
constants below were fixed, no seed named here had been read by any study in this repository;
that pre-commitment is what the run tests, and the run did not revise it. Nothing
below was chosen from a result of this protocol; the constants it fixes are carried
over from protocols that are already closed, and they are named with their source.

This is **not** an amendment to any closed protocol. It does not touch the closed
reusable-knowledge study's verdict, seeds or thresholds, and it does not touch the
formation-provenance study's association result. It is a new question with a new
endpoint.

Related: `docs/REUSABLE-KNOWLEDGE-PREREGISTRATION.md` (the closed study whose world,
withholding rule and comparator sweep are reused), `docs/FORMATION-PROVENANCE-PREREGISTRATION.md`
and `docs/FORMATION-PROVENANCE-STUDY.md` (the association study, whose instrument is
reused here only as a **diagnostic**), `docs/V2-CAPACITY-DESIGN-BRIEF.md`,
`docs/G13-D-DIAGNOSTIC-PLAN.md` (the diagnostic that motivates fixing capacity).

## 1. Question

> Does the structure Organica forms during development improve held-out prediction
> on the same generative law, against simple baselines that received the same
> exposure, under proper probability scoring?

The unit of the claim is a **held-out transition**, scored by **log-loss in nats**.
It is not an occurrence count, not a retention index, and not a margin over a base
rate.

## 2. What is measured

- **Score.** Mean log-loss per held-out tag pair, in nats, for the probability the
  arm assigns to the observed next-event tag given the current one. Lower is better.
- **Primary window.** All consecutive pairs in cycles 150–200 of the generated
  world — the closed protocol's held-out generalization window, never shown to the
  organism.
- **Co-primary window.** The withheld-relation subset of that window: pairs whose
  cell transition was withheld from every formation exposure. This is the transfer
  limb, and it is scored separately and reported whether or not the primary moves.
- Both shapes are reported per seed and pooled; the primary is the pooled primary
  window, not the better of the two.

## 3. Arms

1. **Organica.** The frozen engine, capacity `MAX_PREDICTIONS = 1000`, the
   structure-edge readout with its calibrated smoothing `alpha = 256.0`. Both
   constants are carried over unchanged: capacity from the G13-D scope and the
   closed study's variant, alpha calibrated on seed `20261099`. Neither is retuned
   here, and `alpha` is not a free parameter of this study.
2. **Strongest simple baseline.** The closed protocol's comparator sweep — replay,
   bigram, decayed bigram — each swept over its declared grid, with the best
   configuration selected on a tuning split that is excluded from the fitting rows.
   The cell counter is reported as a privileged reference and is not eligible to be
   the strongest baseline, exactly as in the closed protocol.
3. **References, not arms.** Base rate and the closed-form Bayes ceiling, reported
   beside the two arms so a margin can be read against the task's headroom.

**Exposure symmetry.** Every arm is fitted on the identical 110-cycle formation
stream, including warmup, with the tuning split fixed at the last 15 formation
cycles and excluded from every fit. No arm receives data another does not. Where
the closed protocol says a baseline may not be handicapped, this protocol adds: it
may not be handicapped *and* it must be tuned.

## 4. Endpoint and bar

**Endpoint:** `delta = log-loss(Organica) − log-loss(strongest baseline)` on the
primary window, pooled over the confirmatory seeds, negative meaning Organica
scored better.

**Bar, fixed now:** the **upper** bound of a 98.33 % interval on `delta` must be
**below zero**. An interval that contains zero is reported as **no improvement
detected**, not as equivalence. The interval is a percentile interval from 10,000
cluster-bootstrap resamples of the confirmatory seeds, because pairs within a seed
are not independent; the method is recorded with the number.

The co-primary transfer window is reported with the same interval and its own
counts. It does not gate the primary verdict, and a primary pass with a transfer
window that does not move is reported as **held-out generalization only**, with the
word transfer withheld.

## 5. Seeds

Fresh, and disjoint from every seed used in this repository:

| block | seeds | use |
|---|---|---|
| design | `20270201`–`20270205` | harness audit, liveness and denominator feasibility only; no endpoint |
| confirmatory | `20270206`–`20270220` (n = 15) | the endpoint of §4, run once |

`20261201`–`20261205` are the closed study's calibration cells, `20261206` is burned,
`20261207`–`20261226` its confirmatory set, and `20270101`–`20270120` the provenance
study's design and confirmatory blocks. None of them is read, extended or re-scored
here.

## 6. Gates

Each gate can fail, and a failure stops the protocol rather than shrinking it.

- **G1 liveness.** On every design seed, Organica must form at least one prediction
  with measurable support at the freeze point. A readout with nothing in it is not a
  learner.
- **G2 denominators.** Every arm must be scored on the same non-zero set of held-out
  pairs, and every design seed must contribute at least one scored pair in each
  window. A zero denominator is reported **not measurable** and excluded; it is never
  a score of zero.
- **G3 the harness can fail.** The audit must separate the Bayes ceiling from a
  one-transition learner on the same windows, must reject a deliberately degraded
  readout (a copy with a fraction of its edges removed), and must show both
  comparisons firing. A harness that cannot fail is decoration.
- **G4 instrument neutrality.** The formation recording hook must reproduce the
  engine's own candidates exactly, the same comparison the provenance instrument
  already makes on synthetic controls.
- **G5 calibration independence.** `alpha`, the capacity, the comparator grids and
  the tuning split are fixed in this document. No value is chosen, adjusted or
  re-selected on a confirmatory seed.
- **G6 the disqualifier can fire.** Before any study seed is touched, the attribution
  rule in §11.3 must demonstrate on synthetic fixtures, with no engine run, that it can
  return each of its four outcomes: a world-majority margin **passes**; a self-majority
  margin **withholds** and labels the result **not a transfer result**; an unattributed
  margin **withholds as not attributable**; and an empty positive margin is **not
  evaluable**, never a share of zero. The fixtures must also show the rule firing at
  exactly 0.50 and not firing at 0.4999, must classify `world == self` as self-majority,
  and must show that relaxing the threshold to 0.90 stops the self-majority fixture from
  withholding. That last check is the point: it proves the fixture carries the signal,
  rather than the rule being unable to fire at all. A disqualifier that cannot withhold
  is not a disqualifier, and the provenance clause would be decoration.

## 7. The provenance diagnostic (compulsory, never the success measure)

Origins are recorded at formation, as in the provenance study, and reported for every
arm and window: the share of asserted edges whose recorded source rows were world
events, and the per-claim support behind the readout.

**Pre-committed disqualifier, following the project's standing rule.** If Organica's
margin is carried mainly by support whose source rows are the organism's own sleep
payloads, the result is reported as **not a transfer result** even if the score
clears the bar. The diagnostic is reported for every outcome, including a null one,
and it never becomes a second success criterion: it can only disqualify a claim, not
manufacture one.

## 8. Stop rules

- **One build, one stop condition.** The build is complete when §2–§7 are
  implemented and the gates can fire; no feature may be added afterwards. A defect
  may be fixed, and a fixed defect is disclosed.
- **No endpoint on the design block.** The design seeds audit the harness and
  nothing else; their scores are not read as a result.
- **One confirmatory run.** No seed added, dropped or re-drawn; no re-run on these
  seeds; no parameter changed after a number is seen.
- **No threshold movement.** The bar in §4 is fixed. If it fails, it fails, and the
  failure is reported with the interval that produced it.
- The closed study and the provenance study are untouched. A failure here does not
  reopen either.

## 9. What a result would and would not mean

**Would mean, on a pass:** on these worlds, with equal exposure and a tuned simple
baseline, the structure the engine formed assigned better probabilities to held-out
transitions than the strongest simple model, and the **upper** bound of the 98.33 %
cluster-bootstrap interval on `delta` lay **below zero**. That is §4's bar, restated here
in the same direction so the two sections cannot be read apart. The direction is not
incidental: `delta` is Organica minus baseline, so negative means Organica scored better,
and a *lower* bound above zero would be evidence of the wrong direction rather than a
pass. An interval containing zero is **no improvement detected**, never equivalence.

**What "moved" means on the co-primary window.** The same rule, on the withheld-relation
cells only: the window **moved** if the upper bound of its own 98.33 % interval on its own
`delta` is below zero; it **did not move** if that interval contains zero, and a primary
pass is then reported as **held-out generalization only** with the word transfer withheld;
and it moved **the wrong way** — reported as reversed on that window, not as a null — if
its lower bound is above zero. The co-primary interval does not gate the primary verdict,
and neither window is re-scored because the other disagrees.

**Would not mean:** that Organica "understands" the law, that the margin generalizes
beyond this world family and this engine, that the closed study's transfer failure is
reversed, or that any of it is evidence of general intelligence. A pass on the
primary window alone is held-out generalization; only the co-primary window speaks to
transfer, and only within this design.

**Would not mean, on a fail:** that the engine forms nothing useful. It would mean
that under this scoring rule, at this capacity, on these worlds, the formed structure
did not beat a tuned simple baseline by the pre-committed margin — and the provenance
diagnostic would say whether the support behind the readout was mostly self-sourced.

## 10. Build status and run order

**Built, and the design block has run once.** `benchmarks/functional_structure.py` implements
the measurement contract of §11.2 and §11.3 — cells, per-cell loss, the four attribution
outcomes — and its G6 fixtures fire with no engine module imported and no study seed read.
`benchmarks/functional_harness.py` is the engine binding: one formation run per seed over the
110-cycle stream, the calibrated readout, both windows, and gates G1–G5.
`docs/functional_structure_design_audit.json` is the audit artifact of step 2. It records no
`delta`, and `confirmatory_seeds_run` is 0.

**Run order, fixed now.** The earlier wording of this section forbade a run that the design
block *is*: it said no cell of any block may run until the harness and its gates are
committed and the design block has passed, and the design block cannot pass without running
its five seeds. The sequence is therefore three steps, and each step names what it is allowed
to produce.

1. **Build and commit.** The harness, its gates and their failing controls are committed and
   passing. No confirmatory seed is read at this step.
2. **Design block only — `20270201`–`20270205`.** These five seeds are run once, for liveness
   (G1), denominators (G2), the harness-can-fail control (G3), instrument neutrality (G4) and
   the recorded disqualifier wiring of §11.5. They are an **instrument audit, not a result**.
3. **Confirmatory block, only if the design block passes — `20270206`–`20270220`.** One run,
   no seed added, dropped or re-drawn. **This step has since run: see §10.4.** If any design gate fails, the protocol stops at step 2:
   the failure is disclosed, the defect is fixed, the fixed harness is re-audited on the same
   five design seeds, and no confirmatory seed is touched.

**What a design seed may and may not produce.** The design run forms gate and wiring diagnostics.
It computes Organica's loss and the baseline's loss on every realised cell of both windows,
because §11.3's share is defined on that difference; what the lock withholds is the **pooled**
`delta` of §4, not the per-cell losses it is built from. No design-seed margin is compared with
§4's bar, quoted as a result, or carried into the language of §9. §11.5's disqualifier status is
computed and recorded as an **instrument reading**: on a design seed there is no study claim yet
for the rule to withhold, so its output is not a verdict about Organica in either direction, and
its shares are not reported. A design number may appear only inside a diagnostic that is labelled
as one.

**The endpoint stayed locked until step 3.** No confirmatory seed was generated, no arm was fitted
on one, and no preliminary look at the endpoint was taken until every design gate had passed and
that passing run was committed. Step 3 has since run (§10.4); that lock was released by the owner's
authorisation, not by anything in this section.

**What that lock covers, corrected (2026-11-02).** Its first wording said the endpoint is "not
formed" on a design seed, and that was too strong to be true. §11.3's share is defined on per-cell
paired losses, so the wiring step computes Organica's loss and the baseline's loss on every
realised cell of both windows and subtracts them; those per-cell differences are the endpoint's
building block, and they exist. What is withheld is the statistic and the verdict: the pooled
`delta` of §4 is **not formed on design seeds**, no design margin is compared with §4's bar, and
nothing says in which direction the endpoint would fall. The artifact declares both lists under
`endpoint_boundary` and labels what it does compute an **endpoint-derived diagnostic**. Recording
the overstatement is the point — a lock that claims more than it does is a false assurance, and
this one was caught by reading the artifact instead of the prose.

### 10.1 What the design block found (2026-11-02, before any confirmatory seed)

**Every gate passed on all 5 design seeds.** The readout is live (G1: 325–340
edges, every window's realised cells supported), every arm scores the same 12768-cell denominator in
both windows (G2), the harness separates the law from a one-transition learner and rejects a
readout with half its edges dropped (G3), the recording hook leaves the frozen candidates
identical (3995 with the hook and 3995 without, same
readout table — G4, run once on the first seed), and every fixed constant is the committed one
with the hash seed pinned (G5). The windows hold 399 primary pairs and 93–127
withheld pairs per seed, so neither gate is measuring an empty set.

**The disqualifier wiring works, and it reports something the protocol did not anticipate.** On
the first seed the primary window's positive-margin cells split 7 world-majority,
113 self-majority and 291 unattributed; the co-primary window splits
0, 113 and 291. Both exceed the 0.50 unattributed threshold, so on this
seed §11.3 returns `not_attributable` and withholds whatever the score. That status is an
instrument reading: it is not a verdict about Organica, and no confirmatory claim exists yet for
it to withhold.

That is structural, not a property of the seed. The reason is visible in the formation record:
all 96 available relations are recorded on every seed, 92–96 of them world-majority;
but the 32 withheld relations are withheld **from formation**, so they cannot carry a world count —
12–16 of the 32 appear at all, and **0–0** of them is world-majority on
every seed (`provenance_coverage` in the artifact). A rule that withholds whenever the
unattributed share reaches 0.50 therefore withholds on the co-primary window by construction, on
every world, because the relations that window scores are exactly the ones formation never
carried.

**Consequence, recorded rather than repaired.** §11.3 as committed makes the co-primary claim
unattributable by construction, and the primary window's margin is concentrated on the same
cells, so the rule would withhold there too. Changing the threshold, dropping unattributed cells
from the denominator, or exempting the co-primary window would each be a re-scoring of a
pre-committed rule after seeing a number. That decision belongs to the owner as an amendment;
nothing in this document, and nothing in the harness, has been changed to make the rule fire
differently. At the time of the design step no confirmatory seed had been generated,
fitted or scored; §10.4 is the run that followed.

### 10.2 Recorded status of the transfer limb (2026-11-02)

**The co-primary window is scored, and its result is recorded as not attributable under the
current provenance measure.** The narrowness of that status matters more than its words: it says
the measure cannot certify a transfer claim on the withheld relations. It does **not** say Organica
failed to transfer, and it must not be read as one.

The reason is structural and is in the record. Across the five design seeds all 96 available
relations appear and 92–96 are world-majority, while only 12–16 of the 32 withheld
relations appear at all and **0–0** of them is world-majority on any seed. A withheld relation
could not have been carried by a world row, because formation never took it. Under §11.3 a pair
with sleep support only is self-majority and a pair with no record is unattributed; both withhold.
The unattributed share on the co-primary window is therefore above 0.50 **by construction** on
every world: it follows from which relations formation was denied, not from any margin. The limb
can be scored but cannot establish transfer. That share was obtained by computing per-cell paired
losses on the design seeds — §10.3 says exactly what that means — and the derivation does not
depend on the losses, because a relation formation never carried cannot acquire world support. Evidence that the engine
did *not* transfer would need a measure that could attribute those pairs, and this one cannot.

Three consequences are recorded rather than acted on:

1. **The threshold stays where §11.3 put it.** Lowering it, dropping unattributed cells from the
   denominator, or exempting the co-primary window would each re-score a pre-committed rule after
   the numbers were seen (§4, §8, and AGENTS rule 19's logic).
2. **The primary window is affected in weaker form.** Its positive-margin cells split
   7–58 world, 101–144 self and
   228–381 unattributed across the five seeds, so §11.3 would withhold there
   as well. §4's score verdict is not gated by the diagnostic — §7 makes it disqualifying for a
   transfer claim, not for the endpoint — but a primary margin reported beside "not attributable"
   is a weaker object than §7 assumed when it was written.
3. **Claiming transfer needs a different provenance measure, not a different threshold:** one that
   traces a derived structure back to the evidence it was built from. The audit-trace lineage walk
   is the existing component; the instrument used here answers "which row type carried these tags",
   which is a different question and was never going to answer this one.

**The decision this leaves open, for the owner.** Whether the confirmatory block is still worth its
one run to answer §1's question — held-out prediction against a tuned baseline — knowing that no
transfer claim is available either way. **Recommendation: run it.** §1 asks about held-out
prediction; the co-primary was added to test whether a margin survives on unseen relations, and
that test is unavailable under this measure whether or not the block runs. Declining the run would
leave §1 unmeasured as well, and running it cannot make the transfer claim worse than not running.
What the run must not be reported as is a transfer result. **Taken:** the owner authorised that
one run on 2026-11-02, for the primary question alone, and §10.4 records it. The recommendation did
not authorise it — the owner did.

### 10.3 What was actually computed and inspected (2026-11-02)

Plainly, so that nothing above has to be read between the lines.

- **Computed.** Per-cell paired losses for Organica and for the tuning-selected baseline, on the
  realised cells of both windows, for all five design seeds; arm-level window losses and
  tuning-split losses, for G3 and for the baseline-family choice. These are **endpoint-derived
  diagnostics** — the same cells and the same losses the endpoint aggregates.
- **Withheld.** The pooled `delta` of §4, any comparison of a design margin with §4's bar, any
  statement of direction, and every confirmatory statistic. `delta` is `null` in the artifact for
  exactly that reason.
- **Inspected.** The per-cell losses were read: by the attribution, which is how the share that
  §10.2 reports was produced; by G3, for the degraded-readout control; and in this document, for
  the split in §10.1 and the coverage in §10.2. The transfer measure was classified as
  un-attributable from those diagnostics.
- **Concluded.** That the current provenance measure cannot certify a claim on the co-primary
  window. That conclusion is about the instrument. It is derivable from the coverage counts alone
  — 12–16 of 32 withheld relations recorded, none world-majority — and it is not a statement about
  whether Organica transferred.

The distinction the earlier wording blurred is between a lock on a *statistic* and a lock on all
the arithmetic beneath it. With a share defined on paired losses only the first is possible.
Claiming the second was inaccurate, and the correction narrows the claim rather than widening the
permission: more is now said about what was read, and nothing new is permitted.

### 10.4 The confirmatory run (2026-11-02, one run, no re-run)

The block ran once: seeds `20270206`–`20270220`, n = 15, 432 s, artifact
`docs/functional_structure_confirmatory.json`. All 15 seeds selected the same baseline family
(bigram) on their tuning split, so §4's bar was supplied by one comparator throughout.

**Primary window — the bar was not met.** Pooled `delta` = -0.003818 nats (Organica minus
baseline); 98.33 % percentile interval from 10000 cluster-bootstrap resamples over seeds,
[-0.010802, 0.002863]. The interval contains zero, so the outcome is **no
improvement detected**. Per-seed deltas run from -0.027099 to 0.015468: the
sign flips across seeds, which is what "no improvement detected" looks like at this n rather than a
near miss in one direction. §8 fixes one run; this was it, and it is not re-run.

**Co-primary window — a large score improvement that is not a transfer result.** Pooled `delta` =
-0.359327 nats, interval [-0.369382, -0.345823], which is **improvement** on the score:
the readout assigns much better probability to the withheld relations than the tuned bigram does.
The disqualifier reports `not_attributable` on that window (world 0.000000, self
0.299193, unattributed 0.700807 of the positive margin), exactly as
§10.2 predicted from construction, and **the transfer claim is withheld whatever the score**.

**Provenance on the primary window.** Its positive margin splits world 0.003292, self
0.298208, unattributed 0.698500, status `not_attributable`. The compulsory diagnostic of §7
therefore certifies neither window's margin, and it is reported for the null result as §7 requires.

**Frozen.** This result is final for this protocol: no re-run, no seed added or dropped, no
threshold, constant or gate adjusted in its light (§8). A different question needs a new
pre-registration and a fresh seed block.

**In §9's language, and no further.** This is **no improvement detected** on the primary window: not
equivalence, and not evidence that the engine forms nothing useful. It says that under this scoring
rule, at capacity 1,000 with smoothing 256.0, on these worlds, the formed structure did not beat the
tuned bigram by a detectable margin on held-out prediction. The co-primary improvement is a score,
not a transfer: it is not attributable under this measure (§10.2), and §4 gives it no power to turn a
failed primary into a pass. Reading it as one would be the protocol becoming convenient after the
fact, which is exactly what §8 forbids.

---

## 11. Amendment 1 — executable definitions (2026-11-02, before the build)

**Why this amendment exists.** A review found three clauses that could not be
implemented without interpretation: the tuning/exposure rule, the probability score,
and the self-sourced disqualifier. A protocol that needs interpretation at build time
is not yet a protocol. This amendment fixes all three, is committed **before the
harness exists and before any cell has run**, and changes no seed, no gate, no
capacity, no alpha and no statistical bar. Where it contradicts §3 or §2, it
supersedes them and says so.

### 11.1 Exposure and tuning

The earlier text said every arm is fitted on the 110-cycle stream *and* that the last
15 cycles are excluded from every fit. Those cannot both hold.

**The rule now.** All 110 formation cycles are exposure for every arm. The prescribed
last 15 cycles are **excluded from hyperparameter selection only**; they are not
excluded from any fit. Concretely, and following the closed protocol's
`comparator_sweep`:

1. Baseline configurations are ranked by their log-loss on the tuning split (the last
   15 formation cycles, 120 events).
2. The winning configuration for each baseline family is then **refit on all 110
   cycles** before scoring. This is what the closed protocol already does, and it
   gives the baseline the larger sample, never the smaller one.
3. Organica has no fit step: it develops online over the same 110 cycles, including
   the tuning cycles, and its readout is frozen at the end of them.

So every arm sees the identical rows; the tuning cycles are held out from *selection*
and from nothing else. An arm is never fitted on fewer rows than another.

### 11.2 The probability score

"Log-loss per held-out tag pair" was imprecise. The score is the closed protocol's
`benchmarks/acquisition_baselines.py::score` with `exclude_self=True`, adopted
unchanged:

- For each consecutive held-out event pair (current event, next event), let `C` be the
  current event's tags and `T` the next event's tags intersected with the vocabulary
  `V`.
- For every `a` in `C` and **every** `b` in `V`, form one scored cell: `p = clamp(p(b|a))`
  and `y = 1` if `b` is in `T` and `b != a`, else `0`. The cell's loss is
  `-[y ln p + (1 - y) ln(1 - p)]`.
- The `b = a` cell is **kept in the denominator with label zero**, exactly as `score`
  does; it is not dropped.
- The score is the total loss over all cells divided by the number of cells. The
  denominator is therefore the number of event pairs times `|C|` times `|V|`, and it
  is reported per window.

Two-tag events therefore contribute two source tags against the whole vocabulary, not
two "pairs". There are no sampled negative examples: every vocabulary tag is scored,
and the mass on the others is the implicit negative set. This is one score, fixed
here, and it is the same quantity the closed protocol reported as log-loss in nats.

**Co-primary window.** Same cells and same denominator rule, but only over the
consecutive event pairs whose cell transition was withheld from every formation
exposure, selected by the closed protocol's own held-out filter.

### 11.3 The self-sourced disqualifier, as a rule

The earlier text named a disqualifier without defining it. It is defined here on the
same scale as the endpoint, so "carried mainly by" is a computable share.

1. **Pair support.** For an ordered tag pair `(a, b)`, the formation record gives the
   cumulative counts `world(a,b)` and `self(a,b)` of transitions whose source row was
   a world event or a sleep payload. The pair is **world-majority** if
   `world > self`; **self-majority** if `self > 0 and self >= world` (ties count
   against the claim); **unattributed** if both are zero.
2. **Per-cell contribution.** For every scored cell with `y = 1` — a transition that
   actually occurred in the held-out window — define its contribution as
   `delta = loss(baseline) - loss(Organica)` on that cell. Positive means Organica
   assigned the observed tag a better probability than the baseline did. Cells with
   `y = 0` are excluded from the attribution (they are still in the score), because
   the question is what carried the improvement on realised transitions.
3. **The share.** Let `S` be the sum of positive `delta` over cells whose pair is
   self-majority, and `P` the sum of positive `delta` over all `y = 1` cells. The
   disqualifying share is `S / P`, reported with the world-majority and unattributed
   shares and their cell counts.
4. **The rule.** If `S / P >= 0.50`, the transfer claim is **withheld** and the result
   is reported as **not a transfer result**, whatever the score. If the unattributed
   share is `>= 0.50`, the margin is reported as **not attributable** and the transfer
   claim is withheld for the same reason: provenance that was never recorded cannot
   certify a claim. Otherwise the transfer claim may be made, subject to §4.
5. **What it cannot do.** The share is a diagnostic. It can withhold a transfer
   claim; it cannot create one, cannot change the endpoint, cannot move the bar, and
   is reported for a null result as well as a positive one. `P = 0` is reported as
   **not evaluable**, never as a share of zero.

### 11.4 What is unchanged

Seeds and blocks (§5), gates (§6), capacity, alpha, the endpoint and its bar (§4),
the stop rules (§8) and the build status (§10) are unchanged by this amendment. No cell had run
when these definitions were committed, and none could run until the harness and the definitions
were committed together. Both blocks have since run — §10.1 and §10.4 record them — and this
amendment was not revised afterwards.

**Note on §10 (added afterwards, disclosed).** §10's run order was revised on
2026-11-02 in a separate commit, because its original wording forbade the design run it
depended on. The revision sequences the blocks and locks the endpoint; it changes no seed,
gate, capacity, alpha or bar, so nothing in this amendment is affected.

### 11.5 Which baseline, which window

§11.3 says "baseline" without naming one, and the study has two windows. Both are fixed
here.

**Baseline.** The attribution uses the single strongest simple comparator — the arm that
supplies the endpoint's bar in §4 — at its selected configuration, refit on all 110 rows,
scored on exactly the cells it is compared on there. It is not recomputed per cell, not
re-chosen per seed, and no cell is attributed against whichever baseline happens to favour
Organica on that cell. The `loss(baseline)` of §11.3 is that arm's loss on that cell.

**Window.** The primary window (formation cycles 150–200) supplies the headline share; the
co-primary withheld-relation window supplies its own share over its own cells. The two are
computed **separately and never pooled** — no cell, pair or margin crosses between them,
because the co-primary window exists precisely to ask whether the margin survives on
relations no arm was exposed to.

**Decision rule.** Within a window the share is pooled over the 15 confirmatory seeds, with
per-seed shares reported beside it. The disqualifier is evaluated in **both** windows, and
the transfer claim is withheld if **either** reaches the threshold. A claim therefore needs
the primary and the co-primary margin to both be world-majority attributable.

**Gate use.** On design seeds the same function is run and its status recorded. G6's
fixtures are what prove it can fire; design-seed statuses are an audit, not a result.

