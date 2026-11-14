# A1 successor requirements and refusal checklist

**ID:** `A1-REDESIGN-REQUIREMENTS-1`  
**Date:** 2026-11-14  
**Status:** `REFERENCE — NO FREEZE, NO GRANT, NO RUN`

This is the front door for a second A1 successor candidate. It restates constraints already fixed by the C1/C4 gate, the disposition memo, the N20 rule and the successor preflight. It does **not** choose a design, select targets, reserve seeds, freeze a manifest, issue a grant or run a cell.

## 1. Candidate package

A candidate is a JSON spec with these fields:

| Field | Requirement |
| --- | --- |
| `kind` | `a1_successor_candidate` |
| `id` | A unique candidate ID |
| `seed_block` | At least **six fresh seeds**; not the current six; no duplicate seeds |
| `targets_in_scope` | `true` iff C2/C8 are in scope |
| `per_seed` | Every seed → candidate rows `{edge, A, K}` from a no-arm 120-cycle replay |

The candidate universe must be **one orientation per undirected pair**. Each row is a raw A/K boolean, not a treatment result.

## 2. Machine-readable contract

The schema is [`a1_successor_candidate.schema.json`](a1_successor_candidate.schema.json); the standard-library validator is [`A1-SUCCESSOR-SCHEMA.md`](A1-SUCCESSOR-SCHEMA.md). It checks the candidate package, the seed and universe declarations, the target-selection declaration, and the governance flags, then runs the existing preflight as a separate gate.

```bash
python -m benchmarks.a1_successor_schema --check
python -m benchmarks.a1_successor_schema --validate docs/a1_successor_candidate.json
python -m benchmarks.a1_successor_schema --self-test
```

`--check` verifies the committed schema and page and that the live candidate is structurally valid even when its gate fails. `--validate` is strict: any refusal, including a failing C1 gate, returns non-zero.

## 3. PASS conditions

A candidate passes only if **all** of these hold:

- **Freshness:** the block is not the current six seeds and was not selected, reordered or filtered on the same no-arm A/K that judges it. Any earlier K exposure, including a one-seed timing probe, is disclosed and did not alter the block.
- **Independence:** at least **60 independent edges per seed** after duplicate and reverse-duplicate removal.
- **C1 ceiling:** `min(A available, K available, independent edges) ≥ 60` on **every** seed.
- **Stream integrity:** no duplicate oriented edge, reverse pair or self-loop.
- **Targets, if in scope:** a capacity-respecting **20-row A+K matching** exists on every seed. This proves constructibility only; it does not prove C2 or C8 and does not repair C1.
- **One universe:** the runner, selector and result layer declare and use the same edge universe. The N4/N20 target profile and the 112-row directed cell stream must not silently substitute for the candidate stream.
- **Preflight before freeze:** `A1-SUCCESSOR-PREFLIGHT-1` returns `PASS` **before** any target freeze, seed reservation, grant or run.

## 4. Refusal conditions

Any one of these is a `FAIL`, not a reason to retry:

- `REUSED_CONTROL_SEEDS` — the current six seeds are only the negative control.
- `SEED_SCREENED_ON_K` — the block was chosen or reordered on the no-arm K it is meant to test.
- `UNDISCLOSED_K_EXPOSURE` — a prior probe is omitted from the candidate record.
- `DUPLICATE_EDGE`, `REVERSE_DUPLICATE`, `SELF_LOOP` — the stream is inflated or malformed.
- `INDEPENDENT_BELOW_60` — fewer than 60 independent edges after dedupe.
- `C1_BELOW_60` — the minimum of A, K and independent edges is below 60.
- `TARGET_POOL_BELOW_20` — C2/C8 are in scope but a 20-row matching does not exist.
- `TARGETS_SELECTED_BEFORE_PREFLIGHT` — a candidate spec is not a target freeze.
- `UNIVERSE_INCONSISTENT` — the scorer and the candidate use different edge sets.
- `NO_PREFLIGHT_PASS` — a proposal proceeds without a passing preflight.
- `PASS_TREATED_AS_GRANT` — a PASS is used to freeze, reserve or run.

