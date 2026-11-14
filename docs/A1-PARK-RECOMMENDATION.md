# A1 park recommendation

**ID:** `A1-PARK-RECOMMENDATION-1`  
**Date:** 2026-11-14  
**Status:** `RECOMMENDATION — OWNER DECISION REQUIRED; NO FREEZE, NO GRANT, NO RUN`  
**Decision owner:** ____________________  
**Decision and date:** ____________________

**Recommendation: park the current A1 design.** Do not freeze a target set, issue a grant or run a cell. Preserve the existing records and treat A1 as **not run / not identified under the current design**, with C1 as the blocking gate.

This is a recommendation, not the owner's decision and not a treatment claim.

## 1. What was tested

| Candidate | Independent edges | C1 ceiling by seed | Result |
| --- | ---: | --- | --- |
| Current six-seed control | 63–64 | 44, 31, 39, 35, 43, 36 | FAIL 0/6 |
| Fresh block `20650101–20650106` | 63–64 | 40, 37, 46, 42, 31, 38 | FAIL 0/6 |
| 28-tag larger universe `20660101–20660106` | 158–172 | 23, 40, 42, 55, 47, 37 | FAIL 0/6 |

The fresh block had a 20-row A+K matching on **6/6**, so target capacity was not its blocker; its best C1 was still **14 rows short**. K was lower on five seeds and A on `20650105`.

The larger universe cleared the structural edge target, but K fell to **23–55** rows and the 20-row matching to **18, 15, 16, 26, 26, 18**. Its best C1 was **55**, still five short. More edges did not preserve availability; support per possible pair diluted it, including within the old vocabulary.

The dilution is now measured. Candidate edges rose **383 → 1000**, but K-available rows rose only **242 → 244**; A rose **279 → 353**, also sublinearly. The old-old family was not protected: its K density fell **63.2% → 18.9%**, while new-involving edges were not worse. By transition type, flip-P K rows stayed at **145 → 146** and flip-Q at **97 → 98** while their edge counts roughly doubled. The constraint is **K supply**, not edge count.

The K-supply discriminator narrows the next question. On the fixed 28-tag world, prediction caps **20/40/80** move A **271 → 353 → 498** but K stays **240 → 244 → 244**, so **prediction-cap is not the K bound**. Support K density rises **10.7% → 40.9%** across support bins, but at matched support the 16-tag world still has more K (8–15: **42.7% vs 28.3%**; 16+: **68.8% vs 40.9%**; weighted gap **25.0 pp**). The reading is **support-associated, not fully explanatory**. The next diagnostic should target the **carrier path** directly.

The absolute-K predictor join is the caution on that next step: across **18** seeds, no pre-run feature beats the mean baseline out of world. The best model is `A_available` at **4.65** K rows, only **0.16** better than baseline, and it is a post-run output; the best pre-run feature is **0.64 rows worse**. `candidate_edges` fails out of world (MAE **177.21**) and has rho **0.03** inside the 28-tag block. Total K is **seed-specific** under these summaries. The carrier-supply trace finds the window: **1,765** candidate edges produce **714** candidate K, while **1,004** loop-eligible candidates never become K; every loop-carried K ranks **1–15**, every eligible non-K **16+** (median **49**). The builder sees **1,421,231** possible 2-/3-cycles and returns **26,932** (**1.90%**), with the 15-loop cap binding on **81.2%** of cycles. Candidate K stays **228/242/244** across **382/383/1,000** candidates, while engine-wide directed K sums to **3,548** against **714** candidate K. That is a fixed output-window account, not an edge shortage. The loop-cap counterfactual confirms the window is causal in direction: at caps **15/30/60/120**, candidate K rises **714 → 1,001 → 1,294 → 1,498**, with **10** edges reshuffled out. But it is not a fixed K quota—an **8×** cap buys **2.1×** candidate K, and the 28-tag block still reaches only **733/1,000** at cap 120. Reopening A1 would require a construction that predicts and overcomes that sublinear window, not merely a larger cap or edge count. The C1 counterfactual shows why a K-only repair is insufficient: at cap 120, A is the binding path on **18/18** seeds, K on **0**, and the marginal C1 ceiling passes only **2/18** (larger-28 seeds **67** and **66**); the joint A∩K ceiling passes **0/18** because those overlaps are **58** and **52**. The A edge set is unchanged by the loop cap. The prediction-cap counterfactual shows A is movable: at loop cap 120, caps **20/40/80** move A **744 → 913 → 1,129** while K stays **1,499 → 1,498 → 1,497**. Marginal C1 passes **0 → 2 → 6 /18**, joint C1 **0 → 0 → 4 /18**; all four joint passes are larger-28, and both 16-tag blocks remain **0/6** (joint maxima **59** and **58**). A viable successor must therefore address the loop window, prediction capacity above 80, and the A/K overlap—not just one of them. At the shipped prediction cap 112, larger-28 now clears **6/6** jointly (minimum 60), but the 16-tag blocks clear only **2/12** (`20630103` 60, `20650104` 63; ten fail with max 59); overall joint C1 is **8/18**. The larger construction has an availability path at loop cap 120 and prediction cap 112, but the 16-tag A shortfall remains. Park stays the default for the current design because its shipped operating point is not this cap pair and the 16-tag branch still fails; it is no longer accurate to say every tested construction fails under every cap.

