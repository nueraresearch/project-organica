# Confirming transition-probability strength before adoption — pre-registration

**Status: PREREGISTRATION, 2026-11-06. The engine is unchanged. Option 2r is a
lead candidate, not a fix.** Nothing in `organica/` is edited until every
condition in §7 holds.

The candidate is: prediction strength becomes
`count / out_counts[source]` — the `transition_prob` the engine already
computes for ranking (`organica/sleep_extraction.py:453-478`) — with
`STABLE_THRESHOLD` recalibrated. `docs/DECAY-FIX-OPTIONS.md` measured it as the
only arm alive at 300 cycles on one seed and one matrix world.

That is enough to justify a confirmation run and not enough to change the
engine. This document fixes the run before it happens.

## 1. Why the first probe cannot decide adoption

Three limits, all of which this design must answer:

* **One seed, one world.** The probe used seed `20261023` and the
  `L1_hub1_t3_disjoint` lattice. It cannot separate a mechanism from a favourable draw.
* **The stable set is small.** The surviving arm held 18 stable
  prediction edges at cycle 300. Eighteen edges cannot establish a 0.95
  precision: zero false assertions in eighteen is consistent with a true
  precision well below 0.95. §6 replaces a bare precision floor with a
  zero-false-assertion rule and a minimum-size condition for estimating
  precision at all.
* **A global threshold is hostile to hubs.** A uniform valid transition at
  out-degree 12 has probability about 0.083, below the probe's 0.15 threshold.
  Whether Option 2r merely moves the starvation from low-degree to high-degree
  worlds is untested, so degree is a stratifying variable, not a nuisance.

## 2. Arms

| arm | strength | threshold | decay |
|---|---|---|---|
| **S** shipped | `count / source_frequency` | 0.30 | 0.95 |
| **T** option 2r | `count / out_counts[source]` | `tau*`, calibrated in §3 | 0.95 |

Everything else is identical: same stimulus, cycle counts, seed set, analysis.
T is a harness subclass until adoption; the engine files are not touched by the
confirmation run.

## 3. Threshold calibration — separate seeds, sealed before held-out

* **Calibration seeds:** `20261201`–`20261208` (8). They are not held-out seeds
  and are not used anywhere else in the repository.
* **Calibration worlds:** degrees `2, 3, 6, 12`, built with
  `organica.scale_streams.expanding_triangles(n=d)` and
  `organica.branch_streams.lattice_stream`, 300 cycles each.
* **Grid:** `tau` in 0.05, 0.075, 0.10, 0.15, 0.20, 0.25, 0.30.
* **Selection rule, fixed now:** among the values that pass the liveness gate on
  **every** calibration cell and keep precision at or above 0.95 on every cell,
  choose the one with the **highest mean coverage**; break ties toward the
  larger `tau` (fewer assertions). No other criterion may be used.
* **One global threshold.** Per-degree thresholds are a different mechanism and
  are out of scope; if no single `tau` qualifies, record **"no global threshold
  clears all degree regimes"** and stop. That is a finding about the mechanism,
  not a failed run.
* **Seal:** `tau*`, the calibration artifact and its sha256 are written to
  `docs/confirmation/calibration.json` before the first held-out cell. The
  held-out runner reads `tau*` from that file and never recomputes it
  (rule 19).

## 4. Held-out design

* **Seeds:** `20261210`–`20261229` (20 per regime). Before the first held-out
  cell, these are checked mechanically against every seed-bearing artifact
  under `docs/`; any overlap aborts the run.
* **Degree regimes:** `d` in 2, 3, 6, 12. Each world's **realised out-degree is
  measured and recorded**; if it differs from the intended `d`, the cell is
  NOT COMPARABLE and is excluded (rule 13a). The degree axis must be live
  before any cell is read.
* **Stationary phase:** 300 cycles, both arms.
* **Shift phase:** 80 cycles of A then 40 of a relabelled B with a disjoint
  vocabulary, at `d = 3` and `d = 12` only, to test revision under the regime
  where the threshold is most likely to bite.
* **Task endpoint:** frozen-model held-out next-tag prediction at 200 train /
  100 test cycles (`benchmarks/heldout_prediction.py`), per arm, seed and
  degree; the comparator is the best of its Markov and decayed baselines.
* **Scoring labels:** the world's directed edge set is derived from the
  stimulus by the engine's own lookback rule. Labels score the selector; they
  never enter it.

## 5. Endpoints

| endpoint | definition | direction |
|---|---|---|
| liveness | at least one theory in the final 10% of cycles and mean beliefs at least 2 | **gate only** |
| precision | stable prediction edges that are world edges, over stable edges | higher |
| coverage | stable prediction edges that are world edges, over world edges | higher |
| false assertions | count of stable edges that are **not** world edges, per cycle | lower |
| revision (B) | B-edge coverage 40 cycles after the vocabulary shift | higher |
| revision (A) | share of stable edges still belonging to A at the end | lower |
| task outcome | held-out log-loss over known tags (primary); Brier and F1 diagnostics | lower |

