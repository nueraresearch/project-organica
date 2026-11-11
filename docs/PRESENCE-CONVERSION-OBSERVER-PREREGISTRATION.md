# Presence to assertion: the conversion observer (PRESENCE-CONVERSION-1)

Generated from `docs/presence_conversion_observer_prereg.json` by `python -m benchmarks.presence_conversion_observer --render-prereg`. Do not edit by hand.

**Status: FROZEN, RUN. Authorised 2026-11-10 and run.** The verdict is `OBSERVER NOT NEUTRAL`; the artifact is `docs/presence_conversion_observer_run.json` and the result page is `docs/PRESENCE-CONVERSION-OBSERVER-RESULT.md`.

Question 3 of the conversion program (`docs/PRESENCE-ASSERTION-CONVERSION-PREREGISTRATION.md`), frozen on its own so the three internal stages can be observed without waiting for Q1 or for the Q2 cap block. It uses Q3's stage chain and loss rule without renaming them, keeps X1-X7, and adds X8: an observer-off control on the same seeds that must reproduce the published audit row, because an observer that changes behaviour is not an observer.

## The question

On the shipped engine at the shipped cap, where do world edges leave the conversion path between raw presence and final assertion - and which observed stage is the first dominant loss, with C (constructed candidates), E (eligibility reason) and R (rank) recorded rather than inferred?

## The hypothesis, stated before any cell

The audit counts the two endpoints and the ladder traces one cap level with an offered arm that raises the cap, so neither records what the engine constructed inside a shipped run. If the pre-cap candidate list can be recorded without changing the returned window, the loss can be placed at construction, admission or assertion before any mechanism is proposed.

**Prediction.** The observer-off and observer-on arms are identical on every seed, C contains every world edge that meets the engine's minimum count, E explains every present edge that is not in C, and the first dominant loss falls at one observed step of the retained chain.

**Falsifier.** Any seed on which the observer changes presence, the ordered admission window, the admitted union or the final assertion: the observer is then not behaviour-neutral and Q3 is void rather than a conversion result.

**Alternative.** The engine may consult MAX_PREDICTIONS somewhere other than the final truncation; then lifting the cap inside the call changes the engine's own construction and the neutrality control catches it. That outcome is a void instrument, not evidence about the conversion path.

## Why the two earlier blocks cannot answer this

| Block | Artifact | Reading | Why it does not answer Q3 |
| --- | --- | --- | --- |
| same-build presence/assertion audit | `docs/presence_assertion_audit_0.14.0.json` | 112 of 112 world edges present, 40 asserted on the witness seed at the shipped cap | it counts the endpoints only; nothing between presence and assertion is observed |
| presence-to-assertion ladder trace (exploratory) | `docs/presence_assertion_ladder_0.14.0.json` | 423 misses: 0 never offered, 171 offered and not admitted, 252 admitted and not asserted | its offered arm raises the cap in a recording subclass, so it is a counterfactual, not an observation of the shipped run; `C`, `E` and `R` are not recorded |
| cap-only preregistration | `docs/presence_cap_prereg.json` | freezes one changed constant with no observer inside construction | it cannot see which candidates the cap truncated or what order they carried |

## The observer, and the one method it replaces

| Field | Value |
| --- | --- |
| Engine | 0.14.0 |
| Engine edit | **none** |
| Observer | `benchmarks.presence_conversion_observer.StageObserverSleepService` |
| Base class | `organica.sleep.SleepService` |
| Overrides | `_build_predictions` |
| Mechanism | the engine's own `_build_predictions` is called with `MAX_PREDICTIONS` temporarily at the diagnostic ceiling, the full pre-cap list is recorded, the shipped cap is restored, and the engine's own first `MAX_PREDICTIONS` rows are returned unchanged; no construction, ranking or filtering is reimplemented |
| Why it can fail | if `MAX_PREDICTIONS` is consulted anywhere but the final truncation, the lifted call changes the engine's own list and the observer-on window differs from the observer-off window; X1 catches it on the first seed |

The observer calls the engine's own method with `MAX_PREDICTIONS` at the diagnostic ceiling of 1000000000, records the full candidate list, restores the shipped cap of 40 and returns the engine's own first 40 rows. It reimplements no construction, ranking or filtering. Neutrality is the identity `engine(cap=40) == observer(cap=40)`, and it is checked on every seed rather than assumed from reading the code.

## What C, E and R are

| Stage | Symbol | Definition | Recorded as |
| --- | --- | --- | --- |
| Candidate | `C` | candidates constructed before the cap | one row per candidate: edge, rank, strength, support, ratio, admitted |
| Eligible | `E` | why a present edge did or did not become a candidate | one outcome per present world edge: `constructed`, `below_prediction_min_count`, or `unexplained` |
| Scored | `R` | the order the engine gave each candidate | the row's rank in the pre-cap list, with its strength and support |

**An identity this engine makes.** Construction already applies the eligibility filters, so `C` and `E` hold the same edges: `E` is the reason record, not a separate retention step, and reporting it as one would invent a stage. A later engine that separates construction from eligibility gains a step; this record would then be re-registered rather than re-read.

## The design

| Field | Value |
| --- | --- |
| Arms | observer off (shipped `SleepService`), observer on (`StageObserverSleepService`) |
| Seeds | 20611501, 20611502, 20611503, 20611504, 20611505, 20611506 |
| Bootstrap | 20611507 |
| Cycles | 120 |
| Cells | 12 (2 arms x 6 seeds) |
| Witness cell | seed 20261100, observer off; it must reproduce the published audit row |
| Pairing | same seed, same world, same cap; only the observer differs |
| World | the Gate-13 compositional world, warmup and acquisition as in the audit |

