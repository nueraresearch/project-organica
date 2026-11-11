# Authorisation: PRESENCE-BAND-3

Dated 2026-11-11. Recorded against `docs/presence_band_rank_3_prereg.json`, which was
frozen before any cell. This document is the grant; it is not a result.

## The grant

> Preregister a repaired band block with fresh seeds and the fixed harness, with B5 still able to fail, and record its grant before running.

## What is authorised

The twelve design cells (six fresh seeds x cap 40 and cap 112 at 120 cycles), the
fresh-process determinism rerun of seed 20612401 at 112, gates B1-B8 as frozen, and the
result artifact and page. The 40 arm is the pre-treatment control; the 112 arm is the
designated counterfactual.

The grant also authorises building the planned arm and its preflight, because the block
cannot run without them. Building the arm does not open a cell: the preflight must pass
against this record before any cell is measured.

## What is not authorised

- **An engine edit.** Only `SleepService.MAX_PREDICTIONS` is set per cell; no frozen
  engine file changes, and the pin, version and canaries stay at 0.15.0.
- **A change to the fresh seeds, band rule, caps, cycles, endpoints, gates or decision
  table.** They are read once, in the frozen order, and a gate failure is VOID rather
  than an invitation to amend the gate.
- **A substitution of Q4's band or Q4's worlds.** BAND-3 is a fresh-world block; reusing
  a Q4 seed or edge would change the claim without a new record.
- **A re-score of BAND-1 or BAND-2.** BAND-1 stays VOID and BAND-2 stays unrun; neither
  is evidence for this block in either direction.
- **Any capability, retention or transfer claim.** The block reads whether the measured
  rank-21-40 edges enter service; it does not measure an ability.

## Status at the date of this document

Granted 2026-11-11 against the frozen record. The arm is not built, no cell has run, and
`cells_run` is 0. The grant precedes the run; it does not authorise a result.
