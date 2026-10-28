# Gate 13 Preflight Audit: Counterfactual Decomposition of Acquisition Coverage

**Date:** 2026-10-28  
**Scope:** Controlled counterfactual diagnosis across diagnostic seeds `20261101`–`20261105`  
**Status:** Campaign Paused. Seeds `20261101`–`20261105` designated diagnostic / inspected.  
**Raw Telemetry:** `docs/gate13_counterfactual_audit.json`

---

## 1. Executive Summary & Experimental Finding

Across all five diagnostic seeds (`20261101`–`20261105`), the frozen engine consistently fails Gate 13 (threshold $\ge 0.50$), asserting **0 to 3 of 112** ground-truth world transition edges ($0.0\%$ to $2.7\%$), while raw temporal memory contains **112/112 (100.0%)** of those transitions.

A controlled counterfactual audit isolated each stage of the acquisition pipeline to locate where transition information is lost:

1. **Information Presence in Raw Memory:**
   - Both **lookback=3** (`mem.temporal_edges`) and **lookback=1** (direct 1-step predecessor pairs from the raw event stream) achieve **112/112 (100.0%)** coverage across all 5 seeds.
2. **The Capacity Counterfactual (Decisive Proof):**
   - The engine's `_build_predictions` detector applies a minimum count threshold (`PREDICTION_MIN_COUNT = 5`) followed by a capacity cap (`MAX_PREDICTIONS = 20`) sorted by raw temporal count.
   - **Counterfactual without cap:** When all prediction candidates meeting `min_count >= 5` are retained without the `MAX_PREDICTIONS = 20` cap, coverage jumps from **0.0%–0.9% to 99.1%–100.0% (111–112 out of 112 edges)**.
   - **With the `MAX_PREDICTIONS = 20` cap:** Coverage drops to **0.0%–0.9% (0 to 1 of 112 edges)**.
   - **Mechanism:** Within-cell tag pairs accumulate higher-count temporal edges in raw memory than cross-cell transitions. The top 20 candidate slots are 95%–100% saturated by within-cell temporal edges (19–20 intra-cell vs. 0–1 inter-cell), completely discarding the valid cross-cell transition edges.
3. **Marker Isolation:**
   - Non-vocabulary marker strings (specifically `'high_structural_significance'` from hypothesis evaluation) were strictly excluded from world-tag edge accounting, confirming that the remaining asserted edges are overwhelmingly intra-cell pairs.

---

## 2. Multi-Stage Coverage Breakdown Across Seeds

| Seed | Raw Temp (Lookback 3) | 1-Step Temp (Lookback 1) | Uncapped Predictions (`min_count >= 5`) | Capped Predictions (`MAX_PREDICTIONS = 20`) | Final Projected Graph (Gate 13) | Gate 13 Verdict |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `20261101` | **112 / 112** (100%) | **112 / 112** (100%) | **111 / 112** (99.1%) | **0 / 112** (0.0%) | **0 / 112** (0.0%) | **FAIL** |
| `20261102` | **112 / 112** (100%) | **112 / 112** (100%) | **112 / 112** (100%) | **1 / 112** (0.9%) | **1 / 112** (0.9%) | **FAIL** |
| `20261103` | **112 / 112** (100%) | **112 / 112** (100%) | **112 / 112** (100%) | **0 / 112** (0.0%) | **1 / 112** (0.9%) | **FAIL** |
| `20261104` | **112 / 112** (100%) | **112 / 112** (100%) | **112 / 112** (100%) | **0 / 112** (0.0%) | **0 / 112** (0.0%) | **FAIL** |
| `20261105` | **112 / 112** (100%) | **112 / 112** (100%) | **112 / 112** (100%) | **0 / 112** (0.0%) | **3 / 112** (2.7%) | **FAIL** |

---

## 3. Candidate Type Breakdown & Structural Profile

Evaluating individual candidate types (with markers excluded) reveals that structure formation across all sleep detectors is heavily biased toward within-cell clusters:

