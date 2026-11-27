# Stage B — seed-allocation record for the 0.16.0 build

**Status: DRAFT — AWAITING OWNER SIGNATURE. NOTHING IS ALLOCATED, NO CELL HAS RUN, AND NO SEED
HAS BEEN DRAWN BY THIS DOCUMENT.**

**Dated:** 2026-11-24. **Prepared by:** the agent, at the owner's request. **The decision is the
owner's; the wording of this record is not.** This is the record the owner signs; the machine file a
runner reads is a separate dated artifact (see §7).

**Build under allocation:** engine **0.16.0**, commit `716da31be3f304715c3ecbd4063dcac44abb54e1`,
engine SHA-256 `25843ded68f50e90ad04bd80df4ade86f57d31eb7ed61ef77d6d7f4fedfe4236`. A different engine
byte or commit voids this allocation and needs a new signature.

---

## 1. What is being allocated, and what the block's status actually is

The reserved block is **724 integers, `700000001`–`700000724`** — chosen as one plain block before
any Stage B world, so that no value reads as a calendar date.

| range | count | status on 2026-11-24 |
| --- | --- | --- |
| `700000001`–`700000180` | 180 | **spent** — `2:1`, 2026-11-04 block |
| `700000181`–`700000360` | 180 | **spent** — `3:1`, 2026-11-04 block |
| `700000361`–`700000540` | 180 | **spent** — `4:1`, 2026-11-04 block |
| `700000541`–`700000720` | 180 | **spent** — `6:1`, 2026-11-04 block |
| `700000721`–`700000724` | 4 | **never drawn** — spares, reserved |

**The 720 pre-assigned seeds are not fresh.** They were allocated on **2026-11-03**
(`docs/stage_b_allocation.json`) and spent by the block that ran on **2026-11-04**: 720 cells, **587
scored**, verdict **`NOT SUPPORTED`** in all four configurations (`docs/stage_b_results.md`). The
owner's decision of 2026-11-04 (`DECISION-STAGE-B-SEQUENCE.md` §D14) records that all 720 remain
spent and that a repeat on the same clock is not authorised.

So this record asks for something specific and narrow: **a second use of integers already spent, on
a different instrument.** Signing it is what authorises that re-use. Three consequences are part of
the record and not of the fine print:

1. **The 0.9.0 block stands.** Its allocation, its cells, its verdict and its result page are not
   re-scored, rescored, merged, replaced or withdrawn. `docs/stage_b_allocation.json` is **not
   overwritten**: the signed 0.16.0 record is written to its own path (§7).
2. **This is not a replication.** `DECISION-STAGE-B-SEQUENCE.md` §D15 already rules that a later
   engine may not be used to produce "the same" block: a different engine is a different measurement
   instrument and needs its own pre-registration. The 0.16.0 block is named *the 0.16.0 block*; its
   result may be compared to the 0.9.0 result and may not be presented as reproducing it.
3. **The four spares do not make this a fresh block.** Four seeds cannot carry a 180-per-
   configuration conjunction. This record does not draw them, and substitution remains closed: a
   censored world releases its seed to no one.

## 2. Cost, restated before anything is allocated

### 2.1 Plan arithmetic

| quantity | value | source |
| --- | --- | --- |
| worlds | **720** (180 per configuration) | `docs/stage_b_protocol.json` → `sample_size` |
| median horizon by configuration | `2:1` **649**, `3:1` **514**, `4:1` **472**, `6:1` **439** cycles | `stage_b_protocol.json` → `clock.median_horizon_by_config_cycles` |
| total cycles at those horizons | **373,320** | `stage_b_protocol.json` → `cost.cycles_total` |
| bound if every world ran 600 cycles | **144,000** | `stage_b_protocol.json` → `cost.cycles_if_every_world_ran_600` |
| relative to Phase L | **2.5925×** | `stage_b_protocol.json` → `cost.relative_to_phase_l` |

### 2.2 Measured rate, and the two committed totals

`docs/stage_b_cost_estimate.json` measures **10 design-block cells** at
**0.235431–0.318279 s/cycle** (mean **0.286542**) and reports **29.14 serial hours**
(23.94–32.37), or **3.67 wall hours on eight workers** at the measured two-worker efficiency of
0.994. Its cycle total is **366,120**, from per-world counts of 639 / 504 / 462 / 429.

