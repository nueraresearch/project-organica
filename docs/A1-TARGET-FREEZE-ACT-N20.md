# A1 N=20 target-freeze act — re-issued draft

> **Re-issued 2026-11-15 for `20740101-20740106`.** This edition replaces the 2026-11-14 draft bound to `20630101-20630106`, a block spent by `A1-BASELINE-AVAILABILITY-1`; that edition's tables remain in git history (`1b822af`) and are not restated here. Every table, count and digest below is bound to the adopted block. Nothing in this act is signed, frozen, granted or run.
>
> **Digests re-verified 2026-11-15, not recomputed.** Every digest below was checked against its
> source at re-issue: the 6 per-seed selection digests and the artifact SHA-256 against
> `docs/a1_c8_target_selection.json`. All 7 match, and `python -m benchmarks.a1_c8_target_selection --check` reports the artifact clean, so
> this edition changes no target and reserves no new digest.
>
> **Corrected 2026-11-15.** An earlier status on this act said the C1 denominator held it at **58** rows.
> That 58 is the *previous* block's cell-stream minimum (`20630101–20630106`, spent); the adopted block
> `20740101–20740106` was baselined on the same day and observes a cell-stream minimum of **64** against
> the floor of 60, meeting it on all six seeds. What holds this act is **target competence**, measured on
> the adopted block in [`A1-TARGET-VIABILITY-ADOPTED`](A1-TARGET-VIABILITY-ADOPTED.md).

**ID:** `A1-TARGET-FREEZE-N20-1`

**Date:** 2026-11-15

