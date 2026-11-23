# `DECISION-V2-A4-BASE-WORLD` — release one A1 seed for A4's storage measurement

**Status:** `ADOPTED 2026-11-16 — ONE A1 SEED IS RELEASED TO A4; THE 135,168-BYTE CAP IS UNCHANGED`

**Decision ID:** `DECISION-V2-A4-BASE-WORLD-1` · **Date:** 2026-11-16

**Instruction:** release or reallocate the held base-world seed so A4 can be measured without spending a reserved block
(owner, 2026-11-16).

**Narrows:** the A1-TWO-PATH-1 reservation in `docs/a1_seed_reservations.json`, by one seed. **Leaves untouched:** the
A1 manifest, its targets, its VOID result, the other five A1 seeds, the ten V2 cell seeds, the frozen engine, the readout
and the endpoint.

## 1. The decision

1. Release seed 20740101 from the A1-TWO-PATH-1 reservation and reallocate it as the base world for A4, which is a
   storage measurement and not an A1 cell.
2. A1-TWO-PATH-1 is frozen on a VOID synthetic-fixture assembly and refuses a second run, so the released seed has no
   remaining A1 use; the other five seeds stay held and the ten V2 cell seeds are untouched.
3. The 135,168-byte A4 cap is unchanged; only the reservation that made the seed unavailable is changed.

## 2. Why the seed, and why now

A4 is the only gate that needs a **rebuilt base world** at `m = 2`: the sizing artifact's 135,168-byte cap was measured
on the world recorded in `docs/v1_carrier_identity.json`, and no other seed supports that criterion. The smoke world is
a different world; substituting it would answer a different question.

The seed was held for A1-TWO-PATH-1, but A1's result is a **VOID assembly over a synthetic fixture** — not six executed
cells — and its frozen manifest refuses a second run. The reservation therefore protected a use that cannot happen. A4
needs the world now, and releasing one seed is the smallest change that lets both records be true: A1 keeps five held
seeds and its frozen VOID record; A4 measures the base world it was specified against.

## 3. What changes, and what does not

| | |
|---|---|
| **Reservation** | 20740101 leaves the A1 unspent block and becomes a spent row owned by the A1 manifest, restated by the A4 gate record and this decision; the A1 unspent block keeps 20740102–20740106 |
| **Gate record** | `docs/v2_first_cell_gates.json` names 20740101 as A4's reallocated base seed and is an allowed restatement of the released row |
| **A1 manifest** | unchanged: its block, targets, status and VOID result are historical and no second run is permitted |
| **A4 cap** | unchanged at 135,168 bytes; the measurement is 16 pages / 65,536 bytes at `m = 2` |
| **V2 cell seeds** | untouched; no cell, no arm, no seed from the ten-seed block is spent |
| **Engine and readout** | untouched; the measurement opens no `memory.db` and writes only the primitive's scratch store |

## 4. Rejected alternatives

**Reuse the seed without releasing it.** The reservation would still hold a seed that another artifact uses, and the
collision scan would refuse the gate record.

**Substitute the spent smoke world.** It is not the base world and cannot support the 135,168-byte criterion.

**Allocate a different seed.** A4's budget was measured on this world; a different world would be a new criterion, not
the same gate.

**Mark the whole A1 block spent.** A1 ran a synthetic fixture, not cells; marking all six spent would discard five
unspent seeds and overstate what A1 used.

## 5. Evidence

- `docs/a1_two_path_manifest.json` — frozen, `GRANTED, RUN — VOID (C4_DELTA)`, and a second run refused.
- `docs/a1_two_path_result.json` — the VOID assembly over the synthetic fixture, not six executed cells.
- `docs/a1_seed_reservations.json` — the split A1 reservation and the released row.
- `docs/v2_first_cell_gates.json` — A1–A5 PASS, with A4 on the reallocated base seed.
- `docs/V2-PRIMITIVE-SIZING.md`, `docs/v2_primitive_sizing.json` — the 135,168-byte cap at `m = 2`.

## 6. Signature

| | |
|---|---|
| **Owner** | owner |
| **Adopt / reject** | `ADOPTED` |
| **Date** | 2026-11-16 |
| **Note** | One seed is released; the A4 cap is unchanged and no cell is authorised. |