**The two committed totals differ by 7,200 cycles and the difference is not a re-measurement.** It is
the horizon set: the protocol multiplies its median horizons (649/514/472/439) by 180, and the cost
estimate multiplies the per-world counts it was built from (639/504/462/429) by 180. This record does
not silently choose one. Restated at 373,320 cycles the measured rate gives **24.4–33.0 serial
hours** (29.7 at the mean, 3.7 on eight workers); at 366,120 it gives the committed 29.14 / 3.67.

### 2.3 What the cost is not

- **It is not measured on 0.16.0.** Both the rate check and the estimate predate this build and carry
  **no engine stamp** (`engine_version` is absent from both artifacts). The 0.16.0 pipeline is not the
  pipeline those ten cells ran.
- **It is planning-only and wall-clock only.** No monetary cost is claimed, no cluster is named, and
  the estimate's own assumptions say the per-cycle rate is measured from one configuration and that
  wall clock assumes linear speedup with no I/O contention.
- **It must be re-measured before the first cell**, with the runner's own `--rate-check` and
  `--estimate` on this build. Until then the honest restatement is a range: **≈24–33 serial hours,
  ≈3.7–7.3 wall hours at 8/4 workers, 373,320 cycles at the protocol's horizons.**

## 3. The reliability assumption, restated

**Reliability is not measured.** The engine is deterministic per seed, so re-running a world is not a
replication and no test-retest estimate exists (`stage_b_protocol.json` →
`sample_size.reliability_measured: false`). The block is sized at a **declared planning assumption of
ρ = 0.50**, and `planning_assumption_is_established_lower_bound` is **false**.

| assumed reliability ρ | observed effect (Spearman) | worlds per configuration (ladder) |
| --- | --- | --- |
| 1.00 | 0.500 | 48 |
| 0.90 | 0.474 | 54 |
| 0.80 | 0.446 | 62 |
| 0.70 | 0.417 | 72 |
| 0.60 | 0.386 | 85 |
| **0.50 (declared)** | **0.352** | **104** |
| 0.40 | 0.314 | 131 |
| 0.30 | 0.272 | 177 |

**The block is 180, not 104, and the difference is the conjunction.** The claim is that the relation
holds in **every** claimed configuration, so the block is the smallest tested size whose lower 95 %
Monte-Carlo bound on the four-configuration conjunction clears the 0.90 bar:

| size | per configuration | conjunction | lower bound | clears |
| --- | --- | --- | --- | --- |
| 150 | 0.9750 | 0.9037 | 0.8470 | no |
| 160 | 0.9775 | 0.9130 | 0.8588 | no |
| **180** | **0.9975** | **0.9900** | **0.9706** | **yes — smallest tested** |
| 200 | 0.9950 | 0.9801 | 0.9531 | yes |

Three limits are stated rather than left implicit:

- **ρ = 0.50 is the worst instrument the claim could survive, not a measured floor.** At ρ < 0.50 the
  conjunction is weaker than 0.9706 and **is not re-derived here**. The ladder's 177 worlds at ρ = 0.30
  fits inside 180, but that is a per-configuration count, not the conjunction gate.
- **A null result under a lower true reliability is not evidence of absence.** If the relation is
  absent on 0.16.0, the reading is bounded by this assumption, not licensed past it.
- **200 is not smaller and its bound is lower than 180's** — Monte Carlo, not a monotone curve. 180 is
  selected by the pre-declared rule, not by preferring a round number.

## 4. What this record does not restate, because it is the protocol's

The hypothesis, the predictor (confirmed onset of `DI`), the endpoint (`revision_held_out`), the
eligibility rule (`onset + 101 ≤ horizon`), the falsifiers, the outcomes table and the analysis are
frozen in `docs/STAGE-B-PROTOCOL.md` and `docs/stage_b_protocol.json`. This record changes **no**
parameter in them. Two inherited facts the owner should have in view:

- **The `2:1` shortfall is a property of the 0.9.0 clock and build.** That block scored 47 of 180
  `2:1` worlds; a repeat on the same clock reproduced that fraction by construction (§D14). The
  0.16.0 onset distribution is **unmeasured**, so the scoreable fraction of each arm on this build is
  unknown until the block runs — it is not carried over from the 0.9.0 block.
- **The 0.05-nat effect gap is a model, not an identity** (linear in standardised units, across-world
  SD 0.05). Authorising the block does not make it an identity.

