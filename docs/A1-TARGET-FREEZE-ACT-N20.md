# A1 N=20 target-freeze act — draft

**ID:** `A1-TARGET-FREEZE-N20-1`

**Date:** 2026-11-14

**Status:** `DRAFT — C8 RESOLUTION PREPARED; NOT SIGNABLE: C5 TARGET-TIMING PRECONDITION UNRESOLVED; N=20 VALIDATOR READY; N=4 MANIFEST UNCHANGED; NO GRANT, NO RUN`

**Decision owner:** ____________________

**Signature and date:** ____________________

**This is a prepared act, not an executed freeze.** The live manifest remains `REGISTERED DESIGN — NOT FROZEN, NOT RUN, NO GRANT`, its target block remains `UNRESOLVED — MUST BE FIXED BEFORE FREEZE`, and no seed is reserved. This act is also **not signable yet**: C5 is unresolved for the current targets. The manifest validator now has an N=20 target profile, and the act's 20-row block validates under it. Signing after C5 is cleared would perform the freeze described below; it would not issue a grant, run a cell or observe C8.

## 1. What would be frozen

The act freezes **Path A** for the registered A1 attempt:

> the representative eligible pre-37 cycle-membership directed-edge effect.

It adopts [`A1-C8-EXPANSION-1`](A1-C8-EXPANSION.md) and freezes the exact 20 target strings per seed from [`a1_c8_target_selection.json`](a1_c8_target_selection.json). The four current Path A targets are retained in every seed; the other 16 rows per seed are added from the registered expansion artifact. The current order is the selection order, not a claim that the original four are positions 1–4.

This act **supersedes** the unsigned N=4 act [`A1-TARGET-FREEZE-1`](A1-TARGET-FREEZE-ACT.md) if it is signed. The N=4 act is not executed by this draft, and the live manifest is unchanged until signature.

**C8 is the reason for the act.** Twenty target rows per seed make the per-seed C8 step `1/20 = 0.05`, equal to the unchanged 0.05 ceiling. This resolves the C8 denominator; it does not measure C8, and it does not resolve C5, C1 or C4.

## 2. Exact target sets

The following are the exact 20 strings in the committed selection order. **Current four:** the existing Path A targets. **New 16:** the expansion rows added by this act.

### Seed `20630101`

**Current four (retained):** `verdant>sable`, `olive>cedar`, `fern>willow`, `yarrow>amber`

**New 16:** `amber>olive`, `ochre>cedar`, `fern>maple`, `umber>fern`, `ochre>birch`, `crimson>birch`, `maple>olive`, `sable>indigo`, `teal>birch`, `sable>umber`, `indigo>yarrow`, `yarrow>cedar`, `willow>slate`, `slate>umber`, `crimson>amber`, `ochre>indigo`

**All 20:** `verdant>sable`, `olive>cedar`, `fern>willow`, `amber>olive`, `ochre>cedar`, `yarrow>amber`, `fern>maple`, `umber>fern`, `ochre>birch`, `crimson>birch`, `maple>olive`, `sable>indigo`, `teal>birch`, `sable>umber`, `indigo>yarrow`, `yarrow>cedar`, `willow>slate`, `slate>umber`, `crimson>amber`, `ochre>indigo`

### Seed `20630102`

**Current four (retained):** `umber>ochre`, `verdant>teal`, `indigo>sable`, `slate>birch`

**New 16:** `ochre>amber`, `verdant>olive`, `verdant>crimson`, `willow>teal`, `ochre>indigo`, `cedar>umber`, `yarrow>amber`, `teal>cedar`, `willow>crimson`, `fern>olive`, `cedar>birch`, `yarrow>indigo`, `sable>amber`, `fern>crimson`, `willow>maple`, `maple>sable`

**All 20:** `umber>ochre`, `verdant>teal`, `ochre>amber`, `verdant>olive`, `verdant>crimson`, `willow>teal`, `indigo>sable`, `ochre>indigo`, `cedar>umber`, `slate>birch`, `yarrow>amber`, `teal>cedar`, `willow>crimson`, `fern>olive`, `cedar>birch`, `yarrow>indigo`, `sable>amber`, `fern>crimson`, `willow>maple`, `maple>sable`

### Seed `20630103`

**Current four (retained):** `teal>willow`, `amber>verdant`, `fern>maple`, `olive>indigo`

**New 16:** `teal>verdant`, `amber>indigo`, `willow>umber`, `slate>cedar`, `sable>yarrow`, `verdant>crimson`, `crimson>indigo`, `willow>crimson`, `amber>ochre`, `maple>umber`, `yarrow>maple`, `sable>olive`, `fern>ochre`, `slate>birch`, `ochre>yarrow`, `birch>teal`

