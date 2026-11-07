# The density interaction: the registered block (2026-11-07)

**Status: HELD, NOT RUN (pre-run review found the dense end has no headroom; docs/DENSITY-INTERACTION-REVIEW.md). The criteria, gates, bars, seed block, exposure schemes and decision table remain as frozen, and no judged cell has run**

**Every figure this block produces carries its arm and its scheme.** The arms are
`global count-ranked top-k` (rank every candidate row in the pool by count, ties on a stable key, take the top k at the cap) and `intra-cell-excluded ranking` (the same count ordering over the eligible rows only; rows whose two tags sit in the same cell are not eligible for the budget); the schemes are
`fixed-total` exposure and `fixed-per-edge` exposure. A number quoted from this block
without its arm, its cap and its scheme is not a number from this block.

## 1. Question and endpoint

Does the value of excluding the intra-cell row class from the prediction budget depend on how dense the world's edge set is, and in which direction?

The endpoint is **precision at a fixed cap**: the share of the budget spent on the world's
edges. It is not coverage. Coverage divides by |W|, which grows from 24 to
192 across this ladder, so a coverage difference is forced by arithmetic and
declines whether or not the treatment does anything — the defect that withdrew the
ordering block's second criterion. Precision's denominator is the arm's own selection, so
its shape across the ladder is a fact about the ranking.

This is a selection measurement, not a behavioural one: it says nothing about prediction,
revision or retention.

## 2. Design

**The world.** 16 tags in four cells, |P_world| = 240 directed non-self pairs; W is a seed-and-density subset of the 192 cross-cell pairs, so no intra-cell row can ever be a world edge; the within-cell filler's event count is (1 - rho_world) times a fixed peak budget, so its share of the stream falls faster than (1 - rho_world) as |W| grows

**Densities.** 0.1, 0.2, 0.4, 0.6, 0.8, i.e. 24, 48, 96, 144, 192 world edges at 16 tags. The top of the
ladder is the whole cross-cell universe, which is why it stops at 0.8: a higher density is
not a denser version of this world but a different vocabulary.

**Exposure.** primary = fixed total exposure (400 events, 50 cycles at every density); sensitivity = fixed exposure per edge (each world edge emitted twice, so the horizon grows with |W|)

**The grid.** 160 cells over seeds **20330101–20330108**, bootstrap **20330109**
— 2 arms x 2 caps x 5 densities x 2 schemes x 8 seeds = 320, of which the judged grid is the primary scheme only: 2 arms x 2 caps x 5 densities x 8 seeds = 160; the sensitivity scheme is analysed as the exposure check and the higher caps are recovery rows. Freshness: the first contiguous window of nine integers at or above 20330101 that appears in no file under docs, tests, benchmarks, research-journal or papers; the ninth is the bootstrap seed and is not a world seed

## 3. The bars, the criteria and the gates

**Interaction bar 0.08; level bar 0.08.** carried as policy from the completed ordering block, where the adoption bar was one half of that block's measured mean delta (0.1615) floored to two decimals. It is NOT calibrated on this layer and this block is not a replication of that figure: the comparison here is a different intervention (eligibility, not ordering) on a different instrument, and a pass means only that the arm cleared a bar fixed before the run

**The criterion is the interaction, judged whole.** interaction on precision at the primary cap: mean over seeds of [Delta(0.8) - Delta(0.1)] at or above the interaction bar, with its paired interval's lower bound above zero, where Delta(rho) = precision(intra_cell_excluded, cap 20) - precision(control, cap 20). level at the dense end, on precision: mean over seeds of Delta(0.8) at or above the level bar, with its paired interval's lower bound above zero and at least seven of eight seeds positive. The conjunction is
the criterion: the number of criteria satisfied is not a score, and a failed half is not
re-read afterwards.

**The exposure check.** if the primary scheme's direction does not hold under the sensitivity scheme (its interaction mean is not positive), the verdict is EXPOSURE ARTIFACT and nothing is adopted; the two schemes exist to separate geometry from exposure

* **G0 liveness** — the two arms' selected sets must differ on at least seven of eight seeds at the sparse end in the primary scheme, or the manipulation did not occur
* **G1 presence ceiling** — every world edge must be present in the pool at every cell (presence = 1.0), or the cell tests memory rather than ranking
* **G2 arithmetic** — covered cannot exceed asserted; precision must equal covered over asserted; precision cannot exceed 1; rho_rank is reported for every cell
* **G3 axis live** — rho_rank must rise from the sparsest to the densest level in both schemes, or the manipulation never reached the ranker
* **G4 control reproduces Gate 13** — the control's precision at the sparse end must not exceed the declared ceiling 0.50; the world must reproduce the condition the study is about rather than being easier
* **G5 identity where it must hold** — on a pool whose every row is a world edge and which contains no intra-cell row, the two arms must select the same set and Delta must be exactly 0; a non-zero Delta there is a harness defect
* **G6 treatment does what it claims** — coverage of the treatment must be at least the control's on every cell, because an excluded row is never a world edge; a violation means the arms are not the pair they claim to be

