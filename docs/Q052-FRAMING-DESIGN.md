# Q052 framing design — is `burst_L1`'s late collapse competition loss? (Q052)

**Status: a framing design, not a preregistration and not an experiment.** It specifies the one
measurement that decides whether Q053 may test a competition-preserving mechanism on two world
families or must stay `lattice_L1`-scoped. It allocates no seed, fixes no capability bar, changes
no engine file, and runs no cell. The owner ordering that makes it a prerequisite is action 51 in
`docs/USER-MANUAL.md`.

## 0. The observation that forces the question

`docs/long_delay_capability_burst_L1_calibration.json` (seed 20302801, 300 cycles) measures the
same four decay arms as Q051 on the second family: shipped `0.95` ends with **3** theories and
holds 2-5 through the late window; `0.99` ends with **0** and is zero across the whole late
window; `0.9925` ends with **0** with late counts between 0 and 3; `1.0` ends with **3**. The
artifact sets `contrast_ready: false`, because the shipped arm is alive at 300 and the Q051
contrast needs a dead shipped arm.

Two things follow. The lattice arm pair cannot transfer, which is already recorded. And the
survival ordering is **not monotone in the decay factor** on this family: the shipped factor
survives, an interior factor dies, and the ceiling survives. Survival ordering alone therefore
cannot say whether the collapse is the same mechanism or a different one, which is exactly the
question Q053's scope depends on.

## 1. What is measured, and what is not

The lattice census is measured and is the control (`docs/decay_competition_probe.json`, engine
`0.13.0`, arm FULL, factor 0.9924, seeds 20302701-20302703): at the death cycle no subject
retains two competing hypotheses (`subjects_with_competing_at_death` is empty) while six subjects
still retain two pairs each; the last live top theory is `bravo` at 866 = 433 + 433;
`retained_at_death` holds 13 pairs; the label is SAME_PAIR and P1-P3 all hold.

Nothing equivalent exists for `burst_L1`. That artifact records `world: lattice_L1` and a single
`factor: 0.9924`; the capability instrument has a family selector
(`benchmarks/long_delay_capability.py`, `stream_for(..., family=...)`, with `burst_L1` built from
`organica.scale_streams.burst_stream`), but the competition probe does not.

## 2. The instrument (specified, not built)

`benchmarks/decay_competition_probe.py` is extended with one parameter, `--family`, selecting the
same `stream_for` the capability instrument already uses. Nothing in `organica/` changes.

Each probe cell must record, in addition to the fields the lattice artifact already carries:
`family`, `last_live_cycle`, `death_cycle`, `top_theory`, `theories_at_last_live`,
`theories_at_death`, `subjects_with_pairs_at_death`, `subjects_with_competing_at_death`,
`retained_at_death`, and two new totals, `edge_mass_at_last_live` and `edge_mass_at_death`, where
edge mass is the sum of the retained pairs' `support_count`.

Because the burst arm's late counts are not terminal — the `0.9925` late series rises and falls
inside its own window — the probe records the **census at every live-to-dead and dead-to-live
transition** across the late window, not one snapshot. A single snapshot of an intermittent
series is not a representative measurement.

The lattice control runs in the same block, on the same instrument, and must reproduce cycle
299 live and 300 dead with 866 = 433 + 433 and an empty competing census. If it does not, the
block is VOID and no classification is made.

## 3. Pre-committed classification

Definitions, using the field names above. `mass_ratio` is
`edge_mass_at_death / edge_mass_at_last_live`.

| Label | Condition |
| --- | --- |
| `SAME_COMPETITION_LOSS` | Every probed burst death cell has an **empty** `subjects_with_competing_at_death`, at least two subjects in `subjects_with_pairs_at_death`, at least one subject with two or more competing hypotheses at the last live cycle, and a `mass_ratio` no lower than the lattice control's minus 0.05. |
| `DIFFERENT_SUPPORT_COLLAPSE` | Any probed cell has a `mass_ratio` at least 0.05 below the control's, so support mass falls with competition rather than after it. |
| `DIFFERENT_COMPETITION_PRESENT` | Any probed cell has a non-empty `subjects_with_competing_at_death`, so theory formation failed while competition was still available — a selection or admission failure, not competition loss. |
| `DIFFERENT_INTERMITTENT` | The probed arm shows two or more live-to-dead transitions in the late window, so its collapse is not a terminal event at all. |
| `VOID` | The control does not reproduce, fewer than two dying cells are captured, or the census is incomplete. |

`SAME_COMPETITION_LOSS` requires unanimity across cells. One cell with a different label is
enough to reject it, because Q053's scope decision cannot rest on a mixed mechanism.

