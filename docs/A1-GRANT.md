# A1 grant — `A1-TARGET-FREEZE-N20-1`

**Granted:** 2026-11-15 · **Owner's words:** *"Sign updated freeze act. Grant. Run."*

**What is granted.** The 36 treatment cells and the determinism control specified by the frozen two-path manifest
(`docs/a1_two_path_manifest.json`, status `GRANTED, NOT RUN`) may be executed, on the six seeds reserved for this study,
at the cycle count and prediction cap the manifest fixes, against the target block frozen by
`A1-TARGET-FREEZE-N20-1`.

**What the grant rests on.** The act was signed on 2026-11-15 against the block `DECISION-A1-COMPETENT-ESTIMAND`
adopts: **20 / 17 / 20 / 20 / 18 / 20** rows, 115 observations over 90 unique edges, selected from the baseline-competent
population. C5 timing was re-cleared on those rows (`docs/A1-C5-TARGET-TIMING-COMPETENT.md`): no carrier reaches a
target before the cycle-4 `U`. The scorer is pinned by digest (`docs/a1_scorer_pin.json`), and `a1_result.assemble`
refuses to score if either pinned module has changed — so the code that produces a verdict is the code that was frozen
before the grant, not code chosen after the cells exist.

**What the grant does not do.** It does not freeze a result, does not run anything by itself, and does not authorise
changing the target block, the seeds, the threshold, the estimand or the scorer. A re-pin is a reviewed commit, not an
adjustment made while reading results. It does not license a continuity claim with the N=4 design: only 7 of the 24
previous targets survive into this block, and two seeds keep none.

**Consequences already recorded, not deferred.** `floor(0.05 × 17) = 0` and `floor(0.05 × 18) = 0`, so seeds 20740102
and 20740104 may spend no C8 assertion — they must be perfect. That follows from the size of their blocks, which follows
from the competence rule, which is signed; it is not a licence to widen a denominator after seeing a result.

**State now.** `GRANTED, NOT RUN`. No cell has executed, no seed has been drawn for a cell, and no result artifact
exists. The run is `python -m benchmarks.a1_two_path --measure`; assembly is `python -m benchmarks.a1_result assemble`.
