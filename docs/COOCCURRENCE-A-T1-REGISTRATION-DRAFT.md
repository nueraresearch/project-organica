# Registration and grant — draft for the (a)+T1 co-occurrence build

**Status: signed 2026-11-20 — floor 35.** The two objects below are written as
[`constraint_registrations/CONSTRAINT-COOCCURRENCE-A-T1.json`](constraint_registrations/CONSTRAINT-COOCCURRENCE-A-T1.json)
and [`COOCCURRENCE-A-T1-GRANT.json`](COOCCURRENCE-A-T1-GRANT.json), the ledger row is appended
`in-test`, and the seed block is reserved. No cell has run. The decision it implements is recorded in
[`constraint_decisions/DECISION-COOCCURRENCE-BUILD.json`](constraint_decisions/DECISION-COOCCURRENCE-BUILD.json)
and the terms come from [`COOCCURRENCE-A-T1-MEMO.md`](COOCCURRENCE-A-T1-MEMO.md).

## 1. What the successor constraint says

K1 was retired as an invalid attempt: its registered endpoint asserts all eighteen gold pairs, so
recall is already at its ceiling and its intervention could only add false assertions. This
constraint names the deficit the 0.15.0 replication actually has — the served path keeps false pairs
and drops gold ones — and intervenes there.

- **Constraint id:** `CONSTRAINT-COOCCURRENCE-A-T1-1`, ledger row `K1S - support-gated co-occurrence admission`.
- **Hypothesis:** the K1 deficit is candidate admission, not pair content. Admitting a temporal pair
  only when its within-event co-occurrence count reaches a high floor should retain all eighteen gold
  pairs and serve almost nothing else.
- **Intervention:** `_build_predictions` only. Admit by support at the granted floor `F`; serve one
  ranked list; no partition, no backfill, no frozen-engine edit.
- **Endpoint:** the per-seed paired K1 difference (Organica minus the strongest-of-grid baseline)
  under 0.16.0, minus the 0.15.0 value, with 98.33% intervals; precision and recall beside it.
- **Claim ceiling T1:** an improvement over 0.15.0 of at least 0.10 F1. Not a win over the comparator.

## 2. The floor: 44 or 35

`F* = 44` is the largest recall-preserving floor on the ten committed seeds — the pooled gold
minimum, which seed `20261028` attains exactly. The memo allows the grant to carry explicit
fresh-seed margin below it. On the measured curves the two candidates are:

| Floor | `M` on the ten seeds | directed admitted | fresh-seed margin | band 18–69 |
|---|---|---|---|---|
| **44** | 19, 20, 19, 19, 21, 21, 18, 20, 19, 20 | 36–42 | **0 counts**: `20261028`'s tightest gold pair is exactly 44 | clears both edges |
| **35** | 21, 22, 23, 22, 22, 24, 24, 23, 23, 23 | 42–48 | **+9 counts** on every seed (gold minima 44–55) | clears both edges |

The band is slack either way, and the memo now says why: at `F*` the band cannot fail, since `M ≥ 18`
by the definition of `F*` and `M ≤ 24` because only 24 pairs co-occur. So a higher floor buys no band
safety — it buys a tighter filter, and it spends all the fresh-seed margin at the same time. A new
seed whose tightest gold pair falls one count below `F*` is VOID under liveness, not a null result.

**Chosen: 35.** It keeps every measured property, adds nine counts of margin against the
only failure mode the preflight did not rule out, and leaves the served set at 21–24 pairs — three at
most above the band floor and 45 below its ceiling.

**What the block can and cannot show — arithmetic, not a result.** With recall at 1 and every
admitted pair served, F1 is `36 / (M + 18)`: 0.857 at `M = 24`, 0.923 at `M = 21`, 1.000 at
`M = 18`. Against the pooled strongest-of-grid 0.936, that is a gap of −0.079 to +0.064 and an
improvement over the 0.15.0 gap of +0.545 to +0.611 — past the 0.10 pass line at either floor, before
any cell runs, if the fresh seeds' counts and comparator resemble the committed ten's. The block
therefore confirms the count and tests fresh-seed liveness; it is not a discriminating test of the
band. That is a reason to keep the block cheap (20 cells) and the floor safe, not a reason to skip it.

## 3. The reserved seeds

`20261300, 20261301, 20261302, 20261303, 20261304, 20261305, 20261306, 20261307, 20261308, 20261309`

