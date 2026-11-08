# Competition preservation as the next development target (Q053)

**Status: a design record, not an experiment and not a decision to change the engine.**
It names the measured failure mode, five candidate interventions, and the comparison that
would test one of them. It selects no mechanism, allocates no seed, fixes no bar, and runs
no cell. The owner decision that motivates it is action 50 in `docs/USER-MANUAL.md`.

The evidence is in `docs/decay_support_probe.json`,
`docs/decay_competition_probe.json`, `docs/long_delay_capability_confirm.json` and
`docs/long_delay_capability_burst_L1_calibration.json`.

## 1. What the probes established

At **0.9924**, the last live cycle is **299** and its top theory is `bravo` at
**866 = 433 + 433**. At cycle **300** the theory layer is empty, but the beliefs are not:
six subjects (`bravo`, `charlie`, `delta`, `echo`, `foxtrot`, `golf`) still retain **two
pairs each**, and each subject retains **one competing hypothesis plus one
`high_structural_significance` marker**. No subject retains **two competing hypotheses**,
which is what theory formation requires. The failure is **competition collapse**, not loss
of support mass.

At **0.9925** on cycle 300 the top theory is `alpha` at **1309 = 438 + 438 + 433**, so the
same world can retain three competing hypotheses when the decay factor is high enough.

Q051 then showed that extending persistence does not automatically convert this survival
into a capability-sized ranking gain: the confirmatory late median was **+0.0265**
(bootstrap interval **[0.0111, 0.0355]**) against the frozen **0.0412** bar, with **9 of
10** seeds positive, an early median of **+0.0119**, and growth in **6 of 10**. The
persistence route is closed for adoption, not because the late effect is zero, but because
it is neither large enough nor isolated enough.

## 2. The question

**Can competition be preserved or regenerated without globally reducing forgetting, and
does that produce a capability gain over shipped 0.95?**

The comparison is deliberately not another decay sweep. It is:

| Arm | Configuration |
| --- | --- |
| control | shipped `0.95`, no mechanism, no-op subclass |
| treatment | shipped `0.95` plus one competition mechanism |

Holding decay at 0.95 is what makes the mechanism separable from persistence. A treatment
that only works by lowering the global decay factor is a persistence result and does not
answer this question.

## 3. Candidate mechanisms (none chosen)

Each candidate targets the measured boundary directly. The list is a design space, not a
shortlist, and no candidate may be adopted from this record.

| Candidate | What it changes | Main risk |
| --- | --- | --- |
| **Second-best retention floor** | Keep at least two competing hypotheses per active subject through consolidation. | A stale minority survives on old evidence and competes with the current best. |
| **Diversity floor on retained hypotheses** | Reserve part of the hypothesis budget for competing expectations rather than filling it by strength alone. | Displaces high-support structure and may lower precision. |
| **Protected minority-hypothesis pool** | Give minority expectations a separate budget that global allocation cannot consume. | The pool can become a museum of dead structure; cap accounting must be explicit. |
| **Competition regeneration after consolidation** | If a subject falls to one hypothesis, re-derive a competing one from recent evidence. | Regenerated competition may be unsupported, which is fabrication rather than preservation. |
| **Subject-level competition quota** | Require an active subject to contribute at least two competing hypotheses before global allocation fills the remaining slots. | It may dilute the global budget and be specific to the seven-tag lattice. |

The first two preserve existing structure; the third protects it; the fourth creates it;
the fifth allocates it. They are different interventions and must not be merged into one
"competition" arm without a mechanism-level prediction for each.

## 4. What a protocol must measure

**Intermediate (manipulation check, judged first).** The number of subjects with at least
two competing hypotheses in the late window, and the per-subject competing count. The
treatment must raise this quantity above the control; otherwise the mechanism did not
operate and the capability endpoint is unrun, not null.

**Primary capability endpoint.** The same online next-cycle recall@5 instrument used by
Q051: early **40-90**, late **240-300**, `k = 5`, median per-seed gap. The bar must be
calibrated on design seeds that are not judged, and frozen before the confirmatory block.

**Manipulation check.** The shipped arm's late theory count is zero by cycle 240 and the
treatment retains theories through 300. If both arms die, or both survive, the block is
void rather than a capability comparison.

**Controls that must be able to fail.** A no-op subclass must reproduce the shipped arm
exactly; a deliberately wrong competition count must fail the scorer; and the mechanism
must change competition without changing the global decay constant.

## 5. Decision needed before a protocol is frozen

1. Choose **one** mechanism and its parameter (for example, a floor of two, a pool size, or
   a quota), with a mechanism-level prediction for why it preserves competition.
2. Fix the competition metric and the window before seeing the confirmatory capability
   gap.
3. Name a fresh seed block and a design block that calibrates the bar but is not judged.
4. Decide whether the capability test uses `lattice_L1`, `burst_L1`, or both. The
   `burst_L1` calibration shows the decay arms reverse there, so it cannot inherit
   Q051's arms; it needs its own matched pair if it is used.
5. Freeze an adoption rule: a capability gain is necessary but not sufficient; the
   mechanism must also not reduce early ranking or global forgetting beyond a stated
   bound.

## 6. Falsifiers

- The mechanism does not raise the late competition count: an unrun experiment, not a null.
- Competition rises but late recall@5 does not: preservation is not sufficient for the
  capability claim.
- The treatment only wins when the global decay factor is also lowered: a persistence
  confound, not a competition effect.
- Competition rises by retaining stale or unsupported pairs: the intervention manufactures
  competition rather than preserving it.
- Early ranking falls: the mechanism buys late competition at a cost the protocol must
  price, not ignore.

## 7. Stop condition and scope

One mechanism, one protocol, one confirmatory block. **No decay-factor sweep, no further
0.9924/0.9925 verification, and no additional persistence diagnostic on `lattice_L1` is
planned.** The mechanism is applied in-process as a `SleepService` subclass; the frozen
engine files are untouched, and no engine version adopts it without a recorded decision
after the capability bar is met.

This record may be fixed if it is found wrong. It may not grow into a second mechanism,
a second endpoint, or an experiment without a preregistration. Q052 remains a separate
second-family replication question and is not answered here.

## 8. What this does not claim

No mechanism has been chosen or implemented. No cell has run. Nothing here shows that
competition preservation improves capability, that the five candidates are feasible, or
that the effect would generalize beyond the tested world. The strongest supported sentence
remains the Q051 one: persistence produces a small ranking benefit in this synthetic world,
but it is neither large enough nor isolated enough to satisfy the capability criterion.
