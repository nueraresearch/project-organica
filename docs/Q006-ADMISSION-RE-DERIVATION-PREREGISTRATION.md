# Q006 admission re-derivation — protocol

**Status: FROZEN, NOT RUN.** No cell has run on this registration. The endpoint, seeds,
bars, gates and decision table below were written before the first cell.

This is the Q006 Half-A re-derivation. It asks whether the historical answer recorded for
Q006 survives on the pinned 0.13.0 engine, not whether the old artifact was wrong on the
build that produced it. The old result is quoted as history, never as the comparator for a
new verdict.

## 1. Historical answer

Q006's recorded answer is **NO GAIN ON THIS LAYER** from
`docs/admission_two_arm_result.json`: mean paired coverage gain **-0.077009**, 95% interval
**[-0.099331, -0.056920]**, **0 of 8** seeds positive, precision difference **-0.096528**.
That artifact records no `engine_version`; its seed block **20320101–20320108** is consumed
and is not reused here.

## 2. Question and endpoint

Does the restored diversity-first Layer-1 admission cover more of the world's compositional
edges than the reference engine on the same generated world, at the same budget and the same
number of cycles?

The endpoint is `asserted_coverage` from `gate_acquisition_sufficiency`: the fraction of
the world's compositional edges present in the arm's asserted structure. It is coverage,
not behaviour.

## 3. Design

120 cycles of the Gate 13 compositional world, identical for both arms of a seed; the only
difference is the service class. **16 cells — 2 arms x 8 seeds.**

- Reference arm: `organica.sleep.SleepService`
- Adopted arm: `DiversityFirstSleepService`, restored in-process from the definition at
  commit `a82e890`; the module was deleted at withdrawal and no frozen engine file is edited.

Fresh seed block **20510101–20510108**, bootstrap **20510109**: the first contiguous window
of nine integers at or above 20510101 that appears in no file under `docs`, `tests`,
`benchmarks`, `research-journal` or `papers` when this registration was written. The ninth
integer is the bootstrap seed and is not a world seed.

## 4. Bars and guard

- **Gain bar 0.08** — carried as policy from the original `ADMISSION-TWO-ARM-1` registration;
  not calibrated on this layer.
- **Precision guard -0.05** — declared, not calibrated.

The gain is judged whole: mean paired coverage difference at or above the bar, its 95%
interval lower bound above zero, and at least 7 of 8 seeds positive. The guard can only
prevent a gain being claimed.

## 5. Decision table

| Condition | Verdict | Reading |
| --- | --- | --- |
| gates pass; gain passes; guard passes | **ADOPTED ARM GAINS** | the restored adopted admission covers more of the world's edges without losing precision |
| gates pass; gain passes; guard fails | **PRICED TRADE** | coverage rises and precision falls; nothing is claimed as a gain |
| gates pass; gain fails; interval width at or below 0.30 | **NO GAIN ON THIS LAYER** | the adopted rule does not cover more here; the historical negative answer survives |
| gates pass; gain fails; interval width above 0.30 | **UNDERPOWERED** | the interval cannot place the difference |
| a gate fails | **VOID** | reported as the gate, never as a verdict |

## 6. Gates

- **G0 liveness** — the two arms' asserted fingerprints must differ on at least seven of
  eight seeds.
- **G1 world present** — raw temporal coverage must be 1.0 in both arms of every seed.
- **G2 arithmetic** — covered cannot exceed asserted, and coverage and precision must equal
  their stated ratios.
- **G3 determinism** — the reference arm re-run on the first seed must reproduce its
  asserted fingerprint.
- **G4 denominator** — the world must have at least one compositional edge in every seed.
- **G5 boundary** — no frozen engine file may differ from HEAD when the block runs.

A failed gate voids the block and no criterion is read.

## 7. Classification

The re-derived verdict is classified once, as a whole:

- **SURVIVED** — the verdict is `NO GAIN ON THIS LAYER`.
- **REVERSED** — the verdict is `ADOPTED ARM GAINS`.
- **CHANGED** — the verdict is `PRICED TRADE`.
- **NOT_MEASURABLE** — the verdict is `UNDERPOWERED` or `VOID`.

## 8. Scope

One world family, one horizon, one cap. A surviving negative answer closes this admission
question on this layer; it does not establish that diversity-first ordering is wrong
anywhere else. The historical artifact is not edited or re-scored.