- **Repo guard.** `benchmarks.presence_cap_experiment.seed_collisions` over `docs/*.json` returns no
  collision for any of the ten.
- **Wider scan.** Every `.json`, `.md`, `.txt`, `.py`, `.cff` and `.toml` file in the repository
  (409 distinct seed-like eight-digit values, 112 of them 2026-prefixed) names none of the ten.
- **Position.** The block sits above the highest contiguous committed block, `20261023–20261229`,
  and is disjoint from every value in the scan.
- **Discipline.** The treatment arm spends these ten; the reproduction arm uses only the committed
  ten `20261023–20261032`; the preflight and the reproduction control spend no fresh seed.

## 4. The registration object

To be written as `docs/constraint_registrations/CONSTRAINT-COOCCURRENCE-A-T1.json`.

```json
{
  "kind": "constraint_registration",
  "id": "CONSTRAINT-COOCCURRENCE-A-T1-1",
  "constraint": "K1S - support-gated co-occurrence admission",
  "status": "registered",
  "status_date": "2026-11-20",
  "intervention": "_build_predictions admits a temporal pair only when its within-event co-occurrence count is at least the floor F fixed in the grant; one ranked list; no partition, no backfill, no frozen-engine edit.",
  "endpoint": "per-seed paired K1 difference (Organica minus the strongest-of-grid baseline) under 0.16.0 minus its 0.15.0 value, with 98.33% intervals; precision and recall beside it",
  "comparator": "strongest-of-grid simple baseline, best configuration per seed",
  "seed_block": "successor block 20261300-20261309 (treatment) + Phase K K1 seeds 20261023-20261032 (reproduction control)",
  "decision_threshold": {
    "pass": "The K1 paired difference improves by at least 0.10 relative to the 0.15.0 same-build -0.623961 gap, and the K2 and K3 paired differences change by no more than 0.05 absolute.",
    "fail": "K1 improves by less than 0.05, or a guard family changes by more than 0.05 absolute.",
    "inconclusive": "K1 improvement is between 0.05 and 0.10, or the registration's audit/validity condition fails."
  },
  "threshold_values": {
    "baseline_gap": -0.623961,
    "pass_min_improvement": 0.10,
    "pass_max_k1_abs_change": 0.05,
    "fail_below_improvement": 0.05,
    "inconclusive_min_improvement": 0.05,
    "inconclusive_max_improvement": 0.10
  },
  "threshold_rule": "These are pre-registered provisional thresholds, not values estimated from the intervention run. baseline_gap is the 0.15.0 same-build K1 replication value, not 0.9.0's -0.3437. Improvement is the post-intervention K1 difference minus baseline_gap.",
  "guard": "recall >= 0.95 on every seed and no gold pair dropped; K2 and K3 absolute paired differences change by <= 0.05.",
  "liveness": "Every seed serves fewer than 70 pairs; the floor removes at least one candidate; all eighteen gold pairs are retained on every seed; otherwise VOID.",
  "claim_ceiling": "T1: an improvement over 0.15.0 of at least 0.10 F1; not a win over the strongest-of-grid comparator.",
  "preflight": "docs/COOCCURRENCE-A-T1-MEMO.md, 2026-11-19, ten committed K1 seeds: F* = 44, M 18-21, directed admitted 36-42, 24 co-occurring pairs against 120 unordered temporal pairs; PASS. NOT A RESULT.",
  "grant": "docs/COOCCURRENCE-A-T1-GRANT.json",
  "does_not_allocate": "This registration allocates no seed, cell or result. The owner's grant of 2026-11-20 fixes the floor, names the ten fresh seeds and authorises the 20 cells; no cell may run without it."
}
```

## 5. The grant object

Written as `docs/COOCCURRENCE-A-T1-GRANT.json`. `block.floor` is **35**, the owner's choice on
2026-11-20; `44` was the alternative.

