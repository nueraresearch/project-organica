# V2 first experiment — pre-registration

**Status:** `SIGNED 2026-11-16 — THE PROTOCOL IS FIXED; NO CELL IS AUTHORISED`

**Serves:** requirements 2 and 7 of [`DECISION-V2-CHARTER`](DECISION-V2-CHARTER.md) (adopted 2026-11-16), and requirement 6's
acceptance tests. **Authorises:** nothing — no cell, no module, no engine change and no spending until
[`DECISION-V2-FIRST-CELL`](DECISION-V2-FIRST-CELL.md) is signed. The seeds are *held*, not spent.

## 1. What this document fixes

A pre-registration is only worth what it fixes *before* a result is seen. This one fixes the endpoint, the failure rule, the
arms, the gate order, the admission threshold `m`, the world and boundary, the seed block, the readout, the revision rule, the
interval method and the scorer pin. It was signed on 2026-11-16, before any cell ran and before any readout existed.

One thing is deliberately **not** fixed here, because it is not this document's to fix: the authorisation itself (a
separate decision). The readout adapter is written and its digest is in the scorer pin; an amendment below records the one
protocol change the dry run forced, made before any cell and before any observation.

## 2. The one question

> Does a composition-bearing object with a content-free id and a membership mutation predict held-out edges better than the
> same atoms' pair counts — and if it does not, is that the charter's answer?

This is the charter's diagnosis, made falsifiable: V1 has no addressable handle on what it stores, so an object that can be
named and revised should buy prediction that the counts alone do not. "Should" is the hypothesis; the counts are the
comparator.

## 3. The failure criterion, fixed

From requirement 7 and [`V2-MUTABLE-IDENTITY-SPEC`](V2-MUTABLE-IDENTITY-SPEC.md) §8.3:

> **If the prediction arm's interval includes zero, the primitive is bookkeeping and the charter fails at its first
> experiment.** The test is directional: the charter passes only when the interval lies entirely **below** zero, and an
> interval entirely above zero is a reversal that fails it too (Amendment 2).

That is the whole criterion, and it is one endpoint. A tie is a result. Adding features to rescue it, re-reading the
endpoint, or reporting a secondary measure as the headline are protocol violations, not judgement calls. This document also
inherits the discipline that a `VOID` stops interpretation before any effect is quoted (requirement 4).

## 4. The arms, fixed

| Arm | Primitive | Readout | What it isolates |
|---|---|---|---|
| **A — baseline** | none | pair counts only | the comparator the charter names |
| **B — label** | content-free ids, membership **frozen** at admission | the same readout as C | whether an id alone buys anything |
| **C — address** | content-free ids and **maintained** membership (§7.4) | the same readout | whether revision buys anything over a label |

All three arms share the world, the cycle schedule, the caps, the scorer and the seed. The only difference is the primitive
binding. Arm B exists because the code reading found three separate absences — a content-free id, a membership mutation and a
consumer — and an experiment that adds all three at once cannot say which one paid
([`CODE-AS-EVIDENCE`](CODE-AS-EVIDENCE.md) §6).

## 5. The admission threshold: `m` is fixed here

> **`m = 2`, fixed in this section at signing, before any cell runs.**

`m` is a count of **total appearances** of a canonical key, one appearance per sleep cycle at most. The value is fixed *here*
and nowhere else: the charter's requirement 6 delegates it to this pre-registration, the resolutions decision adopts the rule
but not the value, and an implementation constant is not a policy.

**Why 2.** It is the smallest value that excludes singletons, and it retains the largest admissible population: on the
measured world it admits **115 of 158** canonical node sets (**72.8%**), **345** member references, at **135,168 bytes** —
**2.538×** the pair tables and **0.698%** of the 19,374,080-byte store
([`V2-PRIMITIVE-SIZING`](V2-PRIMITIVE-SIZING.md); artifact `docs/v2_primitive_sizing.json`).

The higher thresholds are recorded so the choice is visible, not so it can be revisited after a result:

| Threshold | Composites admitted | Primitive bytes |
|---|---|---|
| `m >= 2` | 115 | 135,168 |
| `m >= 3` | 97 | 90,112 |
| `m >= 5` | 66 | 73,728 |
| `m >= 10` | 33 | 53,248 |
| `m >= 20` | 20 | 45,056 |

**Changing `m` after this pre-registration is signed is a new pre-registration.** It voids any cell already run under this
one, because the population that cell measured would no longer be the population this document defines. The first experiment
uses `m = 2` or it is not this experiment.

## 6. Requirement 6's acceptance tests, fixed

These gates come **before** any behavioural arm, and each one is a `VOID` if it fails. A partial pass is not a pass.

