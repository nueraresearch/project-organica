# The interval on null worlds — a protocol diagnostic

**Status:** `PROTOCOL DIAGNOSTIC — A NULL-WORLD CALIBRATION, NOT A CELL AND NOT A VERDICT`

**Question:** the first cell fails when its 99% interval includes zero. What is the opposite error — how often does that
interval **exclude** zero on a world with no composition to learn? A rule that cannot produce a false pass on a null world
cannot manufacture a result; a rule that can, at a rate worth knowing, has a number attached to it now.

## 1. What is null here

`each event draws two tags independently from the same 16-tag pool, at the same 8 events per block and the same block count; no temporal law`. The tag pool is 16 tags, every event carries
two of them, and the world has 8 events per block over
120 blocks — the real world's shape, with its temporal law removed. The engine, the detection,
the admission at `m = 2`, the calibration band, the per-arm β grid
`[1, 2, 4, 8]`, the 20-cycle revision rule and the scorer are unchanged. Only the sequence is gone.

## 2. What the null worlds measured

`d = L_C − L_A` per seed; a positive value means the primitive scored *worse* than the pair counts.

| Seed | A | B | C | β (B) | β (C) | Composites |
|---|---|---|---|---|---|---|
| `20920101` | 0.376210 | 0.377164 | 0.377027 | 1 | 1 | 97 |
| `20920102` | 0.381360 | 0.382899 | 0.382250 | 1 | 1 | 114 |
| `20920103` | 0.382719 | 0.383522 | 0.383837 | 1 | 1 | 149 |
| `20920104` | 0.375018 | 0.378279 | 0.376923 | 1 | 1 | 122 |
| `20920105` | 0.376870 | 0.378481 | 0.377758 | 1 | 1 | 86 |
| `20920106` | 0.379284 | 0.381238 | 0.380397 | 1 | 1 | 113 |
| `20920107` | 0.379603 | 0.381953 | 0.381042 | 1 | 1 | 158 |
| `20920108` | 0.375153 | 0.375795 | 0.374963 | 1 | 1 | 125 |
| `20920109` | 0.379253 | 0.380775 | 0.380875 | 1 | 1 | 130 |
| `20920110` | 0.380910 | 0.383522 | 0.382371 | 1 | 1 | 87 |
| `20920111` | 0.378330 | 0.378540 | 0.378868 | 1 | 1 | 129 |
| `20920112` | 0.382271 | 0.383586 | 0.382963 | 1 | 1 | 130 |
| `20920113` | 0.381869 | 0.382928 | 0.382751 | 1 | 1 | 119 |
| `20920114` | 0.377264 | 0.378309 | 0.378144 | 1 | 1 | 133 |
| `20920115` | 0.378543 | 0.380907 | 0.379845 | 1 | 1 | 170 |
| `20920116` | 0.380740 | 0.382377 | 0.381854 | 1 | 1 | 132 |
| `20920117` | 0.382330 | 0.383408 | 0.382621 | 1 | 1 | 145 |
| `20920118` | 0.378315 | 0.378136 | 0.377389 | 1 | 1 | 111 |
| `20920119` | 0.372795 | 0.373780 | 0.373027 | 1 | 1 | 123 |
| `20920120` | 0.376692 | 0.376164 | 0.377563 | 1 | 1 | 151 |

Across 20 null worlds: mean `d` = **0.000847**, sd `0.000645`, range
`[-0.000926, 0.001905]`; median composites 127, median
detections 1710. The 20-seed interval — wider than the protocol's ten-seed cell, and reported
only as a reference — is `[0.000454, 0.001176]` around `0.000847`.

## 3. The calibration

`1000` cells, each drawing 10 distinct null seeds and applying the protocol's interval
(2,000 resamples per cell, level 99%).

| Quantity | Value |
|---|---|
| Cells in which the interval **included** zero | **57 of 1,000** (0.0570) |
| Cells in which it excluded zero | 943 (0.9430) |
| — excluded **above** zero (C worse) | 943 |
| — excluded **below** zero (C better) | 0 |
| False-pass rate under the **directional** rule (Amendment 2) | **0.0000** |
| Cell intervals containing the null's pool mean | 0.9820 |
| Median interval width | 0.000970 |

## 4. What this establishes, and what it does not

**The interval is calibrated around the null's mean** — 98.2% of cell intervals contained the
pool mean — **but the null's mean is not zero.** On structureless worlds arm C is slower by
**0.000847** nats (sd 0.000645), so at ten seeds the interval resolves that handicap in
94.3% of cells. Every one of those exclusions lies **above** zero: the rule never claims the
primitive helped, but it does reject the null, and the two-sided wording as first signed would count that as a pass.

**That wording was wrong and is corrected.** Amendment 2 makes the criterion directional: the charter passes only when the
interval lies entirely **below** zero; an interval including zero fails as bookkeeping, and an interval entirely above zero
fails as a reversal. Under that rule the null's false-pass rate is **0.0000** — 0 of
1,000 cells claimed a benefit that was not there.

**What is not established:** the rate of the charter's own error, a null verdict when the primitive does work. That is a
power question and this diagnostic does not measure it. The null also removes the temporal law rather than generating
independently drawn worlds from the same family, and its cell draws reuse the same 20 worlds, so the rate's
uncertainty is a little wider than the Monte Carlo error suggests.

**One caution about the construction:** removing the temporal law changes what the detector sees — the median null world
yielded 1710 loop detections — so this is the readout's null behaviour on worlds where
detections still form, not the whole engine on a different law.

## 5. Reproduction

```bash
python -m benchmarks.v2_first_cell_null --write    # artifact and this page
python -m benchmarks.v2_first_cell_null --check    # pins, a small deterministic run, page freshness
```

Artifact: [`v2_first_cell_null.json`](v2_first_cell_null.json).
