# Decision: C8 is adjudicated on at least N_min competent rows, not exactly N

**Date:** 2026-11-15

**ID:** `DECISION-A1-C8-NMIN-1`

**Status:** `ADOPTED BY OWNER 2026-11-15 — AT-LEAST-N_min REPLACES EXACT-N; N_min = 17 CERTIFIED; NOT FROZEN, NOT RUN`

**Scope:** the C8 competence rule only. This decision changes no threshold, freezes no manifest, reserves no seed, authorises no cell and measures no effect.

## Decision

C8 is adjudicated on any block containing at least N_min competent directed target rows; exact-N construction is preferred but not required.

N_min is 17, certified as the largest block the binding adopted seed can reach.

The threshold stays 0.05 per seed, read as the assertion rate over that seed's competent rows.

The observed row count per seed is reported with the result, and any count below 20 is named as such.

No cell is authorised by this decision.

| Element | Value |
| --- | --- |
| Unit | One competent directed target row (both baseline paths A and K present, no-arm A+K+ replay) |
| Nominal | 20 rows per seed — still preferred, and used wherever constructible |
| **N_min** | **17 rows per seed** |
| Threshold | **0.05** per seed, unchanged — the assertion rate over that seed's competent rows |
| Endpoint cap | 3 selected edges per tag, unchanged |
| Disclosure | The observed N per seed is reported with the result, and any N below 20 is named as such |

This supersedes answer 1 of [`A1-C2-C8-COMPETENCE-RULE`](A1-C2-C8-COMPETENCE-RULE.md), which read a short block as VOID. The owner's reasoning is recorded here because it is the operative one: **competence is not created or destroyed by the difference between 17 and 20 rows**, so a seed judged against the same 0.05 rate should not be inadmissible merely for being smaller — especially when smaller is *stricter*, not weaker.

## Why N_min = 17, and not 18 or 20

`N_min` is not a preference; it is the largest value every adopted seed can actually reach, and it is **certified on the binding seed rather than estimated**.

| Seed | Competent pool | Largest block | Status |
| --- | ---: | ---: | --- |
| `20740101` | 38 | 20 (21 constructible) | at least 21 |
| **`20740102`** | **27** | **17** | **exact — 18 impossible, exhaustively** |
| `20740103` | 37 | 20 (23 constructible) | exact at 23 |
| `20740104` | 40 | 20 (22 constructible) | at least 22 |
| `20740105` | 32 | 18 | at least 18; 20 not constructible by the declared rule |
| `20740106` | 31 | 20 (21 constructible) | exact at 21 |

`20740102` pools **27** competent rows over **15** tags, and **no eighteen of them satisfy the cap of 3**: all `C(27,18) = 4,686,825` subsets were enumerated and none is feasible, while seventeen exist. So the true maximum there is **17**, and no rule that includes that seed can set `N_min` above it. Seeds 101, 104 and 105 are *lower bounds* — their true maxima are at least 21, 22 and 18, possibly higher — so `N_min = 17` is set by the one seed that is proven, not by the three that are not.

**Operative block sizes under this rule** (exactly 20 where constructible, otherwise the largest the declared construction finds, provided ≥ 17): **20, 17, 20, 20, 18, 20.** `20740105` is 18 because the declared construction does not find 20 there; that is a statement about the constructor, not a proof that 20 is impossible.

## Rejected alternatives

**Keep exactly-N and treat a short block as VOID.** Rejected because it makes an 18-row block inadmissible while judging it against a stricter criterion (zero assertions tolerated against one at twenty), which is not defensible as a rule.

**Set N_min to 20.** Rejected because seed 20740102 cannot field twenty competent rows under the cap: all 4,686,825 eighteen-row subsets were enumerated and none is feasible, so its maximum is 17.

**Run whatever block the search happens to find, without a floor.** Rejected because an unfloored block lets a small block pass trivially and turns the constructor into the estimand.

## What this rule is not: "the largest block available"

