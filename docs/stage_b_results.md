# Stage B: the planned-onset relation, and how the block resolved it

**Verdict: `NOT SUPPORTED`.** The block ran 720 allocated worlds across four
configurations and 587 were scored. No configuration showed the predicted relation --
earlier behavioural onset of the late structure predicting a lower held-out log loss -- with an
interval excluding zero.

This document is the standalone record of the block: the design as committed, the measured
relation, why `2:1` cannot carry a verdict, and the reproduction check that was run against the
engine after the verdict was recorded. Every number below is substituted from
`docs/stage_b_runner.json` and `docs/stage_b_rerun_check.json` by script, not typed.

## 1. What was run

The design is `docs/DECISION-STAGE-B-SEQUENCE.md` §D13, implemented by
`benchmarks/stage_b_runner.py`. Each world is a scale-stream world with its declared transition
withheld while the organism is exposed; a world's onset is the first cycle at which the late
structure has been sustained for ten consecutive cycles; the behavioural window is fixed at the
planned confirmation plus a 50-cycle learning phase and a 50-cycle test phase; the score is the
mean pairwise log loss of the frozen backoff readout on the withheld pairs in that window. A world
is eligible iff its onset plus 101 cycles fits inside its horizon, so a follow-up is never
truncated and a world is never scored at a boundary.

| configuration | planned confirmation | horizon | worlds |
| --- | --- | --- | --- |
| `2:1` | 539 | 640 | 180 |
| `3:1` | 404 | 505 | 180 |
| `4:1` | 362 | 463 | 180 |
| `6:1` | 329 | 430 | 180 |

Each configuration's 180 seeds were pre-assigned, the block of 720 was allocated once, and the
four spares `700000721`-`700000724` were never drawn. No world was regenerated, no seed was
substituted and no cell was re-run to replace a result.

## 2. The result

| configuration | worlds | scored | ineligible | censored | onset median | Spearman | 0.9833 interval | predicted sign held |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `2:1` | 180 | 47 | 133 | 49 | 515 | +0.1819 | [-0.1950, 0.5277] | no |
| `3:1` | 180 | 180 | 0 | 0 | 333 | -0.0328 | [-0.2106, 0.1502] | no |
| `4:1` | 180 | 180 | 0 | 0 | 275.5 | -0.0507 | [-0.2173, 0.1168] | no |
| `6:1` | 180 | 180 | 0 | 0 | 232 | -0.1077 | [-0.2812, 0.0745] | no |

The aggregation rule committed before the run, quoted from the artifact: *"supported only if the predicted relation holds with an interval excluding zero in every claimed configuration; otherwise mixed, never a best-configuration finding"*.
The verdict is `NOT SUPPORTED` because the condition was not met in any of the four
configurations. The three larger arms have point estimates in the predicted direction and intervals
that include zero; `2:1` has a positive point estimate and an interval that also includes zero.
`NOT SUPPORTED` is the whole-block outcome, not a best-configuration finding, and no arm is
described as a win.

Reproduce it with:

```
python benchmarks/stage_b_runner.py --verify docs/stage_b_runner.json
```

which re-derives the allocation membership, the spares, the 180 cells per configuration, each
cell's eligibility from its own onset and horizon, each trajectory's length against its cycle
count, the measurability of every scored outcome, and then recomputes §5 from the cells and
compares every Spearman, interval and the verdict with the file.

## 3. `2:1` cannot carry a verdict, and a repeat cannot change that

`2:1`'s planned confirmation is **539** cycles. Of its 180 worlds, **47**
were scored, **133** were ineligible and **49** of those
never produced a sustained onset inside their horizon. The remaining **84** onsets fell
between 540 and 589 -- after the clock, so their behavioural window
would have preceded them. The observed onsets span 479-579.

That is why this is **under-powered, not a reversal**. Its interval is 0.7227 wide,
2.2 times the narrowest of the other three (0.3341),
and it contains zero with a point estimate in the wrong direction: a large interval around a
noisy estimate is not evidence against the prediction, and this document does not read it as one.
Because eligibility reduces exactly to `onset <= planned confirmation` -- the horizon is the
confirmation plus 101 in every arm -- a repeat with the same clock reproduces a comparable
scoreable fraction by construction. The owner recorded on 2026-11-04 that the shortfall stands as
a consequence of the planned clock (§D14), that a repeat is not authorised, and that a re-centred
clock would be a new pre-registered study with its own prediction and its own allocation.