The size choice was structural, not a K screen: 24 tags gave only **127–136** independent edges, while 28 tags gave **158–172**.

## 2. Why park rather than try another block

- No tested universe clears the adopted **60-row C1 floor**.
- A fresh block in the same world fails, and a predeclared larger world fails through measured K dilution: **+617** edges bought **+2** K rows.
- Target changes do not address C1: N20 and the competent-target rule are conditional C2/C8 work, and reverse-orientation rows are rejected as duplication.
- Selecting another seed block, another tag count or another edge subset after seeing K would select on the same no-arm baseline that judges the candidate. That is not a repair.
- Changing the 60-row floor or the 0.95 rule is a different study, not an A1 successor.

The stop rule in the disposition memo applies: if the no-arm preflight cannot show 60 K-available rows on every seed, **do not freeze, do not grant and do not run**.

## 3. What park means

- A1 is recorded as **not run / not identified under the current design**.
- C1 remains the blocking gate.
- No target is frozen, no seed is reserved, no grant is issued and no A1 cell is run.
- The C1/C4/C7/C8 contracts, ceilings, K decomposition, baseline records, fresh-block candidate and larger-universe candidate are preserved.
- The existing negative controls and failed candidates are not reinterpreted as treatment results.

**Park does not mean** treatment failure, a negative C2/C8 result, or evidence that the effect is absent. It means the current design cannot produce a measurable test under its own adopted contract.

## 4. What would reopen A1

A future owner decision may reopen only with:

1. a new, predeclared universe/construction that passes the no-arm preflight **without selecting on K**;
2. at least **60 independent C1 rows** on every seed, with stream integrity;
3. a **20-row** matching if C2/C8 remain in scope;
4. one edge universe shared by selector, runner and scorer;
5. a new protocol, freeze, seed reservation and dated grant.

A genuinely different construction is allowed to be tried. It must **specifically explain and overcome the measured K dilution**; a larger edge count alone is not enough. The discriminator rules out prediction-cap as the **K** bound and leaves support only partial; the later prediction-cap counterfactual shows A is movable, but cap 80 gives only **4/18** joint C1 passes and neither 16-tag block clears 60. The account must therefore name a **carrier-path** lever and a **prediction-cap or overlap** lever, and predict both effects before K is measured. It must be fixed before its K is measured. A structural predictor join is not that account: no pre-run feature in the current data predicts absolute K across worlds, and the carrier-supply trace shows why — the count is set by which loops enter the fixed 15-slot output window, not by how many structural edges exist.

## 5. Decision

| Option | Meaning |
| --- | --- |
| **PARK** | Recommended. Preserve A1 as not identified under the current design; no freeze, grant or run. |
| HOLD | Keep the branch open without a new candidate; no authority changes. |
| FUND NEW FEASIBILITY | Authorize one new predeclared construction through the preflight before any protocol act. |

**Owner decision:** ____________________  
**Date:** ____________________  
**Signature:** ____________________

## 6. What this is not

This is not a freeze, grant, run or treatment result. It selects no target, reserves no seed and makes no C2/C8 or causal claim.

## References

- [Disposition memo](A1-DISPOSITION-MEMO.md)
- [Successor requirements](A1-REDESIGN-REQUIREMENTS.md)
- [Fresh-seed candidate](A1-SUCCESSOR-CANDIDATE.md)
- [Larger-universe candidate](A1-LARGER-UNIVERSE-CANDIDATE.md)
- [K dilution report](A1-K-DILUTION.md)
- [K-supply discriminator](A1-K-SUPPLY-DISCRIMINATOR.md)
- [Absolute-K predictors](A1-K-TOTAL-PREDICTORS.md)
- [Carrier-supply trace](A1-K-CARRIER-SUPPLY.md)
- [Loop-cap counterfactual](A1-LOOP-CAP-COUNTERFACTUAL.md)
- [C1 at loop cap 120](A1-C1-CAP120.md)
- [Prediction-cap C1](A1-PREDICTION-CAP-C1.md)
- [Prediction cap 112](A1-PREDICTION-CAP-112.md)
- [Successor preflight](A1-SUCCESSOR-PREFLIGHT.md)
- [C1/C4 VOID gate](A1-C1-C4-VOID-GATE.md)
- [Pre-freeze checklist](A1-PRE-FREEZE-CHECKLIST.md)