## 5. What the signature authorises

Signing this record authorises **only**:

1. The **720 pre-assigned seeds** `700000001`–`700000720`, 180 per configuration, to be spent by a
   Stage B block on the **0.16.0 build named above** — as a second use of spent integers, named the
   **0.16.0 block**.
2. That block's cells to be run against the frozen protocol's predictor, endpoint, eligibility rule
   and analysis, unchanged.
3. The four spares `700000721`–`700000724` to stay **undrawn**, with substitution **closed**.

It authorises **no cell by itself**: allocation is permission, and the first cell remains a separate
deliberate invocation of the runner.

## 6. What the signature does not do

- It does not run anything, generate a world, or spend a seed.
- It does not re-score, replace, merge with, or replicate the 0.9.0 block, and it does not reopen its
  `NOT SUPPORTED` verdict.
- It does not answer eligibility for any configuration, does not make ρ = 0.50 an established lower
  bound, and does not make the 0.05-nat gap an identity.
- It does not authorise a second block, a re-centred clock, a new endpoint, an engine change or a
  version bump. A re-centred clock is a new pre-registration with its own allocation (§D14).
- It does not authorise the four spares under any circumstance in this record.

## 7. What must be true before the first cell — build, not number

These are preconditions, not parameters, and none of them is satisfied by signing:

1. **The machine record exists at its own path.** This signed document is written as
   `docs/stage_b_allocation_0.16.0.json` with `allocated: true` and the 720 seeds, and the 0.9.0
   `docs/stage_b_allocation.json` is left untouched. The runner currently reads only the 0.9.0 path;
   pointing it at the 0.16.0 record is a code change made **after** signature, and until it exists
   the allocation cannot spend a seed.
2. **A preflight on this build.** `benchmarks.stage_b_runner --self-test` passes, and one consumed
   design-block seed demonstrates that the withholding world, the confirmed-onset predictor and the
   `revision_held_out` endpoint run on 0.16.0. A design-block cell is smoke, not a Stage B cell.
3. **A measured cost on this build.** `--rate-check` and `--estimate` are re-run on 0.16.0 so the cost
   in §2 is measured rather than inherited from cells that predate the build.
4. **The protocol's status block stops saying "NOT RUN".** `docs/stage_b_protocol.json` and
   `docs/STAGE-B-PROTOCOL.md` currently carry `seeds_allocated: 0`, `worlds_run: 0` and "No
   confirmatory Stage B world has run", which the 2026-11-04 block already contradicts. That is a
   factual correction owed whether or not this allocation is signed.

## 8. Signature

I allocate the 720 pre-assigned seeds `700000001`–`700000720` to the Stage B **0.16.0** block, 180
per configuration, at the restated cost in §2 and under the reliability assumption in §3, with the
four spares `700000721`–`700000724` undrawn and substitution closed. I have read §1: this is a second
use of seeds the 2026-11-04 block spent, on a different engine, and it is not a replication of that
block.

**Signed:** ______________________________  **Date:** ________________

**Repository owner**

---

## Appendix — provenance of every number restated here

| claim | artifact |
| --- | --- |
| block shape, pre-assignment, spares, substitution | `docs/stage_b_protocol.json` → `seeds` |
| 0.9.0 allocation and its date | `docs/stage_b_allocation.json` |
| 720 cells, 587 scored, `NOT SUPPORTED` | `docs/stage_b_runner.json`; `docs/stage_b_results.md` |
| 720 remain spent; repeat not authorised | `docs/DECISION-STAGE-B-SEQUENCE.md` §D14 |
| later engine is a different instrument | `docs/DECISION-STAGE-B-SEQUENCE.md` §D15 |
| horizons, 373,320 cycles, 2.5925× | `docs/stage_b_protocol.json` → `clock`, `cost` |
| 366,120 cycles, 0.286542 s/cycle, 29.14 h | `docs/stage_b_cost_estimate.json` |
| measured rate ranges and non-proportionality | `docs/stage_b_rate_check.json` |
| reliability 0.50, ladder, conjunction rows | `docs/stage_b_protocol.json` → `sample_size` |
| frozen hypothesis, endpoint, eligibility | `docs/STAGE-B-PROTOCOL.md` §§1–4 |
| build identity | `docs/stage_b_protocol.json` → `engine_version`, `engine_commit`, `engine_sha256` |