Precision and coverage are reported together and never as one number. A change
that raises coverage by admitting false assertions is not an improvement.

## 6. Liveness is a comparability gate, not a success

A cell whose arm fails liveness is **NOT COMPARABLE**: excluded, reported as
excluded, never scored as zero, never replaced. Passing liveness only makes a
cell readable. It is not evidence for adoption and is not counted as one.

## 7. Decision rule — adoption requires all of these (as amended by §13–§15)

Evaluated once, by the committed analysis script, on the held-out cells only.

1. **Comparability.** Both arms pass liveness in at least 90% of cells within
   every degree regime. Otherwise the overall verdict is NOT COMPARABLE and no
   adoption question is answered.
2. **High-degree safety.** At `d = 12`: T passes liveness on at least 90% of
   seeds; median coverage is not more than 0.05 below S's; and T does not lose
   the task endpoint (a 99% paired interval whose upper bound is below zero is
   a loss).
3. **Honesty of the assertion set.** Zero false assertions in at least 90% of
   cells, and precision at or above 0.95 wherever a cell holds at least 40
   stable edges. (Below 40 edges, only the zero-false rule is used — a ratio on
   eighteen edges is not a precision estimate.)
4. **Task improvement.** The paired difference `S - T` in held-out log-loss,
   pooled over degrees 2, 3 and 6 and paired by seed and degree, has a 99%
   interval whose lower bound is above zero; and no one of those regimes shows
   a loss by the same interval rule.
5. **Coverage.** Median coverage for T is at least S's in each of degrees 2, 3
   and 6, and no regime drops by more than 0.05.
6. **Useful revision.** At `d = 3`, T reaches B coverage of at least 0.5 forty
   cycles after the shift and its A share is no higher than S's. At `d = 12`,
   T's B coverage is not more than 0.10 below S's.

If every condition holds, adopt Option 2r as a new engine version (§9). If any
fails, the run reports which, with the label that fits:

* *improves low-degree only* — 4 or 5 fails at `d = 12` while lower degrees pass;
* *trades precision for coverage* — 3 fails while 4 passes;
* *no task effect* — 4 fails with 3 and 5 passing;
* *not comparable* — 1 fails.

No condition may be re-read, relaxed or dropped after the results are seen.

## 8. Sample size and what it can separate

Twenty seeds per regime give a paired 99% interval on log-loss and on coverage.
A coverage difference of about 0.10 is separable at this n; smaller differences
are reported as unresolved rather than as wins. Precision at eighteen edges is
**not** separable from 0.90 — which is why §7 condition 3 uses a zero-false
rule and requires 40 edges before quoting a precision. This is stated now so
that a later small-`n` precision figure is not read as a 0.95 result.

## 9. What adoption would then require

In order, and only after §7 passes:

1. A new engine version (`0.13.0`), with the version bump, changelog entry,
   identity record and regression test in the same change.
2. The decay fix recorded as a decision with its evidence, and the option probe
   retained as the counterfactual.
3. A 3,000-cycle matrix rerun on the new version, with the reference arm's
   liveness checked before any metric is ranked.
4. Only then the affected paper experiments, each keeping its `v0.9.0` results
   beside the new ones and labelled.

## 10. Exclusions and stopping

* Censored or non-comparable cells are reported and excluded, never replaced.
* No seed is added, dropped or substituted after the first held-out cell.
* The harness build is finished when the degree audit, the calibration seal,
  the held-out runner and the analysis script exist, and the shipped arm
  reproduces its known failure on the matrix stimulus. No feature may be added
  afterwards; defects may be fixed.
* No paper, release or engine change happens on the strength of the probe.

## 11. What would falsify the mechanism, not just the threshold

* `tau*` selected below 0.075 — about `1/12` — means the "fix" is a threshold
  low enough to admit a uniform degree-12 transition, and the mechanism claim
  collapses into a parameter change.
* T's advantage disappearing once false assertions are matched to S's means the
  gain was volume, not precision.
* A `d = 12` collapse means the measure relocates the starvation instead of
  removing it.

## 12. Status at registration

* Engine: unchanged; `organica/` has no edits from this line of work.
* Probe: `docs/DECAY-FIX-OPTIONS.md`, one seed, 300 cycles.
* Calibration: not run. Held-out: not run. No cell exists.
* Harness: `benchmarks/decay_confirmation.py`, with `audit`, `calibrate`,
  `heldout` and `analyze`. Artifacts written with `--smoke` are marked
  `"protocol": false` and are not verdicts.

