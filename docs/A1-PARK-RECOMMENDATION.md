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

The larger universe cleared the structural edge target, but K fell to **23–55** rows and the 20-row matching to **18, 15, 16, 26, 26, 18**. Its best C1 was **55**, still five short. More edges did not preserve availability; the added vocabulary diluted it.

The size choice was structural, not a K screen: 24 tags gave only **127–136** independent edges, while 28 tags gave **158–172**.

## 2. Why park rather than try another block

- No tested universe clears the adopted **60-row C1 floor**.
- A fresh block in the same world fails, and a predeclared larger world fails through dilution.
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

A genuinely different construction is allowed to be tried. It must explain why it does not repeat the dilution failure, and it must be fixed before its K is measured.

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
- [Successor preflight](A1-SUCCESSOR-PREFLIGHT.md)
- [C1/C4 VOID gate](A1-C1-C4-VOID-GATE.md)
- [Pre-freeze checklist](A1-PRE-FREEZE-CHECKLIST.md)
