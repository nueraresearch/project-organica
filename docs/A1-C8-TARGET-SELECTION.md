# A1 C8 expansion target selection

**ID:** `A1-C8-EXPANSION-1`  
**Status:** `TARGET SETS FORMED — REGISTERED, NOT FROZEN, NOT A RESULT`

**This is not an experimental result.** No A1 arm cell was run; no manifest was frozen.

The design selects **20 A-K- target rows per seed** with the same pre-36 eligibility and hash order as the four-target protocol. Endpoint overlap is permitted and each tag's selected degree is capped at **3**; target rows are therefore not independent and no target edge is repeated. The C8 ceiling remains **0.05**, so the per-seed step is `1/20 = 0.05`.

| Seed | Status | Candidates | Eligible | A-K- rows | Max degree |
| ---: | --- | ---: | ---: | ---: | ---: |
| 20630101 | TARGET SET FORMED | 64 | 64 | 20 | 3 |
| 20630102 | TARGET SET FORMED | 63 | 63 | 20 | 3 |
| 20630103 | TARGET SET FORMED | 64 | 64 | 20 | 3 |
| 20630104 | TARGET SET FORMED | 64 | 64 | 20 | 3 |
| 20630105 | TARGET SET FORMED | 64 | 64 | 20 | 3 |
| 20630106 | TARGET SET FORMED | 63 | 63 | 20 | 3 |

**Registered, not frozen:** the live N=4 manifest is unchanged. Adopting this design requires a target-protocol/freeze act that replaces the current target set; this artifact authorises no run.

**Not evidence:** A no-arm, 36-cycle target-selection pass for a registered design. It freezes no manifest, reserves no seed, authorises no cell and records no C8 measurement.