```json
{
  "kind": "cooccurrence_block_grant",
  "grant_id": "COOCCURRENCE-A-T1-2026-11-20",
  "granted_on": "2026-11-20",
  "granted_by": "owner",
  "authorizes": "cooccurrence-a-t1-block",
  "block": {
    "engine": "0.16.0",
    "change": "_build_predictions only: admit a temporal pair when its within-event co-occurrence count is at least the floor; serve one ranked list; no partition, no backfill, no frozen-engine edit",
    "allocation_law": "a",
    "term_sheet": "T1",
    "floor": 35,
    "seeds_treatment": [20261300, 20261301, 20261302, 20261303, 20261304, 20261305, 20261306, 20261307, 20261308, 20261309],
    "seeds_reproduction": [20261023, 20261024, 20261025, 20261026, 20261027, 20261028, 20261029, 20261030, 20261031, 20261032],
    "cycles": 300,
    "scale": 1,
    "workers": 8,
    "cells": 20
  },
  "cells_arithmetic": "20 = 10 treatment (0.16.0 x fresh seeds) + 10 reproduction (0.15.0 x committed seeds).",
  "readout": "per-seed paired K1 difference (Organica minus strongest-of-grid) under 0.16.0 minus its 0.15.0 value; 10,000 bootstrap replicates; 98.33% intervals; precision and recall beside it; the strongest-of-grid comparator reported per seed",
  "thresholds": {
    "baseline_gap": -0.623961,
    "pass_min_improvement": 0.10,
    "pass_max_k1_abs_change": 0.05,
    "fail_below_improvement": 0.05,
    "inconclusive_min_improvement": 0.05,
    "inconclusive_max_improvement": 0.10
  },
  "guards": "recall >= 0.95 on every seed and no gold pair dropped; K2 and K3 absolute paired differences change by <= 0.05",
  "liveness": "every seed serves fewer than 70 pairs; the floor removes at least one candidate; all eighteen gold pairs are retained; otherwise VOID and no criterion is read",
  "claim_ceiling": "T1: an improvement over 0.15.0 of at least 0.10 F1; not a win over the strongest-of-grid comparator",
  "execution": "one block, no re-execution, no mid-block change of law or floor; the reproduction arm uses the committed ten only"
}
```

## 6. The ledger row

To be appended to `docs/bottleneck_map.json` → `constraint_ledger.rows`. It stays `open` until the
grant exists; the grant moves it to `in-test`, and K3's row is open but not in test.

```json
{
  "constraint": "K1S - support-gated co-occurrence admission",
  "evidence": "K1 retired as an invalid attempt (cells_started 0). 0.15.0 same-build replication: Organica 0.3120 vs strongest-of-grid 0.9360; difference -0.623961 [-0.646675, -0.599907]; 10/10 per-seed differences negative. Preflight 2026-11-19 on the ten K1 seeds: 120 unordered temporal pairs, 24 carrying within-event co-occurrence; F* = 44, M_s(F*) 18-21. NOT A RESULT.",
  "hypothesis": "The K1 deficit is candidate admission, not pair content: the served-path rules keep false pairs and drop gold ones, and admitting strictly by within-event support at a high floor serves all eighteen gold pairs with few decoys.",
  "intervention": "Engine 0.16.0: _build_predictions admits a temporal pair when its co-occurrence count is at least the granted floor F, serves one ranked list, no partition or backfill, no frozen-engine edit.",
  "decision_rule": "PASS: the K1 paired difference improves by at least 0.10 relative to -0.623961 while the K2 and K3 paired differences change by no more than 0.05 absolute. FAIL: less than 0.05, or a guard family changes by more than 0.05. INCONCLUSIVE: between 0.05 and 0.10, or the audit/validity condition fails.",
  "state": "open",
  "registration": "docs/constraint_registrations/CONSTRAINT-COOCCURRENCE-A-T1.json"
}
```

## 7. What must exist before a cell can run

1. The owner's floor (`35` or `44`) and date written into the two objects above, the objects written
   as files, and the ledger row appended as `in-test`.
2. Engine 0.16.0 built from the `_build_predictions` change, `CHANGELOG` entry, `python -m
   benchmarks.engine_pin` re-pin.
3. Nothing else: the decision is recorded, the preflight passed, and the seed block is scanned.

**Proposed addition — not a settled term.** The reproduction arm could serve as the control that the
0.15.0 gap has not drifted: if it did not reproduce `-0.623961` within its interval, the block would
be VOID before the treatment arm is read. That rule is **not** in either object above — the grant's
`liveness` string carries only the three floor conditions — so it is a proposal for the owner to
adopt or drop, not a term of the signed block — the 2026-11-20 signature did not adopt it. Adopting
it later means adding the condition to `block.liveness`, or to a separate `reproduction_control`
field so the two VOID conditions stay distinguishable.