| Gate | What must hold | How it is checked |
|---|---|---|
| **A1 — canonicalisation** | On the experiment's own detections, the direction-free key yields exactly the distinct node-set count, no key maps to two different node sets, and a direction flip does not change the id. The two development worlds are the regression: 177 → 158 with multiplicities `{1: 139, 2: 19}`, and 138 → 125. | the identity artifact plus a replay of the experiment's detection stream |
| **A2 — identifier invariants** | `I1` the id is stable across versions, member changes and flips; `I2` it is not a function of the members; `I3` ids are never reused after retirement and a retired id resolves to a tombstone; `I4` retrieval accepts the id only; `I5` `(id, version)` names a state while `id` names the object. | the specification's named tests, each built to fail first |
| **A3 — mutation invariants** | `M1` a mutation touches only its own composite's rows; `M2` atoms are immutable, so no shared count or binding moves; `M3` the change is atomic and versioned, and a stale version is rejected; `M4` retirement writes a tombstone and preserves the id; `M5` the frozen graph stays read-only. `M1`, `M2` and `M5` carry a bystander composite as the control. | the specification's named tests, with the bystander asserted byte-identical |
| **A4 — cost** | At `m = 2` the primitive is at most **135,168 bytes** on the base world, with no per-mutation history table, and compaction restores every live composite's resolved member set exactly. | page-count measurement on a rebuilt store; before/after resolution comparison |
| **A5 — determinism** | The same detections produce the same keys, the same member resolutions and the same allocation order on a replay; ids are monotonic and retirement never frees one. | two replays of the same stored stream, compared |

`A1` has one deliberate asymmetry: the exact numbers 177 → 158 and `{1: 139, 2: 19}` are a **regression on the measured
store**, while the experiment's own world must satisfy the **invariant** (keys = distinct node sets, no cross-node-set merge,
multiplicity at most 2 for `cycle3`). A new world is allowed different numbers; it is not allowed a key that mixes two node
sets.

## 7. The behavioural cell, fixed

### 7.1 Seeds and pairing

**Ten seeds, `20910101`–`20910110`**, declared in [`v2_first_cell_seeds.json`](v2_first_cell_seeds.json) and held in
`docs/a1_seed_reservations.json`. One world per seed; all three arms run on that world; comparisons are paired by seed. The
block is *reserved*, not spent, until the authorisation decision is signed.

### 7.2 World and boundary

The measured compositional family: `generate_compositional_world(seed, cycles=120)` with default events per cycle and no
held cell. The boundary is expressed in **blocks**, not sleep cycles, because a block whose last event is skipped never runs a
sleep cycle (92 of 120 in the measured replay) and a boundary in sleep cycles would move with the seed.

- **Training:** blocks `0–95`.
- **Calibration:** blocks `80–95` — used only to select `β`; counts for calibration scoring come from blocks `0–79`.
- **Held out:** blocks `96–119`, scored once, with every model frozen at the end of block 95.

### 7.3 The readout, fixed

For consecutive events `e_t, e_{t+1}`, the asserted edges are `(u, v)` with `u ∈ tags(e_t)`, `v ∈ tags(e_{t+1})`, `u ≠ v`.
The vocabulary `V` is every tag seen in training. Held-out tags outside `V` are reported as a novelty diagnostic and never
scored. Log-loss per event is the mean over source tags in `e_t` and targets in `V` with `y = 1[v ∈ tags(e_{t+1})]`,
reusing `benchmarks/heldout_prediction.py::_score`; `p` is clipped to `[1e-9, 1 − 1e-9]`.

Counts are frozen from the training blocks. For each arm:

- **Arm A:** `p_uv = (n_uv + α) / (n_u + α·|V|)`.
- **Arms B and C:** `p_uv = (n_uv + α + β·c_uv) / (n_u + α·|V| + β·Σ_w c_uw)`, where `c_uv` is the number of admitted
  composites that contain the edge `(u, v)` as a member — frozen at admission for B, maintained by §7.4 for C.

`α = 0.5` (the value the existing instrument uses). `β` is selected **per arm** from the grid `{1, 2, 4, 8}` — zero excluded since Amendment 1 — on the
calibration blocks by that arm's own calibration log-loss, so the baseline is not handicapped; the selected `β` is recorded
and applied unchanged to the held-out blocks. Arm A selects no `β` (its readout has no membership term).

### 7.4 The revision rule for arm C, fixed

At the end of each training block, every admitted composite's member set is the set of its member edges that meet `m`
appearances in a trailing window of **20 sleep cycles**; edges below `m` are removed and edges that close the cycle and meet
`m` are added. Every change increments the version through `add_member`/`remove_member` and **never** changes the id. Arm B
freezes the member set at the first block in which all three members met `m`. The rule lives in the readout harness, not in
the engine; the primitive supplies only the mutation operations, and the harness reports the number of mutations per seed as a
diagnostic, not a criterion.

### 7.5 The interval and the decision, fixed

