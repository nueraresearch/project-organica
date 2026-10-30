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
| **1** | `P-none × E-pres` | Organica | 0.453018 | 0.453886 | 0.463391 |
| **2** | `P-org × E-pres` | Organica | 0.452951 | 0.453823 | 0.463334 |
| **3** | `P-org × E-rem` | Organica | 0.452951 | 0.453823 | 0.428125 |
| **4** | `P-obs × E-pres` | Organica | 0.453018 | 0.453886 | 0.463391 |
| **5** | `P-obs × E-rem` | Organica | 0.453018 | 0.453886 | 0.427846 |
| **6** | `P-none × E-rem` | Organica | 0.453018 | 0.453886 | 0.427846 |
| **7** | `E-pres` | Replay | 0.347521 | 0.349592 | 0.351989 |
| **8** | `E-rem` | Replay | 0.403045 | 0.403045 | 0.403045 |
| **9** | `E-pres` | Statistical | 0.347273 | 0.350723 | 0.352194 |
| **10** | `E-rem` | Statistical | 0.403045 | 0.403045 | 0.403045 |
| *Ref* | *Bayes ceiling* | *Closed-form* | *0.276259* | *0.272383* | *0.275208* |
| *Ref* | *Base rate* | *Marginal* | *0.409581* | *0.409529* | *0.406084* |

---

### 2.1 Correction 1 (2026-10-29): transcription drift in the score matrix

**What was wrong.** The 10-cell score matrix above was transcribed from
`docs/acquisition_single_seed_pilot.json` by hand, and **18 of its 36 values
disagree with that artifact** — every one of them in the fourth or fifth
decimal of log-loss (the largest disagreement is $6.7\times10^{-5}$). The
artifact itself did not change: the same values are present in both commits
that carried it (`89b0744`, 2026-10-28, and `4ceeab4`, 2026-10-29), so the
drift is in the transcription, not in the run. No conclusion in this document
changes: Organica's readout still loses to both baselines, and the E-rem floor
is still $0.403045$.

**What was done.** Every value in the matrix above was replaced with the
artifact's value, read mechanically from the JSON rather than retyped. The check
is permanent: `tests/test_readout_tables.py`. Six of the drifted values had been
inherited by `papers/01_developmental_structure_formation.md`
§4.7, and the five-row summary that repeats this matrix in
`docs/ACQUISITION-ENDPOINT-AUDIT.md`, `docs/ORGANICA-V2-DESIGN-BRIEF.md`,
`docs/FACTS-SHEET.md`, `research-journal/phase_g_findings_20261021.md` and
`research-journal/_journal_entry_51.md` was corrected with it.

**Why it is recorded here rather than applied silently.** The artifact is
stable and the table was not, so the table was wrong — and a wrong number in a
table that reads as machine-generated is the kind of defect that survives
every review, because it looks checked. The rule this exposes is narrow and
worth stating: **a table transcribed from an artifact is a new claim, and it
needs a mechanical check against that artifact.** The generator that draws the
manuscript's figure for this readout now reads the artifact directly and
asserts the values it draws, so the transcription step no longer exists on
that path, and `tests/test_readout_tables.py` now asserts every document that
restates this readout against the artifact. See `docs/USER-MANUAL.md` finding 34.

**A first repair made it worse, and the mechanical check caught it (2026-10-30).**
The correction was first applied by a script that replaced the drifted rows with
hand-written replacements. That script **replaced the two reference rows**
(Bayes ceiling, base rate) with **duplicate copies of cells 7 and 8**, so the
table went from *18 wrong values* to *12 rows, of which 2 were duplicates and 2
references were missing*. The defect was invisible to review: the table still
had the right shape, the right headers and the right-looking numbers. It was
caught only by running the table against the artifact mechanically. The table
above is now **regenerated from `docs/acquisition_single_seed_pilot.json`** rather
than patched, and `tests/test_readout_tables.py` asserts that the checker can
itself fail.

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
