# `DECISION-V2-FIRST-CELL` — authorise one cell of the first V2 experiment

**Status:** `DRAFT — AWAITING THE OWNER'S SIGNATURE; ONE CELL AND NO ENGINE CHANGE`

**Decision ID:** `DECISION-V2-FIRST-CELL` · **Date:** 2026-11-16
**Instruction:** draft the authorisation decision that follows the signed pre-registration, for the owner's signature
(owner, 2026-11-16).

**Narrows:** requirement 4 of [`DECISION-V2-CHARTER`](DECISION-V2-CHARTER.md), which withholds a cell until it is separately
authorised. **Leaves untouched:** every frozen engine file, every published artifact, every verdict, and requirement 5's
one-report stop.

## 1. The decision

Authorise one cell of the pre-registered first V2 experiment — ten seeds `20910101`–`20910110`, three arms on each, held-out next-edge log-loss under the pre-registered 99% paired-bootstrap rule, with `m = 2`, the pinned world, detector and log-loss instrument, and a build confined to `benchmarks/v2_first_cell_readout.py` — with no engine change, no V2 module, no promotion, no second report and no seed spent beyond that block, and with the cell refusing to run until the adapter's digest is in the scorer pin.

## 2. What the cell is, and why it is one cell

[`V2-FIRST-EXPERIMENT-PREREGISTRATION`](V2-FIRST-EXPERIMENT-PREREGISTRATION.md) is signed: the endpoint, the arms, the
`A1`–`A5` gates, `m = 2`, the world and boundary, the seed block, the readout, the revision rule and the 99% paired-bootstrap
interval are fixed, and `docs/v2_first_cell_scorer_pin.json` fixes the world generator, the detector and the log-loss
instrument. The authorisation is the only thing between that protocol and a run, and it is one cell because the charter
reports the first experiment once: a second cell would re-score a verdict that had already been delivered.

| | |
|---|---|
| Seeds | ten, `20910101`–`20910110`, paired; declared in `docs/v2_first_cell_seeds.json`, held in `docs/a1_seed_reservations.json` |
| World | `generate_compositional_world(seed, cycles=120)`, blocks `0–95` train, `80–95` calibration, `96–119` held out |
| Arms | A pair counts, B frozen membership, C maintained membership; same readout and scorer |
| Endpoint | mean paired difference in held-out next-edge log-loss, arm C − arm A |
| Decision rule | paired bootstrap over seeds, 10,000 resamples, 99% percentile, directional since Amendment 2: pass only if the interval lies entirely below zero |
| Gates | `A1`–`A5` before any arm; any failure is `VOID` |
| Build | one new module, `benchmarks/v2_first_cell_readout.py`, written and pinned by digest before this decision |
| Stop | one report; the charter closes, pass or fail |

## 3. What this decision does not authorise

No engine change, no change to the pinned modules, no new V2 module beyond the one readout adapter, no promotion, no
extension of the first report, and no seed beyond the declared block. It does not adopt the primitive, does not amend
`m`, and does not permit a second experiment. The seeds stop being *held* and become *spent* when this decision is
signed; the adapter is already pinned.

## 4. Alternatives rejected

| Alternative | Why not |
|---|---|
| Run the cell without a signed pre-registration | The endpoint and `m` would be chosen after the first look, which is the failure the pre-registration exists to prevent. |
| Authorise the build without a cell | An open-ended build has no stop condition and would become the phase the charter forbids. |
| Authorise more than one cell | The charter reports the first experiment once; a second cell would re-score a verdict already delivered. |
| Settle the scorer or the β grid during the run | A scorer chosen after seeing held-out data is not a scorer, and the baseline would be tuned against the test. |
| Authorise an engine change at the same time | It would confound the cell: a changed substrate cannot be compared with the pinned one. |

## 5. Evidence

- [`V2-FIRST-EXPERIMENT-PREREGISTRATION`](V2-FIRST-EXPERIMENT-PREREGISTRATION.md) — the signed protocol.
- [`v2_first_cell_seeds.json`](v2_first_cell_seeds.json) — the declared block.
- [`v2_first_cell_scorer_pin.json`](v2_first_cell_scorer_pin.json) — the pinned modules and the adapter rule.
- [`V2-MUTABLE-IDENTITY-SPEC`](V2-MUTABLE-IDENTITY-SPEC.md) §8 — the earning test and the `I1`–`I5`/`M1`–`M5` battery.
- [`DECISION-V2-PRIMITIVE-RESOLUTIONS`](DECISION-V2-PRIMITIVE-RESOLUTIONS.md) — the adopted content of requirement 6.
- [`V2-PRIMITIVE-SIZING`](V2-PRIMITIVE-SIZING.md) — `m = 2` at 135,168 bytes, 2.538× the pair tables.
- [`CODE-AS-EVIDENCE`](CODE-AS-EVIDENCE.md) §6 — the three measured absences the arms separate.
- [`V1-REKEYING-TWO-SEEDS`](V1-REKEYING-TWO-SEEDS.md) — two worlds replicate the sign, not the magnitude.

## 6. Signature

**Unsigned.** Signing spends the seed block and authorises the cell; the signature line records the owner, the date, and the
commit that adds the adapter's digest to the scorer pin.

| | |
|---|---|
| **Owner** | _unsigned_ |
| **Status** | _unsigned_ |
| **Date** | _unsigned_ |
