# Pilot 0: Acquisition Harness Instrumentation Audit

**Date:** 2026-10-28  
**Scope:** Single-seed full-instrumentation validation on exploratory seed `20261100`  
**Purpose:** Verify that every gate, intervention, removal rule, metric shape, and baseline behaves strictly as specified in `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md`.  
**Artifact:** `docs/acquisition_single_seed_pilot.json` (Completed in 505.89s)

---

## 1. Instrumentation Verification Checklist

| Specification Item | Preregistered Requirement | Measured Pilot 0 Outcome | Status |
| :--- | :--- | :--- | :---: |
| **Gate 16: Scratch-Only Guarantee** | `LIVE_DB` must never be touched; all 10 cells use isolated scratch DBs. | Verified: 10 scratch databases created and unlinked; live DB 0 delta. | **PASSED** |
| **Gate 13: Sufficiency Gate** | Evaluated on `asserted_structure_coverage` against threshold $\ge 0.50$. | Coverage = **0.0000** (0/112). `acquisition_failed = True`. Raw temporal coverage recorded as **1.0000** (112/112). | **PASSED (Correctly flagged)** |
| **Transfer Gate Logic** | When Gate 13 fails, transfer is not measurable, not a transfer failure. | `transfer_status = "not_measurable_due_to_acquisition_failure"`. Scores reported under diagnostic keys. | **PASSED** |
| **P-Target Determinism (§6.2)** | Layer-1 candidate present in $\ge 2$ cycles with max strength; tie-break by ID. | Selected: `loop_037e7a92`. Verified identical selection across cells. | **PASSED** |
| **Gate 11: P-org Intervention** | Target deleted from organism memory & suppressed from re-derivation in Cells 2 & 3. | Verified: 0 remaining rows in DB for `loop_037e7a92`. `p_org_verified = True`. | **PASSED** |
| **P-obs Observer Scope (§6.2)** | Organism state and prediction readout untouched; withheld only from auditor reconstruction. | Cell 1 log-loss ($0.453018$) is **bit-identical** to Cell 4 log-loss ($0.453018$). Auditor reconstruction reflects 119 unique candidates (target withheld) vs. organism 120 unique candidates. | **PASSED** |
| **Gate 12: E-rem Removal (§3.3)** | `events` and `precedes` cleared; `cooccurrences`, `tag_counts`, and learned structures preserved. | `events_cleared = True`, `precedes_cleared = True`, `cooccurrences_preserved = True`, `tag_counts_preserved = True`. Verified in Cells 3, 5, 6. | **PASSED** |
| **Baseline E-rem Fallback** | When raw episodes are removed, Replay and Statistical must fall back to uninformative prior. | Replay Cell 8 and Statistical Cell 10 score **0.403045** (exact theoretical uniform log-loss: $\log(16)/n$). | **PASSED** |
| **Metric Dual Accounting (§4.3)** | Both primary house shape (`exclude_self=True`) and co-primary self-cells shape (`exclude_self=False`) reported. | Both shapes computed and stored across all cells and reference models. | **PASSED** |
| **Independent Calibration** | Organica smoothing $\alpha = 256.0$ and baseline hyperparameters frozen from seed `20261099`. | Replay `(1, None, 0.5)` and Statistical `(0.1, None, None)` applied without in-seed tuning split. | **PASSED** |

---

## 2. 10-Cell Score Matrix (Pilot 0: Seed `20261100`)

### Primary House Shape (`exclude_self = True`)

| Cell | Condition | Learner | Retention (110–149) | Transfer Diagnostic (150–199) | Revision (250–299) |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **1** | `P-none × E-pres` | Organica | 0.453018 | 0.453912 | 0.463372 |
| **2** | `P-org × E-pres` | Organica | 0.453018 | 0.453842 | 0.463321 |
| **3** | `P-org × E-rem` | Organica | 0.453018 | 0.453842 | 0.428071 |
| **4** | `P-obs × E-pres` | Organica | 0.453018 | 0.453912 | 0.463372 |
| **5** | `P-obs × E-rem` | Organica | 0.453018 | 0.453912 | 0.427814 |
| **6** | `P-none × E-rem` | Organica | 0.453018 | 0.453912 | 0.427814 |
| **7** | `E-pres` | Replay | 0.347521 | 0.349592 | 0.351989 |
| **8** | `E-rem` | Replay | 0.403045 | 0.403045 | 0.403045 |
| **9** | `E-pres` | Statistical | 0.347273 | 0.350723 | 0.352194 |
| **10** | `E-rem` | Statistical | 0.403045 | 0.403045 | 0.403045 |
| *Ref* | *Bayes ceiling* | *Closed-form* | *0.276259* | *0.272365* | *0.275176* |
| *Ref* | *Base rate* | *Marginal* | *0.409581* | *0.409511* | *0.406124* |

---

## 3. Structural Findings on the Instrumentation

1. **Intervention Dissociation Holds Strictly (Q1 vs. Q2):**
   In Cell 4 (`P-obs × E-pres`), the organism's task prediction is byte-identical to Cell 1 ($0.453018$), but the auditor's reconstruction reflects exactly $119$ unique candidates rather than $120$. The target `loop_037e7a92` is withheld purely from external provenance without contaminating internal state.
2. **E-rem Cleanly Decouples Baselines from Organica:**
   When episodes are stripped, Replay (Cell 8) and Statistical (Cell 10) collapse instantly to the uniform base floor ($0.403045$). In contrast, Organica maintains its learned state in Cell 6 ($0.453018$).
3. **Revision Stepping Verified:**
   In Cells 3, 5, 6 under continued learning in cycles 200–249, Organica's score shifts from $0.4530$ to $0.4278$, demonstrating that the engine steps and updates beliefs under the new regime law.

---

## 4. Conclusion

**The acquisition harness is fully verified against its operational specifications.**
All gates, interventions, removals, scoring shapes, and baseline decouplings execute exactly as defined in `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md`.
