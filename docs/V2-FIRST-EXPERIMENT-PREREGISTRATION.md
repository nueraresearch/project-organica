# V2 first experiment — pre-registration skeleton

**Status:** `DRAFT SKELETON — NOT A PRE-REGISTRATION, AND NO CELL IS AUTHORISED`

**Serves:** requirements 2 and 7 of [`DECISION-V2-CHARTER`](DECISION-V2-CHARTER.md) (adopted 2026-11-16), and requirement 6's
acceptance tests. **Authorises:** nothing — no cell, no module, no engine change, no seed, no spending.

## 1. What this document fixes, and what it leaves open

A pre-registration is only worth what it fixes *before* a result is seen. This skeleton therefore fixes the parts that would
be tempting to choose afterwards — the endpoint, the failure rule, the arms, the gate order and the admission threshold — and
lists, explicitly, the parts that cannot be fixed without an authorisation (seeds, n, world, scorer, interval method,
readout). An open field is not a decision deferred to the analysis; it is a field that must be filled before the cell runs.

## 2. The one question

> Does a composition-bearing object with a content-free id and a membership mutation predict held-out edges better than the
> same atoms' pair counts — and if it does not, is that the charter's answer?

This is the charter's diagnosis, made falsifiable: V1 has no addressable handle on what it stores, so an object that can be
named and revised should buy prediction that the counts alone do not. "Should" is the hypothesis; the counts are the
comparator.

## 3. The failure criterion, fixed

From requirement 7 and [`V2-MUTABLE-IDENTITY-SPEC`](V2-MUTABLE-IDENTITY-SPEC.md) §8.3:

> **If the prediction arm's interval includes zero, the primitive is bookkeeping and the charter fails at its first
> experiment.**

That is the whole criterion, and it is one endpoint. A tie is a result. Adding features to rescue it, re-reading the
endpoint, or reporting a secondary measure as the headline are protocol violations, not judgement calls. This document also
inherits the discipline that a `VOID` stops interpretation before any effect is quoted (requirement 4).

## 4. The arms, fixed

| Arm | Primitive | Readout | What it isolates |
|---|---|---|---|
| **A — baseline** | none | pair counts only | the comparator the charter names |
| **B — label** | content-free ids, **no** membership mutation | the same readout as C | whether an id alone buys anything |
| **C — address** | content-free ids **and** membership mutation | the same readout | whether revision buys anything over a label |

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

**Changing `m` after this skeleton is signed is a new pre-registration.** It voids any cell already run under this one, because
the population that cell measured would no longer be the population this document defines. The first experiment uses `m = 2`
or it is not this experiment.

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

## 7. The behavioural cell: fixed here, open there

**Fixed.**

- The endpoint is **held-out next-edge log-loss** on cycles after the training boundary, computed from the readout each arm
  exposes, paired across arms by seed and cycle.
- The comparison is **C against A** for the charter's question; **B against A** is a reported decomposition, not a second
  failure criterion.
- The failure rule is §3's: an interval for C − A that includes zero closes the charter.
- The cell reports once. The charter then closes, pass or fail (requirement 5).

**Open — every field below must be filled before authorisation, and none of them is decided by this draft.**

| Field | State |
|---|---|
| Seed block | **none reserved by this draft**; an unspent block must be declared in `docs/a1_seed_reservations.json` at authorisation |
| Number of seeds | unset |
| World family and size | unset (the development worlds were 120 blocks / 92 sleep cycles; this is evidence, not a specification) |
| Training / evaluation boundary | unset |
| Interval method and level | unset; must be named with the code that computes it |
| Scorer pin | unset; the pre-registration must name the scorer's hash |
| Readout implementation | unset; the consumer is a build item in its own right (requirement 6(h)) |

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
readable. `m` and the endpoint are locked at signature; a change to either is a new pre-registration and voids prior cells.

## 11. What this skeleton does not decide

It does not reserve seeds, choose a world, set n, pick an interval method, pin the scorer, design the readout, or authorise
the cell. Those are the authorisation's business, and the authorisation is a separate decision from the charter.

## 12. Signature

| | |
|---|---|
| **Owner** | _unsigned_ |
| **Status** | `DRAFT SKELETON` |
| **Date** | _pending_ |
| **Note** | Filling the open fields in §7 and signing this document is the pre-registration; it still authorises no cell until the separate authorisation decision is signed. |