The control's own `mass_ratio` must be at least 0.90 for the block to be admissible. If it is
not, the premise imported from the lattice probe — that supports do not collapse at death — is
false on its own re-measurement, and the framing stops as VOID rather than comparing against a
control that no longer means what it did.

## 4. What each label decides

| Label | Q053 scope | Next deliverable |
| --- | --- | --- |
| `SAME_COMPETITION_LOSS` | Two families permitted, matched arms, one mechanism. | Q053 mechanism choice and preregistration, naming both family pairs. |
| any `DIFFERENT_*` | `lattice_L1` only. | `burst_L1` gets its own diagnosis; no two-family protocol. |
| `VOID` | Unchanged. | Re-run the framing instrument; no conclusion either way. |

## 5. The shipped-arm problem the framing has already exposed

On `burst_L1` the shipped `0.95` arm is alive at 300, so the Q053 comparison — shipped `0.95`
against `0.95` plus one mechanism — has **no dying control on that family**. A two-family
protocol must therefore either use a dying burst arm (`0.99` or `0.9925`) as its control and say
plainly that it is not the shipped build, or keep the intervention contrast on `lattice_L1` and
use `burst_L1` only to replicate the mechanism. This record does not choose between them; it
records that the choice is forced and must not be made silently inside a preregistration.

## 6. Seeds and cost

The framing needs a fresh seed block, disjoint from the threshold block (20302701-20302703), the
twelve-seed decay replication (20301201-20301212) and the burst calibration (20302801). **No block
is named here**; naming it belongs to the preregistration that follows this record. Cost is one
probe cell per arm and seed with the existing instrument, plus the lattice control cell. No
capability endpoint is scored, and no prediction, revision or adaptation task runs.

## 7. Falsifiers

- The burst census disagrees with the lattice census on any of the four counters: not the same mechanism.
- The control fails to reproduce: VOID, not DIFFERENT.
- An arm never dies in the window (`0.95`, `1.0`): that arm is not evidence, and is reported as not applicable, never as agreement.
- An intermittent series sampled once and read as terminal: a measurement defect, not a classification.

## 8. Stop condition and scope

One instrument, one classification, one record. **No intervention is built from this record, no
capability endpoint is scored, no engine file changes and no seed is allocated.** This is not a
preregistration: it fixes what would count as same and as different, not a bar, a block or an
adoption rule. It may be fixed if it is found wrong; it may not grow into a second instrument or
a second question.

## 9. What this does not claim

Nothing here says whether `burst_L1`'s collapse is competition loss. No cell has run on the second
family's competition census, no mechanism is chosen, and no Q053 transfer is established. It also
does not claim the two families differ in difficulty: the calibration measures survival of decay
arms, not capability, and it records `contrast_ready: false`.

## 10. What the run returned (2026-11-08)

The framing instrument ran: `benchmarks/competition_census.py`, three fresh burst seeds
(20302901-20302903) at factor 0.9925, and the lattice control (seed 20302701, 0.9924)
through the same code path. The control reproduced the committed census exactly -- cycle
299 live, 300 dead, `bravo` at 866 = 433 + 433, empty competing census at death -- so the
instrument is the same instrument and the second family is measured on it.

**The label is `VOID`, and it is void on this record's own admissibility floor, not on the
family.** The control's `mass_ratio` is **0.578** against the required 0.90: at the death
cycle, retained support mass falls to 58 % of its last-live value. The premise imported
from the lattice probe -- that supports do not collapse at death -- is therefore false
under this record's own definition of edge mass. Section 3 says that case stops the framing
as VOID rather than comparing against a control that no longer means what it did, and that
is what happened.

**What the defect is.** Edge mass as defined here sums every retained hypothesis's
`support_count`. At the death cycle the theory layer is empty but thirteen pairs are still
retained, so the drop is the mass of the hypotheses that died with the layer -- most
plausibly the competing ones. The definition cannot separate the cause from the consequence:
if competition collapse prunes the competitors, total retained mass falls whether or not
support collapse is the mechanism. A floor of 0.90 on this quantity tests the premise with a
measure the hypothesis itself predicts will fall.

**What is left open.** No classification was made, so Q053's scope is unchanged and stays
`lattice_L1`-only pending a fixed instrument. The burst cells' own ratios (0.314, 0.184,
0.041) and censuses are in `docs/q052_competition_census.json` as observations, not as a
verdict. The fix this record needs before a re-run is a mass definition that is not moved by
the death it measures -- the support mass of the pairs retained at the last live cycle,
tracked through death, rather than the total retained at each cycle -- and a floor
calibrated on a world where the answer is known. It is recorded here and **not applied**:
changing the definition after reading this control would be re-scoring the protocol.

