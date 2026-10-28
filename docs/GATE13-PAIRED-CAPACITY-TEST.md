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
