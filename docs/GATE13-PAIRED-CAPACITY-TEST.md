# Gate 13 Paired Full-Acquisition Capacity Experiment

**Date:** 2026-10-28  
**Scope:** Paired scratch-only full acquisition runs across diagnostic seeds `20261101`–`20261105`  
**Status:** Diagnostic Complete. Seeds `20261101`–`20261105` designated diagnostic / inspected.  
**Raw Telemetry:** `docs/gate13_paired_capacity_test.json`

---

## 1. Executive Summary & Experimental Finding

To test whether the `MAX_PREDICTIONS = 20` cap is sufficient to explain the Gate 13 acquisition failure under full sleep cycles—or whether downstream selection, decay, or persistence bottlenecks would remove those transitions—we executed a paired, scratch-only full acquisition experiment (cycles 0–109):

- **Control:** The standard engine with `MAX_PREDICTIONS = 20`.
- **Treatment:** The identical engine and observation stream, but raising only `MAX_PREDICTIONS` to 1,000 (enough to admit all candidate predictions meeting `PREDICTION_MIN_COUNT = 5`).
- **All other systems frozen:** Minimum count thresholds, community detection, loop detection, natural selection, decay, pruning, composite formation, readout projection, and the Gate 13 threshold ($0.50$) remained identical.

### Results Across Diagnostic Seeds

| Seed | Control (Cap = 20) Final Asserted Overlap | Control Gate 13 Verdict | Treatment (Cap = 1000) Final Asserted Overlap | Treatment Gate 13 Verdict | Control Asserted Breakdown | Treatment Asserted Breakdown |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `20261101` | **0 / 112** (0.0%) | **FAIL** | **110 / 112** (98.2%) | **PASS** | 26 intra / 1 inter | 52 intra / 189 inter |
| `20261102` | **1 / 112** (0.9%) | **FAIL** | **112 / 112** (100.0%) | **PASS** | 39 intra / 2 inter | 53 intra / 190 inter |
| `20261103` | **1 / 112** (0.9%) | **FAIL** | **112 / 112** (100.0%) | **PASS** | 38 intra / 2 inter | 53 intra / 191 inter |
| `20261104` | **0 / 112** (0.0%) | **FAIL** | **112 / 112** (100.0%) | **PASS** | 28 intra / 0 inter | 52 intra / 192 inter |
| `20261105` | **3 / 112** (2.7%) | **FAIL** | **112 / 112** (100.0%) | **PASS** | 34 intra / 3 inter | 53 intra / 190 inter |

---

## 2. Decision Rule Interpretation

The preregistered interpretation of this diagnostic experiment:
- *“Final coverage clears 0.50 with the higher cap: strong evidence the cap is sufficient to explain the acquisition failure on these seeds.”*

**Outcome:**
Under Treatment, final asserted coverage rose from **0.0%–2.7% to 98.2%–100.0%**, easily clearing the 0.50 Gate 13 sufficiency threshold on every single seed.

This establishes two critical facts:
1. **Downstream selection does NOT discard cross-cell predictions:**
   When admitted by the detector, cross-cell predictions are reinforced and retained across 110 sleep cycles through natural selection and decay. They persist into the final candidate database.
2. **The Layer-1 cap alone is the bottleneck on these seeds:**
   The failure of Gate 13 in the baseline engine is caused entirely by the sorting-by-count truncation at `MAX_PREDICTIONS = 20`, where high-count within-cell temporal edges monopolize the top 20 slots.

---

## 3. Cycle-by-Cycle Accumulation Milestones (Seed `20261101`)

Tracking the emergence of cross-cell predictions across cycles under Treatment shows steady developmental accumulation:

| Cycle | World Edges in Temporal Memory | World Edges in Admitted Predictions | Admitted Prediction Candidates Count |
| :---: | :---: | :---: | :---: |
| 10 | 98 / 112 | 7 / 112 | 57 |
| 20 | 110 / 112 | 46 / 112 | 182 |
| 30 | 112 / 112 | 82 / 112 | 266 |
| 40 | 112 / 112 | 98 / 112 | 305 |
| 50 | 112 / 112 | 106 / 112 | 324 |
| 60 | 112 / 112 | 107 / 112 | 328 |
| 70 | 112 / 112 | 108 / 112 | 329 |
| 80 | 112 / 112 | 108 / 112 | 332 |
| 90 | 112 / 112 | 108 / 112 | 333 |
| 100 | 112 / 112 | 110 / 112 | 336 |
| 110 | 112 / 112 | 110 / 112 | 336 |

In contrast, under Control (`cap = 20`), the number of admitted world edges in predictions remained at **0 / 112** at every single cycle from cycle 10 to 110.

---

## 4. Methodological Conclusion & Options

1. **Protocol Rigor & Integrity:**
   - The engine files (`organica/sleep.py`, `organica/memory.py`) remain completely unmodified.
   - The Gate 13 threshold remains fixed at $0.50$.
   - Seeds `20261101`–`20261105` are classified as diagnostic preflight seeds and cannot be used as confirmatory evidence.
2. **Options for Project Organica:**
   - **Option A (Stimulus / Task Redesign):** Design the task stimulus so that transition relations are not swamped by intra-event co-occurrences (e.g. single-tag transitions instead of 2-tag co-occurring events), allowing the frozen engine's `MAX_PREDICTIONS = 20` to capture cross-state dynamics naturally.
   - **Option B (Engine Parameter Reconfiguration):** Formally document the Layer-1 capacity cap limitation as a known boundary condition of Organica V1, and specify a capacity or diversity parameter for future engine revisions.

---

## 5. Re-measurement on later builds (2026-11-06)

**The cap-20 range above does not reproduce on any build from `9f2c8e1` (2026-11-04) onward.**
The same five diagnostic seeds, the same harness (`run_paired_condition`, control arm,
`max_predictions=20`, cycles 0–109) and the same 112 world edges, re-measured:

| build | covered world edges per seed | asserted-coverage range | Gate 13 passes |
|---|---|---|---|
| `89b0744` as recorded (2026-10-28) | 0 / 1 / 1 / 0 / 3 | 0.0000–0.0268 | 0 of 5 |
| `e6d1bcc` (master at the freeze) | 81 / 87 / 91 / 77 / 74 | 0.6607–0.8125 | 5 of 5 |
| reader + carried-forward amendment (working tree, 2026-11-06) | 59 / 54 / 84 / 60 / 61 | 0.4821–0.7500 | 4 of 5 |

Bisected on seed `20261101`: `89b0744` returns 1 of 112 — inside the recorded band, and the only
build measured here that stays inside it — **`9f2c8e1`** is the first build that leaves it at
59 of 112, and `7201d79` returns 81, where it stays through
`6d45eb7` and `e6d1bcc`. Runs are deterministic within a build (seed `20261101` run twice on
`e6d1bcc` returned 81 both times, and `PYTHONHASHSEED=0` returned
81), so the difference is the build, not the draw.

Two limits on this correction. **First**, the re-check of `89b0744` covers one seed, not five:
`20261101` reads 0 of 112 recorded and 1 of 112 re-measured, so
the *band* reproduces on its own build and the per-seed value differs by one edge — reported, not
smoothed. **Second**, the cap-1000 treatment arm has since been re-run on both later builds (§6): it reads
1.0000–1.0000 on the amended engine, so the 98.2–100 % figure above is superseded upward rather than
withdrawn, and the paired contrast is re-established — but at 0.4821–0.7500 against 1.0000–1.0000, not
0.0–2.7 % against 98.2–100 %.

**What this means for the record.** The sentence "the frozen engine asserts 0.0 %–2.7 % of the
world's relations at `MAX_PREDICTIONS = 20`" is true of the model as it stood on 2026-10-28 and
false of every build after it that was measured here (`9f2c8e1` onward). It is quoted in
`docs/ACQUISITION-ENDPOINT-AUDIT.md`, `docs/FORMATION-UTILIZATION-PREREGISTRATION.md`,
`docs/REUSABLE-KNOWLEDGE-PREREGISTRATION.md`, `docs/GATE13-CAUSAL-ACCOUNT.md`,
`docs/ORGANICA-V2-DESIGN-BRIEF.md`, `docs/FACTS-SHEET.md` (AC12), `docs/USER-MANUAL.md` (§2 and
finding 25), `papers/01_developmental_structure_formation.md` and the research journal; those
documents are not edited here, and this section is the correction they should be read against.
Every verdict that rested on the Gate 13 failure — the campaign stopping at its own gate, the
"capacity is the proximate bound" account, the V2 premise — was measured before 2026-11-04 and is
now a statement about that build. Nothing here re-scores those verdicts for the runs that produced
them; what it does is withdraw the range as a description of the *current* engine.

Artifact: `docs/gate13_cap20_build_comparison.json`.

---

## 6. Treatment arm re-measured (2026-11-06)

The cap-1000 arm was re-run on the same five diagnostic seeds and the same 112 world edges:

| build | covered world edges per seed | asserted-coverage range | Gate 13 |
|---|---|---|---|
| `89b0744` as recorded (2026-10-28) | 110 / 112 / 112 / 112 / 112 | 0.9821–1.0000 | 5 of 5 pass |
| `e6d1bcc` (master at the freeze) | 112 / 112 / 112 / 112 / 112 | 1.0000–1.0000 | 5 of 5 pass |
| reader + carried-forward amendment (working tree) | 112 / 112 / 112 / 112 / 112 | 1.0000–1.0000 | 5 of 5 pass |

**98.2–100 % holds, and improves to 100 % on every seed.** Raising only the Layer-1 cap still restores
the whole world's relations on both later builds, so the cap remains the *proximate* bound in the sense
this test measures, and the freeze amendment does not disturb it.