**All 20:** `teal>willow`, `amber>verdant`, `fern>maple`, `teal>verdant`, `amber>indigo`, `willow>umber`, `olive>indigo`, `slate>cedar`, `sable>yarrow`, `verdant>crimson`, `crimson>indigo`, `willow>crimson`, `amber>ochre`, `maple>umber`, `yarrow>maple`, `sable>olive`, `fern>ochre`, `slate>birch`, `ochre>yarrow`, `birch>teal`

### Seed `20630104`

**Current four (retained):** `indigo>ochre`, `teal>fern`, `willow>olive`, `birch>verdant`

**New 16:** `birch>fern`, `maple>amber`, `cedar>indigo`, `amber>willow`, `birch>slate`, `amber>yarrow`, `crimson>indigo`, `slate>willow`, `teal>ochre`, `maple>crimson`, `slate>maple`, `fern>umber`, `teal>crimson`, `umber>olive`, `cedar>yarrow`, `sable>cedar`

**All 20:** `indigo>ochre`, `teal>fern`, `willow>olive`, `birch>verdant`, `birch>fern`, `maple>amber`, `cedar>indigo`, `amber>willow`, `birch>slate`, `amber>yarrow`, `crimson>indigo`, `slate>willow`, `teal>ochre`, `maple>crimson`, `slate>maple`, `fern>umber`, `teal>crimson`, `umber>olive`, `cedar>yarrow`, `sable>cedar`

### Seed `20630105`

**Current four (retained):** `cedar>olive`, `indigo>teal`, `verdant>maple`, `ochre>fern`

**New 16:** `cedar>sable`, `umber>birch`, `slate>olive`, `cedar>birch`, `amber>crimson`, `amber>birch`, `umber>fern`, `crimson>verdant`, `fern>slate`, `teal>crimson`, `slate>yarrow`, `yarrow>verdant`, `yarrow>umber`, `ochre>olive`, `amber>indigo`, `willow>maple`

**All 20:** `cedar>olive`, `indigo>teal`, `verdant>maple`, `ochre>fern`, `cedar>sable`, `umber>birch`, `slate>olive`, `cedar>birch`, `amber>crimson`, `amber>birch`, `umber>fern`, `crimson>verdant`, `fern>slate`, `teal>crimson`, `slate>yarrow`, `yarrow>verdant`, `yarrow>umber`, `ochre>olive`, `amber>indigo`, `willow>maple`

### Seed `20630106`

**Current four (retained):** `sable>maple`, `teal>umber`, `cedar>olive`, `amber>crimson`

**New 16:** `willow>cedar`, `teal>willow`, `crimson>yarrow`, `birch>willow`, `amber>maple`, `sable>slate`, `fern>indigo`, `yarrow>slate`, `cedar>maple`, `birch>indigo`, `teal>olive`, `fern>umber`, `yarrow>olive`, `umber>verdant`, `sable>crimson`, `amber>slate`

**All 20:** `sable>maple`, `teal>umber`, `cedar>olive`, `willow>cedar`, `amber>crimson`, `teal>willow`, `crimson>yarrow`, `birch>willow`, `amber>maple`, `sable>slate`, `fern>indigo`, `yarrow>slate`, `cedar>maple`, `birch>indigo`, `teal>olive`, `fern>umber`, `yarrow>olive`, `umber>verdant`, `sable>crimson`, `amber>slate`

| Seed | Candidates | Eligible | A−K− rows | Retained | New | Max degree | Selection digest |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `20630101` | 64 | 64 | 20 | 4 | 16 | 3 | `029749776f555743` |
| `20630102` | 63 | 63 | 20 | 4 | 16 | 3 | `132ba4ab73b30b60` |
| `20630103` | 64 | 64 | 20 | 4 | 16 | 3 | `e43ee50632fc2ab3` |
| `20630104` | 64 | 64 | 20 | 4 | 16 | 3 | `431394460a400a49` |
| `20630105` | 64 | 64 | 20 | 4 | 16 | 3 | `64f888517920177b` |
| `20630106` | 63 | 63 | 20 | 4 | 16 | 3 | `5f84322410f92c41` |

**Target observations:** 120. **Unique target edges:** 104. **Retained current targets:** 24/24 observations (four per seed). **New rows:** 96 (16 per seed).

**Selection artifact digest (SHA-256):** `daa207f2a6b0644081677691cebc54131d36151406e0121cbe364df005c5cc76`

## 3. Effect of signature

Signing and dating this act would, in the freeze record:

- adopt `A1-C8-EXPANSION-1` and record its selection artifact;
- set the manifest target block to `FIXED BEFORE FREEZE` with the exact 20-target `by_seed` mapping;
- set `targets.n_per_seed` to **20** and the manifest `frozen` flag to `true`;
- reserve the six candidate seeds as the fixed seed block;
- leave `authorisation.granted: false` and `granted_on: null`;
- leave the result absent and C1/C4 unobserved.

