# Phase L — V1 primary axis: results

**Run date:** 2026-10-25 · **Arm:** V1 (primary axis) · **Cells:** 80 of 80, complete
**Verdict by the four pre-committed criteria: `H3-L — INCONCLUSIVE`.**
**Protocol remedy for this outcome: raise n; conclude nothing. No outcome here authorises a V2.**

Protocol: [`docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md`](PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md)
(frozen; Amendments 1 and 2 applied **before** any Phase L outcome existed).

---

## 1. Run provenance

| Field | Value |
|---|---|
| Arm | V1 only (primary axis) |
| Sweep points | 8 — 1:4, 1:3, 1:2, 1:1, 2:1, 3:1, 4:1, 6:1 |
| Seeds | 10 per point (20261023 – 20261032) |
| Cells | 80, all complete |
| Workers | 12 |
| `PYTHONHASHSEED` | `0` — **pinned as required** (recorded as the actual value, not as an assumption) |
| Bootstrap replicates | 10,000, paired across seeds |
| Decision interval | **99.00%** (alpha 0.01) — the corrected value from Amendment 2 |
| Wall clock | 8,057.8 s |
| Engine | Organica 1, frozen at tag `v0.9.0` (verified unchanged by `tests/test_v1_freeze.py`, 16/16) |
| Harness | commit `8d49eaf` |

Artifacts: `docs/phase_l_results.json` (canonical) and `docs/phase_l_results.ndjson`
(live recording, one line per cell).

---

## 2. Instrument audits — all four pass

| Audit | Result | Evidence |
|---|---|---|
| Discrimination control | **PASS** | floor: first-seen-wins DI 0.000 / PI 1.000; ceiling: last-seen-wins DI 1.000 / PI 0.000 — the metric separates both extremes |
| Ceiling check | **PASS** | the perfect model returns DI 1.000 with both structures retained (18/18 and 18/18) — DI 1.0 with PI 1.0 is reachable, so DI is not a retention artefact |
| Degeneracy audit | **PASS** | 0 problems; every cell has a full denominator (`early_available` 18/18, `late_available` 18/18) |
| V4 pressure audit | **PASS** | peak beliefs 11 (cap_pressure 3) → **15**, the cap itself (cap_pressure 24) — the cap binds, so the V4 arm can move |

**Unmeasurable cells: 0.** No point was excluded, and nothing was zeroed.

---

## 3. The primary curve

V1, 10 seeds per sweep point. DI = Displacement Index, PI = Knowledge Preservation Index,
DS = Displacement Score (`DI − PI`, **diagnostic only** — not a metric, not a criterion, never averaged).

| Label | DI (sd) | PI (sd) | DS | Revision latency (cycles) | Seeds reaching DI > 0.5 |
|---|---|---|---|---|---|
| 1:4 | 0.000 (0.000) | 0.789 (0.078) | −0.789 | — | 0 / 10 |
| 1:3 | 0.000 (0.000) | 0.794 (0.070) | −0.794 | — | 0 / 10 |
| 1:2 | 0.000 (0.000) | 0.783 (0.096) | −0.783 | — | 0 / 10 |
| 1:1 | 0.000 (0.000) | 0.728 (0.055) | −0.728 | — | 0 / 10 |
| 2:1 | 0.283 (0.124) | 0.600 (0.122) | −0.317 | — | 0 / 10 |
| 3:1 | 0.722 (0.037) | 0.022 (0.039) | +0.700 | 347 | 10 / 10 |
| 4:1 | 0.739 (0.064) | 0.000 (0.000) | +0.739 | 285 | 10 / 10 |
| 6:1 | 0.750 (0.029) | 0.000 (0.000) | +0.750 | 236 | 10 / 10 |

---

## 4. The four pre-committed criteria

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | **DI is monotone increasing** with a non-degenerate range | **MET** | DI non-decreasing across all 8 points; range 0.750 ≥ 0.25 |
| 2 | **PI is monotone decreasing** over the same sweep | **NOT MET** | mean PI **rises** 0.789 → 0.794 between 1:4 and 1:3 (+0.005) before falling monotonically through the rest of the sweep |
| 3 | **The curves cross**, interior to the sweep | **MET** | crossing at **3:1** — sweep position 5 of 7 interior positions |
| 4 | **The crossing is reproducible** (paired bootstrap over seeds, 99% interval excludes both endpoints) | **MET** | interval **[5.0, 5.0]**; **10,000 / 10,000** replicates found a crossing |

