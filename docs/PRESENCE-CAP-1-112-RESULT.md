# PRESENCE-CAP-1-112 -- result

**Verdict: `CAP LIMITING`** with **112** shipped.

| Seed | A_W at 40 | A_W at 80 | A_W at 112 | A_W uncapped | Gain 40->112 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 20611901 | 28 | 32 | 51 | 112 | 23 | |
| 20611902 | 34 | 39 | 55 | 112 | 21 | |
| 20611903 | 35 | 38 | 54 | 112 | 19 | |
| 20611904 | 29 | 36 | 44 | 112 | 15 | |
| 20611905 | 46 | 47 | 58 | 111 | 12 | |
| 20611906 | 40 | 49 | 57 | 112 | 17 | |

## The 21-40 band

**Not identifiable from this block.** the 62 rank-21-40 edges are a Q4 artifact on Q4's six audit seeds; Q2's fresh seeds have different worlds, and its cells record counts, not per-edge ceiling ranks. The block shows more world edges entering service, not that those named edges do.

| Seed | Admitted 40 | Admitted 112 | S_ever 40 | S_ever 112 | A_W 40 | A_W 112 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20611901 | 80 | 100 | 80 | 100 | 28 | 51 |
| 20611902 | 88 | 101 | 88 | 101 | 34 | 55 |
| 20611903 | 63 | 96 | 63 | 96 | 35 | 54 |
| 20611904 | 80 | 100 | 80 | 100 | 29 | 44 |
| 20611905 | 77 | 98 | 77 | 98 | 46 | 58 |
| 20611906 | 73 | 102 | 73 | 102 | 40 | 57 |

The block measures more world edges entering service, but not the named Q4 edges. The decision's acceptance condition therefore remains **unadjudicated**, and the decision stays **PENDING**.

## Gates

| Gate | Result |
| --- | --- |
| `K1_build` | PASS |
| `K2_same_world` | PASS |
| `K3_presence_invariant` | PASS |
| `K4_cap_live` | PASS |
| `K5_cap_only` | PASS |
| `K6_denominator` | PASS |

Bar: **10** asserted world edges.

## Provenance disposition

**Status: PROVISIONAL, NOT OWNER-AUTHORISED (2026-11-14).** The numerical result and gates stand as recorded; the run is not owner-authorised and may not be cited as a confirmatory cap-112 result. See `docs/CAP-112-PROVENANCE-DISPOSITION.md`.

Executed without a recorded owner run authorisation. The numerical result and gates stand as recorded but are provisional; this is not an owner-authorised or confirmatory cap-112 result.
