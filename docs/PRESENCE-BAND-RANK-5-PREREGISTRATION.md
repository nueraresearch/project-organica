# PRESENCE-BAND-5 — runnable allocation-law band block

**Status.** FROZEN, RUN. Generated from `docs/presence_band_rank_5_prereg.json`.

| Field | Value |
| --- | --- |
| Seeds | 20612601, 20612602, 20612603, 20612604, 20612605, 20612606 |
| Cells | 12 |
| Caps | 40, 112 |
| Cycles | 120 |
| Grant | 2026-11-11 |
| Runner | built |
| Cells run | 13 |

## Reconciliation

The engine fills the remaining 56 seats with cooccurrences, then backfills unused cooccurrence seats with further transitions. A full window therefore has transitions + cooccurrences = 112.

BAND-1 observed 64-69 transitions; those are 56 plus backfill, with 48-43 cooccurrences. 64-69 is not an acceptance threshold.

**B5 rule.** Defensible B5: at least one full 112-row window; every full window has transitions >= 56, cooccurrences <= 56 and the sum 112; every allocation row sums to its window; the maximum served transition rank is above 40; every served edge parses and every served transition is ranked.

## Acceptance

**A.** B5 allocation law passes.

**B.** every band edge is served at 112 and none at 40, with a live seed axis.

Perfect band service cannot rescue a failed B5; a perfect allocation cannot rescue an unserved band edge.

## Grant

> Register a new band block with a defensible B5 allocation rule and a fresh dated grant, then run its twelve cells into a per-edge result.

`docs/AUTHORISATION-PRESENCE-BAND-5.md`

## Gates

| Gate | Rule |
| --- | --- |
| `B1_build` | one shipped 0.15.0 build across all cells; only MAX_PREDICTIONS differs |
| `B2_world` | each seed has the same world digest and present fingerprint at both caps |
| `B3_band_identity` | each band edge is a present transition at rank 21-40 with a recorded rank |
| `B4_control_40` | cap 40 serves no band edge and its full 40-row windows sum with a 20-transition floor |
| `B5_allocation_law` | cap 112 full windows satisfy transitions + cooccurrences = 112, transitions >= 56, cooccurrences <= 56, with rank and parsing live |
| `B6_denominator` | every seed has a non-empty band and every band edge reaches the ledger |
| `B7_determinism` | a fresh-process rerun of seed 20612601 at 112 reproduces its ledger |
| `B8_seed_axis` | at least three distinct served-band sets across the six seeds |

## Result

**VOID** — `docs/presence_band_rank_5_run.json`

A preregistration until the cells run; after the run it reads allocation and band service on this world family, not capability, retention or transfer.
