# Phase L — V1 primary axis: the raise-n result (n = 30)

**Run date:** 2026-10-25 · **Arm:** V1 (primary axis) · **Cells:** 240 of 240, complete
**Verdict by the four pre-committed criteria: `H3-L — INCONCLUSIVE`.**
**Protocol remedy for this outcome: raise n; conclude nothing. No outcome here authorises a V2.**

> **This document is the measurement record.** The published *characterization*
> — what the measurement means, in the owner's reading — is
> **[`docs/PHASE-L-SYNTHESIS.md`](PHASE-L-SYNTHESIS.md)**. The two are kept
> separate on purpose: the verdict is what the protocol produced, and the
> characterization is what the shape turned out to be. Neither re-scores the
> other.

This is the **raise-n** run: the protocol's own remedy for the n=10 result,
taken on the primary axis with the same sweep, the same criteria and no
edits (Amendment 3, committed **before** the run existed).

Protocol: [`docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md`](PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md)
(frozen; Amendments 1, 2 and 3 — all applied before any raise-n outcome existed).

| | n = 10 (first run) | n = 30 (raise-n, this run) |
|---|---|---|
| Cells | 80 | **240** (the 80 reused, not recomputed; 160 added) |
| Seeds per point | 10 | **30** (20261023–20261052) |
| Verdict | `H3-L — INCONCLUSIVE` | `H3-L — INCONCLUSIVE` |
| Criterion 1 (DI monotone) | **met** | **not met** |
| Criterion 2 (PI monotone) | not met | not met |
| Criterion 3 (DI range ≥ 0.25, crossing interior) | met | met |
| Criterion 4 (RT interval excludes endpoints) | met | met |

---

## 1. Run provenance

| Field | Value |
|---|---|
| Arm | V1 only (primary axis) |
| Sweep points | 8 — 1:4, 1:3, 1:2, 1:1, 2:1, 3:1, 4:1, 6:1 |
| Seeds | 30 per point (20261023 – 20261052) |
| Cells | 240, all complete |
| Workers | 12 |
| `PYTHONHASHSEED` | `0` — **pinned as required** (recorded as the actual value) |
| Bootstrap replicates | 10,000, paired across seeds **by seed** |
| Decision interval | **99.00%** (alpha 0.01) |
| Wall clock | 12,738.1 s |
| Engine | Organica 1, frozen at tag `v0.9.0` (verified unchanged by `tests/test_v1_freeze.py`, 16/16) |

**The reuse was verified:** all 80 original cells are present in the n=30 file
and **byte-identical** to the n=10 record; each sweep point has exactly 30
cells with 30 distinct seeds.

**Instrument audits — all four pass:** discrimination control, ceiling check,
degeneracy audit (every cell with a full denominator), V4 pressure audit
(peak beliefs 11 → 15, the cap binds). **Unmeasurable cells: 0.**

Artifacts: `docs/phase_l_results.json` (canonical, n=30),
`docs/phase_l_results.ndjson` (live recording), and
`docs/phase_l_results_n10.json` / `.ndjson` (the n=10 record, preserved
unmodified).

---

## 2. The curve

| Label | DI (sd) | PI (sd) | DS | Revision latency | Seeds reaching DI > 0.5 |
|---|---|---|---|---|---|
| 1:4 | 0.000 (0.000) | 0.743 (0.101) | −0.743 | — | 0/30 |
| 1:3 | 0.000 (0.000) | 0.754 (0.079) | −0.754 | — | 0/30 |
| 1:2 | 0.000 (0.000) | 0.748 (0.091) | −0.748 | — | 0/30 |
| 1:1 | 0.000 (0.000) | 0.717 (0.064) | −0.717 | — | 0/30 |
| 2:1 | 0.204 (0.119) | 0.606 (0.090) | −0.402 | — | 0/30 |
| 3:1 | 0.706 (0.059) | 0.039 (0.044) | +0.667 | 356 | 30/30 |
| 4:1 | 0.722 (0.076) | 0.000 (0.000) | +0.722 | 291 | 30/30 |
| 6:1 | 0.715 (0.048) | 0.000 (0.000) | +0.715 | 244 | 30/30 |