What changes is the size of the contrast, and it is worth stating plainly. On `89b0744` the paired
comparison was 0.0000–0.0268 at cap 20 against 0.9821–1.0000 at cap 1,000. On the amended
engine it is **0.4821–0.7500 against 1.0000–1.0000** — the cap still explains a great deal, but the
baseline it is compared against is no longer a near-zero one, so a reader should not carry the old
margin forward. Both statements are about five diagnostic seeds; no confirmatory seed ran.

Two limits. The measurement is **at the ceiling**: 112 of 112 world edges is the maximum this metric
can return, so it cannot discriminate between builds on coverage and says nothing about precision —
the 0.3438 precision ceiling is a separate measurement and is untouched by any of this. And the only
differences between the two later builds are in the asserted set's size (243–247 edges at `e6d1bcc`,
244–245 amended), not in the world edges covered.

Artifact: `docs/gate13_cap1000_build_comparison.json`.

---

## 7. Asserted-set precision at both caps (2026-11-06)

Coverage is at its ceiling in §6, so coverage cannot say whether the amended engine's asserted set is
*better* or merely *larger*. Precision can: of the edges the organism asserts at the end of
acquisition, what fraction are real world edges?

**Basis.** `covered_world_edges / final_asserted_edges_count` for each cell of the paired harness —
the final asserted structure filtered to the world's vocabulary and excluding non-vocabulary
markers, which is exactly the set coverage is scored against. This is **not** the Layer-1
selection-precision ceiling of 0.3438 in `docs/GATE13-CAUSAL-ACCOUNT.md`; that measures a different
quantity on a different basis, and the two numbers are not comparable.

| arm | precision per seed | median |
|---|---|---|
| `89b0744` cap 20 | 0.0000 / 0.0244 / 0.0250 / 0.0000 / 0.0811 | 0.0244 |
| `89b0744` cap 1,000 | 0.4564 / 0.4609 / 0.4590 / 0.4590 / 0.4609 | 0.4590 |
| `e6d1bcc` cap 20 | 0.4602 / 0.4462 / 0.4596 / 0.4724 / 0.4654 | 0.4602 |
| `e6d1bcc` cap 1,000 | 0.4571 / 0.4571 / 0.4590 / 0.4534 / 0.4609 | 0.4571 |
| amended cap 20 | 0.4155 / 0.4576 / 0.4746 / 0.4651 / 0.4552 | 0.4576 |
| amended cap 1,000 | 0.4571 / 0.4571 / 0.4590 / 0.4590 / 0.4571 | 0.4571 |

**The ceiling hides no quality change, in either direction.** Every arm on a later build sits between
0.4155 and 0.4746 — a spread of 0.0591 — while recall moves from the amended cap-20 range
(0.4821–0.7500) to 1.0000 at cap 1,000. The amended engine's median precision is
0.4576 at cap 20 against 0.4602 at `e6d1bcc`/cap 20, and 0.4571 at cap 1,000. The extra edges that
raising the cap admits are world and non-world in very nearly the same proportion as the edges
already there, so *recall rises and precision does not*: the amendment changes which structures are
asserted and how many, not how often an asserted edge is a world edge.

The one arm that differs is the recorded `89b0744` control, whose precision is 0.0000 on two seeds
and 0.0244 / 0.0250 / 0.0811 on the others — it asserted
27–41 edges and almost none of them were world edges. That is the arm §5 shows
no longer reproduces.

**Limits.** Five diagnostic seeds of one 2-tag compositional world family, no confirmatory seed; and
this is the *final asserted set*, so it says nothing about the earlier Layer-1 stage or about
precision under a per-source allocation rule.

Artifact: `docs/gate13_asserted_precision.json`.

---

## 8. The capacity curve, and where the step actually is (2026-11-06)

§6 measured two points and §7 measured precision at them. Two points cannot show shape, so the cap
was swept — 1, 2, 5, 10, 20, 50, 100, 200, 500, 1,000 — on all three builds, reporting recall,
precision and the size of the final asserted set together. Figure:
`docs/figure_gate13_capacity_curve_by_build.svg`; every number in it comes from
`docs/gate13_cap_curve_by_build.json`.

This is **not** the seed-keyed capacity sweep behind `docs/GATE13-CAUSAL-ACCOUNT.md` §3 — that is
`docs/gate13_capacity_sweep.json` (caps 20/40/80/uncapped on `89b0744` alone), a separate artifact that neither replaces
the other. Where the two overlap they agree on 4 of 5 seeds at cap 20, and both give 0–3 of 112. The one seed that differs is 20261101, by a single
edge: this sweep (hash order unpinned) returns 1, the committed sweep returns 0, and re-running that
cell with `PYTHONHASHSEED=0` returns 0 on 27 asserted edges — so the difference is
hash-order sensitivity in a harness that does not pin it, not a measurement of a different engine.

### 8.1 Recall (world edges asserted ÷ 112, median of seeds)

| build | 1 | 2 | 5 | 10 | 20 | 50 | 100 | 200 | 500 | 1000 |
|---|---|---|---|---|---|---|---|---|---|---|
| `89b0744` (recorded) | 0.0000 | 0.0000 | 0.0000 | 0.0089 | 0.0089 | 0.0000 | 0.1696 | 0.5714 | 1.0000 | 1.0000 |
| `e6d1bcc` | 0.7143 | 0.7143 | 0.7411 | 0.7768 | 0.7768 | 0.7857 | 0.8839 | 0.9821 | 1.0000 | 1.0000 |
| amended engine | 0.5089 | 0.5089 | 0.5089 | 0.5089 | 0.5357 | 0.6071 | 0.6964 | 0.9375 | 1.0000 | 1.0000 |
| `89b0744` (recorded) seeds | 3 | 3 | 3 | 3 | 5 | 3 | 3 | 3 | 3 | 5 |
| `e6d1bcc` seeds | 5 | 5 | 3 | 3 | 3 | 3 | 2 | 1 | 1 | 5 |
| amended engine seeds | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 |

### 8.2 Precision (world edges ÷ asserted edges, median of seeds)

| build | 1 | 2 | 5 | 10 | 20 | 50 | 100 | 200 | 500 | 1000 |
|---|---|---|---|---|---|---|---|---|---|---|
| `89b0744` (recorded) | 0.0000 | 0.0000 | 0.0000 | 0.0286 | 0.0250 | 0.0000 | 0.2836 | 0.4508 | 0.4590 | 0.4590 |
| `e6d1bcc` | 0.4591 | 0.4552 | 0.4596 | 0.4596 | 0.4596 | 0.4573 | 0.4670 | 0.4641 | 0.4590 | 0.4571 |
| amended engine | 0.4651 | 0.4651 | 0.4615 | 0.4597 | 0.4576 | 0.4626 | 0.4564 | 0.4619 | 0.4571 | 0.4571 |
|---|---|---|---|---|---|---|---|---|---|---|
| `89b0744` (recorded) | 30 | 39 | 34 | 32 | 37 | 40 | 68 | 128 | 243 | 243 |
| `e6d1bcc` | 173 | 173 | 190 | 194 | 195 | 192 | 212 | 237 | 244 | 245 |
| amended engine | 129 | 129 | 130 | 130 | 134 | 147 | 174 | 224 | 245 | 245 |

The last block of rows is the **asserted-set size**, and it is the quantity that makes the other two
readable: it is itself a function of the cap, so recall and precision are being read against a moving
population rather than a fixed budget.

**Precision is flat across the entire curve, not only at its endpoints.** Over all ten caps the
amended engine's median precision moves within 0.0087
(0.4651 at cap 1 to 0.4571 at cap 1,000) while its recall rises from
0.5089 to 1.0000; `e6d1bcc` moves within 0.0118 (0.4591 to
0.4571) while its recall rises from 0.7143 to 1.0000. So the asymmetry in §7 is a property of
the whole dose-response, not of the two caps that happened to be compared: within each build, raising
the cap buys recall and leaves precision where it was.

**The step belongs to `89b0744`, and it is a step in the asserted set rather than in precision.**
On that build recall is 0.0000–0.0000 — at most one of 112 world edges — for every cap up to 50, then
0.1696 at cap 100, 0.5714 at 200 and 1.0000 at 500. Its asserted set is
30–40 edges all the way out to cap 50 and only then begins to grow, to 68 at cap 100,
128 at 200 and 243 at 500. Precision at those small caps is 0.0000–0.0286, zero on 4 of the 6 caps up to 50, and where it is zero it is a *measurable* zero: the arm asserts 30–40 edges and none of them is a world edge. So the low-cap
regime on the older build is not "high precision at low recall" (nothing is asserted that is world-aligned
at all) and it is not a threshold in discriminativeness; it is a threshold in **asserted-set size**, and
coverage follows the set. On the two later builds the asserted set is not cap-bound (129 edges on the
amended engine and 173 on `e6d1bcc` already at cap 1), which is why there is no step to find there.

**The amendment shrinks the asserted set, and that costs coverage — it is not a better selector.**
Against `e6d1bcc` the amended engine is *lower* at every cap below 500: recall 0.5089 against 0.7143 at cap 1,
0.5357 against 0.7768 at cap 20, 0.6964 against 0.8839 at cap 100, converging to equality at
500 and 1,000 (1.0000 against 1.0000 and 1.0000 against 1.0000). The asserted set is smaller (129 against
173 edges at cap 1) and the precision is unchanged (0.4651 against 0.4591). That is the signature of a
**proportional reduction**: the carried-forward copies the amendment stops counting were not chiefly noise,
they included world edges too, so removing them removes both at about the same rate. The earlier reading
that the amendment improves structure selection is therefore **not supported** by the sweep, and the
amendment's justification stands where it always did — semantically, that a prior carried across cycles
should not be scored as this cycle's evidence — not on coverage.

