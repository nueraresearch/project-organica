# Functional structure — pre-registration (V1)

**Status: committed before any cell has run under it, and before the harness is
built.** No seed named here has been read by any study in this repository. Nothing
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
transitions than the strongest simple model, and the margin's lower uncertainty bound
cleared zero. If the transfer window also moved, the same statement holds for
transitions withheld from all formation exposure.

**Would not mean:** that Organica "understands" the law, that the margin generalizes
beyond this world family and this engine, that the closed study's transfer failure is
reversed, or that any of it is evidence of general intelligence. A pass on the
primary window alone is held-out generalization; only the co-primary window speaks to
transfer, and only within this design.

**Would not mean, on a fail:** that the engine forms nothing useful. It would mean
that under this scoring rule, at this capacity, on these worlds, the formed structure
did not beat a tuned simple baseline by the pre-committed margin — and the provenance
diagnostic would say whether the support behind the readout was mostly self-sourced.

## 10. Build status

**Not built.** The endpoint needs a scoring harness that does not exist yet: a
log-loss readout over held-out pairs for every arm on one exposure stream, the
comparator sweep with its tuning split, the gate audit with its failing controls, and
the formation recorder wired in as a diagnostic. The provenance runner measures
occurrence, not probability, and is not this harness.

Nothing in this document authorizes running that build, and no cell of any block may
run until the harness and its gates are committed and the design block has passed.
