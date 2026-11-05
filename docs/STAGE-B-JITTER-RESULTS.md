# Stage B: the hash-order jitter, measured

**Reading: R3.** This is the run of the diagnostic defined and committed in
`docs/STAGE-B-JITTER-DIAGNOSTIC.md`, on the pre-committed sample and redraws. It re-scores no verdict and
changes no cell in the assembly.

## 1. What was run

71 cells: every cell whose recorded onset lies within 10 cycles of its clock (38 cells),
plus the positional sample of the rest (33 cells), each under `PYTHONHASHSEED`
0, 1, 2 -- 213 runs,
213 present, every cell completing every redraw (71 of
71).

## 2. The reading

**R3: void.** 4 cells moved further than the 10-cycle ceiling the band rests on:
`2:1` 700000078 (16 cycles), `2:1` 700000157 (16 cycles), `2:1` 700000119 (14 cycles), `2:1` 700000057 (13 cycles). The band was too narrow and the enumeration was incomplete, so **no conclusion is
drawn about eligibility**. The control is applied to every cell that was redrawn, band cells
included: the ceiling is a property of the displacement distribution, not of a cell's role, and a
cell beyond it means cells outside the band could have flipped too.

## 3. Displacement

Across the 70 cells that produced an onset, the largest absolute onset difference from the committed
value was **16** cycles, and **15** cells moved at all. The ceiling the band
was drawn against was 10, so it did not hold.

| configuration | seed | committed onset | redraw onsets | max displacement |
| --- | --- | --- | --- | --- |
| `2:1` | 700000078 | 541 | 541, 557, 557 | 16 |
| `2:1` | 700000157 | 531 | 515, 531, 515 | 16 |
| `2:1` | 700000119 | 546 | 560, 546, 546 | 14 |
| `2:1` | 700000057 | 543 | 543, 543, 530 | 13 |
| `4:1` | 700000401 | 275 | 275, 283, 283 | 8 |
| `2:1` | 700000121 | 553 | 553, 558, 558 | 5 |
| `2:1` | 700000127 | 533 | 533, 529, 529 | 4 |
| `2:1` | 700000094 | 536 | 536, 533, 533 | 3 |
| `3:1` | 700000221 | 339 | 336, 339, 339 | 3 |
| `3:1` | 700000321 | 327 | 324, 324, 324 | 3 |
| `2:1` | 700000007 | 543 | 543, 543, 545 | 2 |
| `4:1` | 700000421 | 296 | 298, 296, 298 | 2 |

## 4. Eligibility, which is the quantity that matters

| configuration | band cells | eligibility flips | max displacement |
| --- | --- | --- | --- |
| `2:1` | 38 | 1 | 16 |

The one band cell that flipped: `2:1` 700000057 -- committed onset 543 against a clock of 539 (ineligible), redraw 543 (ineligible), 543 (ineligible), 530 (eligible). 1 of the 38 band cells changed eligibility in any redraw;
8 cells changed a scored outcome by more than 1e-9, and
1 changed whether an outcome existed at all (censored to measured, or the
reverse). Those numbers are descriptive: the reading above is what licenses or withholds a conclusion.

## 5. What this does and does not establish

- It establishes what the jitter does to **this** block under `v0.9.0`: only the displacement distribution, descriptively -- the eligibility reading is void, so this
  run says nothing about the block's denominators.
- It does not re-run the block, does not change the assembly, and does not touch the `NOT SUPPORTED` verdict
  (§D15).
- It does not license regenerating the block under a tie-broken engine: that is a different instrument and a
  different study.
- Three redraws bound the presence of an effect, not its rate. It says nothing about other engines, other world
  families or other arms.
- **The ceiling was wrong, so the band must be redrawn.** A usable measurement needs a new band around the
  measured displacement, a new enumeration and a new run, committed as a new definition before it runs. That is
  the owner's decision (manual action row 19), and it changes nothing already recorded.

## 6. Provenance

- Definition and pre-committed readings: `docs/STAGE-B-JITTER-DIAGNOSTIC.md`.
- Run data and comparisons: `docs/stage_b_jitter_diagnostic.json`.
- Committed cells: `docs/stage_b_runner.json`; the four-cell check: `docs/stage_b_rerun_check.json`.
- Mechanism: journal §187; boundary: §D15; the run: journal §189.