Against the recorded build the picture is a large coverage *gain* at small caps (0.0000 to
0.5089 at cap 1) and equality from cap 500 up (1.0000 against 1.0000). Both readings belong in the same sentence, because a reader who
takes only the first will conclude the amendment improves coverage, and a reader who takes only the second
will conclude it costs coverage; it does the first against the 2026-10-28 build and the second against the
freeze commit.


### 8.3 What capacity buys, and what the amendment drops (2026-11-06)

Flat precision at the endpoints raises two questions the medians cannot answer: when the cap rises, how
accurate are the edges it *adds*; and when the amendment shrinks the asserted set, what kind of edge does
it *remove*. Both are ratios of differences, so both are computed **per seed and paired within a seed** —
a difference of medians is not the median of differences, and here it is the difference that carries the
claim. Source: `docs/gate13_cap_curve_by_build.json`, key `marginal_assertions`.

**The edges capacity buys are almost exactly as accurate as the ones it starts with.** Marginal precision
is world edges gained ÷ asserted edges gained between cap 1 and cap 1,000, per seed:

| build | seeds | marginal precision (median) | marginal range | initial-set precision (cap 1) |
|---|---|---|---|---|
| amended engine | 5 | 0.4483 | 0.4265–0.5189 | 0.4651 |
| `e6d1bcc` | 5 | 0.4600 | 0.4432–0.5102 | 0.4591 |
| `89b0744` (recorded) | 5 | 0.5213 | 0.5185–0.5411 | 0.0000 |

The amended engine's added edges sit 0.0168 below
its own cap-1 set; `e6d1bcc`'s sit 0.0009 above.
Both gaps are a fraction of the endpoint spans in §8.2, so "precision is flat" is not an averaging artefact:
what the cap adds is asserted at nearly the hit rate the set already had. `89b0744`'s high marginal figure is
not a quality gain — its cap-1 set contains no world edges, so there was nothing
there to dilute the rate — and its endpoint precision (0.4590) is the same rate both later builds reach
(0.4571 on the amended engine and at `e6d1bcc`); the higher marginal figure is arithmetic, not quality.

**Above saturation, precision is arithmetic rather than measurement.** In all 22 cells where the asserted set covers every world edge (all three builds, at caps 500 and 1,000): precision is exactly 112 ÷ the asserted-set size (0.4571 at 245 edges, 0.4590 at 244 edges), so the only
quantity free to vary is the size of the set and the flat top of §8.2's precision curve is forced, not
observed. The caps that carry the claim are the unsaturated ones: restricted to caps 1–200, where recall is
below 1, the amended engine's precision still spans 0.0087 (0.4564–0.4651) and `e6d1bcc`'s
0.0118 (0.4552–0.4670) — identical to the spans over the full range — so the finding does not
depend on the caps at which it cannot fail.

**The amendment removes a sample of edges, not a sample of noise.** At cap 1, the edges `e6d1bcc` asserts
and the amended engine does not, paired by seed:

| seed | `e6d1bcc` asserted | amended asserted | dropped | dropped world edges | dropped precision | retained precision |
|---|---|---|---|---|---|---|
| 20261101 | 173 | 139 | 34 | 23 | 0.6765 | 0.4101 |
| 20261102 | 196 | 116 | 80 | 34 | 0.4250 | 0.4569 |
| 20261103 | 199 | 176 | 23 | 8 | 0.3478 | 0.4716 |
| 20261104 | 159 | 120 | 39 | 16 | 0.4103 | 0.4750 |
| 20261105 | 143 | 129 | 14 | 6 | 0.4286 | 0.4651 |
| **total** | 870 | 680 | 190 | 87 | 0.4579 (pooled) | 0.4651 (median) |