The rule prefers **exactly 20** wherever constructible and falls back to the largest block the declared
constructor finds, not to the largest block that exists. The difference is measurable and would change
the operative sizes: the maxima include 21, 23, 22 and 21 on four seeds, so a "largest admissible block"
rule would score **21 / 17 / 23 / 22 / 18 / 21** rather than **20 / 17 / 20 / 20 / 18 / 20**. Tolerance
is unchanged either way (`floor(0.05 × N)` is 1 from 20 upward), but the block sizes would vary more
across seeds for no gain in resolution.

"Largest admissible" is a coherent rule. It is a *different* one, and it should be chosen explicitly
rather than inferred from this decision — the sentence to adopt is "exactly N where constructible",
which is what is written above.

## What this does to the gate, arithmetically

Tolerance is `floor(0.05 × N)`, so it does not fall as N falls — it rises as N rises:

| N per seed | Assertions tolerated | Failure condition |
| ---: | ---: | --- |
| 17 | **0** | 1 assertion (5.9%) |
| 18 | **0** | 1 assertion (5.6%) |
| 20 | 1 | 2 assertions (10%) |
| 21–23 | 1 | 2 assertions (8.7–9.5%) |

**There is no perverse incentive in this rule.** A smaller block never earns slack: at 17 and 18 rows the seed must be *perfect*, while a 20-row seed may spend one assertion. The direction of the asymmetry is conservative, and that is the property that makes at-least-N_min defensible where a "run whatever you can get" rule would not be.

## What this changes

- **C8 becomes adjudicable on the adopted block.** Under exact-N it was VOID on two seeds; under at-least-N_min all six seeds field a competent block of at least 17, so the gate can be scored everywhere — no cap change and no tag-count change required.
- **The estimand is the rate, not the block size.** C8 still reads "assertion rate over that seed's competent target rows ≤ 0.05". N is a resolution attribute of the measurement, disclosed per seed, not part of the claim.
- **The estimand's population changes once.** The filtered block replaces 14 of 24 four-row targets and, at N=20, 42 of 80 rows — already declared as a new estimand, not a repair of the representative set.

## What this does not change

The 0.05 ceiling, the 3-per-tag cap, the N=20 nominal, C1 (0.95, directed rows, C4-expanded denominator), C4 (0.05 maximum over non-target deltas), C7, the freeze, the grant, and the requirement that the selection rule and pool be recorded before the run. C8 remains `NOT ADJUDICATED` if the run VOIDs on C1/C4.

## One honesty note on the residual

Three seeds' maxima are lower bounds. That does not weaken `N_min = 17` — the binding seed is exact — but it does mean the *reported* N for those seeds depends on the constructor, and a different declared constructor could reach 20 where this one reached 18. The constructor is therefore part of the rule: sorted competent pool, deterministic hash tie-break, fixed restart budget, and exactly-20 preferred. Changing it after seeing a result would be a selection change, not an implementation detail.

## Reproduce the certification

```bash
python -m benchmarks.a1_competence_filter_draft --check     # pool sizes and cap witnesses
```

The 17-row maximum on `20740102` was certified by exhaustive enumeration over all eighteen-row subsets of its 27-row pool (`C(27,18) = 4,686,825`, none feasible); seventeen rows are witnessed by the construction the draft records. The block sizes 20 / 17 / 20 / 20 / 18 / 20 are that construction's output with exactly-20 preferred, and no engine was run.

## Consequence for the freeze chain

`C2_C8_competence_rule` is **answered** by this decision, leaving `C4_exposure_acceptance` as the only unsatisfied precondition. The two freeze acts still read `HELD ON C2/C8 COMPETENCE AND C4 EXPOSURE`; re-issuing them is a separate owner act and is **not** done here. C8 no longer blocks the freeze; C4's posture does, and its VOID probability remains unmeasured ([`A1-C4-RISK-POSTURE`](A1-C4-RISK-POSTURE.md)).