A candidate that needs a lower floor, a different estimator, a favourable seed subset, or reverse-orientation rows is **not a successor under this checklist**. The 28-tag candidate also shows that a larger universe can fail by **dilution**: more independent edges does not preserve the K rate.

## 5. Current evidence

| Candidate | Independent edges | C1 ceiling by seed | 20-row matching | Result |
| --- | ---: | --- | --- | --- |
| Current six-seed control | 63–64 | 44, 31, 39, 35, 43, 36 | 32, 23, 36, 27, 35, 33 | FAIL 0/6 |
| Fresh block `20650101–20650106` | 63–64 | 40, 37, 46, 42, 31, 38 | 33, 30, 46, 36, 20, 32 | FAIL 0/6 |
| 28-tag larger universe `20660101–20660106` | 158–172 | 23, 40, 42, 55, 47, 37 | 18, 15, 16, 26, 26, 18 | FAIL 0/6 |

The fresh block had **64, 64, 64, 64, 63, 64** independent edges and a 20-row matching on **6/6**; its best seed was still **14 rows short**. The 28-tag candidate cleared the structural **144-edge** target but K collapsed to **23–55** and matching failed on four seeds. The cross-world report shows the mechanism: candidate edges rose **383 → 1000**, K-available rows rose only **242 → 244**, and old-old K density fell **63.2% → 18.9%**. The larger-universe route is therefore **tested and failed at this construction**; it does not prove every possible larger world fails, but it removes “just add tags” as a presumed fix. The redesign target is **K-capable edges**, not independent edges. The K-supply discriminator adds that prediction capacity is not the bound: caps **20/40/80** move A **271 → 353 → 498** but K stays **240 → 244 → 244**. Support is real but only partial (matched-support gap **25.0 pp**), so a future candidate still needs a carrier-path account, not another cap or tag count. The absolute-K predictor join finds no cross-world pre-run predictor: the best pre-run feature is **0.64 rows worse** than the mean baseline, and the best model (`A_available`, **4.65**) is a post-run output only **0.16** better than baseline. Another structural summary is not a mechanism. The carrier-supply trace supplies the missing path account: **1,765** candidate edges yield **714** candidate K, but **1,004** loop-eligible candidates never become K. Every loop-carried K ranks **1–15** in the engine's loop order; every eligible non-K ranks **16+** (median **49**). The builder sees **1,421,231** possible 2-/3-cycles and returns **26,932** (**1.90%**), with the 15-loop cap binding on **81.2%** of cycles. Candidate K stays **228/242/244** across **382/383/1,000** candidates while engine-wide directed K sums to **3,548** against **714** candidate K. A future design must therefore change the carrier output window or its ranking, not merely add candidate edges. The counterfactual confirms the direction: at loop caps **15/30/60/120**, candidate K rises **714 → 1,001 → 1,294 → 1,498**, with only **10** edges lost to reshuffling. But the 15-slot window is **not a fixed K quota**—8× the cap buys 2.1× K, and the 28-tag block still reaches only **733/1,000** at cap 120. A successor can use the window as a lever, but it must predict the sublinear response rather than assume a fixed budget. The C1 counterfactual then shows the remaining limit: at cap 120 A is the binding path on **18/18** seeds, K on **0**, and the marginal C1 ceiling passes only **2/18** (larger-28 seeds **67** and **66**); the joint A∩K ceiling passes **0/18** because those overlaps are **58** and **52**. The A edge set is unchanged by the loop cap. A K-only repair therefore cannot make C1 viable; the next account must also address the prediction path. The prediction-cap counterfactual shows that path responds to a lever: at loop cap 120, caps **20/40/80** move A **744 → 913 → 1,129** while K stays **1,499 → 1,498 → 1,497**. Marginal C1 passes **0 → 2 → 6 /18**, joint C1 **0 → 0 → 4 /18**; all four joint passes are larger-28, and both 16-tag blocks remain **0/6** (joint maxima **59** and **58**). A successor needs prediction capacity above 80, or an overlap repair, or both; cap 80 alone is not sufficient. The shipped cap 112 resolves larger-28 but not the 16-tag blocks: at loop cap 120 and prediction cap 112, A is **1,269**, A∩K **1,150**, and joint C1 **8/18**—**6/6** in larger-28 (minimum 60) but only **2/12** across current-16 and fresh-16 (`20630103` 60, `20650104` 63; the other ten fail with max 59). A successor can use the larger construction at this cap pair, but the 16-tag design still needs more A coverage or a different prediction selection. The cap-112 decomposition identifies the missing rows: **69** across the ten failing seeds, all support-eligible transitions, **62/69** `flip_q`; `flip_p` A rate **97.8%** vs `flip_q` **80.5%**. The design question is therefore why `flip_q` transitions rank below the 112-row window, not how to add candidate edges or lower the support floor. The cap-80 larger-28 overlap points to a second, separate repair target: all six seeds clear A, but the two joint failures (`20660102` **56**, `20660103` **51**) lose **19** and **32** A edges to K non-coverage, needing only **4** and **9** additional covered A edges. K totals are already **124** and **105** against A **75** and **83**, so the requirement is selective carrier coverage, not more K volume. A successor can repair this on the K side or by serving the K\A pools (**68/54**) into A; the decomposition does not choose between them. The selection trace locates the gates: A\K is entirely the `MAX_LOOPS=120` cutoff on the entropy-ranked loop order (all 104 edges rank 121–848), while K\A is mostly the cap-80 `transition_budget=40` cutoff (254/338 transitions rank 41–383), plus 68 below the support floor and 16 with no prediction candidate. A successor that only adds candidate edges or lowers support does not address either dominant window.