Pooled, 87 of the 190 removed edges are world edges
(0.4579), against a retained rate of 0.4651; the median per-seed removed
rate is 0.4250 (range 0.3478–0.6765), which weights
seeds equally rather than by how many edges each one loses. On seed 20261101 the removed edges were the
better sample (0.6765 against 0.4101). So the amendment does not
preferentially discard noise: it discards edges whose world-edge density is the same, within
0.0401, as the set it keeps, and on one seed above it. That is why
recall falls while precision does not move — and it makes the familiar account ("the noisy assertions were
dropped and the useful ones kept") false here, in the specific quantity that would have to shift for it to
be true. `89b0744` describes a different failure: at caps up to 50 it asserts 24–46 edges of
which 0–6 are world edges, so its precision is low because the ranking reaches almost
nothing, not because it discards well.



### 8.4 The candidate population, and why precision sits at the base rate (2026-11-06)

§8.2's flat precision and §8.3's "the amendment removes a sample of edges" both defer to a question the
medians cannot answer: what is the ranking choosing *from*? The population was measured directly on the
amended engine with the cap removed (1,000, the treatment arm): the `precedes` table restricted to world
vocabulary, which is the set `_build_predictions` ranks. On every seed it is **240 rows and it
contains all 112 world edges** — a coverage ceiling of 1.0000 — so its base rate of world
edges is 112 ÷ 240 = **0.4667**. At cap 1,000 the asserted set is
245 edges covering all 112: precision 0.4571, which is the base rate. Nothing
was filtered out; the population was asserted in full.

**The count ranking barely sorts the population, and where it does sort it, it sorts the wrong way.**
World-edge density by count-decile, median of the five diagnostic seeds:

| decile | rank range | rows | world-edge density (median) | range across seeds |
|---|---|---|---|---|
| 1 | 1–24 | 24 | 0.2500 | 0.2083–0.3750 |
| 2 | 25–48 | 24 | 0.5000 | 0.3750–0.5833 |
| 3 | 49–72 | 24 | 0.5000 | 0.4167–0.5833 |
| 4 | 73–96 | 24 | 0.5417 | 0.5000–0.5833 |
| 5 | 97–120 | 24 | 0.5000 | 0.3750–0.5000 |
| 6 | 121–144 | 24 | 0.5417 | 0.4167–0.6667 |
| 7 | 145–168 | 24 | 0.5417 | 0.5000–0.6250 |
| 8 | 169–192 | 24 | 0.5000 | 0.4583–0.5833 |
| 9 | 193–216 | 24 | 0.4583 | 0.4167–0.5833 |
| 10 | 217–240 | 24 | 0.3333 | 0.2917–0.4167 |

**192 of 240 rows share the identical count 10** — the `temporal_count` column is
degenerate across ranks 25–216, so inside that block admission is decided by sort order, not by
evidence. That is also the mechanism behind the hash-order sensitivity noted in §8: which of the tied rows a
small cap admits is not a measurement of anything. The genuinely ordered rows are the top of the table, and
there the ordering is anti-discriminative: cumulative density in the top 20 is
0.1500–0.2500 against a base rate of 0.4667.

**Against a random draw of the same size, the asserted set is at chance.**

| build | cap | asserted (median) | covered (median) | chance (asserted × 0.4667) | difference |
|---|---|---|---|---|---|
| `amended` | 1 | 129 | 57 | 60.2 | -3.2 |
| `amended` | 20 | 134 | 60 | 62.5 | -2.5 |
| `amended` | 100 | 174 | 78 | 81.2 | -3.2 |
| `amended` | 1000 | 245 | 112 | 114.3 | -2.3 |
| `e6d1bcc` | 1 | 173 | 80 | 80.7 | -0.7 |
| `e6d1bcc` | 20 | 195 | 87 | 91.0 | -4.0 |
| `e6d1bcc` | 100 | 210.0 | 96.5 | 98.0 | -1.5 |
| `e6d1bcc` | 1000 | 245 | 112 | 114.3 | -2.3 |
| `89b0744` | 1 | 30 | 0 | 14.0 | -14.0 |
| `89b0744` | 20 | 37 | 1 | 17.3 | -16.3 |
| `89b0744` | 100 | 68 | 19 | 31.7 | -12.7 |
| `89b0744` | 1000 | 243 | 112 | 113.4 | -1.4 |

So "why 0.4571" has an arithmetic answer. It is the population's own composition — 112
law-bearing pairs among 240 observed vocabulary pairs — and both later builds assert a set
statistically indistinguishable from a random sample of the population (median -2.4 world
edges below chance across the 8 build/cap points). It is not a property of the amendment, of the
cap, or of the ranking criterion. The pool is also not deficient in the way the upstream story expects: it is
**complete** in coverage but unrankable, because the engine holds no observable that separates the
112 law edges from the 128 others and its only ordering ties across
80% of the rows. `docs/GATE13-RANKING-CRITERION.md` §3 reached the same conclusion from
the criterion grid (best cell 0.0804 coverage at precision 0.4500); this states it as a property of the
population rather than of five formulas.

**Limits.** Five diagnostic seeds, one 2-tag compositional world, diagnostic only. The population is measured
on the cap-1,000 arm, so the asserted sizes for the other caps are §8.1's cells compared against that
population; 4–6 asserted edges at cap 1,000 are absent from the final `precedes`
table, so the chance comparison is an approximation to that size. Decile membership inside the tied block is
sort order, which is why the decile densities are reported as a range across seeds and not as a trend.
Artifact: `docs/gate13_candidate_pool_density.json`.



### 8.5 Can anything break the tie? (2026-11-06)

The tie block leaves one question: does any ordering the engine can already compute beat the population's
base rate at the top? Six were measured on the same population, all from fields already stored or derivable
from the table — `count` (the admission rule), `count / source_freq` (the `ratio` the engine computes and
stores), `count / target_freq`, cosine, pmi, and `count / source_out_degree` (a structural variant, to test
whether out-degree carries anything):

| criterion | distinct values | modal tie share | top-20 density | top-40 | top-80 |
|---|---|---|---|---|---|
| `count` | 9–14 | 0.78–0.86 | 0.1500–0.2500 | 0.3000–0.3750 | 0.4000–0.4625 |
| `ratio` | 39–48 | 0.11–0.14 | 0.5000–0.6000 | 0.5000–0.5500 | 0.4375–0.5000 |
| `target_ratio` | 41–48 | 0.09–0.12 | 0.2000–0.4000 | 0.3000–0.3500 | 0.2500–0.3125 |
| `cosine` | 107–137 | 0.02–0.03 | 0.1500–0.4000 | 0.3250–0.4500 | 0.4125–0.4625 |
| `pmi` | 106–137 | 0.02–0.03 | 0.1500–0.4000 | 0.3250–0.4750 | 0.4500–0.4750 |
| `count_per_outdeg` | 9–14 | 0.78–0.86 | 0.1500–0.2500 | 0.3000–0.3750 | 0.4000–0.4625 |

Base rate on every seed is 0.4667; a criterion that ranked perfectly would read 1.0000 at every k.

**The stored `ratio` is the only criterion that breaks the tie.** It takes 39–48
distinct values against 9–14 for count, and its largest tie is
0.11–0.14 of the pool rather than 0.78–0.86. Its top-20 density exceeds the base rate on all five
seeds (0.5000–0.6000), pooled 54 of 100 rows against
46.67 expected — about 1.47 SE. **That is a directional signal, not an established effect:** at k = 20
one row is worth 0.05, the per-seed binomial SE is about 0.11, and the lift is gone by top-80
(0.4375–0.5000, i.e. at base). Establishing it needs more rows per test, not more seeds.

**Everything else is at or below chance, and the engine's own rule is significantly below it.** Pooled top-20
under `count` is 20 of 100 rows against 46.67 expected (-5.35 SE).
`count / out_degree` is identical to `count` on every seed, because out-degree does not vary usefully across
the pool — the structural variant carries nothing here.

**This refines, and does not overturn, `docs/GATE13-RANKING-CRITERION.md`.** That record measured `ratio`
selecting 20 mixed edges with coverage 0.0000 and concluded the criterion was actively harmful. That was the
**raw** table, where the engine's own vocabulary rows have no frequency entry, `freqs.get(tag_from, 1)` returns 1,
and so ratio collapses to count and the internal rows win. Restricted to the world-vocabulary pool there are no
such rows, and the same stored field becomes the only ordering above base. The failure therefore has two
separable parts — **contamination** (a provenance problem) and **tie-breaking** (a criterion problem) — and
neither alone is sufficient, which is what that document concluded from a different measurement.

**Limits.** Five diagnostic seeds, one 2-tag world; each top-k test is 20–80 rows of one population, so the
pooled 1.47 SE figure is reported as directional and no criterion is claimed to clear 0.50 Gate 13-style
thresholds. The population is the cap-1,000 arm; the other caps are §8.1's cells. Artifact:
`docs/gate13_tiebreak_tests.json`.


**Limits.** Five diagnostic seeds on the amended engine and at most three on each earlier build (the seed
count per cell is in the tables above, and `89b0744`'s cap-20/1,000 cells for its other two seeds are the
2026-10-28 record rather than a re-run). One 2-tag compositional world family; no confirmatory seed. The
figure draws medians only, so the per-seed spread is in the artifact and not in the picture.

### 8.6 The pre-registered `ratio` arm: the ordering is a binding constraint (2026-11-06)

Protocol: [`docs/GATE13-RATIO-ADMISSION-PREREGISTRATION.md`](GATE13-RATIO-ADMISSION-PREREGISTRATION.md), arms and
predictions frozen before the run. Arm **C** is the count-sorted admission of this harness, arm **R** is the
same construction and cap ordered by the stored `ratio = count / source_freq`, arm **E** is the engine's own
rule at the same budget, added by Amendment 1 as a reference and not used to score anything. Five diagnostic
seeds, caps 10/20/100/1,000, `PYTHONHASHSEED=0` in all three arms, 55 cells.
`benchmarks/run_ratio_admission_arm.py`, artifact `docs/gate13_ratio_arm.json`.

**Correction to §8.4 and §8.5, disclosed before the run and not folded into the numbers.** Those sections call
count "the admission rule". That is the rule of `PairedDiagnosticSleepService`, the harness every §5–§8 figure
here was measured under; the engine's own `_build_predictions` sorts transitions by *target entropy* first,
then transition probability, then count, and splits the budget half to transitions and half to
co-occurrences. The *measurement* in §8.4–§8.5 stands — count-ranking is at chance and the stored `ratio` is
the only tested ordering above base — but the sentence that it is what the engine does is wrong, and arm E
exists to say what the engine's rule actually costs.

**Primary cap, paired per seed** (M1 coverage, M5 asserted size, M2 precision):

| seed | C coverage | R coverage | Δ | asserted C / R | C precision | R precision | Δ |
|---|---|---|---|---|---|---|---|
| 20261101 | 0.5268 | 0.5893 | +0.0625 | 142 / 157 | 0.4155 | 0.4204 | +0.0049 |
| 20261102 | 0.4821 | 0.5357 | +0.0536 | 118 / 132 | 0.4576 | 0.4545 | -0.0031 |
| 20261103 | 0.7500 | 0.8214 | +0.0714 | 177 / 190 | 0.4746 | 0.4842 | +0.0096 |
| 20261104 | 0.5357 | 0.6161 | +0.0804 | 129 / 139 | 0.4651 | 0.4964 | +0.0313 |
| 20261105 | 0.5446 | 0.6161 | +0.0715 | 134 / 146 | 0.4552 | 0.4726 | +0.0174 |

**P1 — the control is at chance: passes, 4 of 5.** C's precision at cap 20 sits within 0.05 of the
0.4667 base rate on 4 seeds; the exception is 20261101, at 0.0512 from base,
just outside the band. **P2 — R breaks the tie: passes, 5 of 5.** R takes
39–48 distinct score values
against 9–14 for C, and its
largest tie falls from 0.7833–0.8625
of the pool to 0.1083–0.1375.
**P3 — R's coverage exceeds C's: passes, 5 of 5**, by 0.0536 to 0.0804 coverage. **P4 — the
precision guard: passes.** Paired at the same cap, precision moves by -0.0031 to 0.0313; on 1
seed it falls, by at most 0.0031. A strictly size-matched interpolation is
possible on 1 of 5 seeds, because R's smallest measured asserted set at cap 10 already exceeds C's
at cap 20 — where it is possible it reads 0.0275. Elsewhere R dominates at a
*larger* set, which is the stronger statement: more edges, higher precision.

**Marginal precision runs the other way, and that is what a better ordering looks like.** Between cap 20 and
cap 1,000 C adds 242 world edges among 523 new assertions
(0.4627) and R adds 204 among 459
(0.4444). R's margin is *lower* precisely because it front-loads the pool: by cap 20
it has already asserted more of the world, so the edges left for the margin are the worse ones. Both arms end at
the same full pool, so the endpoint is unchanged — this is a redistribution of quality towards small caps, not a
gain at saturation.

**The engine's own rule sits between the two, and at cap 100 below count.** Arm E at cap 20 gives a median
coverage of 0.5536 against C's 0.5357 and R's
0.6161, with precision 0.4662. At cap 100 it is
*worse than count on both* — coverage 0.6607 against
0.6964, precision 0.4444 against
0.4564 — so entropy-first ordering does not rescue the window, and the stored
`ratio` beats the rule the engine actually applies as well as the harness's simplification of it.

**Instrument note, disclosed.** The first R instantiation re-sorted the parent's return value, which the parent
had already truncated to the cap; seven R cells reproduced C exactly, which is the signature of a no-op. Those
rows were discarded before any result was read, the subclass was changed to lift the parent's budget for the
one call and apply the cap itself, and no protocol quantity — arm definition, cap, seed, metric or prediction —
changed. The discarded rows are not in the artifact.

**What the outcome table says.** P3 and P4 both pass, so the reading is the registered one: *admission is a
binding constraint and capacity is downstream*. §8.2–§8.3 measured the second half — capacity buys recall at the
set's existing hit rate. This measures the first half: which edges get in matters more than how many do, and
the engine already computes the field that orders them.

**Limits.** Five diagnostic seeds, one 2-tag compositional world, no confirmatory block. `ratio` is one of six
tested orderings and was the only one above base at 1.47 SE, so the *choice* of it is not established by these
cells — only that applying it at a fixed cap raises coverage without a precision penalty. Arm C is the
harness's rule, so the C/R contrast sizes the ordering effect inside this benchmark, not inside the engine;
arm E is the engine's rule and carries no registered prediction. The caps are a coarse grid, so asserted sizes
between measured points are interpolated, and the cap-10 cells exist only to bracket P4. A positive result here
is a reason to write a confirmatory block, not to alter a frozen primitive. Artifact: `docs/gate13_ratio_arm.json`.

### 8.7 The confirmatory block: the treatment reproduces, the control's chance premise does not (2026-11-06)

Pre-registration [`docs/GATE13-RATIO-CONFIRMATORY-PREREGISTRATION.md`](GATE13-RATIO-CONFIRMATORY-PREREGISTRATION.md),
authorised the same day on **allocation B** (20270602–20270626, the block with 0 occurrences across the 440 files
scanned, taken over the requested but doubly-committed 20261106–20261130). 275 cells, the arm exactly as
development ran it, `PYTHONHASHSEED=0`, no engine change; artifact `docs/gate13_ratio_confirm.json`.

**Verdict: PARTIAL / NOT COMPARABLE.** Scored as §5 wrote it, before the numbers were in. C0, C2, C3 and C4 pass; **C1 fails**,
and under the frozen outcome table that makes the block not comparable to the development block rather than a
confirmation of it.

| seed | C coverage | R coverage | Δ | asserted C / R | C precision | R precision | Δ |
|---|---|---|---|---|---|---|---|
| 20270602 | 0.4375 | 0.4821 | +0.0446 | 129 / 136 | 0.3798 | 0.3971 | +0.0173 |
| 20270603 | 0.4643 | 0.5893 | +0.1250 | 120 / 145 | 0.4333 | 0.4552 | +0.0219 |
| 20270604 | 0.4821 | 0.5268 | +0.0447 | 128 / 124 | 0.4219 | 0.4758 | +0.0539 |
| 20270605 | 0.6875 | 0.7768 | +0.0893 | 169 / 188 | 0.4556 | 0.4628 | +0.0072 |
| 20270606 | 0.6696 | 0.7054 | +0.0358 | 163 / 171 | 0.4601 | 0.4620 | +0.0019 |
| 20270607 | 0.7321 | 0.7589 | +0.0268 | 187 / 193 | 0.4385 | 0.4404 | +0.0019 |
| 20270608 | 0.5357 | 0.6339 | +0.0982 | 125 / 149 | 0.4800 | 0.4765 | -0.0035 |
| 20270609 | 0.5714 | 0.6250 | +0.0536 | 161 / 163 | 0.3975 | 0.4294 | +0.0319 |
| 20270610 | 0.3036 | 0.3125 | +0.0089 | 93 / 85 | 0.3656 | 0.4118 | +0.0462 |
| 20270611 | 0.4821 | 0.5893 | +0.1072 | 130 / 153 | 0.4154 | 0.4314 | +0.0160 |
| 20270612 | 0.5268 | 0.5446 | +0.0178 | 132 / 134 | 0.4470 | 0.4552 | +0.0082 |
| 20270613 | 0.3839 | 0.4375 | +0.0536 | 111 / 107 | 0.3874 | 0.4579 | +0.0705 |
| 20270614 | 0.5536 | 0.5714 | +0.0178 | 148 / 151 | 0.4189 | 0.4238 | +0.0049 |
| 20270615 | 0.6607 | 0.7232 | +0.0625 | 159 / 169 | 0.4654 | 0.4793 | +0.0139 |
| 20270616 | 0.6696 | 0.6696 | +0.0000 | 174 / 169 | 0.4310 | 0.4438 | +0.0128 |
| 20270617 | 0.4554 | 0.4911 | +0.0357 | 116 / 116 | 0.4397 | 0.4741 | +0.0344 |
| 20270618 | 0.7321 | 0.7857 | +0.0536 | 176 / 187 | 0.4659 | 0.4706 | +0.0047 |
| 20270619 | 0.7143 | 0.7411 | +0.0268 | 184 / 189 | 0.4348 | 0.4392 | +0.0044 |
| 20270620 | 0.6696 | 0.7768 | +0.1072 | 164 / 185 | 0.4573 | 0.4703 | +0.0130 |
| 20270621 | 0.5893 | 0.6339 | +0.0446 | 152 / 158 | 0.4342 | 0.4494 | +0.0152 |
| 20270622 | 0.5536 | 0.6339 | +0.0803 | 126 / 141 | 0.4921 | 0.5035 | +0.0114 |
| 20270623 | 0.4554 | 0.5446 | +0.0892 | 126 / 138 | 0.4048 | 0.4420 | +0.0372 |
| 20270624 | 0.6429 | 0.6875 | +0.0446 | 163 / 175 | 0.4417 | 0.4400 | -0.0017 |
| 20270625 | 0.4375 | 0.4732 | +0.0357 | 125 / 136 | 0.3920 | 0.3897 | -0.0023 |
| 20270626 | 0.6875 | 0.7054 | +0.0179 | 159 / 166 | 0.4843 | 0.4759 | -0.0084 |

**C0 — liveness: passes.** R's asserted set differs from C's at cap 20 on 25 of 25 seeds, and at caps 10
and 100 on 25 and 25; at cap 1,000 the two coincide on every seed **by construction**, because both
arms reach the full 240-row pool (coverage 1.0000 on 25/25 for C and 25/25 for R). The instrument is alive — the
failure mode that cost the development block seven cells would have shown identical digests at the small caps.

**C1 — the control is at chance: FAILS (18 of 25).** This is the finding. C's cap-20 precision is
below the frozen 0.4667 base rate on 22 of 25 seeds — median 0.4348, range 0.3656–0.4921 —
and 7 seeds sit outside the ±0.05 band, all on the low side. On these worlds the count-sorted rule is not
at chance; it is *worse* than chance, which is a different object from "at chance, therefore uninformative".

**C2 — tie broken: passes (24 of 25).** R takes 27–52 distinct score values
against 7–14 for C. The bar is 3× and the tightest margin is 2.83×, so
one seed misses it — reported rather than rounded up.

**C3 — the directional hypothesis: passes (24 of 25; one-sided exact sign test p = 7.7e-07).** Paired cap-20
coverage moves by 0.0000 to 0.1250 (median 0.0446), against the development block's 0.0536 to 0.0804.
The sign is the same everywhere it is not a tie; the median gain is smaller than in development.

**C4 — precision guard: passes.** The paired precision delta runs -0.0084 to 0.0705 (median 0.0128), falling
on 4 of 25 seeds and never by more than 0.0084 against the −0.05 floor. A size-matched point
is bracketed on 9 of 25 seeds (R's smallest asserted set already exceeds C's at cap 20 on the rest).
**Marginal precision, cap 20 to 1,000:** 0.4876 for C, 0.4673 for R — both reach the same full
pool, so this is a redistribution towards small caps, as in development.

**What this settles.** Two things, and neither is what the pre-registration hoped for. First, the *treatment
contrast reproduces*: on 25 seeds named nowhere else in this tree, the stored-ratio ordering beats the count
ordering's coverage on 24 of 25 seeds at the operating cap, at p = 7.7e-07, with no precision penalty. Second, the
*control's premise does not*: §8.4–§8.5 describe count-ranking as "at chance", and on these worlds it is below
chance on 22 of 25 seeds. The comparison between the two orderings is robust; the baseline the earlier record
described is seed-dependent, so the honest verdict is the registered one — **not comparable** — and the claim that
count is at chance must be restated as measured on 20261101–20261105 rather than as a property of the ranking.

**What it does not settle.** That `ratio` is the right criterion (one of six orderings, 1.47 SE above base in
the §8.5 screen; this block tests applying it, not choosing it). Nothing beyond this 2-tag world family or this
commit. And nothing about the engine: even a clean pass licenses a recorded decision, never a change to a frozen
primitive — and this was not a clean pass.

**Limits.** One world family, one engine build; the block was chosen by a scan, so "unseen" means unnamed in this
tree, not sampled from a population. C is the harness's rule rather than the engine's. C2's tightest margin is 2.83×.
The C1 failure has two readings that more data could separate — the control genuinely worsening on fresh worlds,
or a ±0.05 band around a population base rate that is too tight for 25 seeds — and this block cannot distinguish
them, so it reports the failure and not a mechanism. **§8.8** separates the two on 200 fresh seeds: the comparator is exact by construction, and the
band is the defect.
### 8.8 Why C1 failed: the constant is structural, the tolerance was not (2026-11-06)

**A diagnostic, not a confirmatory test.** This section tests no hypothesis, re-scores no criterion and changes
no verdict; it characterises the C1 failure recorded in §8.7. 200 seeds, 20270701–20270900 — scanned before the block ran across 6578 files, with every file this section touches excluded from the scan: `20270820` — a date (2027-08-20) in 11 files, none of them a seed list. One cell per seed, arm C at cap 20 only, through
`benchmarks/gate13_control_precision_sweep.py`, which imports `run_cell` from the registered arm instead of
reimplementing it; `PYTHONHASHSEED=0`. Artifact `docs/gate13_control_precision_sweep.json`.

**First, the comparator is exact — which settles one of §8.7's two readings.** `pool_diagnostics` reports 240
pool rows containing 112 world edges on every cell: base rate 0.4667 **by construction**, on all 200 seeds
(verified, not assumed: `comparator_check.constant` is true). So 0.4667 is not a rate estimated from the
development block's five seeds, and "the development block was a lucky draw on the baseline" is false. Equally,
it is not a sampled mean that a fresh block could drift away from — it is the pool's composition.

| statistic | value |
|---|---|
| seeds | 200 (20270701–20270900) |
| mean cap-20 precision | 0.4449 (95% CI 0.4397–0.4500) |
| median | 0.4503 |
| standard deviation | 0.0376 |
| range | 0.2929–0.5290 |
| interquartile range | 0.4254–0.4696 |
| below 0.4667 | 71.0% (mean offset -0.0218, t = -8.2) |
| within ±0.05 of 0.4667 | 81.5% |
| asserted-set size | 91–203, median 148 |
| pool top-20 density | median 0.2500, range 0.0000–0.5500 |

**Second, the control is mildly anti-selective, and consistently so.** Cap-20 asserted precision sits below the
base rate on 71.0% of 200 fresh worlds, by -0.0218 on average, at t = -8.2 — an offset
far too small to see in five seeds and far too systematic to be noise in 200. §8.4–§8.5 said the count
ranking is "at chance"; the honest restatement is *at chance or slightly below it*, and the anti-selection is a
property of the ordering that reproduces across 200 worlds rather than a property of the diagnostic block.

**Third, what actually fired was C1's tolerance.** A ±0.05 band around a structural constant covers 81.5% of
seeds when the statistic has sd 0.0376 and sits 0.0218 below that constant. On 25 seeds that predicts 20.4
inside the band (sd 1.94), so a bar of 21 has a **49.7%** chance of passing under a population identical to this
sweep's — a coin flip, fixed before any confirmatory seed was read. The block scored 18 (z -1.2; P(X ≤ 18) = 0.17), and
its mean precision 0.4338 sits at the 32.0th percentile of the sweep (z -0.30). The development block's mean 0.4536 sits
at the 54.5th percentile (z +0.23). Neither block is a different regime; the development block was never comfortably
inside its own band either — 4 of 5 is z +0.2 on this coverage.

**Verdict on §8.7's two readings: neither.** The control did not worsen on fresh worlds (its fresh-block mean is
-0.30 sd from the sweep's), and the baseline is not an artifact of the development block (it is exact on all
200 cells). What failed is the calibration of C1: a 0.0218 systematic shortfall against a statistic of
sd 0.0376, judged by a 21-of-25 bar that the band satisfies 49.7% of the time by construction. That is a defect in the
criterion, not in the control, and it is the kind of defect the §6 outcome table cannot detect — it read the
failure as "not comparable" when the data say "the test was under-powered by its own band".