## 13. Amendment 1 — high degree and the shipped baseline (2026-11-06, before any cell)

The harness audit and `benchmarks/hub_degree_probe.py` establish a closed form:
for a hub of degree `N`, the shipped strength is `count / source_frequency =
1/N`, so at `STABLE_THRESHOLD = 0.30` the shipped arm forms **no** stable hub
edges at `N >= 4`. Requiring it to pass liveness at degrees 6 and 12 would make
the run non-comparable by construction, and the resulting "failure" would be a
property of the baseline, not of the candidate.

This amendment was written before any calibration or held-out cell was run. The
text of §1–§12 above stands; where the two differ, this section governs.

* **§7.1 comparability.** The transition arm must pass liveness in at least 90%
  of cells in **every** regime. The shipped arm must pass only at degrees 2 and
  3. Its absence at 6 and 12 is recorded as the shipped baseline's known
  ceiling and reported beside the result; it is not a failed comparison and it
  is not a win for the candidate.
* **§7.2 high-degree safety.** At degree 12 the transition arm must be live in
  at least 90% of cells, carry zero false assertions in at least 90% of cells,
  and reach a median coverage of at least 0.5. There is no paired shipped
  comparison at this degree.
* **§7.4 task.** Paired only where both arms are live (degrees 2 and 3). At 6
  and 12 the transition arm's task score is reported descriptively and may never
  be counted as a win over an arm that formed no structure.
* **§7.5 coverage.** Compared at degrees 2 and 3. At 6 and 12 coverage is
  reported as an absolute, because there is no shipped denominator.
* **§7.6 revision.** Degree 3 stays paired as written. At degree 12 the
  transition arm must reach an absolute B coverage of at least 0.40 forty cycles
  after the shift.
* **Labels.** `improves low-degree only` now means the **transition** arm fails
  the degree-12 conditions, not that the shipped arm is absent there.

## 14. Amendment 2 — the degree ladder and the seed blocks (2026-11-06, before any cell)

The harness's design audit and seed scanner found two defects in §3–§4. Neither
is a result: no calibration or held-out cell had been run when this was written.

**Degrees are measured, not assumed.** `scale_stream` emits `h a`, `a b`, `b h`
per triangle, and the engine's 3-event lookback therefore records **two** hub
targets per triangle. The realised hub out-degree is `2n`, not `n`: the audit
measures 4, 6, 12 and 24 for 2, 3, 6 and 12 triangles. The regimes are now the
measured out-degrees **2, 4, 6 and 12**, built from 1, 2, 3 and 6 triangles.
Degree 3 is not constructible in this family and `degree_world` rejects an odd
target rather than rounding it. Degree 6 is the old L1 working point, and the
threshold grid is unchanged: it still brackets the degree-12 transition
probability `1/12 ≈ 0.083` between 0.075 and 0.10.

**The seed blocks are chosen by scan, not by hand.** Both hand-picked blocks
failed the harness's own overlap check: `20261201`–`20261208` is used by
`docs/regime_shift_results.json`, `docs/acquisition_compositional_gate.json`,
`docs/provenance_diagnostic.json` and six `reusable_knowledge_*` artifacts, and
`20270101`–`20270108` was already consumed as well. The blocks are therefore the
first contiguous unused windows above 20300101, computed from every `seed`-named
integer under `docs/`: calibration **`20300101`–`20300108`**, held-out
**`20300109`–`20300128`**. The scan reruns on every protocol
invocation; any later artifact that consumes these seeds makes the run refuse to
start, and no block is ever re-picked after a cell is run.

**Superseding §13's degree-3 references.** Paired task and coverage comparisons
use degrees 2 and 4; the vocabulary shift is measured at degrees 4 and 12; the
degree-12 revision floor stays absolute at 0.40.

## 15. Amendment 3 — the task endpoint must clear the strongest simple baseline (2026-11-06, before any cell)

Rule 11 and rule 25(a) require the strongest simple comparator and its lower
bound, never the weakest. §7.4 pairs the shipped arm against the candidate, which
answers "does the candidate beat the shipped arm" but not "does either arm
predict the world". A candidate can win that pair while both arms lose to a
bigram, and that win would be reported as a task improvement.

The task endpoint already computes the best of the Markov and decayed baselines
with the held-out instrument's own scoring functions on the degree world (the
substitution §4 implied, recorded here). Condition 4 now also requires
**non-inferiority to that baseline**: the transition arm's median held-out
log-loss may not exceed the best baseline's median by more than 0.05 nats in
either paired regime (degrees 2 and 4). Failing it is labelled `worse than the
simple baseline` and is not counted as a task win over the shipped arm. The
adoption claim remains shipped-versus-candidate; this check only disqualifies a
"win" between two arms that both lose to a simple learner.

No calibration or held-out cell had been run when this was written.