**The shape is a step function, not a ramp.** Three plateaus and two
transitions:

- **DI = 0.000 exactly** at 1:4, 1:3, 1:2 and 1:1 — for all 30 seeds. The late
  structure is never incorporated at these ratios.
- **DI ≈ 0.71** at 3:1, 4:1 and 6:1 — saturation, with the early structure
  entirely gone (PI = 0.000).
- **PI ≈ 0.74** at 1:4, 1:3 and 1:2, easing to 0.717 at 1:1.
- Two sharp transitions: 1:1 → 2:1 and 2:1 → 3:1.

Revision latency (co-primary report, not a criterion): **0/30** seeds reach
DI > 0.5 at 1:4 through 2:1, and **30/30** at 3:1 (**mean 356 cycles, median
351**), 291 at 4:1 (median 286), 244 at 6:1 (median 240). The transition is
abrupt, not gradual.

---

## 3. The four pre-committed criteria

| # | Criterion | n = 10 | n = 30 | Evidence at n = 30 |
|---|---|---|---|---|
| 1 | **DI monotone increasing** | met | **NOT MET** | DI dips at the top: 4:1 0.722 → 6:1 0.715, a step of −0.007 [−0.037, +0.022] |
| 2 | **PI monotone decreasing** | not met | **NOT MET** | PI rises at the bottom: 1:4 0.743 → 1:3 0.754, a step of +0.011 [−0.026, +0.044] |
| 3 | **DI range ≥ 0.25 and the crossing is interior** | met | met | range 0.722; crossing at **3:1**, interior |
| 4 | **The RT interval excludes both endpoints** | met | met | **[5.0, 5.0]**, 10,000 / 10,000 replicates found a crossing |

**Criterion 1 flipped.** It was met at n=10 and is not met at n=30 — because
the top of the curve has a −0.007 step whose 99% interval contains zero.

**Terminal outcome:** `H3-L — INCONCLUSIVE`, unchanged. The remedy is *raise
n; conclude nothing*, and no Phase L outcome authorises a V2. The secondary
arms V2–V5 were **not** run.

---

## 4. The Revision Threshold

| Quantity | n = 10 | n = 30 |
|---|---|---|
| Crossing label | 3:1 | **3:1** |
| Sweep position | 5 of 7 interior | 5 of 7 interior |
| Paired-bootstrap interval (99%) | [5.0, 5.0] | **[5.0, 5.0]** |
| Replicates that found a crossing | 10,000 / 10,000 | **10,000 / 10,000** |
| Robustness — 8 alternative bootstrap seeds | INTERIOR (8/8) | **INTERIOR (8/8)** |
| Leave-one-seed-out crossings | 3:1 in 10 of 10 | **3:1 in 30 of 30** |

The crossing location is the most stable quantity in the phase. It did not
move when n tripled, and dropping any single seed leaves it at 3:1.

---

## 5. The adjacent-difference diagnostic (Amendment 3)

The monotone criteria are evaluated on the **mean** curve, so each is a
statement about the **sign** of an adjacent difference. This diagnostic
reports the paired difference for each adjacent pair with a 99% paired
bootstrap interval. **It is a diagnostic**: not a metric, not a criterion, in
no verdict, never averaged.

| Step | dDI (99% paired interval) | dPI (99% paired interval) |
|---|---|---|
| 1:4 → 1:3 | +0.000 [+0.000, +0.000] | **+0.011 [−0.026, +0.044]** |
| 1:3 → 1:2 | +0.000 [+0.000, +0.000] | **−0.006 [−0.046, +0.033]** |
| 1:2 → 1:1 | +0.000 [+0.000, +0.000] | **−0.031 [−0.078, +0.015]** |
| 1:1 → 2:1 | **+0.204 [+0.148, +0.261]** | **−0.111 [−0.157, −0.065]** |
| 2:1 → 3:1 | **+0.502 [+0.443, +0.559]** | **−0.567 [−0.619, −0.522]** |
| 3:1 → 4:1 | +0.017 [−0.022, +0.056] | **−0.039 [−0.059, −0.020]** |
| 4:1 → 6:1 | **−0.007 [−0.037, +0.022]** | +0.000 [+0.000, +0.000] |