**What this does not do.** It does not re-score C1: §8.7's `PARTIAL / NOT COMPARABLE` verdict stands exactly as the
frozen table returned it, and this section adds a characterisation beside it, per the rule that a protocol verdict
and a scientific characterisation are different artifacts. It says nothing about `ratio` — arm C only. It cannot
separate "count ordering is anti-selective" from "the asserted set is a different size from the pool draw" (the
asserted set is 91–203 rows against a 240-row pool), and the 81.5% coverage is estimated from the same sweep, so
the binomial view is descriptive rather than a pre-registered power statement. One world family, one build, 300
cycles, cap 20.

### 8.9 C1 re-specified with its power computed in advance (2026-11-06)

§8.8 showed that C1's band was miscalibrated: at 81.5% per-seed coverage, a 21-of-25 bar passes 49.7% of the time on a
population that matches the reference. Amendment 1 to the pre-registration
([§13](GATE13-RATIO-CONFIRMATORY-PREREGISTRATION.md)) replaces it **prospectively** with an equivalence test on the block
mean: pass iff m̄, the mean cap-20 control precision over the block's 25 seeds, lies within δ = 0.032 of the structural
comparator 0.4667 — that is, m̄ ∈ [0.4347, 0.4987]. δ is the smallest 0.001-grid value at which 90.8% of 20,000 bootstrap
25-seed blocks from the 200-seed sweep satisfy the band (closed form 0.0315); fail-low and fail-high are separate outcomes
and both mean not comparable.