## 6. Order of operations

```text
candidate spec (no target)
        ↓
successor preflight
        ↓
   PASS ──────► new protocol → freeze → dated grant → run
        │
        └── FAIL ──► park, or a new predeclared candidate
```

A FAIL does **not** license target-selection tricks, a lower floor, a new estimator or a rerun. Those are different studies, not repairs.

## 7. What this is not

This is not a redesign, a target selection, a freeze, a grant or a run. It selects no target, reserves no seed and makes no C2/C8 or treatment claim.

## Reproduce

```bash
python -m benchmarks.a1_successor_preflight --check
python -m benchmarks.a1_successor_candidate --check
```

## References

- [Successor preflight](A1-SUCCESSOR-PREFLIGHT.md)
- [K dilution report](A1-K-DILUTION.md)
- [K-supply discriminator](A1-K-SUPPLY-DISCRIMINATOR.md)
- [Absolute-K predictors](A1-K-TOTAL-PREDICTORS.md)
- [Carrier-supply trace](A1-K-CARRIER-SUPPLY.md)
- [Loop-cap counterfactual](A1-LOOP-CAP-COUNTERFACTUAL.md)
- [C1 at loop cap 120](A1-C1-CAP120.md)
- [Prediction-cap C1](A1-PREDICTION-CAP-C1.md)
- [Prediction cap 112](A1-PREDICTION-CAP-112.md)
- [Cap-112 16-tag decomposition](A1-PREDICTION-CAP112-DECOMPOSE.md)
- [Candidate schema](A1-SUCCESSOR-SCHEMA.md)
- [Fresh-seed candidate](A1-SUCCESSOR-CANDIDATE.md)
- [Disposition memo](A1-DISPOSITION-MEMO.md)
- [Park recommendation](A1-PARK-RECOMMENDATION.md)
- [C1/C4 VOID gate](A1-C1-C4-VOID-GATE.md)
- [N20 competent rule](A1-N20-COMPETENT-SELECTION.md)
- [Pre-freeze checklist](A1-PRE-FREEZE-CHECKLIST.md)