**Both failing steps have intervals that contain zero.** Every step whose
interval excludes zero is a real transition; every step whose interval
contains zero is a plateau edge. The criterion failures are signs of zero
differences.

---

## 6. How stable are the criteria themselves?

*This analysis was run **after** the n=30 outcome was known. It is a
characterization of what the verdict means. It changes no criterion, no
verdict and no prediction — the verdict stands as `H3-L — INCONCLUSIVE`.*

Resampling the 30 measured seeds and recomputing the four criteria:

| Criterion | random 10-seed subsets | random 20-seed subsets | n = 30 |
|---|---|---|---|
| 1. DI monotone increasing | 19.3% | 16.1% | 0% |
| 2. PI monotone decreasing | 12.0% | 6.6% | 0% |
| 3. DI range ≥ 0.25 | **100.0%** | **100.0%** | met |
| 3b. Crossing interior to the sweep | **100.0%** | **100.0%** | met |
| **All four together** | **2.9%** | **1.2%** | 0% |

**Criteria 3 and 3b are properties of the system.** They hold in every
resample. **Criteria 1 and 2 are mostly properties of the draw.** A random
20-seed subset satisfies both monotone criteria only 1.2% of the time — and
the n=10 run's criterion-1 pass was itself one of the lucky 19%.

The phase's pre-committed bar, as written, asks for strict monotonicity of a
curve that has plateaus. **Strict monotonicity is not a property this
organism's displacement curve has**, at any practical n: the low end is
DI = 0.000 exactly and the high end saturates at DI ≈ 0.71. More seeds
cannot make a plateau into a ramp.

This is the substantive content of the raise-n run. It is **not** a license
to re-score the protocol: the verdict is INCONCLUSIVE, no boundary is
claimed, and the four criteria stand as written.

---

## 7. The added seeds moved the curve — and that is not ordinary noise

The raise-n run is not "the n=10 curve plus precision". The twenty added
seeds shifted the curve consistently, and two of those shifts fall outside
what pure resampling produces.

| Point | original 10 | added 20 | gap | p (random 10-vs-20 splits) |
|---|---|---|---|---|
| DI at 6:1 | 0.750 | 0.697 | −0.053 | **0.0022** |
| DI at 2:1 | 0.283 | 0.164 | −0.119 | **0.0103** |
| DI at 3:1 | 0.722 | 0.697 | −0.025 | 0.35 |
| DI at 4:1 | 0.739 | 0.714 | −0.025 | 0.39 |
| PI at 1:4 | 0.789 | 0.719 | −0.069 | 0.087 |
| PI at 1:3 | 0.794 | 0.733 | −0.061 | 0.059 |
| PI at 1:2 | 0.783 | 0.731 | −0.053 | 0.136 |
| PI at 1:1 | 0.728 | 0.711 | −0.017 | 0.55 |

Every non-zero gap points the same way: the added seeds sit lower on both
DI and PI.

The seed enters the world only through `random.Random(seed)`, and the entity
set does not depend on it, so the seeds *should* be exchangeable. But the
campaign's seeds are **consecutive integers**, and "the first ten consecutive
seeds" versus "the next twenty" is precisely the pattern that
non-exchangeability would produce — and precisely what an unlucky draw would
produce too.

**A seed-exchangeability audit was run to tell the two apart.** It is an
instrument audit: it produces no experimental claim, changes no criterion and
cannot turn this result into a boundary claim.

### 7.1 The audit's answer: the seeds ARE exchangeable

Thirty **fresh, non-consecutive, pre-declared** seeds (a fixed draw over a
range of 10⁹, so they carry no block structure) were run at the same sweep
point — 6:1, the point with the largest observed gap — and asked the same
question.