| shift in the control's true mean | P(C1′ passes) |
|---|---|
| +0.000 | 0.908 |
| -0.005 | 0.761 |
| -0.010 | 0.527 |
| -0.015 | 0.269 |
| -0.022 | 0.052 |
| -0.032 | 0.001 |
| -0.050 | 0.000 |
| +0.020 | 1.000 |

The criterion is calibrated against the reference population rather than against a hope: it now fails 9.2% of matching
blocks instead of half of them. It also has a stated cost — the margin absorbs a further 0.0102 of systematic shortfall
(1.4 se), and the pass rate falls below half at a shift of -0.011 — and a stated blind spot, the mean only, with
0.0% of in-band calibration blocks showing a within-block sd above
0.0753. Margin fragility under resampling of the calibration data: 0.0269–0.0367.
Derivation `docs/gate13_c1_respecification.json`; `benchmarks/derive_c1_respecification.py`. It is not applied to
20270602–20270626 — §8.7's verdict stands — and §8.8's characterisation is unchanged by it.

### 8.10 Block 2: the first comparable block, and the treatment does not reproduce (2026-11-06)

Pre-registration [`docs/GATE13-RATIO-BLOCK2-PREREGISTRATION.md`](GATE13-RATIO-BLOCK2-PREREGISTRATION.md), frozen before the
first cell on seeds 20270901-20270925 (scanned: zero occurrences across the tree), 275 cells, C1′ as the comparability
test with δ = 0.032 read from the calibration artifact. Artifact `docs/gate13_ratio_block2.json`.

**Verdict: TREATMENT NOT REPRODUCED.** C0, C1′ and C2 pass; C3 fails; C4 passes on its thresholds.

| id | result | detail |
|---|---|---|
| C0 | pass | digests differ 25/25 at cap 20, 25 and 25 at caps 10 and 100 |
| C1′ | pass | mean C precision 0.4530 (-0.0137 from base), band [0.4347, 0.4987] |
| C2 | pass | 22/25 at ≥ 3×, tightest 2.73× |
| C3 | **fail** | 20/25, p = 0.002, median Δ +0.0535 |
| C4 | pass | median Δ +0.0003, worst -0.0292, 12 falling |

