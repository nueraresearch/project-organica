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

## 6. Scorer history

`DECISION-A1-VOID-ACCEPTED` accepted this assembly and authorised a repair, so the pin has two states and both are
recorded here rather than replaced silently.

| Pin | `a1_arms.py` | `a1_result.py` | Used for |
|---|---|---|---|
| at this run | `98a90732ce832aab27906ad2e4d31715caeab3957382f5965b5cb0c628bafc38` | `ea42e376787cd4d0cc2d9d7ee4f6b3ea1876d45d8e9d3727183c1ec9d4e4e58e` | **this assembly**, including the five coverage failures |
| after the authorised repair | `5ce958b7839e09ebd10ce7787d1d5b3ab3023eb4b6d47a684b97edf8c6e5c86d` | `ea42e376787cd4d0cc2d9d7ee4f6b3ea1876d45d8e9d3727183c1ec9d4e4e58e` | future runs only |

**The repair is one line of authority, not a re-score.** `registered_target_map()` now reads the artifact the frozen
manifest's targets name; before, it read a module-level default pointing at the representative block. No threshold,
tolerance, formula or gate changed.

**This run was not re-assembled with the repaired scorer, and must not be.** The committed
`docs/a1_two_path_result.json` is the pre-repair assembly; running the repaired scorer over the same parts would move
five gates from FAIL to a different answer after the cells were seen, which is exactly what
`DECISION-A1-VOID-ACCEPTED` refuses. The C4 `VOID` is identical under either pin, because C4 never reads the expected
target list.


## 7. Reproduce

```bash
python -m benchmarks.a1_two_path --measure              # 36 cells + control, ~5 minutes
python -m benchmarks.a1_result --parts                  # assembly through the pinned scorer
```

Parts live in `.scratch/a1_two_path/parts/` and are not committed; the assembled report is
`docs/a1_two_path_result.json`.
