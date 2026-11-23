# Authorisation: PRESENCE-BAND-5

Dated 2026-11-11. Recorded against `docs/presence_band_rank_5_prereg.json`, before
the arm was built or any cell was opened.

## The grant

> Register a new band block with a defensible B5 allocation rule and a fresh dated grant, then run its twelve cells into a per-edge result.

## What is authorised

The twelve design cells (six fresh seeds 20612601-20612606 x caps 40 and 112 at
120 cycles), the fresh-process determinism rerun of seed 20612601 at 112, gates
B1-B8, and the per-edge result artifact and page.

The B5 rule is the BAND-4 allocation law: a full 112-row window has
`transitions + cooccurrences = 112`, with `transitions >= 56` and
`cooccurrences <= 56`; 64-69 is floor plus backfill, not a threshold.

## What is not authorised

- An engine edit; only `SleepService.MAX_PREDICTIONS` is set per cell.
- A change to the fresh seeds, caps, cycles, gates, allocation rule or acceptance
  criteria after a cell runs.
- Reusing BAND-1, BAND-2, BAND-3 or BAND-4 cells as this block's result.
- Any capability, retention or transfer claim.