## 11. Amendment A2, and what the amended run returned (2026-11-08)

Section 10 named the fix and left it unapplied. This is the amendment that applies it, recorded
before the cells were read: the A1 artifact stands as written (`VOID`), and A2 runs beside it as a
second artifact rather than editing the first.

**Two changes, and two disclosures.** (1) The mass is now the support mass of the hypotheses
retained at the **last live cycle**, tracked through death: a cohort member that is gone counts as
zero, and a hypothesis that was never in the cohort is never counted, so pruning outside the
cohort cannot move the ratio. (2) The floor is calibrated, not asserted: on committed lattice
cells at the control's own family and factor, floor = the lowest observed cohort ratio minus
0.05. The control's seed (20302701) is **excluded** from that calibration, because a threshold
computed from the cell it judges is not a threshold. The probed block is fresh --
20303001-20303003, disjoint from the threshold block, the twelve-seed replication, the burst
calibration and the A1 block. The control keeps seed 20302701 because its job is to reproduce a
specific trajectory.

**Disclosure 1: the calibration has no spread.** The two calibration cells return the same
cohort ratio to six decimals (0.578178), and the A1 control's total-mass ratio was also 0.578.
At the lattice death the retained set is a subset of the cohort, so the two definitions coincide
there, and the lattice death transition is the same in mass terms across seeds. The consequence is
that the calibrated floor (0.5282) is the known world's own value minus the margin.

**Disclosure 2: the admissibility gate cannot fire.** Because the floor is the known world's
value minus 0.05, a control that reproduces the known world passes it by construction. The gate
is retained for the record but it carries no information, and the label below does not rest on
it; it rests on the burst cells' ratios against a threshold whose provenance is the known world.
A1's extra 0.05 collapse margin is removed for the same reason: with a calibrated floor, a line
0.05 below it would sit below the known world's own ratio.

**The control, under the amended mass.** Reproduced exactly: 299 live, 300 dead, `bravo` at
866 = 433 + 433, empty competing census. Its cohort is 17 hypotheses at the last live cycle, 13 of
which survive to death, and their mass falls 4,106 -> 2,374, a ratio of **0.578** against the
floor of **0.528**.

**The probed cells.** Each seed dies once, terminally:

| Seed | Last live | Death | Top at last live | Cohort | Survived | Mass at last live -> death | Ratio | Pairs at death | Competing at death |
|---|---|---|---|---|---|---|---|---|---|
| 20303001 | 133 | 134 | `foxtrot` 642 | 14 | 11 | 1,394 -> 429 | 0.308 | 2 (`novaaaa`, `nvlpaaa`) | 0 |
| 20303002 | 130 | 131 | `delta` 629 | 16 | 12 | 1,386 -> 437 | 0.315 | 2 (`novaaaa`, `nvlpaaa`) | 0 |
| 20303003 | 130 | 131 | `bravo` 636 | 15 | 7 | 1,981 -> 67 | 0.034 | 0 | 0 |

**The label is `DIFFERENT_SUPPORT_COLLAPSE`.** No cell is intermittent, none retains a competing
census at death, and every cell's cohort mass falls below the calibrated floor -- by 0.21 to 0.49.
Under the amended definition the burst deaths are not the lattice signature: the pairs' own
supports are what fails at the death, far more sharply than in the known world.

**What this decides.** `burst_L1` is not a second instance of the lattice competition-loss
mechanism, so Q053 stays `lattice_L1`-scoped and burst cannot be pooled into a two-family
mechanism claim. Q052's framing is answered to that extent and closed in the registry.

**What it does not decide, and the confound that matters.** The burst cells die at cycles 131-134
and the control at 300, so a lower one-step mass retention may reflect *where in the growth and
decay history the death lands* rather than a different mechanism: at 131 the pairs' supports are
smaller and the top cluster is smaller (629-642 against 866). The design contains no control for
death age, so this record establishes that the **signature** differs, not **why**. A mechanism
choice for Track B therefore still rests on the lattice cells alone, and a death-age-matched
comparison is the missing cell, not a reparsed one.

The amendment's artifact is `docs/q052_competition_census_a2.json`, its page is
`docs/Q052-COMPETITION-CENSUS-A2.md`, its module is `benchmarks/q052_amendment_a2.py` -- a layer
over the same instrument, which calls `competition_census.run_cell` and changes only the census
arithmetic -- and its tests are `tests/test_q052_amendment_a2.py`.