**The first comparable block in the record.** C1′ passes here, so the control behaves like the calibrated population
(§8.8, Amendment 1 §13 of block 1's pre-registration) and the treatment comparison is interpretable for the first time.
On that comparison, C3 returns 20 of 25 positive seeds against a bar of 21: 5 seeds did not improve
(20270901 (Δ +0.0000); 20270905 (Δ -0.0089); 20270908 (Δ -0.0179); 20270913 (Δ +0.0000); 20270921 (Δ -0.0446)). The median gain is +0.0535, slightly *larger* than block 1's +0.0446, while the count of
improved seeds falls from 24 to 20 — the effect has become less reliable, not absent. C2 still passes, so the
discriminator exists; what fails is the consistency of its benefit. C4 passes its thresholds but its median has gone to
+0.0003 from +0.0128, with 12 of 25 seeds losing precision: the coverage the rule buys at cap 20 is now
bought at essentially no precision change on the median and a visible cost on the worst seeds (-0.0292).

**Replication, stated plainly.** Block 1: 24/25, p = 7.7e-07, median +0.0446, precision median +0.0128. Block 2: 20/25,
p = 0.002, median +0.0535, precision median +0.0003. The pre-registered replication bar was missed by
one seed. That is reported as a miss — the criterion was evaluated once, by code, and is not re-read as a near-pass; the
nominal p-value is recorded beside the verdict, not substituted for it.

**Disclosed, not scored.** Cap-1,000 coverage is 1.0000 on 21/25 seeds for C and 21/25 for R; the remainder
fall short of the full pool (20270901 (C 0.9911, R 0.9911); 20270903 (C 0.9911, R 0.9911); 20270907 (C 0.9911, R 0.9911); 20270920 (C 0.9911, R 0.9911)). No criterion reads cap 1,000 and the cap-20 criteria are unaffected.

**What this settles.** On a fresh, comparable allocation, the admission-rule hypothesis as pre-registered is **not
supported**: the stored ratio still breaks ties and still gains coverage on most seeds, but not on enough of them to clear
the bar it was given in advance. Combined with block 1 — where the treatment passed and the control criterion was
miscalibrated — the honest summary is a small, directionally consistent, unreliable benefit, not an admission bottleneck.

**What it does not settle.** Other world families and caps (the open question a single family cannot answer), the other five
orderings, and whether the mechanism is tie-breaking or the candidate space. C2 passing says the discriminator exists, so
the next question is why its benefit varies this much across seeds — not whether it is present.

### 8.11 Why the benefit varies: an exploratory look at the 20/5 split (2026-11-06)

Diagnostic only. `benchmarks/diagnose_ratio_seed_split.py` pairs the cap-20 pool diagnostics already stored in both block
artifacts against the paired coverage delta, and asks whether block 2's 20 improving and 5 non-improving seeds differ on
any property of the candidate pool. Artifact `docs/gate13_ratio_seed_split.json`. **This is not a test and it re-scores
nothing:** the two groups are defined by the outcome they are compared on, the failure group has 5 members, and no
criterion here was pre-registered.

**The dispersion is real.** Block 1: 24 positive, 1 zero, 0 negative, sd
0.0339, mean 0.0529, median 0.0446. Block 2: 20 positive, 2
zero, 3 negative, sd 0.0381, mean 0.0389, median 0.0535, range
-0.0446 to 0.1339. The median rose while the mean fell: the treatment still produces its typical gain
(the median is larger than block 1's) but produces it on fewer seeds, and now loses ground on some.

**Pool structure does not separate them.** On the count tie block (201 rows
against 202, permutation p = 0.9016), on the number
of distinct ratio values (41 against 44, p =
0.9674), on the ratio-to-count distinct-value ratio (3.42
against 3.64, p = 0.4518) and on cap-20 control
precision (0.4625 against 0.4357, p =
0.3582) the two groups are indistinguishable. The one variable that separates at conventional levels,
the size of the ratio arm's asserted set (160 against
121, p = 0.0333), is downstream of the outcome rather than a
property of the pool: the arm asserts more rows when its ordering finds more to assert. It cannot be read as a cause.

**The ranking improves; the improvement does not convert.** Top-20 world-edge density uplift does differ — medians
0.25 against 0.10, mean difference
0.0975, permutation p = 0.0558 — and across both blocks it correlates with
the coverage delta: pooled r = 0.362 (0.052 to
0.618, n = 50, r² = 0.131), block 1 r =
0.349 (0.040 to 0.610) and block 2
r = 0.297 (-0.236 to 0.728). The
correlation is weak, it explains about 13 percent of the variance, and block 2's
interval contains zero. And the failing seeds are not seeds where the ordering failed: their uplift is 0.20, 0.30, 0.05, 0.10, 0.00 —
2 of the five at or above 0.20, including 20270905, whose delta is -0.0089 despite the group's
largest uplift. The largest loss, 20270921 at -0.0446, had no uplift at all. Nor is the comparison
lost on a degraded control: the failure group's cap-20 precision (median 0.4357) is not below
the improving group's (0.4625).

**What this supports, and what it does not.** It does not support candidate-pool structure — tie-block size, distinct-value
count, ratio diversity — as the moderator of the treatment's benefit; on this evidence those are the wrong variables. What
it does support is narrower: the ratio ordering reliably finds a denser top-20, that density carries a small amount of
information about the eventual coverage gain, and the conversion from the one to the other is not determined by it. The
remaining candidates are dynamic — the order in which the cap is spent relative to which edges become assertable, and what
a seed's assertion path does with a denser top-20 — and none of them is measured here. Testing any of them needs a fresh
allocation, a pre-registered moderator and a bar fixed before the cells are run. The 20/5 split can generate that
hypothesis; it cannot adjudicate it.

### 8.12 How the failing seeds spent the cap: a verified replay (2026-11-06)

Exploratory follow-up to §8.11. The block-2 artifact stores aggregates only, and the `top_k` density recorded there is
measured on the *final* pool — after the treatment has acted. `benchmarks/diagnose_assertion_path.py` therefore replays
the cap-20 cells for the five non-improving seeds and five improving seeds matched on recorded top-20 uplift, records
every per-cycle admission window, and accepts a replay only if its asserted set, covered count and SHA-1 digest equal
the stored cell's. **All 20 replays matched** (`replay_mismatches` is empty), so the traces are the cells that
were scored. Artifact `docs/gate13_assertion_path.json`.

**The window is 20 rows and the arms spend it in opposite ways.** Over 107-109 cycles with admissions, the
count arm makes 443.4 world-edge admissions spread across 76-87
distinct edges; the ratio arm makes 767.4 admissions concentrated into 26-41
distinct edges. Per cycle the ratio window is about 1.7× as often a world edge, but it reaches roughly a third as many
distinct edges — the treatment trades exploration for repetition, about 4.2× per edge. That concentration is the
admission-side content of the ratio rule.

**The failing seeds did not spend the cap worse.** Non-improving against matched improving: ratio-window admissions
802.4 against 732.4, distinct window edges 30.6
against 33.8, asserted rows 123.0 against 151.2. The failing
seeds' windows assert world edges slightly more often and end with fewer distinct covered edges
(55.2 against 70.6). On this trace there is no admission-side difference between the two
groups: whatever separates them is not how the cap is spent.

**And the window does not account for the coverage.** In all 10 of 10 ratio cells
the final covered count exceeds the number of distinct world edges its windows ever touched (62.9 covered
against 26-41 window-touched), with 41.3 covered edges per
seed appearing in no window at all; for the count arm that happens in 1 of 10
cells (60.2 covered, 12.4 outside any window). `structure_edges` aggregates all six
structure types from the stored candidate snapshots and the prediction window touches only some of them, so a
window-level trace cannot attribute the ratio arm's coverage. That is a resolution boundary, not a mechanism: an
event-level claim would need a store-time observer at the structure level, which this harness does not have
(AGENTS rule 17(d)).

**What this changes.** §8.11 left the question at "the conversion from a denser top-20 to coverage is not determined by
the pool". This replay narrows it again: the conversion is not determined by the admission window either — the failing
and improving seeds admit at the same rate, the same window size, with the failing ones repeating world edges slightly
more and still ending with fewer distinct covered edges. The variation therefore sits downstream of admission, in how
repeated assertions of the same structures are consolidated into the other structure types, and that is what the next
instrument needs to observe. It is not a reason to change the cap, and it changes no verdict.

### 8.13 What carries the coverage: loop candidates, and prediction candidates that add or duplicate (2026-11-06)

Exploratory follow-up to §8.12. `benchmarks/diagnose_structure_provenance.py` wraps `MemoryService.store` and captures
every `event_type="sleep"` payload as it is written — the same candidate rows `structure_edges` aggregates — then
reconstructs the live set the way `_load_prior_candidates` does (newest generation per key, death records dropped), and
attributes each covered world edge to the structure type(s) asserting it. Fidelity is enforced three ways, and a cell is
not read unless all three hold: the replay reproduces the stored asserted set, covered count and digest; the
reconstructed edge set equals `structure_edges` on the database's own candidate list; and every per-edge weight agrees.
**All 20 cells pass all three** (`verification_failures` is empty). Artifact `docs/gate13_structure_provenance.json`.

**Two of the eight branches carry the coverage.** `loop_candidate` accounts for 27-89 covered
world edges per seed and `prediction_candidate` for 3-16; every other branch contributes at
most 1 edge in any cell. (`structure_edges` documents "six structure types"; the code has eight branches —
`concept_candidate` and `phrase_candidate` share one. This is a wording defect in the docstring, recorded here and not
changed in the frozen readout.)

**The loop component is arm-invariant.** Loop attribution is identical in both arms on all 10 seeds — maximum
difference 0 edges. Loops are built from the stream and are not what the cap ranks, so this is the internal
consistency check one wants: the two arms differ only in which predictions are admitted.

**The treatment is entirely temporal, and the split is redundancy.** The ratio arm raises prediction attribution in both
groups — 6.2 to 11.8 in the failing seeds,
8.2 to 13.6 in the matched improving ones. What differs is
whether those edges are already in the loop structure: covered edges asserted by both a loop and a prediction rise
1.4 to 8.8 in the failing group and **fall** 5.2 to
3.6 in the improving group, giving 56.8 to 55.2 against
63.6 to 70.6. The three clearest cases: 20270901 goes from
7 prediction edges with 0 overlap to
13 with 6, and coverage is unchanged at
34; 20270921 goes from 9 to
15 with overlap 2 to 13, and loses
63 to 58; 20270906 goes from
9 to 16 while overlap drops
9 to 1, and gains 62 to 77.

**This closes §8.12's boundary.** The coverage that appeared outside any admission window is loop coverage, and loops are
not the object the cap ranks. The cap ranks prediction candidates; the readout counts both. So the honest statement of
the mechanism is: the ratio rule does not touch the loop structure at all, it changes which temporal edges are asserted,
and that change is worth something only where those edges are not already present in the loops.

**Limits.** This is the composition of the final asserted set at the readout's own resolution, not a time order: an edge
asserted by both a loop and a prediction is double-attributed in the final structure, and this measurement cannot say
which came first. The groups are the same 5-versus-5 split as §8.11-§8.12, defined by the outcome, with no pre-registered
criterion; nothing here re-scores a verdict.

## 8.14 Block 3: loop redundancy as a moderator, on a fresh allocation

The 20/5 split survived §8.11-§8.13's three structural explanations, so block 3 tested the strongest remaining one on
seeds that had never been used: that the arm pays only where the pre-run loops leave room. 200 cells, seeds
20271101-20271200, C and R at cap 20, pre-registered with its bars, threshold (0.509), power and
decision table fixed before the first cell (`docs/GATE13-RATIO-REDUNDANCY-PREREGISTRATION.md`), and scored once.

Gates held: 100/100 seeds had arm-dependent asserted sets, mean control precision
0.4444 sat inside the C1′ band [0.4347, 0.4987], and the loop edge sets were
identical across arms on 100/100 seeds, so the covariate is arm-independent as designed.

| Criterion | Reading | Bar | Pass |
| --- | --- | --- | --- |
| M1 half-split | low `r` (n=31) 0.0357 vs high (n=69) 0.0536; difference -0.0179 | ≥ +0.03 | no |
| M2 monotone | Spearman -0.02, CI [-0.243, 0.185] | ≤ -0.25 | no |
| M3 replication | 88/100 positive | ≥ 66 | yes |

**Verdict: MODERATOR NOT SUPPORTED.** The gain itself is now a three-block fact: 88/100 fresh seeds improve, mean
0.0442 coverage. Its moderator is not. Where pre-run loops cover more of the world the arm does slightly
*worse* (0.0536 vs 0.0357), and the rank correlation is -0.02 — the registered
threshold of -0.25 is outside the interval, not merely unattained. Since §8 fixed joint power at 0.327 for a
mechanism-sized effect, a miss is evidence against that mechanism, and the redundancy explanation is retired.

**Limits.** Only 31 seeds fall below the fixed threshold, because `r` in this allocation sits higher than in
calibration (0.2054-0.8214), so M1 is additionally undersized on its low half; the sign is wrong
either way. The covariate was measured on the control arm before the ratio arm was scored, but both arms share the seed's
world, so this tests redundancy as a *predictor*, not as an intervention. Nothing here revises §8.11-§8.13 or the earlier
verdicts.

## 8.15 Block 4: control-side temporal redundancy, voided by its own measurability gate

Block 3 retired loop *quantity*. Block 4 tested the other half of §8.13 — whether the seeds that improve are the ones where
the control's temporal edges are already largely implied by its loops (`o_s = |L ∩ P ∩ W| / |P ∩ W|`, threshold
0.3095 from the 10 calibration seeds). 200 cells on fresh seeds 20271202-20271301, pre-registered and scored once.

**Verdict: VOID / NOT COMPARABLE.** G0 (100/100 arm-dependent sets) and G1 (control precision
0.4465 in band) passed. G2 failed at 87/100 measurable against a required
96: the covariate's denominator, |P_s ∩ W|, fell below 3 on 13 control cells, so `o_s` was not measurable there; those seeds are excluded and counted, never imputed. No criterion is read.

**The covariate is the finding here.** On the fresh allocation the control's temporal world edges are few — 0-11 where
calibration gave 3-12 — so the share is undefined on 13 seeds and saturated on the rest (0.7191 mean, 78 of
87 above threshold). The design error is visible before any criterion: a share whose denominator can be
absent produces a covariate that is both unmeasurable and compressed. Excluding those seeds, as the freeze required, left too
few to test the registered split, and the gate fired rather than the block being quietly analysed on a skewed subset.

**Disclosed, not scored.** On the measurable seeds the association is positive — Spearman 0.389, CI [0.192, 0.551] — and the
gain replicates at 81/87 with mean 0.0494. That is the direction the hypothesis predicted
and it is **not** a result of this block: the gate voided it, and reporting those numbers as support would be the
re-scoring §7 forbids. They are recorded so the next covariate can be specified against a measured denominator.

**Limits.** Nothing here speaks to the moderator hypothesis. What it does say is that §8.13's overlap pattern cannot be
turned into a between-seed covariate of this form without solving the denominator first — by using a count rather than a
share, or by taking the overlap over asserted edges rather than world edges.

## 8.16 Block 5: the block-4 covariate with its floor and cut repaired