## 4. Verification: the analysis, and the engine

Two different things were checked, and they license two different claims.

**The analysis.** `--verify` audits the assembly where it lives: allocation membership, the four
spares, the cell counts, eligibility against each cell's own onset and horizon, trajectory length
against cycles run, measurability against each outcome, and a recomputation of the whole §5
analysis. It passed, and its own controls are tested -- an honest block is accepted, a drawn spare
is refused, and an unsupported verdict is caught.

**The engine.** `--verify` recomputes the analysis from the committed cells; it does not ask
whether the engine would produce those cells again. That gap was closed after the verdict was
recorded, on four cells chosen before anything was re-run by an outcome-independent rule (the 90th
cell of each configuration's block).

| configuration | seed | onset (assembly -> re-run) | eligible | score | cycles differing |
| --- | --- | --- | --- | --- | --- |
| `2:1` | 700000090 | 562 -> 552 | no -> no | -- -> -- | 10 of 589 |
| `3:1` | 700000270 | 326 -> 332 | yes -> yes | 0.154001 -> 0.154001 | 35 of 454 |
| `4:1` | 700000450 | 279 -> 279 | yes -> yes | 0.147971 -> 0.147971 | 0 of 412 |
| `6:1` | 700000630 | 259 -> 250 | yes -> yes | 0.147733 -> 0.147733 | 71 of 379 |

One cell reproduced exactly. In three, the trajectory differs from the cycle where the sustained
run is detected onward, and the onset moves by a few cycles; in every measurable cell the score is
identical to six decimals and no cell's eligibility changes. A cell run twice inside one parent process is bit-identical, so this
is not randomness in the world or in the readout. It is the engine's tag scoring, which iterates
`set` unions of string tags (`organica/sleep.py`, `_score_tags`) and then sorts by frequency with a
stable sort, so ties resolve in the process's string-hash order. The same cell run once per hash
seed settles it: `PYTHONHASHSEED` 0, 1, 2, 3, 4, 5 give onsets
250, 259, 250, 259, 250, 259 -- alternating -- with a score of
0.147733 in every run.

What that means, stated at the width of the check: the committed onsets are reproducible to a few
cycles but not bit-identically across processes, and the block is one such draw. Four cells cannot
estimate how often a shift of this size moves a cell across its clock, so the size of the effect
on the aggregate is **not measured** and is not reported as zero. What can be said is that the
verdict does not rest on single cells: every interval contains zero by a margin far wider than the
shifts observed here, and the three measurable cells scored identically.

## 5. What this does not establish

- It does not establish the relation in either direction. `NOT SUPPORTED` means the block did not
  find it under this design; it is not evidence that the relation is absent in general.
- It says nothing about `2:1` beyond "under-powered at this clock". The arm is uninformative, not
  negative.
- It is one world family, one engine, one block of 720 worlds, and one readout frozen at the
  planned window. Nothing here is a claim about intelligence or about transfer.
- The engine's cycle-level output is hash-order sensitive; the aggregate effect of that on this
  block was not measured. The dependence is behaviour of the frozen engine, so it stays: removing
  it is a separately versioned engine change (§D15), and this block is not regenerated under that
  engine.
- V2 is not authorised, no seed remains unspent in this block, and the four spares stay undrawn.

## 6. Provenance

- Design and decisions: `docs/DECISION-STAGE-B-SEQUENCE.md` §D13 (the three decisions, 2026-11-03)
  and §D14 (the `2:1` shortfall accepted as a clock consequence, 2026-11-04), and §D15 (the
  tie-break stays in the frozen engine, 2026-11-04).
- Protocol: `docs/stage_b_protocol.md`; machine-readable `docs/stage_b_protocol.json`.
- Cells and analysis: `docs/stage_b_runner.json`, 10,000 bootstrap
  replicates at level 0.9833, PRNG seed 20261107.
- Reproduction check: `docs/stage_b_rerun_check.json`.
- Narrative record: `research-journal/phase_g_findings_20261021.md` §186 and §187.
