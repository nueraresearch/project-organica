# Authorisation: PRESENCE-BAND-1

Dated 2026-11-11. Recorded against `docs/presence_band_rank_prereg.json`, which was frozen
ungranted. This document is the grant; it is not a result.

## The grant

> Build the band arm runner and its refusal, then run the 12 cells under a recorded authorisation.

## What is authorised

The twelve design cells (six Q4 seeds x cap 40 and cap 112 at 120 cycles), the fresh-process
determinism rerun of seed 20611601 at 112, gates B1-B8 as frozen, and the result artifact and
page. The 40 arm is the pre-treatment control; the 112 arm is the designated counterfactual.

## What is not authorised

- **An engine edit.** Only `SleepService.MAX_PREDICTIONS` is set per cell; no frozen engine file
  changes, and the pin, version and canaries stay at 0.15.0.
- **A change to the frozen band, caps, seeds, cycles, endpoints, gates or decision table.** They
  are read once, in the frozen order, and a gate failure is VOID rather than an invitation to
  amend the gate.
- **A re-score of Q2 or Q4.** `CAP LIMITING` and `CONVERSION STAGE MEASURED` stand.
- **Any capability, retention or transfer claim.** The block reads whether the 62 named edges
  enter service; it does not measure an ability.

## Status at the date of this document

Granted 2026-11-11 against the frozen record. The arm and its preflight were built before the
grant; the twelve cells and the rerun execute under this grant, and the verdict is recorded in
`docs/presence_band_rank_run.json` without re-reading the gates.