**Status:** `DRAFT — RE-ISSUED 2026-11-15; DIGESTS VERIFIED 7/7 AGAINST THE SELECTION ARTIFACT; C1 DENOMINATOR RECONCILED TO THE PROTOCOL AND MET ON THE ADOPTED BLOCK'S OPERATIVE CELL ROW (CELL-STREAM MINIMUM 64 AGAINST THE FLOOR OF 60, ALL SIX SEEDS); C4 EXPOSURE ADOPTED (POSTURE A) AND C8 COMPETENCE DECIDED (N_min 17); HELD ON TARGET COMPETENCE — 0/6 SEEDS ARE C2-VIABLE ON THE ADOPTED BLOCK FOR THIS DESIGN (A1-TARGET-VIABILITY-ADOPTED); AWAITING THE OWNER'S SIGNATURE; NOT FROZEN, NO GRANT, NO RUN`C1_DENOMINATOR_BELOW_FLOOR` BEFORE ANY GATE WAS READ; NO

**Decision owner:** ____________________

**Signature and date:** ____________________

**This is a prepared act, not an executed freeze.** The live manifest remains `REGISTERED DESIGN — NOT FROZEN, NOT RUN, NO GRANT`, its target block remains `UNRESOLVED — MUST BE FIXED BEFORE FREEZE`, and no seed is reserved. The C5 target-timing blocker is cleared by the separately registered earlier-`U` protocol at cycle 4; the cycle-36 sample remains the target-selection diagnostic. The manifest validator now has an N=20 target profile, and the act's 20-row block validates under it. Signing would perform the freeze described below; it would not issue a grant, run a cell or observe C8.

## 1. What would be frozen

The act freezes **Path A** for the registered A1 attempt:

> the representative eligible pre-37 cycle-membership directed-edge effect.

It adopts [`A1-C8-EXPANSION-1`](A1-C8-EXPANSION.md) and freezes the exact 20 target strings per seed from [`a1_c8_target_selection.json`](a1_c8_target_selection.json). The four current Path A targets are retained in every seed; the other 16 rows per seed are added from the registered expansion artifact. The current order is the selection order, not a claim that the original four are positions 1–4.

This act **supersedes** the unsigned N=4 act [`A1-TARGET-FREEZE-1`](A1-TARGET-FREEZE-ACT.md) if it is signed. The N=4 act is not executed by this draft, and the live manifest is unchanged until signature.

**C8 is the reason for the act.** Twenty target rows per seed make the per-seed C8 step `1/20 = 0.05`, equal to the unchanged 0.05 ceiling. This resolves the C8 denominator; it does not measure C8. C5 target timing is cleared separately by the earlier-`U` protocol; C1 and C4 remain post-freeze gates.

## 2. Exact target sets

The following are the exact 20 strings in the committed selection order. **Current four:** the existing Path A targets. **New 16:** the expansion rows added by this act.

### Seed `20740101`

**Current four (retained):** `indigo>fern`, `teal>slate`, `maple>cedar`, `verdant>umber`

**New 16:** `umber>cedar`, `slate>birch`, `fern>yarrow`, `crimson>sable`, `indigo>olive`, `indigo>maple`, `cedar>sable`, `verdant>olive`, `sable>verdant`, `umber>birch`, `amber>olive`, `birch>fern`, `crimson>maple`, `yarrow>slate`, `teal>willow`, `ochre>crimson`

**All 20:** `indigo>fern`, `teal>slate`, `maple>cedar`, `umber>cedar`, `slate>birch`, `verdant>umber`, `fern>yarrow`, `crimson>sable`, `indigo>olive`, `indigo>maple`, `cedar>sable`, `verdant>olive`, `sable>verdant`, `umber>birch`, `amber>olive`, `birch>fern`, `crimson>maple`, `yarrow>slate`, `teal>willow`, `ochre>crimson`

### Seed `20740102`

**Current four (retained):** `olive>umber`, `willow>yarrow`, `verdant>crimson`, `ochre>slate`

**New 16:** `verdant>ochre`, `verdant>willow`, `yarrow>ochre`, `umber>slate`, `amber>sable`, `sable>maple`, `sable>willow`, `crimson>indigo`, `olive>maple`, `yarrow>crimson`, `amber>birch`, `maple>birch`, `fern>teal`, `teal>birch`, `indigo>umber`, `slate>amber`

**All 20:** `olive>umber`, `willow>yarrow`, `verdant>crimson`, `verdant>ochre`, `ochre>slate`, `verdant>willow`, `yarrow>ochre`, `umber>slate`, `amber>sable`, `sable>maple`, `sable>willow`, `crimson>indigo`, `olive>maple`, `yarrow>crimson`, `amber>birch`, `maple>birch`, `fern>teal`, `teal>birch`, `indigo>umber`, `slate>amber`

### Seed `20740103`

**Current four (retained):** `yarrow>teal`, `amber>willow`, `birch>fern`, `verdant>sable`

**New 16:** `willow>yarrow`, `cedar>teal`, `sable>teal`, `olive>sable`, `maple>cedar`, `cedar>olive`, `fern>ochre`, `ochre>olive`, `amber>verdant`, `ochre>willow`, `amber>slate`, `umber>verdant`, `crimson>maple`, `yarrow>indigo`, `fern>umber`, `slate>umber`

**All 20:** `yarrow>teal`, `willow>yarrow`, `cedar>teal`, `amber>willow`, `sable>teal`, `birch>fern`, `verdant>sable`, `olive>sable`, `maple>cedar`, `cedar>olive`, `fern>ochre`, `ochre>olive`, `amber>verdant`, `ochre>willow`, `amber>slate`, `umber>verdant`, `crimson>maple`, `yarrow>indigo`, `fern>umber`, `slate>umber`

### Seed `20740104`

**Current four (retained):** `slate>indigo`, `umber>cedar`, `crimson>sable`, `willow>birch`

**New 16:** `olive>indigo`, `slate>maple`, `cedar>verdant`, `amber>maple`, `teal>slate`, `maple>sable`, `indigo>amber`, `umber>olive`, `verdant>olive`, `teal>yarrow`, `verdant>yarrow`, `teal>cedar`, `ochre>amber`, `crimson>yarrow`, `birch>umber`, `crimson>fern`

**All 20:** `slate>indigo`, `umber>cedar`, `crimson>sable`, `olive>indigo`, `slate>maple`, `willow>birch`, `cedar>verdant`, `amber>maple`, `teal>slate`, `maple>sable`, `indigo>amber`, `umber>olive`, `verdant>olive`, `teal>yarrow`, `verdant>yarrow`, `teal>cedar`, `ochre>amber`, `crimson>yarrow`, `birch>umber`, `crimson>fern`

### Seed `20740105`

**Current four (retained):** `ochre>crimson`, `verdant>willow`, `sable>yarrow`, `fern>olive`

**New 16:** `fern>ochre`, `olive>willow`, `willow>amber`, `teal>slate`, `sable>teal`, `teal>umber`, `fern>umber`, `cedar>slate`, `crimson>slate`, `amber>maple`, `verdant>cedar`, `cedar>amber`, `olive>crimson`, `umber>maple`, `birch>indigo`, `verdant>maple`

**All 20:** `ochre>crimson`, `verdant>willow`, `sable>yarrow`, `fern>ochre`, `olive>willow`, `fern>olive`, `willow>amber`, `teal>slate`, `sable>teal`, `teal>umber`, `fern>umber`, `cedar>slate`, `crimson>slate`, `amber>maple`, `verdant>cedar`, `cedar>amber`, `olive>crimson`, `umber>maple`, `birch>indigo`, `verdant>maple`

### Seed `20740106`

**Current four (retained):** `indigo>teal`, `birch>ochre`, `amber>yarrow`, `verdant>sable`

**New 16:** `verdant>teal`, `ochre>fern`, `verdant>yarrow`, `yarrow>willow`, `birch>crimson`, `maple>ochre`, `crimson>cedar`, `umber>teal`, `amber>maple`, `fern>willow`, `slate>willow`, `olive>fern`, `maple>indigo`, `indigo>birch`, `amber>slate`, `umber>cedar`

**All 20:** `indigo>teal`, `verdant>teal`, `birch>ochre`, `amber>yarrow`, `ochre>fern`, `verdant>yarrow`, `yarrow>willow`, `verdant>sable`, `birch>crimson`, `maple>ochre`, `crimson>cedar`, `umber>teal`, `amber>maple`, `fern>willow`, `slate>willow`, `olive>fern`, `maple>indigo`, `indigo>birch`, `amber>slate`, `umber>cedar`

| Seed | Candidates | Eligible | A−K− rows | Retained | New | Max degree | Selection digest |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `20740101` | 64 | 64 | 20 | 4 | 16 | 3 | `f440a99296934789` |
| `20740102` | 64 | 64 | 20 | 4 | 16 | 3 | `002057a0ceb76a63` |
| `20740103` | 64 | 64 | 20 | 4 | 16 | 3 | `684a4ff4d58e4f86` |
| `20740104` | 64 | 64 | 20 | 4 | 16 | 3 | `60344feeb208447a` |
| `20740105` | 64 | 64 | 20 | 4 | 16 | 3 | `7c1c094b6bf2a663` |
| `20740106` | 62 | 62 | 20 | 4 | 16 | 3 | `8a223c4bc586c756` |

**Target observations:** 120. **Unique target edges:** 100. **Retained current targets:** 24/24 observations (four per seed). **New rows:** 96 (16 per seed).

**Selection artifact digest (SHA-256):** `2af0a2e0f4d8464b8c8e9fcaeefeb0268b896551fb2046491962b6465c73d54b`

## 2a. The selection record this act must carry

[`DECISION-A1-C8-SELECTION`](DECISION-A1-C8-SELECTION.md) S2 requires the pool and the selected block to be written into
this act, together with the identity of the constructor that produced the block, **before any cell runs**. These are the
fields that clause needs. None of them can be filled after the run without the act having been violated.

<!-- s2-fields:start -->
| Field | What it must contain | State |
| --- | --- | --- |
| Act ID | this act's own identifier, as quoted in its status line | `NOT RECORDED` |
| Competent pool per seed | every competent row per seed, in the constructor's order | `NOT RECORDED` |
| Competent pool digest | SHA-256 over that pool as one canonical text | `NOT RECORDED` |
| Selected block per seed | the edges this act freezes, per seed | `NOT RECORDED` |
| Selected block digest | SHA-256 over the blocks as frozen | `NOT RECORDED` |
| Row count per seed | competent rows available, and rows selected, per seed | `NOT RECORDED` |
| Constructor identity | the module that produced the block, and its source digest | `NOT RECORDED` |
| Constructor output digest | SHA-256 of the JSON artifact the constructor wrote | `NOT RECORDED` |
| Competence predicate | the record that defines which rows are competent | `FIXED BY RECORD` |
| Unfiltered selection | where the S5 disclosure is written | `NOT RECORDED` |
<!-- s2-fields:end -->

**This act is not signable while any row above reads `NOT RECORDED`.** A blank row is a reason to withhold the signature,
not a gap to close after the run: an unfilled row means the pool was never recorded, and a pool recorded after the run is a
pool chosen with the outcome in view.

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
- apply the N=20 target block to the live manifest before signature;
- regenerate targets or permit post-outcome re-selection;
- change the 0.05 C8 ceiling, the 0.05 C7 A/K margin, or the C1/C4 gate.

**Blocking precondition — the C1 denominator is reconciled, and what is outstanding is the owner's confirmation.** The denominator is not an open choice: [`A1-TARGET-SELECTION-PROTOCOL.md`](A1-TARGET-SELECTION-PROTOCOL.md) records that `c1_rows` *"includes baseline-available non-target edges in the C1 denominator"*, the [60-row gate](A1-C1-C4-VOID-GATE.md) applies the floor to **observed paired-control denominators**, and three committed documents label the **63–64** figure as a candidate-count upper bound and explicitly *"not an observed baseline-availability denominator"*. Measured under that definition, the adopted stream's paired-control denominator is **79 / 64 / 79 / 74 / 72 / 74** — minimum **64** against the floor of **60**, so **the floor is reachable**; the planning quantity would read **45 / 34 / 47 / 48 / 38 / 41** (min 34). **The earlier blocker on this act used the planning quantity as though it were the scored one**, which is a definition drift rather than a world property, and this edition replaces it. **Three things this does not establish.** (1) **C1 has not been scored** — retained ÷ denominator needs a run; a reachable floor is not a pass. (2) **The power analysis sits on the planning quantity**: a larger true denominator is conservative for power, but the 63-row reference in [`DECISION-A1-PATH-A-C1-RULE.md`](DECISION-A1-PATH-A-C1-RULE.md) is not the quantity it names and should be corrected with disclosure. (3) **C4's exposure widened with C1's denominator**: the same non-target stream is C4's row set and every measurable delta must stay within 0.05, so the binding constraint may have moved from C1's row count to C4's delta ceiling, which no pre-run measurement can settle. `docs/a1_design_viability.json` reasons about C1 through the planning quantity, so its "do not freeze" disposition rests on the same reading; it is left intact and flagged rather than rewritten — its disposition reads *"Do not freeze or run the current A1 design on these records"*. **What is outstanding is one owner act:** confirming that the protocol sentence is authoritative — the reconciliation is recorded here, not adopted by a tool. The 2026-11-15 re-issue of [`A1-DESIGN-VIABILITY-1`](A1-DESIGN-VIABILITY.md) adds a prior question the sentence does not answer: *what is a row?* Counting each directed orientation as its own row clears the floor on every adopted seed (64–79); counting each undirected relation once does not (35–51). Both are recorded; neither is chosen.

## 4. Preconditions

C5 target timing and the N=20 validator are satisfied. The table records the state at the re-issue date; the act remains unsigned.

| Precondition | State |
| --- | --- |
| P0 protocol compliance | **PASS** |
| Six target sets formed | **PASS** |
| Twenty targets per seed | **PASS** — 20 rows on all six seeds |
| Four current targets retained | **PASS** — 4/4 in every seed |
| Selection artifact internally consistent | **PASS** |
| C5: earlier `U` before carrier, K and Y | **PASS** — fixed cycle-4 `U`; no current target carrier before cycle 4; earliest current carrier cycle 8, earliest observed carrier cycle 6; four current targets preserved ([audit](A1-C5-TARGET-TIMING.md)) |
| N=20 target validation | **PASS** — `a1_two_path` accepts 20 unique targets per seed with permitted overlap and endpoint degree at most 3 |
| C8 denominator | **PASS** — 20 rows per seed; `1/20 = 0.05`; ceiling unchanged |
| C1 acceptance rule | **RECORDED — BINDING FOR A1** |
| C1/C4 gate order and 60-row floor | **ADOPTED — BINDING FOR A1 (2026-11-14)** |
| Grant | **NOT ISSUED** |
| Run | **NOT STARTED** |

**C5 is cleared for these targets without re-selecting any of them.** The earlier-`U` protocol fixes the C5 sample at cycle 4, after the cycle-4 observations are stored and before the cycle-4 sleep call. The no-arm replay records the earliest current carrier at cycle 8 and no current target carrier before cycle 4; the cycle-36 sample remains the target-selection diagnostic only. The four retained targets are therefore preserved, and the 16 expansion rows are not exempt: the same cycle-4 rule applies to every row. The replay also records **11 of 24 current observations with no carrier by 120**; an absent carrier is not a timing violation, and those rows remain subject to the structural gates that require carrier availability at run time. This is a design check, not an A1 cell, and it does not weaken C5: a cell still fails if its U is later than a carrier, K or Y that exists.

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

## 6. After signature

1. **C5 timing:** cleared by the registered earlier-`U` protocol at cycle 4; see [`A1-C5-TARGET-TIMING.md`](A1-C5-TARGET-TIMING.md).
2. **Sign this act:** record the owner signature and effective date, freeze the exact 20 sets and reserve the seed block.
3. **Grant:** record the separate dated run-authorising grant in the manifest.
4. **Run and measure:** execute the planned cells and assemble C1/C4 and the remaining gate records.

Until the grant, the execution gate must refuse. Until the run, there are no cell parts, no C1/C4 denominator and no C8 measurement.

## 7. Checks

- `python -m benchmarks.a1_c8_target_selection --check`
- `python -m benchmarks.a1_target_selection --check`
- `python -m benchmarks.a1_adversarial_audit --check`
- `python -m benchmarks.a1_c5_target_timing --check`
- `python -m benchmarks.a1_two_path --check`
- `python -m benchmarks.a1_two_path --self-test`

The N=20 selection check and self-test are clean, the C5 timing audit is clean, and the N=20 target block validates under `a1_two_path`'s target-set check. No A1 cell was opened.

**Not evidence:** A prepared N=20 freeze act. It freezes nothing until signed, issues no grant, runs no cell and makes no C8 measurement. C5 target timing is cleared by a separate no-arm audit, not by this act.
