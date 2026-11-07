# The density interaction, block A2: the registered block (2026-11-07)

**This block has run: the frozen analysis path returned EXCLUSION PAYS AT SPARSE DENSITY AND GROWS WITH DENSITY.** Section 9 records the result, and sections 1–8 are preserved exactly as committed before the run.

**Status: RUN (2026-11-07). All 640 registered cells executed on the sixteen registered seeds; every gate passed and the frozen analysis path returned EXCLUSION PAYS AT SPARSE DENSITY AND GROWS WITH DENSITY.**

**Every figure this block produces carries its arm, its scheme and its cap.** The arms are
`global count-ranked top-k` (rank every candidate row by count, ties on the engine's own key, take the top k) and `intra-cell-excluded ranking` (the same count ordering over the eligible rows only; rows whose two tags sit in one cell are not eligible); the schemes are
`fixed-total` exposure and `fixed-per-edge` exposure. A number quoted from this block
without its arm, its cap and its scheme is not a number from this block.

A2 replaces A1 (DENSITY-INTERACTION-1), which a pre-run review placed on hold as HELD - NOT RUNNABLE AS REGISTERED
(`docs/DENSITY-INTERACTION-REVIEW.md`). A1 is retained, frozen and unrun; its failure was that the dense end
of its ladder was saturated by arithmetic, not that its question was wrong.

## 1. Question and endpoint

At a fixed selection budget, does excluding the intra-cell row class buy precision on the world's edges in a sparse world, and how does that value move as the world densifies?

The endpoint is **precision at a fixed cap**: the share of the budget spent on the world's
edges. precision at a fixed cap is the endpoint: its denominator is the arm's own selection. Coverage divides by |W|, which grows 24 to 192, so a coverage difference is forced by arithmetic

This is a selection measurement, not a behavioural one: it says nothing about prediction,
revision or retention.

## 2. Design

**The world.** 16 tags in four cells, |P_world| = 240 directed non-self pairs; W is a seed-and-density subset of the 192 cross-cell pairs, so no intra-cell row can ever be a world edge. The within-cell filler carries a FIXED event budget at every density (the constant family): it keeps the ineligible class competing for the ranking budget across the whole ladder, which is the Gate 13 condition the design record rests on. A1 used the proportional family, under which the filler's mass collapses as the world densifies and the dense end saturates

**Densities.** 0.1, 0.2, 0.4, 0.6, 0.8 — 24, 48, 96, 144, 192 world edges at 16 tags.

**Exposure.** primary = fixed total exposure (400 events, 50 cycles at every density); sensitivity = fixed exposure per edge (each world edge emitted twice, so the horizon grows with |W|)

**The grid.** 320 judged cells and 320 exposure-check cells over
seeds **20330201–20330216**, bootstrap **20330217**. 2 arms x 2 caps x 5 densities x 16 seeds = 320 judged cells in the primary scheme, and the same count again in the sensitivity scheme for the exposure check; 640 cells in total

Freshness: the first contiguous window of seventeen integers at or above 20330201 that appears in no file under docs, tests, benchmarks, research-journal or papers; the seventeenth is the bootstrap seed

## 3. The criterion, the bar and the gates

**The estimand.** Delta(rho) = precision(intra_cell_excluded, cap 20) - precision(control, cap 20) at density rho

**The bar is 0.05.** calibrated on eight UNREGISTERED seeds (992001-992008) before this block existed, where the sparse-end mean was 0.094 with a per-seed sd of 0.062; the bar is set at roughly half that mean so the block is powered (~0.8 at sixteen seeds) rather than fitted to the judged run. Rule 19 permits calibration only on data that is not being judged, and these seeds are not in the block

**C1 is the judged criterion.** level at the sparse end on precision at the primary cap: mean over seeds of Delta(0.1) at or above the sparse bar, with its paired interval's lower bound above zero and at least eleven of sixteen seeds positive

**The interaction is not a criterion.** the interaction Delta(0.8) - Delta(0.1) is NOT a criterion. It is reported with its interval and its per-seed values, because the dense end is pinned by the pool's composition (the pilot measured Delta(0.8) = 0.150 with zero spread on eight seeds), so a criterion there would be arithmetic rather than evidence

**Judged whole.** C1 is the whole judged criterion; the gates are preconditions, not scores, and the density slope is a description rather than a second criterion

**The exposure check.** if the sparse-end level does not hold under the sensitivity scheme, the verdict is EXPOSURE ARTIFACT and nothing is adopted

* **G0 liveness** — the two arms' selected sets must differ on at least fourteen of sixteen seeds at the sparse end in the primary scheme
* **G1 presence ceiling** — every world edge must be present in the pool at every cell (presence = 1.0)
* **G2 arithmetic** — covered cannot exceed asserted; precision must equal covered over asserted; precision cannot exceed 1; rho_rank is reported for every cell
* **G3 axis live** — rho_rank must rise from the sparsest to the densest level in both schemes
* **G4 control reproduces Gate 13** — the control's mean precision at the sparse end must not exceed 0.50
* **G5 identity where it must hold** — on a pool whose every row is a world edge, the two arms must select the same set and Delta must be exactly 0
* **G6 treatment does what it claims** — coverage of the treatment must be at least the control's on every cell

**Void rule.** a failed gate voids the block and no criterion is read; a cell set that is not the pre-registered grid is refused

## 4. Decision table

| Condition | Verdict | Reading | Decision |
| --- | --- | --- | --- |
| gates pass; C1 passes; the interaction interval lies above zero | **EXCLUSION PAYS AT SPARSE DENSITY AND GROWS WITH DENSITY** | the freed budget buys more as the world's edge set grows; this is the A1 mechanism, now measured where the treatment is not pinned | adopt intra-cell exclusion as an allocation change behind a recorded owner decision; no behavioural claim |
| gates pass; C1 passes; the interaction interval straddles zero | **EXCLUSION PAYS AT SPARSE DENSITY; DENSITY SLOPE NOT IDENTIFIED** | the exclusion buys precision where the world is sparse, and the block cannot place how that changes with density | adopt at the sparse end; move the density question to the candidate space, since the dense end is pinned by composition |
| gates pass; C1 passes; the interaction interval lies below zero | **EXCLUSION PAYS MORE AT SPARSE THAN DENSE** | the crowded class, not density, is the lever; the dense end has little left to fix | adopt at the sparse end; retire the density interaction as a moderator of this bottleneck |
| gates pass; C1 fails | **EXCLUSION DOES NOT PAY AT SPARSE DENSITY** | removing the ineligible class does not buy precision at the budget where Gate 13's observation lives | retire budget competition as the lever at this cap and world family; move the line to the candidate space |
| gates pass; a criterion passes but the sensitivity scheme's sparse-end mean is not positive | **EXPOSURE ARTIFACT** | the direction reverses under the other exposure scheme | adopt nothing; report both schemes |
| gates pass; a criterion fails and the interval is wider than 0.30 | **UNDERPOWERED** | the interval cannot place the sparse-end level; absence is not established | neither pole; a new block on fresh seeds may be registered, never a re-read |
| a gate fails | **VOID** | reported as the gate, never as a verdict | none; fix the harness |

## 5. What is reported

Delta(rho) per seed, per scheme and per cap, with its paired interval; both arms'
precision and coverage at every density; the pool's intra-cell share and `rho_rank` at every
cell; and the recovery curve at the caps 20, 40, 80, 160, 240 as a characterization, never as a
criterion and never as the rank of the first edge. The interaction is reported with its
interval and its per-seed values, and the decision table places it, but it is not scored.

## 6. The pilot: calibration on unregistered seeds

The bar and the seed count rest on a pilot that this block does not judge.
calibration on unregistered seeds: the block's seeds are not measured here, and these seeds are not in the block

| scheme | sparse mean | dense mean | interaction mean | per seed |
|---|---|---|---|---|
| primary | 0.094 (sd 0.062) | 0.150 (sd 0.000) | +0.0563 (sd 0.062) | +0.10, +0.05, +0.10, +0.00, +0.15, +0.05, +0.05, -0.05 |
| sensitivity | 0.075 (sd 0.046) | 0.150 (sd 0.000) | +0.0750 (sd 0.046) | +0.10, +0.05, +0.15, +0.05, +0.10, +0.10, +0.00, +0.05 |

at cap 20 the dense pool holds 192 world rows and 48 intra rows, so the control's top 20 is 17 world rows and the treatment's is 20: Delta(0.8) = 0.150 with no spread on any seed. That is why the interaction cannot be a criterion

for the sparse bar 0.05 at sixteen seeds the standard error is 0.0155 and the power against the pilot mean 0.094 is about 0.8

The designed pools, which are the world's own construction with no engine, show the shape
the registration assumes: the intra-cell share falls (yes), the control's own
precision rises (yes) — the design record's mechanical prediction — and the
treatment's advantage rises with density (yes) on the **designed** pools:

| rho_world | control, cap 20 | treated, cap 20 | Delta, cap 20 | intra-cell share |
|---|---|---|---|---|
| 0.1 | 0.3406 | 0.4188 | +0.0781 | 0.2935 |
| 0.2 | 0.4938 | 0.5781 | +0.0844 | 0.2501 |
| 0.4 | 0.7094 | 0.9063 | +0.1969 | 0.2184 |
| 0.6 | 0.5687 | 0.8906 | +0.3219 | 0.2047 |
| 0.8 | 0.6500 | 1.0000 | +0.3500 | 0.2000 |

Those are properties of the world, not of the engine, and they are not scored. They
establish only that the registered direction is representable by this instrument.

## 7. Analysis and runner

`./.venv/bin/python -m benchmarks.score_density_interaction_a2 --results docs/density_interaction_a2_run.json --out docs/density_interaction_a2_result.json`

The analysis path is `benchmarks/score_density_interaction_a2.py`, frozen with this registration. It reads only the cells the
runner writes, validates the grid, and imports nothing from the engine. The runner is
`./.venv/bin/python -m benchmarks.run_density_interaction --prereg docs/density_interaction_a2_prereg.json --out docs/density_interaction_a2_run.json`; it can be sliced (`--scheme`, `--seeds`) and appended (`--append`), and it
refuses to overwrite a cell inside one block. A1's registration is held, and the runner
refuses it by name.

## 8. Allocation

16 world seeds, 1 bootstrap seed, 320 judged cells,
320 exposure-check cells, 3 recovery caps,
1 thresholds, 1 bars. one bar: the sparse-end level

No arm may run before this file is committed.


## 9. Result (post-freeze)

**EXCLUSION PAYS AT SPARSE DENSITY AND GROWS WITH DENSITY.** the exclusion buys precision at the sparse end, and the dense-minus-sparse difference lies above zero

- **Cells:** 640; gates all passed.
- **C1, the sparse-end level:** mean +0.059375, 95 percent interval
  [+0.040625, +0.078125], width 0.037500, bar 0.05, 13 of 16 seeds
  positive — passed.
- **The interaction (descriptive, not judged):** mean +0.090625, interval
  [+0.071875, +0.109375].
- **Exposure check:** sensitivity-scheme sparse mean +0.059375, 11 of 16
  seeds positive — holds.

| rho_world | Delta precision, primary | Delta precision, sensitivity | primary − sensitivity |
| --- | --- | --- | --- |
| 0.1 | +0.059375 | +0.059375 | +0.000000 |
| 0.2 | +0.053125 | +0.090625 | -0.037500 |
| 0.4 | +0.028125 | +0.146875 | -0.118750 |
| 0.6 | +0.031250 | +0.196875 | -0.165625 |
| 0.8 | +0.150000 | +0.150000 | +0.000000 |

Sections 1–8 are exactly as committed before the run. Cells are in
`docs/density_interaction_a2_run.json`; the verdict is the frozen scorer's output in
`docs/density_interaction_a2_result.json`.
