# Authorisation: T1-PERSISTENCE-OFF

Dated 2026-11-11. Recorded against `docs/t1_persistence_off_prereg.json`, which was frozen
ungranted. This document is the grant; it is not a result.

## The grant

> Run the T1 persistence-off block at the shipped cap and finish it into its result.

## What is authorised

The twelve design cells (shipped and persistence-off x six fresh seeds at cap 112), the
fresh-process determinism rerun, the gates B1-B8 as frozen, and the result artifact and page.

## What is not authorised

- **An engine edit.** The treatment is a `MemoryService` subclass; no frozen engine file changes.
- **A cap, version, pin or canary change.** The block runs on the shipped 0.15.0 build at 112.
- **A change to the frozen gates, endpoints, margin or decision table.** They are read once, in the
  order the record fixes, and a gate failure is VOID rather than an invitation to amend the gate.
- **A re-score of Q4 or Q2.** Those verdicts stand for the builds and blocks they measured.
- **Any capability, retention or transfer claim.** The block is one ablation on six seeds.

## Status at the date of this document

Granted 2026-11-11 against the frozen record. The arm and runner were built after the grant; the
twelve cells and the rerun then executed, and the result is `VOID` on G4 because two
persistence-off cells served zero world edges. The endpoint is computed but not adjudicated.