**Void rule.** a failed gate voids the block and no criterion is read; a cell set that is not the pre-registered grid is refused

## 4. Decision table

| Condition | Verdict | Reading | Decision |
| --- | --- | --- | --- |
| gates pass; C1 and C2 pass; the sensitivity scheme agrees in sign | **DENSITY INTERACTION SUPPORTED** | excluding the intra-cell class spends a larger share of the budget on world edges as the world's edge set gets denser, and the effect is an interaction rather than a main effect of density | adopt intra-cell exclusion as an allocation change behind a recorded owner decision; this licenses no behavioural claim |
| gates pass; the interaction interval places the mean at or below zero | **ADVANTAGE FALLS WITH DENSITY** | the benefit shrinks as the world densifies; the mechanism claim that this is budget competition is wrong, and something other than the crowded class is being measured | do not adopt; diagnose what the arms differ in before any further density work |
| gates pass; both criteria fail and the interval is narrow | **FLAT - GEOMETRY NOT THE LEVER** | the exclusion's value does not vary with density in this world family, so density is not the moderator for this ranking bottleneck | retire budget competition as the lever at this cap and world family; move the line to the candidate space |
| gates pass; a criterion passes but the sensitivity scheme's interaction mean is not positive | **EXPOSURE ARTIFACT** | the direction reverses under the other exposure scheme, which by the design record's own confound rule is an exposure artifact rather than geometry | adopt nothing; report the confound and the two schemes' numbers side by side |
| gates pass; a criterion fails and the interval is wider than 0.30 | **UNDERPOWERED** | the interval cannot place the interaction; absence of an effect is not established | neither pole; the block may be re-registered on a fresh seed block, never re-read |
| a gate fails | **VOID** | reported as the gate, never as a verdict | none; fix the harness and register a new block |

## 5. What is reported

Delta(rho) per seed, per scheme and per cap, with its paired interval; the precision and
coverage of both arms at every density; the pool's intra-cell share and `rho_rank` at every
cell; and the recovery curve at the caps 20, 40, 80, 160, 240 as a characterization, never as
a criterion and never as the rank of the first edge.

## 6. Pre-run amendment A1 — the registered direction was corrected before any cell

**A1, dated 2026-11-07, before the first judged cell.** The design record's registered direction (the advantage declines with density) was measured against the design's own world before any engine cell, and it does not hold: on the designed pools the advantage grows with density at both caps

The evidence is the design's own world, measured with no engine: the arms on the
**designed** pools, over the registered seed block. At the primary cap:

| rho_world | control, cap 20 | treated, cap 20 | Delta, cap 20 | intra-cell share |
|---|---|---|---|---|
| 0.1 | 0.3187 | 0.3938 | +0.0750 | 0.2893 |
| 0.2 | 0.5188 | 0.6062 | +0.0875 | 0.2512 |
| 0.4 | 0.7188 | 0.8875 | +0.1687 | 0.2166 |
| 0.6 | 0.5563 | 0.8688 | +0.3125 | 0.2052 |
| 0.8 | 0.6500 | 1.0000 | +0.3500 | 0.2000 |

Across the ladder the intra-cell share falls (yes), the control's own
precision rises (yes) — which is the design record's mechanical prediction —
and the treatment's advantage rises with density (yes). The mechanism is
stated in the registration: **the benefit of freeing budget is bounded by how many world
rows exist to fill it**, and that count grows with density, so a sparse world has too few
world edges for the freed budget to spend on.

These are properties of the world, not of the engine, and they are not scored. What they
establish is that the corrected direction is **representable** by this instrument — which
the original prediction was not, because on this world it is the opposite of what the
construction produces. The design record's original prediction is retained in its section
5 and marked superseded in its section 10. The criterion tests the corrected direction, the original prediction is retained in the design record and marked superseded there, and the manipulation, world family, arms, caps, endpoint, seed block and bars are unchanged.

## 7. Analysis and runner

`./.venv/bin/python -m benchmarks.score_density_interaction --results docs/density_interaction_run.json --out docs/density_interaction_result.json`

The analysis path is `benchmarks/score_density_interaction.py`, frozen with this registration. It reads only the cells
the runner writes, validates the grid, and imports nothing from the engine. The runner is
`./.venv/bin/python -m benchmarks.run_density_interaction --run`; it can be sliced (`--scheme`, `--seeds`) and appended (`--append`), and it
refuses to overwrite a cell inside one block.

## 8. Allocation

8 world seeds, 1 bootstrap seed, 160 judged cells,
160 exposure-check cells, 3 recovery caps, 2
thresholds, 2 bars. two bars are fixed here: the interaction bar and the level bar

No arm may run before this file is committed.
