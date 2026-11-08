# The last surviving support at the 0.9924/0.9925 edge

Generated from `docs/decay_support_probe.json`. The probe reuses the forced-decay runner
and captures the engine's own theory, hypothesis and pre-decay edge counts on seed 20302701.

## Direct measurement

| Factor | Last live cycle | Death cycle | Top theory | Theory support | Competing hypotheses |
| --- | --- | --- | --- | --- | --- |
| 0.9924 | 299 | 300 | bravo | 866 | bravo->charlie 433; bravo->alpha 433 |
| 0.9925 | 300 | 301 | alpha | 1309 | alpha->echo 438; alpha->delta 438; alpha->charlie 433 |

Every hypothesis `support_count` equals its pre-decay temporal edge count exactly: the counts
are 433-438, not a low-count threshold. The 0.9924 last theory is a pair of 433-count supports;
the 0.9925 top theory is three supports (438, 438, 433).

## What actually changes at cycle 300

At 0.9924, cycle 300 has **zero theories** even though the top hypotheses still carry hundreds of
counts. The engine forms a theory only when one subject has at least two competing hypotheses.
At 0.9924 the last such pair is at cycle 299 (`bravo -> alpha` 433 and `bravo -> charlie` 433);
at cycle 300 every subject has only one retained hypothesis. At 0.9925, subject `alpha` still
retains three competing hypotheses at cycle 300 (`echo` 438, `delta` 438, `charlie` 433), so the
theory survives.

The limiting quantity is therefore the **number of competing supports per subject**, not the
absolute support count and not a count near 5. The 433-438 supports are roughly two orders of
magnitude above `PREDICTION_MIN_COUNT`.

## Correction to the earlier inference

An earlier inference from the death times suggested an effective support of about 49 counts.
The direct probe does not support that. The measured supports are 433-438 per hypothesis; the
49-count figure assumed a single support crossing 5 and ignored the two-hypothesis/retention
requirement. The threshold label is unchanged; the mechanism is corrected.

## Scope

One seed (20302701), one world (`lattice_L1`), one arm (FULL), one factor pair and 300 cycles.
This is a mechanism diagnostic, not a new threshold and not an adaptation or capability result.
