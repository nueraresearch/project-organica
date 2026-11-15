# A1 run — 2026-11-15

**Ran:** 2026-11-15 · **Manifest:** `GRANTED, NOT RUN` at launch (`docs/a1_two_path_manifest.json`) · **Grant:**
[`A1-GRANT`](A1-GRANT.md) · **Act:** [`A1-TARGET-FREEZE-ACT-N20`](A1-TARGET-FREEZE-ACT-N20.md)

**Verdict as the protocol scores it: `VOID` — `VOID gates: C4_no_interference`, `reason code: C4_DELTA`.**

## 1. What was executed

37 cells: the six planned cells on each of the six reserved seeds (`20740101`–`20740106`), plus the determinism control
(`A+K+`, seed `20740101`). Each cell ran 120 cycles at cap 40 with the U sample at cycle 4, against the 20 / 17 / 20 /
20 / 18 / 20 target block the signed act froze. Every cell wrote a part stamped `engine_version 0.15.0`, commit
`fb701f48b9d5`; no cell opened the live `memory.db` — each used its own scratch database.

**The determinism control repeated exactly.** The control part's 20 target rows and 92 neighbour rows are byte-identical
to the `A+K+` part it repeats, with the same object fingerprint `84cb1c2f89c1a19d`.

**Assembly went through the pinned scorer.** `a1_result.assemble` verifies the `a1_arms` / `a1_result` digests before it
scores and raises on a mismatch; it did not raise. The machine result is `docs/a1_two_path_result.json`.

## 2. The C1/C4 disposition

| Gate | Result | Denominator | The numbers |
|---|---|---|---|
| C1 path separation | **PASS** | A− 457 rows, K− 478 rows | A− 455/457 = 0.996; K− 478/478 = 1.000; tolerance 0.95 |
| C4 no interference | **FAIL → VOID** | 2,785 non-target rows, 2,785 measured, 0 unmeasured | max A/K/Y = 0.000000 / 0.575000 / 0.575000; tolerance 0.05 |

C1 passes on every seed (per-seed A− ranges 0.986–1.000, K− 1.000). C4 does not: **510 non-target rows exceed the 0.05
tolerance**, and every one of them is in a cell where carrier removal is blocked — `A+K-` (256) and `A-K-` (254). By
path: 280 K, 230 Y, **0 A**. Deltas run from 0.058333 to 0.575.

**That distribution is the finding's shape, not a detail.** The intervention that blocks carrier removal for the 20
target edges does not stay local to them: carriers are multi-edge paths, so removing the carriers that contain a target
also removes carriers of other edges. C4 exists to detect exactly this, and it did. A VOID is not a negative result —
it says these cells cannot be used to adjudicate an effect, and the pre-committed gate order says so before any
C2/C8 number is read.

## 3. The five complete-coverage gates, and a defect in how they were read

The assembly reports five further gates failing on coverage:

| Gate | Rows | Coverage problems |
|---|---|---|
| C2 treatment consistency | 460 / 480 | 48 |
| C3 positivity | 690 / 720 | 72 |
| C5 common cause | 690 / 720 | 72 |
| C7 assertion block | 460 / 480 | 48 |
| C9 same object | 690 / 720 | 72 |

**Every problem is the same one: `target list does not match`.** The cause is mechanical, not scientific.
`a1_arms.registered_target_map()` reads `docs/a1_c8_target_selection.json` — the *representative* block — to build the
expected per-seed target lists. The cells carry the *competent* block, which the signed act froze and the manifest reads
from `docs/a1_c8_target_selection_competent.json`. The two blocks share only 37 of 115 rows, so every seed mismatches and
every gate that requires complete target coverage fails by construction.

**This is not repaired here, deliberately.** `a1_arms.py` is pinned by `docs/a1_scorer_pin.json`, and changing which
artifact supplies the expected target list would change five gate outcomes *after* the cells were seen. That is the
change the pin exists to stop being silent. The fix is small — read the selection artifact the manifest's targets name —
but it must be a disclosed, re-pinned commit, and the C4 `VOID` is unaffected either way because C4 does not use the
expected target list.

## 4. What is adjudicable

Nothing in C2, C4, C7, C8 or C9. The C1/C4 disposition is `VOID` on C4, and five structural gates were scored against
the wrong expectation. **No C8 assertion is reported, no competence claim is made, and no effect estimate is quoted** —
the block ran and the protocol says its result cannot be read as evidence.

**What the run does establish, at the level of the instrument:** the seven cells it takes to cover a seed execute in
about eight seconds each, the engine stamps every part, the determinism control reproduces a cell exactly, and the
scorer's pin held. Those are properties of the harness, not findings about the organism — the same distinction the
project already draws for its audit traces.

## 5. Reproduce

```bash
python -m benchmarks.a1_two_path --measure              # 36 cells + control, ~5 minutes
python -m benchmarks.a1_result --parts                  # assembly through the pinned scorer
```

Parts live in `.scratch/a1_two_path/parts/` and are not committed; the assembled report is
`docs/a1_two_path_result.json`.