### Candidate Type Overlap with World Edges (Seed `20261101`)
- **`prediction_candidate`**: 22 unique cands $\to$ 22 asserted edges (**22 intra-cell, 0 inter-cell**), **0/112 world overlap**.
- **`loop_candidate`**: 22 unique cands $\to$ 30 asserted edges (**30 intra-cell, 0 inter-cell**), **0/112 world overlap**.
- **`process_candidate`**: 11 unique cands $\to$ 14 asserted edges (**14 intra-cell, 0 inter-cell**), **0/112 world overlap**.
- **`workflow_concept`**: 11 unique cands $\to$ 7 asserted edges (**7 intra-cell, 0 inter-cell**), **0/112 world overlap**.
- **`dream`**: 6 unique cands $\to$ 4 asserted edges (**4 intra-cell, 0 inter-cell**), **0/112 world overlap**.
- **`hypothesis`**: 12 unique cands $\to$ 2 asserted edges (**2 intra-cell, 0 inter-cell**), **0/112 world overlap**.

### Candidate Type Overlap with World Edges (Seed `20261105`)
- **`prediction_candidate`**: 28 unique cands $\to$ 22 asserted edges (**22 intra-cell, 0 inter-cell**), **0/112 world overlap**.
- **`loop_candidate`**: 22 unique cands $\to$ 28 asserted edges (**26 intra-cell, 2 inter-cell**), **2/112 world overlap**.
- **`dream`**: 8 unique cands $\to$ 4 asserted edges (**2 intra-cell, 2 inter-cell**), **2/112 world overlap**.
- **Total projected graph**: 3 asserted edges overlap with world ground-truth relations (**3/112 = 2.68%**).

---

## 4. Why the Capacity Cap Filters Out the World Transitions

The counterfactual comparison provides a clear explanation:
1. **Uncapped Temporal Statistics:**
   - On seed `20261101`, there are **237 candidate transitions** meeting `min_count >= 5` in temporal memory: **48 intra-cell** and **189 inter-cell**.
   - These 189 inter-cell candidates cover **111 of the 112** ground-truth world transitions (99.1%).
2. **Frequency Disparity:**
   - In Task 2, an event draws 2 tags from a 4-tag cell. Because tags within a cell co-occur in close proximity across subsequent events, intra-cell pairs accumulate high counts (often $\ge 50$).
   - Cross-cell transitions are distributed across 2 possible successor cells (flip-P vs flip-Q) and across 4 tags per cell, meaning each individual cross-cell edge has lower counts (typically 10–30).
3. **The Sort & Truncation Bottleneck:**
   - In `organica/sleep.py`, `_build_predictions` executes:
     ```python
     candidates.sort(key=lambda p: p.evidence["temporal_count"], reverse=True)
     return candidates[:self.MAX_PREDICTIONS]  # MAX_PREDICTIONS = 20
     ```
   - Because the 48 within-cell pairs dominate the highest frequency tiers in the temporal transition table, sorting by raw temporal count guarantees that all 20 slots are filled by within-cell pairs.
   - The cross-cell transitions—despite being present, valid, and above threshold—are discarded by truncation at rank 21+.

---

## 5. Methodological & Protocol Implications

1. **Gate 13 Remains Intact:**
   The $0.50$ sufficiency threshold remains fixed. Gate 13 functioned as intended: preventing an unmeasurable transfer experiment from running on an organism that failed to assert the generating relations.
2. **Frozen Engine Taxonomy Boundary:**
   The limitation is not a defect in readout projection, nor an absence of the signal in memory. It is a direct consequence of Layer-1 sorting by raw count combined with the capacity cap (`MAX_PREDICTIONS = 20`) in the frozen engine under this stimulus density.
3. **Status of Confirmatory Sample:**
   Seeds `20261101`–`20261105` are classified as **diagnostic preflight seeds** alongside exploratory seed `20261100`. They will not be counted as confirmatory evidence in any future study.
4. **Campaign Status:**
   The full 30-seed campaign remains **paused**.
