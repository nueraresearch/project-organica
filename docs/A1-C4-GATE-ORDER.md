# A1 C4 gate order

**Decision:** `POST-FREEZE VOID GATE`
**Date:** 2026-11-14
**Machine record:** [`a1_c4_gate_order.json`](a1_c4_gate_order.json)

**This is not a freeze, grant or result.** No target was frozen, no seed was reserved and no cell was run.

## Decision

C4 is **not** a pre-freeze admissibility gate. It is a **post-freeze VOID gate**.

The target manifest is frozen first, in a separate owner act. The dated grant follows, the planned cells run, and `a1_result.assemble` scores C1 and C4 from the resulting parts. If C4 fails or is unmeasurable, the A1 run is **VOID** before any claim is read.

## Why

C4 is an interference check on the executed edge-level arms, not a property of the target set. It cannot be observed without cells. Making C4 a pre-freeze condition would require either:

- freezing in order to measure the thing that is supposed to gate the freeze; or
- running an unregistered diagnostic cell before the freeze.

Both are worse than a post-freeze gate. The post-freeze route preserves the precommitted thresholds and blindness: no outcome is observed before the target manifest and grant are fixed.

C1 is scored in the same post-freeze assembly and uses the C4-expanded denominator. C1 remains the primary preservation gate; C4 supplies the non-target denominator and an interference veto.

**Draft extension:** [`A1-C1-C4-VOID-GATE-1`](A1-C1-C4-VOID-GATE.md) proposes making C1 a post-freeze VOID gate as well. It is **DRAFT — NOT DECIDED**; this C4-only record remains authoritative until it is adopted.

## VOID condition

C4 fails if any measurable non-target A, K or Y neighbour delta exceeds **0.05**, or if the non-target stream is unmeasurable. The A1 run is then **VOID**. It is not evidence, cannot be cited as a failed replication, and cannot be patched into a passing result under the same design.

## Effect on freeze

This decision removes C4 from the **pre-freeze blocker set**. It does **not** freeze the targets. The targets remain draft and the manifest remains unfrozen because no separate owner freeze act has been recorded. The grant and run remain open.

## Sequence

1. Owner freezes the representative target manifest.
2. Owner records the dated grant.
3. The planned cells run.
4. `a1_result.assemble` scores C1 and C4.
5. A C4 failure or unmeasurable C4 makes the result **VOID**.

**Not evidence:** a gate-order decision only.
