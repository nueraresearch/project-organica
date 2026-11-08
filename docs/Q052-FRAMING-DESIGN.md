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