**Freshness.** The six seeds and the bootstrap are fresh: they appear in no other docs artifact. The witness seed is the published audit's first seed and is the only reused seed; it is a control, not a cell in the reading.

## The behaviour-neutrality control

For each seed the two arms must produce identical presence, identical ordered admission windows, identical admitted union and identical final assertion. The comparison is ordered: a set comparison would pass a reordered window, and a reordered window is a changed engine. `X1` fails on the first difference and the verdict is `OBSERVER NOT NEUTRAL` — the block is void, no stage reading is made, and the instrument is fixed in a new block.

## Gates

| Gate | Requirement |
| --- | --- |
| `X1_observer_neutral` | for every seed, observer-off and observer-on produce identical presence, identical ordered admission windows, identical admitted union, identical final assertion and identical asserted world edges; the first difference fails the gate |
| `X2_stage_complete` | every observed stage has per-edge membership and a nonzero denominator, and E leaves no present edge `unexplained` |
| `X3_no_unobserved_imputation` | no stage is assigned a count without an observation; an unobserved stage is named and excluded |
| `X4_same_object` | `A_W` is a subset of `P`; a failure is an object mismatch |
| `X5_witnesses` | at least one positive `A_pred` edge and one negative `P` minus `A_W` edge per seed |
| `X6_seed_axis` | at least two distinct stage fingerprints across the six seeds |
| `X7_determinism` | a fresh-process rerun of the first seed reproduces its stage fingerprints and its ordered windows |
| `X8_control_reproduces_audit` | the witness cell (seed 20261100, observer off) reproduces the published audit row: present count, asserted count and asserted fingerprint |

## The loss rule

For each seed, count world edges retained at each observed stage. The first dominant loss is the earliest stage with the largest absolute drop in world-edge count; ties go to the earlier stage. Report the relative share beside the absolute drop, because a large relative loss on a small denominator is not the same finding. A stage whose denominator is zero is not measurable and is excluded, never reported as 0.0. A negative drop is a gain and is reported as one. An asserted edge that was never admitted is a bypass, reported separately and counted neither as retention nor as loss.

Retained chain: `W -> P -> C -> S_cycle -> S_ever -> A_pred`.

Ties go to the earlier stage. Relative shares are reported beside the absolute drop and never name a suspect on their own. A stage with a zero denominator is not measurable and is excluded, never reported as `0.0`. An asserted edge that never passed admission is a bypass: reported separately, counted neither as retention nor as loss.

## The decision table

- **X1 fails on any seed** -> **OBSERVER NOT NEUTRAL**.
  - Decision: void the block; fix the instrument and register a new block, never re-read this one
  - Licences: nothing about conversion; the divergence is a fact about the observer, not about the engine
- **any X gate other than X1 fails** -> **VOID**.
  - Decision: no reading is made; repair the harness and register a fresh block
  - Licences: nothing; the block is inadmissible
- **X gates pass but C, E or R is unobserved on some seed** -> **PARTIAL OBSERVATION**.
  - Decision: report the observed chain only, name the unobserved stage, and stop Q3 at the last observed stage
  - Licences: a narrower target than the draft's; no loss may be assigned to an unobserved stage and no mechanism may be proposed from the gap
- **every X gate passes and C, E and R are observed on every seed** -> **CONVERSION OBSERVED**.
  - Decision: publish the per-seed stage table, the first dominant loss stage and the bypass split; take the named stage to a separate mechanism preregistration
  - Licences: target selection only: a mechanism preregistration with its own control; no engine change, no defect verdict and no capability claim

## Adoption, withdrawal and stop

Only `CONVERSION OBSERVED` produces a target, and what it licenses is a separate mechanism preregistration that names the stage it intervenes on, its own control and its own withdrawal rule. No arm of this block edits `organica/`, and no verdict here changes the engine.

**Withdrawal.** The reading is withdrawn if the observer class gains a second override, if the witness stops reproducing the audit row, if the engine pin moves without a version bump, or if a later block finds the observer-off arm was not the shipped build. A withdrawn reading is recorded, not deleted.

**Not authorised by this record.** running the cells before the owner records authorisation; editing any file under organica/; assigning a loss to an unobserved stage; proposing or implementing a mechanism from the stage table; re-scoring the audit, the ladder or the cap preregistration

**Stop condition.** One block, two arms, six seeds, one stage table. When it is analysed the Q3 question is closed in one of the four verdicts above. A follow-up may read these cells at a different resolution; it may not add a seed, swap an arm or re-run a failing seed. Any intervention needs its own preregistration.

## Cost and authorisation

12 cells, 120 cycles each, two arms. The block has been run; the verdict is `OBSERVER NOT NEUTRAL`.

**Authorisation.** The draft program's freeze checklist requires the owner's authorisation before a run, and the owner gave it on 2026-11-10: `Authorize all runs`, covering all three frozen conversion blocks. The grant is recorded in `docs/AUTHORISATION-PRESENCE-CONVERSION-1.md` and quoted there; the record stays FROZEN, NOT RUN and no cell has run. `--measure`, `--cell` and `--finish` still validate the grant on every invocation. A grant is not a run: executing the first cell is a separate, dated act.

## What this does not claim

This record measures where world edges leave the conversion path on one world family, one engine build and one cap, with a benchmark-only observer. It does not show that any stage is a defect, that a mechanism is responsible, that raising the cap or changing the ranking would help, or that the assertion endpoint is wrong. `U`, the readout/use stage, is not observed. A named loss stage is a target for a separate preregistration, not a licence to edit the engine.