| Seed set | DI mean at 6:1 |
|---|---|
| campaign, original 10 | 0.7500 |
| campaign, added 20 | 0.6972 |
| campaign, all 30 | 0.7148 |
| **AUDIT, fresh 30 non-consecutive** | **0.7241** |

**The fresh set lands on the pooled value.** Its mean differs from the
campaign's 30-seed mean by +0.0093 — **p = 0.60** against random 30/30 splits
of all 60 measured values. If the campaign's consecutive seeds were
systematically different from other seeds, a scattered fresh set would give a
different mean. It does not.

**And the fresh set's own arbitrary half-split has the opposite sign.** Its
first 15 seeds give DI 0.7037 and its second 15 give 0.7444 — a gap of
**−0.0407**, against the campaign's **+0.0528**. Similar magnitude, opposite
direction. That is what an exchangeable axis looks like when the partition is
arbitrary: the lumpy, discrete DI distribution (values are multiples of 1/18)
routinely produces gaps of this size under a split, and the *direction* is
where the luck goes.

**Therefore: the original ten seeds were an unlucky high draw, not a
seed-block artifact.** The shift between the n=10 and n=30 curves is sampling
luck, exactly as the owner suspected might be true.

**Consequence for the bootstrap: the paired bootstrap over seeds is sound.**
And the n=30 curve is the better estimate — not because the added seeds were
different, but because there are more of them.

*(The audit's own numbers are in `docs/phase_l_seed_audit.json`; the script is
`benchmarks/phase_l_seed_audit.py`, and it checkpoints after every cell so a
killed run resumes rather than redoing work — which it had to, after a first
run was killed by a background-task cancellation.)*

---

## 8. What is established, and what is pending

### Established (measured, preregistered, audited)

- **The instrument works.** Four audits pass; the sweep is non-degenerate; the
  manipulation lands; no cell was unmeasurable.
- **The displacement curve has a stable shape**: a preservation plateau
  (DI = 0.000 exactly, PI ≈ 0.74), a transition band, a displacement
  plateau (DI ≈ 0.71, PI = 0.000), and a crossing at **3:1** that is interior
  to the sweep and reproducible under every check — 10,000/10,000 bootstrap
  replicates, 8 alternative bootstrap seeds, and leave-one-seed-out at 3:1 in
  **30 of 30** folds.
- **The crossing is the phase's most stable quantity.** Tripling n did not
  move it.
- **The two stable criteria are the two robust ones.** The DI range and the
  interior crossing hold in 100% of random subsets; the two strict-monotonicity
  criteria hold in 7–19%.

### Pending — not established

- **A boundary in the `H2-L` sense is not established.** Two of the four
  criteria are not met, and the pre-committed verdict is INCONCLUSIVE.
- **That PI decreases monotonically across the sweep, and that DI increases
  monotonically across the sweep, are not established** — and the data says
  the curve does not have those properties at its two plateaus.
- **The seed axis's exchangeability is not settled** (§7).
- **V2–V5 were not run.** No Phase L outcome authorises a V2.
- Nothing about capability, and nothing about the support ratio being *the*
  operative variable beyond this axis on this engine. The baseline rule was
  recorded and not exercised.

---

## 9. What was deliberately not done

- No prediction was revised, and no criterion was re-read or relaxed.
- No gate was relaxed to make the campaign runnable or the verdict tidier.
- The diagnostic was reported **with** the failing criteria, not instead of them.
- **V2–V5 were not launched.** No Phase L outcome authorises a V2.
- Unmeasurable values were excluded, never zeroed — there were none.

---

## 10. Reproduction

```bash
$env:PYTHONHASHSEED='0'
python benchmarks/phase_l_campaign.py --families V1 --seeds 30 --workers 12 \
       --resume --out docs/phase_l_results.json
python benchmarks/phase_l_analyze.py --results docs/phase_l_results.json
```

The harness is resumable: it rebuilds completed cells from the results file,
or from the NDJSON live recording if that file is missing or truncated, and
it survives a torn final line from a hard kill. Nothing in this run was
re-run and no progress was lost; the 80 original cells were reused exactly
as measured.