Block 4's covariate was sound and its specification was not. Block 5 keeps `o_s = |L ∩ P ∩ W| / |P ∩ W|`, lowers the
measurability floor from 3 to 1 — a share with denominator 1 is coarse, not undefined — and chooses the cut by a stated
balance rule over 110 non-judged cells (the 10 block-2 and 100 block-4 cells) instead of the median of ten. Cut 0.75,
which splits the calibration cells 53/56. 200 cells on fresh seeds 20271403-20271502, pre-registered with a fourth gate,
G3, that requires 40 seeds in each half: block 4's imbalance was invisible to G2 alone.

| Gate | Reading | Pass |
| --- | --- | --- |
| G0 liveness | 100/100 seeds with arm-dependent asserted sets | yes |
| G1 C1′ | mean control precision 0.4467 in [0.4347, 0.4987] | yes |
| G2 measurability | 99/100 seeds with `o_s` defined at floor 1 (required 96) | yes |
| G3 split liveness | 42 low / 57 high at `o*` = 0.75 (each ≥ 40) | yes |

**Verdict: DIRECTIONAL ONLY.** All four gates pass. **M1 half-split** fails: median gain 0.0357 low against 0.0625 high, a difference of +0.0268 against the 0.03 bar, on 42 low and 57 high seeds. **M2 association** passes: Spearman 0.407, 95% CI [0.219, 0.576], against the 0.25 bar. **M3 replication** passes as the secondary criterion: 88/99 seeds positive, 66 required.

The association replicates at the bar, so the direction of §8.13's pattern survives out of sample. The half-split contrast does not clear its bar, which is what the pre-registered power table said to expect: M1 has 0.283 power at the calibrated effect because the calibrated gap sits below 0.03. **A failed M1 here is therefore not evidence against the hypothesis** — it is the registered expectation — while the passing M2 is evidence for the association.

**What the repair established.** The denominator defect is fixed and the gate now measures what it was meant to measure:
`o_s` is defined on 99 of 100 seeds at floor 1, against 87 of 100 at floor 3. The count
covariate that §8.15 suggested instead was calibrated first and rejected before freezing — it is always defined but its
association is 0.241 on 110 cells with an expected half-split gap of 0.015, so it would have produced a null without
testing anything. Both calibrations are in `docs/gate13_temporal_redundancy_b5_calibration.json`, including the rejected
candidate, so the choice is auditable rather than asserted.

**Limit, stated in advance and now on the record.** M1's bar is fixed at 0.03 for comparability across blocks 2–5, and the
calibrated half-split gap is 0.0258 — below it. M1 therefore has 0.283
power at the calibrated effect, and §8 publishes that asymmetry before the run rather than after a miss. No third
between-seed proxy will fix it: at this effect size, raising n approaches a 50% ceiling rather than power.

## 8.17 Block 6: the loop-free preference arm (intervention, not moderator)

Blocks 3–5 tried to predict *which seeds* benefit from ratio admission. Block 6 instead changes the rule: arm Y admits
exactly R's candidates under R's cap, except that a candidate whose edge a loop candidate asserts that cycle sorts
after one that no loop asserts. 300 cells, seeds 20271614-20271713, arms C, R and Y at cap 20.

The arm was calibrated twice before freezing, and the second calibration is the load-bearing one: reordering (X) and
reserving the cap (Y) selected identical candidates on every cycle of all ten calibration seeds, because the candidate
pool always holds at least 20 non-loop edges. The preference is therefore at maximum dose on this world family, and the
block registered one intervention arm rather than a dose ladder.

| Gate | Reading | Pass |
| --- | --- | --- |
| G0 liveness, Y vs R | 62/100 seeds with different asserted sets | NO |
| G0b liveness, C vs R | 100/100 seeds with different asserted sets | yes |
| G1 comparability (C1′) | mean control precision 0.4441 in [0.4347, 0.4987] | yes |
| G2 perturbation | 100/100 seeds with at least one edge displaced (required 96) | yes |

**Verdict: VOID / NOT COMPARABLE.** Gate G0 failed: Y and R asserted the same set on 38 seeds, so the intervention did not reach the final structure often enough to compare. Per §6 the gate is reported and **no criterion is read**; the scorer's numbers are in the artifact and are descriptive only. **The gate's bar was not achievable on this distribution, and that is a defect of this block's specification rather than evidence about the arm.** Calibration measured Y-vs-R liveness at 6 of 10 seeds and G0 required 96 of 100, so the same class of error block 4 made -- a threshold the calibrated distribution cannot reach -- was written into a new gate with the calibration number printed beside it. The numbers below are descriptive only and read no criterion: M1's mean 0.0095 sits below its 0.01 bar, so the block would not have passed M1 either, and M2's pass is a mechanism check on data the gate voided.

**The criterion was chosen in calibration, and the choice is disclosed.** The per-seed effect is zero on half the
calibration seeds and 0.027–0.063 on the rest, so a median criterion would have reported the zeros as the result and a
sign criterion had about 3% power at 100 seeds. The primary criterion is the paired mean difference, with its bar fixed
at 0.01 — one fifth of the R-over-C gain the intervention is meant to add to — and at the calibrated effect the bar sat
2.46 standard errors below the mean, giving 0.997 power. That is the opposite of block 5's
asymmetry, and it is the reason this block could test the intervention at all.

**Limits.** The mean is tail-sensitive: 5 of 10 calibration seeds carried
the whole effect, and the ten-seed sd is uncertain. The readout is blocks 2–5's end-of-acquisition asserted structure,
which accumulates ninety cycles; an effect measured on the admitted set each cycle would be a different, separately
calibrated block. And the arm removes prediction candidates whose edges loops assert — it does not modify loops, does not
remove them from the readout, and so cannot speak to what loops are for.

## 8.18 Block 7: the same arm with a gate that can fire

Block 6's void was arithmetic, not evidence: G0 required the arm to change 96 of 100 final asserted sets while the
calibration printed beside that bar measured 6 of 10. Block 7 keeps everything — arm Y, world, cap 20, readout, C1′
band, G2, M1's 0.01 bar, M2's mechanism check — and sets G0 to 50/100, calibrated to the pooled liveness rate
0.6182 from 110 non-judged pairs (block 6's void cells plus the ten dose seeds). Under that rate G0
passes with probability 0.9939; under block 6's bar it would have passed with probability
0.0. 300 cells, seeds 20271715-20271814.

| Gate | Reading | Pass |
| --- | --- | --- |
| G0 liveness, Y vs R | 72/100 seeds with different asserted sets (bar 50) | yes |
| G0b liveness, C vs R | 100/100 seeds with different asserted sets (bar 96) | yes |
| G1 comparability (C1′) | mean control precision 0.4427 in [0.4347, 0.4987] | yes |
| G2 perturbation | 100/100 seeds with an edge displaced (bar 96) | yes |

**Verdict: INTERVENTION SUPPORTED.** All four gates pass. **M1** passes: mean Y − R coverage 0.0127, 95% interval [0.0092, 0.01652], against the 0.01 bar (median 0.0089, 53/100 seeds positive). **M2** passes: novel covered edges +1.4 on average (interval [0.98, 1.8], bar 0.005), loop-covered change +0.05.

The admission budget's redundancy is a **cost** at this cap and readout, now measured on a fresh allocation with a gate that could fire. The gain sits where the arm claims -- novel edges with loop-covered coverage unchanged. It licenses an admission-rule change; it does not say what loops are for, because the arm removes prediction candidates whose edges loops assert and leaves the loops themselves untouched.

**Power, stated before the run and not repaired afterwards.** The pooled calibration mean was 0.0100,
below the unchanged 0.01 bar, so M1 was a coin flip at best and the pre-registration said a miss would not be evidence
against the intervention. That disclosure is why a miss here is reported as the end of this readout rather than as a
negative result, and why the bar was not lowered after block 6's miss.

**Limits.** The pooled sd comes mostly from block 6's void cells, which is a single 110-pair draw. The readout remains
the ninety-cycle accumulation, on which the intervention changes the final structure on only about three seeds in five;
an endpoint that scored the admitted set each cycle would be more sensitive and is a separate, separately calibrated
block. And the arm removes prediction candidates whose edges loops assert — loops, construction and thresholds are
untouched, so nothing here speaks to what loops are for.

## 8.19 Block 8 — cap scaling (2026-11-06)

Block 7 measured the loop-free admission arm's gain at cap 20. Block 8 asks whether that gain scales with the budget:
arms R and Y at caps **40** and **100**, 100 fresh seeds (20271826-20271925), 400 cells.
DiD(seed) = (Y − R at cap 100) − (Y − R at cap 40), paired within seed.

| Gate | Reading | Pass |
| --- | --- | --- |
| G0 liveness, both caps | 86/100 and 100/100 (bar 50) | yes |
| G1 perturbation, both caps | 100/100 and 100/100 (bar 96) | yes |
| G2 axis live | R lift 0.0942 (0.0867, 0.1023) | yes |

Gain at cap 40: 0.0179; at cap 100: 0.0420. M1 (mean DiD ≥
0.01) passes at 0.0240 (0.0196,
0.0285); M2 (positive at both) passes.

**Verdict: SCALING SUPPORTED.** The gain grows with the budget and is positive at both caps: the mechanism the arm claims -- spending admission slots on edges loops do not already assert -- is the one that produces the effect, because the effect grows when the pool of redundant edges does.

The launcher also ran arm C, which this design excludes; those cells are unregistered, unjudged and kept in `.scratch/loop_free_cap_unregistered_C.jsonl`.

Artifacts: `docs/GATE13-LOOP-FREE-CAP-SCALING-PREREGISTRATION.md`, `docs/gate13_loop_free_cap.json`,
`docs/gate13_loop_free_cap_calibration.json`, `benchmarks/score_loop_free_cap.py`.