**Criterion 2 is the only failure.** The rise that breaks it is +0.005 at a point whose
standard deviation is 0.070 (and the neighbouring point's is 0.078). The criterion is
evaluated on the mean curve exactly as the frozen protocol specifies; it is not met.

**The criterion was not re-read, relaxed, or reinterpreted after the fact.** It was
evaluated once, by the committed code, and it failed.

### Terminal outcome

Protocol §7 pre-committed four outcomes. The verdict maps to **H3-L — inconclusive**:
*raise n; do not conclude anything.*

---

## 5. The Revision Threshold

| Quantity | Value |
|---|---|
| Crossing label | **3:1** |
| Sweep position | 5 of 7 interior positions |
| Paired-bootstrap interval (99%) | **[5.0, 5.0]** — the narrowest an interval over 8 positions can be |
| Replicates that found a crossing | **10,000 / 10,000** |
| Excludes both endpoints | **Yes** (criterion 4 satisfied) |
| Robustness — 8 alternative bootstrap seeds | `INTERIOR` (all eight) |
| Leave-one-seed-out crossings | **3:1 in 10 of 10** |

The crossing location is not a coincidence of the seed set: dropping any single seed
leaves it at 3:1, and the bootstrap never placed it anywhere else.

---

## 6. Revision latency (co-primary report, Amendment 2)

Reported separately; never averaged; **not** a success criterion.

- **0 of 10 seeds** reached DI > 0.5 at 1:4, 1:3, 1:2, 1:1 or 2:1 — the organism never
  began revising under those pressures within the run.
- At 3:1: **10 / 10** seeds reached it, median **347 cycles** from the late group's arrival.
- At 4:1: **10 / 10**, median **285 cycles**. At 6:1: **10 / 10**, median **236 cycles**.

Latency falls as pressure rises, and the transition is abrupt rather than gradual:
the organism does not revise slightly more under higher pressure — it goes from *never*
(0/10) to *always* (10/10) between 2:1 and 3:1.

---

## 7. The DS diagnostic

DS is reported per point so coexistence and displacement can be told apart, and it is
never a criterion. It shows the transition passing through a coexistence region
rather than a clean handover: at 2:1 the organism retains 60% of the early structure
while holding 28% of the late structure (DI 0.283 / PI 0.600, DS −0.317). The gap
between the two indices — the thing Phase K's K3 showed is not automatic — only turns
positive at 3:1.

---

## 8. What is established, and what is pending

### Established (measured, preregistered, audited)

- **The instrument works.** All four audits pass; the sweep is non-degenerate; the
  manipulation lands (DI moves from 0.000 to 0.750 across the axis); no cell was
  unmeasurable.
- **The pilot's flat line was an artefact, and the fix held.** DI = 0.000 at the four
  lowest points is now a *property of the organism under low displacement pressure*,
  not an artefact of the harness — the same code, the same audits, a different answer.
- **The organism sits at the preservation pole** at 1:4, 1:3, 1:2 and 1:1: nothing of
  the late structure is incorporated, and roughly three-quarters of the early structure
  survives.
- **On the primary axis, DI and PI cross at 3:1, interior to the sweep, and the
  crossing location is highly reproducible** (criterion 3 and criterion 4 both met).

### Pending — not established

- **A boundary in the H2-L sense is not established.** Criterion 2 was not met, so the
  pre-committed verdict is INCONCLUSIVE and the protocol's remedy governs.
- **PI's monotone decrease over the sweep is not established.**
- **V2–V5 were not run.** The protocol states that no outcome authorises a V2, and the
  secondary arms remain unmeasured.
- Nothing about capability, and nothing about the support ratio being *the* operative
  variable beyond this one axis on this one frozen engine.
- The baseline rule ("every simple baseline swept over a declared grid, **best** score
  used") was recorded and **not exercised** in V1 — the V1 arm is the organism's own
  curve, bracketed by the control and ceiling check rather than by a competing system.

---

## 9. One honest wrinkle in the protocol's own labels

The protocol describes the `H3-L` bucket as *"intervals too wide to place RT."*
**That is not what happened here.** The RT interval is `[5.0, 5.0]` — the narrowest
possible — criterion 4 passes, and the crossing survived every robustness check. The
verdict is INCONCLUSIVE because **criterion 2 failed**, not because the RT could not be
located.

This is recorded as a fact about the protocol's wording, **not** as a basis for
re-reading the criterion or for converting the verdict. The criterion was evaluated as
committed; it failed; the verdict stands as `INCONCLUSIVE`; the protocol's remedy for
that verdict — *raise n; conclude nothing* — governs. But the bucket's label and its
stated rationale should not be allowed to drift apart in later phases, and the next
phase should say what "inconclusive" means when the interval is narrow and a different
criterion failed.

---

## 10. What was deliberately not done

- No prediction was revised to fit any number above.
- No gate was relaxed, and no criterion was re-read after the fact.
- **V2–V5 were not launched.** No Phase L outcome authorises a V2, and the secondary
  arms are to be narrowed after the first sweep is reported.
- The DS diagnostic was never treated as a metric or a criterion.
- Unmeasurable values were excluded, never zeroed — there were none this time.

---

## 11. Reproduction

```bash
$env:PYTHONHASHSEED='0'
python benchmarks/phase_l_campaign.py --families V1 --seeds 10 --workers 12 \
       --resume --out docs/phase_l_results.json
python .scratch/analyze_phase_l.py          # curves, criteria, RT interval, robustness
```

The harness is resumable: it rebuilds completed cells from the results file, or from
the NDJSON live recording if that file is missing or truncated, and it survives a torn
final line from a hard kill. Nothing in this run was re-run, and no progress was lost.