The act does **not**:

- issue a grant;
- open a database or run a cell;
- produce a C1 or C4 denominator or a C8 measurement;
- resolve the C5 target-timing blocker;
- apply the N=20 target block to the live manifest before signature;
- regenerate targets or permit post-outcome re-selection;
- change the 0.05 C8 ceiling, the 0.05 C7 A/K margin, or the C1/C4 gate.

## 4. Preconditions

The act may be signed only after C5 is cleared; the N=20 validator row is already satisfied. The table records the state at the draft date.

| Precondition | State |
| --- | --- |
| P0 protocol compliance | **PASS** |
| Six target sets formed | **PASS** |
| Twenty targets per seed | **PASS** — 20 rows on all six seeds |
| Four current targets retained | **PASS** — 4/4 in every seed |
| Selection artifact internally consistent | **PASS** |
| C5: cycle-36 `U` before carrier, K and Y | **UNRESOLVED — BLOCKING** — a no-arm 36-cycle audit found 15/24 current target observations with a carrier before cycle 36 |
| N=20 target validation | **PASS** — `a1_two_path` accepts 20 unique targets per seed with permitted overlap and endpoint degree at most 3 |
| C8 denominator | **PASS** — 20 rows per seed; `1/20 = 0.05`; ceiling unchanged |
| C1 acceptance rule | **RECORDED — BINDING FOR A1** |
| C1/C4 gate order and 60-row floor | **ADOPTED — BINDING FOR A1 (2026-11-14)** |
| Grant | **NOT ISSUED** |
| Run | **NOT STARTED** |

**C5 is not made true by adopting N=20.** The four retained targets carry the existing timing problem, and the 16 new rows are not exempt. The no-arm audit is a design check, not an A1 cell: it replayed the same world and sleep schedule through cycle 36 and found carriers before the cycle-36 `U` sample on 15 of 24 current target observations. A freeze that preserves those targets must first clear this precondition, either by a registered target screen/regeneration or by a separately registered earlier-`U` protocol. This act does not choose between those remedies.

**The N=20 validator is implemented, not merely documented.** `benchmarks.a1_two_path` selects the target profile from `targets.n_per_seed`: N=4 still requires four disjoint targets, while N=20 requires 20 unique targets, permits endpoint overlap, caps each endpoint at degree 3 and validates the block against [`a1_c8_target_selection.json`](a1_c8_target_selection.json). The block recorded in this act passes that check. This does not apply it to the live manifest; that still waits for signature.

C1/C4 remain post-freeze validity gates. This act does not wait for them, and it does not re-open their adopted gate order. C7 remains a per-edge A/K rate over 120 cycles and is unchanged. C1 target-only remains 20 rows, still below the 60-row floor; the C1 total upper bound remains 63–64 with 43–44 non-target rows. The act therefore does not make C1 admissible by itself.

## 5. What does not change

- The live manifest remains **NOT FROZEN** until this act is signed and the update is applied.
- The N=4 act remains **DRAFT — AWAITING OWNER SIGNATURE** and is not executed.
- The six candidate seeds remain **PROVISIONAL CANDIDATES** until signature.
- No target is regenerated or altered by this draft; the exact N=20 strings are copied from the committed selection artifact.
- No cell is authorised.
- The 60-row C1 floor and the C1/C4 post-freeze VOID gate remain **ADOPTED — BINDING FOR A1**.
- C8 remains **UNMEASURED**; this act only makes its denominator adjudicable after a valid run.

## 6. After the blockers and signature

1. **Clear C5:** complete a registered target screen/regeneration, or a separately registered earlier-`U` protocol, and record the result.
2. **Sign this act:** record the owner signature and effective date, freeze the exact 20 sets and reserve the seed block.
3. **Grant:** record the separate dated run-authorising grant in the manifest.
4. **Run and measure:** execute the planned cells and assemble C1/C4 and the remaining gate records.

Until the grant, the execution gate must refuse. Until the run, there are no cell parts, no C1/C4 denominator and no C8 measurement.

## 7. Checks

- `python -m benchmarks.a1_c8_target_selection --check`
- `python -m benchmarks.a1_target_selection --check`
- `python -m benchmarks.a1_adversarial_audit --check`
- `python -m benchmarks.a1_two_path --check`
- `python -m benchmarks.a1_two_path --self-test`

The N=20 selection check and self-test are clean, and the N=20 target block validates under `a1_two_path`'s target-set check. No cell or database was opened.

**Not evidence:** A prepared N=20 freeze act. It freezes nothing until signed, issues no grant, runs no cell, makes no C8 measurement and does not clear the C5 blocker.