For each seed `s`, `d_s = L_C(s) − L_A(s)` is the difference in held-out log-loss. The endpoint is the mean of `d_s`. The
interval is a **paired bootstrap over seeds** — 10,000 resamples, 99% percentile — because the world is the unit of inference;
resampling events would multiply n without adding a world. With ten seeds this interval is deliberately wide, which makes a
pass harder, not easier. **The charter passes only if the interval lies entirely below zero**; an interval including zero fails, and so does one entirely above it (§3, Amendment 2). Two diagnostics are recorded beside the rule and neither is a criterion: the null-world false-pass rate
([`V2-FIRST-CELL-NULL`](V2-FIRST-CELL-NULL.md)), the power curve at that noise
([`V2-FIRST-CELL-POWER`](V2-FIRST-CELL-POWER.md)), the handicap's decomposition
([`V2-FIRST-CELL-HANDICAP`](V2-FIRST-CELL-HANDICAP.md)), a matched control on the revision offset
([`V2-FIRST-CELL-MASS-MATCH`](V2-FIRST-CELL-MASS-MATCH.md)), and a planted-signal positive control
([`V2-FIRST-CELL-PLANTED`](V2-FIRST-CELL-PLANTED.md)). `d_B` is reported beside it as a
decomposition, not a second criterion.

A seed with no held-out positives is not measurable and is excluded with the exclusion reported; if fewer than **8 of 10**
seeds remain, the cell is `VOID` rather than a negative result.

### 7.6 The scorer pin, fixed

[`v2_first_cell_scorer_pin.json`](v2_first_cell_scorer_pin.json) records the SHA-256 of the world generator, the detector and
the log-loss instrument. The harness refuses to score when a digest differs. The readout adapter
(`benchmarks/v2_first_cell_readout.py`) is implemented and its digest is recorded in the same pin file;
`python -m benchmarks.v2_first_cell_readout --check` verifies every digest and a deterministic small-world run, and a stale
digest refuses the cell. Re-pinning is allowed and is a reviewed commit.

### 7.7 What remains before the cell

Only the authorisation: [`DECISION-V2-FIRST-CELL`](DECISION-V2-FIRST-CELL.md) must be signed; the adapter and its digest
are already in §7.6's pin. Nothing else in this document is open.

## 8. The control arm, secondary

Requirement 6(c)–(d) implies a mechanism check, and the specification's §8.2 states it: retire or remove one member from a
composite and measure the effect on its members, with a bystander composite as the control. A tie on the **bystander** is a
pass for `M1`; a tie on the **members** means the primitive is useless for control.

This arm can `VOID` the cell if `M1` is violated. It **cannot** rescue or fail the charter on its own, because requirement 7
fixes one earning test and §3 fixes it here.

## 9. Gate order and stop condition

1. `A1`–`A5` (§6). Any failure is `VOID`: the cell does not run and no effect is quoted.
2. The behavioural cell (§7). Any `VOID` again stops interpretation before a number is read.
3. One report. The charter closes, pass or fail; extending it or adding a feature needs a new decision (requirement 5).

## 10. Deviations

This document is not edited after a cell runs. A deviation is disclosed in an amendment, and the original text stays
readable. `m`, the endpoint, the interval and the readout are locked at signature; a change to any of them is a new
pre-registration and voids prior cells.


## 10a. Amendment 1 — the β grid excludes zero (2026-11-16, before any cell)

The first executable dry run (`docs/v2_first_cell_dry_run.json`, smoke seed `20911101`) selected `β = 0` for arm C on the
calibration band, which makes the membership term vanish and reproduces arm A exactly; arm B was also being scored at
`β = 0`. A treatment arm that can select itself into the null is not a test of the treatment, so the grid is now
`{1, 2, 4, 8}` and **each** arm selects its own β on the calibration band with its own membership. The rescorings are
distinct — A `0.280457`, B `0.289424` (`β = 1`), C `0.285669` (`β = 1`) — on one smoke seed, which is a check that the arms
separate, not a result. No cell has run and no seed from the ten-seed block has been spent, so this changes the protocol
before its first observation.


## 10b. Amendment 2 — the criterion is directional (2026-11-16, before any cell)

The null-world calibration ([`V2-FIRST-CELL-NULL`](V2-FIRST-CELL-NULL.md)) put 20 structureless worlds through the same
engine, admission, β grid and scorer, then applied this interval to 1,000 ten-seed cells. It **included zero in only 57**
cells (0.0570): arm C is slower by **0.000847** nats (sd 0.000645) on a world with nothing to learn, and at ten seeds the
interval resolves that handicap. All **943** exclusions lay **above** zero. Under the two-sided wording as signed, a cell in
which the primitive was reliably *worse* would count as a pass, because the rule asked only whether the interval contained
zero. The criterion is therefore directional: the charter passes only when the interval lies entirely **below** zero; an
interval including zero is bookkeeping; an interval entirely above zero is a reversal. Both fail. Under the amended rule the
null's false-pass rate is **0 of 1,000** cells. No cell has run, so this is a pre-observation correction, disclosed with its
evidence.

## 11. What this pre-registration does not decide

The authorisation, the adapter's implementation and its digest. It does not authorise a cell, reserve spending, or permit a
second report.

## 12. Signature

| | |
|---|---|
| **Owner** | owner |
| **Status** | `SIGNED 2026-11-16 — protocol fixed; no cell authorised` |
| **Date** | 2026-11-16 |
| **Note** | Signing fixes the protocol; the cell still needs the separate authorisation decision, and the adapter's digest is added to the pin in that commit. |
